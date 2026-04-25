import streamlit as st
import anthropic
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NurtureFind Dubai",
    page_icon="🌿",
    layout="wide",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #FAF8F4;
    color: #1C1C1C;
}
h1, h2, h3 { font-family: 'DM Serif Display', serif; }

.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
}
.hero h1 { font-size: 3rem; color: #1C1C1C; margin-bottom: 0.5rem; }
.hero p {
    font-size: 1.1rem; color: #6B6B6B;
    max-width: 520px; margin: 0 auto 2rem; line-height: 1.6;
}

.specialist-card {
    background: #FFFFFF;
    border: 1px solid #E8E4DE;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.specialist-name {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem; color: #1C1C1C; margin-bottom: 0.2rem;
}
.specialist-specialty {
    font-size: 0.82rem; color: #8A7E6E; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.8rem;
}
.badge {
    display: inline-block; background: #F0EDE7; color: #5A5045;
    border-radius: 20px; padding: 0.2rem 0.7rem;
    font-size: 0.78rem; margin-right: 0.4rem; margin-bottom: 0.4rem;
}
.badge-green { background: #E6F4EE; color: #2D7A4F; }
.match-reason {
    background: #FFF8EC; border-left: 3px solid #E8A838;
    padding: 0.6rem 0.9rem; border-radius: 0 8px 8px 0;
    font-size: 0.85rem; color: #5A4A2A; margin-top: 0.8rem; line-height: 1.5;
}
.contact-links {
    display: flex; gap: 0.5rem; margin-top: 1rem; flex-wrap: wrap;
}
.contact-btn {
    display: inline-flex; align-items: center; gap: 0.35rem;
    padding: 0.4rem 0.85rem; border-radius: 8px;
    font-size: 0.82rem; font-weight: 500; text-decoration: none;
}
.btn-wa  { background: #E8F5E9; color: #2E7D32; }
.btn-ig  { background: #FCE4EC; color: #880E4F; }
.btn-web { background: #E3F2FD; color: #1565C0; }

.stat { font-size: 0.82rem; color: #8A7E6E; margin-bottom: 0.25rem; }
.stat strong { color: #1C1C1C; font-weight: 500; }
.divider { border: none; border-top: 1px solid #E8E4DE; margin: 2rem 0; }

.stTextArea textarea {
    border-radius: 12px !important; border: 1.5px solid #D9D4CC !important;
    background: #FFFFFF !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important; padding: 1rem !important;
}
.stButton > button {
    background-color: #2D5A3D !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    padding: 0.6rem 2rem !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important; font-weight: 500 !important; width: 100% !important;
}
.stButton > button:hover { background-color: #234A31 !important; }
</style>
""", unsafe_allow_html=True)


# ─── Load specialists from Google Sheets ─────────────────────────────────────
@st.cache_data(ttl=300)
def load_specialists():
    creds_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1
    df = pd.DataFrame(sheet.get_all_records())
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


# ─── AI matching ─────────────────────────────────────────────────────────────
def match_specialists(problem_text: str, df: pd.DataFrame) -> list:
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

    summary = [
        {"id": i, "name": row.get("name", ""), "specialty": row.get("specialty", ""), "keywords": row.get("keywords", "")}
        for i, row in df.iterrows()
    ]

    prompt = f"""You are a specialist matching engine for a parenting support platform in Dubai, UAE.

A parent has described their problem:
\"{problem_text}\"

Here are the available specialists:
{json.dumps(summary, indent=2)}

Return a JSON array of the top 3 most relevant specialists, ranked by relevance.
Each object must have:
- "id": the specialist's id (integer)
- "match_reason": one sentence (max 20 words) explaining why this specialist fits this specific problem

Return ONLY valid JSON. No explanation, no markdown, no extra text.
Example: [{{"id": 0, "match_reason": "Specializes in newborn sleep training and night waking issues."}}]
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.content[0].text.strip())


# ─── Render specialist card ───────────────────────────────────────────────────
def val(row, key, default=""):
    v = row.get(key, default)
    return str(v).strip() if pd.notna(v) and str(v).strip() not in ("", "nan") else default

def render_card(row, match_reason=""):
    name      = val(row, "name", "Unknown")
    specialty = val(row, "specialty")
    certs     = val(row, "certifications")
    location  = val(row, "location")
    yrs       = val(row, "years_experience")
    followers = val(row, "instagram_followers")
    price     = val(row, "price_aed")
    dha       = str(val(row, "dha_licensed", "no")).lower() in ("yes", "true", "1")
    languages = val(row, "languages")
    whatsapp  = val(row, "whatsapp_link")
    instagram = val(row, "instagram_link")
    website   = val(row, "website_link")

    dha_html  = '<span class="badge badge-green">✓ DHA Licensed</span>' if dha else ""
    cert_html = "".join(f'<span class="badge">{c.strip()}</span>' for c in certs.split(",") if c.strip())
    lang_html = "".join(f'<span class="badge">{l.strip()}</span>' for l in languages.split(",") if l.strip())

    contact_html = '<div class="contact-links">'
    if whatsapp:
        contact_html += f'<a class="contact-btn btn-wa" href="{whatsapp}" target="_blank">💬 WhatsApp</a>'
    if instagram:
        contact_html += f'<a class="contact-btn btn-ig" href="{instagram}" target="_blank">📸 Instagram</a>'
    if website:
        contact_html += f'<a class="contact-btn btn-web" href="{website}" target="_blank">🌐 Website</a>'
    contact_html += "</div>"

    try:
        followers_fmt = f"{int(float(followers)):,}"
    except Exception:
        followers_fmt = followers or "—"

    try:
        price_fmt = f"AED {int(float(price)):,}"
    except Exception:
        price_fmt = f"AED {price}" if price else "—"

    match_block = f'<div class="match-reason">💡 {match_reason}</div>' if match_reason else ""

    st.markdown(f"""
<div class="specialist-card">
    <div class="specialist-name">{name}</div>
    <div class="specialist-specialty">{specialty}</div>
    {dha_html}
    <hr style="border:none;border-top:1px solid #F0EDE7;margin:0.8rem 0;">
    <div class="stat">📍 <strong>{location}</strong></div>
    <div class="stat">🏅 <strong>{yrs} yrs</strong> experience</div>
    <div class="stat">📸 <strong>{followers_fmt}</strong> Instagram followers</div>
    <div class="stat">💰 <strong>{price_fmt}</strong> per session</div>
    <br>{cert_html}<br>{lang_html}
    {contact_html}
    {match_block}
</div>""", unsafe_allow_html=True)


# ─── HERO ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🌿 NurtureFind</h1>
    <p>Describe what your child is going through. We'll match you with the right specialist in Dubai.</p>
</div>
""", unsafe_allow_html=True)

# ─── Load data ────────────────────────────────────────────────────────────────
try:
    df = load_specialists()
except Exception as e:
    st.error(f"Could not load specialist data from Google Sheets: {e}")
    st.stop()

# ─── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filter Results")

    dha_only = st.checkbox("DHA Licensed only", value=False)

    price_range = None
    try:
        prices = pd.to_numeric(df["price_aed"], errors="coerce").dropna()
        if not prices.empty:
            min_p, max_p = int(prices.min()), int(prices.max())
            price_range = st.slider("Max price (AED)", min_p, max_p, max_p, step=50)
    except Exception:
        pass

    all_langs = set()
    for langs in df.get("languages", pd.Series([])):
        for l in str(langs).split(","):
            l = l.strip()
            if l and l != "nan":
                all_langs.add(l)
    selected_lang = st.selectbox("Language", ["All"] + sorted(all_langs))

    st.markdown("---")
    st.markdown("<small style='color:#8A7E6E'>Specialist data refreshes every 5 min from Google Sheets.</small>", unsafe_allow_html=True)

# ─── Apply filters ────────────────────────────────────────────────────────────
filtered = df.copy()

if dha_only:
    filtered = filtered[filtered["dha_licensed"].astype(str).str.lower().isin(["yes", "true", "1"])]

if price_range is not None:
    filtered = filtered[pd.to_numeric(filtered["price_aed"], errors="coerce").fillna(0) <= price_range]

if selected_lang != "All":
    filtered = filtered[filtered["languages"].str.contains(selected_lang, case=False, na=False)]

# ─── Search ───────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    problem = st.text_area(
        label="",
        placeholder="e.g. My 8-month-old wakes up every hour at night and can't fall back asleep on her own...",
        height=120,
        label_visibility="collapsed",
    )
    find_btn = st.button("Find Specialists →")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─── Results ─────────────────────────────────────────────────────────────────
if find_btn:
    if not problem.strip():
        st.warning("Please describe your child's situation first.")
    elif filtered.empty:
        st.warning("No specialists match the current filters. Try adjusting the sidebar filters.")
    else:
        with st.spinner("Finding the best specialists for you..."):
            try:
                matches = match_specialists(problem, filtered)
                st.markdown("### Top matches for your situation")
                st.markdown(
                    f"<p style='color:#8A7E6E;margin-top:-0.5rem;margin-bottom:1.5rem;'>"
                    f"Based on: <em>\"{problem[:80]}{'...' if len(problem) > 80 else ''}\"</em></p>",
                    unsafe_allow_html=True,
                )
                cols = st.columns(len(matches))
                for rank, match in enumerate(matches):
                    with cols[rank]:
                        render_card(filtered.iloc[match["id"]], match["match_reason"])

            except json.JSONDecodeError:
                st.error("Matching returned an unexpected response. Please try again.")
            except anthropic.AuthenticationError:
                st.error("Anthropic API key missing or invalid. Check Streamlit secrets.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

else:
    if not filtered.empty:
        st.markdown("### All Specialists")
        cols = st.columns(3)
        for i, (_, row) in enumerate(filtered.iterrows()):
            with cols[i % 3]:
                render_card(row)
    else:
        st.info("No specialists match the selected filters.")

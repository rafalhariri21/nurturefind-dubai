import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import re

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
.no-results {
    text-align: center; padding: 2rem;
    color: #8A7E6E; font-size: 1rem;
}

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


# ─── Keyword map: specialist type → trigger words ────────────────────────────
# Each entry maps a specialty label to a list of keywords.
# If ANY keyword appears in the parent's problem text, that specialty scores a match.
SPECIALTY_KEYWORDS = {
    "Sleep Consultant": [
        "sleep", "sleeping", "not sleeping", "won't sleep", "wakes up", "night waking",
        "bedtime", "nap", "naps", "napping", "tired", "overtired", "night routine",
        "sleep training", "cry it out", "sleep schedule", "insomnia", "restless",
    ],
    "Sleep Therapist": [
        "sleep anxiety", "nightmares", "night terrors", "fear of dark", "sleep regression",
        "sleep disorder", "can't fall asleep", "sleep problem", "sleep issue",
    ],
    "Lactation Consultant (IBCLC)": [
        "breastfeeding", "breast feeding", "nursing", "latch", "latching", "milk",
        "milk supply", "low milk", "formula", "bottle", "nipple", "pumping",
        "engorgement", "mastitis", "not feeding", "feeding issues", "newborn feeding",
    ],
    "Developmental Pediatrician / Autism Specialist": [
        "autism", "asd", "developmental delay", "not talking", "speech delay",
        "social skills", "eye contact", "stimming", "repetitive behaviour", "sensory",
        "milestone", "milestones", "development", "not walking", "late talker",
    ],
    "Paediatric Nutritionist / Dietitian": [
        "not eating", "picky eater", "fussy eater", "won't eat", "eating habits",
        "nutrition", "diet", "weight", "underweight", "overweight", "solid foods",
        "weaning", "food refusal", "food allergy", "allergies", "intolerance",
        "feeding", "baby food", "healthy eating", "growth",
    ],
    "Paediatric Occupational Therapist": [
        "fine motor", "gross motor", "occupational therapy", "ot", "handwriting",
        "coordination", "sensory processing", "sensory issues", "touch sensitivity",
        "play skills", "self care", "dressing", "feeding therapy", "balance",
        "physical development", "muscle tone",
    ],
    "Child Psychologist": [
        "anxiety", "worried", "fear", "phobia", "stress", "emotional", "behaviour",
        "behavioral", "tantrums", "meltdown", "anger", "aggression", "hitting",
        "biting", "depression", "sad", "withdrawn", "school refusal", "trauma",
        "therapy", "mental health", "self-esteem", "confidence",
    ],
    "Paediatric Dentist": [
        "teeth", "tooth", "dental", "dentist", "gums", "teething", "cavity",
        "cavities", "toothache", "brushing", "thumb sucking", "pacifier",
        "orthodontic", "braces", "mouth", "oral",
    ],
    "Parenting Coach": [
        "parenting", "discipline", "boundaries", "rules", "routine", "screen time",
        "sibling", "siblings", "fighting", "jealousy", "reward", "punishment",
        "communication", "listening", "defiant", "disobedient", "strong-willed",
        "overwhelmed parent", "burnout", "parenting style",
    ],
    "Child & Adolescent Psychiatrist": [
        "adhd", "attention", "hyperactive", "impulsive", "medication", "psychiatrist",
        "psychiatric", "bipolar", "ocd", "obsessive", "compulsive", "eating disorder",
        "anorexia", "bulimia", "self harm", "suicidal", "psychosis", "tics",
        "tourette", "adolescent", "teenager", "teen", "mood disorder",
    ],
}


# ─── Keyword matching function ────────────────────────────────────────────────
def keyword_match(problem_text: str, df: pd.DataFrame) -> list:
    """
    Score each specialist by counting how many of their keywords
    appear in the parent's problem text. Return top matches sorted
    by score, with a human-readable match reason.
    """
    text = problem_text.lower()
    # tokenise into words so "sleep" doesn't match "asleep" unexpectedly
    # but also check phrase matches for multi-word keywords
    results = []

    for idx, row in df.iterrows():
        specialty = str(row.get("specialty", "")).strip()
        # Find which keyword category this specialist belongs to
        matched_keywords = []
        score = 0

        for specialty_type, keywords in SPECIALTY_KEYWORDS.items():
            # match by specialist's specialty field (partial, case-insensitive)
            if specialty_type.lower() in specialty.lower() or specialty.lower() in specialty_type.lower():
                for kw in keywords:
                    if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE):
                        matched_keywords.append(kw)
                        score += 1

        # also check the specialist's own keywords column from the sheet
        own_keywords = str(row.get("keywords", ""))
        for kw in [k.strip() for k in own_keywords.split(",") if k.strip()]:
            if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE):
                if kw not in matched_keywords:
                    matched_keywords.append(kw)
                    score += 1

        if score > 0:
            # Build a readable match reason from matched keywords
            kw_display = ", ".join(matched_keywords[:3])
            reason = f"Matched on: {kw_display}"
            results.append({"idx": idx, "score": score, "reason": reason})

    # Sort by score descending, return top 3
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:3]


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

    match_block = f'<div class="match-reason">🔍 {match_reason}</div>' if match_reason else ""

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

# ─── Search box ──────────────────────────────────────────────────────────────
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
        matches = keyword_match(problem, filtered)

        if not matches:
            st.markdown('<div class="no-results">🔍 No strong keyword matches found.<br>Try using different words — for example: <em>sleep, eating, behaviour, speech, teeth, anxiety.</em></div>', unsafe_allow_html=True)
        else:
            st.markdown("### Best matches for your situation")
            st.markdown(
                f"<p style='color:#8A7E6E;margin-top:-0.5rem;margin-bottom:1.5rem;'>"
                f"Based on: <em>\"{problem[:80]}{'...' if len(problem) > 80 else ''}\"</em></p>",
                unsafe_allow_html=True,
            )
            cols = st.columns(len(matches))
            for rank, match in enumerate(matches):
                with cols[rank]:
                    render_card(filtered.loc[match["idx"]], match["reason"])

else:
    if not filtered.empty:
        st.markdown("### All Specialists")
        cols = st.columns(3)
        for i, (_, row) in enumerate(filtered.iterrows()):
            with cols[i % 3]:
                render_card(row)
    else:
        st.info("No specialists match the selected filters.")

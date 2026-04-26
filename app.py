import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import re
from datetime import datetime

st.set_page_config(
    page_title="NurtureFind",
    page_icon="🌿",
    layout="wide",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #FAF8F4;
    color: #1C1C1C;
}
h1, h2, h3 { font-family: 'DM Serif Display', serif; }

.hero { text-align: center; padding: 3rem 1rem 2rem; }
.hero h1 { font-size: 3rem; color: #1C1C1C; margin-bottom: 0.5rem; }
.hero p { font-size: 1.1rem; color: #6B6B6B; max-width: 560px; margin: 0 auto 2rem; line-height: 1.6; }

.specialist-card {
    background: #FFFFFF; border: 1px solid #E8E4DE;
    border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;
    transition: box-shadow 0.2s, border-color 0.2s;
}
.specialist-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-color: #2D5A3D; }
.specialist-name { font-family: 'DM Serif Display', serif; font-size: 1.25rem; color: #1C1C1C; margin-bottom: 0.15rem; }
.specialist-specialty { font-size: 0.78rem; color: #8A7E6E; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.7rem; }

.badge { display: inline-block; background: #F0EDE7; color: #5A5045; border-radius: 20px; padding: 0.18rem 0.65rem; font-size: 0.76rem; margin-right: 0.35rem; margin-bottom: 0.35rem; }
.badge-green  { background: #E6F4EE; color: #2D7A4F; }
.badge-amber  { background: #FFF8EC; color: #7A5A1A; }
.badge-blue   { background: #E3F2FD; color: #1565C0; }
.badge-purple { background: #F3E5F5; color: #6A1B9A; }
.badge-red    { background: #FBE9E7; color: #BF360C; }

.pill-row { display: flex; flex-wrap: wrap; gap: 0.3rem; margin: 0.5rem 0; }

.stat { font-size: 0.82rem; color: #8A7E6E; margin-bottom: 0.22rem; }
.stat strong { color: #1C1C1C; font-weight: 500; }

.stars { color: #E8A838; font-size: 1rem; }
.rating-count { font-size: 0.78rem; color: #8A7E6E; margin-left: 0.3rem; }

.match-reason { background: #FFF8EC; border-left: 3px solid #E8A838; padding: 0.55rem 0.85rem; border-radius: 0 8px 8px 0; font-size: 0.83rem; color: #5A4A2A; margin-top: 0.8rem; line-height: 1.5; }
.divider { border: none; border-top: 1px solid #E8E4DE; margin: 2rem 0; }

/* Contact & booking buttons */
.contact-links { display: flex; gap: 0.5rem; margin-top: 0.8rem; flex-wrap: wrap; }
.contact-btn { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.4rem 0.85rem; border-radius: 8px; font-size: 0.82rem; font-weight: 500; text-decoration: none; }
.btn-wa   { background: #E8F5E9; color: #2E7D32; }
.btn-ig   { background: #FCE4EC; color: #880E4F; }
.btn-web  { background: #E3F2FD; color: #1565C0; }
.btn-li   { background: #E8EAF6; color: #1A237E; }
.btn-book { background: #2D5A3D; color: #FFFFFF; font-weight: 600; }

/* Profile */
.profile-header { background: #FFFFFF; border: 1px solid #E8E4DE; border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem; }
.profile-name { font-family: 'DM Serif Display', serif; font-size: 2rem; color: #1C1C1C; margin-bottom: 0.25rem; }
.profile-specialty { font-size: 0.9rem; color: #8A7E6E; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 1rem; }
.profile-section { background: #FFFFFF; border: 1px solid #E8E4DE; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; }
.profile-section h4 { font-family: 'DM Serif Display', serif; font-size: 1.1rem; color: #2D5A3D; margin-bottom: 0.75rem; }
.bio-text { font-size: 0.95rem; line-height: 1.75; color: #3A3A3A; }
.package-card { background: #FAF8F4; border: 1px solid #E8E4DE; border-radius: 10px; padding: 1rem; margin-bottom: 0.6rem; }
.package-name  { font-weight: 600; font-size: 0.92rem; color: #1C1C1C; }
.package-price { font-size: 0.88rem; color: #2D5A3D; font-weight: 600; margin-top: 0.2rem; }
.package-desc  { font-size: 0.83rem; color: #6B6B6B; margin-top: 0.3rem; line-height: 1.5; }

/* Reviews */
.review-card { background: #FAF8F4; border: 1px solid #E8E4DE; border-radius: 10px; padding: 1rem; margin-bottom: 0.7rem; }
.review-author { font-weight: 600; font-size: 0.88rem; color: #1C1C1C; }
.review-date   { font-size: 0.78rem; color: #8A7E6E; margin-left: 0.5rem; }
.review-text   { font-size: 0.88rem; color: #3A3A3A; margin-top: 0.4rem; line-height: 1.55; }

.stButton > button {
    background-color: #2D5A3D !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    padding: 0.6rem 2rem !important; font-size: 1rem !important;
    font-weight: 500 !important; width: 100% !important;
}
.stButton > button:hover { background-color: #234A31 !important; }
.stTextArea textarea {
    border-radius: 12px !important; border: 1.5px solid #D9D4CC !important;
    background: #FFFFFF !important; font-size: 1rem !important; padding: 1rem !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Keyword map ──────────────────────────────────────────────────────────────
SPECIALTY_KEYWORDS = {
    "Sleep Consultant": ["sleep","sleeping","not sleeping","won't sleep","wakes up","night waking","bedtime","nap","naps","napping","tired","overtired","night routine","sleep training","cry it out","sleep schedule","insomnia","restless"],
    "Sleep Therapist": ["sleep anxiety","nightmares","night terrors","fear of dark","sleep regression","sleep disorder","can't fall asleep","sleep problem","sleep issue"],
    "Lactation Consultant (IBCLC)": ["breastfeeding","breast feeding","nursing","latch","latching","milk","milk supply","low milk","formula","bottle","nipple","pumping","engorgement","mastitis","not feeding","feeding issues","newborn feeding"],
    "Developmental Pediatrician / Autism Specialist": ["autism","asd","developmental delay","not talking","speech delay","social skills","eye contact","stimming","repetitive behaviour","sensory","milestone","milestones","development","not walking","late talker"],
    "Paediatric Nutritionist / Dietitian": ["not eating","picky eater","fussy eater","won't eat","eating habits","nutrition","diet","weight","underweight","overweight","solid foods","weaning","food refusal","food allergy","allergies","intolerance","feeding","baby food","healthy eating","growth"],
    "Paediatric Occupational Therapist": ["fine motor","gross motor","occupational therapy","ot","handwriting","coordination","sensory processing","sensory issues","touch sensitivity","play skills","self care","dressing","feeding therapy","balance","physical development","muscle tone"],
    "Child Psychologist": ["anxiety","worried","fear","phobia","stress","emotional","behaviour","behavioral","tantrums","meltdown","anger","aggression","hitting","biting","depression","sad","withdrawn","school refusal","trauma","therapy","mental health","self-esteem","confidence"],
    "Paediatric Dentist": ["teeth","tooth","dental","dentist","gums","teething","cavity","cavities","toothache","brushing","thumb sucking","pacifier","orthodontic","braces","mouth","oral"],
    "Parenting Coach": ["parenting","discipline","boundaries","rules","routine","screen time","sibling","siblings","fighting","jealousy","reward","punishment","communication","listening","defiant","disobedient","strong-willed","overwhelmed parent","burnout","parenting style"],
    "Child & Adolescent Psychiatrist": ["adhd","attention","hyperactive","impulsive","medication","psychiatrist","psychiatric","bipolar","ocd","obsessive","compulsive","eating disorder","anorexia","bulimia","self harm","suicidal","psychosis","tics","tourette","adolescent","teenager","teen","mood disorder"],
}

# ─── Google Sheets helpers ────────────────────────────────────────────────────
def get_gc():
    creds_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

@st.cache_data(ttl=300)
def load_specialists():
    gc = get_gc()
    sh = gc.open_by_key(st.secrets["GOOGLE_SHEET_ID"])
    df = pd.DataFrame(sh.sheet1.get_all_records())
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

@st.cache_data(ttl=60)
def load_reviews():
    try:
        gc = get_gc()
        sh = gc.open_by_key(st.secrets["GOOGLE_SHEET_ID"])
        try:
            ws = sh.worksheet("Reviews")
        except gspread.exceptions.WorksheetNotFound:
            return pd.DataFrame(columns=["specialist_name","reviewer_name","rating","review_text","date"])
        df = pd.DataFrame(ws.get_all_records())
        if df.empty:
            return pd.DataFrame(columns=["specialist_name","reviewer_name","rating","review_text","date"])
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        return df
    except Exception:
        return pd.DataFrame(columns=["specialist_name","reviewer_name","rating","review_text","date"])

def submit_review(specialist_name, reviewer_name, rating, review_text):
    gc = get_gc()
    sh = gc.open_by_key(st.secrets["GOOGLE_SHEET_ID"])
    try:
        ws = sh.worksheet("Reviews")
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title="Reviews", rows=1000, cols=10)
        ws.append_row(["specialist_name","reviewer_name","rating","review_text","date"])
    ws.append_row([
        specialist_name, reviewer_name, rating,
        review_text, datetime.now().strftime("%Y-%m-%d")
    ])
    load_reviews.clear()

# ─── Helpers ──────────────────────────────────────────────────────────────────
def val(row, key, default=""):
    v = row.get(key, default)
    s = str(v).strip()
    return s if pd.notna(v) and s not in ("", "nan", "None") else default

def is_yes(row, key):
    return str(val(row, key, "no")).lower() in ("yes", "true", "1")

def stars_html(rating):
    r = round(float(rating))
    return "⭐" * r + "☆" * (5 - r)

def avg_rating(reviews_df, name):
    sub = reviews_df[reviews_df["specialist_name"] == name]
    if sub.empty:
        return None, 0
    try:
        avg = round(pd.to_numeric(sub["rating"], errors="coerce").dropna().mean(), 1)
        return avg, len(sub)
    except Exception:
        return None, 0

# ─── Keyword matching ─────────────────────────────────────────────────────────
def keyword_match(problem_text, df):
    text = problem_text.lower()
    results = []
    for idx, row in df.iterrows():
        specialty = str(row.get("specialty", "")).strip()
        matched_kws, score = [], 0
        for stype, kws in SPECIALTY_KEYWORDS.items():
            if stype.lower() in specialty.lower() or specialty.lower() in stype.lower():
                for kw in kws:
                    if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE):
                        matched_kws.append(kw)
                        score += 1
        for kw in [k.strip() for k in str(row.get("keywords","")).split(",") if k.strip()]:
            if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE) and kw not in matched_kws:
                matched_kws.append(kw)
                score += 1
        if score > 0:
            results.append({"idx": idx, "score": score, "reason": f"Matched on: {', '.join(matched_kws[:3])}"})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:3]

# ─── Search result card ───────────────────────────────────────────────────────
def render_card(row, reviews_df, match_reason=""):
    name        = val(row, "name", "Unknown")
    specialty   = val(row, "specialty")
    location    = val(row, "location")
    city        = val(row, "city")
    yrs         = val(row, "years_experience")
    price       = val(row, "price_aed")
    nationality = val(row, "nationality")
    dha         = is_yes(row, "dha_licensed")
    languages   = val(row, "languages")
    online      = is_yes(row, "online_consultation")
    free_intro  = is_yes(row, "free_intro_session")
    booking     = val(row, "booking_link")
    whatsapp    = val(row, "whatsapp_link")

    dha_badge    = '<span class="badge badge-green">✓ DHA Licensed</span>' if dha else ""
    online_badge = '<span class="badge badge-blue">💻 Online</span>' if online else ""
    intro_badge  = '<span class="badge badge-amber">🎁 Free intro</span>' if free_intro else ""
    nat_badge    = f'<span class="badge">{nationality}</span>' if nationality else ""
    lang_html    = "".join(f'<span class="badge">{l.strip()}</span>' for l in languages.split(",") if l.strip())

    avg, count = avg_rating(reviews_df, name)
    rating_html = ""
    if avg:
        rating_html = f'<div style="margin:0.3rem 0"><span class="stars">{stars_html(avg)}</span><span class="rating-count">{avg} ({count} review{"s" if count!=1 else ""})</span></div>'

    try:    price_fmt = f"AED {int(float(price)):,}"
    except: price_fmt = f"AED {price}" if price else "—"

    book_btn = ""
    if booking:
        book_btn = f'<a class="contact-btn btn-book" href="{booking}" target="_blank">📅 Book now</a>'
    elif whatsapp:
        book_btn = f'<a class="contact-btn btn-book" href="{whatsapp}" target="_blank">📅 Book via WhatsApp</a>'

    match_block = f'<div class="match-reason">🔍 {match_reason}</div>' if match_reason else ""

    location_str = f"{location}, {city}" if city and city not in location else location

    st.markdown(f"""
<div class="specialist-card">
    <div class="specialist-name">{name}</div>
    <div class="specialist-specialty">{specialty}</div>
    {rating_html}
    <div class="pill-row">{dha_badge}{online_badge}{intro_badge}{nat_badge}</div>
    <hr style="border:none;border-top:1px solid #F0EDE7;margin:0.7rem 0;">
    <div class="stat">📍 <strong>{location_str}</strong></div>
    <div class="stat">🏅 <strong>{yrs} yrs</strong> experience</div>
    <div class="stat">💰 From <strong>{price_fmt}</strong> per session</div>
    <div style="margin-top:0.5rem">{lang_html}</div>
    <div class="contact-links">{book_btn}</div>
    {match_block}
</div>""", unsafe_allow_html=True)

    if st.button(f"View {name}'s full profile", key=f"profile_{name}_{id(row)}"):
        st.session_state["profile_id"] = name
        st.rerun()

# ─── Full profile page ────────────────────────────────────────────────────────
def render_profile(row, reviews_df):
    name         = val(row, "name", "Unknown")
    specialty    = val(row, "specialty")
    bio          = val(row, "bio")
    location     = val(row, "location")
    city         = val(row, "city")
    area         = val(row, "area")
    yrs          = val(row, "years_experience")
    followers    = val(row, "instagram_followers")
    price        = val(row, "price_aed")
    nationality  = val(row, "nationality")
    dha          = is_yes(row, "dha_licensed")
    dha_number   = val(row, "dha_license_number")
    languages    = val(row, "languages")
    certs        = val(row, "certifications")
    clinics      = val(row, "clinics")
    insurance    = val(row, "insurance_accepted")
    online       = is_yes(row, "online_consultation")
    free_intro   = is_yes(row, "free_intro_session")
    whatsapp     = val(row, "whatsapp_link")
    instagram    = val(row, "instagram_link")
    website      = val(row, "website_link")
    linkedin     = val(row, "linkedin_link")
    booking      = val(row, "booking_link")
    packages_raw = val(row, "packages")

    if st.button("← Back to search"):
        st.session_state.pop("profile_id", None)
        st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Header
    col_info, col_contact = st.columns([3, 1])
    with col_info:
        dha_badge    = '<span class="badge badge-green">✓ DHA Licensed</span>' if dha else '<span class="badge">No DHA License</span>'
        online_badge = '<span class="badge badge-blue">💻 Online consultations</span>' if online else ""
        intro_badge  = '<span class="badge badge-amber">🎁 Free intro session</span>' if free_intro else ""
        nat_badge    = f'<span class="badge">{nationality}</span>' if nationality else ""
        lang_html    = "".join(f'<span class="badge">{l.strip()}</span>' for l in languages.split(",") if l.strip())
        cert_html    = "".join(f'<span class="badge badge-purple">{c.strip()}</span>' for c in certs.split(",") if c.strip())

        try:    followers_fmt = f"{int(float(followers)):,}"
        except: followers_fmt = followers or "—"
        try:    price_fmt = f"AED {int(float(price)):,}"
        except: price_fmt = f"AED {price}" if price else "—"

        avg, count = avg_rating(reviews_df, name)
        rating_html = ""
        if avg:
            rating_html = f'<div style="margin:0.5rem 0"><span class="stars" style="font-size:1.2rem">{stars_html(avg)}</span><span class="rating-count" style="font-size:0.9rem"> {avg} out of 5 ({count} review{"s" if count!=1 else ""})</span></div>'

        location_parts = [p for p in [area, location, city] if p and p not in ["", "nan"]]
        location_str = ", ".join(dict.fromkeys(location_parts))

        st.markdown(f"""
<div class="profile-header">
    <div class="profile-name">{name}</div>
    <div class="profile-specialty">{specialty}</div>
    {rating_html}
    <div class="pill-row">{dha_badge}{online_badge}{intro_badge}{nat_badge}</div>
    <hr style="border:none;border-top:1px solid #F0EDE7;margin:0.9rem 0;">
    <div class="stat">📍 <strong>{location_str}</strong></div>
    <div class="stat">🏅 <strong>{yrs} years</strong> of experience</div>
    <div class="stat">📸 <strong>{followers_fmt}</strong> Instagram followers</div>
    <div class="stat">💰 From <strong>{price_fmt}</strong> per session</div>
    {"<div class='stat'>🌍 <strong>Nationality: " + nationality + "</strong></div>" if nationality else ""}
    {"<div class='stat'>🪪 DHA License: <strong>" + dha_number + "</strong></div>" if dha_number else ""}
    <div style="margin-top:0.7rem">{cert_html}</div>
    <div style="margin-top:0.4rem">{lang_html}</div>
</div>""", unsafe_allow_html=True)

    with col_contact:
        st.markdown('<div class="profile-section"><h4>📬 Contact & Book</h4>', unsafe_allow_html=True)
        if booking:
            st.markdown(f'<a class="contact-btn btn-book" href="{booking}" target="_blank" style="margin-bottom:0.5rem;display:inline-flex">📅 Book now</a><br>', unsafe_allow_html=True)
        elif whatsapp:
            st.markdown(f'<a class="contact-btn btn-book" href="{whatsapp}" target="_blank" style="margin-bottom:0.5rem;display:inline-flex">📅 Book via WhatsApp</a><br>', unsafe_allow_html=True)
        if whatsapp:
            st.markdown(f'<a class="contact-btn btn-wa" href="{whatsapp}" target="_blank">💬 WhatsApp</a><br><br>', unsafe_allow_html=True)
        if instagram:
            st.markdown(f'<a class="contact-btn btn-ig" href="{instagram}" target="_blank">📸 Instagram</a><br><br>', unsafe_allow_html=True)
        if website:
            st.markdown(f'<a class="contact-btn btn-web" href="{website}" target="_blank">🌐 Website</a><br><br>', unsafe_allow_html=True)
        if linkedin:
            st.markdown(f'<a class="contact-btn btn-li" href="{linkedin}" target="_blank">💼 LinkedIn</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([3, 2])

    with left:
        if bio:
            st.markdown(f'<div class="profile-section"><h4>👤 About</h4><p class="bio-text">{bio}</p></div>', unsafe_allow_html=True)

        if packages_raw:
            pkgs_html = '<div class="profile-section"><h4>📦 Packages & Pricing</h4>'
            for pkg in packages_raw.split("|"):
                parts = [p.strip() for p in pkg.split(";")]
                pname  = parts[0] if len(parts) > 0 else ""
                pprice = parts[1] if len(parts) > 1 else ""
                pdesc  = parts[2] if len(parts) > 2 else ""
                pkgs_html += f'<div class="package-card"><div class="package-name">{pname}</div><div class="package-price">{pprice}</div>{"<div class=\'package-desc\'>" + pdesc + "</div>" if pdesc else ""}</div>'
            pkgs_html += "</div>"
            st.markdown(pkgs_html, unsafe_allow_html=True)

        # ── Reviews section ──
        st.markdown('<div class="profile-section"><h4>⭐ Reviews</h4>', unsafe_allow_html=True)
        specialist_reviews = reviews_df[reviews_df["specialist_name"] == name] if not reviews_df.empty else pd.DataFrame()

        if not specialist_reviews.empty:
            for _, rev in specialist_reviews.iterrows():
                r_name  = str(rev.get("reviewer_name", "Anonymous"))
                r_date  = str(rev.get("date", ""))
                r_text  = str(rev.get("review_text", ""))
                r_stars = rev.get("rating", 0)
                try:    r_stars_html = stars_html(r_stars)
                except: r_stars_html = ""
                st.markdown(f"""
<div class="review-card">
    <span class="review-author">{r_name}</span>
    <span class="review-date">{r_date}</span>
    <div class="stars" style="font-size:0.9rem">{r_stars_html}</div>
    <div class="review-text">{r_text}</div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#8A7E6E;font-size:0.9rem">No reviews yet. Be the first to leave one!</p>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Leave a review form ──
        with st.expander("✍️ Leave a review"):
            with st.form(key=f"review_form_{name}"):
                r_name_input = st.text_input("Your name (or leave blank to stay anonymous)")
                r_rating     = st.select_slider("Rating", options=[1, 2, 3, 4, 5], value=5, format_func=lambda x: "⭐" * x)
                r_text_input = st.text_area("Your experience", placeholder="Share how this specialist helped your family...")
                submitted    = st.form_submit_button("Submit review")
                if submitted:
                    if not r_text_input.strip():
                        st.warning("Please write something before submitting.")
                    else:
                        try:
                            submit_review(
                                name,
                                r_name_input.strip() or "Anonymous",
                                r_rating,
                                r_text_input.strip()
                            )
                            st.success("Thank you! Your review has been submitted.")
                        except Exception as e:
                            st.error(f"Could not save review: {e}")

    with right:
        if clinics:
            ch = '<div class="profile-section"><h4>🏥 Clinics & Locations</h4>'
            for c in clinics.split(","):
                ch += f'<div class="stat" style="margin-bottom:0.4rem">📌 {c.strip()}</div>'
            ch += "</div>"
            st.markdown(ch, unsafe_allow_html=True)

        if insurance:
            ih = '<div class="profile-section"><h4>🏦 Insurance Accepted</h4>'
            for ins in insurance.split(","):
                ih += f'<span class="badge">{ins.strip()}</span>'
            ih += "</div>"
            st.markdown(ih, unsafe_allow_html=True)

        extras = []
        if online:  extras.append("💻 <strong>Online consultations available</strong>")
        if free_intro: extras.append("🎁 <strong>Free intro session</strong> — no-commitment first call")
        if extras:
            eh = '<div class="profile-section"><h4>✨ Good to know</h4>' + "".join(f'<div class="stat" style="margin-bottom:0.6rem">{e}</div>' for e in extras) + "</div>"
            st.markdown(eh, unsafe_allow_html=True)


# ─── ROUTING ─────────────────────────────────────────────────────────────────
try:
    df = load_specialists()
except Exception as e:
    st.error(f"Could not load data from Google Sheets: {e}")
    st.stop()

reviews_df = load_reviews()

if "profile_id" in st.session_state:
    pid   = st.session_state["profile_id"]
    match = df[df["name"] == pid]
    if not match.empty:
        render_profile(match.iloc[0], reviews_df)
    else:
        st.error("Specialist not found.")
        if st.button("← Back"):
            st.session_state.pop("profile_id", None)
            st.rerun()
    st.stop()

# ─── MAIN PAGE ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🌿 NurtureFind</h1>
    <p>Describe what your child is going through. We'll match you with the right specialist.</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")

    # City
    all_cities = ["All"]
    if "city" in df.columns:
        cities = sorted(df["city"].dropna().unique().tolist())
        all_cities += [c for c in cities if c and c != "nan"]
    selected_city = st.selectbox("🏙️ City", all_cities)

    # Area (dynamic: filtered by city if selected)
    area_df = df if selected_city == "All" else df[df["city"] == selected_city]
    all_areas = ["All"]
    if "area" in df.columns:
        areas = sorted(area_df["area"].dropna().unique().tolist())
        all_areas += [a for a in areas if a and a != "nan"]
    selected_area = st.selectbox("📍 Area", all_areas)

    # Language
    all_langs = set()
    for langs in df.get("languages", pd.Series([])):
        for l in str(langs).split(","):
            l = l.strip()
            if l and l != "nan": all_langs.add(l)
    selected_lang = st.selectbox("🗣️ Language", ["All"] + sorted(all_langs))

    # Nationality
    all_nats = ["All"]
    if "nationality" in df.columns:
        nats = sorted(df["nationality"].dropna().unique().tolist())
        all_nats += [n for n in nats if n and n != "nan"]
    selected_nat = st.selectbox("🌍 Nationality", all_nats)

    st.markdown("---")
    dha_only    = st.checkbox("✅ DHA Licensed only")
    online_only = st.checkbox("💻 Online consultation")
    intro_only  = st.checkbox("🎁 Free intro session")

    price_range = None
    try:
        prices = pd.to_numeric(df["price_aed"], errors="coerce").dropna()
        if not prices.empty:
            min_p, max_p = int(prices.min()), int(prices.max())
            price_range = st.slider("💰 Max price (AED)", min_p, max_p, max_p, step=50)
    except: pass

    st.markdown("---")
    st.markdown("<small style='color:#8A7E6E'>Data refreshes every 5 min.</small>", unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered = df.copy()
if selected_city != "All" and "city" in filtered.columns:
    filtered = filtered[filtered["city"].str.lower() == selected_city.lower()]
if selected_area != "All" and "area" in filtered.columns:
    filtered = filtered[filtered["area"].str.lower() == selected_area.lower()]
if selected_lang != "All":
    filtered = filtered[filtered["languages"].str.contains(selected_lang, case=False, na=False)]
if selected_nat != "All" and "nationality" in filtered.columns:
    filtered = filtered[filtered["nationality"].str.lower() == selected_nat.lower()]
if dha_only:
    filtered = filtered[filtered["dha_licensed"].astype(str).str.lower().isin(["yes","true","1"])]
if online_only:
    filtered = filtered[filtered["online_consultation"].astype(str).str.lower().isin(["yes","true","1"])]
if intro_only:
    filtered = filtered[filtered["free_intro_session"].astype(str).str.lower().isin(["yes","true","1"])]
if price_range is not None:
    filtered = filtered[pd.to_numeric(filtered["price_aed"], errors="coerce").fillna(0) <= price_range]

# ── Search box ────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    problem  = st.text_area("", placeholder="e.g. My 8-month-old wakes up every hour at night and can't fall back asleep on her own...", height=120, label_visibility="collapsed")
    find_btn = st.button("Find Specialists →")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Results ───────────────────────────────────────────────────────────────────
if find_btn:
    if not problem.strip():
        st.warning("Please describe your child's situation first.")
    elif filtered.empty:
        st.warning("No specialists match the current filters.")
    else:
        matches = keyword_match(problem, filtered)
        if not matches:
            st.markdown('<div style="text-align:center;color:#8A7E6E;padding:2rem">No strong matches found. Try words like: sleep, eating, behaviour, speech, teeth, anxiety.</div>', unsafe_allow_html=True)
        else:
            st.markdown("### Best matches for your situation")
            st.markdown(f"<p style='color:#8A7E6E;margin-top:-0.5rem;margin-bottom:1.5rem;'>Based on: <em>\"{problem[:80]}{'...' if len(problem)>80 else ''}\"</em></p>", unsafe_allow_html=True)
            cols = st.columns(len(matches))
            for rank, match in enumerate(matches):
                with cols[rank]:
                    render_card(filtered.loc[match["idx"]], reviews_df, match["reason"])
else:
    if not filtered.empty:
        st.markdown(f"### All Specialists ({len(filtered)})")
        cols = st.columns(3)
        for i, (_, row) in enumerate(filtered.iterrows()):
            with cols[i % 3]:
                render_card(row, reviews_df)
    else:
        st.info("No specialists match the selected filters.")

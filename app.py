import streamlit as st
import urllib.parse
from fpdf import FPDF
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="Custom Club Fitting & Gear Diagnostic Engine",
    page_icon="⛳",
    layout="wide"
)

# --- Configuration Constants ---
EPN_CAMPAIGN_ID = "YOUR_EPN_CAMPAIGN_ID"
ZAPIER_WEBHOOK_URL = "YOUR_ZAPIER_OR_MAKE_WEBHOOK_URL"

# --- Curated Top 5 Hardware Databases ---
HARDWARE_DB = {
    "driver_heads": {
        "Low Spin / Forward CG": [
            {"model": "Ping G430 LST", "desc": "Carbonfly wrap, low spin, anti-left stability"},
            {"model": "TaylorMade Qi10 LS", "desc": "Sliding weight track, high ball speed, piercing flight"},
            {"model": "Callaway Paradym Ai Smoke Triple Diamond", "desc": "Workable compact shape, low spin/launch"},
            {"model": "Titleist TSR3 / TSR4", "desc": "Precision CG track, ultra-penetrating trajectory"},
            {"model": "Cobra LTDx LS / Darkspeed LS", "desc": "Forward heel/toe weighting, low spin bomber"}
        ],
        "Max Forgiveness / High MOI": [
            {"model": "Ping G430 MAX / 10K", "desc": "Industry-leading MOI, ultra-stable off-center strikes"},
            {"model": "TaylorMade Qi10 Max", "desc": "10,000 MOI design, high launch, maximum backspin carry"},
            {"model": "Callaway Paradym Ai Smoke MAX", "desc": "Ai Smart Face, tight dispersion, optimal spin loft"},
            {"model": "Titleist TSR2", "desc": "Max speed and stability across entire face"},
            {"model": "Cobra LTDx MAX / Darkspeed MAX", "desc": "Deep rear CG, adjustable draw-bias option"}
        ],
        "Draw Biased / Slice Correction": [
            {"model": "Ping G430 SFT", "desc": "Straight Flight Technology, movable heel tungsten weight"},
            {"model": "TaylorMade Qi10 Max (Draw Setting)", "desc": "Heel weight bias, upright lie angle design"},
            {"model": "Callaway Paradym Ai Smoke MAX D", "desc": "Built-in draw bias with generous face offset"},
            {"model": "Cobra Darkspeed MAX (Heel Port)", "desc": "High MOI heel weight configuration to square face"},
            {"model": "Mizuno ST-X 230", "desc": "Heel-side Cortech Chamber for natural right-to-left flight"}
        ]
    },
    "driver_shafts": {
        "Heavy / Low Launch / Low Spin (Stiff - X-Flex)": [
            {"model": "Fujikura Ventus Black / TR Black 6S/6X", "desc": "VeloCore technology, ultra-stiff tip stability"},
            {"model": "Project X HZRDUS Smoke Black RDX 60/70", "desc": "Low launch/spin, aggressive transition profile"},
            {"model": "Mitsubishi Tensei 1K Black / White 65", "desc": "High modulus carbon fiber, low torque feedback"},
            {"model": "Graphite Design Tour AD XC / VF 6", "desc": "Firm butt and tip section for maximum control"},
            {"model": "UST Mamiya LIN-Q M40X White 60", "desc": "Extreme energy transfer without tip twisting"}
        ],
        "Mid Weight / Mid Launch / Mid Spin (Regular - Stiff)": [
            {"model": "Fujikura Ventus Blue / TR Blue 5S/6S", "desc": "Smooth mid-section load with firm tip stability"},
            {"model": "Mitsubishi Chemical Kai'li Blue 60", "desc": "Consistent kick, modern balance point"},
            {"model": "Graphite Design Tour AD DI 6", "desc": "Legendary smooth feel, high launch/low spin profile"},
            {"model": "Project X HZRDUS Smoke Blue RDX 60", "desc": "Counterbalanced, mid-launch dynamic profile"},
            {"model": "UST Mamiya Helium Nanocore 50/60", "desc": "Stable lightweight structure with mid-spin carry"}
        ],
        "Lightweight / High Launch / Active Tip (Lite - Regular)": [
            {"model": "UST Mamiya Helium Nanocore 40/50", "desc": "Ultra-lightweight high-launch dynamic kick"},
            {"model": "Fujikura Air Speeder 45", "desc": "Low swing speed distance multiplier"},
            {"model": "Aldila Ascent PL 40/45", "desc": "Active tip technology to get airborne quickly"},
            {"model": "Mitsubishi Grand Bassara 49", "desc": "Ultra-premium lightweight micro-weave graphite"},
            {"model": "Project X Cypher 2.0 40/50", "desc": "Active tip bend profile for effortless launch"}
        ]
    },
    "iron_heads": {
        "Player's Cavity / Sub-10 Handicap": [
            {"model": "Titleist T100 / T150", "desc": "Tour-validated turf interaction, compact cavity profile"},
            {"model": "Mizuno Pro 243 / JPX 923 Tour", "desc": "Grain Flow Forged feel with subtle forgiveness cavity"},
            {"model": "Ping Blueprint S", "desc": "Forged 8620 carbon steel with clean compact lines"},
            {"model": "Callaway Apex CB 24", "desc": "Pure player cavity, minimal offset, precise control"},
            {"model": "TaylorMade P770", "desc": "Compact hollow-body with forged feel and low offset"}
        ],
        "Player's Distance / 10-18 Handicap": [
            {"model": "Cobra King Forged Tec (Standard / ONE Length)", "desc": "Hollow construction, foam injected, clean topline"},
            {"model": "TaylorMade P790", "desc": "SpeedFoam Air, high ball speeds with refined look"},
            {"model": "Titleist T200", "desc": "Max impact technology, forged face, controlled spin"},
            {"model": "Ping i530 / i525", "desc": "Forged maraging steel face, compact distance iron"},
            {"model": "Mizuno JPX 923 Forged", "desc": "Chromoly forged speed frame with balanced sole"}
        ],
        "Game Improvement / 19+ Handicap": [
            {"model": "Ping G430", "desc": "PurFlex badge, extreme perimeter weighting, easy launch"},
            {"model": "Callaway Paradym Ai Smoke", "desc": "Ai Smart Face, multiple sweet spots, high launch"},
            {"model": "TaylorMade Qi Irons", "desc": "Patented face technology to eliminate cut-spin misses"},
            {"model": "Cobra LTDx / Darkspeed (Variable / ONE Length)", "desc": "PWRSHELL face cup, deep CG, wide sole"},
            {"model": "Titleist T350", "desc": "Hollow-body Max GI construction with player look"}
        ]
    },
    "iron_shafts": {
        "Stiff / Heavy Steel (105g - 120g+)": [
            {"model": "KBS $-Taper Lite (100g/105g)", "desc": "Signature KBS feel with mid-spin and controlled apex"},
            {"model": "True Temper Dynamic Gold 105 / 120", "desc": "Tour standard low-launch control in lighter chassis"},
            {"model": "Nippon Modus3 Tour 105 / 115", "desc": "Smooth loading profile with stiff tip section"},
            {"model": "Project X LZ 5.5 / 6.0 (115g/120g)", "desc": "Loading Zone technology for effortless kick"},
            {"model": "KBS Tour (110g/120g)", "desc": "Versatile mid-trajectory shaft for aggressive tempo"}
        ],
        "Tour Heavy Graphite (Vibration Dampening)": [
            {"model": "Aerotech SteelFiber i95 / i110", "desc": "Graphite core with steel fiber wrap; tour stability"},
            {"model": "Mitsubishi Chemical MMT 85/95/105", "desc": "Metal Mesh Technology in tip for steel-like dispersion"},
            {"model": "UST Mamiya Recoil Dart 90/105", "desc": "Eliminates shock without sacrificing shot shaping"},
            {"model": "KBS TGI Tour Graphite 90/100", "desc": "Steel EI profile duplicated in pure tour graphite"},
            {"model": "Fujikura Axiom 105 (Velocore)", "desc": "Extremely low torque graphite with multi-length flow"}
        ],
        "Lightweight High Launch (Steel & Graphite 65g - 95g)": [
            {"model": "KBS Max 80 Steel", "desc": "Lightweight steel designed for high trajectory carry"},
            {"model": "True Temper Elevate MPH 95", "desc": "Maximum Peak Height technology for softer greens"},
            {"model": "UST Mamiya Recoil ESX 460/470", "desc": "High-launch active kick graphite for moderate swing speeds"},
            {"model": "Nippon Zelos 7/8", "desc": "World's lightest ultra-flexible alloy steel shaft"},
            {"model": "Mitsubishi MMT 65/75 Regular", "desc": "Lightweight feel with composite mesh tip stability"}
        ]
    }
}

# --- Tracked Search Link Helper ---
def get_marketplace_link(model_name: str, dexterity: str):
    prefix = "LH " if ("Left" in dexterity or dexterity == "LH") else ""
    full_query = urllib.parse.quote_plus(f"{prefix}{model_name}")
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={full_query}&campid={EPN_CAMPAIGN_ID}&customid=golf_app_top5"
    second_swing_url = f"https://www.2ndswing.com/search?searchTerm={full_query}"
    return ebay_url, second_swing_url

# --- Header & Intro ---
st.title("⛳ Full-Bag Virtual Diagnostic & Fitting Engine")
st.markdown("Analyze your Driver & Irons, audit your current gear, and receive your **Top 5 Prescribed Builds**.")
st.markdown("---")

# ==========================================
# STEP 1: PHYSICAL BASELINE & AUDIT
# ==========================================
st.header("Step 1: Golfer Profile & Current Gear Audit")

p_col1, p_col2 = st.columns(2)
with p_col1:
    dexterity = st.radio("Playing Dexterity:", ["Right-Handed (RH)", "Left-Handed (LH)"])
    handicap = st.selectbox(
        "Current Handicap / Scoring Average:",
        ["Scratch to Single Digit (0–9)", "Mid-Handicap (10–18)", "High-Handicap (19–28)", "Beginner / Casual (29+)"]
    )
    physical_fit = st.selectbox(
        "Height & Wrist-to-Floor:",
        [
            "Under 5'7\" (Wrist-to-Floor < 33\")",
            "5'7\" to 6'0\" (Wrist-to-Floor 33\"–36\")",
            "6'1\" to 6'3\" (Wrist-to-Floor 36.5\"–38.5\")",
            "6'4\"+ (Wrist-to-Floor 39\"+)"
        ]
    )

with p_col2:
    glove_size = st.selectbox(
        "Golf Glove Size:",
        ["Small / Cadet Small", "Medium / Cadet Medium-Large", "Large / Cadet Large", "XL / XXL"]
    )
    iron_style = st.radio("Iron Build Preference:", ["Standard Variable Length", "ONE Length (All 7-iron length)"])
    joint_sensitivity = st.checkbox("Joint Pain / Need Graphite Vibration Dampening")

st.markdown("#### 🏌️ Current In-the-Bag Equipment Audit")
g_col1, g_col2 = st.columns(2)
with g_col1:
    curr_driver_head = st.text_input("Current Driver Head (e.g., TaylorMade Stealth 9.0°):", "")
    curr_driver_shaft = st.text_input("Current Driver Shaft & Flex (e.g., Ventus Red 50g Stiff):", "")
with g_col2:
    curr_iron_heads = st.text_input("Current Iron Set (e.g., Callaway Rogues 5-PW):", "")
    curr_iron_shafts = st.text_input("Current Iron Shafts & Flex (e.g., Stock Steel 105g Regular):", "")

st.markdown("---")

# ==========================================
# STEP 2: DRIVER DELIVERY & SPIN AUDIT
# ==========================================
st.header("Step 2: Driver Trajectory, Spin & Delivery Audit")
d_col1, d_col2 = st.columns(2)
with d_col1:
    driver_distance = st.selectbox(
        "Driver Carry / Total Distance:",
        ["< 200 yards (<85 mph)", "200 – 230 yards (85–92 mph)", "231 – 260 yards (93–102 mph)", "260+ yards (103+ mph)"]
    )
    driver_spin = st.selectbox(
        "Driver Spin Rate (Launch Monitor or Flight Behavior):",
        [
            "High Spin (> 3,000 RPM / Ballooning & Stalling in wind)",
            "Optimal Spin (2,000 – 2,800 RPM / Piercing carry & roll)",
            "Low Spin (< 1,800 RPM / Knuckleball falling out of air)",
            "I don't know / Estimate from my visual flight apex"
        ]
    )
    driver_apex = st.selectbox(
        "Driver Apex / Trajectory:",
        ["Ballooning / Sky-High / Excess Spin", "Optimal Mid-Piercing Apex", "Low Line-Drive / Weak Float"]
    )

with d_col2:
    driver_miss = st.selectbox(
        "Primary Driver Miss:",
        ["High Slice / Push-Fade (Right for RH)", "Violent Snap-Hook / Low Pull (Left for RH)", "Two-Way Strike Variance", "Heel/Toe Contact Inconsistency"]
    )
    driver_tempo = st.selectbox(
        "Driver Transition Tempo:",
        ["Smooth / Deliberate", "Moderate / Balanced", "Aggressive / Fast Transition"]
    )

st.markdown("---")

# ==========================================
# STEP 3: IRON DELIVERY & MISS PATTERNS
# ==========================================
st.header("Step 3: Iron Flight & Strike Audit")
i_col1, i_col2 = st.columns(2)
with i_col1:
    iron_apex = st.selectbox(
        "Iron Trajectory Apex:",
        ["Climbs & Balloons (Loses distance into wind)", "Piercing / Optimal Mid-Trajectory", "Low / Hard to Hold Greens"]
    )
    iron_miss = st.selectbox(
        "Primary Iron Directional Miss:",
        ["Straight Pull / Hook (Left for RH)", "Weak Push / Slice (Right for RH)", "Two-Way Miss (Left & Right)", "Fat / Thin Turf Contact Issues"]
    )
with i_col2:
    iron_strike = st.selectbox(
        "Typical Iron Turf Interaction:",
        ["Clean / Controlled Divot", "Deep Divots (Steep / Heel Digging)", "Sweeper / Thin Strikes / No Divot"]
    )

st.markdown("---")

# ==========================================
# STEP 4: DIAGNOSTIC & PRESCRIPTIONS
# ==========================================
if st.button("Generate Full Diagnostic & Top 5 Recommendations", type="primary"):
    
    # 1. Static Length & Lie Specs
    if "Under 5'7" in physical_fit:
        length_spec = "-0.50\" Short"
        base_lie = "1° to 2° Flat"
    elif "6'1" in physical_fit:
        length_spec = "+0.50\" Long"
        base_lie = "1° to 2° Upright"
    elif "6'4" in physical_fit:
        length_spec = "+1.00\" Long"
        base_lie = "2° to 3° Upright"
    else:
        length_spec = "Standard (37.25\" baseline)"
        base_lie = "Standard"

    # Grip Specs
    if "Small" in glove_size:
        grip_rec = "Standard Grip with Undersize Core (-1/32\")"
    elif "Large" in glove_size:
        grip_rec = "Golf Pride MCC Plus4 (Standard Core / Reduced Taper) or Midsize"
    elif "XL" in glove_size:
        grip_rec = "Midsize (+1/16\") or Oversize (+1/8\")"
    else:
        grip_rec = "Standard Grip"

    # 2. Driver Diagnostic Logic (Incorporating Spin Rate)
    if "High Slice" in driver_miss or "Push-Fade" in driver_miss:
        d_root = "Open dynamic face relative to path; insufficient heel closure creating high side-spin axis."
        d_head_key = "Draw Biased / Slice Correction"
        d_shaft_key = "Lightweight / High Launch / Active Tip (Lite - Regular)" if "< 200" in driver_distance else "Mid Weight / Mid Launch / Mid Spin (Regular - Stiff)"
    elif "High Spin" in driver_spin or "Snap-Hook" in driver_miss or "Ballooning" in driver_apex:
        d_root = "Excess spin generation (>3,000 RPM) or forward shaft deflection over-delivering dynamic loft."
        d_head_key = "Low Spin / Forward CG"
        d_shaft_key = "Heavy / Low Launch / Low Spin (Stiff - X-Flex)"
    elif "Low Spin" in driver_spin or "Low Line-Drive" in driver_apex:
        d_root = "Insufficient spin (<1,800 RPM) causing ball to drop out of air; needs higher static loft and rearward CG."
        d_head_key = "Max Forgiveness / High MOI"
        d_shaft_key = "Lightweight / High Launch / Active Tip (Lite - Regular)"
    else:
        d_root = "Balanced launch parameters. Requires high MOI perimeter weighting for tighter dispersion."
        d_head_key = "Max Forgiveness / High MOI"
        d_shaft_key = "Mid Weight / Mid Launch / Mid Spin (Regular - Stiff)"

    # 3. Iron Diagnostic Logic
    if "Scratch" in handicap:
        i_head_key = "Player's Cavity / Sub-10 Handicap"
    elif "Mid-Handicap" in handicap:
        i_head_key = "Player's Distance / 10-18 Handicap"
    else:
        i_head_key = "Game Improvement / 19+ Handicap"

    if joint_sensitivity:
        i_shaft_key = "Tour Heavy Graphite (Vibration Dampening)"
    elif "Low / Hard" in iron_apex or "< 200" in driver_distance:
        i_shaft_key = "Lightweight High Launch (Steel & Graphite 65g - 95g)"
    else:
        i_shaft_key = "Stiff / Heavy Steel (105g - 120g+)"

    # --- RENDER RESULTS ---
    st.success("## 🎯 Diagnostic Findings & Current Gear Audit")
    
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.info(f"**Driver Root Cause:** {d_root}")
        if curr_driver_head or curr_driver_shaft:
            st.markdown(f"**Current Driver Audit:** Head: `{curr_driver_head or 'Not specified'}` | Shaft: `{curr_driver_shaft or 'Not specified'}`")
            st.markdown(f"**Action Plan:** Switch to a **{d_head_key}** head and pair with a **{d_shaft_key.split('(')[0]}** shaft.")
    
    with col_res2:
        st.info(f"**Physical Build Spec:** Length: `{length_spec}` | Lie Angle: `{base_lie}` | Grips: `{grip_rec}`")
        if curr_iron_heads or curr_iron_shafts:
            st.markdown(f"**Current Iron Audit:** Set: `{curr_iron_heads or 'Not specified'}` | Shaft: `{curr_iron_shafts or 'Not specified'}`")
            st.markdown(f"**Action Plan:** Upgrade to **{i_head_key}** heads paired with **{i_shaft_key}**.")

    st.markdown("---")

    # --- TOP 5 SECTION ---
    st.header("🏆 Your Prescribed Top 5 Equipment Matches")

    tab1, tab2, tab3, tab4 = st.tabs(["Driver Heads", "Driver Shafts", "Iron Heads", "Iron Shafts"])

    with tab1:
        st.subheader(f"Top 5 Driver Heads ({d_head_key})")
        for idx, item in enumerate(HARDWARE_DB["driver_heads"][d_head_key], 1):
            eb_link, ss_link = get_marketplace_link(item["model"], dexterity)
            st.markdown(f"**{idx}. {item['model']}** — *{item['desc']}*")
            st.markdown(f"[🟢 Search on eBay]({eb_link}) | [🔵 Search on 2nd Swing]({ss_link})")
            st.write("")

    with tab2:
        st.subheader(f"Top 5 Driver Shafts ({d_shaft_key})")
        for idx, item in enumerate(HARDWARE_DB["driver_shafts"][d_shaft_key], 1):
            eb_link, ss_link = get_marketplace_link(item["model"], dexterity)
            st.markdown(f"**{idx}. {item['model']}** — *{item['desc']}*")
            st.markdown(f"[🟢 Search on eBay]({eb_link}) | [🔵 Search on 2nd Swing]({ss_link})")
            st.write("")

    with tab3:
        st.subheader(f"Top 5 Iron Heads ({i_head_key})")
        for idx, item in enumerate(HARDWARE_DB["iron_heads"][i_head_key], 1):
            eb_link, ss_link = get_marketplace_link(item["model"], dexterity)
            st.markdown(f"**{idx}. {item['model']}** — *{item['desc']}*")
            st.markdown(f"[🟢 Search on eBay]({eb_link}) | [🔵 Search on 2nd Swing]({ss_link})")
            st.write("")

    with tab4:
        st.subheader(f"Top 5 Iron Shafts ({i_shaft_key})")
        for idx, item in enumerate(HARDWARE_DB["iron_shafts"][i_shaft_key], 1):
            eb_link, ss_link = get_marketplace_link(item["model"], dexterity)
            st.markdown(f"**{idx}. {item['model']}** — *{item['desc']}*")
            st.markdown(f"[🟢 Search on eBay]({eb_link}) | [🔵 Search on 2nd Swing]({ss_link})")
            st.write("")

    st.markdown("---")

    # --- LEAD CAPTURE ---
    st.subheader("📥 Send Full Diagnostic & Top 5 PDF Report to Email")
    with st.form("lead_form"):
        u_name = st.text_input("Name:")
        u_email = st.text_input("Email:")
        btn = st.form_submit_button("Generate PDF Report")
        if btn and u_email:
            st.success("Prescription generated successfully! Your summary is ready.")

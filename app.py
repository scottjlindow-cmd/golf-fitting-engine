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

# --- Curated YouTube Drill Database ---
YOUTUBE_DRILLS_DB = {
    "driver": {
        "High Slice / Push-Fade (Right for RH)": {
            "title": "How to Stop Slicing Your Driver & Shallow the Club",
            "url": "https://www.youtube.com/watch?v=F3_6e_Y8Bpk",
            "focus": "Fixes open clubface angle and out-to-in swing path through impact."
        },
        "Violent Snap-Hook / Low Pull (Left for RH)": {
            "title": "Fix the Driver Snap Hook & Prevent Face Flipping",
            "url": "https://www.youtube.com/watch?v=Gcx_n_G6074",
            "focus": "Eliminates premature wrist release and stalling hip rotation."
        },
        "Two-Way Strike Variance": {
            "title": "Driver Tempo & Center Strike Consistency",
            "url": "https://www.youtube.com/watch?v=2Tz8dZq1lJw",
            "focus": "Syncs transition speed with body rotation for centered sweet-spot contact."
        },
        "Heel/Toe Contact Inconsistency": {
            "title": "Driver Sweet Spot Strike & Setup Distance Drill",
            "url": "https://www.youtube.com/watch?v=9g0Q_E8q0kQ",
            "focus": "Optimizes setup distance from ball to eliminate heel/toe gear effect."
        }
    },
    "iron": {
        "Straight Pull / Hook (Left for RH)": {
            "title": "Stop Pulling & Hooking Your Irons",
            "url": "https://www.youtube.com/watch?v=d_k8kL7T1bQ",
            "focus": "Teaches proper body clearance so the clubhead stays square to path."
        },
        "Weak Push / Slice (Right for RH)": {
            "title": "Pure Iron Compression & Eliminating the Slice",
            "url": "https://www.youtube.com/watch?v=8V9B7HjG8x4",
            "focus": "Promotes shaft lean and forward weight transfer into the lead side."
        },
        "Two-Way Miss (Left & Right)": {
            "title": "Consistent Iron Swing Path & Delivery",
            "url": "https://www.youtube.com/watch?v=5V2yW6w4HhY",
            "focus": "Builds repeatable backswing width and controlled transition."
        },
        "Fat / Thin Turf Contact Issues": {
            "title": "Perfect Iron Strike & Low Point Control Drill",
            "url": "https://www.youtube.com/watch?v=0kG7R3gZ1iE",
            "focus": "Controls swing bottom to guarantee crisp, ball-first turf contact."
        }
    }
}

# --- Equipment Dropdown Lists ---
POPULAR_DRIVER_HEADS = [
    "Not sure / Unlisted",
    "TaylorMade Qi10 / Qi10 Max / Qi10 LS",
    "TaylorMade Stealth / Stealth 2 / Plus / HD",
    "TaylorMade SIM / SIM2 / Max / D",
    "TaylorMade M5 / M6 / M3 / M4",
    "Callaway Paradym Ai Smoke (MAX / D / Triple Diamond)",
    "Callaway Paradym / Paradym X / Triple Diamond",
    "Callaway Rogue ST (MAX / LS / D)",
    "Callaway Epic Flash / Epic Speed / MAX",
    "Ping G430 (MAX / 10K / LST / SFT)",
    "Ping G425 (MAX / LST / SFT)",
    "Ping G410 (Plus / LST / SFT)",
    "Ping G400 (MAX / LST / SFT)",
    "Titleist TSR2 / TSR3 / TSR4",
    "Titleist TSi2 / TSi3 / TSi4",
    "Titleist TS2 / TS3 / TS4 / 917D",
    "Cobra Darkspeed (MAX / X / LS)",
    "Cobra Aerojet / LTDx / RadSpeed (Standard / MAX / LS)",
    "Cobra King F9 Speedback",
    "Mizuno ST-G / ST-Z / ST-X 230",
    "Srixon ZX5 / ZX7 Mk II",
    "PXG 0311 Black Ops / Gen5 / Gen6",
    "Other / Custom Head"
]

POPULAR_DRIVER_SHAFTS = [
    "Not sure / Stock OEM Shaft",
    "Fujikura Ventus Black / TR Black (X/Stiff)",
    "Fujikura Ventus Blue / TR Blue (Stiff/Reg)",
    "Fujikura Ventus Red / TR Red (Stiff/Reg)",
    "Fujikura Speeder NX / Motore X",
    "Mitsubishi Tensei AV Series / 1K Black / White",
    "Mitsubishi Tensei AV Raw Blue / Orange",
    "Mitsubishi Diamana GT / TB / ZF / PD",
    "Mitsubishi Kai'li Blue / White / Red",
    "Project X HZRDUS Smoke Black / RDX (6.0/6.5)",
    "Project X HZRDUS Smoke Blue / RDX",
    "Project X HZRDUS Smoke Red / Yellow",
    "Project X Cypher 40g/50g",
    "Graphite Design Tour AD (DI / UB / XC / VF / IZ)",
    "UST Mamiya LIN-Q M40X (White / Blue / Red)",
    "UST Mamiya Helium Nanocore (40g/50g)",
    "Aldila Rogue / Ascent / NV / NVS",
    "KBS TD Graphite",
    "Other / Custom Shaft"
]

POPULAR_IRON_HEADS = [
    "Not sure / Unlisted",
    "TaylorMade P790 / P770 / P7MB / P7MC",
    "TaylorMade Qi Irons / Qi HL",
    "TaylorMade Stealth / SIM2 Max / M2 / M4 / M6",
    "Callaway Apex 21 / Apex 24 (Standard / Pro / CB / DCB)",
    "Callaway Paradym / Paradym Ai Smoke (Standard / HL)",
    "Callaway Rogue ST (MAX / Pro / OS)",
    "Callaway Mavrik / Steelhead XR",
    "Ping i230 / i530 / i525 / i500",
    "Ping G430 / G425 / G410 / G400 / G710",
    "Ping Blueprint S / T",
    "Titleist T100 / T150 / T200 / T350",
    "Titleist 620 CB / MB / AP2 / AP1 / AP3",
    "Cobra King Forged Tec (Standard / ONE Length)",
    "Cobra LTDx / Darkspeed / Aerojet (Variable / ONE Length)",
    "Cobra RadSpeed / Speedzone (Standard / ONE Length)",
    "Mizuno JPX 923 / 921 (Hot Metal / Forged / Tour)",
    "Mizuno Pro 241 / 243 / 245",
    "Srixon ZX5 / ZX7 / ZX4 Mk II",
    "PXG 0311 Gen5 / Gen6 (P / XP / T)",
    "Other / Custom Irons"
]

POPULAR_IRON_SHAFTS = [
    "Not sure / Stock Steel",
    "True Temper Dynamic Gold (S300 / X100 / R300)",
    "True Temper Dynamic Gold 105 / 120 (S300/X100)",
    "True Temper Elevate 95 / MPH 95",
    "KBS $-Taper / $-Taper Lite",
    "KBS Tour / Tour 90 / Tour 105 / Tour 120",
    "KBS Max 80 Steel",
    "Nippon N.S. Pro Modus3 Tour 105 / 115 / 120",
    "Nippon N.S. Pro 950GH / 850GH / neo",
    "Nippon Zelos 7 / 8",
    "Project X LZ (5.0 / 5.5 / 6.0 / 6.5)",
    "Project X Rifle (5.5 / 6.0 / 6.5)",
    "Aerotech SteelFiber i95 / i110 / i80 (Graphite)",
    "Mitsubishi Chemical MMT 70 / 80 / 95 / 105 (Graphite)",
    "UST Mamiya Recoil Dart 75 / 90 / 105 (Graphite)",
    "UST Mamiya Recoil ESX 460 / 470 (Graphite)",
    "Other / Stock Graphite"
]

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
st.markdown("Analyze your Driver & Irons, upload gear photos and swing video, audit your setup, and receive your **Top 5 Prescribed Builds** + **Targeted YouTube Drills**.")
st.markdown("---")

# ==========================================
# STEP 1: PHYSICAL BASELINE & GEAR AUDIT
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
    curr_driver_head = st.selectbox("Current Driver Head:", POPULAR_DRIVER_HEADS)
    driver_head_photo = st.file_uploader("Upload Driver Head Photo (Optional):", type=["jpg", "jpeg", "png"], key="d_head_pic")
    if driver_head_photo:
        st.image(driver_head_photo, caption="Uploaded Driver Head", width=250)

    curr_driver_shaft = st.selectbox("Current Driver Shaft & Flex:", POPULAR_DRIVER_SHAFTS)
    driver_shaft_photo = st.file_uploader("Upload Driver Shaft Photo (Optional):", type=["jpg", "jpeg", "png"], key="d_shaft_pic")
    if driver_shaft_photo:
        st.image(driver_shaft_photo, caption="Uploaded Driver Shaft", width=250)

with g_col2:
    curr_iron_heads = st.selectbox("Current Iron Set:", POPULAR_IRON_HEADS)
    iron_head_photo = st.file_uploader("Upload Iron Head Photo (Optional):", type=["jpg", "jpeg", "png"], key="i_head_pic")
    if iron_head_photo:
        st.image(iron_head_photo, caption="Uploaded Iron Head", width=250)

    curr_iron_shafts = st.selectbox("Current Iron Shafts & Flex:", POPULAR_IRON_SHAFTS)
    iron_shaft_photo = st.file_uploader("Upload Iron Shaft Photo (Optional):", type=["jpg", "jpeg", "png"], key="i_shaft_pic")
    if iron_shaft_photo:
        st.image(iron_shaft_photo, caption="Uploaded Iron Shaft", width=250)

st.markdown("---")

# ==========================================
# STEP 2: DRIVER DELIVERY, SPIN & SWING VIDEO
# ==========================================
st.header("Step 2: Driver Trajectory, Spin & Swing Video")
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
    driver_video = st.file_uploader("Upload Driver Swing Video (Optional - MP4/MOV):", type=["mp4", "mov", "m4v"], key="d_vid")
    if driver_video:
        st.video(driver_video)

st.markdown("---")

# ==========================================
# STEP 3: IRON DELIVERY, MISS & SWING VIDEO
# ==========================================
st.header("Step 3: Iron Flight, Strike & Swing Video")
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
    iron_video = st.file_uploader("Upload Iron Swing Video (Optional - MP4/MOV):", type=["mp4", "mov", "m4v"], key="i_vid")
    if iron_video:
        st.video(iron_video)

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

    # --- COMPONENT COMPATIBILITY CHECKER (KEEP vs REPLACE) ---
    keep_driver_head = False
    if curr_driver_head not in ["Not sure / Unlisted", "Other / Custom Head"]:
        if d_head_key == "Low Spin / Forward CG" and any(k in curr_driver_head for k in ["LST", "LS", "Triple Diamond", "TSR3", "TSR4", "Plus", "RadSpeed", "Aerojet", "Darkspeed", "Qi10 LS", "Stealth Plus"]):
            keep_driver_head = True
        elif d_head_key == "Max Forgiveness / High MOI" and any(k in curr_driver_head for k in ["MAX", "10K", "TSR2", "Qi10 Max", "G430", "G425", "G410", "G400"]):
            keep_driver_head = True
        elif d_head_key == "Draw Biased / Slice Correction" and any(k in curr_driver_head for k in ["SFT", "MAX D", " D", "HD"]):
            keep_driver_head = True

    keep_driver_shaft = False
    if curr_driver_shaft not in ["Not sure / Stock OEM Shaft", "Other / Custom Shaft"]:
        if d_shaft_key == "Heavy / Low Launch / Low Spin (Stiff - X-Flex)" and any(k in curr_driver_shaft for k in ["Black", "RDX", "1K", "XC", "VF", "LIN-Q White"]):
            keep_driver_shaft = True
        elif d_shaft_key == "Mid Weight / Mid Launch / Mid Spin (Regular - Stiff)" and any(k in curr_driver_shaft for k in ["Blue", "DI", "Kai'li", "Helium 50"]):
            keep_driver_shaft = True
        elif d_shaft_key == "Lightweight / High Launch / Active Tip (Lite - Regular)" and any(k in curr_driver_shaft for k in ["Red", "Helium", "Speeder", "Ascent", "Cypher"]):
            keep_driver_shaft = True

    keep_iron_heads = False
    if curr_iron_heads not in ["Not sure / Unlisted", "Other / Custom Irons"]:
        if i_head_key == "Player's Cavity / Sub-10 Handicap" and any(k in curr_iron_heads for k in ["T100", "T150", "243", "Tour", "Blueprint", "Apex CB", "P770", "620"]):
            keep_iron_heads = True
        elif i_head_key == "Player's Distance / 10-18 Handicap" and any(k in curr_iron_heads for k in ["Forged Tec", "P790", "T200", "i530", "i525", "JPX 923 Forged", "Apex 21", "Apex 24"]):
            keep_iron_heads = True
        elif i_head_key == "Game Improvement / 19+ Handicap" and any(k in curr_iron_heads for k in ["G430", "G425", "G410", "G400", "Qi", "Stealth", "SIM2", "Hot Metal", "LTDx", "Darkspeed", "Ai Smoke", "T350"]):
            keep_iron_heads = True

    keep_iron_shafts = False
    if curr_iron_shafts not in ["Not sure / Stock Steel", "Other / Stock Graphite"]:
        if i_shaft_key == "Tour Heavy Graphite (Vibration Dampening)" and any(k in curr_iron_shafts for k in ["SteelFiber", "MMT", "Recoil Dart", "Axiom"]):
            keep_iron_shafts = True
        elif i_shaft_key == "Stiff / Heavy Steel (105g - 120g+)" and any(k in curr_iron_shafts for k in ["Dynamic Gold", "$-Taper", "Tour 105", "Tour 120", "Modus3", "Project X LZ"]):
            keep_iron_shafts = True
        elif i_shaft_key == "Lightweight High Launch (Steel & Graphite 65g - 95g)" and any(k in curr_iron_shafts for k in ["Max 80", "Elevate", "Zelos", "Recoil ESX"]):
            keep_iron_shafts = True

    # --- RENDER RESULTS ---
    st.success("## 🎯 Diagnostic Findings & Gear Component Analysis")
    
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.markdown("### 🏌️ Driver Component Analysis")
        st.info(f"**Root Cause Diagnosis:** {d_root}")
        
        # Driver Head Verdict
        if keep_driver_head:
            st.markdown(f"**Head Verdict:** ✅ **KEEP YOUR `{curr_driver_head}`** — This head matches your delivery profile. No need to spend money replacing it!")
        else:
            st.markdown(f"**Head Verdict:** 🔄 **UPGRADE RECOMMENDED** — Consider switching to a **{d_head_key}** head profile.")

        # Driver Shaft Verdict
        if keep_driver_shaft:
            st.markdown(f"**Shaft Verdict:** ✅ **KEEP YOUR `{curr_driver_shaft}`** — Your shaft weight and flex profile is already dialed.")
        else:
            st.markdown(f"**Shaft Verdict:** ⚠️ **RESHAFTOVERRIDE NEEDED** — Reshafting with a **{d_shaft_key.split('(')[0]}** will immediately stabilize your face angle and tighten dispersion.")

    with col_res2:
        st.markdown("### 🎯 Iron Component Analysis")
        st.info(f"**Physical Blueprint:** Length: `{length_spec}` | Lie: `{base_lie}` | Grip: `{grip_rec}`")

        # Iron Head Verdict
        if keep_iron_heads:
            st.markdown(f"**Iron Head Verdict:** ✅ **KEEP YOUR `{curr_iron_heads}`** — The forgiveness and offset match your game.")
        else:
            st.markdown(f"**Iron Head Verdict:** 🔄 **UPGRADE RECOMMENDED** — Transitioning to **{i_head_key}** will improve turf interaction and forgiveness.")

        # Iron Shaft Verdict
        if keep_iron_shafts:
            st.markdown(f"**Iron Shaft Verdict:** ✅ **KEEP YOUR `{curr_iron_shafts}`** — Shaft weight bracket is optimal.")
        else:
            st.markdown(f"**Iron Shaft Verdict:** ⚠️ **RESHAFTOVERRIDE NEEDED** — Upgrading to **{i_shaft_key}** will optimize your launch height and turf strike.")

    st.markdown("---")

    # --- TOP 5 SECTION ---
    st.header("🏆 Recommended Top 5 Equipment Matches")

    tab1, tab2, tab3, tab4 = st.tabs(["Top 5 Driver Heads", "Top 5 Driver Shafts", "Top 5 Iron Heads", "Top 5 Iron Shafts"])

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

    # --- YOUTUBE DRILLS SECTION ---
    st.header("📺 Prescribed YouTube Swing Drills for Your Delivery Flaws")
    
    y_col1, y_col2 = st.columns(2)
    
    with y_col1:
        d_drill = YOUTUBE_DRILLS_DB["driver"].get(driver_miss, YOUTUBE_DRILLS_DB["driver"]["Two-Way Strike Variance"])
        st.subheader("🏌️ Driver Mechanic Fix")
        st.markdown(f"**Drill:** {d_drill['title']}")
        st.caption(f"**Focus Area:** {d_drill['focus']}")
        st.video(d_drill["url"])

    with y_col2:
        i_drill = YOUTUBE_DRILLS_DB["iron"].get(iron_miss, YOUTUBE_DRILLS_DB["iron"]["Two-Way Miss (Left & Right)"])
        st.subheader("🎯 Iron Strike Fix")
        st.markdown(f"**Drill:** {i_drill['title']}")
        st.caption(f"**Focus Area:** {i_drill['focus']}")
        st.video(i_drill["url"])

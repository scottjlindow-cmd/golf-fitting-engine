import streamlit as st
import urllib.parse
from fpdf import FPDF
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="Tour Studio | Master Virtual Club Fitting",
    page_icon="🏌️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Configuration Constants ---
EPN_CAMPAIGN_ID = "YOUR_EPN_CAMPAIGN_ID"

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

# --- YouTube Drills Database ---
YOUTUBE_DRILLS_DB = {
    "driver": {
        "High Slice / Push-Fade (Right for RH)": {
            "title": "Fix the Slice & Shallow Your Driver Path",
            "url": "https://www.youtube.com/watch?v=F3_6e_Y8Bpk",
            "focus": "Neutralizes steep out-to-in swing path and promotes natural face squaring."
        },
        "Violent Snap-Hook / Low Pull (Left for RH)": {
            "title": "Eliminate the Driver Snap-Hook & Loft Flip",
            "url": "https://www.youtube.com/watch?v=Gcx_n_G6074",
            "focus": "Fixes early wrist release and stalled body rotation through impact."
        },
        "Two-Way Strike Variance": {
            "title": "Driver Transition Tempo & Strike Center",
            "url": "https://www.youtube.com/watch?v=2Tz8dZq1lJw",
            "focus": "Synchronizes arm swing with chest turn for sweet-spot impact."
        },
        "Heel/Toe Contact Inconsistency": {
            "title": "Driver Sweet Spot & Ball Distance Drill",
            "url": "https://www.youtube.com/watch?v=9g0Q_E8q0kQ",
            "focus": "Eliminates gear-effect spin variance by stabilizing setup distance."
        }
    },
    "iron": {
        "Straight Pull / Hook (Left for RH)": {
            "title": "Stop Pulling & Hooking Your Irons",
            "url": "https://www.youtube.com/watch?v=d_k8kL7T1bQ",
            "focus": "Teaches proper body clearance so the clubhead stays square to target."
        },
        "Weak Push / Slice (Right for RH)": {
            "title": "Pure Iron Compression & Eliminating the Slice",
            "url": "https://www.youtube.com/watch?v=8V9B7HjG8x4",
            "focus": "Promotes shaft lean and forward weight transfer into the lead side."
        },
        "Two-Way Miss (Left & Right)": {
            "title": "Consistent Iron Path & Delivery",
            "url": "https://www.youtube.com/watch?v=5V2yW6w4HhY",
            "focus": "Builds repeatable backswing width and controlled transition."
        },
        "Fat / Thin Turf Contact Issues": {
            "title": "Low Point Control & Ball-First Strike",
            "url": "https://www.youtube.com/watch?v=0kG7R3gZ1iE",
            "focus": "Controls swing bottom for crisp turf interaction."
        }
    }
}

# --- Tracked Search Link Helper ---
def get_marketplace_link(model_name: str, dexterity: str):
    prefix = "LH " if ("Left" in dexterity or dexterity == "LH") else ""
    full_query = urllib.parse.quote_plus(f"{prefix}{model_name}")
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={full_query}&campid={EPN_CAMPAIGN_ID}&customid=golf_fit_tour"
    second_swing_url = f"https://www.2ndswing.com/search?searchTerm={full_query}"
    return ebay_url, second_swing_url

# --- PDF Generation Class ---
class FittingReportPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 8, 'TOUR FITTING STUDIO | OFFICIAL BUILD SPECIFICATION SHEET', border=False, align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 5, 'Master Club Builder Hardware Blueprint & Diagnostic Breakdown', border=False, align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

# --- Header & Intro ---
st.title("🏌️‍♂️ Tour Studio | Master Virtual Club Fitting Session")
st.markdown(
    "Welcome to your automated Tour-level fitting appointment. "
    "We evaluate your **Biometrics**, **In-the-Bag Gear Compatibility**, **Launch & Spin Characteristics**, and **Swing Mechanics** to build your custom spec sheet."
)
st.markdown("---")

# ==========================================
# STAGE 1: GOLFER INTERVIEW & BIOMETRICS
# ==========================================
st.subheader("📋 Stage 1: Player Biometrics & Physical Baseline")
b_col1, b_col2 = st.columns(2)

with b_col1:
    dexterity = st.radio("Playing Dexterity:", ["Right-Handed (RH)", "Left-Handed (LH)"])
    handicap = st.selectbox(
        "Current Handicap / Scoring Average:",
        ["Scratch to Single Digit (0–9)", "Mid-Handicap (10–18)", "High-Handicap (19–28)", "Beginner / Casual (29+)"]
    )
    physical_fit = st.selectbox(
        "Height & Wrist-to-Floor Measurement:",
        [
            "Under 5'7\" (Wrist-to-Floor < 33\")",
            "5'7\" to 6'0\" (Wrist-to-Floor 33\"–36\")",
            "6'1\" to 6'3\" (Wrist-to-Floor 36.5\"–38.5\")",
            "6'4\"+ (Wrist-to-Floor 39\"+)"
        ]
    )

with b_col2:
    glove_size = st.selectbox(
        "Golf Glove Size (Hand Size Calibration):",
        ["Small / Cadet Small", "Medium / Cadet Medium-Large", "Large / Cadet Large", "XL / XXL"]
    )
    iron_style = st.radio("Iron Build Architecture:", ["Standard Variable Length", "ONE Length (Single-Length Build)"])
    joint_sensitivity = st.checkbox("Joint/Elbow Sensitivity (Prioritize Graphite Vibration Dampening)")

st.markdown("---")

# ==========================================
# STAGE 2: IN-THE-BAG GEAR AUDIT & PHOTOS
# ==========================================
st.subheader("🎒 Stage 2: In-the-Bag Equipment Audit & Component Upload")
st.caption("Upload photos so the builder can inspect face wear, hosel settings, and shaft labels.")

g_col1, g_col2 = st.columns(2)
with g_col1:
    st.markdown("**Driver Setup**")
    curr_driver_head = st.selectbox("Current Driver Head:", POPULAR_DRIVER_HEADS)
    driver_head_photo = st.file_uploader("Snap/Upload Driver Head Photo:", type=["jpg", "jpeg", "png"], key="d_head_pic")
    if driver_head_photo:
        st.image(driver_head_photo, caption="Current Driver Head", width=220)

    curr_driver_shaft = st.selectbox("Current Driver Shaft & Flex:", POPULAR_DRIVER_SHAFTS)
    driver_shaft_photo = st.file_uploader("Snap/Upload Driver Shaft Label:", type=["jpg", "jpeg", "png"], key="d_shaft_pic")
    if driver_shaft_photo:
        st.image(driver_shaft_photo, caption="Current Driver Shaft", width=220)

with g_col2:
    st.markdown("**Iron Setup**")
    curr_iron_heads = st.selectbox("Current Iron Set:", POPULAR_IRON_HEADS)
    iron_head_photo = st.file_uploader("Snap/Upload Iron Head / Sole Photo:", type=["jpg", "jpeg", "png"], key="i_head_pic")
    if iron_head_photo:
        st.image(iron_head_photo, caption="Current Iron Head", width=220)

    curr_iron_shafts = st.selectbox("Current Iron Shafts & Flex:", POPULAR_IRON_SHAFTS)
    iron_shaft_photo = st.file_uploader("Snap/Upload Iron Shaft Label:", type=["jpg", "jpeg", "png"], key="i_shaft_pic")
    if iron_shaft_photo:
        st.image(iron_shaft_photo, caption="Current Iron Shaft", width=220)

st.markdown("---")

# ==========================================
# STAGE 3: LAUNCH MONITOR & SWING MECHANICS
# ==========================================
st.subheader("📊 Stage 3: Launch Monitor Data, Delivery & Swing Videos")

l_col1, l_col2 = st.columns(2)
with l_col1:
    st.markdown("**Driver Delivery Metrics**")
    driver_distance = st.selectbox(
        "Driver Carry / Total Distance:",
        ["< 200 yards (<85 mph)", "200 – 230 yards (85–92 mph)", "231 – 260 yards (93–102 mph)", "260+ yards (103+ mph)"]
    )
    driver_spin = st.selectbox(
        "Driver Backspin Rate (Launch Monitor or Visual Flight):",
        [
            "High Spin (> 3,000 RPM / Ballooning & Stalling into wind)",
            "Optimal Spin (2,000 – 2,800 RPM / Piercing carry & roll)",
            "Low Spin (< 1,800 RPM / Knuckleball falling out of air)",
            "Estimate from my flight apex"
        ]
    )
    driver_miss = st.selectbox(
        "Driver Directional Miss Pattern:",
        ["High Slice / Push-Fade (Right for RH)", "Violent Snap-Hook / Low Pull (Left for RH)", "Two-Way Strike Variance", "Heel/Toe Contact Inconsistency"]
    )
    driver_tempo = st.selectbox(
        "Driver Transition Tempo (Shaft Load):",
        ["Smooth / Deliberate", "Moderate / Balanced", "Aggressive / Fast Transition"]
    )
    driver_video = st.file_uploader("Upload Driver Swing Video (MP4/MOV):", type=["mp4", "mov", "m4v"], key="d_vid")
    if driver_video:
        st.video(driver_video)

with l_col2:
    st.markdown("**Iron Delivery Metrics**")
    iron_apex = st.selectbox(
        "Iron Trajectory Apex:",
        ["Climbs & Balloons (Loses distance into wind)", "Piercing / Optimal Mid-Trajectory", "Low / Hard to Hold Greens"]
    )
    iron_miss = st.selectbox(
        "Iron Directional Miss Pattern:",
        ["Straight Pull / Hook (Left for RH)", "Weak Push / Slice (Right for RH)", "Two-Way Miss (Left & Right)", "Fat / Thin Turf Contact Issues"]
    )
    iron_strike = st.selectbox(
        "Iron Turf Interaction / Divot Depth:",
        ["Clean / Controlled Divot", "Deep Divots (Steep / Heel Digging)", "Sweeper / Thin Strikes / No Divot"]
    )
    iron_video = st.file_uploader("Upload Iron Swing Video (MP4/MOV):", type=["mp4", "mov", "m4v"], key="i_vid")
    if iron_video:
        st.video(iron_video)

st.markdown("---")

# ==========================================
# STAGE 4: MASTER FITTER RESULTS & SPEC SHEET
# ==========================================
if st.button("🔨 Run Master Fitting Diagnostic & Generate Full Blueprint", type="primary"):
    
    # 1. Physical Specs Calculation
    if "Under 5'7" in physical_fit:
        length_spec = "-0.50\" Short (36.75\" 7-Iron)"
        base_lie = "1° to 2° Flat"
        sw_spec = "D0 - D1"
    elif "6'1" in physical_fit:
        length_spec = "+0.50\" Long (37.75\" 7-Iron)"
        base_lie = "1° to 2° Upright"
        sw_spec = "D2 - D3"
    elif "6'4" in physical_fit:
        length_spec = "+1.00\" Long (38.25\" 7-Iron)"
        base_lie = "2° to 3° Upright"
        sw_spec = "D3 - D4"
    else:
        length_spec = "Standard (37.25\" 7-Iron baseline)"
        base_lie = "Standard Neutral"
        sw_spec = "D2"

    # Grip Specifications
    if "Small" in glove_size:
        grip_rec = "Standard Grip (-1/32\" Undersize core)"
    elif "Large" in glove_size:
        grip_rec = "Golf Pride MCC Plus4 (Standard Core / Reduced Lower-Hand Taper)"
    elif "XL" in glove_size:
        grip_rec = "Midsize (+1/16\") or Oversize (+1/8\")"
    else:
        grip_rec = "Standard Round Grip (58R/60R)"

    # 2. Driver Prescription Engine
    if "High Slice" in driver_miss or "Push-Fade" in driver_miss:
        d_root = "Dynamic face angle is open to swing path; excessive side-spin tilt."
        d_head_key = "Draw Biased / Slice Correction"
        d_shaft_key = "Lightweight / High Launch / Active Tip (Lite - Regular)" if "< 200" in driver_distance else "Mid Weight / Mid Launch / Mid Spin (Regular - Stiff)"
        d_hosel_rec = "+1.0° Upright Lie (Draw setting); Standard Loft"
        d_driver_length = "45.00\" (Tour Optimized)"
    elif "High Spin" in driver_spin or "Snap-Hook" in driver_miss or "Ballooning" in driver_apex:
        d_root = "Over-acceleration of soft-tip shaft forward kick delivering excessive dynamic loft and spin."
        d_head_key = "Low Spin / Forward CG"
        d_shaft_key = "Heavy / Low Launch / Low Spin (Stiff - X-Flex)"
        d_hosel_rec = "Lower -1.0° Loft sleeve setting (Opens face 1° to eliminate left miss)"
        d_driver_length = "44.75\" – 45.00\""
    elif "Low Spin" in driver_spin or "Low Line-Drive" in driver_apex:
        d_root = "Sub-optimal spin (<1,800 RPM) causing ball flight to drop prematurely; requires rearward CG lift."
        d_head_key = "Max Forgiveness / High MOI"
        d_shaft_key = "Lightweight / High Launch / Active Tip (Lite - Regular)"
        d_hosel_rec = "+1.0° to +1.5° Higher Loft setting"
        d_driver_length = "45.25\""
    else:
        d_root = "Balanced launch parameters. Requires high MOI chassis to tighten dispersion."
        d_head_key = "Max Forgiveness / High MOI"
        d_shaft_key = "Mid Weight / Mid Launch / Mid Spin (Regular - Stiff)"
        d_hosel_rec = "Standard Neutral"
        d_driver_length = "45.00\""

    # 3. Iron Prescription Engine
    if "Scratch" in handicap:
        i_head_key = "Player's Cavity / Sub-10 Handicap"
        offset_pref = "Minimal / Tour Blade offset"
    elif "Mid-Handicap" in handicap:
        i_head_key = "Player's Distance / 10-18 Handicap"
        offset_pref = "Low-to-Moderate offset (Player's Distance)"
    else:
        i_head_key = "Game Improvement / 19+ Handicap"
        offset_pref = "Moderate-to-High offset (Draw-promoting Game Improvement)"

    if joint_sensitivity:
        i_shaft_key = "Tour Heavy Graphite (Vibration Dampening)"
        shaft_mat = "Composite / SteelFiber Graphite"
    elif "Low / Hard" in iron_apex or "< 200" in driver_distance:
        i_shaft_key = "Lightweight High Launch (Steel & Graphite 65g - 95g)"
        shaft_mat = "Lightweight High-Rebound Alloy Steel"
    else:
        i_shaft_key = "Stiff / Heavy Steel (105g - 120g+)"
        shaft_mat = "Tour-Weight Stiff Steel (105g–120g)"

    # Dynamic Lie Angle Bend based on miss & strike
    if "Pull" in iron_miss or "Deep Divots" in iron_strike:
        final_lie_angle = f"{base_lie} (Adjusted 1.0° to 1.5° FLATTER to prevent heel grab)"
    elif "Push" in iron_miss or "Slice" in iron_miss:
        final_lie_angle = f"{base_lie} (Adjusted 1.0° to 1.5° MORE UPRIGHT to help square face)"
    else:
        final_lie_angle = base_lie

    # Component Keep vs Replace Verification
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

    # --- MASTER SPEC SHEET DISPLAY ---
    st.success("## 🏆 Master Club Builder Spec Sheet & Build Prescription")
    
    spec_col1, spec_col2 = st.columns(2)
    with spec_col1:
        st.markdown("### 🏌️ Driver Specification")
        st.write(f"**Clubhead Class:** {d_head_key}")
        st.write(f"**Optimal Playing Length:** {d_driver_length}")
        st.write(f"**Hosel / Sleeve Adjustment:** {d_hosel_rec}")
        st.write(f"**Prescribed Shaft Profile:** {d_shaft_key.split('(')[0]}")
        st.write(f"**Target Swingweight:** D3 – D4")
        st.write(f"**Grip Blueprint:** {grip_rec}")
        
    with spec_col2:
        st.markdown("### 🎯 Iron Specification")
        st.write(f"**Iron Head Profile:** {i_head_key}")
        st.write(f"**Length Blueprint:** {length_spec}")
        st.write(f"**Dynamic Lie Angle Bend:** {final_lie_angle}")
        st.write(f"**Prescribed Iron Shaft:** {i_shaft_key.split('(')[0]}")
        st.write(f"**Target Swingweight:** {sw_spec}")
        st.write(f"**Build Architecture:** {iron_style}")

    st.markdown("---")

    # --- IN-THE-BAG COMPONENT AUDIT VERDICT ---
    st.subheader("🔬 In-the-Bag Component Analysis (Keep vs. Reshaft vs. Replace)")
    
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.markdown("**Driver Bag Audit**")
        st.caption(f"Diagnosed delivery flaw: {d_root}")
        if keep_driver_head:
            st.success(f"✅ **KEEP HEAD:** `{curr_driver_head}` matches your CG & delivery profile.")
        else:
            st.warning(f"🔄 **UPGRADE HEAD:** Consider moving from `{curr_driver_head}` to a `{d_head_key}` head.")

        if keep_driver_shaft:
            st.success(f"✅ **KEEP SHAFT:** `{curr_driver_shaft}` flex & weight match your swing speed.")
        else:
            st.error(f"⚠️ **RESHAFTOVERRIDE:** Reshaft your head with a **{d_shaft_key.split('(')[0]}** to stabilize face angle.")

    with v_col2:
        st.markdown("**Iron Bag Audit**")
        st.caption(f"Diagnosed strike flaw: {final_lie_angle}")
        if keep_iron_heads:
            st.success(f"✅ **KEEP HEADS:** `{curr_iron_heads}` provide optimal sole geometry.")
        else:
            st.warning(f"🔄 **UPGRADE HEADS:** Move to `{i_head_key}` for proper launch & forgiveness.")

        if keep_iron_shafts:
            st.success(f"✅ **KEEP SHAFTS:** `{curr_iron_shafts}` weight bracket is dialed.")
        else:
            st.error(f"⚠️ **RESHAFTOVERRIDE:** Reshaft to **{i_shaft_key.split('(')[0]}** to eliminate ballooning/pulls.")

    st.markdown("---")

    # --- TOP 5 SECTION ---
    st.header("🛒 Top 5 Prescribed Builds & Search Market Links")
    t1, t2, t3, t4 = st.tabs(["Top 5 Driver Heads", "Top 5 Driver Shafts", "Top 5 Iron Heads", "Top 5 Iron Shafts"])

    with t1:
        for idx, item in enumerate(HARDWARE_DB["driver_heads"][d_head_key], 1):
            eb_link, ss_link = get_marketplace_link(item["model"], dexterity)
            st.markdown(f"**{idx}. {item['model']}** — *{item['desc']}*")
            st.markdown(f"[🟢 Search on eBay]({eb_link}) | [🔵 Search on 2nd Swing]({ss_link})")
            st.write("")

    with t2:
        for idx, item in enumerate(HARDWARE_DB["driver_shafts"][d_shaft_key], 1):
            eb_link, ss_link = get_marketplace_link(item["model"], dexterity)
            st.markdown(f"**{idx}. {item['model']}** — *{item['desc']}*")
            st.markdown(f"[🟢 Search on eBay]({eb_link}) | [🔵 Search on 2nd Swing]({ss_link})")
            st.write("")

    with t3:
        for idx, item in enumerate(HARDWARE_DB["iron_heads"][i_head_key], 1):
            eb_link, ss_link = get_marketplace_link(item["model"], dexterity)
            st.markdown(f"**{idx}. {item['model']}** — *{item['desc']}*")
            st.markdown(f"[🟢 Search on eBay]({eb_link}) | [🔵 Search on 2nd Swing]({ss_link})")
            st.write("")

    with t4:
        for idx, item in enumerate(HARDWARE_DB["iron_shafts"][i_shaft_key], 1):
            eb_link, ss_link = get_marketplace_link(item["model"], dexterity)
            st.markdown(f"**{idx}. {item['model']}** — *{item['desc']}*")
            st.markdown(f"[🟢 Search on eBay]({eb_link}) | [🔵 Search on 2nd Swing]({ss_link})")
            st.write("")

    st.markdown("---")

    # --- COACHING DRILLS SECTION ---
    st.header("📺 Mechanical Drills: Fix the Swing Delivery")
    dy_col1, dy_col2 = st.columns(2)
    with dy_col1:
        d_drill = YOUTUBE_DRILLS_DB["driver"].get(driver_miss, YOUTUBE_DRILLS_DB["driver"]["Two-Way Strike Variance"])
        st.subheader("🏌️ Driver Swing Drill")
        st.markdown(f"**{d_drill['title']}**")
        st.caption(f"Focus: {d_drill['focus']}")
        st.video(d_drill["url"])

    with dy_col2:
        i_drill = YOUTUBE_DRILLS_DB["iron"].get(iron_miss, YOUTUBE_DRILLS_DB["iron"]["Two-Way Miss (Left & Right)"])
        st.subheader("🎯 Iron Strike Drill")
        st.markdown(f"**{i_drill['title']}**")
        st.caption(f"Focus: {i_drill['focus']}")
        st.video(i_drill["url"])

    st.markdown("---")

    # --- OFFICIAL PDF DOWNLOAD ---
    st.subheader("📄 Download Your Official Custom Fitting Spec Sheet")
    pdf = FittingReportPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Driver Build Blueprint:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"- Head Category: {d_head_key}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"- Shaft Profile: {d_shaft_key}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"- Playing Length: {d_driver_length} | Hosel: {d_hosel_rec}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Iron Build Blueprint:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"- Head Profile: {i_head_key}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"- Length Adjustment: {length_spec}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"- Lie Angle Bend: {final_lie_angle}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"- Target Shaft: {i_shaft_key}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"- Grip Specification: {grip_rec}", new_x="LMARGIN", new_y="NEXT")

    pdf_bytes = bytes(pdf.output())
    st.download_button(
        label="📥 Download Official Tour Spec Sheet (PDF)",
        data=pdf_bytes,
        file_name="Tour_Custom_Fitting_Spec_Sheet.pdf",
        mime="application/pdf"
    )

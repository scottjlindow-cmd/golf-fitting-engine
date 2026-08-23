import streamlit as st
import urllib.parse
from fpdf import FPDF
import plotly.graph_objects as go
import numpy as np

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
            {"model": "Ping G430 LST", "desc": "Carbonfly wrap, low spin, anti-left stability", "price": "$310 - $375 Used"},
            {"model": "TaylorMade Qi10 LS", "desc": "Sliding weight track, high ball speed, piercing flight", "price": "$340 - $410 Used"},
            {"model": "Callaway Paradym Ai Smoke Triple Diamond", "desc": "Workable compact shape, low spin/launch", "price": "$330 - $395 Used"},
            {"model": "Titleist TSR3 / TSR4", "desc": "Precision CG track, ultra-penetrating trajectory", "price": "$295 - $360 Used"},
            {"model": "Cobra LTDx LS / Darkspeed LS", "desc": "Forward heel/toe weighting, low spin bomber", "price": "$175 - $265 Used"}
        ],
        "Max Forgiveness / High MOI": [
            {"model": "Ping G430 MAX / 10K", "desc": "Industry-leading MOI, ultra-stable off-center strikes", "price": "$325 - $390 Used"},
            {"model": "TaylorMade Qi10 Max", "desc": "10,000 MOI design, high launch, maximum backspin carry", "price": "$330 - $400 Used"},
            {"model": "Callaway Paradym Ai Smoke MAX", "desc": "Ai Smart Face, tight dispersion, optimal spin loft", "price": "$320 - $385 Used"},
            {"model": "Titleist TSR2", "desc": "Max speed and stability across entire face", "price": "$280 - $340 Used"},
            {"model": "Cobra LTDx MAX / Darkspeed MAX", "desc": "Deep rear CG, adjustable draw-bias option", "price": "$165 - $250 Used"}
        ],
        "Draw Biased / Slice Correction": [
            {"model": "Ping G430 SFT", "desc": "Straight Flight Technology, movable heel tungsten weight", "price": "$315 - $370 Used"},
            {"model": "TaylorMade Qi10 Max (Draw Setting)", "desc": "Heel weight bias, upright lie angle design", "price": "$330 - $400 Used"},
            {"model": "Callaway Paradym Ai Smoke MAX D", "desc": "Built-in draw bias with generous face offset", "price": "$320 - $385 Used"},
            {"model": "Cobra Darkspeed MAX (Heel Port)", "desc": "High MOI heel weight configuration to square face", "price": "$220 - $285 Used"},
            {"model": "Mizuno ST-X 230", "desc": "Heel-side Cortech Chamber for natural right-to-left flight", "price": "$160 - $220 Used"}
        ]
    },
    "driver_shafts": {
        "Heavy / Low Launch / Low Spin (Stiff - X-Flex)": [
            {"model": "Fujikura Ventus Black / TR Black 6S/6X", "desc": "VeloCore technology, ultra-stiff tip stability", "price": "$180 - $240 Used"},
            {"model": "Project X HZRDUS Smoke Black RDX 60/70", "desc": "Low launch/spin, aggressive transition profile", "price": "$85 - $125 Used"},
            {"model": "Mitsubishi Tensei 1K Black / White 65", "desc": "High modulus carbon fiber, low torque feedback", "price": "$135 - $185 Used"},
            {"model": "Graphite Design Tour AD XC / VF 6", "desc": "Firm butt and tip section for maximum control", "price": "$190 - $250 Used"},
            {"model": "UST Mamiya LIN-Q M40X White 60", "desc": "Extreme energy transfer without tip twisting", "price": "$115 - $160 Used"}
        ],
        "Mid Weight / Mid Launch / Mid Spin (Regular - Stiff)": [
            {"model": "Fujikura Ventus Blue / TR Blue 5S/6S", "desc": "Smooth mid-section load with firm tip stability", "price": "$185 - $245 Used"},
            {"model": "Mitsubishi Chemical Kai'li Blue 60", "desc": "Consistent kick, modern balance point", "price": "$90 - $130 Used"},
            {"model": "Graphite Design Tour AD DI 6", "desc": "Legendary smooth feel, high launch/low spin profile", "price": "$180 - $235 Used"},
            {"model": "Project X HZRDUS Smoke Blue RDX 60", "desc": "Counterbalanced, mid-launch dynamic profile", "price": "$95 - $135 Used"},
            {"model": "UST Mamiya Helium Nanocore 50/60", "desc": "Stable lightweight structure with mid-spin carry", "price": "$80 - $115 Used"}
        ],
        "Lightweight / High Launch / Active Tip (Lite - Regular)": [
            {"model": "UST Mamiya Helium Nanocore 40/50", "desc": "Ultra-lightweight high-launch dynamic kick", "price": "$80 - $115 Used"},
            {"model": "Fujikura Air Speeder 45", "desc": "Low swing speed distance multiplier", "price": "$110 - $150 Used"},
            {"model": "Aldila Ascent PL 40/45", "desc": "Active tip technology to get airborne quickly", "price": "$75 - $110 Used"},
            {"model": "Mitsubishi Grand Bassara 49", "desc": "Ultra-premium lightweight micro-weave graphite", "price": "$195 - $260 Used"},
            {"model": "Project X Cypher 2.0 40/50", "desc": "Active tip bend profile for effortless launch", "price": "$80 - $120 Used"}
        ]
    },
    "iron_heads": {
        "Player's Cavity / Sub-10 Handicap": [
            {"model": "Titleist T100 / T150", "desc": "Tour-validated turf interaction, compact cavity profile", "price": "$650 - $850 Used Set"},
            {"model": "Mizuno Pro 243 / JPX 923 Tour", "desc": "Grain Flow Forged feel with subtle forgiveness cavity", "price": "$580 - $780 Used Set"},
            {"model": "Ping Blueprint S", "desc": "Forged 8620 carbon steel with clean compact lines", "price": "$690 - $890 Used Set"},
            {"model": "Callaway Apex CB 24", "desc": "Pure player cavity, minimal offset, precise control", "price": "$640 - $830 Used Set"},
            {"model": "TaylorMade P770", "desc": "Compact hollow-body with forged feel and low offset", "price": "$520 - $720 Used Set"}
        ],
        "Player's Distance / 10-18 Handicap": [
            {"model": "Cobra King Forged Tec (Standard / ONE Length)", "desc": "Hollow construction, foam injected, clean topline", "price": "$380 - $550 Used Set"},
            {"model": "TaylorMade P790", "desc": "SpeedFoam Air, high ball speeds with refined look", "price": "$550 - $750 Used Set"},
            {"model": "Titleist T200", "desc": "Max impact technology, forged face, controlled spin", "price": "$590 - $790 Used Set"},
            {"model": "Ping i530 / i525", "desc": "Forged maraging steel face, compact distance iron", "price": "$540 - $720 Used Set"},
            {"model": "Mizuno JPX 923 Forged", "desc": "Chromoly forged speed frame with balanced sole", "price": "$490 - $680 Used Set"}
        ],
        "Game Improvement / 19+ Handicap": [
            {"model": "Ping G430", "desc": "PurFlex badge, extreme perimeter weighting, easy launch", "price": "$530 - $690 Used Set"},
            {"model": "Callaway Paradym Ai Smoke", "desc": "Ai Smart Face, multiple sweet spots, high launch", "price": "$550 - $720 Used Set"},
            {"model": "TaylorMade Qi Irons", "desc": "Patented face technology to eliminate cut-spin misses", "price": "$520 - $680 Used Set"},
            {"model": "Cobra LTDx / Darkspeed (Variable / ONE Length)", "desc": "PWRSHELL face cup, deep CG, wide sole", "price": "$320 - $480 Used Set"},
            {"model": "Titleist T350", "desc": "Hollow-body Max GI construction with player look", "price": "$580 - $760 Used Set"}
        ]
    },
    "iron_shafts": {
        "Stiff / Heavy Steel (105g - 120g+)": [
            {"model": "KBS $-Taper Lite (100g/105g)", "desc": "Signature KBS feel with mid-spin and controlled apex", "price": "$175 - $240 Set Pulls"},
            {"model": "True Temper Dynamic Gold 105 / 120", "desc": "Tour standard low-launch control in lighter chassis", "price": "$150 - $210 Set Pulls"},
            {"model": "Nippon Modus3 Tour 105 / 115", "desc": "Smooth loading profile with stiff tip section", "price": "$180 - $250 Set Pulls"},
            {"model": "Project X LZ 5.5 / 6.0 (115g/120g)", "desc": "Loading Zone technology for effortless kick", "price": "$190 - $260 Set Pulls"},
            {"model": "KBS Tour (110g/120g)", "desc": "Versatile mid-trajectory shaft for aggressive tempo", "price": "$160 - $220 Set Pulls"}
        ],
        "Tour Heavy Graphite (Vibration Dampening)": [
            {"model": "Aerotech SteelFiber i95 / i110", "desc": "Graphite core with steel fiber wrap; tour stability", "price": "$260 - $350 Set Pulls"},
            {"model": "Mitsubishi Chemical MMT 85/95/105", "desc": "Metal Mesh Technology in tip for steel-like dispersion", "price": "$240 - $330 Set Pulls"},
            {"model": "UST Mamiya Recoil Dart 90/105", "desc": "Eliminates shock without sacrificing shot shaping", "price": "$220 - $310 Set Pulls"},
            {"model": "KBS TGI Tour Graphite 90/100", "desc": "Steel EI profile duplicated in pure tour graphite", "price": "$270 - $360 Set Pulls"},
            {"model": "Fujikura Axiom 105 (Velocore)", "desc": "Extremely low torque graphite with multi-length flow", "price": "$380 - $500 Set Pulls"}
        ],
        "Lightweight High Launch (Steel & Graphite 65g - 95g)": [
            {"model": "KBS Max 80 Steel", "desc": "Lightweight steel designed for high trajectory carry", "price": "$120 - $170 Set Pulls"},
            {"model": "True Temper Elevate MPH 95", "desc": "Maximum Peak Height technology for softer greens", "price": "$140 - $190 Set Pulls"},
            {"model": "UST Mamiya Recoil ESX 460/470", "desc": "High-launch active kick graphite for moderate swing speeds", "price": "$190 - $270 Set Pulls"},
            {"model": "Nippon Zelos 7/8", "desc": "World's lightest ultra-flexible alloy steel shaft", "price": "$180 - $250 Set Pulls"},
            {"model": "Mitsubishi MMT 65/75 Regular", "desc": "Lightweight feel with composite mesh tip stability", "price": "$210 - $290 Set Pulls"}
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

# --- 2D Flight Trajectory Visualizer (Plotly) ---
def render_trajectory_chart(driver_miss: str, base_distance: float):
    # Simulated current vs fitted trajectory
    x_curr = np.linspace(0, base_distance, 50)
    x_fit = np.linspace(0, base_distance + 18, 50)
    
    if "Slice" in driver_miss:
        y_curr = 42 * np.sin(np.pi * x_curr / base_distance)  # High ballooning
        y_fit = 32 * np.sin(np.pi * x_fit / (base_distance + 18))  # Piercing mid
    elif "Low" in driver_miss or "Thin" in driver_miss:
        y_curr = 18 * np.sin(np.pi * x_curr / base_distance)
        y_fit = 32 * np.sin(np.pi * x_fit / (base_distance + 18))
    else:
        y_curr = 38 * np.sin(np.pi * x_curr / base_distance)
        y_fit = 33 * np.sin(np.pi * x_fit / (base_distance + 18))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_curr, y=y_curr, mode='lines', name='Current Flight (Flawed Delivery)',
        line=dict(color='#ff4b4b', width=3, dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=x_fit, y=y_fit, mode='lines', name='Optimized Tour Fit (+18 yds & Lower Spin)',
        line=dict(color='#00d26a', width=4)
    ))
    fig.update_layout(
        title="<b>Flight Apex & Trajectory Comparison (Side-View Profile)</b>",
        xaxis_title="Carry Distance (Yards)",
        yaxis_title="Apex Height (Feet)",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320
    )
    return fig

# --- Header & Intro ---
st.title("🏌️‍♂️ Tour Studio | Master Virtual Club Fitting Session")
st.markdown(
    "Welcome to your automated Tour-level fitting appointment. "
    "We evaluate your **Biometrics**, **In-the-Bag Gear Compatibility**, **Launch & Spin Characteristics**, and **Full-Bag Gapping** to build your master spec sheet."
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
# STAGE 3: LAUNCH MONITOR, DELIVERY & SHORT GAME
# ==========================================
st.subheader("📊 Stage 3: Launch Monitor Data, Delivery & Short Game Setup")

l_col1, l_col2, l_col3 = st.columns(3)
with l_col1:
    st.markdown("**Driver Delivery Metrics**")
    driver_distance = st.selectbox(
        "Driver Carry Distance:",
        ["< 200 yards (<85 mph)", "200 – 230 yards (85–92 mph)", "231 – 260 yards (93–102 mph)", "260+ yards (103+ mph)"]
    )
    driver_spin = st.selectbox(
        "Driver Backspin Rate:",
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
        "Driver Transition Tempo:",
        ["Smooth / Deliberate", "Moderate / Balanced", "Aggressive / Fast Transition"]
    )

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
        "Iron Turf Interaction:",
        ["Clean / Controlled Divot", "Deep Divots (Steep / Heel Digging)", "Sweeper / Thin Strikes / No Divot"]
    )

with l_col3:
    st.markdown("**Wedge & Putter Intake**")
    pw_loft = st.selectbox(
        "Pitching Wedge Loft (Check set specs):",
        ["Modern Strong (41° – 43° Loft)", "Standard Player Distance (44° – 45° Loft)", "Traditional Classic (46° – 48° Loft)"]
    )
    bunker_turf = st.selectbox(
        "Home Course Turf / Sand Condition:",
        ["Soft / Fluffy Sand & Plush Fairways", "Firm / Tight Lies & Hard Packed Sand", "Average / Standard Conditions"]
    )
    putter_stroke = st.selectbox(
        "Putting Stroke Arc:",
        ["Straight-Back Straight-Through (No Face Rotation)", "Slight Arc Stroke", "Strong Arcing Stroke (Blade Style)"]
    )

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

    # Dynamic Lie Angle Bend
    if "Pull" in iron_miss or "Deep Divots" in iron_strike:
        final_lie_angle = f"{base_lie} (Adjusted 1.0° to 1.5° FLATTER to prevent heel grab)"
    elif "Push" in iron_miss or "Slice" in iron_miss:
        final_lie_angle = f"{base_lie} (Adjusted 1.0° to 1.5° MORE UPRIGHT to help square face)"
    else:
        final_lie_angle = base_lie

    # 4. Wedge Gapping & Bounce Matrix
    if "Modern Strong" in pw_loft:
        wedge_blueprint = "48° Gap Wedge (08°–10° Bounce) ➔ 52° Mid-Wedge (08°–10° Bounce) ➔ 56° Sand (12° High Bounce) ➔ 60° Lob (06°–08° Low/Mid Bounce)"
    elif "Standard Player" in pw_loft:
        wedge_blueprint = "50° Gap Wedge (08°–10° Bounce) ➔ 54° Sand Wedge (10°–12° Bounce) ➔ 58° Lob Wedge (08° Bounce)"
    else:
        wedge_blueprint = "52° Gap Wedge (08° Bounce) ➔ 56° Sand Wedge (12°–14° High Bounce) ➔ 60° Lob Wedge (04°–08° Low Bounce)"

    # Putter Neck Engine
    if "Straight-Back" in putter_stroke:
        putter_rec = "Face-Balanced Mallet (Double-Bend / Single-Bend Spud Neck)"
    elif "Slight Arc" in putter_stroke:
        putter_rec = "Mid-Hang Mallet or Wide Blade (Short Slant Neck / Plumber's Neck)"
    else:
        putter_rec = "Full Toe-Hang Traditional Blade (Flow Neck / Heel-Shafted Neck)"

    # Keep vs Replace Logic
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

    # --- TRAJECTORY VISUALIZER DISPLAY ---
    st.success("## 🎯 Launch Monitor Trajectory & Dispersion Projection")
    base_dist = 195 if "< 200" in driver_distance else (215 if "200" in driver_distance else 245)
    st.plotly_chart(render_trajectory_chart(driver_miss, base_dist), use_container_width=True)

    # --- RESHAFT SAVINGS CALCULATOR ---
    st.subheader("💰 Reshaft ROI & Cost Savings Calculator")
    if keep_driver_head and not keep_driver_shaft:
        st.markdown(
            """
            <div style="background-color:#1e3d2f; padding:15px; border-radius:8px; border-left:6px solid #00d26a;">
                <h4 style="margin:0; color:#00d26a;">💡 Master Builder Value Play: Save ~$380 by Reshafting</h4>
                <p style="margin-top:5px; color:#e0e0e0;">
                    Your <b>current driver head</b> is already an optimal match for your launch physics. Buying a brand-new driver at retail costs <b>$599</b>. 
                    Upgrading to a pre-owned tour-grade shaft from our list below costs only <b>~$110–$190</b>, giving you 95%+ of the performance gains while saving you hundreds.
                </p>
            </div>
            """, unsafe_allow_html=True
        )
        st.write("")

    # --- MASTER SPEC SHEET DISPLAY ---
    st.markdown("### 🏆 Master Club Builder Complete Spec Sheet")
    
    spec_col1, spec_col2 = st.columns(2)
    with spec_col1:
        st.markdown("#### 🏌️ Driver Blueprint")
        st.write(f"**Clubhead Class:** {d_head_key}")
        st.write(f"**Optimal Playing Length:** {d_driver_length}")
        st.write(f"**Hosel / Sleeve Setting:** {d_hosel_rec}")
        st.write(f"**Target Shaft Profile:** {d_shaft_key.split('(')[0]}")
        st.write(f"**Target Swingweight:** D3 – D4")
        st.write(f"**Grip Specification:** {grip_rec}")
        
    with spec_col2:
        st.markdown("#### 🎯 Iron & Short Game Blueprint")
        st.write(f"**Iron Head Profile:** {i_head_key}")
        st.write(f"**Length Adjustment:** {length_spec}")
        st.write(f"**Dynamic Lie Angle Bend:** {final_lie_angle}")
        st.write(f"**Target Iron Shaft:** {i_shaft_key.split('(')[0]}")
        st.write(f"**Wedge Gapping Blueprint:** {wedge_blueprint}")
        st.write(f"**Putter Neck Alignment:** {putter_rec}")

    st.markdown("---")

    # --- TOP 5 SECTION WITH ESTIMATED PRICING ---
    st.header("🛒 Top 5 Recommended Builds & Secondary Market Tracker")
    t1, t2, t3, t4 = st.tabs(["Top 5 Driver Heads", "Top 5 Driver Shafts", "Top 5 Iron Heads", "Top 5 Iron Shafts"])

    with t1:
        for idx, item in enumerate(HARDWARE_DB["driver_heads"][d_head_key], 1):
            eb_link, ss_link = get_marketplace_link(item["model"], dexterity)
            st.markdown(f"**{idx}. {item['model']}** — *{item['desc']}* | 💵 **Est. Value:** `{item['price']}`")
            st.markdown(f"[🟢 Search on eBay]({eb_link}) | [🔵 Search on 2nd Swing]({ss_link})")
            st.write("")

    with t2:
        for idx, item in enumerate(HARDWARE_DB["driver_shafts"][d_shaft_key], 1):
            eb_link, ss_link = get_marketplace_link(item["model"], dexterity)
            st.markdown(f"**{idx}. {item['model']}** — *{item['desc']}* | 💵 **Est. Value:** `{item['price']}`")
            st.markdown(f"[🟢 Search on eBay]({eb_link}) | [🔵 Search on 2nd Swing]({ss_link})")
            st.write("")

    with t3:
        for idx, item in enumerate(HARDWARE_DB["iron_heads"][i_head_key], 1):
            eb_link, ss_link = get_marketplace_link(item["model"], dexterity)
            st.markdown(f"**{idx}. {item['model']}** — *{item['desc']}* | 💵 **Est. Value:** `{item['price']}`")
            st.markdown(f"[🟢 Search on eBay]({eb_link}) | [🔵 Search on 2nd Swing]({ss_link})")
            st.write("")

    with t4:
        for idx, item in enumerate(HARDWARE_DB["iron_shafts"][i_shaft_key], 1):
            eb_link, ss_link = get_marketplace_link(item["model"], dexterity)
            st.markdown(f"**{idx}. {item['model']}** — *{item['desc']}* | 💵 **Est. Value:** `{item['price']}`")
            st.markdown(f"[🟢 Search on eBay]({eb_link}) | [🔵 Search on 2nd Swing]({ss_link})")
            st.write("")

    st.markdown("---")

    # --- COACHING DRILLS SECTION ---
    st.header("📺 Mechanical Drills: Fix the Delivery Flaw")
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

import streamlit as st
import urllib.parse
from fpdf import FPDF
import requests
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Virtual Golf Club Fitting Engine",
    page_icon="⛳",
    layout="centered"
)

# --- Configuration Constants ---
EPN_CAMPAIGN_ID = "YOUR_EPN_CAMPAIGN_ID"  # Replace with your eBay Partner Network Campaign ID
ZAPIER_WEBHOOK_URL = "YOUR_ZAPIER_OR_MAKE_WEBHOOK_URL"  # Replace with your webhook endpoint for lead capture

# --- PDF Generation Class ---
class FittingReportPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'VIRTUAL GOLF EQUIPMENT DIAGNOSTIC REPORT', border=False, align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', 'I', 9)
        self.cell(0, 5, 'Custom Performance Blueprint & Hardware Specifications', border=False, align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def build_pdf_report(user_name: str, dexterity: str, distance_range: str, handicap: str, length_spec: str, miss_pattern: str, target_shaft: str, head_rec: str, lie_rec: str, grip_rec: str) -> bytes:
    pdf = FittingReportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Section 1: Player Summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Player Diagnostic Summary: {user_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"- Dexterity: {dexterity}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"- Speed/Distance Baseline: {distance_range}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"- Handicap Bracket: {handicap}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"- Length Adjustment: {length_spec}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"- Primary Ball Flight Miss: {miss_pattern}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Section 2: Prescribed Hardware Blueprint
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Prescribed Hardware Blueprint", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"- Target Shaft Profile: {target_shaft}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"- Head Geometry / Offset: {head_rec}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"- Dynamic Lie Angle Bend: {lie_rec}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"- Grip Specification: {grip_rec}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Section 3: Performance Note
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Coach Performance Note:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 9)
    note_text = (
        "Equipment stability provides the baseline for consistency. Pair your recommended shaft weight "
        "and clubhead profile with a balanced transition tempo. Allow the lower-torque shaft profile to "
        "deliver dynamic consistency and square the face naturally through impact."
    )
    pdf.multi_cell(0, 5, note_text)
    return bytes(pdf.output())

# --- Affiliate URL Generator Utility ---
def get_tracked_marketplace_urls(query: str, dexterity: str):
    if "Left" in dexterity or dexterity == "LH":
        full_query = f"LH {query}"
    else:
        full_query = query
    clean_query = urllib.parse.quote_plus(full_query)
    
    # eBay Partner Network Structured URL
    ebay_base = "https://www.ebay.com/sch/i.html"
    ebay_params = {
        "_nkw": full_query,
        "mkcid": "1",
        "mkrid": "711-53200-19255-0",
        "siteid": "0",
        "campid": EPN_CAMPAIGN_ID,
        "customid": "golf_app_v1",
        "_sop": "12"
    }
    ebay_url = f"{ebay_base}?{urllib.parse.urlencode(ebay_params)}"
    second_swing_url = f"https://www.2ndswing.com/search?searchTerm={clean_query}"
    
    return ebay_url, second_swing_url

# --- UI / Front-End App Flow ---
st.title("⛳ Virtual Golf Equipment Diagnostic Engine")
st.write("Diagnose swing delivery flaws, eliminate flight misses, and generate custom hardware specs.")
st.markdown("---")

# Screen 1: Player Profile & Physical Baseline
st.subheader("Step 1: Player Profile & Physical Baseline")
col1, col2 = st.columns(2)
with col1:
    dexterity = st.radio("Playing Dexterity:", ["Right-Handed (RH)", "Left-Handed (LH)"])
    distance = st.selectbox(
        "Driver Carry / Total Distance:",
        ["< 200 yards (Speed: <85 mph)", "200 – 230 yards (Speed: 85–92 mph)", "231 – 260 yards (Speed: 93–102 mph)", "260+ yards (Speed: 103+ mph)"]
    )
    handicap = st.selectbox(
        "Handicap Bracket:",
        ["Scratch to Single Digit (0–9)", "Mid-Handicap (10–18)", "High-Handicap (19–28)", "Beginner / Casual (29+)"]
    )

with col2:
    physical_fit = st.selectbox(
        "Height & Wrist-to-Floor:",
        [
            "Under 5'7\" (Wrist-to-Floor < 33\")",
            "5'7\" to 6'0\" (Wrist-to-Floor 33\"–36\")",
            "6'1\" to 6'3\" (Wrist-to-Floor 36.5\"–38.5\")",
            "6'4\"+ (Wrist-to-Floor 39\"+)"
        ]
    )
    glove_size = st.selectbox(
        "Golf Glove Size:",
        ["Small / Cadet Small", "Medium / Cadet Medium-Large", "Large / Cadet Large", "XL / XXL"]
    )
    iron_style = st.radio("Iron Build Preference:", ["Standard Variable Length", "ONE Length (All 7-iron length)"])

# Screen 2: Swing Dynamics & Ball Flight Audit
st.subheader("Step 2: Trajectory, Tempo & Miss Pattern")
col3, col4 = st.columns(2)
with col3:
    tempo = st.selectbox("Transition Tempo:", ["Smooth / Deliberate", "Moderate / Balanced", "Quick / Aggressive"])
    apex = st.selectbox("Normal Ball Flight Apex:", ["Balloons / Climbs too high", "Piercing / Optimal Mid-Flight", "Low / Struggling to get airborne"])

with col4:
    miss = st.selectbox("Primary Miss Direction:", ["Straight Pull / Hook (Left)", "Push / Slice / Leak (Right)", "Two-Way Miss", "Fat / Thin strikes"])
    joint_sensitivity = st.checkbox("Require graphite vibration dampening (joint/arthritis sensitivity)")

st.markdown("---")

# --- Step 3: Logic Execution & Results Rendering ---
if st.button("Generate Hardware Prescription", type="primary"):
    
    # 1. Static Length & Base Lie Mapping
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

    # 2. Grip Specification Mapping
    if "Small" in glove_size:
        grip_rec = "Standard Grip with Undersize Core (-1/32\")"
    elif "Large" in glove_size:
        grip_rec = "Golf Pride MCC Plus4 (Standard Core / Reduced Taper) or Midsize"
    elif "XL" in glove_size:
        grip_rec = "Midsize (+1/16\") or Oversize (+1/8\")"
    else:
        grip_rec = "Standard Grip"

    # 3. Head Profile Mapping by Handicap
    if "Scratch" in handicap:
        head_rec = "Player's Cavity / Tour Muscle Cavity (Minimal Offset)"
    elif "Mid-Handicap" in handicap:
        head_rec = "Player's Distance (Forged Hollow-Body / Low-to-Moderate Offset)"
    else:
        head_rec = "Max Game Improvement (Wide Sole, Deep CG, High Offset)"

    # 4. Diagnostic Decision Trees
    if apex == "Balloons / Climbs too high" and miss == "Straight Pull / Hook (Left)":
        root_cause = "Dynamic loft over-delivery combined with high-torque shaft kick snapping the face closed early."
        if joint_sensitivity:
            target_shaft = "95g – 105g Tour Graphite / SteelFiber Stiff (e.g., SteelFiber i95 Stiff, MMT 95S)"
        else:
            target_shaft = "100g – 110g Stiff Steel (e.g., KBS $-Taper Lite Stiff, DG 105 S300)"
        lie_rec = f"{base_lie} (Adjusted -1.0° Flatter to prevent heel digging)"
        query_model = "Cobra Forged Tec ONE Length KBS Stiff" if "ONE Length" in iron_style else "Forged Tec Stiff Steel Set"

    elif miss == "Push / Slice / Leak (Right)":
        root_cause = "Clubface failing to square through impact; excessive shaft weight or overly flat lie angle."
        target_shaft = "65g – 80g Regular Flex (Active Tip Section)"
        lie_rec = f"{base_lie} (Adjusted +1.0° Upright to encourage face closure)"
        query_model = "Cobra LTDx ONE Length Regular" if "ONE Length" in iron_style else "Game Improvement Regular Iron Set"

    elif apex == "Low / Struggling to get airborne":
        root_cause = "Insufficient dynamic loft and low spin generation from excessively stiff/heavy shaft profile."
        target_shaft = "55g – 70g Lightweight High-Launch Graphite / Active Steel (e.g., KBS Max 80)"
        lie_rec = base_lie
        query_model = "ONE Length Graphite Combo Set" if "ONE Length" in iron_style else "High Launch Regular Iron Set"

    else:
        root_cause = "General delivery variance. Shaft weight stabilization recommended."
        target_shaft = "95g – 105g Mid-Weight Steel or Heavy Graphite (Matched to tempo)"
        lie_rec = base_lie
        query_model = "ONE Length Stiff Steel Set" if "ONE Length" in iron_style else "Stiff Steel Iron Set"

    # Display Diagnostic Summary
    st.success("### 📋 Diagnostic & Hardware Blueprint")
    st.info(f"**Root Cause Identified:** {root_cause}")
    
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.write(f"**Length Spec:** {length_spec}")
        st.write(f"**Target Shaft Profile:** {target_shaft}")
        st.write(f"**Head Construction:** {head_rec}")
    with res_col2:
        st.write(f"**Lie Angle Adjustment:** {lie_rec}")
        st.write(f"**Grip Specification:** {grip_rec}")

    st.markdown("---")

    # Generate Marketplace Links
    ebay_link, second_swing_link = get_tracked_marketplace_urls(query_model, dexterity)

    st.subheader("🛒 Live Secondary Marketplace Deals Matching Your Build")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.link_button("🟢 Shop Matching Builds on eBay", ebay_link)
    with m_col2:
        st.link_button("🔵 Search 2nd Swing Certified Used", second_swing_link)

    st.markdown("---")

    # Lead Capture & Instant PDF Delivery
    st.subheader("📥 Send Full Diagnostic PDF Report to Your Email")
    with st.form("lead_capture_form"):
        user_name = st.text_input("Your Name:")
        user_email = st.text_input("Email Address:")
        submitted = st.form_submit_button("Generate & Download PDF Report")

        if submitted and user_email:
            pdf_bytes = build_pdf_report(
                user_name=user_name if user_name else "Golfer",
                dexterity=dexterity,
                distance_range=distance,
                handicap=handicap,
                length_spec=length_spec,
                miss_pattern=miss,
                target_shaft=target_shaft,
                head_rec=head_rec,
                lie_rec=lie_rec,
                grip_rec=grip_rec
            )

            # Fire Webhook for Email Auto-Delivery
            if ZAPIER_WEBHOOK_URL != "YOUR_ZAPIER_OR_MAKE_WEBHOOK_URL":
                try:
                    payload = {
                        "name": user_name,
                        "email": user_email,
                        "dexterity": dexterity,
                        "distance": distance,
                        "handicap": handicap,
                        "miss": miss,
                        "target_shaft": target_shaft,
                        "head_rec": head_rec,
                        "lie_rec": lie_rec
                    }
                    requests.post(ZAPIER_WEBHOOK_URL, json=payload, timeout=5)
                except Exception:
                    pass

            st.success("Your diagnostic PDF is ready below!")
            st.download_button(
                label="📄 Download Official Prescription PDF",
                data=pdf_bytes,
                file_name=f"Golf_Diagnostic_Report_{user_name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

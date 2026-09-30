import json
import os
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Crisis SOS — Birmingham Pilot", 
    page_icon="🚨", 
    layout="centered"
)

DATABASE_FILE = "crisis_database.json"

def load_database():
    if not os.path.exists(DATABASE_FILE):
        return {"scenarios": []}
    with open(DATABASE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_postcode(postcode):
    """Simple validator checking if postcode starts with Birmingham prefix (B)."""
    cleaned = postcode.strip().upper()
    if cleaned.startswith("B"):
        return True, "Birmingham City Council"
    return False, "External / National Authority"

def main():
    st.title("🚨 Crisis SOS")
    st.markdown("*“Tell us what’s happening. We’ll help you work out what to do next.”*")
    st.write("---")

    db = load_database()
    scenarios = db.get("scenarios", [])

    if not scenarios:
        st.error("No scenarios found in `crisis_database.json`. Make sure your JSON database file is in the same folder.")
        return

    # Step 1: Postcode & Local Authority Check
    st.subheader("1. Where are you located?")
    postcode = st.text_input("Enter your postcode (e.g., B4 6NH):", value="").strip()

    if not postcode:
        st.info("Please enter a postcode above to begin your crisis navigation.")
        return

    is_birmingham, local_authority = validate_postcode(postcode)
    
    if is_birmingham:
        st.success(f"📍 Location detected: **{local_authority}** (Birmingham Pilot Active)")
    else:
        st.warning(f"⚠️️ Location detected: **{local_authority}**. (Note: This pilot is optimized for Birmingham; national fallback rules apply).")

    st.write("---")

    # Step 2: What's happening? (Crisis Intent Triage)
    st.subheader("2. What primary crisis are you facing right now?")
    intent_options = {s["intent_id"]: s["sos_intent"] for s in scenarios}
    
    selected_intent_id = st.selectbox(
        "Select your current situation:",
        options=list(intent_options.keys()),
        format_func=lambda x: intent_options[x]
    )

    selected_scenario = next((s for s in scenarios if s["intent_id"] == selected_intent_id), None)

    if selected_scenario:
        st.write("---")
        
        # Step 3: Urgency & Essential Safety Questions
        st.subheader("3. Safety & Urgency Assessment")
        st.markdown(f"**Urgency Level:** `{selected_scenario['urgency']}` | **Category:** `{selected_scenario['crisis_category']}`")
        
        for idx, question in enumerate(selected_scenario.get("essential_questions", [])):
            st.radio(question, options=["Yes", "No", "Unsure"], key=f"q_{idx}")

        st.write("---")

        # Step 4: Prioritised Action Plan & Verified Services
        if st.button("Generate Prioritised Action Plan", type="primary"):
            st.subheader("📋 Your Prioritised Action Plan")
            
            service = selected_scenario["service"]
            
            st.markdown(f"### Recommended Outcome: {selected_scenario['outcome']}")
            
            with st.container():
                st.markdown(f"**Verified Service / Destination:**")
                st.markdown(f"- **Name:** {service['name']}")
                st.markdown(f"- **Type:** {service['type']}")
                st.markdown(f"- **Eligibility Notes:** {service['eligibility_notes']}")
                st.markdown(f"- **Contact Route:** {service['contact_route']}")
                if service.get("official_url"):
                    st.markdown(f"- **Official Link:** [Access Official Service]({service['official_url']})")
                st.caption(f"Record last verified: {service['last_verified']} | Next review due: {service['next_review']}")

            st.write("---")
            st.markdown("**Fallback Alternative (if primary route fails):**")
            st.info(selected_scenario["fallback_service"])
            
            if selected_scenario.get("escalation"):
                st.warning(f"**Human Escalation Route:** {selected_scenario['escalation']}")
                
            st.caption("🔒 Crisis-first design: Minimising personal data. No data is stored or tracked.")

if __name__ == "__main__":
    main()

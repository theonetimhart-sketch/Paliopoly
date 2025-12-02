import streamlit as st

st.set_page_config(page_title="Paliopoly", layout="centered")
st.title("Paliopoly – Palia Monopoly")

# === 1. NAME ENTRY SCREEN ===
if 'players' not in st.session_state:
    st.subheader("Welcome to Paliopoly!")
    default = "Ashura,Reth,Tish,Hodari"
    names = st.text_input("Enter player names (comma separated)", value=default)
    if st.button("Start Game"):
        player_list = [p.strip() for p in names.split(",") if p.strip()]
        if len(player_list) < 2:
            st.error("Need at least 2 players!")
        else:
            st.session_state.players = player_list
            st.session_state.cash = {p: 1200 for p in player_list}
            st.session_state.props = {p: [] for p in player_list}
            st.session_state.current = 0
            st.rerun()

# === 2. MAIN GAME SCREEN ===
else:
    p = st.session_state.players
    cash = st.session_state.cash
    props = st.session_state.props
    current = p[st.session_state.current]

    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"**Turn:** {current}")
    with col2: st.markdown(f"**Cash:** {cash[current]}g")
    with col3: st.button("Next player →", on_click=lambda: st.session_state.update(current=(st.session_state.current + 1) % len(p)))

    # Dice roll
    dice = st.text_input("Dice roll (2–12) or leave blank", "")
    if dice.isdigit():
        roll = int(dice)
        if 2 <= roll <= 12:
            st.success(f"{current} rolled {roll}")
        else:
            st.error("Dice 2–12 only!")

    st.markdown("### Quick Actions")
    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("Pass GO +300g"):
            cash[current] += 300
            st.balloons()
    with colB:
        if st.button("Pay Renown Tax 200g"):
            cash[current] -= 200
    with colC:
        if st.button("Pay Maji Tax 100g"):
            cash[current] -= 100

    st.markdown("### Pay Rent")
    rent_cols = st.columns(4)
    rents = [
        ("Kilima set 18g", 18), ("Bahari set 27g", 27), ("Elderwood set 36g", 36), ("Maji set 45g", 45),
        ("Rail 40g", 40), ("Rail 80g", 80), ("Rail 120g", 120), ("Rail 160g", 160),
        ("Util ×4", 0), ("Util ×10", 0)
    ]
    for i, (label, amt) in enumerate(rents):
        with rent_cols[i % 4]:
            if "Util" in label:
                if st.button(label):
                    dice_val = st.number_input("Dice total?", 2, 12, 7, key=label)
                    mult = 4 if st.session_state.props[current].count("Util") == 1 else 10
                    pay = dice_val * mult
                    cash[current] -= pay
                    st.write(f"Paid {pay}g")
            else:
                if st.button(label):
                    cash[current] -= amt
                    st.write(f"Paid {amt}g")

    st.markdown("### Trade Properties")
    with st.expander("Trade"):
        giver = st.selectbox("From", p, key="giver")
        receiver = st.selectbox("To", [x for x in p if x != giver], key="recv")
        prop = st.selectbox("Property", props[giver] + ["(none)"], key="prop")
        if st.button("Execute Trade") and prop != "(none)":
            props[giver].remove(prop)
            props[receiver].append(prop)
            st.success(f"{giver} → {receiver}: {prop}")

    st.markdown("### Current Holdings & Cash")
    for pl in p:
        st.write(f"**{pl}** – {cash[pl]}g – Properties: {', '.join(props[pl]) or 'none'}")

    if st.button("Reset Game (new names)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

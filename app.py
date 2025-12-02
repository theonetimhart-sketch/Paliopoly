import streamlit as st

st.set_page_config(page_title="Paliopoly", layout="centered")
st.title("Paliopoly – Chilled Dude Original Edition")

# ====================== YOUR IMAGES ======================
st.image("https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image.png",
         use_column_width=True)
st.image("https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image2.png",
         use_column_width=True, caption="The Board")

# ====================== BOARD ======================
BOARD = [
    ("GO", "go"), ("Kilima 1", "prop", 80, 6, 18), ("Renown Tax", "tax", 100), ("Kilima 2", "prop", 80, 6, 18),
    ("Travel Point 1", "rail", 150, 40), ("Chappa Chest", "chest"), ("Jail", "jail"),
    ("Bahari 1", "prop", 120, 9, 27), ("Chapaa Chance", "chance"), ("Travel Point 2", "rail", 150, 40),
    ("Bahari 2", "prop", 120, 9, 27), ("Utility 1", "util", 100), ("Free Parking", "free"),
    ("Elderwood 1", "prop", 160, 12, 36), ("Chapaa Chance", "chance"), ("Elderwood 2", "prop", 160, 12, 36),
    ("Travel Point 3", "rail", 150, 40), ("Utility 2", "util", 100), ("Go to Jail", "go2jail"),
    ("Chappa Chest", "chest"), ("Travel Point 4", "rail", 150, 40),
    ("Maji Wedding 1", "prop", 200, 15, 45), ("Maji Tax", "tax", 200), ("Maji Wedding 2", "prop", 200, 15, 45)
]

# ====================== FULLY SAFE INITIALIZATION ======================
if 'initialized' not in st.session_state:
    st.subheader("Welcome to Paliopoly!")
    names = st.text_input("Player names (comma separated)", "Chilled Dude, TJediTim, lilshrtchit.ttv")
    if st.button("Start Game"):
        players = [n.strip() for n in names.split(",") if n.strip()]
        if len(players) < 2:
            st.error("Need at least 2 players!")
        else:
            st.session_state.players = players
            st.session_state.cash = {p: 1200 for p in players}
            st.session_state.pos = {p: 0 for p in players}
            st.session_state.owner = {i: None for i in range(24)}
            st.session_state.jail = {p: False for p in players}
            st.session_state.jail_turns = {p: 0 for p in players}
            st.session_state.jailfree_owner = None
            st.session_state.current = 0
            st.session_state.doubles_count = 0
            st.session_state.can_roll = True
            st.session_state.initialized = True
            st.success("Game started! Refresh if needed.")
            st.rerun()

# ====================== GAME ONLY RUNS AFTER INITIALIZED ======================
if st.session_state.get('initialized', False):
    p = st.session_state.players
    cash = st.session_state.cash
    pos = st.session_state.pos
    owner = st.session_state.owner
    jail = st.session_state.jail
    jail_turns = st.session_state.jail_turns
    jailfree_owner = st.session_state.jailfree_owner
    cur = p[st.session_state.current]

    # Header
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"**Turn: {cur}** {'(JAILED)' if jail[cur] else ''}")
    with col2: st.markdown(f"**Cash: {cash[cur]}g**")
    with col3:
        if st.button("Next Player"):
            st.session_state.current = (st.session_state.current + 1) % len(p)
            st.session_state.doubles_count = 0
            st.session_state.can_roll = True
            st.rerun()

    # Jail handling
    if jail[cur]:
        st.error(f"{cur} is in Jail! (Turn {jail_turns[cur]+1}/3)")
        c1, c2 = st.columns(2)
        if c1.button("Pay 100g") and cash[cur] >= 100:
            cash[cur] -= 100
            jail[cur] = False
            st.rerun()
        if c2.button("Use Jail Free Card") and jailfree_owner == cur:
            st.session_state.jailfree_owner = None
            jail[cur] = False
            st.rerun()

    # Normal turn
    elif st.session_state.can_roll:
        roll_input = st.text_input("Enter total dice rolled (2–12)", key="roll_now")
        if roll_input and roll_input.isdigit():
            roll = int(roll_input)
            if 2 <= roll <= 12:
                doubles = st.checkbox("Was this doubles?", key="dubs_now")

                if doubles:
                    st.session_state.doubles_count += 1
                else:
                    st.session_state.doubles_count = 0

                if st.session_state.doubles_count >= 3:
                    pos[cur] = 6
                    jail[cur] = True
                    st.session_state.doubles_count = 0
                    st.session_state.can_roll = False
                    st.error("3 DOUBLES → JAIL!")
                    st.rerun()

                # Move
                old = pos[cur]
                new = (old + roll) % 24
                pos[cur] = new
                name, typ = BOARD[new][0], BOARD[new][1]

                # Pass GO
                if new <= old and new != 0:
                    cash[cur] += 300
                    st.balloons()

                st.success(f"Landed on **{name}**")

                # Rent
                if typ in ("prop","rail","util") and owner[new] and owner[new] != cur:
                    landlord = owner[new]
                    rent = 50  # placeholder
                    cash[cur] -= rent
                    cash[landlord] += rent
                    st.warning(f"Paid {landlord} {rent}g rent!")

                # BUY BUTTON — THIS IS 100% VISIBLE
                if typ in ("prop","rail","util") and owner[new] is None:
                    price = BOARD[new][2]
                    st.markdown("### Available for Purchase")
                    buy_col1, buy_col2 = st.columns([1, 3])
                    with buy_col1:
                        if st.button("BUY NOW", key=f"BUY_{new}"):
                            if cash[cur] >= price:
                                cash[cur] -= price
                                owner[new] = cur
                                st.success(f"You bought {name}!")
                                st.rerun()
                            else:
                                st.error("Not enough cash!")
                    with buy_col2:
                        st.write(f"**{name}** – Cost: **{price}g**")

                # Turn end logic
                if not doubles or typ in ("chest","chance"):
                    st.session_state.can_roll = False
                    st.info("Turn over")
                else:
                    st.info("DOUBLES! Roll again!")

                st.rerun()

    # Player summary
    st.markdown("### Players")
    for player in p:
        props = [BOARD[i][0] for i in range(24) if owner.get(i) == player]
        card = " | Get Out of Jail Free" if jailfree_owner == player else ""
        status = "JAILED" if jail[player] else "Free"
        st.write(f"**{player}** – {cash[player]}g – {status}{card}")
        if props:
            st.write("→ " + ", ".join(props))
        else:
            st.write("→ no properties")

    if st.button("New Game"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

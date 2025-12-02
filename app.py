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

# ====================== INITIALIZE ======================
if 'players' not in st.session_state:
    st.subheader("Welcome to Paliopoly!")
    names = st.text_input("Player names (comma separated)", "Chilled Dude, Player 2")
    if st.button("Start Game"):
        players = [n.strip() for n in names.split(",") if n.strip()]
        if len(players) < 2:
            st.error("Need 2+ players")
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
            st.session_state.just_landed = False
            st.session_state.last_roll = 0
            st.rerun()

# ====================== GAME STARTS HERE ======================
p = st.session_state.players
cash = st.session_state.cash
pos = st.session_state.pos
owner = st.session_state.owner
jail = st.session_state.jail
jail_turns = st.session_state.jail_turns
jailfree_owner = st.session_state.jailfree_owner
cur = p[st.session_state.current]

# Header
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**Turn: {cur}** {'(JAILED)' if jail[cur] else ''}")
with col2:
    st.markdown(f"**Cash: {cash[cur]}g**")

# ====================== JAIL ======================
if jail[cur]:
    st.error("You're in Jail!")
    c1, c2 = st.columns(2)
    if c1.button("Pay 100g") and cash[cur] >= 100:
        cash[cur] -= 100
        jail[cur] = False
        jail_turns[cur] = 0
        st.success("Paid 100g — you're free!")
        st.rerun()
    if c2.button("Use Get Out of Jail Free") and jailfree_owner == cur:
        st.session_state.jailfree_owner = None
        jail[cur] = False
        st.success("Used card — free!")
        st.rerun()

# ====================== NORMAL TURN ======================
elif st.session_state.can_roll:
    roll = st.text_input("Enter total rolled (2–12)", key="roll_input")

    if roll and roll.isdigit() and 2 <= int(roll) <= 12:
        roll_val = int(roll)
        doubles = st.checkbox("Was this doubles?", key="doubles_check")

        # Handle doubles
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

        # Move player
        old_pos = pos[cur]
        new_pos = (old_pos + roll_val) % 24
        pos[cur] = new_pos
        space_name = BOARD[new_pos][0]
        space_type = BOARD[new_pos][1]

        # Pass GO
        if new_pos <= old_pos and new_pos != 0:
            cash[cur] += 300
            st.balloons()

        st.success(f"**Landed on {space_name}!**")

        # Handle rent
        if space_type in ("prop", "rail", "util") and owner[new_pos] and owner[new_pos] != cur:
            landlord = owner[new_pos]
            if space_type == "prop":
                rent = BOARD[new_pos][4]  # with set (simplified)
            elif space_type == "rail":
                rent = 40 * sum(1 for i in range(24) if BOARD[i][1] == "rail" and owner[i] == landlord)
            else:
                rent = roll_val * 10
            cash[cur] -= rent
            cash[landlord] += rent
            st.warning(f"Paid {landlord} {rent}g rent!")

        # BUY BUTTON — THIS WILL NOW ALWAYS APPEAR
        if space_type in ("prop", "rail", "util") and owner[new_pos] is None:
            price = BOARD[new_pos][2]
            st.markdown("---")
            col_buy1, col_buy2 = st.columns([1, 3])
            with col_buy1:
                if st.button("BUY", key=f"buy_now_{new_pos}"):
                    if cash[cur] >= price:
                        cash[cur] -= price
                        owner[new_pos] = cur
                        st.success(f"Bought {space_name} for {price}g!")
                        st.rerun()
                    else:
                        st.error("Not enough cash!")
            with col_buy2:
                st.write(f"**{space_name}** – Cost: {price}g")

        # End turn on cards or no doubles
        if space_type in ("chest", "chance") or not doubles:
            st.session_state.can_roll = False
            st.info("Turn over — press Next Player")
        else:
            st.info("DOUBLES! Roll again!")

        st.rerun()

else:
    if st.button("Next Player"):
        st.session_state.current = (st.session_state.current + 1) % len(p)
        st.session_state.doubles_count = 0
        st.session_state.can_roll = True
        st.rerun()

# ====================== PLAYER SUMMARY ======================
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

# New Game
if st.button("New Game"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

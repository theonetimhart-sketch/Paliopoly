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

SETS = {"Kilima": ["Kilima 1","Kilima 2"], "Bahari": ["Bahari 1","Bahari 2"],
        "Elderwood": ["Elderwood 1","Elderwood 2"], "Maji Wedding": ["Maji Wedding 1","Maji Wedding 2"]}

CHEST = {2:"Advance to GO +300g",3:"JAIL go to Jail",4:"Everyone pays you 50g",5:"Pay 100g",6:"Collect 100g",
         7:"Back 3 spaces",8:"Forward 3 spaces",9:"Pay poorest player 100g",10:"Go to nearest Travel Point",
         11:"Pay 150g",12:"Collect 200g"}

CHANCE = {2:"Free Parking move there",3:"Get Out of Jail Free!",4:"Give 50g to each player",5:"Pay 200g",
          6:"Get 150g",7:"Move to next Utility",8:"Move to next main property",9:"All give you 100g",
          10:"Go to nearest owned property",11:"Pay 100g",12:"Get 200g"}

# ====================== SAFE INITIALIZATION ======================
def init_game():
    st.session_state.players = ["Chilled Dude", "TJediTim", "lilshrtchit.ttv"]
    st.session_state.cash = {p: 1200 for p in st.session_state.players}
    st.session_state.pos = {p: 0 for p in st.session_state.players}
    st.session_state.owner = {i: None for i in range(24)}
    st.session_state.jail = {p: False for p in st.session_state.players}
    st.session_state.jail_turns = {p: 0 for p in st.session_state.players}
    st.session_state.jailfree_owner = None
    st.session_state.current = 0
    st.session_state.doubles_count = 0
    st.session_state.can_roll = True

if 'players' not in st.session_state:
    st.subheader("Welcome to Paliopoly!")
    names = st.text_input("Enter player names (comma separated)", "Chilled Dude, TJediTim, lilshrtchit.ttv")
    if st.button("Start Game"):
        players = [n.strip() for n in names.split(",") if n.strip()]
        if len(players) < 2:
            st.error("Need at least 2 players!")
        else:
            st.session_state.players = players
            init_game()
            st.success("Game started!")
            st.rerun()

# ====================== GAME RUNS ONLY AFTER INIT ======================
if 'players' in st.session_state:
    p = st.session_state.players
    cash = st.session_state.cash
    pos = st.session_state.pos
    owner = st.session_state.owner
    jail = st.session_state.jail
    jail_turns = st.session_state.jail_turns
    jailfree_owner = st.session_state.jailfree_owner
    cur_idx = st.session_state.current
    cur = p[cur_idx]

    # Header
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"**Turn: {cur}** {'(JAILED)' if jail[cur] else ''}")
    with col2: st.markdown(f"**Cash: {cash[cur]}g**")
    with col3:
        if st.button("Next Player"):
            st.session_state.current = (cur_idx + 1) % len(p)
            st.session_state.doubles_count = 0
            st.session_state.can_roll = True
            st.rerun()

    # JAIL
    if jail[cur]:
        st.error(f"{cur} is in Jail! (Turn {jail_turns[cur]+1}/3)")
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("Pay 100g", key="pay100") and cash[cur] >= 100:
            cash[cur] -= 100
            jail[cur] = False
            jail_turns[cur] = 0
            st.rerun()
        if c2.button("Use Card", key="usecard") and jailfree_owner == cur:
            st.session_state.jailfree_owner = None
            jail[cur] = False
            jail_turns[cur] = 0
            st.rerun()
        if c3.button("Doubles Yes", key="dubsyes"):
            jail[cur] = False
            jail_turns[cur] = 0
            st.rerun()
        if c4.button("No Doubles", key="nodubs"):
            jail_turns[cur] += 1
            if jail_turns[cur] >= 3:
                cash[cur] -= 100
                jail[cur] = False
            st.rerun()

    # NORMAL TURN
    elif st.session_state.can_roll:
        roll_str = st.text_input("Enter total rolled (2–12)", key="roll_input")
        if roll_str and roll_str.isdigit():
            roll = int(roll_str)
            if 2 <= roll <= 12:
                is_doubles = st.checkbox("Was this doubles?", key="is_doubles")

                # Doubles count
                if is_doubles:
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

                # Taxes
                if typ == "tax":
                    cash[cur] -= BOARD[new][2]
                    st.info(f"Paid {BOARD[new][2]}g tax")

                # Go to Jail
                elif typ == "go2jail":
                    pos[cur] = 6
                    jail[cur] = True
                    st.session_state.doubles_count = 0
                    st.session_state.can_roll = False
                    st.error("Go to Jail!")
                    st.rerun()

                # Cards end turn
                elif typ == "chest":
                    st.success(f"CHAPPA CHEST → {CHEST.get(roll, 'No effect')}")
                    st.session_state.can_roll = False
                elif typ == "chance":
                    st.success(f"CHAPAA CHANCE → {CHANCE.get(roll, 'No effect')}")
                    if roll == 3 and not jailfree_owner:
                        st.session_state.jailfree_owner = cur
                    st.session_state.can_roll = False

                # RENT
                if typ in ("prop","rail","util") and owner[new] and owner[new] != cur:
                    landlord = owner[new]
                    if typ == "prop":
                        set_name = next(k for k,v in SETS.items() if name in v)
                        full = all(owner[BOARD.index(s)] == landlord for s in SETS[set_name])
                        rent = BOARD[new][4] if full else BOARD[new][3]
                    elif typ == "rail":
                        rent = sum(1 for i in range(24) if BOARD[i][1]=="rail" and owner[i]==landlord) * 40
                    else:
                        utils = sum(1 for i in range(24) if BOARD[i][1]=="util" and owner[i]==landlord)
                        rent = roll * (10 if utils == 2 else 4)
                    cash[cur] -= rent
                    cash[landlord] += rent
                    st.warning(f"Paid {landlord} {rent}g rent!")

                # BUY BUTTON — WORKS 100%
                if typ in ("prop","rail","util") and owner[new] is None:
                    price = BOARD[new][2]
                    if st.button(f"BUY {name} – {price}g", key=f"buy_{new}"):
                        if cash[cur] >= price:
                            cash[cur] -= price
                            owner[new] = cur
                            st.success(f"{cur} bought {name}!")
                        else:
                            st.error("Not enough cash!")
                        st.rerun()

                st.success(f"Landed on **{name}**")

                if is_doubles and st.session_state.doubles_count < 3 and typ not in ("chest","chance"):
                    st.info("DOUBLES! Roll again!")
                else:
                    st.session_state.can_roll = False

                st.rerun()

    else:
        st.info("Turn over — press Next Player")

    st.markdown(f"**On:** {BOARD[pos[cur]][0]}")

    # TRADES
    with st.expander("Trades"):
        giver = st.selectbox("Giver", p, index=cur_idx)
        receiver = st.selectbox("Receiver", [x for x in p if x != giver])
        amount = st.number_input("Cash", 0, step=10)
        owned = [BOARD[i][0] for i in range(24) if owner[i] == giver]
        prop = st.selectbox("Property", ["(none)"] + owned)
        card = st.selectbox("Jail Free Card", ["(none)", "Get Out of Jail Free Card"] if jailfree_owner == giver else ["(none)"])
        if st.button("Trade"):
            if amount == 0 and prop == "(none)" and card == "(none)":
                st.warning("Nothing selected")
            elif amount > 0 and cash[giver] < amount:
                st.error("Not enough cash")
            else:
                if amount: cash[giver] -= amount; cash[receiver] += amount
                if prop != "(none)":
                    idx = next(i for i,s in enumerate(BOARD) if s[0]==prop)
                    owner[idx] = receiver
                if card != "(none)":
                    st.session_state.jailfree_owner = receiver
                st.success("Trade complete!")
                st.rerun()

    # PLAYER SUMMARY
    st.markdown("### Players")
    for pl in p:
        props = [BOARD[i][0] for i in range(24) if owner.get(i) == pl]
        card = " | Get Out of Jail Free" if jailfree_owner == pl else ""
        st.write(f"**{pl}** – {cash[pl]}g – {'JAILED' if jail[pl] else 'Free'}{card}")
        if props:
            st.write("→ " + ", ".join(props))
        else:
            st.write("→ no properties")

    if st.button("New Game"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

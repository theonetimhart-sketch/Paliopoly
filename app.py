import streamlit as st

st.set_page_config(page_title="Paliopoly", layout="centered")
st.title("Paliopoly – Chilled Dude Official Referee App")

# ====================== IMAGES ======================
st.image("https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image.png",
         use_column_width=True)
st.image("https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image2.png",
         use_column_width=True, caption="The Board")

# ====================== BOARD ======================
BOARD = [
    ("GO", "go"), 
    ("Kilima 1", "prop", 80, 6, 18), ("Renown Tax", "tax", 100), ("Kilima 2", "prop", 80, 6, 18),
    ("Travel Point 1", "rail", 150, 40), ("Chappa Chest", "chest"), ("Jail", "jail"),
    ("Bahari 1", "prop", 120, 9, 27), ("Chapaa Chance", "chance"), ("Travel Point 2", "rail", 150, 40),
    ("Bahari 2", "prop", 120, 9, 27), ("Utility 1", "util", 100), ("Free Parking", "free"),
    ("Elderwood 1", "prop", 160, 12, 36), ("Chapaa Chance", "chance"), ("Elderwood 2", "prop", 160, 12, 36),
    ("Travel Point 3", "rail", 150, 40), ("Utility 2", "util", 100), ("Go to Jail", "go2jail"),
    ("Chappa Chest", "chest"), ("Travel Point 4", "rail", 150, 40),
    ("Maji Wedding 1", "prop", 200, 15, 45), ("Maji Tax", "tax", 200), ("Maji Wedding 2", "prop", 200, 15, 45)
]

# ====================== FIXED CARD ORDER (matches your in-game signs) ======================
# CHANGE THESE TO EXACTLY MATCH YOUR PHYSICAL DECK ORDER TOP → BOTTOM
# You only need to edit this once and it will always be correct

CHAPPA_CHEST_ORDER = [
    "Get Out of Jail Free! (Chappa Chest)",
    "Advance to GO → Collect 300g",
    "Bank error in your favor → Collect 200g",
    "Doctor's fees → Pay 150g",
    "From sale of stock → You get 150g",
    "You are assessed for street repairs → Pay 40g per property",
    "Chapaa holiday fund matures → Collect 100g",
    "Income tax refund → Collect 80g",
    "Life insurance matures → Collect 100g",
    "Pay hospital fees → 100g",
    "School fees → Pay 150g",
    "You inherit 200g from a distant relative",
    "Go back 3 spaces",
    # Add more if you have extras — exact order matters!
]

CHAPAA_CHANCE_ORDER = [
    "Get Out of Jail Free! (Chapaa Chance)",
    "Advance to GO → Collect 300g",
    "Go directly to Jail. Do not pass GO.",
    "Advance to Maji Wedding 1",
    "Advance to Travel Point 4 (if pass GO collect 300g)",
    "Bank pays you dividend → 150g",
    "Your building loan matures → Collect 150g",
    "You have won a crossword competition → Collect 100g",
    "Go back to Kilima 1",
    "Pay each player 50g (you're too rich)",
    "Drunk in charge → Fine 120g",
    "Speeding fine → 80g",
    # Add more if needed
]

# Auto-initialize decks in fixed order
if 'chest_index' not in st.session_state:
    st.session_state.chest_index = 0
    st.session_state.chance_index = 0

def draw_chest():
    card = CHAPPA_CHEST_ORDER[st.session_state.chest_index]
    st.session_state.chest_index = (st.session_state.chest_index + 1) % len(CHAPPA_CHEST_ORDER)
    return card

def draw_chance():
    card = CHAPAA_CHANCE_ORDER[st.session_state.chance_index]
    st.session_state.chance_index = (st.session_state.chance_index + 1) % len(CHAPAA_CHANCE_ORDER)
    return card

# ====================== INITIALIZATION ======================
if 'initialized' not in st.session_state:
    st.subheader("Paliopoly – Official In-Game Referee")
    st.write("This app follows your **real board & dice** exactly. Card order is fixed to match your signs!")
    names = st.text_input("Player names (comma separated)", "Chilled Dude, TJediTim, lilshrtchit.ttv")
    if st.button("Start Game"):
        players = [n.strip() for n in names.split(",") if n.strip()]
        if len(players) < 2:
            st.error("Need at least 2 players!")
        else:
            st.session_state.players = players
            st.session_state.cash = {p: 1200 for p in players}
            st.session_state.position = {p: 0 for p in players}
            st.session_state.properties = {i: None for i in range(len(BOARD))}
            st.session_state.in_jail = {p: False for p in players}
            st.session_state.jail_turns = {p: 0 for p in players}
            st.session_state.jail_free_card = None  # Will be set to player name when drawn
            st.session_state.current_player_idx = 0
            st.session_state.doubles_streak = 0
            st.session_state.rolled_this_turn = False
            st.session_state.landed_space = None
            st.session_state.last_message = ""
            st.session_state.chest_index = 0
            st.session_state.chance_index = 0
            st.session_state.initialized = True
            st.success("Synced to your real board! Ready when you are.")
            st.rerun()

# ====================== MAIN GAME ======================
if st.session_state.get('initialized', False):
    players = st.session_state.players
    current_idx = st.session_state.current_player_idx
    current = players[current_idx]
    
    cash = st.session_state.cash
    pos = st.session_state.position
    owner = st.session_state.properties
    jail = st.session_state.in_jail

    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        st.markdown(f"**Turn: {current}** {'JAILED' if jail[current] else ''}")
    with col2:
        st.markdown(f"**Cash: {cash[current]}g**")
    with col3:
        st.write(f"Space: {BOARD[pos[current]][0]}")
    with col4:
        if st.button("Next Player ➡️"):
            st.session_state.current_player_idx = (current_idx + 1) % len(players)
            st.session_state.doubles_streak = 0
            st.session_state.rolled_this_turn = False
            st.session_state.landed_space = None
            st.session_state.last_message = ""
            st.rerun()

    if st.session_state.last_message:
        st.info(st.session_state.last_message)

    st.divider()

    # JAIL
    if jail[current]:
        st.error(f"{current} is in Jail! (Turn {st.session_state.jail_turns[current]+1}/3)")
        j1, j2 = st.columns(2)
        with j1:
            if st.button("Pay 100g") and cash[current] >= 100:
                cash[current] -= 100
                jail[current] = False
                st.session_state.jail_turns[current] = 0
                st.session_state.last_message = "Paid 100g fine → Free!"
                st.rerun()
        with j2:
            if st.button("Use Jail Free Card") and st.session_state.jail_free_card == current:
                st.session_state.jail_free_card = None
                jail[current] = False
                st.session_state.jail_turns[current] = 0
                st.session_state.last_message = "Used Get Out of Jail Free!"
                st.rerun()
        st.session_state.jail_turns[current] += 1
        if st.session_state.jail_turns[current] >= 3:
            if cash[current] >= 100:
                cash[current] -= 100
                jail[current] = False
                st.session_state.last_message = "3 turns served → Paid 100g and released"
                st.rerun()
        st.stop()

    # ROLL INPUT
    if not st.session_state.rolled_this_turn:
        st.info("Enter your real dice roll below:")
        roll = st.number_input("Total rolled (2–12)", min_value=2, max_value=12, step=1, key="roll_input")
        doubles = st.checkbox("Was it doubles?", key="dubs")
        if st.button("Confirm Roll"):
            if doubles:
                st.session_state.doubles_streak += 1
                if st.session_state.doubles_streak >= 3:
                    pos[current] = 6
                    jail[current] = True
                    st.session_state.last_message = "3 DOUBLES → STRAIGHT TO JAIL!"
                    st.session_state.rolled_this_turn = True
                    st.rerun()
            else:
                st.session_state.doubles_streak = 0

            old = pos[current]
            new = (old + roll) % len(BOARD)
            pos[current] = new
            st.session_state.landed_space = new
            st.session_state.rolled_this_turn = True

            crossed_go = new < old or (old + roll >= len(BOARD))
            if crossed_go and new != 0:
                cash[current] += 0  # Wait — you said 300g on GO only, not passing
                st.session_state.last_message = f"Moved {roll} → {BOARD[new][0]}"
            else:
                st.session_state.last_message = f"Landed on {BOARD[new][0]}"

            # Auto-handle landing
            space = BOARD[new]
            name, typ = space[0], space[1]

            if typ == "tax":
                tax = space[2]
                cash[current] -= tax
                st.session_state.last_message = f"Paid {tax}g {name}!"

            elif typ == "go2jail":
                pos[current] = 6
                jail[current] = True
                st.session_state.last_message = "GO TO JAIL! Do not pass GO."

            elif typ in ("prop", "rail", "util") and owner[new] and owner[new] != current:
                landlord = owner[new]
                rent = 0
                if typ == "prop": rent = space[3]
                elif typ == "rail":
                    count = sum(1 for i,o in owner.items() if o==landlord and BOARD[i][1]=="rail")
                    rent = 40 * (2 ** (count-1))
                elif typ == "util":
                    count = sum(1 for i,o in owner.items() if o==landlord and BOARD[i][1]=="util")
                    rent = roll * (10 if count==1 else 20)
                cash[current] -= rent
                cash[landlord] += rent
                st.session_state.last_message = f"Paid {landlord} {rent}g rent on {name}!"

            elif typ == "chest":
                card = draw_chest()
                st.session_state.last_message = f"Chappa Chest: {card}"
                if "Jail Free" in card:
                    st.session_state.jail_free_card = current

            elif typ == "chance":
                card = draw_chance()
                st.session_state.last_message = f"Chapaa Chance: {card}"
                if "Jail Free" in card:
                    st.session_state.jail_free_card = current
                elif "directly to Jail" in card:
                    pos[current] = 6
                    jail[current] = True

            st.rerun()

    # BUY PROPERTY
    landed = st.session_state.landed_space
    if landed and BOARD[landed][1] in ("prop","rail","util") and owner[landed] is None:
        price = BOARD[landed][2]
        name = BOARD[landed][0]
        if st.button(f"BUY {name} for {price}g", key=f"buy_{landed}"):
            if cash[current] >= price:
                cash[current] -= price
                owner[landed] = current
                st.session_state.last_message = f"{current} bought {name}!"
                st.rerun()

    # PLAYER SUMMARY
    st.markdown("### Players")
    for i, p in enumerate(players):
        props = [BOARD[j][0] for j, o in owner.items() if o == p]
        card = " | Get Out of Jail Free" if st.session_state.jail_free_card == p else ""
        status = "JAILED" if jail[p] else "Free"
        marker = "→" if i == current_idx else "  "
        st.write(f"{marker} **{p}** – {cash[p]}g – {status}{card}")
        if props:
            st.caption("   " + " • ".join(props))

    if st.button("Reset Everything (New Game)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

import streamlit as st

st.set_page_config(page_title="Paliopoly – Chilled Dude Edition", layout="centered")
st.title("Paliopoly – Official In-Game Referee")
st.markdown("**Real board • Real dice • Real signs • Zero surprises**")

# ======================
# Editable flavour text
# ======================
# Chest & Chance texts are separate for easy editing. Effects below use these texts unchanged.
CHEST_TEXT = {
    2: "Advance to GO! (+300g) — A friendly PelicanPilot gives you a lift to Kilima!",
    3: "GO TO JAIL! — A mischievous Sifuu teleports you to the holding pens.",
    4: "Everyone pays you 50g — The villagers chip in to celebrate your charm.",
    5: "Pay 100g — A capybara steals part of your picnic.",
    6: "Collect 100g — You discover a tucked-away coin pouch.",
    7: "Go back 3 spaces — A glowing root tangles your feet and drags you back.",
    8: "Go forward 3 spaces — A playful air sprite zips you ahead.",
    9: "Pay poorest player 100g — You help out the most in-need villager.",
    10: "Go to nearest Travel Point — A travelling merchant points you toward the nearest post.",
    11: "Pay 150g — You contribute to the town festival.",
    12: "Collect 200g — You find a generous tip from a grateful traveler."
}

CHANCE_TEXT = {
    2: "Free Parking! Collect pot — A Sernuk unearths treasure at Free Parking.",
    3: "Get Out of Jail Free! — A Chapaa slips you a secret key.",
    4: "Give 50g to everyone — Your pouch overflows and you share the joy.",
    5: "Pay 200g — You accidentally break a vendor's stall.",
    6: "Collect 150g — You win a small contest at the square.",
    7: "Move to next shrub — A mischievous creature nudges you to the next shrub.",
    8: "Move to next main property — A traveling guide points you onward.",
    9: "Everyone gives you 100g — The crowd showers you with gifts.",
    10: "Go to nearest owned property — You are summoned to the nearest owned property.",
    11: "Pay 100g — Pay a small local fee.",
    12: "Collect 200g — A surprise reward arrives!"
}

# ====================== IMAGES ======================
st.image(
    "https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image.png",
    use_column_width=True
)
st.image(
    "https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image2.png",
    use_column_width=True, caption="The Board"
)

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

FREE_PARKING_INDEX = 12  # confirmed

# ====================== INITIALIZATION ======================
if 'initialized' not in st.session_state:
    st.session_state.free_parking_pot = 0
    st.subheader("Start Paliopoly Session")
    names = st.text_input("Player names", "Chilled Dude, TJediTim, lilshrtchit.ttv")
    if st.button("Start Game"):
        players = [n.strip() for n in names.split(",") if n.strip()]
        if len(players) < 2:
            st.error("Need 2+ players!")
        else:
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.players_list = players
            st.session_state.cash = {p: 1200 for p in players}
            st.session_state.position = {p: 0 for p in players}
            st.session_state.properties = {i: None for i in range(len(BOARD))}
            st.session_state.in_jail = {p: False for p in players}
            st.session_state.jail_turns = {p: 0 for p in players}
            st.session_state.jail_free_card = None
            st.session_state.current_idx = 0
            st.session_state.doubles_streak = 0
            st.session_state.rolled = False
            st.session_state.landed = None
            st.session_state.last_message = ""
            st.session_state.trade_mode = False
            st.session_state.starting_square = ""
            st.session_state.free_parking_pot = 0
            st.session_state.initialized = True
            st.success("Game started! Roll those real dice!")
            st.rerun()

# ====================== MAIN GAME ======================
if st.session_state.get('initialized', False):
    players_list = st.session_state.players_list
    cur_idx = st.session_state.current_idx
    cur = players_list[cur_idx]
    cash = st.session_state.cash
    pos = st.session_state.position
    owner = st.session_state.properties
    jail = st.session_state.in_jail
    pot = st.session_state.free_parking_pot

    # === SET STARTING SQUARE AT BEGINNING OF TURN ===
    if not st.session_state.rolled and st.session_state.get("starting_square", "") == "":
        st.session_state.starting_square = BOARD[pos[cur]][0]

    # HEADER — NOW SHOWS STARTING SQUARE
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2.5, 2.5])
    with col1:
        st.markdown(f"**Turn: {cur}** {'JAILED' if jail[cur] else ''}")
    with col2:
        st.markdown(f"**Gold: {cash[cur]}g**")
    with col3:
        st.markdown(f"**Pot: {pot}g**")
    with col4:
        if st.session_state.rolled:
            st.success(f"Started on: **{st.session_state.starting_square}**")
        else:
            st.info(f"Starting on: **{BOARD[pos[cur]][0]}**")
    with col5:
        if st.session_state.rolled:
            if st.button("Next Player", type="primary", use_container_width=True):
                st.session_state.current_idx = (cur_idx + 1) % len(players_list)
                st.session_state.doubles_streak = 0
                st.session_state.rolled = False
                st.session_state.landed = None
                st.session_state.trade_mode = False
                st.session_state.last_message = ""
                st.session_state.starting_square = ""
                st.rerun()
        else:
            st.button("Next Player", disabled=True, use_container_width=True)
            st.caption("Roll first!")
    if st.session_state.last_message:
        st.success(st.session_state.last_message)

    # === HELPERS ===
    def add_cash(player, amount):
        st.session_state.cash[player] = max(0, st.session_state.cash.get(player, 0) + amount)

    def move_player(player, new_pos):
        st.session_state.position[player] = new_pos

    def pay_each_from(player_from, amount_each):
        for p in players_list:
            if p == player_from:
                continue
            add_cash(p, amount_each)
            add_cash(player_from, -amount_each)

    def collect_each_to(player_to, amount_each):
        for p in players_list:
            if p == player_to:
                continue
            add_cash(p, -amount_each)
            add_cash(player_to, amount_each)

    def poorest_player():
        return min(players_list, key=lambda x: st.session_state.cash.get(x, 0))

    def next_forward_index(current_pos, candidates):
        for i in candidates:
            if i > current_pos:
                return i
        return candidates[0]

    # === CHEST EFFECTS (logic preserved) ===
    def apply_chest_effect(roll):
        # Keep original behaviour — return flavour text from CHEST_TEXT
        # Effects preserved exactly; only implementation cleaned up.
        if roll == 2:
            move_player(cur, 0)
            add_cash(cur, 300)
        elif roll == 3:
            move_player(cur, 6)
            st.session_state.in_jail[cur] = True
        elif roll == 4:
            for pl in players_list:
                if pl == cur:
                    continue
                add_cash(pl, -50)
                add_cash(cur, 50)
        elif roll == 5:
            add_cash(cur, -100)
        elif roll == 6:
            add_cash(cur, 100)
        elif roll == 7:
            move_player(cur, (pos[cur] - 3) % len(BOARD))
        elif roll == 8:
            move_player(cur, (pos[cur] + 3) % len(BOARD))
        elif roll == 9:
            poor = poorest_player()
            if st.session_state.cash.get(cur, 0) >= 100:
                add_cash(cur, -100)
                add_cash(poor, 100)
        elif roll == 10:
            travel_points = [4, 9, 16, 21]
            next_tp = min(travel_points, key=lambda x: (x - pos[cur]) % len(BOARD))
            move_player(cur, next_tp)
        elif roll == 11:
            add_cash(cur, -150)
        elif roll == 12:
            add_cash(cur, 200)
        # return text for UI display
        return CHEST_TEXT.get(roll, "?? Unknown roll ??")

    # === CHANCE EFFECTS (logic preserved) ===
    def apply_chance_effect(roll):
        # Keep original behaviour — return flavour text from CHANCE_TEXT
        if roll == 2:
            # Free Parking collect pot
            move_player(cur, FREE_PARKING_INDEX)
            add_cash(cur, st.session_state.free_parking_pot)
            st.session_state.update({"free_parking_pot": 0})
        elif roll == 3:
            st.session_state.update({"jail_free_card": cur})
        elif roll == 4:
            for pl in players_list:
                if pl == cur:
                    continue
                add_cash(pl, 50)
                add_cash(cur, -50)
        elif roll == 5:
            add_cash(cur, -200)
        elif roll == 6:
            add_cash(cur, 150)
        elif roll == 7:
            shrubs = [13, 15, 22, 24]
            nxt = next((i for i in shrubs if i > pos[cur]), shrubs[0])
            move_player(cur, nxt)
        elif roll == 8:
            mains = [1, 3, 7, 10, 13, 15, 22, 24]
            nxt = next((i for i in mains if i > pos[cur]), mains[0])
            move_player(cur, nxt)
        elif roll == 9:
            for pl in players_list:
                if pl == cur:
                    continue
                add_cash(pl, -100)
                add_cash(cur, 100)
        elif roll == 10:
            owned_indices = [i for i, o in st.session_state.properties.items() if o and BOARD[i][1] in ("prop", "rail", "util")]
            if owned_indices:
                nearest = min(owned_indices, key=lambda x: (x - pos[cur]) % len(BOARD))
                move_player(cur, nearest)
        elif roll == 11:
            add_cash(cur, -100)
        elif roll == 12:
            add_cash(cur, 200)
        return CHANCE_TEXT.get(roll, "?? Unknown roll ??")

    # TRADE (unchanged placeholder)
    if st.button("Trade / Deal" if not st.session_state.trade_mode else "Cancel Trade"):
        st.session_state.trade_mode = not st.session_state.trade_mode
        st.rerun()
    if st.session_state.trade_mode:
        st.info("Trade mode active — (your trade UI code here)")

    st.divider()

    # JAIL LOGIC (placeholder)
    if jail[cur]:
        st.warning("Player is in jail — (jail logic not shown here if unchanged)")

    # ROLL & LANDING
    if not st.session_state.rolled:
        st.info("Enter your **real dice roll**")
        roll = st.number_input("Total rolled", 2, 12, 7, step=1, key="roll_input")
        doubles = st.checkbox("Doubles?", key="dubs_input")
        if st.button("Confirm Roll", type="primary"):
            st.session_state.last_roll = roll
            if doubles:
                st.session_state.doubles_streak += 1
                if st.session_state.doubles_streak >= 3:
                    move_player(cur, 6)
                    st.session_state.in_jail[cur] = True
                    st.session_state.last_message = "3 DOUBLES → JAIL!"
                    st.rerun()
            else:
                st.session_state.doubles_streak = 0

            old_pos = pos[cur]
            new_pos = (old_pos + roll) % len(BOARD)
            move_player(cur, new_pos)
            st.session_state.landed = new_pos
            st.session_state.rolled = True
            crossed_go = new_pos < old_pos or (old_pos + roll >= len(BOARD))
            if crossed_go and new_pos != 0:
                add_cash(cur, 300)
                st.balloons()

            space = BOARD[new_pos]
            name, typ = space[0], space[1]
            msg = f"Landed on **{name}**"
            if typ == "tax":
                tax = space[2]
                add_cash(cur, -tax)
                st.session_state.free_parking_pot += tax
                msg = f"Paid **{tax}g {name}** → added to Free Parking pot!"
            elif typ == "free":
                if st.session_state.free_parking_pot > 0:
                    add_cash(cur, st.session_state.free_parking_pot)
                    msg = f"FREE PARKING JACKPOT! Collected **{st.session_state.free_parking_pot}g**"
                    st.session_state.update({"free_parking_pot": 0})
                    st.balloons()
                else:
                    msg = "Free Parking — no pot yet!"
            elif typ == "go2jail":
                move_player(cur, 6)
                st.session_state.in_jail[cur] = True
                msg = "GO TO JAIL!"
            elif typ in ("prop", "rail", "util") and owner[new_pos] and owner[new_pos] != cur:
                landlord = owner[new_pos]
                if typ == "prop":
                    rent = space[3]
                elif typ == "rail":
                    rails_owned = sum(1 for i, o in owner.items() if o == landlord and BOARD[i][1] == "rail")
                    rent = 40 * (2 ** (rails_owned - 1)) if rails_owned >= 1 else 40
                else:  # util
                    utils_owned = sum(1 for i, o in owner.items() if o == landlord and BOARD[i][1] == "util")
                    rent = roll * (10 if utils_owned == 1 else 20)
                add_cash(cur, -rent)
                add_cash(landlord, rent)
                msg = f"Paid **{landlord}** {rent}g rent on **{name}**!"
            elif typ == "chest":
                text = apply_chest_effect(roll)
                msg = f"Chappa Chest → {text}"
            elif typ == "chance":
                text = apply_chance_effect(roll)
                msg = f"Chapaa Chance → {text}"

            st.session_state.last_message = msg
            st.rerun()

    # PLAYER SUMMARY
    st.write("### Player summary")
    for pl in players_list:
        st.write(f"{pl}: Gold {st.session_state.cash[pl]}g — Position {st.session_state.position[pl]} — In jail: {st.session_state.in_jail[pl]}")

    if st.button("New Game (Reset Everything)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]

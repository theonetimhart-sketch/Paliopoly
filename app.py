import streamlit as st

st.set_page_config(page_title="Paliopoly", layout="centered")
st.title("🤑 Paliopoly – Chilled Dude Original Edition")

# ====================== IMAGES ======================
st.image("https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image.png",
         use_column_width=True)
st.image("https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image2.png",
         use_column_width=True, caption="The Board")

# ====================== BOARD DEFINITION ======================
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

# ====================== SAFE INITIALIZATION ======================
if 'initialized' not in st.session_state:
    st.subheader("🎲 Welcome to Paliopoly!")
    names = st.text_input("Player names (comma separated)", "Chilled Dude, TJediTim, lilshrtchit.ttv")
    if st.button("🚀 Start Game"):
        players = [n.strip() for n in names.split(",") if n.strip()]
        if len(players) < 2:
            st.error("Need at least 2 players bro!")
        else:
            st.session_state.players = players
            st.session_state.cash = {p: 1200 for p in players}
            st.session_state.position = {p: 0 for p in players}
            st.session_state.properties = {i: None for i in range(len(BOARD))}
            st.session_state.in_jail = {p: False for p in players}
            st.session_state.jail_turns = {p: 0 for p in players}
            st.session_state.jail_free_card = None
            st.session_state.current_player_idx = 0
            st.session_state.doubles_streak = 0
            st.session_state.rolled_this_turn = False
            st.session_state.landed_space = None  # Track where they landed this turn
            st.session_state.initialized = True
            st.success("Game on! Let’s get this gold flowing 💸")
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

    # Header
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        st.markdown(f"**Turn: {current}** {'🔒 JAILED' if jail[current] else ''}")
    with col2:
        st.markdown(f"**Cash: {cash[current]}g**")
    with col3:
        st.write(f"Position: {pos[current]} → {BOARD[pos[current]][0]}")
    with col4:
        if st.button("Next ➡️", use_container_width=True):
            st.session_state.current_player_idx = (current_idx + 1) % len(players)
            st.session_state.doubles_streak = 0
            st.session_state.rolled_this_turn = False
            st.session_state.landed_space = None
            st.rerun()

    st.divider()

    # ==================== JAIL LOGIC ====================
    if jail[current]:
        st.error(f"🔒 {current} is in Jail! (Turn {st.session_state.jail_turns[current] + 1}/3)")
        j1, j2, j3 = st.columns(3)
        with j1:
            if st.button("Pay 100g fine", key="pay_fine"):
                if cash[current] >= 100:
                    cash[current] -= 100
                    jail[current] = False
                    st.session_state.jail_turns[current] = 0
                    st.success("Paid fine. You're free!")
                    st.rerun()
                else:
                    st.error("Broke ahh can't even pay jail fine 😂")
        with j2:
            if st.button("Use Get Out of Jail Free", key="use_card") and st.session_state.jail_free_card == current:
                st.session_state.jail_free_card = None
                jail[current] = False
                st.session_state.jail_turns[current] = 0
                st.success("Used card! Freedom tastes sweet.")
                st.rerun()
        with j3:
            if st.button("Roll for doubles (not implemented yet)"):
                st.info("Coming soon... just pay or use card for now 😅")
        # Auto-release after 3 turns
        st.session_state.jail_turns[current] += 1
        if st.session_state.jail_turns[current] >= 3:
            if cash[current] >= 100:
                cash[current] -= 100
                jail[current] = False
                st.session_state.jail_turns[current] = 0
                st.info("3 turns up. Paid 100g and released.")
                st.rerun()
            else:
                st.error("Can't pay fine after 3 turns. You're stuck forever (jk refresh lol)")
        st.stop()  # No rolling while in jail

    # ==================== NORMAL TURN ====================
    if not st.session_state.rolled_this_turn:
        st.info("🎲 Your turn to roll!")
        roll_input = st.text_input("Enter dice total (2–12)", key="dice_input")
        if roll_input and roll_input.isdigit():
            roll = int(roll_input)
            if 2 <= roll <= 12:
                is_doubles = st.checkbox("Was it doubles?", key="doubles_check")
                
                # Three doubles = jail
                if is_doubles:
                    st.session_state.doubles_streak += 1
                    if st.session_state.doubles_streak >= 3:
                        pos[current] = 6  # Jail position
                        jail[current] = True
                        st.session_state.doubles_streak = 0
                        st.session_state.rolled_this_turn = True
                        st.error("🚔 THREE DOUBLES! GO TO JAIL!")
                        st.rerun()
                else:
                    st.session_state.doubles_streak = 0

                # Move player
                old_pos = pos[current]
                new_pos = (old_pos + roll) % len(BOARD)
                pos[current] = new_pos
                st.session_state.landed_space = new_pos

                # Pass GO collect 300g
                if new_pos < old_pos or (old_pos >= len(BOARD) - roll):  # Crossed GO
                    cash[current] += 300
                    st.balloons()
                    st.success("Passed GO! +300g 💰")

                space = BOARD[new_pos]
                st.success(f"🎯 Landed on **{space[0]}**")

                # Handle landing effects
                name, typ = space[0], space[1]

                # Tax
                if typ == "tax":
                    tax = space[2]
                    cash[current] -= tax
                    st.warning(f"Paid {tax}g tax! Ouch.")

                # Go to Jail space
                elif typ == "go2jail":
                    pos[current] = 6
                    jail[current] = True
                    st.error("🚔 GO TO JAIL! Do not pass GO.")
                    st.session_state.rolled_this_turn = True
                    st.rerun()

                # Property/Rail/Util rent
                elif typ in ("prop", "rail", "util") and owner[new_pos] and owner[new_pos] != current:
                    landlord = owner[new_pos]
                    rent = 0
                    if typ == "prop":
                        rent = space[3]  # base rent
                    elif typ == "rail":
                        rail_count = sum(1 for i, p in owner.items() if p == landlord and BOARD[i][1] == "rail")
                        rent = 40 * (2 ** (rail_count - 1))  # 40, 80, 160, 320
                    elif typ == "util":
                        util_count = sum(1 for i, p in owner.items() if p == landlord and BOARD[i][1] == "util")
                        rent = roll * (10 if util_count == 1 else 20)
                    
                    if cash[current] >= rent:
                        cash[current] -= rent
                        cash[landlord] += rent
                        st.warning(f"Paid {landlord} **{rent}g** rent!")
                    else:
                        st.error(f"Bankrupt! You owe {landlord} {rent}g but only have {cash[current]}g")
                        cash[landlord] += cash[current]
                        cash[current] = 0

                st.session_state.rolled_this_turn = True
                st.rerun()
    else:
        # Already rolled this turn — show what they landed on and offer buy
        landed = st.session_state.landed_space
        if landed is not None:
            space = BOARD[landed]
            name, typ = space[0], space[1]

            if typ in ("prop", "rail", "util") and owner[landed] is None:
                price = space[2]
                st.markdown(f"### 🏷️ **{name}** is unowned!")
                col_buy, col_info = st.columns([1, 2])
                with col_buy:
                    if st.button(f"BUY FOR {price}g 💸", key=f"buy_{landed}_{current}", use_container_width=True):
                        if cash[current] >= price:
                            cash[current] -= price
                            owner[landed] = current
                            st.success(f"You now own **{name}**!")
                            st.rerun()
                        else:
                            st.error("Not enough gold, homie 😭")
                with col_info:
                    st.write(f"**{name}** – Cost: {price}g")
                    if typ == "prop":
                        st.caption(f"Base rent: {space[3]}g | With monopoly: {space[4]}g")
                    elif typ == "rail":
                        st.caption("Rent scales with number of Travel Points owned")
                    elif typ == "util":
                        st.caption("Rent = dice × 10 (or 20 if both owned)")

    # Show player summary
    st.markdown("### 👥 Player Summary")
    for i, player in enumerate(players):
        props = [BOARD[j][0] for j, o in owner.items() if o == player]
        card = " | 🃏 Get Out of Jail Free" if st.session_state.jail_free_card == player else ""
        status = "🔒 JAILED" if jail[player] else "✅ Free"
        color = "🟥" if i == current_idx else "⬜"
        st.write(f"{color} **{player}** – {cash[player]}g – {status}{card}")
        if props:
            st.caption("→ " + ", ".join(props))
        else:
            st.caption("→ no properties yet")

    # New Game button
    if st.button("🔄 Start New Game"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

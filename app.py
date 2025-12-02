import streamlit as st

st.set_page_config(page_title="Paliopoly – Chilled Dude Edition", layout="centered")
st.title("Paliopoly – Official In-Game Referee")
st.markdown("**Real board • Real dice • Real signs • Zero surprises**")

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

# ====================== CARD EFFECTS BASED ON ROLL ======================
def get_chest_effect(roll):
    effects = {
        2: ("Chapaa smiles upon you… Advance to GO! (+300g)", "go"),
        3: ("The Chappa are NOT happy… GO TO JAIL!", "jail"),
        4: ("Chapaa party! Everyone pays you 50g", "collect_from_all", 50),
        5: ("Chapaa stole your lunch → Pay 100g", "pay", 100),
        6: ("Found a shiny flow tree seed → Collect 100g", "collect", 100),
        7: ("Chapaa pushes you backwards → Go back 3 spaces", "back3"),
        8: ("Chapaa gives you a boost → Go forward 3 spaces", "forward3"),
        9: ("Chapaa says help the poor → Pay poorest player 100g", "pay_poorest", 100),
        10: ("Chapaa calls a taxi → Go to nearest Travel Point", "nearest_rail"),
        11: ("Chapaa vet bill → Pay 150g", "pay", 150),
        12: ("Chapaa jackpot! → Collect 200g", "collect", 200)
    }
    return effects.get(roll, ("?? Something went wrong ??", "none"))

def get_chance_effect(roll):
    effects = {
        2: ("Chapaa teleports you → Free Parking! (no effect)", "free_parking"),
        3: ("Chapaa forgives your crimes → Get Out of Jail Free!", "jailfree"),
        4: ("Too generous… Give 50g to every player", "pay_all", 50),
        5: ("Chapaa fine → Pay 200g", "pay", 200),
        6: Get 150
    7: Move to next shrub
    8: Move to next main property
    9: All give you 100
    10: Go to nearest owned by any1
    11: Pay 100
    12: Get 200

    return effects.get(roll, ("?? Something went wrong ??", "none"))

# ====================== INITIALIZATION ======================
if 'initialized' not in st.session_state:
    st.subheader("Start Paliopoly Session")
    names = st.text_input("Player names", "Chilled Dude, TJediTim, lilshrtchit.ttv")
    if st.button("Start Game"):
        players = [n.strip() for n in names.split(",") if n.strip()]
        if len(players) < 2:
            st.error("Need 2+ players!")
        else:
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.players = players
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
            st.session_state.initialized = True
            st.success("Game started! Roll those real dice!")
            st.rerun()

# ====================== MAIN GAME ======================
if st.session_state.get('initialized', False):
    p = st.session_state.players
    cur_idx = st.session_state.current_idx
    cur = p[cur_idx]
    cash = st.session_state.cash
    pos = st.session_state.position
    owner = st.session_state.properties
    jail = st.session_state.in_jail

    col1, col2, col3, col4 = st.columns([2,2,2,1])
    with col1: st.markdown(f"**Turn: {cur}** {'JAILED' if jail[cur] else ''}")
    with col2: st.markdown(f"**Gold: {cash[cur]}g**")
    with col3: st.write(f"Space: {BOARD[pos[cur]][0]}")
    with col4:
        if st.button("Next Player"):
            st.session_state.current_idx = (cur_idx + 1) % len(p)
            st.session_state.doubles_streak = 0
            st.session_state.rolled = False
            st.session_state.landed = None
            st.session_state.trade_mode = False
            st.session_state.last_message = ""
            st.rerun()

    if st.session_state.last_message:
        st.success(st.session_state.last_message)

    # ==================== TRADE BUTTON ====================
    if st.button("Trade / Deal" if not st.session_state.trade_mode else "Cancel Trade"):
        st.session_state.trade_mode = not st.session_state.trade_mode
        st.rerun()

    if st.session_state.trade_mode:
        st.markdown("### Trade Center")
        with st.expander("Create a deal"):
            p1 = st.selectbox("Player 1", p, index=cur_idx)
            p2 = st.selectbox("Player 2", p, index=(cur_idx + 1) % len(p))
            if p1 == p2:
                st.error("Choose two different players")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**{p1} gives →**")
                    give_cash = st.number_input("Gold", 0, cash[p1], 0, key="gc")
                    give_props = st.multiselect("Properties", [BOARD[i][0] for i,o in owner.items() if o==p1 and BOARD[i][1] in ("prop","rail","util")], key="gp")
                    give_jail = st.checkbox("Get Out of Jail Free card", st.session_state.jail_free_card == p1, key="gj1")
                with c2:
                    st.write(f"**{p2} gives →**")
                    take_cash = st.number_input("Gold ", 0, cash[p2], 0, key="tc")
                    take_props = st.multiselect("Properties ", [BOARD[i][0] for i,o in owner.items() if o==p2 and BOARD[i][1] in ("prop","rail","util")], key="tp")
                    take_jail = st.checkbox("Get Out of Jail Free card ", st.session_state.jail_free_card == p2, key="tj2")

                if st.button("EXECUTE TRADE", type="primary"):
                    if give_cash > cash[p1] or take_cash > cash[p2]:
                        st.error("Not enough gold!")
                    else:
                        cash[p1] -= give_cash; cash[p2] += give_cash
                        cash[p2] -= take_cash; cash[p1] += take_cash
                        for prop in give_props:
                            idx = next(i for i,s in enumerate(BOARD) if s[0]==prop)
                            owner[idx] = p2
                        for prop in take_props:
                            idx = next(i for i,s in enumerate(BOARD) if s[0]==prop)
                            owner[idx] = p1
                        if give_jail and st.session_state.jail_free_card == p1:
                            st.session_state.jail_free_card = p2
                        if take_jail and st.session_state.jail_free_card == p2:
                            st.session_state.jail_free_card = p1
                        st.session_state.last_message = f"Trade complete: {p1} ↔ {p2}"
                        st.session_state.trade_mode = False
                        st.rerun()

    st.divider()

    # ==================== JAIL ====================
    if jail[cur]:
        st.error(f"{cur} is in Jail! Turn {st.session_state.jail_turns[cur]+1}/3")
        j1, j2 = st.columns(2)
        with j1:
            if st.button("Pay 100g") and cash[cur] >= 100:
                cash[cur] -= 100
                jail[cur] = False
                st.session_state.jail_turns[cur] = 0
                st.rerun()
        with j2:
            if st.button("Use Jail Free Card") and st.session_state.jail_free_card == cur:
                st.session_state.jail_free_card = None
                jail[cur] = False
                st.rerun()
        st.session_state.jail_turns[cur] += 1
        if st.session_state.jail_turns[cur] >= 3:
            if cash[cur] >= 100:
                cash[cur] -= 100
                jail[cur] = False
                st.rerun()
        st.stop()

    # ==================== ROLL ====================
    if not st.session_state.rolled:
        st.info("Enter your **real dice roll**")
        roll = st.number_input("Total rolled", 2, 12, 7, step=1)
        doubles = st.checkbox("Doubles?")
        if st.button("Confirm Roll"):
            st.session_state.last_roll = roll  # store for card effects
            if doubles:
                st.session_state.doubles_streak += 1
                if st.session_state.doubles_streak >= 3:
                    pos[cur] = 6
                    jail[cur] = True
                    st.session_state.last_message = "3 DOUBLES → JAIL!"
                    st.rerun()
            else:
                st.session_state.doubles_streak = 0

            old_pos = pos[cur]
            new_pos = (old_pos + roll) % len(BOARD)
            pos[cur] = new_pos
            st.session_state.landed = new_pos
            st.session_state.rolled = True

            crossed_go = new_pos < old_pos or (old_pos + roll >= len(BOARD))
            if crossed_go and new_pos != 0:
                cash[cur] += 300
                st.balloons()

            space = BOARD[new_pos]
            name, typ = space[0], space[1]

            # Basic landing messages
            msg = f"Landed on **{name}**"

            if typ == "tax":
                cash[cur] -= space[2]
                msg = f"Paid {space[2]}g tax!"

            elif typ == "go2jail":
                pos[cur] = 6
                jail[cur] = True
                msg = "GO TO JAIL!"

            elif typ in ("prop","rail","util") and owner[new_pos] and owner[new_pos] != cur:
                landlord = owner[new_pos]
                rent = 0
                if typ == "prop": rent = space[3]
                elif typ == "rail":
                    count = sum(1 for i,o in owner.items() if o==landlord and BOARD[i][1]=="rail")
                    rent = 40 * (2 ** (count-1))
                elif typ == "util":
                    count = sum(1 for i,o in owner.items() if o==landlord and BOARD[i][1]=="util")
                    rent = roll * (10 if count==1 else 20)
                cash[cur] -= rent
                cash[landlord] += rent
                msg = f"Paid **{landlord}** {rent}g rent on **{name}**!"

            # CHEST & CHANCE — NOW 100% SAFE
            elif typ == "chest":
                text, _ = get_chest_effect(roll)
                st.session_state.last_message = f"Chappa Chest → {text}"

            elif typ == "chance":
                text, _ = get_chance_effect(roll)
                st.session_state.last_message = f"Chapaa Chance → {text}"

            else:
                st.session_state.last_message = msg

            st.rerun()

    # ==================== BUY ====================
    landed = st.session_state.landed
    if landed and BOARD[landed][1] in ("prop","rail","util") and owner[landed] is None:
        price = BOARD[landed][2]
        if st.button(f"BUY {BOARD[landed][0]} for {price}g", type="primary"):
            if cash[cur] >= price:
                cash[cur] -= price
                owner[landed] = cur
                st.session_state.last_message = f"{cur} bought {BOARD[landed][0]}!"
                st.rerun()

    # ==================== PLAYER SUMMARY ====================
    st.markdown("### Players")
    for i, pl in enumerate(p):
        props = [BOARD[j][0] for j, o in owner.items() if o == pl]
        card = " | Get Out of Jail Free" if st.session_state.jail_free_card == pl else ""
        status = "JAILED" if jail[pl] else "Free"
        arrow = "→" if i == cur_idx else "  "
        st.write(f"{arrow} **{pl}** – {cash[pl]}g – {status}{card}")
        if props:
            st.caption("   • " + " • ".join(props))

    if st.button("New Game"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

import streamlit as st

st.set_page_config(page_title="Paliopoly – Chilled Dude Edition", layout="centered")
st.title("Paliopoly – Chilled Dude Edition")
st.markdown("**Real board • Real dice • Real signs •Real fun • not S6 affiliated, just for us**")

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

# ====================== FREE PARKING POT ======================
if 'free_parking_pot' not in st.session_state:
    st.session_state.free_parking_pot = 0

# ====================== CARD EFFECTS ======================
def get_chest_effect(roll, player, cash, pos, jail, p):
    effects = {
        2: ("Chapaa smiles upon you… Advance to GO! (+300g)", lambda: (set_pos(pos, player, 0), add_cash(cash, player, 300))),
        3: ("The Chappa are NOT happy… GO TO JAIL!", lambda: (set_pos(pos, player, 6), set_jail(jail, player, True))),
        4: ("Chapaa party! Everyone pays you 50g", lambda: collect_from_all(cash, player, p, 50)),
        5: ("Chapaa stole your lunch → Pay 100g", lambda: add_cash(cash, player, -100)),
        6: ("Found a shiny flow tree seed → Collect 100g", lambda: add_cash(cash, player, 100)),
        7: ("Chapaa pushes you backwards → Go back 3 spaces", lambda: set_pos(pos, player, (pos[player] - 3) % len(BOARD))),
        8: ("Chapaa gives you a boost → Go forward 3 spaces", lambda: set_pos(pos, player, (pos[player] + 3) % len(BOARD))),
        9: ("Chapaa says help the poor → Pay poorest player 100g", lambda: pay_poorest(cash, player, p, 100)),
        10: ("Chapaa calls a taxi → Go to nearest Travel Point", lambda: move_to_nearest(pos, player, [4, 10, 16, 20])),
        11: ("Chapaa vet bill → Pay 150g", lambda: add_cash(cash, player, -150)),
        12: ("Chapaa jackpot! → Collect 200g", lambda: add_cash(cash, player, 200))
    }
    text, action = effects.get(roll, ("?? Unknown roll ??", lambda: None))
    action()
    return text

def get_chance_effect(roll, player, cash, pos, owner, p):
    effects = {
        2: ("Chapaa warps you → Free Parking! (collect pot)", lambda: (set_pos(pos, player, 12), add_cash(cash, player, st.session_state.free_parking_pot), set_pot(0))),
        3: ("Chapaa forgives your crimes → Get Out of Jail Free!", lambda: set_jail_free(player)),
        4: ("Too generous… Give 50g to every player", lambda: pay_all(cash, player, p, 50)),
        5: ("Chapaa tax collector → Pay 200g", lambda: add_cash(cash, player, -200)),
        6: ("Chapaa likes your vibe → Collect 150g", lambda: add_cash(cash, player, 150)),
        7: ("Follow the flow trees → Move to next shrub property", lambda: move_to_next_shrub(pos, player)),
        8: ("Chapaa real estate agent → Move to next main property", lambda: move_to_next_main(pos, player)),
        9: ("Everyone loves you → All players give you 100g", lambda: collect_from_all(cash, player, p, 100)),
        10: ("Chapaa drama → Go to nearest property owned by anyone", lambda: move_to_nearest_owned(pos, player, owner)),
        11: ("Chapaa speeding ticket → Pay 100g", lambda: add_cash(cash, player, -100)),
        12: ("Chapaa moon party jackpot → Collect 200g", lambda: add_cash(cash, player, 200))
    }
    text, action = effects.get(roll, ("?? Unknown roll ??", lambda: None))
    action()
    return text

# Helper functions for card effects
def add_cash(cash, player, amount):
    if cash[player] + amount >= 0:
        cash[player] += amount
    else:
        cash[player] = 0

def set_pos(pos, player, new_pos):
    pos[player] = new_pos

def set_jail(jail, player, status):
    jail[player] = status

def set_jail_free(player):
    st.session_state.jail_free_card = player

def set_pot(amount):
    st.session_state.free_parking_pot = amount

def collect_from_all(cash, player, players, amount):
    for p in players:
        if p != player and cash[p] >= amount:
            cash[p] -= amount
            cash[player] += amount

def pay_all(cash, player, players, amount):
    for p in players:
        if p != player and cash[player] >= amount:
            cash[player] -= amount
            cash[p] += amount

def pay_poorest(cash, player, players, amount):
    if players:
        poorest = min(players, key=lambda p: cash[p])
        if cash[player] >= amount:
            cash[player] -= amount
            cash[poorest] += amount

def move_to_nearest(pos, player, targets):
    current = pos[player]
    distances = [(t - current) % len(BOARD) for t in targets]
    min_distance = min(distances)
    target = targets[distances.index(min_distance)]
    pos[player] = target

def move_to_next_shrub(pos, player):
    current = pos[player]
    shrub_positions = [13, 15, 21, 23]  # Elderwood 1, 2, Maji Wedding 1, 2
    for pos in sorted(shrub_positions):
        if pos > current:
            set_pos(pos, player, pos)
            return
    set_pos(pos, player, shrub_positions[0])

def move_to_next_main(pos, player):
    current = pos[player]
    main_positions = [1, 3, 7, 10, 13, 15, 21, 23]  # All properties
    for pos in sorted(main_positions):
        if pos > current:
            set_pos(pos, player, pos)
            return
    set_pos(pos, player, main_positions[0])

def move_to_nearest_owned(pos, player, owner):
    current = pos[player]
    owned = [i for i in range(len(BOARD)) if owner.get(i) and BOARD[i][1] in ("prop", "rail", "util")]
    if owned:
        distances = [(i - current) % len(BOARD) for i in owned]
        min_distance = min(distances)
        target = owned[distances.index(min_distance)]
        pos[player] = target

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
            st.session_state.free_parking_pot = 0
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
    pot = st.session_state.free_parking_pot

    # HEADER
    col1, col2, col3, col4 = st.columns([2,2,2,3])
    with col1: st.markdown(f"**Turn: {cur}** {'JAILED' if jail[cur] else ''}")
    with col2: st.markdown(f"**Gold: {cash[cur]}g**")
    with col3: st.markdown(f"**Pot: {pot}g**")
    with col4:
        if st.session_state.rolled:
            if st.button("Next Player →", type="primary", use_container_width=True):
                st.session_state.current_idx = (cur_idx + 1) % len(p)
                st.session_state.doubles_streak = 0
                st.session_state.rolled = False
                st.session_state.landed = None
                st.session_state.trade_mode = False
                st.session_state.last_message = ""
                st.rerun()
        else:
            st.button("Next Player →", disabled=True, use_container_width=True)
            st.caption("Roll first before ending turn!")

    if st.session_state.last_message:
        st.success(st.session_state.last_message)

    # TRADE
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
                    st.write(f"**{p1} gives**")
                    give_cash = st.number_input("Gold", 0, cash[p1], 0, key="gc3")
                    give_props = st.multiselect("Properties", [BOARD[i][0] for i,o in owner.items() if o==p1 and BOARD[i][1] in ("prop","rail","util")], key="gp3")
                    give_jail = st.checkbox("Jail Free Card", st.session_state.jail_free_card == p1, key="gj3")
                with c2:
                    st.write(f"**{p2} gives**")
                    take_cash = st.number_input("Gold ", 0, cash[p2], 0, key="tc3")
                    take_props = st.multiselect("Properties ", [BOARD[i][0] for i,o in owner.items() if o==p2 and BOARD[i][1] in ("prop","rail","util")], key="tp3")
                    take_jail = st.checkbox("Jail Free Card ", st.session_state.jail_free_card == p2, key="tj3")

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

    # JAIL
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
        if st.session_state.jail_turns[cur] >= 3 and cash[cur] >= 100:
            cash[cur] -= 100
            jail[cur] = False
            st.rerun()
        st.stop()

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
            msg = f"Landed on **{name}**"

            if typ == "tax":
                tax_amount = space[2]
                cash[cur] -= tax_amount
                st.session_state.free_parking_pot += tax_amount
                msg = f"Paid **{tax_amount}g {name}** → added to Free Parking pot! (Now {st.session_state.free_parking_pot}g)"

            elif typ == "free":
                if st.session_state.free_parking_pot > 0:
                    cash[cur] += st.session_state.free_parking_pot
                    msg = f"FREE PARKING JACKPOT! Collected **{st.session_state.free_parking_pot}g**"
                    st.session_state.free_parking_pot = 0
                    st.balloons()
                else:
                    msg = "Free Parking — chilling with the Chappa!"

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

            elif typ == "chest":
                text = get_chest_effect(roll, cur, cash, pos, jail, p)
                msg = f"Chappa Chest → {text}"

            elif typ == "chance":
                text = get_chance_effect(roll, cur, cash, pos, owner, p)
                msg = f"Chapaa Chance → {text}"

            st.session_state.last_message = msg
            st.rerun()

    # BUY PROPERTY
    landed = st.session_state.landed
    if landed and BOARD[landed][1] in ("prop","rail","util") and owner[landed] is None:
        price = BOARD[landed][2]
        if st.button(f"BUY {BOARD[landed][0]} for {price}g", type="primary"):
            if cash[cur] >= price:
                cash[cur] -= price
                owner[landed] = cur
                st.session_state.last_message = f"{cur} bought {BOARD[landed][0]}!"
                st.rerun()

    # PLAYER SUMMARY
    st.markdown("### Players")
    for i, pl in enumerate(p):
        props = [BOARD[j][0] for j, o in owner.items() if o == pl]
        card = " | Get Out of Jail Free" if st.session_state.jail_free_card == pl else ""
        status = "JAILED" if jail[pl] else "Free"
        arrow = "→" if i == cur_idx else "  "
        st.write(f"{arrow} **{pl}** – {cash[pl]}g – {status}{card}")
        if props:
            st.caption("   • " + " • ".join(props))

    if st.button("New Game (Reset Everything)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

import streamlit as st

st.set_page_config(page_title="Paliopoly", layout="centered")
st.title("Paliopoly – Chilled Dude Original Edition")

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

CHEST_CARDS = {2:"Advance to GO +300g",3:"JAIL → go to Jail",4:"Everyone pays you 50g",5:"Pay 100g",6:"Collect 100g",
               7:"Back 3 spaces",8:"Forward 3 spaces",9:"Pay poorest player 100g",10:"Go to nearest Travel Point",
               11:"Pay 150g",12:"Collect 200g"}

CHANCE_CARDS = {2:"Free Parking → move there",3:"Get Out of Jail Free!",4:"Give 50g to each player",5:"Pay 200g",
                6:"Get 150g",7:"Move to next Utility",8:"Move to next main property",9:"All give you 100g",
                10:"Go to nearest owned property",11:"Pay 100g",12:"Get 200g"}

# ====================== INITIALISE ======================
if 'players' not in st.session_state:
    st.subheader("Welcome to Paliopoly!")
    names = st.text_input("Names (comma separated)", "Chilled Dude, TJediTim, lilshrtchit.ttv")
    if st.button("Start Game"):
        pl = [n.strip() for n in names.split(",") if n.strip()]
        if len(pl) < 2:
            st.error("Need 2+ players")
        else:
            st.session_state.players = pl
            st.session_state.cash = {p:1200 for p in pl}
            st.session_state.pos = {p:0 for p in pl}
            st.session_state.owner = {i:None for i in range(24)}
            st.session_state.jail = {p:False for p in pl}
            st.session_state.jail_turns = {p:0 for p in pl}
            st.session_state.jailfree_owner = None
            st.session_state.current = 0
            st.session_state.rolls_this_turn = []  # Track doubles
            st.rerun()

else:
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
    with col1: st.markdown(f"**Turn → {cur}** {'(JAILED – turn {jail_turns[cur]+1}/3)' if jail[cur] else ''}")
    with col2: st.markdown(f"**Cash:** {cash[cur]}g")
    with col3: st.button("Next player →", on_click=lambda: st.session_state.update(current=(st.session_state.current+1)%len(p), rolls_this_turn=[]))

    # ====================== IN JAIL ======================
    if jail[cur]:
        st.error(f"{cur} is in Jail! (turn {jail_turns[cur]+1}/3)")

        c1, c2, c3 = st.columns(3)
        if c1.button("Use Get Out of Jail Free") and jailfree_owner == cur:
            st.session_state.jailfree_owner = None
            jail[cur] = False
            jail_turns[cur] = 0
            st.success("Out with card!")

        if c2.button("Pay 100g") and cash[cur] >= 100:
            cash[cur] -= 100
            jail[cur] = False
            jail_turns[cur] = 0
            st.success("Paid 100g → free!")

        if c3.button("Rolled Doubles – YES"):
            jail[cur] = False
            jail_turns[cur] = 0
            st.success("DOUBLES! You're free!")
            st.session_state.rolls_this_turn = []  # Reset for new turn
        if c3.button("No Doubles"):
            jail_turns[cur] += 1
            st.info("Still in jail...")
            if jail_turns[cur] >= 3:
                if cash[cur] >= 100:
                    cash[cur] -= 100
                    jail[cur] = False
                    st.info("3 turns up — paid 100g and released")

    # ====================== NORMAL TURN ======================
    else:
        if not st.session_state.rolls_this_turn:
            dice = st.text_input("Roll dice (2–12)", value="", key="dice")
        else:
            dice = ""
            st.info("Turn complete → Next player")

        if dice.isdigit():
            roll = int(dice)
            if 2 <= roll <= 12:
                st.session_state.rolls_this_turn.append(roll)
                old = pos[cur]
                new = (old + roll) % 24
                pos[cur] = new
                name, typ = BOARD[new][0], BOARD[new][1]

                # 3 doubles in a row = Jail
                if len(st.session_state.rolls_this_turn) == 3 and all(r == roll for r in st.session_state.rolls_this_turn):
                    pos[cur] = 6
                    jail[cur] = True
                    jail_turns[cur] = 0
                    st.error("3 doubles in a row → Go to Jail!")
                    st.session_state.rolls_this_turn = []  # End turn
                else:
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
                        jail_turns[cur] = 0
                        st.error("Go to Jail!")

                    # CHEST & CHANCE (auto, ends turn)
                    elif typ == "chest":
                        txt = CHEST_CARDS[roll]
                        st.success(f"CHAPPA CHEST → {txt}")
                        if roll == 2: pos[cur] = 0; cash[cur] += 300
                        elif roll == 3: pos[cur] = 6; jail[cur] = True; jail_turns[cur] = 0
                        elif roll == 4: for pl in p: if pl != cur: cash[pl] -= 50; cash[cur] += 50
                        elif roll == 5: cash[cur] -= 100
                        elif roll == 6: cash[cur] += 100
                        elif roll == 7: pos[cur] = (pos[cur] - 3) % 24
                        elif roll == 8: pos[cur] = (pos[cur] + 3) % 24
                        elif roll == 9: poorest = min(p, key=cash.get); cash[cur] -= 100; cash[poorest] += 100
                        elif roll == 10: for i in range(new + 1, new + 25): if BOARD[i % 24][1] == "rail": pos[cur] = i % 24; break
                        elif roll == 11: cash[cur] -= 150
                        elif roll == 12: cash[cur] += 200
                        st.session_state.rolls_this_turn = []  # End turn

                    elif typ == "chance":
                        txt = CHANCE_CARDS[roll]
                        st.success(f"CHAPAA CHANCE → {txt}")
                        if roll == 2: pos[cur] = 12
                        elif roll == 3 and jailfree_owner is None: st.session_state.jailfree_owner = cur
                        elif roll == 4: for pl in p: if pl != cur: cash[cur] -= 50; cash[pl] += 50
                        elif roll == 5: cash[cur] -= 200
                        elif roll == 6: cash[cur] += 150
                        elif roll == 7: for i in range(new + 1, new + 25): if BOARD[i % 24][1] == "util": pos[cur] = i % 24; break
                        elif roll == 8: for i in range(new + 1, new + 25): if BOARD[i % 24][1] == "prop": pos[cur] = i % 24; break
                        elif roll == 9: for pl in p: if pl != cur: cash[pl] -= 100; cash[cur] += 100
                        elif roll == 10: for i in range(new + 1, new + 25): idx = i % 24; if owner[idx] and owner[idx] != cur: pos[cur] = idx; break
                        elif roll == 11: cash[cur] -= 100
                        elif roll == 12: cash[cur] += 200
                        st.session_state.rolls_this_turn = []  # End turn

                    # AUTO RENT
                    if typ in ("prop","rail","util") and owner[new] and owner[new] != cur:
                        landlord = owner[new]
                        if typ == "prop":
                            set_name = next(k for k,v in SETS.items() if name in v)
                            full = all(owner[BOARD.index(s)] == landlord for s in SETS[set_name])
                            rent = BOARD[new][4] if full else BOARD[new][3]
                            reason = f"full {set_name} set" if full else name
                        elif typ == "rail":
                            owned = sum(1 for i in range(24) if BOARD[i][1] == "rail" and owner[i] == landlord)
                            rent = owned * 40
                            reason = f"{owned} Travel Points"
                        else:
                            owned = sum(1 for i in range(24) if BOARD[i][1] == "util" and owner[i] == landlord)
                            rent = roll * (10 if owned == 2 else 4)
                            reason = f"Utility ×{10 if owned == 2 else 4}"
                        cash[cur] -= rent
                        cash[landlord] += rent
                        st.warning(f"Paid {landlord} {rent}g for {reason}")

                    # BUY BUTTON
                    if typ in ("prop","rail","util") and owner[new] is None:
                        price = BOARD[new][2]
                        if st.button(f"BUY {name} – {price}g"):
                            if cash[cur] >= price:
                                cash[cur] -= price
                                owner[new] = cur
                                st.success(f"{cur} bought {name}!")
                            else:
                                st.error("Not enough gold!")

                    st.success(f"Landed on **{name}**")

                    # Extra turn if doubles and not 3 in a row
                    if len(st.session_state.rolls_this_turn) < 3 and roll % 2 == 0:
                        st.session_state.rolled = False  # Allow another roll
                        st.success("DOUBLES! Roll again!")
                    else:
                        st.session_state.rolled = True  # End turn

    st.markdown(f"**Current square:** {BOARD[pos[cur]][0]}")

    # ==================== TRADE ====================
    with st.expander("Trade – Cash & Properties"):
        giver = st.selectbox("Giver", p)
        receiver = st.selectbox("Receiver", [x for x in p if x != giver])
        amount = st.number_input("Cash amount (0=none)", min_value=0, value=0, step=10)
        owned = [BOARD[i][0] for i in range(24) if owner[i]==giver]
        prop = st.selectbox("Property (optional)", ["(none)"] + owned)

        if st.button("Execute Deal"):
            if amount == 0 and prop == "(none)":
                st.warning("Nothing to trade")
            elif amount > 0 and cash[giver] < amount:
                st.error("Not enough cash")
            else:
                if amount > 0:
                    cash[giver] -= amount
                    cash[receiver] += amount
                if prop != "(none)":
                    idx = next(i for i,s in enumerate(BOARD) if s[0]==prop)
                    owner[idx] = receiver
                st.success("Deal done!")

    # Quick taxes
    t1, t2 = st.columns(2)
    if t1.button("Renown Tax 100g"): cash[cur] -= 100
    if t2.button("Maji Tax 200g"): cash[cur] -= 200

    # Player summary
    st.markdown("### Players")
    for pl in p:
        props = [BOARD[i][0] for i in range(24) if owner.get(i)==pl]
        st.write(f"**{pl}** – {cash[pl]}g – {'JAILED' if jail[pl] else 'Free'} – Free cards:{1 if jailfree_owner == pl else 0} – {', '.join(props) or 'nothing'}")

    if st.button("New Game – Reset"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

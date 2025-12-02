import streamlit as st

st.set_page_config(page_title="Paliopoly", layout="centered")
st.title("Paliopoly – Chilled dude Edition")

# ====================== BOARD ======================
BOARD = [
    ("GO", "go"), ("Kilima 1", "prop", 80, 6, 18), ("Renown Tax", "tax", 100), ("Kilima 2", "prop", 80, 6, 18),
    ("Travel Point", "rail", 150, 40), ("Chappa Chest", "chest"), ("Jail", "jail"),
    ("Bahari 1", "prop", 120, 9, 27), ("Chapaa Chance", "chance"), ("Travel Point", "rail", 150, 40),
    ("Bahari 2", "prop", 120, 9, 27), ("Utility 1", "util", 100), ("Free Parking", "free"),
    ("Elderwood 1", "prop", 160, 12, 36), ("Chapaa Chance", "chance"), ("Elderwood 2", "prop", 160, 12, 36),
    ("Travel Point", "rail", 150, 40), ("Utility 2", "util", 100), ("Go to Jail", "go2jail"),
    ("Chappa Chest", "chest"), ("Travel Point", "rail", 150, 40),
    ("Maji Wedding 1", "prop", 200, 15, 45), ("Maji Tax", "tax", 200), ("Maji Wedding 2", "prop", 200, 15, 45)
]

SETS = {"Kilima":["Kilima 1","Kilima 2"], "Bahari":["Bahari 1","Bahari 2"],
        "Elderwood":["Elderwood 1","Elderwood 2"], "Maji Wedding":["Maji Wedding 1","Maji Wedding 2"]}

CHEST_CARDS = {2:"Advance to GO +300g",3:"JAIL → go to Jail",4:"Everyone pays you 50g",5:"Pay 100g",6:"Collect 100g",
               7:"Back 3 spaces",8:"Forward 3 spaces",9:"Pay poorest player 100g",10:"Go to nearest Travel Point",
               11:"Pay 150g",12:"Collect 200g"}

CHANCE_CARDS = {2:"Free Parking → move there",3:"Get Out of Jail Free!",4:"Give 50g to each player",5:"Pay 200g",
                6:"Get 150g",7:"Move to next Utility",8:"Move to next main property",9:"All give you 100g",
                10:"Go to nearest owned property",11:"Pay 100g",12:"Get 200g"}

# ====================== INITIALISE ======================
if 'players' not in st.session_state:
    st.subheader("Welcome to Paliopoly!")
    names = st.text_input("Names (comma separated)", "Chilled dude")
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
            st.session_state.jailfree = {p:0 for p in pl}
            st.session_state.current = 0
            st.session_state.rolled_this_turn = False
            st.rerun()

else:
    p = st.session_state.players
    cash = st.session_state.cash
    pos = st.session_state.pos
    owner = st.session_state.owner
    jail = st.session_state.jail
    jailfree = st.session_state.jailfree
    cur = p[st.session_state.current]

    # Header
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"**Turn → {cur}** {'(JAILED)' if jail[cur] else ''}")
    with col2: st.markdown(f"**Cash:** {cash[cur]}g")
    with col3: st.button("Next player →", on_click=lambda: st.session_state.update(current=(st.session_state.current+1)%len(p), rolled_this_turn=False))

    # DICE — NO DOUBLE MOVES ANYMORE
    if not st.session_state.get('rolled_this_turn', False):
        dice = st.text_input("Roll dice (2–12)", value="", key="dice_input")
    else:
        dice = ""
        st.info("Turn complete — press Next player")

    if dice.isdigit():
        roll = int(dice)
        if 2 <= roll <= 12 and not st.session_state.rolled_this_turn:
            st.session_state.rolled_this_turn = True

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
                st.error("Go to Jail!")

            # Chappa Chest
            elif typ == "chest":
                txt = CHEST_CARDS[roll]
                st.success(f"CHAPPA CHEST → {txt}")
                if roll==2: pos[cur]=0; cash[cur]+=300
                elif roll==3: pos[cur]=6; jail[cur]=True
                elif roll==4:
                    for pl in p:
                        if pl != cur:
                            cash[pl]-=50; cash[cur]+=50
                elif roll==5: cash[cur]-=100
                elif roll==6: cash[cur]+=100
                elif roll==7: pos[cur]=(pos[cur]-3)%24
                elif roll==8: pos[cur]=(pos[cur]+3)%24
                elif roll==9:
                    poorest = min(p, key=cash.get)
                    cash[cur]-=100; cash[poorest]+=100
                elif roll==10:
                    for i in range(new+1,new+25):
                        if BOARD[i%24][1]=="rail":
                            pos[cur]=i%24; break
                elif roll==11: cash[cur]-=150
                elif roll==12: cash[cur]+=200

            # Chapaa Chance
            elif typ == "chance":
                txt = CHANCE_CARDS[roll]
                st.success(f"CHAPAA CHANCE → {txt}")
                if roll==2: pos[cur]=12
                elif roll==3: jailfree[cur]+=1
                elif roll==4:
                    for pl in p:
                        if pl != cur:
                            cash[cur]-=50; cash[pl]+=50
                elif roll==5: cash[cur]-=200
                elif roll==6: cash[cur]+=150
                elif roll==7:
                    for i in range(new+1,new+25):
                        if BOARD[i%24][1]=="util":
                            pos[cur]=i%24; break
                elif roll==8:
                    for i in range(new+1,new+25):
                        if BOARD[i%24][1]=="prop":
                            pos[cur]=i%24; break
                elif roll==9:
                    for pl in p:
                        if pl != cur:
                            cash[pl]-=100; cash[cur]+=100
                elif roll==10:
                    for i in range(new+1,new+25):
                        idx=i%24
                        if owner[idx] and owner[idx]!=cur:
                            pos[cur]=idx; break
                elif roll==11: cash[cur]-=100
                elif roll==12: cash[cur]+=200

            # AUTO RENT
            if typ in ("prop","rail","util") and owner[new] and owner[new]!=cur:
                landlord = owner[new]
                if typ=="prop":
                    set_name = next(k for k,v in SETS.items() if name in v)
                    full = all(owner[BOARD.index(s)]==landlord for s in SETS[set_name])
                    rent = BOARD[new][4] if full else BOARD[new][3]
                    reason = f"full {set_name} set" if full else name
                elif typ=="rail":
                    rent = 40 * sum(1 for i in range(24) if BOARD[i][1]=="rail" and owner[i]==landlord)
                    reason = f"{rent//40} Travel Points"
                else:
                    rent = roll * (10 if sum(1 for i in range(24) if BOARD[i][1]=="util" and owner[i]==landlord)==2 else 4)
                    reason = f"Utility ×{10 if rent > roll*4 else 4}"
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

    st.markdown(f"**Current square:** {BOARD[pos[cur]][0]}")

    # ==================== FULL TRADE (CASH + PROPERTY) ====================
    with st.expander("Trade – Properties & Cash", expanded=False):
        giver = st.selectbox("Giver", p)
        receiver = st.selectbox("Receiver", [x for x in p if x != giver])
        amount = st.number_input("Cash amount (0 = no cash)", min_value=0, value=0, step=10)
        owned = [BOARD[i][0] for i in range(24) if owner[i]==giver]
        prop = st.selectbox("Property (optional)", ["(none)"] + owned)

        if st.button("Execute Deal"):
            if amount == 0 and prop == "(none)":
                st.warning("Add cash or a property!")
            else:
                if amount > 0:
                    if cash[giver] >= amount:
                        cash[giver] -= amount
                        cash[receiver] += amount
                    else:
                        st.error("Giver doesn't have enough cash!")
                        st.stop()
                if prop != "(none)":
                    idx = next(i for i,s in enumerate(BOARD) if s[0]==prop)
                    owner[idx] = receiver
                st.success(f"Deal complete! {amount}g + {prop if prop!='(none)' else 'nothing'}")

    # Quick buttons
    q1, q2, q3 = st.columns(3)
    if q1.button("Renown Tax 100g"): cash[cur] -= 100
    if q2.button("Maji Tax 200g"): cash[cur] -= 200
    if q3.button("Pay 100g → out of Jail") and jail[cur] and cash[cur] >= 100:
        cash[cur] -= 100; jail[cur] = False

    # Balances
    st.markdown("### Players")
    for pl in p:
        props = [BOARD[i][0] for i in range(24) if owner.get(i)==pl]
        st.write(f"**{pl}** – {cash[pl]}g – {'JAILED' if jail[pl] else ''} – Free:{jailfree[pl]} – {', '.join(props) or 'none'}")

    if st.button("New Game – Reset Everything"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

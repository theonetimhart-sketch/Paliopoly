import streamlit as st

st.set_page_config(page_title="Paliopoly", layout="centered")
st.title("Paliopoly – Chilled dude Edition")

# ====================== 24-SQUARE BOARD ======================
BOARD = [
    ("GO", "go"),                               # 0
    ("Kilima 1", "prop", 80, 6, 18),            # 1
    ("Renown Tax", "tax", 100),                 # 2 ← 100g
    ("Kilima 2", "prop", 80, 6, 18),            # 3
    ("Travel Point", "rail", 150, 40),          # 4
    ("Chappa Chest", "chest"),                 # 5
    ("Jail", "jail"),                           # 6
    ("Bahari 1", "prop", 120, 9, 27),           # 7
    ("Chapaa Chance", "chance"),               # 8
    ("Travel Point", "rail", 150, 40),          # 9
    ("Bahari 2", "prop", 120, 9, 27),           # 10
    ("Utility 1", "util", 100),                 # 11
    ("Free Parking", "free"),                   # 12
    ("Elderwood 1", "prop", 160, 12, 36),       # 13
    ("Chapaa Chance", "chance"),               # 14
    ("Elderwood 2", "prop", 160, 12, 36),       # 15
    ("Travel Point", "rail", 150, 40),          # 16
    ("Utility 2", "util", 100),                 # 17
    ("Go to Jail", "go2jail"),                  # 18
    ("Chappa Chest", "chest"),                 # 19
    ("Travel Point", "rail", 150, 40),          # 20
    ("Maji Wedding 1", "prop", 200, 15, 45),    # 21
    ("Maji Tax", "tax", 200),                   # 22 ← 200g
    ("Maji Wedding 2", "prop", 200, 15, 45)     # 23
]

SETS = {
    "Kilima": ["Kilima 1", "Kilima 2"],
    "Bahari": ["Bahari 1", "Bahari 2"],
    "Elderwood": ["Elderwood 1", "Elderwood 2"],
    "Maji Wedding": ["Maji Wedding 1", "Maji Wedding 2"]
}

CHEST_CARDS = {2:"Advance to GO +300g",3:"JAIL → go to Jail",4:"Everyone pays you 50g",5:"Pay 100g",6:"Collect 100g",
               7:"Back 3 spaces",8:"Forward 3 spaces",9:"Pay poorest player 100g",10:"Go to nearest Travel Point",
               11:"Pay 150g",12:"Collect 200g"}

CHANCE_CARDS = {2:"Free Parking → move there",3:"Get Out of Jail Free!",4:"Give 50g to each player",5:"Pay 200g",
                6:"Get 150g",7:"Move to next Utility",8:"Move to next main property",9:"All give you 100g",
                10:"Go to nearest owned property",11:"Pay 100g",12:"Get 200g"}

# ====================== INITIALISE ======================
if 'players' not in st.session_state:
    st.subheader("Welcome to Paliopoly!")
    names =  st.text_input("Names (comma separated)", "Chilled dude")
    if st.button("Start Game"):
        pl = [n.strip() for n in names.split(",") if n.strip()]
        if len(pl) < 2:
            st.error("Need 2+ players")
        else:
            st.session_state.players = pl
            st.session_state.cash = {p: 1200 for p in pl}
            st.session_state.pos = {p: 0 for p in pl}
            st.session_state.owner = {i: None for i in range(24)}
            st.session_state.jail = {p: False for p in pl}
            st.session_state.jailfree = {p: 0 for p in pl}
            st.session_state.current = 0
            st.rerun()

else:
    p = st.session_state.players
    cash = st.session_state.cash
    pos = st.session_state.pos
    owner = st.session_state.owner
    jail = st.session_state.jail
    jailfree = st.session_state.jailfree
    cur = p[st.session_state.current]

    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"**Turn → {cur}** {'(JAILED)' if jail[cur] else ''}")
    with col2: st.markdown(f"**Cash:** {cash[cur]}g")
    with col3: st.button("Next player →", on_click=lambda: st.session_state.update(current=(st.session_state.current+1)%len(p)))

    # DICE – no double-move bug
    dice = st.text_input("Roll dice (2–12)", value="", key=f"dice_{st.session_state.current}")

    if dice.isdigit():
        roll = int(dice)
        if 2 <= roll <= 12:
            old = pos[cur]
            new = (old + roll) % 24
            pos[cur] = new
            space = BOARD[new]
            name, typ = space[0], space[1]

            # Pass GO
            if new <= old and new != 0:
                cash[cur] += 300
                st.balloons()

            # Taxes
            if typ == "tax":
                cash[cur] -= space[2]
                st.info(f"Paid {space[2]}g tax")

            # Go to Jail corner
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
                elif roll==4: [cash.__setitem__(pl,cash[pl]-50) or cash.__setitem__(cur,cash[cur]+50) for pl in p if pl!=cur]
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
                elif roll==4: [cash.__setitem__(cur,cash[cur]-50) or cash.__setitem__(pl,cash[pl]+50) for pl in p if pl!=cur]
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
                elif roll==9: [cash.__setitem__(pl,cash[pl]-100) or cash.__setitem__(cur,cash[cur]+100) for pl in p if pl!=cur]
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
                    rent = space[4] if full else space[3]
                    reason = f"full {set_name} set" if full else name
                elif typ=="rail":
                    rent = 40 * sum(1 for i in range(24) if BOARD[i][1]=="rail" and owner[i]==landlord)
                    reason = f"{rent//40} Travel Points"
                else:
                    rent = roll * (10 if sum(1 for i in range(24) if BOARD[i][1]=="util" and owner[i]==landlord)==2 else 4)
                    reason = f"Utility ×{10 if '10' in str(rent) else 4}"
                cash[cur] -= rent
                cash[landlord] += rent
                st.warning(f"Paid {landlord} {rent}g for {reason}")

            # BUY BUTTON
            if typ in ("prop","rail","util") and owner[new] is None:
                price = space[2]
                if st.button(f"BUY {name} – {price}g"):
                    if cash[cur] >= price:
                        cash[cur] -= price
                        owner[new] = cur
                        st.success(f"{cur} bought {name}!")
                    else:
                        st.error("Not enough gold!")

            st.success(f"Landed on **{name}**")

    st.markdown(f"**Current square:** {BOARD[pos[cur]][0]}")

    # Quick buttons (fixed syntax)
    cq1, cq2, cq3 = st.columns(3)
    if cq1.button("Renown Tax 100g"): cash[cur] -= 100
    if cq2.button("Maji Tax 200g"): cash[cur] -= 200
    if cq3.button("Pay 100g → out of Jail"):
        if jail[cur] and cash[cur] >= 100:
            cash[cur] -= 100
            jail[cur] = False

    # Trade
    with st.expander("Trade Properties"):
        giver = st.selectbox("From", p)
        recv  = st.selectbox("To", [x for x in p if x != giver])
        owned = [BOARD[i][0] for i in range(24) if owner[i]==giver]
        prop  = st.selectbox("Property", ["(none)"] + owned)
        if st.button("Trade!") and prop != "(none)":
            idx = next(i for i,s in enumerate(BOARD) if s[0]==prop)
            owner[idx] = recv
            st.success(f"{prop} → {recv}")

    # Balances
    st.markdown("### Players")
    for pl in p:
        props = [BOARD[i][0] for i in range(24) if owner.get(i)==pl]
        st.write(f"**{pl}** – {cash[pl]}g – {'JAILED' if jail[pl] else ''} – Free:{jailfree[pl]} – {', '.join(props) or 'none'}")

    if st.button("New Game – Reset Everything"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

import streamlit as st

st.set_page_config(page_title="Paliopoly", layout="centered")
st.title("Paliopoly – Chilled dude Edition")

# ====================== 24-SQUARE BOARD ======================
BOARD = [
    ("GO", "go"),                           # 0
    ("Kilima 1", "prop", 80, 6, 18),        # 1
    ("Renown Tax", "tax", 100),             # 2 ← 100g
    ("Kilima 2", "prop", 80, 6, 18),        # 3
    ("Travel Point", "rail", 150, 40),      # 4
    ("Chappa Chest", "chest"),             # 5
    ("Jail", "jail"),                       # 6
    ("Bahari 1", "prop", 120, 9, 27),       # 7
    ("Chapaa Chance", "chance"),           # 8
    ("Travel Point", "rail", 150, 40),      # 9
    ("Bahari 2", "prop", 120, 9, 27),       # 10
    ("Utility 1", "util", 100),             # 11
    ("Free Parking", "free"),               # 12
    ("Elderwood 1", "prop", 160, 12, 36),   # 13
    ("Chapaa Chance", "chance"),           # 14
    ("Elderwood 2", "prop", 160, 12, 36),   # 15
    ("Travel Point", "rail", 150, 40),      # 16
    ("Utility 2", "util", 100),             # 17
    ("Go to Jail", "go2jail"),              # 18
    ("Chappa Chest", "chest"),             # 19
    ("Travel Point", "rail", 150, 40),      # 20
    ("Maji Wedding 1", "prop", 200, 15, 45),# 21
    ("Maji Tax", "tax", 200),               # 22 ← 200g
    ("Maji Wedding 2", "prop", 200, 15, 45) # 23
]

SETS = {
    "Kilima": ["Kilima 1", "Kilima 2"],
    "Bahari": ["Bahari 1", "Bahari 2"],
    "Elderwood": ["Elderwood 1", "Elderwood 2"],
    "Maji Wedding": ["Maji Wedding 1", "Maji Wedding 2"]
}

# ====================== CARDS ======================
CHEST_CARDS = {
    2: "Advance to GO → +300g", 3: "JAIL do not pass GO → go to Jail", 4: "Everyone pays you 50g",
    5: "Pay 100g", 6: "Collect 100g", 7: "Back 3 spaces", 8: "Forward 3 spaces",
    9: "Pay poorest player 100g", 10: "Go to nearest Travel Point", 11: "Pay 150g", 12: "Collect 200g"
}

CHANCE_CARDS = {
    2: "Free Parking → move there", 3: "Get Out of Jail Free Card!", 4: "Give 50g to each player",
    5: "Pay 200g", 6: "Get 150g", 7: "Move to next Utility", 8: "Move to next main property",
    9: "All give you 100g", 10: "Go to nearest property owned by anyone", 11: "Pay 100g", 12: "Get 200g"
}

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

    # Header
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"**Turn → {cur}** {'(In Jail)' if jail[cur] else ''}")
    with col2: st.markdown(f"**Cash:** {cash[cur]}g")
    with col3: st.button("Next player", on_click=lambda: st.session_state.update(current=(st.session_state.current + 1) % len(p)))

    # Dice roll
    dice = st.text_input("Roll dice (2–12)", key="dice")
    message = ""
    if dice.isdigit():
        roll = int(dice)
        if 2 <= roll <= 12:
            old_pos = pos[cur]
            new_pos = (old_pos + roll) % 24
            pos[cur] = new_pos
            space = BOARD[new_pos]
            space_name, space_type = space[0], space[1]

            # Pass GO
            if new_pos <= old_pos and new_pos != 0:
                cash[cur] += 300
                st.balloons()

            # Taxes
            if space_type == "tax":
                tax_amt = space[2]
                cash[cur] -= tax_amt
                message = f"Paid {tax_amt}g tax"

            # Go to Jail
            elif space_type == "go2jail":
                pos[cur] = 6
                jail[cur] = True
                message = "Sent to Jail!"

            # Chappa Chest
            elif space_type == "chest":
                text = CHEST_CARDS[roll]
                st.success(f"CHAPPA CHEST → {text}")
                if roll == 2: pos[cur] = 0; cash[cur] += 300
                elif roll == 3: pos[cur] = 6; jail[cur] = True
                elif roll == 4:
                    for pl in p:
                        if pl != cur:
                            cash[pl] -= 50
                            cash[cur] += 50
                elif roll == 5: cash[cur] -= 100
                elif roll == 6: cash[cur] += 100
                elif roll == 7: pos[cur] = (pos[cur] - 3) % 24
                elif roll == 8: pos[cur] = (pos[cur] + 3) % 24
                elif roll == 9:
                    poorest = min(p, key=lambda x: cash[x])
                    cash[cur] -= 100; cash[poorest] += 100
                elif roll == 10:
                    for i in range(new_pos + 1, new_pos + 25):
                        if BOARD[i % 24][1] == "rail":
                            pos[cur] = i % 24; break
                elif roll == 11: cash[cur] -= 150
                elif roll == 12: cash[cur] += 200

            # Chapaa Chance
            elif space_type == "chance":
                text = CHANCE_CARDS[roll]
                st.success(f"CHAPAA CHANCE → {text}")
                if roll == 2: pos[cur] = 12
                elif roll == 3: jailfree[cur] += 1
                elif roll == 4:
                    for pl in p:
                        if pl != cur:
                            cash[cur] -= 50; cash[pl] += 50
                elif roll == 5: cash[cur] -= 200
                elif roll == 6: cash[cur] += 150
                elif roll == 7:
                    for i in range(new_pos + 1, new_pos + 25):
                        if BOARD[i % 24][1] == "util":
                            pos[cur] = i % 24; break
                elif roll == 8:
                    for i in range(new_pos + 1, new_pos + 25):
                        if BOARD[i % 24][1] == "prop":
                            pos[cur] = i % 24; break
                elif roll == 9:
                    for pl in p:
                        if pl != cur:
                            cash[pl] -= 100; cash[cur] += 100
                elif roll == 10:
                    for i in range(new_pos + 1, new_pos + 25):
                        idx = i % 24
                        if owner[idx] is not None and owner[idx] != cur:
                            pos[cur] = idx; break
                elif roll == 11: cash[cur] -= 100
                elif roll == 12: cash[cur] += 200

            # AUTO RENT
            if space_type in ("prop", "rail", "util") and owner[new_pos] and owner[new_pos] != cur:
                landlord = owner[new_pos]
                if space_type == "prop":
                    set_name = next(k for k, v in SETS.items() if space_name in v)
                    full = all(owner[BOARD.index(s)] == landlord for s in SETS[set_name])
                    rent = space[4] if full else space[3]
                    reason = f"full {set_name} set" if full else space_name
                elif space_type == "rail":
                    owned = sum(1 for i in range(24) if BOARD[i][1] == "rail" and owner[i] == landlord)
                    rent = owned * 40
                    reason = f"{owned} Travel Points"
                else:
                    owned = sum(1 for i in range(24) if BOARD[i][1] == "util" and owner[i] == landlord)
                    rent = roll * (10 if owned == 2 else 4)
                    reason = f"Utility ×{10 if owned == 2 else 4}"
                cash[cur] -= rent
                cash[landlord] += rent
                message = f"Paid {landlord} {rent}g for {reason}"

            # BUY BUTTON
            if space_type in ("prop", "rail", "util") and owner[new_pos] is None:
                price = space[2]
                if st.button(f"BUY {space_name} – {price}g"):
                    if cash[cur] >= price:
                        cash[cur] -= price
                        owner[new_pos] = cur
                        st.success(f"{cur} bought {space_name}!")
                    else:
                        st.error("Not enough gold!")

            st.success(f"Landed on {space_name} → {message or 'nothing extra'}")

    st.markdown(f"**Current square:** {BOARD[pos[cur]][0]}")

    # Quick buttons
    colq = st.columns(4)
    with colq[0]:
        if st.button("Renown Tax 100g"): cash[cur] -= 100
    with colq[1]:
        if st.button("Maji Tax 200g"): cash[cur] -= 200
    with colq[2]:
        if st.button("Pay 100g to leave Jail"):
            if jail[cur] and cash[cur] >= 100:
                cash[cur] -= 100
                jail[cur] = False

    # Trade
    with st.expander("Trade Properties"):
        giver = st.selectbox("From", p)
        recv = st.selectbox("To", [x for x in p if x != giver])
        owned = [BOARD[i][0] for i in range(24) if owner[i] == giver]
        prop = st.selectbox("Property", ["(none)"] + owned)
        if st.button("Execute Trade") and prop != "(none)":
            idx = next(i for i, s in enumerate(BOARD) if s[0] == prop)
            owner[idx] = recv
            st.success(f"{prop} → {recv}")

    # Balances
    st.markdown("### Players")
    for pl in p:
        props = [BOARD[i][0] for i in range(24) if owner.get(i) == pl]
        st.write(f"**{pl}** – {cash[pl]}g – {'JAILED' if jail[pl] else ''} – JailFree:{jailfree[pl]} – {', '.join(props) or 'none'}")

    if st.button("New Game – Reset Everything"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

import streamlit as st

st.set_page_config(page_title="Palia Monopoly", layout="centered")
st.title("Palia Monopoly – Your Board")

if 'players' not in st.session_state:
    names = st.text_input("Enter player names (comma separated)", "Ashura, Reth, Tish, Hodari").split(",")
    st.session_state.players = [p.strip() for p in names]
    st.session_state.cash = {p: 1200 for p in names}
    st.session_state.pos = {p: 0 for p in names}
    st.session_state.current = 0
    st.rerun()

p = st.session_state.players
cash = st.session_state.cash
current = p[st.session_state.current]

col1, col2, col3 = st.columns(3)
with col1: st.write(f"**Turn:** {current}")
with col2: st.write(f"**Cash:** {cash[current]}g")

dice = st.text_input("Dice roll (e.g. 7) or command", "")
if dice.isdigit():
    roll = int(dice)
    newpos = (st.session_state.pos[current] + roll) % 23
    st.session_state.pos[current] = newpos
    st.success(f"{current} rolled {roll} → space {newpos}")
    st.rerun()

if st.button("Buy property (80-200g)"):
    price = st.number_input("Price", 80, 200, 80, 20)
    cash[current] -= price
    st.success(f"{current} bought for {price}g → {cash[current]}g left")
    st.rerun()

if st.button("Pay rent / tax"):
    amt = st.number_input("Amount", 1, 1000, 50)
    to = st.selectbox("Pay to", ["Bank"] + [x for x in p if x != current])
    cash[current] -= amt
    if to != "Bank": cash[to] += amt
    st.success(f"{current} paid {amt}g → {cash[current]}g")
    st.rerun()

if st.button("Pass GO +300g"):
    cash[current] += 300
    st.balloons()

if st.button("Next player →"):
    st.session_state.current = (st.session_state.current + 1) % len(p)
    st.rerun()

st.write("### Balances")
for pl in p: st.write(f"**{pl}**: {cash[pl]}g")

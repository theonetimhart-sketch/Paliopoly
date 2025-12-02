import streamlit as st

st.set_page_config(page_title="Palia Monopoly", layout="centered")
st.title("Palia Monopoly – Your Board")

# Initialize players if not set (use session_state for input persistence)
if 'players' not in st.session_state:
    default_names = "Ashura, Reth, Tish, Hodari"
    st.session_state.input_names = default_names
    names_input = st.text_input("Enter player names (comma separated)", value=st.session_state.input_names)
    if names_input.strip():  # Only split if not empty
        st.session_state.players = [p.strip() for p in names_input.split(",") if p.strip()]
        st.session_state.input_names = names_input  # Persist input
    else:
        st.session_state.players = [p.strip() for p in default_names.split(",")]
    st.session_state.cash = {p: 1200 for p in st.session_state.players}
    st.session_state.pos = {p: 0 for p in st.session_state.players}
    st.session_state.current = 0
    st.rerun()

# Now safe – players always exist
p = st.session_state.players
cash = st.session_state.cash
current = p[st.session_state.current]

# Turn/Cash display
col1, col2, col3 = st.columns(3)
with col1: st.write(f"**Turn:** {current}")
with col2: st.write(f"**Cash:** {cash[current]}g")

# Dice roll
dice = st.text_input("Dice roll (e.g. 7) or command", "")
if dice.isdigit():
    roll = int(dice)
    newpos = (st.session_state.pos[current] + roll) % 23
    st.session_state.pos[current] = newpos
    st.success(f"{current} rolled {roll} → space {newpos}")
    st.rerun()

# Buy button
if st.button("Buy property (80-200g)"):
    price = st.number_input("Price", 80, 200, 80, 20)
    cash[current] -= price
    st.success(f"{current} bought for {price}g → {cash[current]}g left")
    st.rerun()

# Pay rent/tax
if st.button("Pay rent / tax"):
    amt = st.number_input("Amount", 1, 1000, 50)
    to = st.selectbox("Pay to", ["Bank"] + [x for x in p if x != current])
    cash[current] -= amt
    if to != "Bank": cash[to] += amt
    st.success(f"{current} paid {amt}g → {cash[current]}g")
    st.rerun()

# Pass GO
if st.button("Pass GO +300g"):
    cash[current] += 300
    st.balloons()

# Next player
if st.button("Next player →"):
    st.session_state.current = (st.session_state.current + 1) % len(p)
    st.rerun()

# Balances table
st.write("### Balances")
for pl in p:
    st.write(f"**{pl}**: {cash[pl]}g")

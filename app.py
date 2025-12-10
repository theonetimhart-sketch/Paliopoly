import streamlit as st
import random

# ======================
# PAGE SETUP
# ======================
st.set_page_config(page_title="Paliopoly – Chilled Dude Edition", layout="centered")
st.title("Paliopoly – Chilled Dude Edition — Complete")

# ======================
# SPLASH SCREEN
# ======================
SPLASH_IMAGE = "https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/main/image3.PNG"

if 'passed_splash' not in st.session_state:
    st.session_state.passed_splash = False

if not st.session_state.passed_splash:
    st.image(SPLASH_IMAGE, use_column_width=True)
    st.markdown("### Hi ShorTee, thanks for hosting!")
    st.write("Make sure everyone playing is watching at [lilshrtchit Twitch](https://www.twitch.tv/lilshrtchit)")

    # Input player names
    if 'splash_players_input' not in st.session_state:
        st.session_state.splash_players_input = "Chilled Dude, lilshrtchit, Player3"

    st.session_state.splash_players_input = st.text_input(
        "Enter player names (comma separated):",
        st.session_state.splash_players_input,
        key="splash_names_input"
    )

    tentative_players = [n.strip() for n in st.session_state.splash_players_input.split(",") if n.strip()]

    if "Chilled Dude" in tentative_players:
        st.success("Chilled Dude is present!")
        if st.button("Continue"):
            st.session_state.players = tentative_players
            st.session_state.passed_splash = True
            st.experimental_rerun()
    else:
        pwd = st.text_input("Chilled Dude isn't here? Enter host password to continue:", type="password")
        if st.button("Continue without Chilled Dude"):
            if pwd == "TJediTim":
                st.session_state.players = tentative_players
                st.session_state.passed_splash = True
                st.success("Password accepted — continuing!")
                st.experimental_rerun()
            else:
                st.error("Incorrect password.")
    st.stop()

# ======================
# BOARD SETUP
# ======================
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

# ======================
# INITIALIZE SESSION STATE
# ======================
def init_game_state():
    if 'initialized' not in st.session_state:
        st.session_state.update({
            'initialized': False,
            'players': [],
            'cash': {},
            'position': {},
            'properties': {},
            'in_jail': {},
            'jail_turns': {},
            'jail_free_card': None,
            'current_idx': 0,
            'doubles_streak': 0,
            'rolled': False,
            'landed': None,
            'last_message': "",
            'trade_mode': False,
            'starting_square': "",
            'free_parking_pot': 0,
            'bankrupt': {},
            'confirm_bankrupt_for': None,
            'confirm_next_for': None,
            'easter_eggs_claimed': {}
        })
init_game_state()

ss = st.session_state

# ======================
# START GAME
# ======================
if not ss['initialized']:
    players = ss['players']
    ss['cash'] = {p: 1000 for p in players}
    ss['position'] = {p: 0 for p in players}
    ss['properties'] = {i: None for i in range(len(BOARD))}
    ss['in_jail'] = {p: False for p in players}
    ss['jail_turns'] = {p: 0 for p in players}
    ss['bankrupt'] = {p: False for p in players}
    ss['easter_eggs_claimed'] = {p: {} for p in players}
    ss['initialized'] = True

# ======================
# HELPER FUNCTIONS
# ======================
def next_active_idx(start_idx):
    n = len(ss['players'])
    for _ in range(n):
        start_idx = (start_idx + 1) % n
        candidate = ss['players'][start_idx]
        if not ss['bankrupt'].get(candidate, False):
            return start_idx
    return None

def check_game_end():
    active = [p for p in ss['players'] if not ss['bankrupt'].get(p, False)]
    if len(active) <= 1:
        winner = active[0] if active else None
        ss['last_message'] = f"Game over! Winner: **{winner}**" if winner else "Game over! No players remaining."
        st.success(ss['last_message'])
        return True
    return False

# ======================
# DISPLAY PLAYERS
# ======================
with st.expander("Players & Status", expanded=True):
    cols = st.columns(len(ss['players']))
    for i, p in enumerate(ss['players']):
        status = ""
        if ss['bankrupt'].get(p, False):
            status = " — BANKRUPT"
        elif ss['in_jail'].get(p, False):
            status = " — JAILED"
        cols[i].markdown(f"**{p}** — {ss['cash'][p]}g{status}")

# ======================
# MAIN TURN & DICE
# ======================
cur_idx = ss['current_idx'] % len(ss['players'])
cur = ss['players'][cur_idx]

if ss['bankrupt'].get(cur, False):
    nxt = next_active_idx(cur_idx)
    if nxt is None:
        check_game_end()
    else:
        ss['current_idx'] = nxt
        st.experimental_rerun()

if not ss['rolled']:
    st.info(f"{cur}'s turn — enter dice roll")
    roll = st.number_input("Total rolled", 2, 12, 7, step=1, key=f"roll_{cur}")
    doubles = st.checkbox("Doubles?", key=f"dub_{cur}")
    if st.button("Confirm Roll", key=f"roll_confirm_{cur}"):
        ss['rolled'] = True
        old_pos = ss['position'][cur]
        new_pos = (old_pos + roll) % len(BOARD)
        ss['position'][cur] = new_pos
        ss['landed'] = new_pos

        # GO money
        go_msg = ""
        if old_pos + roll >= len(BOARD) or new_pos == 0:
            ss['cash'][cur] += 300
            st.balloons()
            go_msg = " Passed or landed GO → collected 300g!"

        # Easter eggs: Chilled Dude / lilshrtchit / double 1
        easter_msg = []
        player_here = [p for p,pos in ss['position'].items() if pos==new_pos and p!=cur]
        for p in player_here:
            p_key = p.lower()
            if p_key in ["chilled dude", "lilshrtchit"]:
                if not ss['easter_eggs_claimed'][cur].get(p_key, False):
                    bonus = 10
                    if p_key == "chilled dude":
                        ss['cash'][cur] += bonus
                        ss['easter_eggs_claimed'][cur][p_key] = True
                        easter_msg.append(f"Landed on **Chilled Dude** → collected {bonus}g!")
                    else:
                        btn_key = f"sub_{cur}_{p}"
                        if btn_key not in ss:
                            ss[btn_key] = False
                        if not ss[btn_key]:
                            if st.button(f"Yes, I'm subscribed to {p}", key=btn_key):
                                ss[btn_key] = True
                                ss['cash'][cur] += bonus
                                ss['easter_eggs_claimed'][cur][p_key] = True
                                easter_msg.append(f"Landed on **{p}** → subscribed bonus {bonus}g collected!")

        # Double 1
        if roll==2 and doubles:
            easter_msg.append("Rolled double 1 → Remember to hydrate!")

        ss['last_message'] = f"Landed on **{BOARD[new_pos][0]}**. {go_msg} {' '.join(easter_msg)}"

        # Extra turn for doubles
        if doubles and not ss['in_jail'].get(cur, False):
            ss['rolled'] = False
            ss['last_message'] += " — Doubles! Take another turn."

        st.success(ss['last_message'])
        st.experimental_rerun()
# ======================
# PROPERTY BUYING
# ======================
if ss['rolled'] and ss['landed'] is not None:
    landed_idx = ss['landed']
    landed_square = BOARD[landed_idx]
    typ = landed_square[1]
    if typ in ("prop", "rail", "util") and ss['properties'].get(landed_idx) is None:
        price = landed_square[2]
        if st.button(f"Buy {landed_square[0]} for {price}g?", key=f"buy_{cur}_{landed_idx}"):
            if ss['cash'][cur] >= price:
                ss['cash'][cur] -= price
                ss['properties'][landed_idx] = cur
                ss['last_message'] = f"{cur} bought {landed_square[0]}!"
                st.success(ss['last_message'])
                st.experimental_rerun()
            else:
                st.error("Not enough gold!")

# ======================
# SELL TO BANK
# ======================
if cur and not ss['bankrupt'].get(cur, False):
    st.markdown("---")
    st.markdown("### Sell to Bank (50% value)")
    player_props = [i for i,o in ss['properties'].items() if o == cur]
    if player_props:
        for idx in player_props:
            prop = BOARD[idx]
            price = prop[2] if len(prop)>2 else 0
            sell_price = price//2
            colA, colB = st.columns([3,1])
            colA.markdown(f"{idx}: **{prop[0]}** — Buy price {price}g — Sell to bank for **{sell_price}g**")
            if colB.button(f"Sell {idx}", key=f"sell_{cur}_{idx}"):
                ss['cash'][cur] += sell_price
                ss['properties'][idx] = None
                ss['last_message'] = f"Sold {prop[0]} for {sell_price}g"
                st.success(ss['last_message'])
                st.experimental_rerun()
    else:
        st.write("No properties to sell.")

# ======================
# BANKRUPT / QUIT
# ======================
if cur and not ss['bankrupt'].get(cur, False):
    st.markdown("---")
    if st.button("Bankrupt / Quit", key=f"bankrupt_{cur}"):
        ss['confirm_bankrupt_for'] = cur
        st.experimental_rerun()

if ss.get('confirm_bankrupt_for') == cur:
    st.warning(f"Declare **{cur}** bankrupt? Returns all assets to bank.")
    coly, coln = st.columns(2)
    if coly.button("Confirm Bankruptcy", key=f"confirm_bank_{cur}"):
        for i,o in list(ss['properties'].items()):
            if o==cur:
                ss['properties'][i] = None
        ss['cash'][cur] = 0
        if ss.get('jail_free_card')==cur: ss['jail_free_card']=None
        ss['bankrupt'][cur] = True
        ss['confirm_bankrupt_for'] = None
        ss['last_message'] = f"**{cur}** declared BANKRUPT — assets returned to bank."
        nxt = next_active_idx(ss['current_idx'])
        if nxt is None: check_game_end()
        else: ss['current_idx']=nxt
        st.experimental_rerun()
    if coln.button("Cancel", key=f"cancel_bank_{cur}"):
        ss['confirm_bankrupt_for']=None
        st.experimental_rerun()

# ======================
# TRADE SYSTEM
# ======================
if cur and not ss['bankrupt'].get(cur, False):
    if st.button("Trade / Deal" if not ss['trade_mode'] else "Cancel Trade", key=f"trade_toggle_{cur}"):
        ss['trade_mode'] = not ss['trade_mode']
        st.experimental_rerun()

    if ss['trade_mode']:
        st.subheader("Trade / Deal Maker")
        others = [pl for pl in ss['players'] if pl != cur and not ss['bankrupt'].get(pl, False)]
        if not others:
            st.write("No trading partners available.")
        else:
            partner = st.selectbox("Choose a player to trade with:", others, key=f"trade_partner_{cur}")
            st.markdown("---")
            st.markdown("### Your offer")
            offer_gold = st.number_input(f"{cur} gives gold:", min_value=0, max_value=ss['cash'][cur], step=10, key=f"offer_gold_{cur}")
            your_props = [i for i,o in ss['properties'].items() if o==cur]
            offer_props = st.multiselect("Properties to trade:", your_props, format_func=lambda i: BOARD[i][0], key=f"offer_props_{cur}")
            offer_jail_card = (ss.get('jail_free_card')==cur) and st.checkbox("Give Get Out of Jail Free card", key=f"offer_jail_{cur}")

            st.markdown("### Partner offer")
            partner_gold = st.number_input(f"{partner} gives gold:", min_value=0, max_value=ss['cash'][partner], step=10, key=f"partner_gold_{cur}")
            partner_props = [i for i,o in ss['properties'].items() if o==partner]
            partner_offer_props = st.multiselect("Properties to receive:", partner_props, format_func=lambda i: BOARD[i][0], key=f"partner_props_{cur}")
            partner_jail_card = (ss.get('jail_free_card')==partner) and st.checkbox("Receive their Get Out of Jail Free card", key=f"partner_jail_{cur}")

            if st.button("Confirm Trade", type="primary", key=f"confirm_trade_{cur}"):
                valid = True
                for i in offer_props:
                    if ss['properties'].get(i)!=cur:
                        valid=False; st.error(f"You no longer own {BOARD[i][0]}")
                for i in partner_offer_props:
                    if ss['properties'].get(i)!=partner:
                        valid=False; st.error(f"{partner} no longer owns {BOARD[i][0]}")
                if not valid: st.warning("Trade aborted due to changed ownership.")
                else:
                    ss['cash'][cur]-=offer_gold
                    ss['cash'][partner]+=offer_gold
                    ss['cash'][partner]-=partner_gold
                    ss['cash'][cur]+=partner_gold
                    for i in offer_props: ss['properties'][i]=partner
                    for i in partner_offer_props: ss['properties'][i]=cur
                    if offer_jail_card: ss['jail_free_card']=partner
                    elif partner_jail_card: ss['jail_free_card']=cur
                    st.success("Trade completed.")
                    ss['trade_mode']=False
                    ss['last_message'] = f"Trade completed between **{cur}** and **{partner}**!"
                    st.experimental_rerun()

# ======================
# BOARD OWNERSHIP OVERVIEW
# ======================
st.markdown("---")
with st.expander("Board ownership overview", expanded=True):
    sections = {
        "Kilima": [1,3],
        "Bahari": [7,10],
        "Elderwood": [13,15],
        "Maji Wedding": [21,23],
        "Travel Points": [4,9,16,20],
        "Utilities": [11,17]
    }
    icons = {
        "Kilima":"🏠", "Bahari":"🏖️", "Elderwood":"🌲", "Maji Wedding":"💒",
        "Travel Points":"🚂", "Utilities":"🌿"
    }
    for sec, indices in sections.items():
        st.markdown(f"### {icons.get(sec,'')} {sec}")
        for idx in indices:
            owner = ss['properties'].get(idx) or "Bank"
            st.write(f"{BOARD[idx][0]} — {owner}")

# ======================
# NEW GAME RESET
# ======================
st.markdown("---")
if st.button("New Game (Reset Everything)"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

# ======================
# FINAL CHECK: GAME END
# ======================
check_game_end()

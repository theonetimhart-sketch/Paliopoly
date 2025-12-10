import streamlit as st
import random

# ======================
# PAGE SETUP
# ======================
st.set_page_config(
    page_title="Paliopoly – Chilled Dude Edition",
    layout="centered"
)
st.title("Paliopoly – Chilled Dude Edition — Streamer-Friendly")

# ======================
# SPLASH SCREEN / STREAMER INFO
# ======================
if 'splash_done' not in st.session_state:
    st.session_state['splash_done'] = False

if not st.session_state['splash_done']:
    # Splash image only (image3)
    st.image(
        "https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image3.PNG",
        use_column_width=True
    )

    st.subheader("Welcome to Paliopoly — Chilled Dude Edition!")
    st.markdown("Check out the Twitch stream: [lilshrtchit](https://www.twitch.tv/lilshrtchit)")

    # Player input
    names = st.text_input("Enter player names (comma separated)", "Chilled Dude, lilshrtchit, Player3")
    players = [n.strip() for n in names.split(",") if n.strip()]

    # Host verification if Chilled Dude not present
    if "Chilled Dude" not in players:
        st.warning("Chilled Dude (board host) must be present. Enter Discord name to continue.")
        host_pass = st.text_input("Enter Chilled Dude Discord name:", type="password")
        if host_pass != "TJediTim":
            st.stop()

    if st.button("Start Game / Continue"):
        st.session_state['players'] = players
        st.session_state['splash_done'] = True
        st.experimental_rerun()

    st.stop()  # Stop execution until splash is acknowledged

# ======================
# IN-GAME IMAGES
# ======================
st.image(
    "https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image.png",
    use_column_width=True
)
st.image(
    "https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image2.png",
    use_column_width=True,
    caption="The Board"
)

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

# ======================
# PART 2 — GAME START UI, PLAYER INITIALIZATION
# ======================

# Initialize players and per-player Easter egg tracker if not already done
if st.session_state['splash_done'] and not st.session_state['initialized']:
    players = st.session_state.get('players', [])
    if len(players) < 2:
        st.error("Need at least 2 players to start the game!")
        st.stop()

    st.session_state.cash = {p: 1000 for p in players}
    st.session_state.position = {p: 0 for p in players}
    st.session_state.properties = {i: None for i in range(len(BOARD))}
    st.session_state.in_jail = {p: False for p in players}
    st.session_state.jail_turns = {p: 0 for p in players}
    st.session_state.bankrupt = {p: False for p in players}
    st.session_state.easter_eggs_claimed = {p: {"chilled dude": False, "lilshrtchit": False} for p in players}

    st.session_state.current_idx = 0
    st.session_state.doubles_streak = 0
    st.session_state.rolled = False
    st.session_state.landed = None
    st.session_state.last_message = ""
    st.session_state.trade_mode = False
    st.session_state.starting_square = ""
    st.session_state.free_parking_pot = 0
    st.session_state.initialized = True

    st.success("Game initialized! Roll those dice!")
    st.experimental_rerun()


# ======================
# HELPER FUNCTIONS
# ======================
def next_active_idx(start_idx):
    """Return the index of the next non-bankrupt player"""
    players = st.session_state['players']
    n = len(players)
    idx = start_idx
    for _ in range(n):
        idx = (idx + 1) % n
        if not st.session_state['bankrupt'].get(players[idx], False):
            return idx
    return None

def check_game_end():
    """Check if only one active player remains"""
    active = [p for p in st.session_state['players'] if not st.session_state['bankrupt'].get(p, False)]
    if len(active) <= 1 and st.session_state['initialized']:
        winner = active[0] if active else None
        st.session_state['last_message'] = f"Game over! Winner: **{winner}**" if winner else "Game over! No players remaining."
        return True
    return False

def process_landing(player, roll):
    """Return message based on board landing type"""
    idx = st.session_state['position'][player]
    square = BOARD[idx]
    typ = square[1]
    msg = ""
    if typ == "tax":
        amt = square[2]
        st.session_state['cash'][player] -= amt
        msg = f"Paid {amt}g in tax."
    elif typ == "chest":
        msg = "Draw a Chappa Chest card."
    elif typ == "chance":
        msg = "Draw a Chapaa Chance card."
    elif typ == "jail":
        msg = "Just visiting Jail."
    elif typ == "go2jail":
        st.session_state['position'][player] = 6
        st.session_state['in_jail'][player] = True
        st.session_state['jail_turns'][player] = 0
        msg = "Sent to Jail!"
    elif typ in ("prop", "rail", "util"):
        owner = st.session_state['properties'].get(idx)
        if owner is None:
            msg = f"{square[0]} is unowned."
        elif owner != player:
            msg = f"Owned by {owner}."
    return msg

# ======================
# DISPLAY PLAYER STATUS
# ======================
if st.session_state['initialized']:
    ss = st.session_state
    players = ss['players']
    cols = st.columns(len(players))
    for i, pl in enumerate(players):
        status = ""
        if ss['bankrupt'].get(pl, False):
            status = " — BANKRUPT"
        elif ss['in_jail'].get(pl, False):
            status = " — JAILED"
        cols[i].markdown(f"**{pl}** — {ss['cash'][pl]}g{status}")

# ======================
# PART 3 — DICE ROLL, MOVEMENT, EASTER EGGS
# ======================

if st.session_state['initialized']:
    ss = st.session_state
    players = ss['players']
    cur_idx = ss['current_idx'] % len(players)
    ss['current_idx'] = cur_idx
    cur = players[cur_idx]

    # Skip bankrupt players
    if ss['bankrupt'].get(cur, False):
        nxt = next_active_idx(cur_idx)
        if nxt is None:
            check_game_end()
        else:
            ss['current_idx'] = nxt
            st.experimental_rerun()

    # Dice roll input
    if not ss['rolled']:
        st.info(f"{cur}'s turn — Enter your **real dice roll**")
        roll = st.number_input("Total rolled", 2, 12, 7, step=1, key=f"roll_{cur}")
        doubles = st.checkbox("Doubles?", key=f"dubs_{cur}")
        if st.button("Confirm Roll", key=f"confirm_{cur}"):
            ss['last_roll'] = roll

            # Jail handling
            if ss['in_jail'].get(cur, False):
                if doubles:
                    ss['in_jail'][cur] = False
                    ss['jail_turns'][cur] = 0
                    ss['last_message'] = f"{cur} rolled doubles in jail → released and moves {roll}."
                else:
                    ss['jail_turns'][cur] += 1
                    if ss['jail_turns'][cur] >= 3:
                        ss['in_jail'][cur] = False
                        ss['jail_turns'][cur] = 0
                        ss['last_message'] = f"{cur} failed 3 times → released and moves {roll}."
                    else:
                        ss['last_message'] = f"{cur} did not roll doubles (Jail turn {ss['jail_turns'][cur]}/3)."
                        ss['rolled'] = True
                        st.experimental_rerun()

            # Handle 3 doubles → jail
            if doubles:
                ss['doubles_streak'] += 1
                if ss['doubles_streak'] >= 3:
                    ss['position'][cur] = 6
                    ss['in_jail'][cur] = True
                    ss['jail_turns'][cur] = 0
                    ss['rolled'] = True
                    ss['landed'] = 6
                    ss['last_message'] = "3 DOUBLES → JAIL!"
                    st.experimental_rerun()
            else:
                ss['doubles_streak'] = 0

            # Move player if not in jail
            if not ss['in_jail'].get(cur, False):
                old_pos = ss['position'][cur]
                new_pos = (old_pos + roll) % len(BOARD)

                # Collect GO money
                if old_pos + roll >= len(BOARD) or new_pos == 0:
                    ss['cash'][cur] += 300
                    go_msg = " Passed or landed GO → collected 300g!"
                else:
                    go_msg = ""

                ss['position'][cur] = new_pos
                ss['landed'] = new_pos
                ss['rolled'] = True

                # Process landing message
                landing_msg = process_landing(cur, roll)

                # ----------------------
                # Easter eggs: Chilled Dude / lilshrtchit / double 1
                # ----------------------
                easter_msg = []

                # Ensure tracker exists
                if cur not in ss['easter_eggs_claimed']:
                    ss['easter_eggs_claimed'][cur] = {"chilled dude": False, "lilshrtchit": False}

                # Check if special players are on same square
                player_here = [p for p,pos in ss['position'].items() if pos == new_pos and p != cur]
                for p in player_here:
                    p_key = p.lower()
                    if p_key in ["chilled dude", "lilshrtchit"]:
                        if not ss['easter_eggs_claimed'][cur].get(p_key, False):
                            bonus = 10
                            if p_key == "chilled dude":
                                ss['cash'][cur] += bonus
                                ss['easter_eggs_claimed'][cur][p_key] = True
                                easter_msg.append(f"Landed on **Chilled Dude** → collected {bonus}g! Hang out with Chilled Dude!")
                            else:  # lilshrtchit subscription bonus
                                btn_key = f"sub_{cur}_{p}"
                                if btn_key not in ss:
                                    ss[btn_key] = False
                                if not ss[btn_key]:
                                    if st.button(f"Yes, I'm subscribed to {p}", key=btn_key):
                                        ss[btn_key] = True
                                        ss['cash'][cur] += bonus
                                        ss['easter_eggs_claimed'][cur][p_key] = True
                                        easter_msg.append(f"Landed on **{p}** → subscribed bonus {bonus}g collected!")

                # Double 1 Easter egg
                if roll == 2 and doubles:
                    easter_msg.append("Rolled double 1 → Remember to hydrate!")

                ss['last_message'] = f"Landed on **{BOARD[new_pos][0]}**. {go_msg} {landing_msg} {' '.join(easter_msg)}"

                # Extra turn for doubles
                if doubles and not ss['in_jail'].get(cur, False):
                    ss['rolled'] = False
                    ss['last_message'] += " — Doubles! Take another turn."

                st.experimental_rerun()

# ======================
# PART 4 — PROPERTY, TRADE, BANKRUPTCY, BOARD OVERVIEW, NEW GAME
# ======================

if st.session_state['initialized']:
    ss = st.session_state
    cur = ss['players'][ss['current_idx']]

    if ss['rolled'] and ss['landed'] is not None:
        landed_idx = ss['landed']
        landed_square = BOARD[landed_idx]
        typ = landed_square[1]

        # ----------------------
        # Buy property if unowned
        # ----------------------
        if typ in ("prop", "rail", "util") and ss['properties'].get(landed_idx) is None:
            price = landed_square[2]
            if st.button(f"Buy {landed_square[0]} for {price}g?", key=f"buy_{landed_idx}_{cur}"):
                if ss['cash'][cur] >= price:
                    ss['cash'][cur] -= price
                    ss['properties'][landed_idx] = cur
                    ss['last_message'] = f"{cur} bought {landed_square[0]}!"
                    st.success(ss['last_message'])
                    st.experimental_rerun()
                else:
                    st.error("Not enough gold!")

        # ----------------------
        # Sell to Bank
        # ----------------------
        st.markdown("---")
        st.markdown("### Sell to Bank (50% value)")
        player_props = [i for i,o in ss['properties'].items() if o == cur]
        if player_props:
            for idx in player_props:
                prop = BOARD[idx]
                price = prop[2] if len(prop) > 2 else 0
                sell_price = price // 2
                colA, colB = st.columns([3,1])
                colA.markdown(f"{idx}: **{prop[0]}** — Buy price {price}g — Sell for **{sell_price}g**")
                if colB.button(f"Sell {idx}", key=f"sell_{idx}_{cur}"):
                    ss['cash'][cur] += sell_price
                    ss['properties'][idx] = None
                    ss['last_message'] = f"Sold {prop[0]} for {sell_price}g"
                    st.success(ss['last_message'])
                    st.experimental_rerun()
        else:
            st.write("No properties to sell to the bank.")

        # ----------------------
        # Bankruptcy / Quit
        # ----------------------
        st.markdown("---")
        if st.button("Bankrupt / Quit (return assets to bank)", key=f"bankrupt_{cur}"):
            ss['confirm_bankrupt_for'] = cur
            st.experimental_rerun()

        if ss.get('confirm_bankrupt_for') == cur:
            st.warning(f"Are you sure you want to declare **{cur}** bankrupt? This will return all properties to the bank.")
            coly, coln = st.columns(2)
            if coly.button("Confirm Bankruptcy", key=f"confirm_bankrupt_{cur}"):
                for i,o in list(ss['properties'].items()):
                    if o == cur:
                        ss['properties'][i] = None
                ss['cash'][cur] = 0
                if ss.get('jail_free_card') == cur: ss['jail_free_card'] = None
                ss['bankrupt'][cur] = True
                ss['confirm_bankrupt_for'] = None
                ss['last_message'] = f"**{cur}** declared BANKRUPT — assets returned to bank."
                nxt = next_active_idx(ss['current_idx'])
                if nxt is None: check_game_end()
                else: ss['current_idx'] = nxt
                st.experimental_rerun()
            if coln.button("Cancel", key=f"cancel_bankrupt_{cur}"):
                ss['confirm_bankrupt_for'] = None
                st.experimental_rerun()

        # ----------------------
        # Trade System
        # ----------------------
        if st.button("Trade / Deal" if not ss['trade_mode'] else "Cancel Trade", key=f"trade_mode_{cur}"):
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
                offer_gold = st.number_input(f"{cur} gives gold:", min_value=0, max_value=ss['cash'].get(cur,0), step=10, key=f"offer_gold_{cur}")
                your_props = [i for i,o in ss['properties'].items() if o == cur]
                offer_props = st.multiselect("Properties to trade:", your_props, format_func=lambda i: BOARD[i][0], key=f"offer_props_{cur}")
                offer_jail_card = (ss.get('jail_free_card') == cur) and st.checkbox("Give Get Out of Jail Free card", key=f"offer_jail_{cur}")

                st.markdown("### Partner offer")
                partner_gold = st.number_input(f"{partner} gives gold:", min_value=0, max_value=ss['cash'].get(partner,0), step=10, key=f"partner_gold_{cur}")
                partner_props = [i for i,o in ss['properties'].items() if o == partner]
                partner_offer_props = st.multiselect("Properties to receive:", partner_props, format_func=lambda i: BOARD[i][0], key=f"partner_props_{cur}")
                partner_jail_card = (ss.get('jail_free_card') == partner) and st.checkbox("Receive their Get Out of Jail Free card", key=f"partner_jail_{cur}")

                if st.button("Confirm Trade", type="primary", key=f"confirm_trade_{cur}"):
                    valid = True
                    for i in offer_props:
                        if ss['properties'].get(i) != cur:
                            valid = False; st.error(f"You no longer own {BOARD[i][0]}")
                    for i in partner_offer_props:
                        if ss['properties'].get(i) != partner:
                            valid = False; st.error(f"{partner} no longer owns {BOARD[i][0]}")
                    if not valid:
                        st.warning("Trade aborted due to changed ownership.")
                    else:
                        ss['cash'][cur] -= offer_gold
                        ss['cash'][partner] += offer_gold
                        ss['cash'][partner] -= partner_gold
                        ss['cash'][cur] += partner_gold
                        for i in offer_props: ss['properties'][i] = partner
                        for i in partner_offer_props: ss['properties'][i] = cur
                        if offer_jail_card: ss['jail_free_card'] = partner
                        elif partner_jail_card: ss['jail_free_card'] = cur
                        ss['trade_mode'] = False
                        ss['last_message'] = f"Trade completed between **{cur}** and **{partner}**!"
                        st.success(ss['last_message'])
                        st.experimental_rerun()

    # ----------------------
    # Board ownership overview
    # ----------------------
    st.markdown("---")
    with st.expander("Board ownership (tradeable only)", expanded=True):
        sections = {
            "Kilima": [1,3],
            "Bahari": [7,10],
            "Elderwood": [13,15],
            "Maji Wedding": [21,23],
            "Travel Points": [4,9,16,20],
            "Utilities": [11,17]
        }
        icons = {
            "Kilima": "🏠", "Bahari": "🏖️", "Elderwood": "🌲", "Maji Wedding": "💒",
            "Travel Points": "🚂", "Utilities": "🌿"
        }
        for sec, indices in sections.items():
            st.markdown(f"### {icons.get(sec, '')} {sec}")
            for idx in indices:
                owner_name = ss['properties'].get(idx) or "Bank"
                st.write(f"{BOARD[idx][0]} — {owner_name}")

    # ----------------------
    # New game / reset
    # ----------------------
    st.markdown("---")
    if st.button("New Game (Reset Everything)", key="new_game"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# ----------------------
# FINAL CHECK: GAME END
# ----------------------
check_game_end()

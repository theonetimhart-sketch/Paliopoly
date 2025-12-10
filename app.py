import streamlit as st
import random

# ======================
# PAGE SETUP
# ======================
st.set_page_config(page_title="Paliopoly – Chilled Dude Edition", layout="centered")
st.title("Paliopoly – Chilled Dude Edition — Stream-Friendly")
st.markdown("**Includes: jail mechanics, doubles extra turn, chest/chance cards, Easter eggs, trades, bankruptcies**")

# ======================
# SPLASH SCREEN
# ======================
SPLASH_IMAGE = "https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/main/image3.PNG"

if 'passed_splash' not in st.session_state:
    st.session_state.passed_splash = False

if not st.session_state.passed_splash:
    st.image(SPLASH_IMAGE, use_column_width=True)
    st.markdown("### Welcome to Paliopoly — ShorTee hosting!")
    st.write("Make sure everyone playing is watching at [lilshrtchit Twitch](https://www.twitch.tv/lilshrtchit)")

    if 'splash_players_input' not in st.session_state:
        st.session_state.splash_players_input = "Chilled Dude, TJediTim, lilshrtchit.ttv"

    st.session_state.splash_players_input = st.text_input(
        "Enter player names (comma separated):", st.session_state.splash_players_input
    )

    tentative_players = [n.strip() for n in st.session_state.splash_players_input.split(",") if n.strip()]

    # If Chilled Dude is present
    if any(p.lower() == "chilled dude" for p in tentative_players):
        st.success("Chilled Dude is present — ready to play!")
        if st.button("Continue"):
            st.session_state.players = tentative_players
            st.session_state.passed_splash = True
            st.rerun()
    else:
        pwd = st.text_input(
            "Chilled Dude isn't present? Enter his Discord name to continue...", type="password"
        )
        if st.button("Continue"):
            if pwd == "TJediTim":
                st.session_state.players = tentative_players
                st.session_state.passed_splash = True
                st.success("Password accepted — continuing.")
                st.rerun()
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
# CHEST CARD ACTIONS
# ======================
def chest_go_to_go(player, ss, roll):
    ss['position'][player] = 0
    ss['cash'][player] += 300

def chest_go_to_jail(player, ss, roll):
    ss['position'][player] = 6
    ss['in_jail'][player] = True
    ss['jail_turns'][player] = 0

CHEST_CARDS_LIST = [
    ("Chapaa Chase to GO!", chest_go_to_go),
    ("Proudhorned Sernuk teleports you, GO TO JAIL!", chest_go_to_jail),
    ("Elouisa found a cryptid, everyone pays you 50g not to tell them about it", 
        lambda p,ss,roll: [ss['cash'].__setitem__(q, ss['cash'][q]-50) or ss['cash'].__setitem__(p, ss['cash'][p]+50) for q in ss['players'] if q!=p]),
    ("Eshe made Kenli enforce the land tax. Pay 100g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]-100)),
    ("Collect 100g from Subira for helping the order", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]+100)),
    ("Ogupuu drags you into a whirlpool and moves you back 3 spaces", lambda p,ss,roll: ss['position'].__setitem__(p, (ss['position'][p]-3) % len(BOARD))),
    ("Bluebristle Muujin pushes you forward 3 spaces", lambda p,ss,roll: ss['position'].__setitem__(p, (ss['position'][p]+3) % len(BOARD))),
    ("Tamala tricks you into paying the poorest player 100g", lambda p,ss,roll: (lambda poorest=min([x for x in ss['players'] if not ss['bankrupt'].get(x,False)], key=lambda x: ss['cash'][x]): (ss['cash'].__setitem__(p, ss['cash'][p]-100), ss['cash'].__setitem__(poorest, ss['cash'][poorest]+100)))()),
    ("You followed a Peki to the next Travel Point", lambda p,ss,roll: ss['position'].__setitem__(p, min([4,9,16,21], key=lambda x:(x-ss['position'][p])%len(BOARD)))),
    ("Tish has new furniture, pay 150g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]-150)),
    ("Zeki drops off some treasure. collect 200g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]+200))
]

# ======================
# CHANCE CARD ACTIONS
# ======================
def chance_free_parking(player, ss, roll):
    ss['position'][player] = 12
    ss['cash'][player] += ss['free_parking_pot']
    ss['free_parking_pot'] = 0

def chance_get_out_of_jail(player, ss, roll):
    ss['jail_free_card'] = player

CHANCE_CARDS_LIST = [
    ("Tau spots something buried, go to Free Parking to dig it up and collect whatever is there", chance_free_parking),
    ("Plumehound buried a Get Out of Jail Free card, go ahead and keep that one", chance_get_out_of_jail),
    ("Jina found a rare artifact. Give 50g to all the humans", lambda p,ss,roll: [ss['cash'].__setitem__(q, ss['cash'][q]+50) or ss['cash'].__setitem__(p, ss['cash'][p]-50) for q in ss['players'] if q!=p]),
    ("Caught in the restricted section, pay Caleri 200g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]-200)),
    ("Collect 150g for promoting Jels new wardrobe", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]+150)),
    ("Follow a flutterfox to the next shrub", lambda p,ss,roll: ss['position'].__setitem__(p, next((i for i in [13,15,22,24] if i>ss['position'][p]),13))),
    ("Ormuu pushes you to next main property", lambda p,ss,roll: ss['position'].__setitem__(p, next((i for i in [1,3,7,10,13,15,22,24] if i>ss['position'][p]),1))),
    ("Badruu gives you new fruit, everyone gives you 100g for the seeds", lambda p,ss,roll: [ss['cash'].__setitem__(q, ss['cash'][q]-100) or ss['cash'].__setitem__(p, ss['cash'][p]+100) for q in ss['players'] if q!=p]),
    ("Go and help the trufflet at the nearest owned property", lambda p,ss,roll: ss['position'].__setitem__(p, min([i for i,o in ss['properties'].items() if o and BOARD[i][1] in ('prop','rail','util')], key=lambda x:(x-ss['position'][p])%len(BOARD)))),
    ("you lost the Gardners runestone, Pay 100g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]-100)),
    ("Reth just started selling beanburgers and flowtato fries, he pays you 200g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]+200))
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
# SPLASH SCREEN (PLAYER ENTRY)
# ======================
SPLASH_IMAGE = "https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/main/image3.PNG"

if 'passed_splash' not in st.session_state:
    st.session_state.passed_splash = False

if not st.session_state.passed_splash:
    st.image(SPLASH_IMAGE, use_column_width=True)
    st.markdown("### Hi ShorTee, thanks for hosting!")
    st.write("Make sure everyone playing is watching at https://www.twitch.tv/lilshrtchit")
    
    # Player name input
    if 'splash_players_input' not in st.session_state:
        st.session_state.splash_players_input = "Chilled Dude, TJediTim, lilshrtchit.ttv"
    st.session_state.splash_players_input = st.text_input("Enter player names (comma separated):", st.session_state.splash_players_input)
    tentative_players = [n.strip() for n in st.session_state.splash_players_input.split(",") if n.strip()]

    # If Chilled Dude is present
    if "Chilled Dude" in tentative_players:
        st.success("Chilled Dude is playing — yay!")
        if st.button("Continue"):
            st.session_state.players = tentative_players
            st.session_state.passed_splash = True
            st.rerun()
    else:
        pwd = st.text_input("Chilled Dude isn't here? Enter host password to continue...", type="password")
        if st.button("Continue"):
            if pwd == "TJediTim":
                st.session_state.players = tentative_players
                st.session_state.passed_splash = True
                st.success("Password accepted — continuing.")
                st.rerun()
            else:
                st.error("Incorrect password.")
    st.stop()  # Halt until splash complete

# ======================
# START GAME / PLAYER INITIALIZATION
# ======================
if not st.session_state.initialized:
    st.subheader("Welcome to Paliopoly — Chilled Dude Edition!")
    names_input = st.session_state.get('players', [])
    if not names_input:
        names_input = "Chilled Dude, lilshrtchit"
    names = st.text_input("Confirm player names (comma separated):", ", ".join(names_input))
    if st.button("Start Game"):
        players = [n.strip() for n in names.split(",") if n.strip()]
        if len(players) < 2:
            st.error("Need at least 2 players to start!")
        else:
            st.session_state.players = players
            st.session_state.cash = {p: 1000 for p in players}
            st.session_state.position = {p: 0 for p in players}
            st.session_state.properties = {i: None for i in range(len(BOARD))}
            st.session_state.in_jail = {p: False for p in players}
            st.session_state.jail_turns = {p: 0 for p in players}
            st.session_state.bankrupt = {p: False for p in players}
            st.session_state.easter_eggs_claimed = {p: {} for p in players}
            st.session_state.current_idx = 0
            st.session_state.doubles_streak = 0
            st.session_state.rolled = False
            st.session_state.landed = None
            st.session_state.last_message = ""
            st.session_state.trade_mode = False
            st.session_state.starting_square = ""
            st.session_state.free_parking_pot = 0
            st.session_state.initialized = True
            st.success("Game started! Roll those dice!")
            st.rerun()

# ======================
# HELPER FUNCTIONS
# ======================
def next_active_idx(start_idx):
    """Find the next non-bankrupt player index"""
    players = st.session_state.get('players', [])
    n = len(players)
    if n == 0: return None
    idx = start_idx
    for _ in range(n):
        idx = (idx + 1) % n
        candidate = players[idx]
        if not st.session_state.bankrupt.get(candidate, False):
            return idx
    return None

def check_game_end():
    """Check if only one active player remains"""
    players = st.session_state.get('players', [])
    active = [p for p in players if not st.session_state.bankrupt.get(p, False)]
    if len(active) <= 1 and st.session_state.initialized:
        winner = active[0] if active else None
        st.session_state.last_message = f"Game over! Winner: **{winner}**" if winner else "Game over! No players remaining."
        return True
    return False

def process_landing(player, roll):
    """Placeholder for property, chest, chance processing"""
    idx = st.session_state['position'][player]
    square = BOARD[idx]
    msg = ""
    typ = square[1]
    if typ == 'chest':
        card = random.choice(CHEST_CARDS_LIST)
        card[1](player, st.session_state, roll)
        msg = f"Chest card: {card[0]}"
    elif typ == 'chance':
        card = random.choice(CHANCE_CARDS_LIST)
        card[1](player, st.session_state, roll)
        msg = f"Chance card: {card[0]}"
    elif typ == 'tax':
        amount = square[2]
        st.session_state.cash[player] -= amount
        msg = f"Paid tax {amount}g"
    elif typ == 'go2jail':
        st.session_state.position[player] = 6
        st.session_state.in_jail[player] = True
        st.session_state.jail_turns[player] = 0
        msg = "Go to Jail!"
    return msg

# ======================
# MAIN TURN
# ======================
if st.session_state.initialized:
    ss = st.session_state
    cur_idx = ss['current_idx'] % len(ss['players'])
    cur = ss['players'][cur_idx]
    if ss['bankrupt'].get(cur, False):
        nxt = next_active_idx(cur_idx)
        if nxt is None:
            check_game_end()
        else:
            ss['current_idx'] = nxt
            st.rerun()

    # Player info
    with st.expander("Players and status", expanded=False):
        cols = st.columns(len(ss['players']))
        for i, pl in enumerate(ss['players']):
            status_text = ""
            if ss['bankrupt'].get(pl, False):
                status_text = " — BANKRUPT"
            elif ss['in_jail'].get(pl, False):
                status_text = " — JAILED"
            cols[i].markdown(f"**{pl}** — {ss['cash'][pl]}g{status_text}")

# ----------------------
# Dice roll input
# ----------------------
if st.session_state.initialized and not ss['rolled']:
    st.info(f"{cur}'s turn: Enter your **real dice roll**")
    roll = st.number_input("Total rolled", 2, 12, 7, step=1, key="roll_input")
    doubles = st.checkbox("Doubles?", key="dubs_input")
    if st.button("Confirm Roll", type="primary"):
        ss['last_roll'] = roll
        old_pos = ss['position'][cur]

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
                    ss['starting_square'] = BOARD[old_pos][0]
                    st.rerun()

        # Doubles streak
        if doubles:
            ss['doubles_streak'] += 1
            if ss['doubles_streak'] >= 3:
                ss['position'][cur] = 6
                ss['in_jail'][cur] = True
                ss['jail_turns'][cur] = 0
                ss['rolled'] = True
                ss['starting_square'] = BOARD[6][0]
                ss['landed'] = 6
                ss['last_message'] = "3 DOUBLES → JAIL!"
                st.rerun()
        else:
            ss['doubles_streak'] = 0

        # Move player if not in jail
        if not ss['in_jail'].get(cur, False):
            new_pos = (old_pos + roll) % len(BOARD)
            # GO collection
            go_msg = ""
            if old_pos + roll >= len(BOARD) or new_pos == 0:
                ss['cash'][cur] += 300
                st.balloons()
                go_msg = " Passed or landed GO → collected 300g!"
            ss['position'][cur] = new_pos
            ss['landed'] = new_pos
            ss['rolled'] = True
            ss['starting_square'] = BOARD[old_pos][0]

            # Landing processing
            landing_msg = process_landing(cur, roll)

            # ----------------------
            # Easter eggs: Chilled Dude / lilshrtchit / double 1
            # ----------------------
            if cur not in ss['easter_eggs_claimed']:
                ss['easter_eggs_claimed'][cur] = {}
            easter_msg = []
            player_here = [p for p, pos in ss['position'].items() if pos == new_pos and p != cur]
            for p in player_here:
                p_key = p.lower()
                if p_key in ["chilled dude", "lilshrtchit"]:
                    if not ss['easter_eggs_claimed'][cur].get(p_key, False):
                        bonus = 10
                        if p_key == "chilled dude":
                            ss['cash'][cur] += bonus
                            ss['easter_eggs_claimed'][cur][p_key] = True
                            easter_msg.append(f"Landed on **Chilled Dude** → collected {bonus}g! Hang out with Chilled Dude!")
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

            if roll == 2 and doubles:
                easter_msg.append("Rolled double 1 → Remember to hydrate!")

            ss['last_message'] = f"Landed on **{BOARD[new_pos][0]}**. {go_msg} {landing_msg} {' '.join(easter_msg)}"

            if doubles and not ss['in_jail'].get(cur, False):
                ss['rolled'] = False
                ss['last_message'] += " — Doubles! Take another turn."

        st.rerun()

# ======================
# BUY PROPERTY IF UNOWNED
# ======================
if ss['rolled'] and ss['landed'] is not None:
    landed_idx = ss['landed']
    landed_square = BOARD[landed_idx]
    typ = landed_square[1]
    if typ in ("prop", "rail", "util") and ss['properties'].get(landed_idx) is None:
        price = landed_square[2]
        if st.button(f"Buy {landed_square[0]} for {price}g?"):
            if ss['cash'].get(cur, 0) >= price:
                ss['cash'][cur] -= price
                ss['properties'][landed_idx] = cur
                ss['last_message'] = f"{cur} bought {landed_square[0]}!"
                st.success(ss['last_message'])
                st.rerun()
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
            price = prop[2] if len(prop) > 2 else 0
            sell_price = price // 2
            colA, colB = st.columns([3,1])
            colA.markdown(f"{idx}: **{prop[0]}** — Buy price {price}g — Sell to bank for **{sell_price}g**")
            if colB.button(f"Sell {idx}", key=f"sell_{idx}"):
                ss['cash'][cur] += sell_price
                ss['properties'][idx] = None
                ss['last_message'] = f"Sold {prop[0]} for {sell_price}g"
                st.success(ss['last_message'])
                st.rerun()
    else:
        st.write("No properties to sell to the bank.")

# ======================
# BANKRUPT / QUIT
# ======================
if cur and not ss['bankrupt'].get(cur, False):
    st.markdown("---")
    if st.button("Bankrupt / Quit (return assets to bank)"):
        ss['confirm_bankrupt_for'] = cur
        st.rerun()

if ss.get('confirm_bankrupt_for') == cur:
    st.warning(f"Are you sure you want to declare **{cur}** bankrupt? This will return all properties to the bank.")
    coly, coln = st.columns(2)
    if coly.button("Confirm Bankruptcy"):
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
        st.rerun()
    if coln.button("Cancel"):
        ss['confirm_bankrupt_for'] = None
        st.rerun()

# ======================
# TRADE SYSTEM
# ======================
if cur and not ss['bankrupt'].get(cur, False):
    if st.button("Trade / Deal" if not ss['trade_mode'] else "Cancel Trade"):
        ss['trade_mode'] = not ss['trade_mode']
        st.rerun()

    if ss['trade_mode']:
        st.subheader("Trade / Deal Maker")
        others = [pl for pl in ss['players'] if pl != cur and not ss['bankrupt'].get(pl, False)]
        if not others:
            st.write("No trading partners available.")
        else:
            partner = st.selectbox("Choose a player to trade with:", others, key="trade_partner")
            st.markdown("---")
            st.markdown("### Your offer")
            offer_gold = st.number_input(f"{cur} gives gold:", min_value=0, max_value=ss['cash'].get(cur,0), step=10, key="offer_gold")
            your_props = [i for i,o in ss['properties'].items() if o == cur]
            offer_props = st.multiselect("Properties to trade:", your_props, format_func=lambda i: BOARD[i][0], key="offer_props")
            offer_jail_card = (ss.get('jail_free_card') == cur) and st.checkbox("Give Get Out of Jail Free card", key="offer_jail")

            st.markdown("### Partner offer")
            partner_gold = st.number_input(f"{partner} gives gold:", min_value=0, max_value=ss['cash'].get(partner,0), step=10, key="partner_gold")
            partner_props = [i for i,o in ss['properties'].items() if o == partner]
            partner_offer_props = st.multiselect("Properties to receive:", partner_props, format_func=lambda i: BOARD[i][0], key="partner_props")
            partner_jail_card = (ss.get('jail_free_card') == partner) and st.checkbox("Receive their Get Out of Jail Free card", key="partner_jail")

            if st.button("Confirm Trade", type="primary", key="confirm_trade"):
                valid = True
                for i in offer_props:
                    if ss['properties'].get(i) != cur:
                        valid = False; st.error(f"You no longer own {BOARD[i][0]}")
                for i in partner_offer_props:
                    if ss['properties'].get(i) != partner:
                        valid = False; st.error(f"{partner} no longer owns {BOARD[i][0]}")
                if not valid: st.warning("Trade aborted due to changed ownership.")
                else:
                    ss['cash'][cur] -= offer_gold
                    ss['cash'][partner] += offer_gold
                    ss['cash'][partner] -= partner_gold
                    ss['cash'][cur] += partner_gold
                    for i in offer_props: ss['properties'][i] = partner
                    for i in partner_offer_props: ss['properties'][i] = cur
                    if offer_jail_card: ss['jail_free_card'] = partner
                    elif partner_jail_card: ss['jail_free_card'] = cur
                    st.success("Trade completed.")
                    ss['trade_mode'] = False
                    ss['last_message'] = f"Trade completed between **{cur}** and **{partner}**!"
                    st.rerun()

# ======================
# BOARD OWNERSHIP OVERVIEW (TRADEABLE ONLY)
# ======================
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

# ======================
# NEW GAME RESET
# ======================
st.markdown("---")
if st.button("New Game (Reset Everything)"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ======================
# FINAL CHECK: GAME END
# ======================
check_game_end()

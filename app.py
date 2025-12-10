import streamlit as st
import random

# ======================
# PAGE SETUP
# ======================
st.set_page_config(page_title="Paliopoly – Chilled Dude Edition", layout="centered")
st.title("Paliopoly – Chilled Dude Edition — Streamer Friendly")
st.markdown("**Includes: Jail, Doubles, Chest/Chance cards, Easter eggs, property trading, bank handling**")

# ======================
# SPLASH SCREEN
# ======================
SPLASH_IMAGE = "https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/main/image3.PNG"

if 'passed_splash' not in st.session_state:
    st.session_state['passed_splash'] = False

if not st.session_state['passed_splash']:
    st.image(SPLASH_IMAGE, use_column_width=True)
    st.markdown("### Hi ShorTee, thanks for hosting!")
    st.write("Make sure everyone playing is watching at [lilshrtchit Twitch](https://www.twitch.tv/lilshrtchit)")

    # Default player names
    if 'splash_players_input' not in st.session_state:
        st.session_state['splash_players_input'] = "Chilled Dude, lilshrtchit"

    st.session_state['splash_players_input'] = st.text_input(
        "Confirm player names (comma separated):", 
        st.session_state['splash_players_input']
    )

    tentative_players = [n.strip() for n in st.session_state['splash_players_input'].split(",") if n.strip()]

    # If Chilled Dude is present, continue
    if "Chilled Dude" in tentative_players:
        st.success("Chilled Dude is playing — ready to go!")
        if st.button("Continue"):
            st.session_state['players'] = tentative_players
            st.session_state['passed_splash'] = True
            st.rerun()
    else:
        # Password fallback
        pwd = st.text_input("Chilled Dude isn't here? Enter host password to continue...", type="password")
        if st.button("Continue"):
            if pwd == "TJediTim":
                st.success("Password accepted — continuing.")
                st.session_state['players'] = tentative_players
                st.session_state['passed_splash'] = True
                st.rerun()
            else:
                st.error("Incorrect password.")

    st.stop()

# ======================
# BOARD SETUP
# ======================
BOARD = [
    ("GO", "go"),
    ("Kilima 1", "prop", 80, 6, 18),
    ("Renown Tax", "tax", 100),
    ("Kilima 2", "prop", 80, 6, 18),
    ("Travel Point 1", "rail", 150, 40),
    ("Chappa Chest", "chest"),
    ("Jail", "jail"),
    ("Bahari 1", "prop", 120, 9, 27),
    ("Chapaa Chance", "chance"),
    ("Travel Point 2", "rail", 150, 40),
    ("Bahari 2", "prop", 120, 9, 27),
    ("Utility 1", "util", 100),
    ("Free Parking", "free"),
    ("Elderwood 1", "prop", 160, 12, 36),
    ("Chapaa Chance", "chance"),
    ("Elderwood 2", "prop", 160, 12, 36),
    ("Travel Point 3", "rail", 150, 40),
    ("Utility 2", "util", 100),
    ("Go to Jail", "go2jail"),
    ("Chappa Chest", "chest"),
    ("Travel Point 4", "rail", 150, 40),
    ("Maji Wedding 1", "prop", 200, 15, 45),
    ("Maji Tax", "tax", 200),
    ("Maji Wedding 2", "prop", 200, 15, 45)
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
    ("Elouisa found a cryptid, everyone pays you 50g", 
     lambda p, ss, roll: [ss['cash'].__setitem__(q, ss['cash'][q]-50) or ss['cash'].__setitem__(p, ss['cash'][p]+50) for q in ss['players'] if q != p]),
    ("Eshe made Kenli enforce the land tax. Pay 100g", lambda p, ss, roll: ss['cash'].__setitem__(p, ss['cash'][p]-100)),
    ("Collect 100g from Subira for helping the order", lambda p, ss, roll: ss['cash'].__setitem__(p, ss['cash'][p]+100)),
    ("Ogupuu drags you into a whirlpool and moves you back 3 spaces", lambda p, ss, roll: ss['position'].__setitem__(p, (ss['position'][p]-3) % len(BOARD))),
    ("Bluebristle Muujin pushes you forward 3 spaces", lambda p, ss, roll: ss['position'].__setitem__(p, (ss['position'][p]+3) % len(BOARD))),
    ("Tamala tricks you into paying the poorest player 100g", 
     lambda p, ss, roll: (lambda poorest=min([x for x in ss['players'] if not ss['bankrupt'].get(x,False)], key=lambda x: ss['cash'][x]): 
                          (ss['cash'].__setitem__(p, ss['cash'][p]-100), ss['cash'].__setitem__(poorest, ss['cash'][poorest]+100)))()),
    ("You followed a Peki to the next Travel Point", lambda p, ss, roll: ss['position'].__setitem__(p, min([4,9,16,21], key=lambda x:(x-ss['position'][p])%len(BOARD)))),
    ("Tish has new furniture, pay 150g", lambda p, ss, roll: ss['cash'].__setitem__(p, ss['cash'][p]-150)),
    ("Zeki drops off some treasure. collect 200g", lambda p, ss, roll: ss['cash'].__setitem__(p, ss['cash'][p]+200))
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
    ("Tau spots something buried, go to Free Parking to dig it up", chance_free_parking),
    ("Plumehound buried a Get Out of Jail Free card", chance_get_out_of_jail),
    ("Jina found a rare artifact. Give 50g to all the humans", lambda p, ss, roll: [ss['cash'].__setitem__(q, ss['cash'][q]+50) or ss['cash'].__setitem__(p, ss['cash'][p]-50) for q in ss['players'] if q!=p]),
    ("Caught in the restricted section, pay Caleri 200g", lambda p, ss, roll: ss['cash'].__setitem__(p, ss['cash'][p]-200)),
    ("Collect 150g for promoting Jels new wardrobe", lambda p, ss, roll: ss['cash'].__setitem__(p, ss['cash'][p]+150)),
    ("Follow a flutterfox to the next shrub", lambda p, ss, roll: ss['position'].__setitem__(p, next((i for i in [13,15,22,24] if i>ss['position'][p]),13))),
    ("Ormuu pushes you to next main property", lambda p, ss, roll: ss['position'].__setitem__(p, next((i for i in [1,3,7,10,13,15,22,24] if i>ss['position'][p]),1))),
    ("Badruu gives you new fruit, everyone gives you 100g for the seeds", lambda p, ss, roll: [ss['cash'].__setitem__(q, ss['cash'][q]-100) or ss['cash'].__setitem__(p, ss['cash'][p]+100) for q in ss['players'] if q!=p]),
    ("Go and help the trufflet at the nearest owned property", lambda p, ss, roll: ss['position'].__setitem__(p, min([i for i,o in ss['properties'].items() if o and BOARD[i][1] in ('prop','rail','util')], key=lambda x:(x-ss['position'][p])%len(BOARD)))),
    ("You lost the Gardners runestone, Pay 100g", lambda p, ss, roll: ss['cash'].__setitem__(p, ss['cash'][p]-100)),
    ("Reth just started selling beanburgers and flowtato fries, he pays you 200g", lambda p, ss, roll: ss['cash'].__setitem__(p, ss['cash'][p]+200))
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

# Initialize per-player Easter eggs if empty
for p in st.session_state.get('players', []):
    if p not in st.session_state['easter_eggs_claimed']:
        st.session_state['easter_eggs_claimed'][p] = {"chilled dude": False, "lilshrtchit": False}

# ======================
# START GAME UI
# ======================
if not st.session_state.initialized:
    st.subheader("Welcome to Paliopoly — Chilled Dude Edition!")
    st.markdown("Check out the Twitch stream: [lilshrtchit](https://www.twitch.tv/lilshrtchit)")

    # Player names input
    names = st.text_input("Player names (comma separated)", "Chilled Dude, lilshrtchit, Player3")
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
            st.session_state.jail_free_card = None
            st.session_state.current_idx = 0
            st.session_state.doubles_streak = 0
            st.session_state.rolled = False
            st.session_state.landed = None
            st.session_state.last_message = ""
            st.session_state.trade_mode = False
            st.session_state.starting_square = ""
            st.session_state.free_parking_pot = 0
            st.session_state.bankrupt = {p: False for p in players}
            st.session_state.easter_eggs_claimed = {p: {"chilled dude": False, "lilshrtchit": False} for p in players}
            st.session_state.initialized = True
            st.success("Game started! Roll those dice!")
            st.rerun()

# ======================
# HELPER FUNCTIONS
# ======================
def next_active_idx(start_idx):
    """Return next non-bankrupt player index."""
    players = st.session_state['players']
    n = len(players)
    idx = start_idx
    for _ in range(n):
        idx = (idx + 1) % n
        if not st.session_state['bankrupt'].get(players[idx], False):
            return idx
    return None

def check_game_end():
    active = [p for p in st.session_state['players'] if not st.session_state['bankrupt'].get(p, False)]
    if len(active) <= 1:
        winner = active[0] if active else None
        st.session_state['last_message'] = f"Game over! Winner: **{winner}**" if winner else "Game over! No players remaining."
        return True
    return False

def process_landing(player, roll):
    idx = st.session_state['position'][player]
    square = BOARD[idx]
    typ = square[1]
    msg = ""
    if typ == "chest":
        card = random.choice(CHEST_CARDS_LIST)
        card[1](player, st.session_state, roll)
        msg = f"Chest card drawn: {card[0]}"
    elif typ == "chance":
        card = random.choice(CHANCE_CARDS_LIST)
        card[1](player, st.session_state, roll)
        msg = f"Chance card drawn: {card[0]}"
    elif typ == "tax":
        amount = square[2]
        st.session_state['cash'][player] -= amount
        msg = f"Paid tax {amount}g"
    elif typ == "go2jail":
        st.session_state['position'][player] = 6
        st.session_state['in_jail'][player] = True
        st.session_state['jail_turns'][player] = 0
        msg = "Sent to Jail"
    return msg

# ======================
# MAIN TURN
# ======================
if st.session_state.initialized:
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
            st.rerun()

    # Display player info
    with st.expander("Players and status", expanded=False):
        cols = st.columns(len(players))
        for i, pl in enumerate(players):
            status = ""
            if ss['bankrupt'].get(pl, False):
                status = " — BANKRUPT"
            elif ss['in_jail'].get(pl, False):
                status = " — JAILED"
            cols[i].markdown(f"**{pl}** — {ss['cash'][pl]}g{status}")

    # ----------------------
    # DICE ROLL INPUT
    # ----------------------
    if not ss['rolled']:
        st.info(f"{cur}'s turn: Enter your dice roll")
        roll = st.number_input("Total rolled", 2, 12, 7, step=1, key="roll_input")
        doubles = st.checkbox("Doubles?", key="dubs_input")
        if st.button("Confirm Roll", type="primary"):
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
                        ss['last_message'] = f"{cur} failed 3 turns → released and moves {roll}."
                    else:
                        ss['last_message'] = f"{cur} did not roll doubles (Jail turn {ss['jail_turns'][cur]}/3)."
                        ss['rolled'] = True
                        ss['starting_square'] = BOARD[ss['position'][cur]][0]
                        st.rerun()

            # Handle doubles streak
            if doubles:
                ss['doubles_streak'] += 1
                if ss['doubles_streak'] >= 3:
                    ss['position'][cur] = 6  # Jail
                    ss['in_jail'][cur] = True
                    ss['jail_turns'][cur] = 0
                    ss['rolled'] = True
                    ss['starting_square'] = BOARD[ss['position'][cur]][0]
                    ss['landed'] = 6
                    ss['last_message'] = "3 DOUBLES → JAIL!"
                    st.rerun()
            else:
                ss['doubles_streak'] = 0

            # Move player if not jailed
            if not ss['in_jail'].get(cur, False):
                old_pos = ss['position'][cur]
                new_pos = (old_pos + roll) % len(BOARD)

                # GO collection
                go_msg = ""
                if old_pos + roll >= len(BOARD) or new_pos == 0:
                    ss['cash'][cur] += 300
                    st.balloons()
                    go_msg = "Passed or landed GO → collected 300g!"

                # Update position
                ss['position'][cur] = new_pos
                ss['landed'] = new_pos
                ss['rolled'] = True
                ss['starting_square'] = BOARD[old_pos][0]

                # Process landing
                landing_msg = process_landing(cur, roll)

                # ----------------------
                # Easter eggs: Chilled Dude / lilshrtchit / double 1
                # ----------------------
                easter_msg = []
                if 'easter_eggs_claimed' not in ss:
                    ss['easter_eggs_claimed'] = {}
                if cur not in ss['easter_eggs_claimed']:
                    ss['easter_eggs_claimed'][cur] = {}

                # Other players on same square
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
                                if btn_key not in ss: ss[btn_key] = False
                                if not ss[btn_key]:
                                    if st.button(f"Yes, I'm subscribed to {p}", key=btn_key):
                                        ss[btn_key] = True
                                        ss['cash'][cur] += bonus
                                        ss['easter_eggs_claimed'][cur][p_key] = True
                                        easter_msg.append(f"Landed on **{p}** → subscribed bonus {bonus}g collected!")

                # Double 1 Easter egg
                if roll == 2 and doubles:
                    easter_msg.append("Rolled double 1 → Remember to hydrate!")

                # Combine messages
                ss['last_message'] = f"Landed on **{BOARD[new_pos][0]}**. {go_msg} {landing_msg} {' '.join(easter_msg)}"

                # Extra turn for doubles
                if doubles and not ss['in_jail'].get(cur, False):
                    ss['rolled'] = False
                    ss['last_message'] += " — Doubles! Take another turn."

            st.rerun()

# ======================
# START GAME UI
# ======================
if not st.session_state.initialized:
    st.subheader("Welcome to Paliopoly — Chilled Dude Edition!")
    st.markdown("Check out the Twitch stream: [lilshrtchit](https://www.twitch.tv/lilshrtchit)")

    # Player names input
    names = st.text_input("Player names (comma separated)", "Chilled Dude, lilshrtchit, Player3")
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
            st.session_state.jail_free_card = None
            st.session_state.current_idx = 0
            st.session_state.doubles_streak = 0
            st.session_state.rolled = False
            st.session_state.landed = None
            st.session_state.last_message = ""
            st.session_state.trade_mode = False
            st.session_state.starting_square = ""
            st.session_state.free_parking_pot = 0
            st.session_state.bankrupt = {p: False for p in players}
            st.session_state.easter_eggs_claimed = {p: {"chilled dude": False, "lilshrtchit": False} for p in players}
            st.session_state.initialized = True
            st.success("Game started! Roll those dice!")
            st.rerun()

# ======================
# HELPER FUNCTIONS
# ======================
def next_active_idx(start_idx):
    """Return next non-bankrupt player index."""
    players = st.session_state['players']
    n = len(players)
    idx = start_idx
    for _ in range(n):
        idx = (idx + 1) % n
        if not st.session_state['bankrupt'].get(players[idx], False):
            return idx
    return None

def check_game_end():
    active = [p for p in st.session_state['players'] if not st.session_state['bankrupt'].get(p, False)]
    if len(active) <= 1:
        winner = active[0] if active else None
        st.session_state['last_message'] = f"Game over! Winner: **{winner}**" if winner else "Game over! No players remaining."
        return True
    return False

def process_landing(player, roll):
    idx = st.session_state['position'][player]
    square = BOARD[idx]
    typ = square[1]
    msg = ""
    if typ == "chest":
        card = random.choice(CHEST_CARDS_LIST)
        card[1](player, st.session_state, roll)
        msg = f"Chest card drawn: {card[0]}"
    elif typ == "chance":
        card = random.choice(CHANCE_CARDS_LIST)
        card[1](player, st.session_state, roll)
        msg = f"Chance card drawn: {card[0]}"
    elif typ == "tax":
        amount = square[2]
        st.session_state['cash'][player] -= amount
        msg = f"Paid tax {amount}g"
    elif typ == "go2jail":
        st.session_state['position'][player] = 6
        st.session_state['in_jail'][player] = True
        st.session_state['jail_turns'][player] = 0
        msg = "Sent to Jail"
    return msg

# ======================
# MAIN TURN
# ======================
if st.session_state.initialized:
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
            st.rerun()

    # Display player info
    with st.expander("Players and status", expanded=False):
        cols = st.columns(len(players))
        for i, pl in enumerate(players):
            status = ""
            if ss['bankrupt'].get(pl, False):
                status = " — BANKRUPT"
            elif ss['in_jail'].get(pl, False):
                status = " — JAILED"
            cols[i].markdown(f"**{pl}** — {ss['cash'][pl]}g{status}")

    # ----------------------
    # DICE ROLL INPUT
    # ----------------------
    if not ss['rolled']:
        st.info(f"{cur}'s turn: Enter your dice roll")
        roll = st.number_input("Total rolled", 2, 12, 7, step=1, key="roll_input")
        doubles = st.checkbox("Doubles?", key="dubs_input")
        if st.button("Confirm Roll", type="primary"):
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
                        ss['last_message'] = f"{cur} failed 3 turns → released and moves {roll}."
                    else:
                        ss['last_message'] = f"{cur} did not roll doubles (Jail turn {ss['jail_turns'][cur]}/3)."
                        ss['rolled'] = True
                        ss['starting_square'] = BOARD[ss['position'][cur]][0]
                        st.rerun()

            # Handle doubles streak
            if doubles:
                ss['doubles_streak'] += 1
                if ss['doubles_streak'] >= 3:
                    ss['position'][cur] = 6  # Jail
                    ss['in_jail'][cur] = True
                    ss['jail_turns'][cur] = 0
                    ss['rolled'] = True
                    ss['starting_square'] = BOARD[ss['position'][cur]][0]
                    ss['landed'] = 6
                    ss['last_message'] = "3 DOUBLES → JAIL!"
                    st.rerun()
            else:
                ss['doubles_streak'] = 0

            # Move player if not jailed
            if not ss['in_jail'].get(cur, False):
                old_pos = ss['position'][cur]
                new_pos = (old_pos + roll) % len(BOARD)

                # GO collection
                go_msg = ""
                if old_pos + roll >= len(BOARD) or new_pos == 0:
                    ss['cash'][cur] += 300
                    st.balloons()
                    go_msg = "Passed or landed GO → collected 300g!"

                # Update position
                ss['position'][cur] = new_pos
                ss['landed'] = new_pos
                ss['rolled'] = True
                ss['starting_square'] = BOARD[old_pos][0]

                # Process landing
                landing_msg = process_landing(cur, roll)

                # ----------------------
                # Easter eggs: Chilled Dude / lilshrtchit / double 1
                # ----------------------
                easter_msg = []
                if 'easter_eggs_claimed' not in ss:
                    ss['easter_eggs_claimed'] = {}
                if cur not in ss['easter_eggs_claimed']:
                    ss['easter_eggs_claimed'][cur] = {}

                # Other players on same square
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
                                if btn_key not in ss: ss[btn_key] = False
                                if not ss[btn_key]:
                                    if st.button(f"Yes, I'm subscribed to {p}", key=btn_key):
                                        ss[btn_key] = True
                                        ss['cash'][cur] += bonus
                                        ss['easter_eggs_claimed'][cur][p_key] = True
                                        easter_msg.append(f"Landed on **{p}** → subscribed bonus {bonus}g collected!")

                # Double 1 Easter egg
                if roll == 2 and doubles:
                    easter_msg.append("Rolled double 1 → Remember to hydrate!")

                # Combine messages
                ss['last_message'] = f"Landed on **{BOARD[new_pos][0]}**. {go_msg} {landing_msg} {' '.join(easter_msg)}"

                # Extra turn for doubles
                if doubles and not ss['in_jail'].get(cur, False):
                    ss['rolled'] = False
                    ss['last_message'] += " — Doubles! Take another turn."

            st.rerun()

import streamlit as st
import random

# ======================
# PAGE SETUP
# ======================
st.set_page_config(page_title="Paliopoly – Chilled Dude Edition (Fixed)", layout="centered")
st.title("Paliopoly – Chilled Dude Edition — Improved")
st.markdown("**Fixes: jail, doubles, cards, GO money, ownership view, next-turn confirm, endgame handling**")

# ======================
# SPLASH SCREEN
# ======================
# image3 raw URL
SPLASH_IMAGE = "https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/main/image3.PNG"
if 'passed_splash' not in st.session_state:
    st.session_state.passed_splash = False

if not st.session_state.passed_splash:
    st.image(SPLASH_IMAGE, use_column_width=True)
    st.markdown("### Hi ShorTee, thanks for hosting!")
    st.write("make sure everyone playing is watching at https://www.twitch.tv/lilshrtchit")
    # Let user input player names before continuing (we store temporarily)
    if 'splash_players_input' not in st.session_state:
        st.session_state.splash_players_input = "Chilled Dude, TJediTim, lilshrtchit.ttv"
    st.session_state.splash_players_input = st.text_input("Enter player names (comma separated):", st.session_state.splash_players_input)
    tentative_players = [n.strip() for n in st.session_state.splash_players_input.split(",") if n.strip()]
    # If Chilled Dude is present show popup
    if "Chilled Dude" in tentative_players:
        st.success("And Chilled Dude is playing, yay!")
        if st.button("Continue"):
            st.session_state.players = tentative_players
            st.session_state.passed_splash = True
            st.rerun()
    else:
        pwd = st.text_input("Chilled Dude isn't here? What is his name on Discord to continue...", type="password")
        if st.button("Continue"):
            if pwd == "TJediTim":
                st.session_state.players = tentative_players
                st.session_state.passed_splash = True
                st.success("Password accepted — continuing.")
                st.experimental_rerun()
            else:
                st.error("Incorrect password.")
    # HALT here until continue pressed
    st.stop()

# ======================
# IMAGES (main UI)
# ======================
st.image("https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image.png", use_column_width=True)
st.image("https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image2.png", use_column_width=True, caption="The Board")

# ======================
# BOARD SETUP (your provided board)
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
# CARD FLAVOUR TEXT (editable) - preserved
# Using lists for shuffle & draw-under-deck
# Each card: (text, action_fn(player, ss, roll))
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
     lambda p,ss,roll: [ss['cash'].__setitem__(q, ss['cash'][q]-50) or ss['cash'].__setitem__(p, ss['cash'][p]+50)
                       for q in ss['players'] if q!=p]),
    ("Eshe made Kenli enforce the land tax. Pay 100g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]-100)),
    ("Collect 100g from Subira for helping the order", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]+100)),
    ("Ogupuu drags you into a whirlpool and moves you back 3 spaces", lambda p,ss,roll: ss['position'].__setitem__(p, (ss['position'][p]-3) % len(BOARD))),
    ("Bluebristle Muujin pushes you forward 3 spaces", lambda p,ss,roll: ss['position'].__setitem__(p, (ss['position'][p]+3) % len(BOARD))),
    ("Tamala tricks you into paying the poorest player 100g",
     lambda p,ss,roll: (lambda poorest=min([x for x in ss['players'] if not ss['bankrupt'].get(x,False)], key=lambda x: ss['cash'][x]): (
         ss['cash'].__setitem__(p, ss['cash'][p]-100), ss['cash'].__setitem__(poorest, ss['cash'][poorest]+100)))()),
    ("You followed a Peki to the next Travel Point", lambda p,ss,roll: ss['position'].__setitem__(p, min([4,9,16,21], key=lambda x:(x-ss['position'][p])%len(BOARD)))),
    ("Tish has new furniture, pay 150g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]-150)),
    ("Zeki drops off some treasure. collect 200g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]+200))
]

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
# INITIALIZE SESSION STATE (safe defaults)
# ======================
def init_game_state():
    if 'initialized' not in st.session_state:
        st.session_state.update({
            'initialized': False,
            'players': st.session_state.get('players', []),
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
            'bankrupt': {},  # mapping player -> bool
            'confirm_bankrupt_for': None,  # stores player awaiting confirm
            'confirm_next_for': None,  # store player awaiting next confirm
            # decks for under-the-deck behavior
            'chest_deck': random.sample(CHEST_CARDS_LIST, len(CHEST_CARDS_LIST)),
            'chance_deck': random.sample(CHANCE_CARDS_LIST, len(CHANCE_CARDS_LIST)),
        })

init_game_state()

# If the players were set from the splash but we haven't completed initialization, show Start Game UI
if not st.session_state.initialized:
    st.subheader("Start Paliopoly Session")
    # default names field pre-filled from splash input (if any)
    default_names = ", ".join(st.session_state.get('players', [])) if st.session_state.get('players') else "Chilled Dude, TJediTim, lilshrtchit.ttv"
    names = st.text_input("Player names", default_names)
    if st.button("Start Game"):
        players = [n.strip() for n in names.split(",") if n.strip()]
        if len(players) < 2:
            st.error("Need 2+ players!")
        else:
            st.session_state.players = players
            st.session_state.cash = {p:1000 for p in players}
            st.session_state.position = {p:0 for p in players}
            st.session_state.properties = {i: None for i in range(len(BOARD))}
            st.session_state.in_jail = {p: False for p in players}
            st.session_state.jail_turns = {p:0 for p in players}
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
            st.session_state.initialized = True
            # re-shuffle decks when game starts
            st.session_state.chest_deck = random.sample(CHEST_CARDS_LIST, len(CHEST_CARDS_LIST))
            st.session_state.chance_deck = random.sample(CHANCE_CARDS_LIST, len(CHANCE_CARDS_LIST))
            st.success("Game started! Roll those real dice!")
            st.rerun()

# ======================
# helper: get next active player index (skips bankrupt)
# ======================
def next_active_idx(start_idx):
    players = st.session_state.get('players', [])
    n = len(players)
    if n == 0:
        return None
    idx = start_idx
    for _ in range(n):
        idx = (idx + 1) % n
        candidate = players[idx]
        if not st.session_state.bankrupt.get(candidate, False):
            return idx
    return None  # no active found

# ======================
# helper: check game end
# ======================
def check_game_end():
    players = st.session_state.get('players', [])
    active = [p for p in players if not st.session_state.bankrupt.get(p, False)]
    if len(active) <= 1 and st.session_state.initialized:
        winner = active[0] if active else None
        st.session_state.last_message = f"Game over! Winner: **{winner}**" if winner else "Game over! No players remaining."
        return True
    return False

# ======================
# Helper: process landing effects (tax, rent, free, jail, chest/chance, buy prompt)
# If a card moves you, recursively process new landing (max depth to avoid loops)
# Uses under-the-deck behavior: pop(0) and append to bottom
# ======================
def process_landing(player, roll_value, depth=0):
    """Process the effects of landing on the square where player currently is.
    Returns a message string of what happened (concatenated)."""
    if depth > 6:
        return " (stopped recursive card moves)"
    ss = st.session_state
    pos = ss['position'][player]
    space = BOARD[pos]
    name, typ = space[0], space[1]
    messages = []
    # Tax
    if typ == "tax":
        tax = space[2]
        ss['cash'][player] -= tax
        ss['free_parking_pot'] += tax
        messages.append(f"Paid **{tax}g {name}** → added to Free Parking pot!")
    # Free Parking
    elif typ == "free":
        if ss['free_parking_pot'] > 0:
            amt = ss['free_parking_pot']
            ss['cash'][player] += amt
            ss['free_parking_pot'] = 0
            messages.append(f"FREE PARKING JACKPOT! Collected **{amt}g**")
        else:
            messages.append("Free Parking — no pot yet!")
    # Go to jail
    elif typ == "go2jail":
        ss['position'][player] = 6
        ss['in_jail'][player] = True
        ss['jail_turns'][player] = 0
        messages.append("GO TO JAIL!")
        return " ".join(messages)
    # Owned property rent
    elif typ in ("prop", "rail", "util") and ss['properties'].get(pos) and ss['properties'].get(pos) != player:
        landlord = ss['properties'][pos]
        if typ == "prop":
            rent = space[3]
        elif typ == "rail":
            rails_owned = sum(1 for i,o in ss['properties'].items() if o == landlord and BOARD[i][1] == "rail")
            rent = 40 * (2 ** (rails_owned - 1)) if rails_owned >= 1 else 40
        else:  # util
            utils_owned = sum(1 for i,o in ss['properties'].items() if o == landlord and BOARD[i][1] == "util")
            rent = roll_value * (4 if utils_owned == 1 else 10)
        ss['cash'][player] -= rent
        ss['cash'][landlord] += rent
        messages.append(f"Paid **{landlord}** {rent}g rent on **{name}**!")
    # Chest / Chance cards (draw from top of deck and put under deck)
    elif typ == "chest":
        if len(ss['chest_deck']) == 0:
            ss['chest_deck'] = random.sample(CHEST_CARDS_LIST, len(CHEST_CARDS_LIST))
        card = ss['chest_deck'].pop(0)
        ss['chest_deck'].append(card)  # card goes under deck
        text, action = card
        # perform card action
        action(player, ss, roll_value)
        messages.append(f"Chappa Chest → {text}")
        # recursively process new landing if move occurred
        messages.append(process_landing(player, roll_value, depth+1))
    elif typ == "chance":
        if len(ss['chance_deck']) == 0:
            ss['chance_deck'] = random.sample(CHANCE_CARDS_LIST, len(CHANCE_CARDS_LIST))
        card = ss['chance_deck'].pop(0)
        ss['chance_deck'].append(card)
        text, action = card
        action(player, ss, roll_value)
        messages.append(f"Chapaa Chance → {text}")
        messages.append(process_landing(player, roll_value, depth+1))

    return " ".join([m for m in messages if m])

# ======================
# MAIN GAME UI & LOGIC
# ======================
if st.session_state.initialized:
    ss = st.session_state
    players = ss.get('players', [])
    cur_idx = ss.get('current_idx', 0)

    # ensure cur_idx valid
    if players:
        cur_idx = cur_idx % len(players)
    else:
        cur_idx = 0
    ss['current_idx'] = cur_idx
    cur = players[cur_idx] if players else None

    cash = ss.get('cash', {})
    pos = ss.get('position', {})
    owner = ss.get('properties', {})
    jail = ss.get('in_jail', {})
    pot = ss.get('free_parking_pot', 0)

    # HEADER: show players list with bankrupt grey-out
    with st.expander("Players and status", expanded=False):
        cols = st.columns(len(players) if players else 1)
        for i,pl in enumerate(players):
            label = f"{pl} — {ss['cash'].get(pl,0)}g"
            if ss['bankrupt'].get(pl, False):
                cols[i].markdown(f"✅ **{pl}** — BANKRUPT")
            else:
                jail_tag = " — JAILED" if ss['in_jail'].get(pl, False) else ""
                cols[i].markdown(f"**{pl}** — {ss['cash'].get(pl,0)}g{jail_tag}")

    # If current player is bankrupt, skip them automatically to next active
    if cur and ss['bankrupt'].get(cur, False):
        nxt = next_active_idx(cur_idx)
        if nxt is None:
            check_game_end()
        else:
            ss['current_idx'] = nxt
            st.experimental_rerun()

    # show main turn header
    if cur:
        col1, col2, col3, col4, col5 = st.columns([2,2,2,2.5,2.5])
        with col1:
            status = " — JAILED" if jail.get(cur, False) else ""
            bankrupt_label = " — BANKRUPT" if ss['bankrupt'].get(cur, False) else ""
            st.markdown(f"**Turn: {cur}**{status}{bankrupt_label}")
        with col2:
            st.markdown(f"**Gold: {cash.get(cur,0)}g**")
        with col3:
            st.markdown(f"**Pot: {pot}g**")
        with col4:
            if ss['rolled']:
                st.success(f"Started on: **{ss['starting_square']}**")
            else:
                st.info(f"Starting on: **{BOARD[pos.get(cur,0)][0]}**")
        with col5:
            # Next Player: require confirmation to avoid misclick
            if ss['rolled']:
                if ss.get('confirm_next_for') == cur:
                    st.warning("Confirm move to next player?")
                    yes, no = st.columns(2)
                    if yes.button("Confirm Next", key=f"confirm_next_yes_{cur}"):
                        # advance to next active
                        nxt = next_active_idx(cur_idx)
                        # reset per-turn flags
                        ss['rolled'] = False
                        ss['landed'] = None
                        ss['starting_square'] = ""
                        ss['trade_mode'] = False
                        ss['last_message'] = ""
                        ss['confirm_next_for'] = None
                        # reset doubles streak when turn ends
                        ss['doubles_streak'] = 0
                        if nxt is None:
                            check_game_end()
                        else:
                            ss['current_idx'] = nxt
                        st.experimental_rerun()
                    if no.button("Cancel", key=f"confirm_next_no_{cur}"):
                        ss['confirm_next_for'] = None
                        st.experimental_rerun()
                else:
                    if st.button("Next Player (Confirm)", use_container_width=True):
                        ss['confirm_next_for'] = cur
                        st.experimental_rerun()
            else:
                st.button("Next Player", disabled=True, use_container_width=True)
                st.caption("Roll first!")

    if ss['last_message']:
        st.success(ss['last_message'])

    # ======================
    # helper functions used within turn scope
    # ======================
    def add_cash(player, amt):
        ss['cash'][player] = ss['cash'].get(player,0) + amt

    def move_player(player, new_pos):
        ss['position'][player] = new_pos

    # ======================
    # ROLL DICE (only if player is not bankrupt)
    # ======================
    if cur and not ss['bankrupt'].get(cur, False):
        # skip roll UI if player already rolled and needs to buy etc.
        if not ss['rolled']:
            st.info("Enter your **real dice roll**")
            roll = st.number_input("Total rolled", 2, 12, 7, step=1, key="roll_input")
            doubles = st.checkbox("Doubles?", key="dubs_input")
            # Pay-to-exit jail button (50g)
            if ss['in_jail'].get(cur, False):
                if st.button("Pay 50g to Exit Jail"):
                    if ss['cash'].get(cur,0) >= 50:
                        ss['cash'][cur] -= 50
                        ss['in_jail'][cur] = False
                        ss['jail_turns'][cur] = 0
                        ss['last_message'] = f"{cur} paid 50g and left jail."
                        st.experimental_rerun()
                    else:
                        st.error("Not enough gold to pay.")

            if st.button("Confirm Roll", type="primary"):
                ss['last_roll'] = roll
                # If player is in jail: special handling
                if ss['in_jail'].get(cur, False):
                    if doubles:
                        # Immediately freed and move by the roll
                        ss['in_jail'][cur] = False
                        ss['jail_turns'][cur] = 0
                        ss['last_message'] = f"{cur} rolled doubles in jail → released and moves {roll}."
                        # fallthrough to movement
                    else:
                        # not doubles: increase jail turns
                        ss['jail_turns'][cur] = ss['jail_turns'].get(cur,0) + 1
                        if ss['jail_turns'][cur] >= 3:
                            # release on 3rd failed attempt and use the 3rd roll for movement
                            ss['in_jail'][cur] = False
                            ss['jail_turns'][cur] = 0
                            ss['last_message'] = f"{cur} failed 3 times → released and moves {roll}."
                            # fallthrough to movement
                        else:
                            # still in jail and didn't roll doubles: end their attempt (no move)
                            ss['last_message'] = f"{cur} did not roll doubles (Jail turn {ss['jail_turns'][cur]}/3)."
                            # mark they have "rolled" because they've taken their jail attempt (so they must confirm Next Player)
                            ss['rolled'] = True
                            ss['starting_square'] = BOARD[ss['position'][cur]][0]
                            # reset doubles streak because turn effectively ends
                            ss['doubles_streak'] = 0
                            st.experimental_rerun()
                # Doubles streak handling (only if not in jail or just freed)
                if doubles:
                    ss['doubles_streak'] = ss.get('doubles_streak',0) + 1
                    if ss['doubles_streak'] >= 3:
                        # 3 consecutive doubles → go to jail immediately (do not move by the 3rd roll)
                        ss['position'][cur] = 6
                        ss['in_jail'][cur] = True
                        ss['jail_turns'][cur] = 0
                        ss['rolled'] = True
                        ss['starting_square'] = BOARD[pos.get(cur,0)][0]
                        ss['landed'] = 6
                        ss['last_message'] = "3 DOUBLES → JAIL!"
                        st.experimental_rerun()
                else:
                    ss['doubles_streak'] = 0

                # perform movement if not still in jail
                if not ss['in_jail'].get(cur, False):
                    old_pos = ss['position'].get(cur, 0)
                    new_pos = (old_pos + roll) % len(BOARD)
                    # GO money: collect when passing or landing on GO
                    if old_pos + roll >= len(BOARD) or new_pos == 0:
                        add_cash(cur, 300)
                        st.balloons()
                        go_msg = " Passed or landed GO → collected 300g!"
                    else:
                        go_msg = ""
                    move_player(cur, new_pos)
                    ss['landed'] = new_pos
                    ss['rolled'] = True
                    ss['starting_square'] = BOARD[old_pos][0]
                    # process landing (this will also handle chest/chance decks and any moves they cause)
                    landing_msg = process_landing(cur, roll)
                    # If landed on property that is unowned, buy prompt will appear below, so we record last_message accordingly
                    msg = f"Landed on **{BOARD[new_pos][0]}**. {go_msg} {landing_msg}"
                    ss['last_message'] = msg
                    # If doubles and not jailed, allow another roll immediately (do not advance current_idx)
                    if doubles and not ss['in_jail'].get(cur,False):
                        ss['rolled'] = False  # allow them to roll again immediately
                        # keep doubles_streak as is (so next doubles could send to jail)
                        ss['last_message'] += " — Doubles! Take another turn."
                        # do NOT advance current player index; they keep the turn
                    else:
                        # set rolled True; they must confirm Next Player to move on
                        ss['rolled'] = True
                # finally re-render
                st.experimental_rerun()

    # ======================
    # BUY PROPERTY (appears after landing when unowned)
    # ======================
    if cur and ss['rolled']:
        landed_idx = ss.get('landed')
        if landed_idx is not None:
            landed_square = BOARD[landed_idx]
            if landed_square[1] in ("prop", "rail", "util") and ss['properties'].get(landed_idx) is None:
                price = landed_square[2]
                if st.button(f"Buy {landed_square[0]} for {price}g?"):
                    if ss['cash'].get(cur,0) >= price:
                        ss['cash'][cur] -= price
                        ss['properties'][landed_idx] = cur
                        ss['last_message'] = f"{cur} bought {landed_square[0]}!"
                        st.experimental_rerun()
                    else:
                        st.error("Not enough gold!")

    # ======================
    # SELL TO BANK (50%) - only allow current active player (not bankrupt)
    # ======================
    if cur and not ss['bankrupt'].get(cur, False):
        st.markdown("---")
        st.markdown("### Sell to Bank (50% value)")
        player_props = [i for i,o in owner.items() if o == cur]
        if player_props:
            for idx in player_props:
                prop = BOARD[idx]
                price = prop[2] if len(prop) > 2 else 0
                sell_price = price // 2
                colA, colB = st.columns([3,1])
                colA.markdown(f"{idx}: **{prop[0]}** — Buy price {price}g — Sell to bank for **{sell_price}g**")
                if colB.button(f"Sell {idx}", key=f"sell_{idx}"):
                    ss['cash'][cur] = ss['cash'].get(cur,0) + sell_price
                    ss['properties'][idx] = None
                    ss['last_message'] = f"Sold {prop[0]} for {sell_price}g"
                    st.success(ss['last_message'])
                    st.experimental_rerun()
        else:
            st.write("No properties to sell to the bank.")

    # ======================
    # BANKRUPT / QUIT button with confirmation (current player only)
    # ======================
    if cur and not ss['bankrupt'].get(cur, False):
        st.markdown("---")
        if st.button("Bankrupt / Quit (return assets to bank)"):
            ss['confirm_bankrupt_for'] = cur
            st.experimental_rerun()
    if ss.get('confirm_bankrupt_for') == cur:
        st.warning(f"Are you sure you want to declare **{cur}** bankrupt? This will return all properties to the bank.")
        coly, coln = st.columns(2)
        if coly.button("Confirm Bankruptcy"):
            # perform bankruptcy: return properties, set cash 0, mark bankrupt True, remove jail card
            for i,o in list(ss['properties'].items()):
                if o == cur:
                    ss['properties'][i] = None
            ss['cash'][cur] = 0
            if ss.get('jail_free_card') == cur:
                ss['jail_free_card'] = None
            ss['bankrupt'][cur] = True
            ss['confirm_bankrupt_for'] = None
            ss['last_message'] = f"**{cur}** declared BANKRUPT — assets returned to bank."
            # advance to next active
            nxt = next_active_idx(cur_idx)
            if nxt is None:
                check_game_end()
            else:
                ss['current_idx'] = nxt
            st.experimental_rerun()
        if coln.button("Cancel"):
            ss['confirm_bankrupt_for'] = None
            st.experimental_rerun()

    # ======================
    # TRADE SYSTEM (disabled for bankrupt players)
    # ======================
    if cur and not ss['bankrupt'].get(cur, False):
        if st.button("Trade / Deal" if not ss['trade_mode'] else "Cancel Trade"):
            ss['trade_mode'] = not ss['trade_mode']
            st.experimental_rerun()

        if ss['trade_mode']:
            st.subheader("Trade / Deal Maker")
            others = [pl for pl in players if pl != cur and not ss['bankrupt'].get(pl, False)]
            if not others:
                st.write("No trading partners available.")
            else:
                partner = st.selectbox("Choose a player to trade with:", others, key="trade_partner")
                st.markdown("---")
                st.markdown("### Your offer")
                offer_gold = st.number_input(f"{cur} gives gold:", min_value=0, max_value=ss['cash'].get(cur,0), step=10, key="offer_gold")
                your_props = [i for i,o in owner.items() if o == cur]
                offer_props = st.multiselect("Properties to trade:", your_props, format_func=lambda i: BOARD[i][0], key="offer_props")
                offer_jail_card = (ss.get('jail_free_card') == cur) and st.checkbox("Give Get Out of Jail Free card", key="offer_jail")

                st.markdown("### Partner offer")
                partner_gold = st.number_input(f"{partner} gives gold:", min_value=0, max_value=ss['cash'].get(partner,0), step=10, key="partner_gold")
                partner_props = [i for i,o in owner.items() if o == partner]
                partner_offer_props = st.multiselect("Properties to receive:", partner_props, format_func=lambda i: BOARD[i][0], key="partner_props")
                partner_jail_card = (ss.get('jail_free_card') == partner) and st.checkbox("Receive their Get Out of Jail Free card", key="partner_jail")

                if st.button("Confirm Trade", type="primary", key="confirm_trade"):
                    # validate ownership still holds
                    valid = True
                    for i in offer_props:
                        if ss['properties'].get(i) != cur:
                            valid = False
                            st.error(f"You no longer own {BOARD[i][0]}")
                    for i in partner_offer_props:
                        if ss['properties'].get(i) != partner:
                            valid = False
                            st.error(f"{partner} no longer owns {BOARD[i][0]}")
                    if not valid:
                        st.warning("Trade aborted due to changed ownership.")
                    else:
                        # execute cash transfers
                        ss['cash'][cur] -= offer_gold
                        ss['cash'][partner] += offer_gold
                        ss['cash'][partner] -= partner_gold
                        ss['cash'][cur] += partner_gold
                        # transfer properties
                        for i in offer_props: ss['properties'][i] = partner
                        for i in partner_offer_props: ss['properties'][i] = cur
                        # transfer jail card
                        if offer_jail_card:
                            ss['jail_free_card'] = partner
                        elif partner_jail_card:
                            ss['jail_free_card'] = cur
                        st.success("Trade completed.")
                        ss['trade_mode'] = False
                        ss['last_message'] = f"Trade completed between **{cur}** and **{partner}**!"
                        st.experimental_rerun()

    # ======================
    # Board Ownership overview
    # ======================
    st.markdown("---")
    with st.expander("Board ownership (who owns what?)", expanded=True):
        rows = []
        for idx, space in enumerate(BOARD):
            owner_name = ss['properties'].get(idx) or "Bank"
            rows.append(f"{idx}: **{space[0]}** — {owner_name}")
        st.write("\n\n".join(rows))

    # ======================
    # NEW GAME
    # ======================
    st.markdown("---")
    if st.button("New Game (Reset Everything)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

    # check for game end after all actions
    check_game_end()

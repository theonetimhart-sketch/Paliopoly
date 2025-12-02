import streamlit as st

# ======================
# PAGE SETUP
# ======================
st.set_page_config(page_title="Paliopoly – Chilled Dude Edition", layout="centered")
st.title("Paliopoly – Chilled Dude Edition")
st.markdown("**Real board • Real dice • Real signs • not S6 affiliated, just player made for fun**")

# ======================
# IMAGES
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
# ======================
CHEST_CARDS = {
    2: ("Chapaa Chase to GO!", lambda cur,pos,cash,pot: (pos.update({cur:0}), cash.update({cur: cash[cur]+300}))),
    3: ("Proudhorned Sernuk teleports you, GO TO JAIL!", lambda cur,pos,cash,pot: (pos.update({cur:6}), st.session_state.in_jail.update({cur: True}))),
    4: ("Elouisa fount a cryptid, everyone pays you 50g not to tell them about it", lambda cur,pos,cash,pot: [cash.update({p: cash[p]-50}) or cash.update({cur: cash[cur]+50}) for p in st.session_state.players if p != cur]),
    5: ("Eshe made Kenli enforce the land tax. Pay 100g", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]-100})),
    6: ("Collect 100g from Subira for helping the order", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]+100})),
    7: ("Ogupuu drags you into a whirlpool and moves you back 3 spaces", lambda cur,pos,cash,pot: pos.update({cur: (pos[cur]-3)%len(BOARD)})),
    8: ("Bluebristle Muujin pushes you forward 3 spaces", lambda cur,pos,cash,pot: pos.update({cur: (pos[cur]+3)%len(BOARD)})),
    9: ("Tamala tricks you into paying the poorest player 100g", lambda cur,pos,cash,pot: (lambda poorest=min(st.session_state.players, key=lambda x: cash[x]): (cash.update({cur: cash[cur]-100}), cash.update({poorest: cash[poorest]+100})) if cash[cur]>=100 else None)()),
    10: ("You followed a Peki to the next Travel Point", lambda cur,pos,cash,pot: pos.update({cur: min([4,9,16,21], key=lambda x:(x-pos[cur])%len(BOARD))})),
    11: ("Tish has new furniture, pay 150g", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]-150})),
    12: ("Zeki drops off some treasure. collect 200g", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]+200}))
}

CHANCE_CARDS = {
    2: ("Tau spots something buried, go to Free Parking to dig it up and collect whatever is there", lambda cur,pos,cash,pot: (pos.update({cur:12}), cash.update({cur: cash[cur]+pot}), st.session_state.__setitem__('free_parking_pot', 0))),
    3: ("Plumehound buried a Get Out of Jail Free card, go ahead and keep that one", lambda cur,pos,cash,pot: st.session_state.__setitem__('jail_free_card', cur)),
    4: ("Jina found a rare artifact. Give 50g to all the humans", lambda cur,pos,cash,pot: [cash.update({cur: cash[cur]-50}) or cash.update({p: cash[p]+50}) for p in st.session_state.players if p != cur]),
    5: ("Caught in the restricted section, pay Caleri 200g", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]-200})),
    6: ("Collect 150g for promoting Jels new wardrobe", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]+150})),
    7: ("Follow a flutterfox to the next shrub", lambda cur,pos,cash,pot: pos.update({cur: next((i for i in [13,15,22,24] if i>pos[cur]),13)})),
    8: ("Ormuu pushes you to next main property", lambda cur,pos,cash,pot: pos.update({cur: next((i for i in [1,3,7,10,13,15,22,24] if i>pos[cur]),1)})),
    9: ("Badruu gives you new fruit, everyone gives you 100g for the seeds", lambda cur,pos,cash,pot: [cash.update({p: cash[p]-100}) or cash.update({cur: cash[cur]+100}) for p in st.session_state.players if p != cur]),
    10: ("Go and help the trufflet at the nearest owned property", lambda cur,pos,cash,pot: pos.update({cur: min((i for i,o in st.session_state.properties.items() if o and BOARD[i][1] in (\"prop\",\"rail\",\"util\")), key=lambda x:(x-pos[cur])%len(BOARD))})),
    11: ("you lost the Gardners runestone, Pay 100g so Einar and Hekla can help make a new one", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]-100})),
    12: ("Reth just started selling beanburgers and flowtato fries, for giving him the idea to star fast food he pays you 200g", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]+200}))
}

# ======================
# INITIALIZE SESSION STATE (safe defaults)
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
            'bankrupt': {},  # mapping player -> bool
            'confirm_bankrupt_for': None  # stores player awaiting confirm
        })

init_game_state()

# ======================
# START GAME UI
# ======================
if not st.session_state.initialized:
    st.subheader("Start Paliopoly Session")
    names = st.text_input("Player names", "Chilled Dude, TJediTim, lilshrtchit.ttv")
    if st.button("Start Game"):
        players = [n.strip() for n in names.split(",") if n.strip()]
        if len(players) < 2:
            st.error("Need 2+ players!")
        else:
            st.session_state.players = players
            st.session_state.cash = {p:1200 for p in players}
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
        if not st.session_state.bankrupt.get(players[idx], False):
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
# MAIN GAME UI & LOGIC
# ======================
if st.session_state.initialized:
    players = st.session_state.get('players', [])
    cur_idx = st.session_state.get('current_idx', 0)
    # ensure cur_idx valid
    if players:
        cur_idx = cur_idx % len(players)
    else:
        cur_idx = 0
    st.session_state.current_idx = cur_idx
    cur = players[cur_idx] if players else None

    cash = st.session_state.get('cash', {})
    pos = st.session_state.get('position', {})
    owner = st.session_state.get('properties', {})
    jail = st.session_state.get('in_jail', {})
    pot = st.session_state.get('free_parking_pot', 0)

    # HEADER: show players list with bankrupt grey-out
    with st.expander("Players and status", expanded=False):
        cols = st.columns(len(players) if players else 1)
        for i,pl in enumerate(players):
            text = f"{pl} — {st.session_state.cash.get(pl,0)}g"
            if st.session_state.bankrupt.get(pl, False):
                cols[i].markdown(f"✅ **{pl}** — BANKRUPT")
            else:
                cols[i].markdown(f"**{pl}** — {st.session_state.cash.get(pl,0)}g")

    # If current player is bankrupt, skip them automatically to next active
    if cur and st.session_state.bankrupt.get(cur, False):
        nxt = next_active_idx(cur_idx)
        if nxt is None:
            # no active players -> game end
            check_game_end()
        else:
            st.session_state.current_idx = nxt
            st.rerun()

    # show main turn header
    if cur:
        col1, col2, col3, col4, col5 = st.columns([2,2,2,2.5,2.5])
        with col1:
            status = "JAILED" if jail.get(cur, False) else ""
            bankrupt_label = " — BANKRUPT" if st.session_state.bankrupt.get(cur, False) else ""
            st.markdown(f"**Turn: {cur}** {status}{bankrupt_label}")
        with col2:
            st.markdown(f"**Gold: {cash.get(cur,0)}g**")
        with col3:
            st.markdown(f"**Pot: {pot}g**")
        with col4:
            if st.session_state.rolled:
                st.success(f"Started on: **{st.session_state.starting_square}**")
            else:
                st.info(f"Starting on: **{BOARD[pos.get(cur,0)][0]}**")
        with col5:
            if st.session_state.rolled:
                if st.button("Next Player", use_container_width=True):
                    nxt = next_active_idx(cur_idx)
                    if nxt is None:
                        check_game_end()
                    else:
                        st.session_state.current_idx = nxt
                        st.session_state.doubles_streak = 0
                        st.session_state.rolled = False
                        st.session_state.landed = None
                        st.session_state.trade_mode = False
                        st.session_state.last_message = ""
                        st.session_state.starting_square = ""
                        st.rerun()
            else:
                st.button("Next Player", disabled=True, use_container_width=True)
                st.caption("Roll first!")

    if st.session_state.last_message:
        st.success(st.session_state.last_message)

    # ======================
    # HELPERS used within turn scope
    # ======================
    def add_cash(player, amt):
        st.session_state.cash[player] = st.session_state.cash.get(player,0) + amt
        if st.session_state.cash[player] < 0:
            st.session_state.cash[player] = 0

    def move_player(player, new_pos):
        st.session_state.position[player] = new_pos

    def apply_chest_effect(roll):
        text, action = CHEST_CARDS.get(roll, ("?? Unknown ??", lambda cur,pos,cash,pot: None))
        action(cur, st.session_state.position, st.session_state.cash, st.session_state.free_parking_pot)
        return text

    def apply_chance_effect(roll):
        text, action = CHANCE_CARDS.get(roll, ("?? Unknown ??", lambda cur,pos,cash,pot: None))
        action(cur, st.session_state.position, st.session_state.cash, st.session_state.free_parking_pot)
        return text

    # ======================
    # ROLL DICE (only if player is not bankrupt)
    # ======================
    if cur and not st.session_state.bankrupt.get(cur, False):
        if not st.session_state.rolled:
            st.info("Enter your **real dice roll**")
            roll = st.number_input("Total rolled", 2, 12, 7, step=1, key="roll_input")
            doubles = st.checkbox("Doubles?", key="dubs_input")
            if st.button("Confirm Roll", type="primary"):
                st.session_state.last_roll = roll
                # doubles logic
                if doubles:
                    st.session_state.doubles_streak += 1
                    if st.session_state.doubles_streak >= 3:
                        move_player(cur, 6)
                        st.session_state.in_jail[cur] = True
                        st.session_state.last_message = "3 DOUBLES → JAIL!"
                        st.rerun()
                else:
                    st.session_state.doubles_streak = 0

                old_pos = st.session_state.position.get(cur, 0)
                new_pos = (old_pos + roll) % len(BOARD)
                move_player(cur, new_pos)
                st.session_state.landed = new_pos
                st.session_state.rolled = True
                crossed_go = new_pos < old_pos or (old_pos + roll >= len(BOARD))
                if crossed_go and new_pos != 0:
                    add_cash(cur, 300)
                    st.balloons()
                space = BOARD[new_pos]
                name, typ = space[0], space[1]
                msg = f"Landed on **{name}**"
                if typ == "tax":
                    tax = space[2]
                    add_cash(cur, -tax)
                    st.session_state.free_parking_pot += tax
                    msg = f"Paid **{tax}g {name}** → added to Free Parking pot!"
                elif typ == "free":
                    if st.session_state.free_parking_pot > 0:
                        add_cash(cur, st.session_state.free_parking_pot)
                        msg = f"FREE PARKING JACKPOT! Collected **{st.session_state.free_parking_pot}g**"
                        st.session_state.free_parking_pot = 0
                        st.balloons()
                    else:
                        msg = "Free Parking — no pot yet!"
                elif typ == "go2jail":
                    move_player(cur, 6)
                    st.session_state.in_jail[cur] = True
                    msg = "GO TO JAIL!"
                elif typ in ("prop", "rail", "util") and owner.get(new_pos) and owner.get(new_pos) != cur:
                    landlord = owner[new_pos]
                    if typ == "prop":
                        rent = space[3]
                    elif typ == "rail":
                        rails_owned = sum(1 for i,o in owner.items() if o == landlord and BOARD[i][1] == "rail")
                        rent = 40 * (2 ** (rails_owned - 1)) if rails_owned >= 1 else 40
                    else:  # util
                        utils_owned = sum(1 for i,o in owner.items() if o == landlord and BOARD[i][1] == "util")
                        rent = roll * (4 if utils_owned == 1 else 10)
                    add_cash(cur, -rent)
                    add_cash(landlord, rent)
                    msg = f"Paid **{landlord}** {rent}g rent on **{name}**!"
                elif typ == "chest":
                    text = apply_chest_effect(roll)
                    msg = f"Chappa Chest → {text}"
                elif typ == "chance":
                    text = apply_chance_effect(roll)
                    msg = f"Chapaa Chance → {text}"

                st.session_state.last_message = msg

                # After landing: if buyable property and unowned create buy prompt (buy handled below)
                st.rerun()

    # ======================
    # BUY PROPERTY (appears after landing when unowned)
    # ======================
    if cur and st.session_state.rolled:
        landed_idx = st.session_state.landed
        if landed_idx is not None:
            landed_square = BOARD[landed_idx]
            if landed_square[1] in ("prop", "rail", "util") and owner.get(landed_idx) is None:
                price = landed_square[2]
                if st.button(f"Buy {landed_square[0]} for {price}g?"):
                    if st.session_state.cash.get(cur,0) >= price:
                        st.session_state.cash[cur] -= price
                        st.session_state.properties[landed_idx] = cur
                        st.session_state.last_message = f"{cur} bought {landed_square[0]}!"
                        st.rerun()
                    else:
                        st.error("Not enough gold!")

    # ======================
    # SELL TO BANK (50%) - only allow current active player (not bankrupt)
    # ======================
    if cur and not st.session_state.bankrupt.get(cur, False):
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
                    # perform sale
                    st.session_state.cash[cur] = st.session_state.cash.get(cur,0) + sell_price
                    st.session_state.properties[idx] = None
                    st.success(f"Sold {prop[0]} for {sell_price}g")
                    st.rerun()
        else:
            st.write("No properties to sell to the bank.")

    # ======================
    # BANKRUPT / QUIT button with confirmation (current player only)
    # ======================
    if cur and not st.session_state.bankrupt.get(cur, False):
        st.markdown("---")
        if st.button("Bankrupt / Quit (return assets to bank)"):
            st.session_state.confirm_bankrupt_for = cur
            st.rerun()
    if st.session_state.get('confirm_bankrupt_for') == cur:
        st.warning(f"Are you sure you want to declare **{cur}** bankrupt? This will return all properties to the bank.")
        coly, coln = st.columns(2)
        if coly.button("Confirm Bankruptcy"):
            # perform bankruptcy: return properties, set cash 0, mark bankrupt True, remove jail card
            for i,o in list(st.session_state.properties.items()):
                if o == cur:
                    st.session_state.properties[i] = None
            st.session_state.cash[cur] = 0
            # if held jail card, return to bank
            if st.session_state.get('jail_free_card') == cur:
                st.session_state.jail_free_card = None
            st.session_state.bankrupt[cur] = True
            st.session_state.confirm_bankrupt_for = None
            st.session_state.last_message = f"**{cur}** declared BANKRUPT — assets returned to bank."
            # advance to next active
            nxt = next_active_idx(cur_idx)
            if nxt is None:
                check_game_end()
            else:
                st.session_state.current_idx = nxt
            st.rerun()
        if coln.button("Cancel"):
            st.session_state.confirm_bankrupt_for = None
            st.rerun()

    # ======================
    # TRADE SYSTEM (disabled for bankrupt players)
    # ======================
    if cur and not st.session_state.bankrupt.get(cur, False):
        if st.button("Trade / Deal" if not st.session_state.trade_mode else "Cancel Trade"):
            st.session_state.trade_mode = not st.session_state.trade_mode
            st.rerun()

        if st.session_state.trade_mode:
            st.subheader("Trade / Deal Maker")
            others = [pl for pl in players if pl != cur and not st.session_state.bankrupt.get(pl, False)]
            if not others:
                st.write("No trading partners available.")
            else:
                partner = st.selectbox("Choose a player to trade with:", others, key="trade_partner")
                st.markdown("---")
                st.markdown("### Your offer")
                offer_gold = st.number_input(f"{cur} gives gold:", min_value=0, max_value=st.session_state.cash.get(cur,0), step=10, key="offer_gold")
                your_props = [i for i,o in owner.items() if o == cur]
                offer_props = st.multiselect("Properties to trade:", your_props, format_func=lambda i: BOARD[i][0], key="offer_props")
                offer_jail_card = (st.session_state.get('jail_free_card') == cur) and st.checkbox("Give Get Out of Jail Free card", key="offer_jail")

                st.markdown("### Partner offer")
                partner_gold = st.number_input(f"{partner} gives gold:", min_value=0, max_value=st.session_state.cash.get(partner,0), step=10, key="partner_gold")
                partner_props = [i for i,o in owner.items() if o == partner]
                partner_offer_props = st.multiselect("Properties to receive:", partner_props, format_func=lambda i: BOARD[i][0], key="partner_props")
                partner_jail_card = (st.session_state.get('jail_free_card') == partner) and st.checkbox("Receive their Get Out of Jail Free card", key="partner_jail")

                if st.button("Confirm Trade", type="primary", key="confirm_trade"):
                    # validate ownership still holds
                    valid = True
                    for i in offer_props:
                        if st.session_state.properties.get(i) != cur:
                            valid = False
                            st.error(f"You no longer own {BOARD[i][0]}")
                    for i in partner_offer_props:
                        if st.session_state.properties.get(i) != partner:
                            valid = False
                            st.error(f"{partner} no longer owns {BOARD[i][0]}")
                    if not valid:
                        st.warning("Trade aborted due to changed ownership.")
                    else:
                        # execute cash transfers
                        st.session_state.cash[cur] -= offer_gold
                        st.session_state.cash[partner] += offer_gold
                        st.session_state.cash[partner] -= partner_gold
                        st.session_state.cash[cur] += partner_gold
                        # transfer properties
                        for i in offer_props: st.session_state.properties[i] = partner
                        for i in partner_offer_props: st.session_state.properties[i] = cur
                        # transfer jail card
                        if offer_jail_card:
                            st.session_state.jail_free_card = partner
                        elif partner_jail_card:
                            st.session_state.jail_free_card = cur
                        st.success("Trade completed.")
                        st.session_state.trade_mode = False
                        st.session_state.last_message = f"Trade completed between **{cur}** and **{partner}**!"
                        st.rerun()

    # ======================
    # NEW GAME
    # ======================
    st.markdown("---")
    if st.button("New Game (Reset Everything)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # check for game end after all actions
    check_game_end()

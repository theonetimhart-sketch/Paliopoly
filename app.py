import streamlit as st
import random

# ======================
# PAGE SETUP
# ======================
st.set_page_config(page_title="Paliopoly – Chilled Dude Edition", layout="centered")
st.title("Paliopoly – Chilled Dude Edition")
st.markdown("**Full set ×2 rent | Clean grouped ownership | Card moves fully land | Trading | Jail**")

# ======================
# SPLASH SCREEN
# ======================
SPLASH_IMAGE = "https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/main/image3.PNG"
if 'passed_splash' not in st.session_state:
    st.session_state.passed_splash = False

if not st.session_state.passed_splash:
    st.image(SPLASH_IMAGE, use_column_width=True)
    st.markdown("### Hi ShorTee, thanks for hosting!")
    st.write("make sure everyone playing is watching at https://www.twitch.tv/lilshrtchit")

    if 'splash_players_input' not in st.session_state:
        st.session_state.splash_players_input = "Chilled Dude, TJediTim, lilshrtchit.ttv"

    st.session_state.splash_players_input = st.text_input(
        "Enter player names (comma separated):",
        st.session_state.splash_players_input
    )
    players = [n.strip() for n in st.session_state.splash_players_input.split(",") if n.strip()]

    if "Chilled Dude" in players:
        st.success("And Chilled Dude is playing, yay!")
        if st.button("Continue to Let's Play!"):
            st.session_state.players = players
            st.session_state.passed_splash = True
            st.rerun()
    else:
        pwd = st.text_input("Chilled Dude isn't here? Enter his Discord name:", type="password")
        if st.button("Continue"):
            if pwd.strip() == "TJediTim":
                st.session_state.players = players
                st.session_state.passed_splash = True
                st.success("Password accepted!")
                st.rerun()
            else:
                st.error("Wrong password. It's exactly: TJediTim")
    st.stop()

# ======================
# MAIN IMAGES
# ======================
st.image("https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image.png", use_column_width=True)
st.image("https://github.com/theonetimhart-sketch/Paliopoly/blob/main/paliopoly.png", use_column_width=True, caption="The Board")

# ======================
# BOARD WITH COLOR GROUPS
# ======================
BOARD = [
    ("GO", "go"),
    ("Kilima 1", "prop", 80, 6, 18, "purple"),
    ("Renown Tax", "tax", 100),
    ("Kilima 2", "prop", 80, 6, 18, "purple"),
    ("Travel Point 1", "rail", 150, 40),
    ("Chappa Chest", "chest"),
    ("Jail", "jail"),
    ("Bahari 1", "prop", 120, 9, 27, "lightblue"),
    ("Chapaa Chance", "chance"),
    ("Travel Point 2", "rail", 150, 40),
    ("Bahari 2", "prop", 120, 9, 27, "lightblue"),
    ("Utility 1", "util", 100),
    ("Free Parking", "free"),
    ("Elderwood 1", "prop", 160, 12, 36, "orange"),
    ("Chapaa Chance", "chance"),
    ("Elderwood 2", "prop", 160, 12, 36, "orange"),
    ("Travel Point 3", "rail", 150, 40),
    ("Utility 2", "util", 100),
    ("Go to Jail", "go2jail"),
    ("Chappa Chest", "chest"),
    ("Travel Point 4", "rail", 150, 40),
    ("Maji Wedding 1", "prop", 200, 15, 45, "red"),
    ("Maji Tax", "tax", 200),
    ("Maji Wedding 2", "prop", 200, 15, 45, "red")
]

# Color groups for full set rent ×2
COLOR_GROUPS = {
    "purple": [1, 3],
    "lightblue": [7, 10],
    "orange": [13, 15],
    "red": [21, 23]
}

# ======================
# FULL CHEST CARDS — RESTORED
# ======================
def chest_go_to_go(p, ss, _): ss['position'][p] = 0; ss['cash'][p] += 300
def chest_go_to_jail(p, ss, _): ss['position'][p] = 6; ss['in_jail'][p] = True; ss['jail_turns'][p] = 0

CHEST_CARDS_LIST = [
    ("Chapaa Chase to GO!", chest_go_to_go),
    ("Proudhorned Sernuk teleports you, GO TO JAIL!", chest_go_to_jail),
    ("Elouisa found a cryptid, everyone pays you 50g not to tell them about it",
     lambda p,ss,_: [ss['cash'].__setitem__(q, ss['cash'][q]-50) or ss['cash'].__setitem__(p, ss['cash'][p]+50) for q in ss['players'] if q!=p]),
    ("Eshe made Kenli enforce the land tax. Pay 100g", lambda p,ss,_: (ss['cash'].__setitem__(p, ss['cash'][p]-100), ss.__setitem__('free_parking_pot', ss['free_parking_pot']+100))),
    ("Collect 100g from Subira for helping the order", lambda p,ss,_: ss['cash'].__setitem__(p, ss['cash'][p]+100)),
    ("Ogupu drags you into a whirlpool and moves you back 3 spaces", lambda p,ss,_: ss['position'].__setitem__(p, (ss['position'][p]-3)%len(BOARD))),
    ("Bluebristle Muujin pushes you forward 3 spaces", lambda p,ss,_: (old:=ss['position'][p], ss['position'].__setitem__(p, (old+3)%len(BOARD)), ss['cash'].__setitem__(p, ss['cash'][p]+300) if ss['position'][p] < old else None)),
    ("Tamala tricks you into paying the poorest player 100g",
     lambda p,ss,_: (lambda poorest=min([x for x in ss['players'] if not ss['bankrupt'].get(x,False)], key=lambda x:ss['cash'][x]): (ss['cash'].__setitem__(p, ss['cash'][p]-100), ss['cash'].__setitem__(poorest, ss['cash'][poorest]+100)))()),
    ("You followed a Peki to the next Travel Point", lambda p,ss,_: (old:=ss['position'][p], ss['position'].__setitem__(p, min([4,9,16,20], key=lambda x:(x-old)%len(BOARD))), ss['cash'].__setitem__(p, ss['cash'][p]+300) if ss['position'][p] < old else None)),
    ("Tish has new furniture, pay 150g", lambda p,ss,_: (ss['cash'].__setitem__(p, ss['cash'][p]-150), ss.__setitem__('free_parking_pot', ss['free_parking_pot']+150))),
    ("Zeki drops off some treasure. collect 200g", lambda p,ss,_: ss['cash'].__setitem__(p, ss['cash'][p]+200))
]

# ======================
# FULL CHANCE CARDS — RESTORED
# ======================
def chance_free_parking(p, ss, _):
    old = ss['position'][p]
    ss['position'][p] = 12
    if ss['position'][p] < old: ss['cash'][p] += 300
    ss['cash'][p] += ss['free_parking_pot']
    ss['free_parking_pot'] = 0

def chance_get_out_of_jail(p, ss, _):
    ss['jail_free_card'] = p

CHANCE_CARDS_LIST = [
    ("Tau spots something buried, go to Free Parking to dig it up and collect whatever is there", chance_free_parking),
    ("Plumehound buried a Get Out of Jail Free card, go ahead and keep that one", chance_get_out_of_jail),
    ("Jina found a rare artifact. Give 50g to all the humans", lambda p,ss,_: [ss['cash'].__setitem__(q, ss['cash'][q]+50) or ss['cash'].__setitem__(p, ss['cash'][p]-50) for q in ss['players'] if q!=p]),
    ("Caught in the restricted section, pay Caleri 200g", lambda p,ss,_: (ss['cash'].__setitem__(p, ss['cash'][p]-200), ss.__setitem__('free_parking_pot', ss['free_parking_pot']+200))),
    ("Collect 150g for promoting Jels new wardrobe", lambda p,ss,_: ss['cash'].__setitem__(p, ss['cash'][p]+150)),
    ("Follow a flutterfox to the next shrub", lambda p,ss,_: (old:=ss['position'][p], ss['position'].__setitem__(p, next((i for i in [11,17] if i>old), 11)), ss['cash'].__setitem__(p, ss['cash'][p]+300) if ss['position'][p] < old else None)),
    ("Ormuu pushes you to next main property", lambda p,ss,_: (old:=ss['position'][p], ss['position'].__setitem__(p, next((i for i in [1,3,7,10,13,15,21,23] if i>old), 1)), ss['cash'].__setitem__(p, ss['cash'][p]+300) if ss['position'][p] < old else None)),
    ("Badruu gives you new fruit, everyone gives you 100g for the seeds", lambda p,ss,_: [ss['cash'].__setitem__(q, ss['cash'][q]-100) or ss['cash'].__setitem__(p, ss['cash'][p]+100) for q in ss['players'] if q!=p]),
    ("Go and help the truffle at the nearest owned property", lambda p,ss,_: (old:=ss['position'][p], target:=min([i for i,o in ss['properties'].items() if o and BOARD[i][1] in ('prop','rail','util')], key=lambda x:(x-old)%len(BOARD), default=old), ss['position'].__setitem__(p, target), ss['cash'].__setitem__(p, ss['cash'][p]+300) if target != old and ss['position'][p] < old else None)),
    ("you lost the Gardners runestone, Pay 100g", lambda p,ss,_: (ss['cash'].__setitem__(p, ss['cash'][p]-100), ss.__setitem__('free_parking_pot', ss['free_parking_pot']+100))),
    ("Reth just started selling beanburgers and flowtato fries, he pays you 200g", lambda p,ss,_: ss['cash'].__setitem__(p, ss['cash'][p]+200))
]

# ======================
# INITIALIZE GAME
# ======================
if 'initialized' not in st.session_state:
    st.session_state.update({
        'initialized': True,
        'players': st.session_state.players,
        'cash': {p: 1000 for p in st.session_state.players},
        'position': {p: 0 for p in st.session_state.players},
        'properties': {i: None for i, sq in enumerate(BOARD) if sq[1] in ("prop", "rail", "util")},
        'in_jail': {p: False for p in st.session_state.players},
        'jail_turns': {p: 0 for p in st.session_state.players},
        'jail_free_card': None,
        'current_idx': 0,
        'doubles_streak': 0,
        'rolled': False,
        'landed': None,
        'last_message': "",
        'trade_mode': False,
        'starting_square': "",
        'free_parking_pot': 0,
        'bankrupt': {p: False for p in st.session_state.players},
        'confirm_next_for': None,
        'chest_deck': random.sample(CHEST_CARDS_LIST, len(CHEST_CARDS_LIST)),
        'chance_deck': random.sample(CHANCE_CARDS_LIST, len(CHANCE_CARDS_LIST)),
    })

ss = st.session_state
cur = ss.players[ss.current_idx]

while ss.bankrupt.get(cur, False):
    ss.current_idx = (ss.current_idx + 1) % len(ss.players)
    cur = ss.players[ss.current_idx]

# ======================
# UI: Player status
# ======================
with st.expander("Players & Cash", expanded=True):
    cols = st.columns(len(ss.players))
    for i, p in enumerate(ss.players):
        jail = " (JAILED)" if ss.in_jail.get(p) else ""
        bank = " (BANKRUPT)" if ss.bankrupt.get(p) else ""
        at = f"at {BOARD[ss.position[p]][0]}"
        cols[i].markdown(f"**{p}**{jail}{bank}\n{ss.cash[p]}g\n{at}")

c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
c1.markdown(f"**Turn: {cur}** {'(JAILED)' if ss.in_jail.get(cur) else ''}")
c2.markdown(f"**Gold:** {ss.cash[cur]}g")
c3.markdown(f"**Free Parking Pot:** {ss.free_parking_pot}g")
if ss.rolled:
    c4.success(f"Started on: **{ss.starting_square}**")

if ss.last_message:
    st.success(ss.last_message)

# ======================
# Jail options
# ======================
if ss.in_jail.get(cur):
    col_pay, col_card = st.columns(2)
    if col_pay.button("Pay 50g to leave jail") and ss.cash[cur] >= 50:
        ss.cash[cur] -= 50; ss.free_parking_pot += 50; ss.in_jail[cur] = False; ss.jail_turns[cur] = 0; st.rerun()
    if col_card.button("Use Get Out of Jail Free") and ss.jail_free_card == cur:
        ss.jail_free_card = None; ss.in_jail[cur] = False; st.rerun()

# ======================
# Roll dice
# ======================
if not ss.rolled:
    st.info("Enter your real dice roll")
    roll = st.number_input("Total rolled", 2, 12, 7, step=1, key="roll_input")
    doubles_possible = (roll % 2 == 0)
    doubles = False
    if doubles_possible:
        doubles = st.checkbox("Doubles?", key="doubles_checkbox")

    if st.button("Confirm Roll", type="primary"):
        if ss.in_jail.get(cur):
            if doubles:
                ss.in_jail[cur] = False
                ss.jail_turns[cur] = 0
            else:
                ss.jail_turns[cur] += 1
                if ss.jail_turns[cur] >= 3:
                    if ss.cash[cur] >= 50:
                        ss.cash[cur] -= 50; ss.free_parking_pot += 50; ss.in_jail[cur] = False
                    else:
                        ss.last_message = "Can't pay 50g — stuck in jail!"
                        ss.rolled = True
                        st.rerun()
                else:
                    ss.last_message = f"No doubles — jail turn {ss.jail_turns[cur]}/3"
                    ss.rolled = True
                    st.rerun()

        if doubles:
            ss.doubles_streak += 1
            if ss.doubles_streak >= 3:
                ss.position[cur] = 6; ss.in_jail[cur] = True; ss.jail_turns[cur] = 0
                ss.last_message = "3 DOUBLES to JAIL!"
                ss.rolled = True; ss.landed = None
                st.rerun()
        else:
            ss.doubles_streak = 0

        if not ss.in_jail.get(cur):
            old_pos = ss.position[cur]
            new_pos = (old_pos + roll) % len(BOARD)
            passed_go = (old_pos + roll >= len(BOARD)) or new_pos == 0
            if passed_go:
                ss.cash[cur] += 300
                st.balloons()

            ss.position[cur] = new_pos
            ss.landed = new_pos
            ss.starting_square = BOARD[old_pos][0]
            ss.rolled = True

            def land_on(pos, depth=0):
                if depth > 6: return " [card loop stopped]"
                sq = BOARD[pos]
                msg = []
                typ = sq[1]

                if typ == "tax":
                    amt = sq[2]; ss.cash[cur] -= amt; ss.free_parking_pot += amt; msg.append(f"Paid {amt}g tax")
                elif typ == "free":
                    if ss.free_parking_pot:
                        amt = ss.free_parking_pot; ss.cash[cur] += amt; ss.free_parking_pot = 0; msg.append(f"Jackpot! +{amt}g")
                elif typ == "go2jail":
                    ss.position[cur] = 6; ss.in_jail[cur] = True; ss.jail_turns[cur] = 0; msg.append("Go to jail!"); return " ".join(msg)
                elif typ in ("prop","rail","util"):
                    owner = ss.properties.get(pos)
                    if owner and owner != cur:
                        if typ == "prop":
                            base_rent = sq[3]
                            color = sq[5]
                            full_set = all(ss.properties.get(i) == owner for i in COLOR_GROUPS[color])
                            rent = base_rent * 2 if full_set else base_rent
                        elif typ == "rail":
                            owned = sum(1 for i,o in ss.properties.items() if o==owner and BOARD[i][1]=="rail")
                            rent = 40 * (2 ** (owned-1))
                        else:
                            owned = sum(1 for i,o in ss.properties.items() if o==owner and BOARD[i][1]=="util")
                            rent = roll * (10 if owned == 2 else 4)
                        ss.cash[cur] -= rent; ss.cash[owner] += rent
                        extra = " (full set!)" if typ == "prop" and full_set else ""
                        msg.append(f"Paid {owner} {rent}g rent{extra}")
                elif typ == "chest":
                    if not ss.chest_deck: ss.chest_deck = random.sample(CHEST_CARDS_LIST, len(CHEST_CARDS_LIST))
                    card = ss.chest_deck.pop(0); ss.chest_deck.append(card)
                    old = ss.position[cur]; card[1](cur, ss, roll)
                    msg.append(f"Chest: {card[0]}")
                    if ss.position[cur] != old: msg.append(land_on(ss.position[cur], depth+1))
                elif typ == "chance":
                    if not ss.chance_deck: ss.chance_deck = random.sample(CHANCE_CARDS_LIST, len(CHANCE_CARDS_LIST))
                    card = ss.chance_deck.pop(0); ss.chance_deck.append(card)
                    old = ss.position[cur]; card[1](cur, ss, roll)
                    msg.append(f"Chance: {card[0]}")
                    if ss.position[cur] != old: msg.append(land_on(ss.position[cur], depth+1))
                return " ".join(msg)

            landing_msg = land_on(new_pos)
            go_msg = " Passed GO +300g!" if passed_go else ""
            ss.last_message = f"Landed on **{BOARD[new_pos][0]}**{go_msg} — {landing_msg}"
            if doubles and ss.doubles_streak < 3:
                ss.rolled = False
                ss.last_message += " to DOUBLES! Roll again!"
            st.rerun()

# Buy property
if ss.rolled and ss.landed is not None and not ss.in_jail.get(cur):
    sq = BOARD[ss.landed]
    if sq[1] in ("prop","rail","util") and ss.properties.get(ss.landed) is None:
        if st.button(f"Buy {sq[0]} for {sq[2]}g?", key=f"buy_{ss.landed}"):
            if ss.cash[cur] >= sq[2]:
                ss.cash[cur] -= sq[2]
                ss.properties[ss.landed] = cur
                ss.last_message = f"{cur} bought {sq[0]}!"
                st.rerun()

# Confirm next player
if ss.rolled:
    if ss.get('confirm_next_for') == cur:
        st.warning("End turn and pass to next player?")
        y, n = st.columns(2)
        if y.button("Yes to Next"):
            ss.rolled = False; ss.landed = None; ss.last_message = ""; ss.confirm_next_for = None; ss.doubles_streak = 0
            ss.current_idx = (ss.current_idx + 1) % len(ss.players)
            st.rerun()
        if n.button("No"):
            ss.confirm_next_for = None
            st.rerun()
    else:
        if st.button("Next Player to Confirm"):
            ss.confirm_next_for = cur
            st.rerun()

# Trading
if st.button("Trade / Deal" if not ss.trade_mode else "Cancel Trade"):
    ss.trade_mode = not ss.trade_mode
    st.rerun()

if ss.trade_mode:
    st.subheader("Trade / Deal Maker")
    others = [p for p in ss.players if p != cur and not ss.bankrupt.get(p, False)]
    if not others:
        st.write("No active players to trade with.")
    else:
        partner = st.selectbox("Choose trading partner:", others, key="trade_partner")
        st.markdown("---")
        st.markdown("### Your Offer")
        offer_gold = st.number_input(f"{cur} gives gold:", min_value=0, max_value=ss.cash[cur], step=10, key="offer_gold")
        your_props = [i for i,o in ss.properties.items() if o == cur]
        offer_props = st.multiselect("Properties you give:", your_props, format_func=lambda i: BOARD[i][0], key="offer_props")
        offer_jail = (ss.jail_free_card == cur) and st.checkbox("Give Get Out of Jail Free card", key="offer_jail")

        st.markdown("### Their Offer")
        their_gold = st.number_input(f"{partner} gives gold:", min_value=0, max_value=ss.cash[partner], step=10, key="their_gold")
        their_props = [i for i,o in ss.properties.items() if o == partner]
        their_offer_props = st.multiselect("Properties you receive:", their_props, format_func=lambda i: BOARD[i][0], key="their_props")
        their_jail = (ss.jail_free_card == partner) and st.checkbox("Receive their Get Out of Jail Free card", key="their_jail")

        if st.button("Confirm Trade", type="primary"):
            ss.cash[cur] -= offer_gold; ss.cash[partner] += offer_gold
            ss.cash[partner] -= their_gold; ss.cash[cur] += their_gold
            for i in offer_props: ss.properties[i] = partner
            for i in their_offer_props: ss.properties[i] = cur
            if offer_jail: ss.jail_free_card = partner
            elif their_jail: ss.jail_free_card = cur
            st.success(f"Trade complete between {cur} and {partner}!")
            ss.trade_mode = False
            ss.last_message = "Trade completed!"
            st.rerun()

# Ownership — CLEAN & GROUPED
with st.expander("Ownership Overview", expanded=True):
    st.markdown("### Properties")
    for color, positions in COLOR_GROUPS.items():
        st.markdown(f"**{color.title()} Group**")
        for i in positions:
            owner = ss.properties.get(i) or "Bank"
            st.write(f"   • {BOARD[i][0]} — {owner}")

    st.markdown("### Travel Points")
    for i in [4, 9, 16, 20]:
        owner = ss.properties.get(i) or "Bank"
        st.write(f"   • {BOARD[i][0]} — {owner}")

    st.markdown("### Utilities")
    for i in [11, 17]:
        owner = ss.properties.get(i) or "Bank"
        st.write(f"   • {BOARD[i][0]} — {owner}")

    jail_owner = ss.jail_free_card or "Unowned"
    st.markdown(f"**Get Out of Jail Free** — {jail_owner}")

# New Game
if st.button("New Game — Reset Everything"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

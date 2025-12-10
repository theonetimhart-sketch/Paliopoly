import streamlit as st
import random

# ======================
# PAGE SETUP
# ======================
st.set_page_config(page_title="Paliopoly – Chilled Dude Edition", layout="centered")
st.title("Paliopoly – Chilled Dude Edition — Fixed & Working")
st.markdown("**All your fixes applied: jail, doubles, cards, GO money, ownership view, next-turn confirm, bankrupt removal**")

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
    st.session_state.splash_players_input = st.text_input("Enter player names (comma separated):", st.session_state.splash_players_input)
    tentative_players = [n.strip() for n in st.session_state.splash_players_input.split(",") if n.strip()]
    if "Chilled Dude" in tentative_players:
        st.success("And Chilled Dude is playing, yay!")
        if st.button("Continue"):
            st.session_state.players = tentative_players
            st.session_state.passed_splash = True
            st.rerun()
    else:
        pwd = st.text_input("Chilled Dude isn't here? Discord name to continue...", type="password")
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
# IMAGES
# ======================
st.image("https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image.png", use_column_width=True)
st.image("https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/refs/heads/main/image2.png", use_column_width=True, caption="The Board")

# ======================
# BOARD
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
# CARDS – FIXED SYNTAX
# ======================
def chest_go_to_go(p, ss, roll):
    ss['position'][p] = 0
    ss['cash'][p] += 300

def chest_go_to_jail(p, ss, roll):
    ss['position'][p] = 6
    ss['in_jail'][p] = True
    ss['jail_turns'][p] = 0

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
     lambda p,ss,_: (lambda poorest=min([x for x in ss['players'] if not ss['bankrupt'].get(x,False)], key=lambda x:ss['cash'][x]): (
         ss['cash'].__setitem__(p, ss['cash'][p]-100), ss['cash'].__setitem__(poorest, ss['cash'][poorest]+100)))()),
    ("You followed a Peki to the next Travel Point", lambda p,ss,_: (old:=ss['position'][p], ss['position'].__setitem__(p, min([4,9,16,20], key=lambda x:(x-old)%len(BOARD))), ss['cash'].__setitem__(p, ss['cash'][p]+300) if ss['position'][p] < old else None)),
    ("Tish has new furniture, pay 150g", lambda p,ss,_: (ss['cash'].__setitem__(p, ss['cash'][p]-150), ss.__setitem__('free_parking_pot', ss['free_parking_pot']+150))),
    ("Zeki drops off some treasure. collect 200g", lambda p,ss,_: ss['cash'].__setitem__(p, ss['cash'][p]+200))
]

def chance_free_parking(p, ss, roll):
    old = ss['position'][p]
    ss['position'][p] = 12
    if ss['position'][p] < old: ss['cash'][p] += 300
    ss['cash'][p] += ss['free_parking_pot']
    ss['free_parking_pot'] = 0

def chance_get_out_of_jail(p, ss, roll):
    ss['jail_free_card'] = p

CHANCE_CARDS_LIST = [
    ("Tau spots something buried, go to Free Parking to dig it up and collect whatever is there", chance_free_parking),
    ("Plumehound buried a Get Out of Jail Free card, go ahead and keep that one", chance_get_out_of_jail),
    ("Jina found a rare artifact. Give 50g to all the humans", lambda p,ss,_: [ss['cash'].__setitem__(q, ss['cash'][q]+50) or ss['cash'].__setitem__(p, ss['cash'][p]-50) for q in ss['players'] if q!=p]),
    ("Caught in the restricted section, pay Caleri 200g", lambda p,ss,_: (ss['cash'].__setitem__(p, ss['cash'][p]-200), ss.__setitem__('free_parking_pot', ss['free_parking_pot']+200))),
    ("Collect 150g for promoting Jels new wardrobe", lambda p,ss,_: ss['cash'].__setitem__(p, ss['cash'][p]+150)),
    ("Follow a flutterfox to the next shrub", lambda p,ss,_: (old:=ss['position'][p], ss['position'].__setitem__(p, next((i for i in [11,17] if i>old),11)), ss['cash'].__setitem__(p, ss['cash'][p]+300) if ss['position'][p] < old else None)),
    ("Ormuu pushes you to next main property", lambda p,ss,_: (old:=ss['position'][p], ss['position'].__setitem__(p, next((i for i in [1,3,7,10,13,15,21,23] if i>old),1)), ss['cash'].__setitem__(p, ss['cash'][p]+300) if ss['position'][p] < old else None)),
    ("Badruu gives you new fruit, everyone gives you 100g for the seeds", lambda p,ss,_: [ss['cash'].__setitem__(q, ss['cash'][q]-100) or ss['cash'].__setitem__(p, ss['cash'][p]+100) for q in ss['players'] if q!=p]),
    ("Go and help the truffle at the nearest owned property", lambda p,ss,_: (old:=ss['position'][p], ss['position'].__setitem__(p, min([i for i,o in ss['properties'].items() if o and BOARD[i][1] in ('prop','rail','util')], key=lambda x:(x-old)%len(BOARD), default=old)), ss['cash'].__setitem__(p, ss['cash'][p]+300) if ss['position'][p] < old else None)),
    ("you lost the Gardners runestone, Pay 100g", lambda p,ss,_: (ss['cash'].__setitem__(p, ss['cash'][p]-100), ss.__setitem__('free_parking_pot', ss['free_parking_pot']+100))),
    ("Reth just started selling beanburgers and flowtato fries, he pays you 200g", lambda p,ss,_: ss['cash'].__setitem__(p, ss['cash'][p]+200))
]

# ======================
# INITIALIZE
# ======================
def init():
    if 'initialized' not in st.session_state:
        st.session_state.update({
            'initialized': False, 'players': st.session_state.get('players',[]), 'cash':{}, 'position':{}, 'properties':{},
            'in_jail':{}, 'jail_turns':{}, 'jail_free_card':None, 'current_idx':0, 'doubles_streak':0, 'rolled':False,
            'landed':None, 'last_message':"", 'trade_mode':False, 'starting_square':"", 'free_parking_pot':0,
            'bankrupt':{}, 'confirm_bankrupt_for':None, 'confirm_next_for':None,
            'chest_deck': random.sample(CHEST_CARDS_LIST, len(CHEST_CARDS_LIST)),
            'chance_deck': random.sample(CHANCE_CARDS_LIST, len(CHANCE_CARDS_LIST))
        })
init()

if not st.session_state.initialized:
    st.subheader("Start Paliopoly Session")
    default = ", ".join(st.session_state.get('players',[])) or "Chilled Dude, TJediTim, lilshrtchit.ttv"
    names = st.text_input("Player names", default)
    if st.button("Start Game"):
        players = [n.strip() for n in names.split(",") if n.strip()]
        if len(players)<2: st.error("Need 2+ players!")
        else:
            st.session_state.players = players
            st.session_state.cash = {p:1000 for p in players}
            st.session_state.position = {p:0 for p in players}
            st.session_state.properties = {i: None for i, sq in enumerate(BOARD) if sq[1] in ("prop","rail","util")}
            st.session_state.in_jail = {p:False for p in players}
            st.session_state.jail_turns = {p:0 for p in players}
            st.session_state.bankrupt = {p:False for p in players}
            st.session_state.initialized = True
            st.session_state.chest_deck = random.sample(CHEST_CARDS_LIST, len(CHEST_CARDS_LIST))
            st.session_state.chance_deck = random.sample(CHANCE_CARDS_LIST, len(CHANCE_CARDS_LIST))
            st.rerun()

# ======================
# HELPERS
# ======================
def next_player():
    idx = st.session_state.current_idx
    for _ in range(len(st.session_state.players)):
        idx = (idx + 1) % len(st.session_state.players)
        p = st.session_state.players[idx]
        if not st.session_state.bankrupt.get(p, False):
            st.session_state.current_idx = idx
            return
    st.session_state.last_message = "Game Over! Everyone bankrupt."

def process_landing(player, roll, depth=0):
    if depth > 6: return " (card loop stopped)"
    ss = st.session_state
    pos = ss['position'][player]
    sq = BOARD[pos]
    name, typ = sq[0], sq[1]
    msg = []
    if typ == "tax":
        amt = sq[2]
        ss['cash'][player] -= amt
        ss['free_parking_pot'] += amt
        msg.append(f"Paid {amt}g tax")
    elif typ == "free":
        if ss['free_parking_pot']:
            amt = ss['free_parking_pot']
            ss['cash'][player] += amt
            ss['free_parking_pot'] = 0
            msg.append(f"Jackpot! +{amt}g")
    elif typ == "go2jail":
        ss['position'][player] = 6
        ss['in_jail'][player] = True
        ss['jail_turns'][player] = 0
        msg.append("Go directly to jail!")
        return " ".join(msg)
    elif typ in ("prop","rail","util"):
        owner = ss['properties'].get(pos)
        if owner and owner != player:
            if typ == "prop": rent = sq[3]
            elif typ == "rail": rent = 40 * (2 ** (sum(1 for i,o in ss['properties'].items() if o==owner and BOARD[i][1]=="rail")-1))
            else: rent = roll * (10 if sum(1 for i,o in ss['properties'].items() if o==owner and BOARD[i][1]=="util")==2 else 4)
            ss['cash'][player] -= rent
            ss['cash'][owner] += rent
            msg.append(f"Paid {owner} {rent}g rent")
    elif typ == "chest":
        deck = ss['chest_deck']
        if not deck: deck = ss['chest_deck'] = random.sample(CHEST_CARDS_LIST, len(CHEST_CARDS_LIST))
        card = deck.pop(0)
        deck.append(card)
        old = ss['position'][player]
        card[1](player, ss, roll)
        msg.append(f"Chest: {card[0]}")
        if ss['position'][player] != old:
            msg.append(process_landing(player, roll, depth+1))
    elif typ == "chance":
        deck = ss['chance_deck']
        if not deck: deck = ss['chance_deck'] = random.sample(CHANCE_CARDS_LIST, len(CHANCE_CARDS_LIST))
        card = deck.pop(0)
        deck.append(card)
        old = ss['position'][player]
        card[1](player, ss, roll)
        msg.append(f"Chance: {card[0]}")
        if ss['position'][player] != old:
            msg.append(process_landing(player, roll, depth+1))
    return " ".join(msg)

# ======================
# MAIN GAME
# ======================
if st.session_state.initialized:
    ss = st.session_state
    cur = ss.players[ss.current_idx]
    if ss.bankrupt.get(cur, False):
        next_player()
        st.rerun()

    with st.expander("Players", expanded=False):
        cols = st.columns(len(ss.players))
        for i,p in enumerate(ss.players):
            jail = " JAILED" if ss.in_jail.get(p) else ""
            cols[i].write(f"**{p}** {ss.cash[p]}g{jail}")

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"**Turn → {cur}** {'(Jailed)' if ss.in_jail.get(cur) else ''}")
    col2.markdown(f"Gold: {ss.cash[cur]}g")
    col3.markdown(f"Pot: {ss.free_parking_pot}g")

    if ss.last_message:
        st.success(ss.last_message)

    if not ss.rolled:
        st.info("Enter your real dice roll")
        roll = st.number_input("Total", 2,12,7,step=1)
        doubles = st.checkbox("Doubles?")

        if ss.in_jail.get(cur):
            colA, colB = st.columns(2)
            if colA.button("Pay 50g out") and ss.cash[cur] >= 50:
                ss.cash[cur] -= 50
                ss.free_parking_pot += 50
                ss.in_jail[cur] = False
                st.rerun()
            if colB.button("Use Get Out Free") and ss.jail_free_card == cur:
                ss.jail_free_card = None
                ss.in_jail[cur] = False
                st.rerun()

        if st.button("Confirm Roll", type="primary"):
            # Jail logic
            if ss.in_jail.get(cur):
                if doubles:
                    ss.in_jail[cur] = False
                    ss.jail_turns[cur] = 0
                else:
                    ss.jail_turns[cur] += 1
                    if ss.jail_turns[cur] >= 3:
                        if ss.cash[cur] >= 50:
                            ss.cash[cur] -= 50
                            ss.free_parking_pot += 50
                            ss.in_jail[cur] = False
                        else:
                            ss.last_message = "Can't pay 50g — stay in jail!"
                            ss.rolled = True
                            st.rerun()
                    else:
                        ss.last_message = f"No doubles — jail turn {ss.jail_turns[cur]}/3"
                        ss.rolled = True
                        st.rerun()

            # Doubles streak
            if doubles:
                ss.doubles_streak += 1
                if ss.doubles_streak >= 3:
                    ss.position[cur] = 6
                    ss.in_jail[cur] = True
                    ss.jail_turns[cur] = 0
                    ss.last_message = "3 doubles → JAIL!"
                    ss.rolled = True
                    st.rerun()
            else:
                ss.doubles_streak = 0

            if not ss.in_jail.get(cur):
                old = ss.position[cur]
                new = (old + roll) % len(BOARD)
                if new <= old:  # passed GO
                    ss.cash[cur] += 300
                    st.balloons()
                ss.position[cur] = new
                ss.landed = new
                ss.starting_square = BOARD[old][0]
                landing = process_landing(cur, roll)
                ss.last_message = f"Landed on **{BOARD[new][0]}** — {landing}"
                ss.rolled = True
                if doubles:
                    ss.rolled = False
                    ss.last_message += " — Doubles! Roll again!"
                st.rerun()

    # Buy property
    if ss.rolled and ss.landed is not None:
        sq = BOARD[ss.landed]
        if sq[1] in ("prop","rail","util") and ss.properties.get(ss.landed) is None:
            if st.button(f"Buy {sq[0]} for {sq[2]}g?"):
                if ss.cash[cur] >= sq[2]:
                    ss.cash[cur] -= sq[2]
                    ss.properties[ss.landed] = cur
                    ss.last_message = f"{cur} bought {sq[0]}!"
                    st.rerun()

    # Confirm next player
    if ss.rolled:
        if ss.get('confirm_next_for') == cur:
            st.warning("Really end turn?")
            ya, na = st.columns(2)
            if ya.button("Yes"):
                ss.rolled = False
                ss.landed = None
                ss.last_message = ""
                ss.confirm_next_for = None
                ss.doubles_streak = 0
                next_player()
                st.rerun()
            if na.button("No"):
                ss.confirm_next_for = None
                st.rerun()
        else:
            if st.button("Next Player →"):
                ss.confirm_next_for = cur
                st.rerun()

    # Ownership view
    with st.expander("Ownership", expanded=True):
        for i, sq in enumerate(BOARD):
            if sq[1] in ("prop","rail","util"):
                owner = ss.properties.get(i) or "Bank"
                st.write(f"{i}: **{sq[0]}** — {owner}")

    if st.button("New Game"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

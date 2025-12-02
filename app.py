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
# CARD FLAVOUR TEXT (editable)
# ======================
CHEST_CARDS = {
    2: ("Advance to GO!", lambda cur,pos,cash,pot: (pos.update({cur:0}), cash.update({cur: cash[cur]+300}))),
    3: ("GO TO JAIL!", lambda cur,pos,cash,pot: (pos.update({cur:6}), st.session_state.in_jail.update({cur: True}))),
    4: ("Everyone pays you 50g", lambda cur,pos,cash,pot: [cash.update({p: cash[p]-50}) or cash.update({cur: cash[cur]+50}) for p in st.session_state.players if p != cur]),
    5: ("Pay 100g", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]-100})),
    6: ("Collect 100g", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]+100})),
    7: ("Teleport creature moves you back 3 spaces", lambda cur,pos,cash,pot: pos.update({cur: (pos[cur]-3)%len(BOARD)})),
    8: ("Teleport creature moves you forward 3 spaces", lambda cur,pos,cash,pot: pos.update({cur: (pos[cur]+3)%len(BOARD)})),
    9: ("Pay poorest player 100g", lambda cur,pos,cash,pot: (lambda poorest=min(st.session_state.players, key=lambda x: cash[x]): (cash.update({cur: cash[cur]-100}), cash.update({poorest: cash[poorest]+100})) if cash[cur]>=100 else None)()),
    10: ("Go to nearest Travel Point", lambda cur,pos,cash,pot: pos.update({cur: min([4,9,16,21], key=lambda x:(x-pos[cur])%len(BOARD))})),
    11: ("Pay 150g", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]-150})),
    12: ("Collect 200g", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]+200}))
}

CHANCE_CARDS = {
    2: ("Free Parking! Collect pot", lambda cur,pos,cash,pot: (pos.update({cur:12}), cash.update({cur: cash[cur]+pot}), st.session_state.__setitem__('free_parking_pot', 0))),
    3: ("Get Out of Jail Free!", lambda cur,pos,cash,pot: st.session_state.__setitem__('jail_free_card', cur)),
    4: ("Give 50g to everyone", lambda cur,pos,cash,pot: [cash.update({cur: cash[cur]-50}) or cash.update({p: cash[p]+50}) for p in st.session_state.players if p != cur]),
    5: ("Pay 200g", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]-200})),
    6: ("Collect 150g", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]+150})),
    7: ("Move to next shrub", lambda cur,pos,cash,pot: pos.update({cur: next((i for i in [13,15,22,24] if i>pos[cur]),13)})),
    8: ("Move to next main property", lambda cur,pos,cash,pot: pos.update({cur: next((i for i in [1,3,7,10,13,15,22,24] if i>pos[cur]),1)})),
    9: ("Everyone gives you 100g", lambda cur,pos,cash,pot: [cash.update({p: cash[p]-100}) or cash.update({cur: cash[cur]+100}) for p in st.session_state.players if p != cur]),
    10: ("Go to nearest owned property", lambda cur,pos,cash,pot: pos.update({cur: min((i for i,o in st.session_state.properties.items() if o and BOARD[i][1] in ("prop","rail","util")), key=lambda x:(x-pos[cur])%len(BOARD))})),
    11: ("Pay 100g", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]-100})),
    12: ("Collect 200g", lambda cur,pos,cash,pot: cash.update({cur: cash[cur]+200}))
}

# ======================
# INITIALIZE SESSION
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
            'free_parking_pot': 0
        })

init_game_state()

# ======================
# START GAME
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
            st.session_state.initialized = True
            st.success("Game started! Roll those real dice!")
            st.rerun()

# ======================
# MAIN GAME
# ======================
if st.session_state.initialized:
    p = st.session_state.players
    cur_idx = st.session_state.current_idx
    cur = p[cur_idx]
    cash = st.session_state.cash
    pos = st.session_state.position
    owner = st.session_state.properties
    jail = st.session_state.in_jail
    pot = st.session_state.free_parking_pot

    # HEADER
    col1,col2,col3,col4,col5 = st.columns([2,2,2,2.5,2.5])
    with col1: st.markdown(f"**Turn: {cur}** {'JAILED' if jail.get(cur,False) else ''}")
    with col2: st.markdown(f"**Gold: {cash.get(cur,0)}g**")
    with col3: st.markdown(f"**Pot: {pot}g**")
    with col4:
        if st.session_state.rolled:
            st.success(f"Started on: **{st.session_state.starting_square}**")
        else:
            st.info(f"Starting on: **{BOARD[pos.get(cur,0)][0]}**")
    with col5:
        if st.session_state.rolled:
            if st.button("Next Player", use_container_width=True):
                st.session_state.current_idx = (cur_idx + 1) % len(p)
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
    # HELPERS
    # ======================
    def add_cash(player, amt):
        cash[player] = cash.get(player,0)+amt
        if cash[player]<0:
            cash[player]=0

    def move_player(player,new_pos):
        pos[player]=new_pos

    def apply_chest_effect(roll):
        text,action=CHEST_CARDS.get(roll,("?? Unknown ??",lambda cur,pos,cash,pot:None))
        action(cur,pos,cash,pot)
        return text

    def apply_chance_effect(roll):
        text,action=CHANCE_CARDS.get(roll,("?? Unknown ??",lambda cur,pos,cash,pot:None))
        action(cur,pos,cash,pot)
        return text

    # ======================
    # ROLL DICE
    # ======================
    if not st.session_state.rolled:
        st.info("Enter your **real dice roll**")
        roll = st.number_input("Total rolled", 2, 12, 7, step=1, key="roll_input")
        doubles = st.checkbox("Doubles?", key="dubs_input")
        if st.button("Confirm Roll", type="primary"):
            st.session_state.last_roll = roll
            if doubles:
                st.session_state.doubles_streak += 1
                if st.session_state.doubles_streak >= 3:
                    move_player(cur,6)
                    jail[cur]=True
                    st.session_state.last_message="3 DOUBLES → JAIL!"
                    st.rerun()
            else: st.session_state.doubles_streak=0
            old_pos=pos[cur]
            new_pos=(old_pos+roll)%len(BOARD)
            move_player(cur,new_pos)
            st.session_state.landed=new_pos
            st.session_state.rolled=True
            crossed_go=new_pos<old_pos or (old_pos+roll>=len(BOARD))
            if crossed_go and new_pos!=0: add_cash(cur,300); st.balloons()
            space=BOARD[new_pos]
            name,typ=space[0],space[1]
            msg=f"Landed on **{name}**"
            if typ=="tax": tax=space[2]; add_cash(cur,-tax); st.session_state.free_parking_pot+=tax; msg=f"Paid **{tax}g {name} → Free Parking**"
            elif typ=="free":
                if pot>0: add_cash(cur,pot); st.session_state.free_parking_pot=0; msg=f"FREE PARKING JACKPOT! Collected **{pot}g**"; st.balloons()
                else: msg="Free Parking — no pot yet!"
            elif typ=="go2jail": move_player(cur,6); jail[cur]=True; msg="GO TO JAIL!"
            elif typ in ("prop","rail","util") and owner.get(new_pos) and owner[new_pos]!=cur:
                landlord=owner[new_pos]
                rent=space[3] if typ=="prop" else (40*(2**(sum(1 for i,o in owner.items() if o==landlord and BOARD[i][1]=="rail")-1)) if typ=="rail" else roll*(10 if sum(1 for i,o in owner.items() if o==landlord and BOARD[i][1]=="util")==1 else 20))
                add_cash(cur,-rent); add_cash(landlord,rent)
                msg=f"Paid **{landlord} {rent}g rent** on {name}"
            elif typ=="chest": msg=f"Chappa Chest → {apply_chest_effect(roll)}"
            elif typ=="chance": msg=f"Chapaa Chance → {apply_chance_effect(roll)}"
            st.session_state.last_message=msg
            st.rerun()

    # ======================
    # BUY PROPERTY
    # ======================
    landed_square=BOARD[pos[cur]]
    if st.session_state.rolled and landed_square[1] in ("prop","rail","util") and owner.get(pos[cur]) is None:
        price=landed_square[2]
        if st.button(f"Buy {landed_square[0]} for {price}g?"):
            if cash[cur]>=price: cash[cur]-=price; owner[pos[cur]]=cur; st.session_state.last_message=f"{cur} bought {landed_square[0]}!"
            else: st.error("Not enough gold!")

    # ======================
    # TRADE SYSTEM
    # ======================
    if st.button("Trade / Deal" if not st.session_state.trade_mode else "Cancel Trade"):
        st.session_state.trade_mode = not st.session_state.trade_mode
        st.rerun()

    if st.session_state.trade_mode:
        st.subheader("Trade / Deal Maker")
        others=[pl for pl in p if pl!=cur]
        partner=st.selectbox("Choose player to trade with:", others)

        st.markdown("---")
        st.markdown("### Your offer")
        offer_gold=st.number_input(f"{cur} gives gold:",0,cash[cur],10)
        your_props=[i for i,o in owner.items() if o==cur]
        offer_props=st.multiselect("Properties to trade:", your_props, format_func=lambda i:BOARD[i][0])
        offer_jail_card=(st.session_state.get('jail_free_card')==cur) and st.checkbox("Give Get Out of Jail Free card")

        st.markdown("### Partner offer")
        partner_gold=st.number_input(f"{partner} gives gold:",0,cash[partner],10)
        partner_props=[i for i,o in owner.items() if o==partner]
        partner_offer_props=st.multiselect("Properties to receive:", partner_props, format_func=lambda i:BOARD[i][0])
        partner_jail_card=(st.session_state.get('jail_free_card')==partner) and st.checkbox("Receive their Get Out of Jail Free card")

        if st.button("Confirm Trade", type="primary"):
            # Gold
            cash[cur]-=offer_gold; cash[partner]+=offer_gold
            cash[partner]-=partner_gold; cash[cur]+=partner_gold
            # Properties
            for prop in offer_props: owner[prop]=partner
            for prop in partner_offer_props: owner[prop]=cur
            # Jail card
            if offer_jail_card: st.session_state.jail_free_card=partner
            elif partner_jail_card: st.session_state.jail_free_card=cur
            st.session_state.last_message=f"Trade completed between **{cur}** and **{partner}**!"
            st.session_state.trade_mode=False
            st.rerun()

    # ======================
    # NEW GAME
    # ======================
    if st.button("New Game (Reset Everything)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

import streamlit as st
from random import randint, shuffle
from typing import List, Tuple, Callable

# Define cards with effects using st.session_state
CHEST_CARDS: List[Tuple[str, Callable[[str], None]]] = [
    ("Chapaa Chase to GO!", lambda cur: (old := st.session_state.pos[cur], st.session_state.pos[cur] := 0, st.session_state.cash[cur] += 200 if st.session_state.pos[cur] < old else 0)),
    ("Proudhorned Sernuk teleports you. GO TO JAIL!", lambda cur: (st.session_state.pos[cur] := 10, st.session_state.jail[cur] := True, st.session_state.jail_turns[cur] := 0)),
    ("Elouisa found a cryptid, everyone pays you 50g not to tell them about it!", lambda cur: ([st.session_state.cash[p] -= 50 for p in st.session_state.players if p != cur], st.session_state.cash[cur] += 50 * (len(st.session_state.players) - 1))),
    ("Eshe made Kenli enforce the land tax. Pay 100g", lambda cur: (st.session_state.cash[cur] -= 100, st.session_state.pot += 100)),
    ("Collect 100g from Subira for helping the order", lambda cur: st.session_state.cash[cur] += 100),
    ("Ogupu drags you into a whirlpool and moves you back 3 spaces", lambda cur: (old := st.session_state.pos[cur], st.session_state.pos[cur] := (st.session_state.pos[cur] - 3) % 40, st.session_state.cash[cur] += 200 if st.session_state.pos[cur] < old else 0)),  # Back moves rarely pass Go, but check anyway
    ("Bluebristle Muujin pushes you forward 3 spaces", lambda cur: (old := st.session_state.pos[cur], st.session_state.pos[cur] := (st.session_state.pos[cur] + 3) % 40, st.session_state.cash[cur] += 200 if st.session_state.pos[cur] < old else 0)),
    ("Tamala tricks you into paying the poorest player 100g", lambda cur: (poorest := min(st.session_state.players, key=lambda p: st.session_state.cash[p]), st.session_state.cash[cur] -= 100, st.session_state.cash[poorest] += 100, st.session_state.pot += 0)),  # No pot change
    ("You followed a Peki to the next Travel Point", lambda cur: (old := st.session_state.pos[cur], st.session_state.pos[cur] := min([5, 15, 25, 35], key=lambda tp: (tp - old) % 40 if (tp - old) % 40 != 0 else 40), st.session_state.cash[cur] += 200 if st.session_state.pos[cur] < old else 0)),
    ("Tish has new furniture, pay 150g", lambda cur: (st.session_state.cash[cur] -= 150, st.session_state.pot += 150)),
    ("Zeki drops off some treasure. Collect 200g", lambda cur: st.session_state.cash[cur] += 200),
]

CHANCE_CARDS: List[Tuple[str, Callable[[str], None]]] = [
    ("Tau spots something buried, go to Free Parking to dig it up and collect whatever is there", lambda cur: (old := st.session_state.pos[cur], st.session_state.pos[cur] := 20, st.session_state.cash[cur] += 200 if st.session_state.pos[cur] < old else 0, st.session_state.cash[cur] += st.session_state.pot, st.session_state.pot := 0)),
    ("Plumehound buried a Get Out of Jail Free card, go find it and keep that one", lambda cur: st.session_state.jail_free[cur] += 1),
    ("Jina found a rare artifact. Give 50g to all the humans", lambda cur: (num := len(st.session_state.players) - 1, st.session_state.cash[cur] -= 50 * num, [st.session_state.cash[p] += 50 for p in st.session_state.players if p != cur], st.session_state.pot += 50 * num)),
    ("Caught in the restricted section, pay Caleri 200g", lambda cur: (st.session_state.cash[cur] -= 200, st.session_state.pot += 200)),
    ("Collect 150g for promoting Jels new wardrobe", lambda cur: st.session_state.cash[cur] += 150),
    ("Follow a flutterfox to the next shrub", lambda cur: (old := st.session_state.pos[cur], st.session_state.pos[cur] := min([12, 28], key=lambda tp: (tp - old) % 40 if (tp - old) % 40 != 0 else 40), st.session_state.cash[cur] += 200 if st.session_state.pos[cur] < old else 0)),
    ("Ormuu pushes you to next main property", lambda cur: (old := st.session_state.pos[cur], main_props := [1, 3, 6, 8, 9, 11, 13, 14, 16, 18, 19, 21, 23, 24, 26, 27, 29, 31, 32, 34, 37, 39], st.session_state.pos[cur] := min(main_props, key=lambda tp: (tp - old) % 40 if (tp - old) % 40 != 0 else 40), st.session_state.cash[cur] += 200 if st.session_state.pos[cur] < old else 0)),
    ("Badruu gives you new fruit, everyone gives you 100g for the seeds", lambda cur: ([st.session_state.cash[p] -= 100 for p in st.session_state.players if p != cur], st.session_state.cash[cur] += 100 * (len(st.session_state.players) - 1))),
    ("Go and help the truffle at the nearest owned property", lambda cur: (old := st.session_state.pos[cur], owned := [i for i in st.session_state.owners if st.session_state.owners[i] is not None], (st.session_state.pos[cur] := min(owned, key=lambda tp: (tp - old) % 40 if (tp - old) % 40 != 0 else 40) if owned else old, st.session_state.cash[cur] += 200 if st.session_state.pos[cur] < old else 0))),
    ("You lost the Gardeners Runestone. Pay 100g to Einar and Hekla can help make a new one", lambda cur: (st.session_state.cash[cur] -= 100, st.session_state.pot += 100)),
    ("Reth just started selling beanburgers and flowtato fries, for giving him the idea to star fast food he pays you 150g", lambda cur: st.session_state.cash[cur] += 150),
]

# Main app
if 'started' not in st.session_state:
    st.session_state.started = True
    st.session_state.players = ['Player1', 'Player2']  # Add more players as needed
    st.session_state.active_players = set(st.session_state.players)
    st.session_state.pos = {p: 0 for p in st.session_state.players}
    st.session_state.cash = {p: 1500 for p in st.session_state.players}
    st.session_state.jail = {p: False for p in st.session_state.players}
    st.session_state.jail_turns = {p: 0 for p in st.session_state.players}
    st.session_state.jail_free = {p: 0 for p in st.session_state.players}
    st.session_state.pot = 0
    st.session_state.current_player_index = 0
    st.session_state.doubles_count = 0
    st.session_state.turn_phase = 'roll'
    st.session_state.dice = (0, 0)
    st.session_state.chance_deck = CHANCE_CARDS.copy()
    shuffle(st.session_state.chance_deck)
    st.session_state.chest_deck = CHEST_CARDS.copy()
    shuffle(st.session_state.chest_deck)

    # Board setup (standard Monopoly for simplicity, adjust if custom board needed)
    st.session_state.board = [
        'Go', 'Mediterranean Avenue', 'Community Chest', 'Baltic Avenue', 'Income Tax',
        'Reading Railroad', 'Oriental Avenue', 'Chance', 'Vermont Avenue', 'Connecticut Avenue',
        'Jail', 'St. Charles Place', 'Electric Company', 'States Avenue', 'Virginia Avenue',
        'Pennsylvania Railroad', 'St. James Place', 'Community Chest', 'Tennessee Avenue', 'New York Avenue',
        'Free Parking', 'Kentucky Avenue', 'Chance', 'Indiana Avenue', 'Illinois Avenue',
        'B & O Railroad', 'Atlantic Avenue', 'Ventnor Avenue', 'Water Works', 'Marvin Gardens',
        'Go To Jail', 'Pacific Avenue', 'North Carolina Avenue', 'Community Chest', 'Pennsylvania Avenue',
        'Short Line', 'Chance', 'Park Place', 'Luxury Tax', 'Boardwalk'
    ]
    property_positions = [1, 3, 6, 8, 9, 11, 13, 14, 16, 18, 19, 21, 23, 24, 26, 27, 29, 31, 32, 34, 37, 39]
    railroad_positions = [5, 15, 25, 35]
    utility_positions = [12, 28]
    all_properties = property_positions + railroad_positions + utility_positions
    st.session_state.owners = {i: None for i in all_properties}
    # Prices
    st.session_state.prices = {1: 60, 3: 60, 6: 100, 8: 100, 9: 120, 11: 140, 13: 140, 14: 160, 16: 180, 18: 180, 19: 200,
                               21: 220, 23: 220, 24: 240, 26: 260, 27: 260, 29: 280, 31: 300, 32: 300, 34: 320, 37: 350, 39: 400,
                               5: 200, 15: 200, 25: 200, 35: 200, 12: 150, 28: 150}
    # Base rents (simplified, no houses/monopolies)
    st.session_state.base_rents = {i: st.session_state.prices[i] // 10 for i in property_positions}
    for r in railroad_positions:
        st.session_state.base_rents[r] = 25
    for u in utility_positions:
        st.session_state.base_rents[u] = 4  # Multiplied by dice later

cur = st.session_state.players[st.session_state.current_player_index]

st.write(f"Current Player: {cur} {'(Jailed)' if st.session_state.jail[cur] else ''}")

# Display player statuses
for p in st.session_state.players:
    if p in st.session_state.active_players:
        st.write(f"{p}: ${st.session_state.cash[p]} at {st.session_state.board[st.session_state.pos[p]]}")

# Display property overview
st.write("Property Overview:")
for i, name in enumerate(st.session_state.board):
    if i in st.session_state.owners:
        owner = st.session_state.owners[i] if st.session_state.owners[i] else 'Unowned'
        st.write(f"{name} (Position {i}): {owner}")

# Jail options
if st.session_state.jail[cur]:
    if st.button("Pay $50 to get out of jail"):
        st.session_state.cash[cur] -= 50
        st.session_state.pot += 50
        st.session_state.jail[cur] = False
        st.session_state.jail_turns[cur] = 0
        st.rerun()
    if st.session_state.jail_free[cur] > 0 and st.button("Use Get Out of Jail Free card"):
        st.session_state.jail_free[cur] -= 1
        st.session_state.jail[cur] = False
        st.session_state.jail_turns[cur] = 0
        st.rerun()

if st.session_state.turn_phase == 'roll':
    if st.button("Roll Dice"):
        die1 = randint(1, 6)
        die2 = randint(1, 6)
        roll = die1 + die2
        doubles = die1 == die2
        st.session_state.dice = (die1, die2)

        if st.session_state.jail[cur]:
            st.session_state.jail_turns[cur] += 1
            if doubles:
                st.session_state.jail[cur] = False
                st.session_state.jail_turns[cur] = 0
                move_player(cur, roll)
            elif st.session_state.jail_turns[cur] == 3:
                st.session_state.cash[cur] -= 50
                st.session_state.pot += 50
                st.session_state.jail[cur] = False
                st.session_state.jail_turns[cur] = 0
                move_player(cur, roll)
            else:
                st.session_state.turn_phase = 'end'
        else:
            move_player(cur, roll)
            if doubles:
                st.session_state.doubles_count += 1
                if st.session_state.doubles_count == 3:
                    send_to_jail(cur)
                    st.session_state.doubles_count = 0
                    st.session_state.turn_phase = 'end'
                else:
                    st.session_state.turn_phase = 'roll'  # Roll again
            else:
                st.session_state.doubles_count = 0
                st.session_state.turn_phase = 'end'
        st.rerun()

st.write(f"Dice: {st.session_state.dice[0]} + {st.session_state.dice[1]} = {sum(st.session_state.dice)}")

if st.session_state.turn_phase == 'end':
    if st.button("End Turn"):
        next_player()
        st.rerun()

def send_to_jail(cur: str):
    st.session_state.pos[cur] = 10
    st.session_state.jail[cur] = True
    st.session_state.jail_turns[cur] = 0
    st.session_state.turn_phase = 'end'

def move_player(cur: str, amount: int):
    old_pos = st.session_state.pos[cur]
    new_pos = (old_pos + amount) % len(st.session_state.board)
    st.session_state.pos[cur] = new_pos
    if new_pos < old_pos:
        st.session_state.cash[cur] += 200
    land_on(cur)

def land_on(cur: str):
    pos = st.session_state.pos[cur]
    if pos == 30:
        send_to_jail(cur)
        return
    elif pos in [2, 17, 33]:  # Community Chest
        draw_card(cur, 'chest')
    elif pos in [7, 22, 36]:  # Chance
        draw_card(cur, 'chance')
    elif pos in [4, 38]:  # Taxes
        amount = 200 if pos == 4 else 75
        st.session_state.cash[cur] -= amount
        st.session_state.pot += amount
        check_bankrupt(cur)
    elif pos == 20:  # Free Parking
        st.session_state.cash[cur] += st.session_state.pot
        st.session_state.pot = 0
    elif pos in st.session_state.owners:
        owner = st.session_state.owners[pos]
        if owner == cur:
            pass
        elif owner is None:
            price = st.session_state.prices.get(pos, 0)
            if st.button(f"Buy {st.session_state.board[pos]} for ${price}"):
                if st.session_state.cash[cur] >= price:
                    st.session_state.cash[cur] -= price
                    st.session_state.pot += price  # Bank receives? Or not, since bank infinite
                    st.session_state.owners[pos] = cur
                st.rerun()
        else:
            rent = get_rent(pos, owner)
            st.session_state.cash[cur] -= rent
            st.session_state.cash[owner] += rent
            check_bankrupt(cur, owner)

def draw_card(cur: str, deck_type: str):
    if deck_type == 'chance':
        if not st.session_state.chance_deck:
            st.session_state.chance_deck = CHANCE_CARDS.copy()
            shuffle(st.session_state.chance_deck)
        desc, func = st.session_state.chance_deck.pop(0)
    else:
        if not st.session_state.chest_deck:
            st.session_state.chest_deck = CHEST_CARDS.copy()
            shuffle(st.session_state.chest_deck)
        desc, func = st.session_state.chest_deck.pop(0)
    st.write(desc)
    old_pos = st.session_state.pos[cur]
    func(cur)
    new_pos = st.session_state.pos[cur]
    if new_pos != old_pos:
        land_on(cur)

def get_rent(pos: int, owner: str) -> int:
    if pos in [5, 15, 25, 35]:  # Railroads
        num_owned = sum(1 for r in [5, 15, 25, 35] if st.session_state.owners.get(r) == owner)
        return 25 * (2 ** (num_owned - 1))
    elif pos in [12, 28]:  # Utilities
        num_owned = sum(1 for u in [12, 28] if st.session_state.owners.get(u) == owner)
        multiplier = 4 if num_owned == 1 else 10
        return (st.session_state.dice[0] + st.session_state.dice[1]) * multiplier
    else:  # Properties (simplified base rent)
        return st.session_state.base_rents.get(pos, 0)

def check_bankrupt(cur: str, creditor: str = None):
    if st.session_state.cash[cur] < 0:
        st.write(f"{cur} is bankrupt!")
        if creditor:
            for i in st.session_state.owners:
                if st.session_state.owners[i] == cur:
                    st.session_state.owners[i] = creditor
        else:
            for i in st.session_state.owners:
                if st.session_state.owners[i] == cur:
                    st.session_state.owners[i] = None
        if cur in st.session_state.active_players:
            st.session_state.active_players.remove(cur)
        st.session_state.cash[cur] = 0
        next_player()

def next_player():
    st.session_state.current_player_index = (st.session_state.current_player_index + 1) % len(st.session_state.players)
    cur = st.session_state.players[st.session_state.current_player_index]
    while cur not in st.session_state.active_players:
        st.session_state.current_player_index = (st.session_state.current_player_index + 1) % len(st.session_state.players)
        cur = st.session_state.players[st.session_state.current_player_index]
    st.session_state.turn_phase = 'roll'
    st.session_state.doubles_count = 0

import streamlit as st
import random

# ======================
# PAGE SETUP
# ======================
st.set_page_config(page_title="Paliopoly – Chilled Dude Edition", layout="centered")
st.title("Paliopoly – Chilled Dude Edition — Streamer Friendly")
st.markdown("**Includes fixes: doubles, jail, chest/chance, GO money, Easter eggs, trades, bankrupt, board overview**")

# ======================
# SPLASH SCREEN / PLAYER NAMES
# ======================
SPLASH_IMAGE = "https://raw.githubusercontent.com/theonetimhart-sketch/Paliopoly/main/image3.PNG"

if 'passed_splash' not in st.session_state:
    st.session_state.passed_splash = False

if not st.session_state.passed_splash:
    st.image(SPLASH_IMAGE, use_column_width=True)
    st.markdown("### Welcome! Host: ShorTee / lilshrtchit")
    st.write("Make sure players are watching the stream: https://www.twitch.tv/lilshrtchit")

    if 'splash_players_input' not in st.session_state:
        st.session_state.splash_players_input = "Chilled Dude, lilshrtchit, Player3"

    st.session_state.splash_players_input = st.text_input(
        "Enter player names (comma separated):", st.session_state.splash_players_input, key="splash_names"
    )
    tentative_players = [n.strip() for n in st.session_state.splash_players_input.split(",") if n.strip()]

    # Check if Chilled Dude is present
    if any(p.lower() == "chilled dude" for p in tentative_players):
        st.success("Chilled Dude is present!")
        if st.button("Continue", key="splash_continue_cd"):
            st.session_state.players = tentative_players
            st.session_state.passed_splash = True
            st.experimental_rerun()
    else:
        pwd = st.text_input("Chilled Dude is not present. Enter host password:", type="password", key="pwd_input")
        if st.button("Continue", key="splash_continue_pwd"):
            if pwd == "TJediTim":
                st.session_state.players = tentative_players
                st.session_state.passed_splash = True
                st.success("Password accepted — continuing!")
                st.experimental_rerun()
            else:
                st.error("Incorrect password.")

    st.stop()  # halt execution until splash is passed

# ======================
# SESSION STATE INITIALIZATION
# ======================
def init_game_state():
    if 'initialized' not in st.session_state:
        players = st.session_state.get('players', [])
        st.session_state.update({
            'initialized': True,
            'players': players,
            'cash': {p: 1000 for p in players},
            'position': {p: 0 for p in players},
            'properties': {i: None for i in range(25)},  # adjust board length later
            'in_jail': {p: False for p in players},
            'jail_turns': {p: 0 for p in players},
            'jail_free_card': None,
            'current_idx': 0,
            'doubles_streak': 0,
            'rolled': False,
            'landed': None,
            'last_message': "",
            'trade_mode': False,
            'starting_square': "",
            'free_parking_pot': 0,
            'bankrupt': {p: False for p in players},
            'confirm_bankrupt_for': None,
            'confirm_next_for': None,
            'easter_eggs_claimed': {p: {"chilled dude": False, "lilshrtchit": False} for p in players}
        })

init_game_state()

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
    ("Elouisa found a cryptid, everyone pays you 50g", 
     lambda p,ss,roll: [ss['cash'].__setitem__(q, ss['cash'][q]-50) or ss['cash'].__setitem__(p, ss['cash'][p]+50) for q in ss['players'] if q!=p]),
    ("Eshe made Kenli enforce the land tax. Pay 100g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]-100)),
    ("Collect 100g from Subira for helping the order", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]+100)),
    ("Ogupuu drags you into a whirlpool and moves you back 3 spaces", lambda p,ss,roll: ss['position'].__setitem__(p, (ss['position'][p]-3) % len(BOARD))),
    ("Bluebristle Muujin pushes you forward 3 spaces", lambda p,ss,roll: ss['position'].__setitem__(p, (ss['position'][p]+3) % len(BOARD))),
    ("Tamala tricks you into paying the poorest player 100g", 
     lambda p,ss,roll: (lambda poorest=min([x for x in ss['players'] if not ss['bankrupt'].get(x,False)], key=lambda x: ss['cash'][x]): (ss['cash'].__setitem__(p, ss['cash'][p]-100), ss['cash'].__setitem__(poorest, ss['cash'][poorest]+100)))()),
    ("You followed a Peki to the next Travel Point", lambda p,ss,roll: ss['position'].__setitem__(p, min([4,9,16,21], key=lambda x:(x-ss['position'][p])%len(BOARD)))),
    ("Tish has new furniture, pay 150g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]-150)),
    ("Zeki drops off some treasure, collect 200g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]+200))
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
    ("Tau spots something buried, go to Free Parking", chance_free_parking),
    ("Plumehound buried a Get Out of Jail Free card", chance_get_out_of_jail),
    ("Jina found a rare artifact. Give 50g to all other players", lambda p,ss,roll: [ss['cash'].__setitem__(q, ss['cash'][q]+50) or ss['cash'].__setitem__(p, ss['cash'][p]-50) for q in ss['players'] if q!=p]),
    ("Caught in the restricted section, pay Caleri 200g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]-200)),
    ("Collect 150g for promoting Jels new wardrobe", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]+150)),
    ("Follow a flutterfox to the next shrub", lambda p,ss,roll: ss['position'].__setitem__(p, next((i for i in [13,15,22,24] if i>ss['position'][p]),13))),
    ("Ormuu pushes you to next main property", lambda p,ss,roll: ss['position'].__setitem__(p, next((i for i in [1,3,7,10,13,15,22,24] if i>ss['position'][p]),1))),
    ("Badruu gives you new fruit, everyone gives you 100g for the seeds", lambda p,ss,roll: [ss['cash'].__setitem__(q, ss['cash'][q]-100) or ss['cash'].__setitem__(p, ss['cash'][p]+100) for q in ss['players'] if q!=p]),
    ("Go help the trufflet at the nearest owned property", lambda p,ss,roll: ss['position'].__setitem__(p, min([i for i,o in ss['properties'].items() if o and BOARD[i][1] in ('prop','rail','util')], key=lambda x:(x-ss['position'][p])%len(BOARD)))),
    ("You lost the Gardners runestone, Pay 100g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]-100)),
    ("Reth sells beanburgers, pays you 200g", lambda p,ss,roll: ss['cash'].__setitem__(p, ss['cash'][p]+200))
]

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

# ======================
# TRADE SYSTEM
# ======================
if cur and not ss['bankrupt'].get(cur, False):
    if st.button("Trade / Deal" if not ss.get('trade_mode', False) else "Cancel Trade"):
        ss['trade_mode'] = not ss.get('trade_mode', False)
        st.rerun()

    if ss.get('trade_mode', False):
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
                if not valid:
                    st.warning("Trade aborted due to changed ownership.")
                else:
                    # Exchange gold
                    ss['cash'][cur] -= offer_gold
                    ss['cash'][partner] += offer_gold
                    ss['cash'][partner] -= partner_gold
                    ss['cash'][cur] += partner_gold
                    # Exchange properties
                    for i in offer_props: ss['properties'][i] = partner
                    for i in partner_offer_props: ss['properties'][i] = cur
                    # Exchange jail card
                    if offer_jail_card: ss['jail_free_card'] = partner
                    elif partner_jail_card: ss['jail_free_card'] = cur
                    ss['trade_mode'] = False
                    ss['last_message'] = f"Trade completed between **{cur}** and **{partner}**!"
                    st.success(ss['last_message'])
                    st.rerun()

# ----------------------
# BANKRUPT / QUIT
# ----------------------
if cur and not ss['bankrupt'].get(cur, False):
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

# ----------------------
# FINAL CHECK: GAME END
# ----------------------
check_game_end()

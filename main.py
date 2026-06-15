#!/usr/bin/env python3
"""
TerminalQuest - A text-based RPG adventure
Built for Macondo / Hack Club
"""
import json, os, random, sys, time, textwrap

SAVE_FILE = "save.json"
VERSION = "2.0"
WIDTH = 60

# ─── ANSI COLORS ──────────────────────────────────────────
R='\033[0m'; BOLD='\033[1m'; DIM='\033[2m'
RED='\033[91m'; GREEN='\033[92m'; YELLOW='\033[93m'
BLUE='\033[94m'; MAGENTA='\033[95m'; CYAN='\033[96m'; WHITE='\033[97m'
BRED='\033[101m'; BGREEN='\033[42m'

def c(text, color): return f"{color}{text}{R}"
def box(title, char='═'):
    w = WIDTH
    top = f"╔{char*( w-2)}╗"
    mid = f"║  {BOLD}{title:<{w-4}}{R}  ║"
    bot = f"╚{char*(w-2)}╝"
    return f"{top}\n{mid}\n{bot}"

# ─── WORLD ────────────────────────────────────────────────
ROOMS = {
    "forest": {
        "name": "🌲 Dark Forest",
        "desc": "Ancient oaks loom overhead, roots twisting across the muddy path. Strange eyes glint between the trees.",
        "exits": {"north": "village", "east": "cave", "south": "swamp"},
        "enemies": [
            {"name": "Dire Wolf",    "hp": 28, "max_hp": 28, "atk": 6,  "def": 2,  "xp": 12, "gold": 7,  "emoji": "🐺"},
            {"name": "Goblin Scout", "hp": 22, "max_hp": 22, "atk": 5,  "def": 1,  "xp": 8,  "gold": 5,  "emoji": "👺"},
        ],
        "encounter_rate": 0.55
    },
    "village": {
        "name": "🏘️  Riverside Village",
        "desc": "Smoke curls from chimneys. Villagers eye you warily. A wooden sign reads 'Thornwick — pop. 47'.",
        "exits": {"south": "forest", "east": "dungeon", "north": "ruins"},
        "shop": {
            "Iron Sword":   {"price": 40, "stat": "atk", "val": 8,  "emoji": "⚔️ "},
            "Steel Shield": {"price": 35, "stat": "def", "val": 6,  "emoji": "🛡️ "},
            "Health Potion":{"price": 15, "stat": "heal","val": 40, "emoji": "🧪"},
            "Mana Crystal": {"price": 25, "stat": "mp",  "val": 30, "emoji": "💎"},
        },
        "encounter_rate": 0
    },
    "cave": {
        "name": "🕳️  Echoing Cave",
        "desc": "Dripping stalactites catch the torch light. The smell of sulfur hangs heavy in the stale air.",
        "exits": {"west": "forest", "north": "dungeon", "down": "mine"},
        "enemies": [
            {"name": "Cave Troll",   "hp": 45, "max_hp": 45, "atk": 10, "def": 4,  "xp": 25, "gold": 15, "emoji": "👹"},
            {"name": "Giant Spider", "hp": 35, "max_hp": 35, "atk": 8,  "def": 2,  "xp": 18, "gold": 10, "emoji": "🕷️ "},
        ],
        "item": {"name": "🔮 Arcane Gem", "desc": "It pulses with cold energy.", "gold": 60, "collected": False},
        "encounter_rate": 0.65
    },
    "swamp": {
        "name": "🌿 Bogmire Swamp",
        "desc": "Black water gurgles underfoot. Will-o-wisps dance above the fog. The path is barely visible.",
        "exits": {"north": "forest", "east": "mine"},
        "enemies": [
            {"name": "Bog Witch",    "hp": 40, "max_hp": 40, "atk": 12, "def": 1,  "xp": 22, "gold": 18, "emoji": "🧙"},
            {"name": "Slime Beast",  "hp": 30, "max_hp": 30, "atk": 7,  "def": 5,  "xp": 15, "gold": 8,  "emoji": "🫧"},
        ],
        "item": {"name": "🌿 Witch Herb", "desc": "Rare medicinal herb. Worth gold.", "gold": 35, "collected": False},
        "encounter_rate": 0.70
    },
    "mine": {
        "name": "⛏️  Abandoned Mine",
        "desc": "Collapsed timbers. Rusted carts on cracked rails. Something tunneled through these walls recently.",
        "exits": {"up": "cave", "west": "swamp", "north": "dungeon"},
        "enemies": [
            {"name": "Rock Golem",   "hp": 60, "max_hp": 60, "atk": 14, "def": 8,  "xp": 35, "gold": 25, "emoji": "🗿"},
            {"name": "Cave Bat",     "hp": 20, "max_hp": 20, "atk": 9,  "def": 1,  "xp": 10, "gold": 6,  "emoji": "🦇"},
        ],
        "item": {"name": "💎 Adamant Ore", "desc": "A chunk of rare metal. Very valuable.", "gold": 80, "collected": False},
        "encounter_rate": 0.60
    },
    "ruins": {
        "name": "🏛️  Ancient Ruins",
        "desc": "Moss-covered stone arches. Inscriptions in a forgotten tongue. A shattered altar glows faintly.",
        "exits": {"south": "village", "east": "dungeon"},
        "enemies": [
            {"name": "Shade",        "hp": 50, "max_hp": 50, "atk": 15, "def": 3,  "xp": 30, "gold": 20, "emoji": "👻"},
            {"name": "Bone Archer",  "hp": 35, "max_hp": 35, "atk": 11, "def": 2,  "xp": 20, "gold": 12, "emoji": "💀"},
        ],
        "item": {"name": "📜 Ancient Scroll", "desc": "Grants +10 ATK when read.", "stat": "atk", "val": 10, "collected": False},
        "encounter_rate": 0.65
    },
    "dungeon": {
        "name": "🏰 Ancient Dungeon",
        "desc": "Iron torches flicker in the damp darkness. The Dragon's roar shakes dust from the vaulted ceiling.",
        "exits": {"west": "village", "south": "cave", "northwest": "ruins", "southwest": "mine"},
        "boss": {"name": "Inferno Dragon", "hp": 120, "max_hp": 120, "atk": 25, "def": 10, "xp": 200, "gold": 300, "emoji": "🐉"},
        "encounter_rate": 0
    }
}

ITEMS = {
    "Rusty Sword":   {"stat": "atk", "val": 5},
    "Iron Sword":    {"stat": "atk", "val": 8},
    "Steel Shield":  {"stat": "def", "val": 6},
    "Health Potion": {"stat": "heal","val": 40},
    "Mana Crystal":  {"stat": "mp",  "val": 30},
}

# ─── HELPERS ──────────────────────────────────────────────
def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def slow_print(text, delay=0.018):
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()

def hp_bar(current, maximum, width=20):
    pct = current / maximum
    filled = int(pct * width)
    color = GREEN if pct > 0.5 else YELLOW if pct > 0.25 else RED
    bar = f"[{color}{'█'*filled}{'░'*(width-filled)}{R}]"
    return f"{bar} {current}/{maximum}"

def xp_bar(xp, level, width=20):
    needed = level * 50
    pct = min(xp / needed, 1.0)
    filled = int(pct * width)
    bar = f"[{CYAN}{'▓'*filled}{'░'*(width-filled)}{R}]"
    return f"{bar} {xp}/{needed}"

def divider(char='─'): print(c(char * WIDTH, DIM))

def wrap(text, indent=3):
    return textwrap.fill(text, WIDTH, initial_indent=' '*indent, subsequent_indent=' '*indent)

# ─── PLAYER ───────────────────────────────────────────────
def new_game():
    clear()
    print(box("  ⚔️   CREATE YOUR HERO   ⚔️  "))
    print()
    name = input(f"  {CYAN}Hero name{R}: ").strip() or "Hero"
    print()
    print(f"  Choose your {BOLD}class{R}:")
    print(f"  {GREEN}[1]{R} Warrior  — High HP, extra DEF")
    print(f"  {MAGENTA}[2]{R} Rogue    — High ATK, fast")
    print(f"  {BLUE}[3]{R} Mage     — MP spells, balanced")
    ch = input(f"\n  {CYAN}>{R} ").strip()
    classes = {
        "1": {"cls":"Warrior", "hp":130,"atk":14,"def":5, "mp":20},
        "2": {"cls":"Rogue",   "hp":100,"atk":20,"def":2, "mp":20},
        "3": {"cls":"Mage",    "hp":100,"atk":12,"def":3, "mp":60},
    }
    stats = classes.get(ch, classes["1"])
    return {
        "name": name, "class": stats["cls"],
        "hp": stats["hp"], "max_hp": stats["hp"],
        "atk": stats["atk"], "def": stats["def"],
        "mp": stats["mp"], "max_mp": stats["mp"],
        "gold": 15, "xp": 0, "level": 1,
        "kills": 0, "steps": 0,
        "inventory": ["Rusty Sword"],
        "equipped": {"weapon": "Rusty Sword", "armor": None},
        "location": "forest",
        "visited": [],
        "boss_defeated": False
    }

def save_game(player):
    with open(SAVE_FILE, 'w') as f:
        json.dump(player, f, indent=2)
    print(c("  💾 Game saved!", GREEN))

def load_game():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE) as f:
                return json.load(f)
        except:
            return None
    return None

# ─── COMBAT ───────────────────────────────────────────────
def combat(player, enemy_template, is_boss=False):
    enemy = dict(enemy_template)
    print()
    print(box(f"  {enemy['emoji']} ENCOUNTER: {enemy['name'].upper()}  "))
    time.sleep(0.3)

    turn = 0
    while player['hp'] > 0 and enemy['hp'] > 0:
        turn += 1
        print()
        divider()
        print(f"  {c('You', GREEN)}  HP {hp_bar(player['hp'], player['max_hp'], 16)}  {c('MP', BLUE)}: {player['mp']}")
        print(f"  {c(enemy['name'], RED)}  HP {hp_bar(enemy['hp'], enemy['max_hp'], 16)}")
        divider()
        print(f"\n  {BOLD}Actions:{R}")
        print(f"  {GREEN}[a]{R} Attack    {YELLOW}[m]{R} Magic (20 MP)    {CYAN}[p]{R} Use Potion")
        print(f"  {MAGENTA}[s]{R} Special   {RED}[r]{R} Run\n")
        action = input(f"  {CYAN}>{R} ").strip().lower()

        if action == 'r':
            if random.random() < 0.45:
                slow_print(c("  💨 You successfully fled!", YELLOW))
                return player, False
            else:
                slow_print(c("  ❌ Can't escape!", RED))
        elif action == 'a':
            dmg = max(1, random.randint(player['atk']-3, player['atk']+4) - enemy.get('def',0)//2)
            crit = random.random() < 0.15
            if crit: dmg = int(dmg * 1.8)
            enemy['hp'] -= dmg
            msg = f"  ⚔️  You deal {c(str(dmg)+' dmg', GREEN)}"
            if crit: msg += c("  ✨ CRITICAL HIT!", YELLOW)
            slow_print(msg)
        elif action == 'm':
            if player['mp'] >= 20:
                dmg = max(1, random.randint(player['atk']+5, player['atk']+15))
                enemy['hp'] -= dmg
                player['mp'] = max(0, player['mp'] - 20)
                slow_print(f"  💫 Magic bolt deals {c(str(dmg)+' dmg', MAGENTA)}!")
            else:
                slow_print(c("  ❌ Not enough MP!", RED))
                continue
        elif action == 's':
            # Special: stun + heavy hit
            dmg = max(1, random.randint(player['atk']+2, player['atk']+8))
            enemy['hp'] -= dmg
            stun = random.random() < 0.4
            slow_print(f"  🌀 Special attack! {c(str(dmg)+' dmg', CYAN)}")
            if stun:
                slow_print(c("  💫 Enemy is stunned! They miss their turn!", YELLOW))
                if enemy['hp'] > 0:
                    if player['hp'] <= 0:
                        slow_print(c("  💀 You have fallen...", RED))
                        return player, False
                continue
        elif action == 'p':
            potions = [i for i in player['inventory'] if i == 'Health Potion']
            if potions:
                player['inventory'].remove('Health Potion')
                heal = ITEMS['Health Potion']['val']
                player['hp'] = min(player['max_hp'], player['hp'] + heal)
                slow_print(f"  🧪 Healed {c(str(heal)+' HP', GREEN)}! Now at {player['hp']}/{player['max_hp']}")
            else:
                slow_print(c("  ❌ No potions!", RED))
                continue
        else:
            slow_print(c("  ❓ Unknown action.", DIM))
            continue

        # Enemy attacks
        if enemy['hp'] > 0:
            time.sleep(0.2)
            edm = max(1, random.randint(enemy['atk']-3, enemy['atk']+3) - player['def'])
            emiss = random.random() < 0.12
            if is_boss and random.random() < 0.2:
                edm = int(edm * 1.5)
                slow_print(f"  {c('🔥 Dragon breathes fire!', RED)} You take {c(str(edm)+' dmg', RED)}!")
            elif emiss:
                slow_print(c(f"  💨 {enemy['name']} misses!", DIM))
            else:
                player['hp'] -= edm
                slow_print(f"  {enemy['emoji']} {enemy['name']} hits you for {c(str(edm)+' dmg', RED)}!")

    if player['hp'] <= 0:
        player['hp'] = 0
        print()
        slow_print(c("  💀 You have been defeated...", RED), 0.04)
        slow_print(c("  Respawning in the forest with half HP...", YELLOW))
        time.sleep(1)
        player['hp'] = max(1, player['max_hp'] // 2)
        player['location'] = 'forest'
        return player, False

    # Victory
    print()
    slow_print(c(f"  🏆 Victory! {enemy['name']} defeated!", GREEN), 0.025)
    player['xp']   += enemy['xp']
    player['gold'] += enemy['gold']
    player['kills'] += 1
    slow_print(f"  +{c(str(enemy['xp'])+ ' XP', CYAN)}  +{c(str(enemy['gold'])+' gold', YELLOW)}")

    # Level up
    while player['xp'] >= player['level'] * 50:
        player['level']  += 1
        player['atk']    += 2
        player['def']    += 1
        player['max_hp'] += 15
        player['max_mp'] += 10
        player['hp']     = player['max_hp']
        player['mp']     = player['max_mp']
        print()
        slow_print(c(f"  🌟 LEVEL UP! → Level {player['level']}", YELLOW), 0.025)
        slow_print(f"  {GREEN}ATK {player['atk']}  DEF {player['def']}  HP {player['max_hp']}  MP {player['max_mp']}{R}")

    return player, True

# ─── SHOP ─────────────────────────────────────────────────
def shop(player, items):
    while True:
        clear()
        print(box("  🛒  THORNWICK SHOP  "))
        print(f"\n  {YELLOW}💰 Gold: {player['gold']}{R}\n")
        keys = list(items.keys())
        for i, (item, info) in enumerate(items.items(), 1):
            stat_str = f"+{info['val']} {info['stat'].upper()}" if info['stat'] != 'heal' else f"Restores {info['val']} HP"
            print(f"  {CYAN}[{i}]{R} {info['emoji']} {item:<20} {YELLOW}{info['price']}g{R}  {DIM}{stat_str}{R}")
        print(f"\n  {RED}[q]{R} Leave shop\n")
        ch = input(f"  {CYAN}>{R} ").strip().lower()
        if ch == 'q': break
        try:
            idx = int(ch) - 1
            item = keys[idx]
            info = items[item]
            if player['gold'] < info['price']:
                slow_print(c("  ❌ Not enough gold!", RED)); time.sleep(0.8)
            else:
                player['gold'] -= info['price']
                if info['stat'] == 'heal':
                    player['inventory'].append(item)
                    slow_print(c(f"  ✅ Bought {item}!", GREEN))
                elif info['stat'] == 'atk':
                    player['atk'] += info['val']
                    player['inventory'].append(item)
                    slow_print(c(f"  ✅ Bought {item}! ATK +{info['val']}", GREEN))
                elif info['stat'] == 'def':
                    player['def'] += info['val']
                    player['inventory'].append(item)
                    slow_print(c(f"  ✅ Bought {item}! DEF +{info['val']}", GREEN))
                elif info['stat'] == 'mp':
                    player['max_mp'] += info['val']
                    player['mp'] = min(player['mp'] + info['val'], player['max_mp'])
                    player['inventory'].append(item)
                    slow_print(c(f"  ✅ Bought {item}! MP +{info['val']}", GREEN))
                time.sleep(0.7)
        except (ValueError, IndexError):
            slow_print(c("  ❓ Invalid choice.", DIM)); time.sleep(0.5)
    return player

# ─── STATS SCREEN ─────────────────────────────────────────
def show_stats(player):
    clear()
    print(box(f"  📊 {player['name'].upper()} — {player['class'].upper()}  "))
    print(f"\n  {CYAN}Level{R}     {BOLD}{player['level']}{R}")
    print(f"  {GREEN}HP{R}        {hp_bar(player['hp'], player['max_hp'])}")
    print(f"  {BLUE}MP{R}        {hp_bar(player['mp'], player['max_mp'])}")
    print(f"  {CYAN}XP{R}        {xp_bar(player['xp'], player['level'])}")
    print()
    print(f"  {YELLOW}⚔️  ATK{R}    {player['atk']}    {YELLOW}🛡️  DEF{R}    {player['def']}")
    print(f"  {YELLOW}💰 Gold{R}   {player['gold']}    {YELLOW}💀 Kills{R}  {player['kills']}")
    print()
    print(f"  {BOLD}Inventory:{R} {', '.join(player['inventory']) if player['inventory'] else 'Empty'}")
    print(f"  {BOLD}Visited:{R}   {len(player['visited'])}/{len(ROOMS)} rooms")
    print()
    input(f"  {DIM}Press Enter to continue...{R}")

# ─── TITLE SCREEN ─────────────────────────────────────────
def title_screen():
    clear()
    print(c(f"""
╔{'═'*58}╗
║{'':58}║
║{'  ████████╗ ███████╗ ██████╗  ███╗   ███╗ ██╗ ███╗   ██╗':58}║
║{'  ╚══██╔══╝ ██╔════╝ ██╔══██╗ ████╗ ████║ ██║ ████╗  ██║':58}║
║{'     ██║    █████╗   ██████╔╝ ██╔████╔██║ ██║ ██╔██╗ ██║':58}║
║{'     ██║    ██╔══╝   ██╔══██╗ ██║╚██╔╝██║ ██║ ██║╚██╗██║':58}║
║{'     ██║    ███████╗ ██║  ██║ ██║ ╚═╝ ██║ ██║ ██║ ╚████║':58}║
║{'     ╚═╝    ╚══════╝ ╚═╝  ╚═╝ ╚═╝     ╚═╝ ╚═╝ ╚═╝  ╚═══╝':58}║
║{'':58}║
║{'        ⚔️   Q U E S T   ⚔️          v2.0':58}║
║{'':58}║
║{'    A text RPG by Ishaan Sharma  |  Hack Club Macondo':58}║
║{'':58}║
╚{'═'*58}╝
""", CYAN))
    saved = load_game()
    if saved:
        print(f"  {GREEN}[N]{R} New Game    {CYAN}[L]{R} Load Game ({saved['name']} Lv{saved['level']})    {RED}[Q]{R} Quit\n")
    else:
        print(f"  {GREEN}[N]{R} New Game    {RED}[Q]{R} Quit\n")
    ch = input(f"  {CYAN}>{R} ").strip().lower()
    if ch == 'q': sys.exit()
    if ch == 'l' and saved: return saved
    return new_game()

# ─── MAIN GAME LOOP ───────────────────────────────────────
def main():
    player = title_screen()

    while True:
        clear()
        room = ROOMS[player['location']]
        if player['location'] not in player['visited']:
            player['visited'].append(player['location'])
        player['steps'] += 1

        # Room header
        print(box(f"  {room['name']}  "))
        print()
        slow_print(wrap(room['desc']), 0.008)
        print()

        # Status bar
        divider()
        print(f"  ❤️  {hp_bar(player['hp'], player['max_hp'], 14)}  💫 MP:{player['mp']}  💰{player['gold']}g  ⭐Lv{player['level']}")
        divider()

        # Build exits
        exits_list = []
        for direction, dest in room['exits'].items():
            exits_list.append(f"{c('['+direction[0].upper()+']', CYAN)} {direction.capitalize()}")
        print(f"\n  📍 Exits: {' '.join(exits_list)}")

        # Available actions
        print(f"\n  {c('[i]',YELLOW)} Stats    {c('[s]',GREEN)} Save    {c('[q]',RED)} Quit")
        if 'enemies' in room:    print(f"  {c('[f]',RED)} Fight enemy (rate: {int(room['encounter_rate']*100)}%)")
        if 'shop'    in room:    print(f"  {c('[b]',YELLOW)} Enter shop")
        if 'boss'    in room and not player.get('boss_defeated'): print(f"  {c('[boss]',BRED)} ⚠️  FIGHT THE BOSS")
        if 'item'    in room and not room['item']['collected']: print(f"  {c('[g]',MAGENTA)} Grab: {room['item']['name']}")
        if 'item'    in room and 'stat' in room['item'] and not room['item']['collected']: print(f"      └ {room['item']['desc']}")

        print()
        cmd = input(f"  {CYAN}>{R} ").strip().lower()

        if cmd == 'q':
            save_game(player)
            slow_print(c("  👋 Farewell, adventurer!", CYAN))
            break

        elif cmd == 's':
            save_game(player)
            time.sleep(0.8)

        elif cmd == 'i':
            show_stats(player)

        elif cmd == 'f' and 'enemies' in room:
            enemy = random.choice(room['enemies'])
            player, won = combat(player, enemy)
            input(f"\n  {DIM}Press Enter to continue...{R}")

        elif cmd == 'b' and 'shop' in room:
            player = shop(player, room['shop'])

        elif cmd == 'boss' and 'boss' in room and not player.get('boss_defeated'):
            print()
            slow_print(c("  🔥 The earth trembles... The Dragon awakens!", RED), 0.03)
            time.sleep(0.8)
            player, won = combat(player, room['boss'], is_boss=True)
            if won:
                player['boss_defeated'] = True
                print()
                slow_print(c("  🎉 THE DRAGON IS DEFEATED!", YELLOW), 0.04)
                slow_print(c("  ✨ You are the champion of TerminalQuest!", GREEN), 0.03)
                slow_print(f"  Final stats: Lv{player['level']} | {player['kills']} kills | {player['steps']} steps | {player['gold']}g")
                save_game(player)
                input(f"\n  {DIM}Press Enter to exit...{R}")
                break
            input(f"\n  {DIM}Press Enter to continue...{R}")

        elif cmd == 'g' and 'item' in room and not room['item']['collected']:
            item = room['item']
            item['collected'] = True
            player['gold'] += item.get('gold', 0)
            if 'stat' in item:
                player[item['stat']] += item['val']
                slow_print(c(f"  ✨ Used {item['name']}! {item['stat'].upper()} +{item['val']}", MAGENTA))
            else:
                slow_print(c(f"  🎒 Picked up {item['name']}!", CYAN))
                if item.get('gold', 0):
                    slow_print(c(f"  💰 Sold for {item['gold']} gold!", YELLOW))
            time.sleep(0.9)

        elif len(cmd) == 1:
            moved = False
            for direction, dest in room['exits'].items():
                if cmd == direction[0]:
                    player['location'] = dest
                    moved = True
                    # Random encounter on move
                    new_room = ROOMS[dest]
                    if new_room.get('encounter_rate', 0) > 0 and 'enemies' in new_room:
                        if random.random() < new_room['encounter_rate'] * 0.4:
                            time.sleep(0.3)
                            enemy = random.choice(new_room['enemies'])
                            slow_print(c(f"\n  ⚠️  Ambushed by a {enemy['name']}!", RED))
                            time.sleep(0.6)
                            player, _ = combat(player, enemy)
                            input(f"\n  {DIM}Press Enter to continue...{R}")
                    break
            if not moved:
                slow_print(c("  ❓ Can't go that way.", DIM))
                time.sleep(0.5)
        else:
            slow_print(c("  ❓ Unknown command.", DIM))
            time.sleep(0.4)

if __name__ == "__main__":
    main()

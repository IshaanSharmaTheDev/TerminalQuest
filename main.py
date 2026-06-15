#!/usr/bin/env python3
"""
TerminalQuest v3.0
A fully-featured terminal RPG with 10 zones, 4 classes, crafting, quests, skills, and more.
Built for Macondo / Hack Club by Ishaan Sharma
"""
import json, os, random, sys, time, textwrap, math, copy

SAVE_FILE = "save.json"
VERSION   = "3.0"
WIDTH     = 64

# ─── ANSI ──────────────────────────────────────────────────────
R='\033[0m'; BOLD='\033[1m'; DIM='\033[2m'; ITALIC='\033[3m'
UL='\033[4m'
RED='\033[91m'; GREEN='\033[92m'; YELLOW='\033[93m'
BLUE='\033[94m'; MAGENTA='\033[95m'; CYAN='\033[96m'; WHITE='\033[97m'
DRED='\033[31m'; DGREEN='\033[32m'; DYELLOW='\033[33m'; DBLUE='\033[34m'
BGRED='\033[41m'; BGGREEN='\033[42m'; BGYELLOW='\033[43m'; BGBLUE='\033[44m'
BGMAGENTA='\033[45m'; BGCYAN='\033[46m'

def col(text, color): return f"{color}{text}{R}"
def bold(text): return f"{BOLD}{text}{R}"
def dim(text):  return f"{DIM}{text}{R}"

# ─── UI HELPERS ────────────────────────────────────────────────
def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def slow_print(text, delay=0.016):
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()

def instant(text): print(text)

def wrap_print(text, indent=3, delay=0.010):
    lines = textwrap.wrap(text, WIDTH - indent)
    for line in lines:
        slow_print(' ' * indent + line, delay)

def divider(char='─', color=DIM): print(col(char * WIDTH, color))

def header(title, char='═', color=CYAN):
    w = WIDTH
    t = f"  {title}  "
    pad = max(0, w - 2 - len(t))
    lp = pad // 2; rp = pad - lp
    print(col(f"╔{char*( w-2)}╗", color))
    print(col("║", color) + " " + col(t, BOLD + color[:-1] if color else BOLD) + " " * (w-3-len(t)) + col("║", color))
    print(col(f"╚{char*(w-2)}╝", color))

def box_line(text, color=DIM):
    pad = WIDTH - 4 - len(text)
    return col("│ ", color) + text + " " * max(0, pad) + col(" │", color)

def hp_bar(cur, mx, width=18, label="HP"):
    pct = cur / mx if mx else 0
    filled = int(pct * width)
    clr = GREEN if pct > 0.6 else YELLOW if pct > 0.3 else RED
    bar = col('█' * filled, clr) + col('░' * (width - filled), DIM)
    return f"{col(label, clr)} [{bar}] {col(str(cur), clr)}/{mx}"

def mp_bar(cur, mx, width=12):
    pct = cur / mx if mx else 0
    filled = int(pct * width)
    bar = col('▓' * filled, BLUE) + col('░' * (width - filled), DIM)
    return f"{col('MP', BLUE)} [{bar}] {cur}/{mx}"

def xp_bar(xp, needed, width=16):
    pct = min(xp / needed, 1.0) if needed else 1.0
    filled = int(pct * width)
    bar = col('▒' * filled, CYAN) + col('░' * (width - filled), DIM)
    return f"{col('XP', CYAN)} [{bar}] {xp}/{needed}"

def pause(msg="Press Enter to continue..."): input(col(f"\n  {msg}", DIM))

def pick(prompt, choices):
    while True:
        ch = input(col(f"  {prompt} > ", CYAN)).strip().lower()
        if ch in choices:
            return ch
        print(col("  ❓ Invalid.", DIM))

# ─── WORLD DATA ────────────────────────────────────────────────
ROOMS = {
    "forest_entrance": {
        "name": "🌲 Whispering Forest — Entrance",
        "desc": "Dappled sunlight filters through ancient oaks. A weathered signpost points north to Thornwick Village. Strange runes are carved into the bark of the nearest tree.",
        "exits": {"north": "village", "east": "forest_deep", "south": "meadow"},
        "enemies": [
            {"name": "Dire Wolf",    "hp": 30, "max_hp": 30, "atk": 7,  "def": 2, "spd": 8,  "xp": 14, "gold": 8,  "emoji": "🐺", "skills": ["bite"]},
            {"name": "Goblin Scout", "hp": 24, "max_hp": 24, "atk": 6,  "def": 1, "spd": 10, "xp": 9,  "gold": 6,  "emoji": "👺", "skills": ["stab"]},
            {"name": "Giant Rat",    "hp": 18, "max_hp": 18, "atk": 4,  "def": 0, "spd": 12, "xp": 5,  "gold": 3,  "emoji": "🐀", "skills": []},
        ],
        "encounter_rate": 0.50,
        "ambient": ["A distant wolf howl echoes through the trees.", "Something rustles in the underbrush.", "An owl watches you silently from a branch above."],
        "loot_table": ["Iron Ore", "Wolf Pelt", "Goblin Ear"],
    },
    "forest_deep": {
        "name": "🌑 Deep Forest — Heart of Thorns",
        "desc": "The canopy closes overhead, blocking all sunlight. Gnarled roots claw at your boots. The air smells of rot and something older. You feel watched.",
        "exits": {"west": "forest_entrance", "north": "cave_mouth", "down": "underground_river"},
        "enemies": [
            {"name": "Shadow Stalker","hp": 42, "max_hp": 42, "atk": 12, "def": 3, "spd": 14, "xp": 22, "gold": 14, "emoji": "👤", "skills": ["shadowstep", "bite"]},
            {"name": "Venomfang",     "hp": 38, "max_hp": 38, "atk": 9,  "def": 2, "spd": 11, "xp": 18, "gold": 11, "emoji": "🐍", "skills": ["poison"]},
            {"name": "Treant Spawn",  "hp": 55, "max_hp": 55, "atk": 10, "def": 6, "spd": 4,  "xp": 28, "gold": 12, "emoji": "🌳", "skills": ["slam"]},
        ],
        "encounter_rate": 0.65,
        "ambient": ["You hear breathing that isn't yours.", "A branch snaps behind you.", "The shadows seem to shift and pulse."],
        "loot_table": ["Shadow Essence", "Venom Sac", "Ancient Bark"],
        "item": {"name": "📜 Forest Codex", "desc": "An ancient tome. Grants +5 ATK.", "stat": "atk", "val": 5, "collected": False},
    },
    "meadow": {
        "name": "🌸 Sunlit Meadow",
        "desc": "Rolling green hills dotted with wildflowers. A stream babbles nearby. This place feels peaceful — almost unnervingly so. You spot ruins on the eastern hill.",
        "exits": {"north": "forest_entrance", "east": "ruins", "west": "marshlands"},
        "enemies": [
            {"name": "Bandit",       "hp": 32, "max_hp": 32, "atk": 8,  "def": 3, "spd": 7, "xp": 16, "gold": 20, "emoji": "🥷", "skills": ["stab", "steal"]},
            {"name": "Feral Boar",   "hp": 28, "max_hp": 28, "atk": 9,  "def": 2, "spd": 9, "xp": 12, "gold": 5,  "emoji": "🐗", "skills": ["charge"]},
        ],
        "encounter_rate": 0.40,
        "ambient": ["Butterflies dance across your path.", "The stream nearby sounds peaceful.", "Distant thunder rumbles on the horizon."],
        "loot_table": ["Wild Herb", "Bandit Coin", "Boar Tusk"],
        "item": {"name": "🌿 Healing Root", "desc": "Restore 50 HP when used.", "stat": "heal", "val": 50, "collected": False},
    },
    "village": {
        "name": "🏘️  Thornwick Village",
        "desc": "Cobblestone streets wind between timber-framed houses. A blacksmith hammers iron, an alchemist hangs herbs to dry. The inn's warm light spills across the square. Pop. 47 says the sign.",
        "exits": {"south": "forest_entrance", "east": "dungeon_gate", "north": "church", "west": "market"},
        "encounter_rate": 0,
        "shop": {
            "Iron Sword":      {"price": 45,  "stat": "atk", "val": 8,  "emoji": "⚔️ ",  "desc": "A well-balanced iron blade. Reliable in a fight."},
            "Steel Sword":     {"price": 120, "stat": "atk", "val": 18, "emoji": "🗡️ ",  "desc": "Tempered steel. Holds a razor edge."},
            "Leather Armor":   {"price": 35,  "stat": "def", "val": 5,  "emoji": "🥋",   "desc": "Lightweight protection. Better than nothing."},
            "Chain Mail":      {"price": 90,  "stat": "def", "val": 12, "emoji": "🛡️ ",  "desc": "Interlocking rings of steel. Solid protection."},
            "Health Potion":   {"price": 15,  "stat": "heal","val": 40, "emoji": "🧪",   "desc": "Red liquid that smells of copper. Restores 40 HP."},
            "Mega Potion":     {"price": 40,  "stat": "heal","val": 100,"emoji": "💊",   "desc": "Concentrated healing. Restores 100 HP."},
            "Mana Crystal":    {"price": 25,  "stat": "mp",  "val": 30, "emoji": "💎",   "desc": "A cold blue shard. Restores 30 MP."},
            "Antidote":        {"price": 12,  "stat": "cure","val": 1,  "emoji": "💉",   "desc": "Cures poison status."},
            "Smoke Bomb":      {"price": 20,  "stat": "flee","val": 1,  "emoji": "💨",   "desc": "Guarantees escape from any fight."},
        },
        "ambient": ["Children chase chickens through the square.", "The blacksmith wipes sweat from his brow.", "Laughter drifts from the inn."],
    },
    "market": {
        "name": "🛒 Thornwick Market District",
        "desc": "Canvas awnings shade rows of stalls selling everything from salted fish to enchanted trinkets. A hooded merchant eyes you from the shadows.",
        "exits": {"east": "village"},
        "encounter_rate": 0,
        "black_market": {
            "Elixir of Might":   {"price": 200, "stat": "atk", "val": 10, "emoji": "🔴", "desc": "Permanently increases ATK by 10. No questions asked."},
            "Stone Skin Brew":   {"price": 180, "stat": "def", "val": 8,  "emoji": "🟤", "desc": "Permanently increases DEF by 8."},
            "Dragon Blood Vial": {"price": 350, "stat": "max_hp","val":50,"emoji": "🩸", "desc": "Permanently increases max HP by 50."},
            "Arcane Tome":       {"price": 250, "stat": "max_mp","val":50,"emoji": "📙", "desc": "Permanently increases max MP by 50."},
        },
        "ambient": ["A cat watches from atop a vegetable cart.", "Someone whispers a price in your ear.", "The market smells of spice and iron."],
    },
    "church": {
        "name": "⛪ Church of the Ember Flame",
        "desc": "Stained glass filters colored light across stone pews. A priest in ash-gray robes tends to a row of candles. A donation box sits near the altar. The air smells of incense.",
        "exits": {"south": "village"},
        "encounter_rate": 0,
        "healing": True,
        "ambient": ["Soft chanting echoes from the vestry.", "The candles flicker as you enter.", "The priest nods solemnly as you approach."],
    },
    "cave_mouth": {
        "name": "🕳️  Echoing Cave — Mouth",
        "desc": "The cave breathes cold air like a sleeping beast. Phosphorescent fungi line the walls in faint blue rings. Your footsteps echo into a darkness that doesn't echo back.",
        "exits": {"south": "forest_deep", "north": "cave_depths", "east": "mine_shaft"},
        "enemies": [
            {"name": "Cave Troll",    "hp": 55, "max_hp": 55, "atk": 12, "def": 5,  "spd": 5, "xp": 30, "gold": 18, "emoji": "👹", "skills": ["slam", "roar"]},
            {"name": "Giant Spider",  "hp": 40, "max_hp": 40, "atk": 10, "def": 2,  "spd": 9, "xp": 20, "gold": 12, "emoji": "🕷️ ", "skills": ["poison", "web"]},
            {"name": "Cave Bat",      "hp": 22, "max_hp": 22, "atk": 7,  "def": 1,  "spd": 15,"xp": 10, "gold": 5,  "emoji": "🦇", "skills": []},
        ],
        "encounter_rate": 0.60,
        "ambient": ["Water drips in the darkness.", "Your torch casts dancing shadows.", "Something skitters along the ceiling."],
        "loot_table": ["Cave Crystal", "Spider Silk", "Bat Wing"],
        "item": {"name": "🔮 Arcane Gem", "desc": "Pulses with cold energy. Worth 80 gold.", "gold": 80, "collected": False},
    },
    "cave_depths": {
        "name": "🌋 Cave Depths — The Magma Vein",
        "desc": "The cave opens into a vast underground chamber. Rivers of lava cast everything in hellish orange. The heat is intense. Something enormous shifts in the shadows ahead.",
        "exits": {"south": "cave_mouth", "down": "underground_river", "east": "dungeon_gate"},
        "enemies": [
            {"name": "Lava Elemental","hp": 75, "max_hp": 75, "atk": 18, "def": 6, "spd": 6,  "xp": 45, "gold": 30, "emoji": "🔥", "skills": ["burn", "slam"]},
            {"name": "Obsidian Golem","hp": 90, "max_hp": 90, "atk": 15, "def": 12,"spd": 3,  "xp": 50, "gold": 35, "emoji": "🗿", "skills": ["slam", "roar"]},
            {"name": "Fire Wyrm",     "hp": 65, "max_hp": 65, "atk": 20, "def": 4, "spd": 10, "xp": 40, "gold": 28, "emoji": "🐲", "skills": ["burn", "bite"]},
        ],
        "encounter_rate": 0.70,
        "ambient": ["The lava pops and hisses.", "Waves of heat wash over you.", "A deep rumble shakes the stone beneath your feet."],
        "loot_table": ["Magma Core", "Obsidian Shard", "Fire Scale"],
        "item": {"name": "💎 Magma Heart", "desc": "Grants +8 ATK when absorbed.", "stat": "atk", "val": 8, "collected": False},
    },
    "ruins": {
        "name": "🏛️  Ruins of Aeldrath",
        "desc": "Crumbling stone arches rise from the hillside. Inscriptions in a forgotten tongue spiral up the columns. A shattered altar glows faintly at the center. The air hums with residual magic.",
        "exits": {"west": "meadow", "north": "dungeon_gate", "down": "crypt"},
        "enemies": [
            {"name": "Shade",         "hp": 50, "max_hp": 50, "atk": 15, "def": 3, "spd": 11, "xp": 30, "gold": 20, "emoji": "👻", "skills": ["drain", "shadowstep"]},
            {"name": "Bone Archer",   "hp": 38, "max_hp": 38, "atk": 12, "def": 2, "spd": 9,  "xp": 22, "gold": 14, "emoji": "💀", "skills": ["stab"]},
            {"name": "Cursed Knight", "hp": 65, "max_hp": 65, "atk": 17, "def": 8, "spd": 7,  "xp": 38, "gold": 25, "emoji": "⚔️ ", "skills": ["slam", "shield_bash"]},
        ],
        "encounter_rate": 0.65,
        "ambient": ["Wind whispers through the stone arches.", "The altar flickers with pale fire.", "A ghostly shape drifts between columns."],
        "loot_table": ["Soul Fragment", "Ancient Coin", "Cursed Bone"],
        "item": {"name": "📜 Ancient Scroll", "desc": "Grants +5 ATK and +10 max MP.", "stat": "multi", "atk": 5, "max_mp": 10, "collected": False},
    },
    "marshlands": {
        "name": "🌿 Bogmire Marshlands",
        "desc": "Black water gurgles underfoot. Will-o-wisps dance just out of reach above the fog. Every step sucks at your boots. Strange herbs grow from the mud in dense clusters.",
        "exits": {"east": "meadow", "north": "underground_river"},
        "enemies": [
            {"name": "Bog Witch",    "hp": 50, "max_hp": 50, "atk": 16, "def": 2, "spd": 8, "xp": 28, "gold": 22, "emoji": "🧙", "skills": ["poison", "curse"]},
            {"name": "Slime Beast",  "hp": 35, "max_hp": 35, "atk": 8,  "def": 6, "spd": 5, "xp": 16, "gold": 9,  "emoji": "🫧", "skills": ["slam"]},
            {"name": "Marsh Leech",  "hp": 25, "max_hp": 25, "atk": 6,  "def": 1, "spd": 7, "xp": 10, "gold": 4,  "emoji": "🪱", "skills": ["drain"]},
        ],
        "encounter_rate": 0.70,
        "ambient": ["Something splashes nearby.", "The mist thickens around your knees.", "A wisp drifts close then darts away."],
        "loot_table": ["Witch Herb", "Slime Gel", "Marsh Reed"],
        "item": {"name": "🌿 Witch's Reagent", "desc": "Worth 70 gold. Rare alchemical ingredient.", "gold": 70, "collected": False},
    },
    "mine_shaft": {
        "name": "⛏️  Abandoned Mine — Shaft 7",
        "desc": "Collapsed timbers. Rusted carts on cracked rails. The walls are riddled with tunnels — something has been digging here, something much larger than a miner.",
        "exits": {"west": "cave_mouth", "down": "underground_river", "east": "dungeon_gate"},
        "enemies": [
            {"name": "Rock Golem",   "hp": 70, "max_hp": 70, "atk": 16, "def": 10, "spd": 3, "xp": 40, "gold": 28, "emoji": "🗿", "skills": ["slam", "roar"]},
            {"name": "Cave Beetle",  "hp": 28, "max_hp": 28, "atk": 9,  "def": 4,  "spd": 6, "xp": 14, "gold": 7,  "emoji": "🪲", "skills": ["charge"]},
            {"name": "Miner's Ghost","hp": 42, "max_hp": 42, "atk": 11, "def": 1,  "spd": 9, "xp": 24, "gold": 15, "emoji": "👻", "skills": ["drain", "curse"]},
        ],
        "encounter_rate": 0.60,
        "ambient": ["Pick-axe sounds echo from deep within.", "A support beam groans overhead.", "Rats scatter from your torchlight."],
        "loot_table": ["Iron Ore", "Coal Chunk", "Adamant Ore"],
        "item": {"name": "💎 Adamant Ore", "desc": "Rare metal. Grants +6 DEF when forged.", "stat": "def", "val": 6, "collected": False},
    },
    "underground_river": {
        "name": "🌊 Underground River — The Darkflow",
        "desc": "A black river rushes through a vast underground cavern. Stone bridges span its width. The current is violent and loud. Glowing fish dart beneath the surface.",
        "exits": {"up": "forest_deep", "north": "crypt", "east": "cave_depths", "south": "marshlands", "west": "mine_shaft"},
        "enemies": [
            {"name": "River Serpent", "hp": 60, "max_hp": 60, "atk": 14, "def": 4, "spd": 12, "xp": 35, "gold": 22, "emoji": "🐍", "skills": ["poison", "bite"]},
            {"name": "Deep Crawler",  "hp": 45, "max_hp": 45, "atk": 11, "def": 5, "spd": 8,  "xp": 26, "gold": 16, "emoji": "🦀", "skills": ["slam", "web"]},
        ],
        "encounter_rate": 0.55,
        "ambient": ["The river roars in the darkness.", "A glowing fish surfaces then vanishes.", "The bridge sways under your weight."],
        "loot_table": ["River Stone", "Deep Coral", "Glowfish Scale"],
        "item": {"name": "💧 Deepflow Crystal", "desc": "Grants +20 max MP.", "stat": "max_mp", "val": 20, "collected": False},
    },
    "crypt": {
        "name": "🪦 Crypt of the Fallen Kings",
        "desc": "Stone sarcophagi line the walls. Faded crests mark kings long dead. The air is thick with preserving magic and the silence is absolute. At the far end, a door of blackened iron leads deeper.",
        "exits": {"up": "ruins", "south": "underground_river", "north": "dungeon_gate"},
        "enemies": [
            {"name": "Lich Apprentice","hp": 65, "max_hp": 65, "atk": 20, "def": 5, "spd": 10, "xp": 42, "gold": 30, "emoji": "💀", "skills": ["drain", "curse", "shadowstep"]},
            {"name": "King's Revenant","hp": 80, "max_hp": 80, "atk": 18, "def": 9, "spd": 6,  "xp": 48, "gold": 35, "emoji": "👑", "skills": ["slam", "shield_bash", "roar"]},
            {"name": "Soul Spectre",   "hp": 50, "max_hp": 50, "atk": 16, "def": 2, "spd": 14, "xp": 36, "gold": 22, "emoji": "👻", "skills": ["drain", "curse"]},
        ],
        "encounter_rate": 0.68,
        "ambient": ["A sarcophagus lid grinds against stone.", "The torches flicker in unison.", "Whispers fill the air without any source."],
        "loot_table": ["King's Sigil", "Death Shard", "Bone Dust"],
        "item": {"name": "👑 Crown Shard", "desc": "A fragment of an ancient crown. Grants +15 ATK and +15 DEF.", "stat": "multi", "atk": 15, "def": 15, "collected": False},
    },
    "dungeon_gate": {
        "name": "🏰 Dungeon Gate — Threshold of Ashenmoor",
        "desc": "Massive iron gates stand half-open, bent by some ancient force. Beyond is darkness punctuated by the distant sound of wings and fire. The air shimmers with heat.",
        "exits": {"west": "village", "south": "ruins", "northwest": "cave_depths", "northeast": "crypt", "east": "dungeon_throne"},
        "enemies": [
            {"name": "Gate Warden",   "hp": 90, "max_hp": 90, "atk": 22, "def": 12, "spd": 7, "xp": 55, "gold": 40, "emoji": "🗡️ ", "skills": ["slam", "shield_bash", "roar"]},
            {"name": "Hell Hound",    "hp": 65, "max_hp": 65, "atk": 19, "def": 5,  "spd": 13,"xp": 42, "gold": 28, "emoji": "🐕", "skills": ["burn", "bite", "charge"]},
        ],
        "encounter_rate": 0.55,
        "ambient": ["The gates groan in an unfelt wind.", "Distant roaring shakes the walls.", "Your shadow bends toward the darkness ahead."],
        "loot_table": ["Warden's Badge", "Hell Fang", "Scorched Bone"],
    },
    "dungeon_throne": {
        "name": "🔥 Throne Room of the Inferno Dragon",
        "desc": "The ceiling is lost in smoke and flame. A throne of melted swords rises at the far end. Charred bones litter the floor. The Inferno Dragon coils around the throne, one enormous eye opening to fix you with a gaze like a furnace door.",
        "exits": {"west": "dungeon_gate"},
        "boss": {
            "name": "Inferno Dragon", "hp": 200, "max_hp": 200,
            "atk": 30, "def": 12, "spd": 9, "xp": 500, "gold": 500,
            "emoji": "🐉",
            "skills": ["firebreath", "slam", "roar", "burn", "charge"],
            "phases": [
                {"threshold": 0.66, "msg": "The Dragon rears up and breathes a column of white-hot fire!", "atk_boost": 5},
                {"threshold": 0.33, "msg": "🔥 ENRAGED! The Dragon's scales glow molten red!", "atk_boost": 10},
            ]
        },
        "encounter_rate": 0,
        "ambient": ["The heat is almost unbearable.", "The Dragon's eyes track your every movement.", "The ground beneath you is warm."],
    },
}

# ─── ENEMY SKILLS ──────────────────────────────────────────────
ENEMY_SKILLS = {
    "bite":       {"dmg_mult": 1.3, "msg": "sinks its teeth into you", "effect": None},
    "stab":       {"dmg_mult": 1.4, "msg": "drives a blade between your ribs", "effect": None},
    "slam":       {"dmg_mult": 1.5, "msg": "slams into you with full force", "effect": None},
    "charge":     {"dmg_mult": 1.6, "msg": "charges headlong into you", "effect": None},
    "poison":     {"dmg_mult": 0.8, "msg": "spits venom at you", "effect": "poison"},
    "burn":       {"dmg_mult": 0.9, "msg": "breathes fire across you", "effect": "burn"},
    "drain":      {"dmg_mult": 0.7, "msg": "drains your life force", "effect": "drain"},
    "curse":      {"dmg_mult": 0.5, "msg": "lays a weakening curse on you", "effect": "curse"},
    "shadowstep": {"dmg_mult": 1.8, "msg": "teleports behind you and strikes", "effect": None},
    "roar":       {"dmg_mult": 0.0, "msg": "lets out a terrifying roar — you flinch!", "effect": "stun"},
    "web":        {"dmg_mult": 0.3, "msg": "snares you in sticky webbing", "effect": "slow"},
    "shield_bash":{"dmg_mult": 1.2, "msg": "bashes you with a heavy shield", "effect": "stun"},
    "firebreath": {"dmg_mult": 2.0, "msg": "exhales a torrent of dragon fire", "effect": "burn"},
    "steal":      {"dmg_mult": 0.5, "msg": "snatches gold from your belt", "effect": "steal"},
}

# ─── STATUS EFFECTS ────────────────────────────────────────────
STATUS_EFFECTS = {
    "poison": {"color": GREEN,   "msg": "☠️  Poison",  "dot": 8,  "duration": 3},
    "burn":   {"color": RED,     "msg": "🔥 Burn",    "dot": 12, "duration": 2},
    "drain":  {"color": MAGENTA, "msg": "🩸 Drain",   "dot": 6,  "duration": 4},
    "curse":  {"color": MAGENTA, "msg": "💜 Curse",   "dot": 0,  "duration": 3, "atk_reduce": 5},
    "stun":   {"color": YELLOW,  "msg": "⚡ Stun",    "dot": 0,  "duration": 1},
    "slow":   {"color": CYAN,    "msg": "🕸️  Slow",   "dot": 0,  "duration": 2},
}

# ─── PLAYER CLASSES ────────────────────────────────────────────
CLASSES = {
    "Warrior": {
        "desc": "Tank class. High HP and DEF. Special: Whirlwind (hits all enemies).",
        "hp": 150, "mp": 20, "atk": 16, "def": 7, "spd": 6,
        "special": "whirlwind", "special_mp": 15,
        "passive": "Iron Will: 15% chance to ignore damage",
        "level_bonuses": {"hp": 20, "mp": 5,  "atk": 2, "def": 2, "spd": 0},
    },
    "Rogue": {
        "desc": "Glass cannon. Highest ATK and SPD. Special: Backstab (3x crit chance).",
        "hp": 100, "mp": 25, "atk": 22, "def": 2, "spd": 16,
        "special": "backstab", "special_mp": 20,
        "passive": "Evasion: 20% chance to dodge attacks",
        "level_bonuses": {"hp": 10, "mp": 5,  "atk": 4, "def": 1, "spd": 1},
    },
    "Mage": {
        "desc": "Magic specialist. High MP and scaling magic damage. Special: Arcane Burst.",
        "hp": 100, "mp": 80, "atk": 12, "def": 3, "spd": 9,
        "special": "arcane_burst", "special_mp": 30,
        "passive": "Arcane Mastery: +50% magic damage",
        "level_bonuses": {"hp": 10, "mp": 20, "atk": 2, "def": 1, "spd": 1},
    },
    "Paladin": {
        "desc": "Holy warrior. Balanced stats, self-heals in combat. Special: Holy Strike.",
        "hp": 130, "mp": 50, "atk": 14, "def": 5, "spd": 7,
        "special": "holy_strike", "special_mp": 25,
        "passive": "Divine Favor: Heal 5 HP per combat turn",
        "level_bonuses": {"hp": 15, "mp": 10, "atk": 3, "def": 2, "spd": 0},
    },
}

# ─── SPELLS ────────────────────────────────────────────────────
SPELLS = {
    "Fireball":     {"mp": 25, "dmg": (30, 50), "effect": "burn",   "desc": "Hurls a ball of fire."},
    "Ice Lance":    {"mp": 20, "dmg": (25, 40), "effect": "slow",   "desc": "A shard of magical ice."},
    "Thunder Bolt": {"mp": 30, "dmg": (35, 55), "effect": "stun",   "desc": "Strikes with lightning."},
    "Drain Life":   {"mp": 20, "dmg": (20, 35), "effect": "drain",  "desc": "Steal enemy HP.", "heal": True},
    "Holy Light":   {"mp": 25, "dmg": (0,  0),  "effect": None,     "desc": "Restore 50 HP.", "self_heal": 50},
    "Poison Cloud": {"mp": 20, "dmg": (10, 20), "effect": "poison", "desc": "Clouds the area in venom."},
}

# ─── CRAFTING ──────────────────────────────────────────────────
RECIPES = {
    "Health Potion":  {"ingredients": {"Wild Herb": 2, "River Stone": 1},         "result_desc": "Restores 40 HP"},
    "Mega Potion":    {"ingredients": {"Wild Herb": 3, "Cave Crystal": 2},         "result_desc": "Restores 100 HP"},
    "Antidote":       {"ingredients": {"Witch Herb": 1, "Slime Gel": 1},           "result_desc": "Cures poison"},
    "Iron Sword":     {"ingredients": {"Iron Ore": 3, "Coal Chunk": 1},            "result_desc": "+8 ATK weapon"},
    "Steel Sword":    {"ingredients": {"Iron Ore": 5, "Adamant Ore": 2},           "result_desc": "+18 ATK weapon"},
    "Smoke Bomb":     {"ingredients": {"Shadow Essence": 2, "Coal Chunk": 1},      "result_desc": "Guarantees escape"},
    "Mana Crystal":   {"ingredients": {"Cave Crystal": 2, "Glowfish Scale": 1},    "result_desc": "Restores 30 MP"},
    "Arcane Scroll":  {"ingredients": {"Ancient Bark": 2, "Soul Fragment": 1},     "result_desc": "+10 ATK permanent"},
}

# ─── QUESTS ────────────────────────────────────────────────────
QUESTS = {
    "q_wolf_hunt": {
        "name": "Wolf Hunt",
        "desc": "The village elder asks you to slay 3 Dire Wolves terrorizing the farms.",
        "target": "Dire Wolf", "count": 3, "reward_gold": 80, "reward_xp": 50,
        "status": "inactive",
    },
    "q_herb_gather": {
        "name": "Herb Gathering",
        "desc": "The alchemist needs 2 Wild Herbs and 1 Witch Herb for a healing potion batch.",
        "items": {"Wild Herb": 2, "Witch Herb": 1}, "reward_gold": 60, "reward_xp": 40,
        "status": "inactive",
    },
    "q_lost_ore": {
        "name": "The Lost Ore",
        "desc": "A miner's ghost whispers of a cache of Adamant Ore in the mine. Retrieve it.",
        "items": {"Adamant Ore": 1}, "reward_gold": 120, "reward_xp": 80,
        "status": "inactive",
    },
    "q_slay_dragon": {
        "name": "Dragonslayer",
        "desc": "Defeat the Inferno Dragon and save Thornwick forever.",
        "target": "Inferno Dragon", "count": 1, "reward_gold": 1000, "reward_xp": 1000,
        "status": "active",
    },
}

# ─── TITLE SCREEN ──────────────────────────────────────────────
def title_screen():
    clear()
    print(col(r"""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║  ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗ ║
║     ██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║ ║
║     ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║ ║
║     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║ ║
║     ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗ ║
║     ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝ ║
║                                                                ║
║          ⚔️   Q U E S T      v3.0   ⚔️                        ║
║                                                                ║
║   10 Zones · 4 Classes · Crafting · Quests · Boss Fights      ║
║        Built for Macondo  |  Hack Club  |  Ishaan Sharma      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""", CYAN))
    saved = load_game()
    if saved:
        print(col(f"  Save found: {saved['name']} — {saved['class']} Lv{saved['level']} — {len(saved.get('visited',[]))}/14 zones visited", DIM))
    print()
    print(f"  {col('[N]', GREEN)} New Game    {col('[L]', CYAN)} Load Game    {col('[H]', YELLOW)} How to Play    {col('[Q]', RED)} Quit")
    print()
    ch = input(col("  > ", CYAN)).strip().lower()
    if ch == 'q': sys.exit()
    if ch == 'h': how_to_play(); return title_screen()
    if ch == 'l' and saved: return saved
    return new_game()

def how_to_play():
    clear()
    header("📖  HOW TO PLAY — TERMINALQUEST v3.0")
    print(f"""
  {bold('MOVEMENT')}
    Type the first letter of a direction: {col('n', CYAN)}orth, {col('s', CYAN)}outh, {col('e', CYAN)}ast, {col('w', CYAN)}est
    Some areas use {col('u', CYAN)}p / {col('d', CYAN)}own. Full words also work.

  {bold('COMMANDS')}
    {col('[f]', RED)}     Fight a random enemy in this area
    {col('[b]', YELLOW)}     Enter shop / black market
    {col('[g]', MAGENTA)}     Grab a collectible item
    {col('[i]', CYAN)}     View your stats sheet
    {col('[q_]', GREEN)}    Quest board (q_board)
    {col('[c]', YELLOW)}     Crafting menu
    {col('[spell]', BLUE)}  Cast a spell (mages/paladins)
    {col('[boss]', RED)}   Fight the final boss (dungeon only)
    {col('[rest]', GREEN)}  Rest at the church to heal
    {col('[s]', GREEN)}     Save game
    {col('[q]', RED)}     Save and quit

  {bold('COMBAT')}
    {col('[a]', GREEN)} Attack   {col('[m]', BLUE)} Magic   {col('[sp]', MAGENTA)} Special
    {col('[p]', CYAN)} Potion   {col('[r]', YELLOW)} Run     {col('[i]', DIM)} Inspect enemy

  {bold('STATUS EFFECTS')}
    Poison, Burn, Drain, Curse, Stun, Slow
    Use Antidote to cure poison/burn.

  {bold('CRAFTING')}
    Collect loot from battles. Open crafting menu to forge items.

  {bold('QUESTS')}
    Accept quests in the village. Track progress with q_board.
    Completing quests gives bonus gold and XP.
    """)
    pause()

# ─── CHARACTER CREATION ────────────────────────────────────────
def new_game():
    clear()
    header("⚔️   CREATE YOUR HERO")
    print()
    name = input(col("  Hero name: ", CYAN)).strip() or "Hero"
    print()
    print(f"  {bold('Choose your class:')}\n")
    for i, (cls, data) in enumerate(CLASSES.items(), 1):
        print(f"  {col(f'[{i}]', CYAN)} {bold(cls):<12} {col(data['desc'], DIM)}")
        print(f"      HP:{data['hp']}  MP:{data['mp']}  ATK:{data['atk']}  DEF:{data['def']}  SPD:{data['spd']}")
        print(f"      {col('Passive:', YELLOW)} {data['passive']}")
        print()
    ch = input(col("  Choice [1-4]: ", CYAN)).strip()
    cls_map = {"1": "Warrior", "2": "Rogue", "3": "Mage", "4": "Paladin"}
    cls = cls_map.get(ch, "Warrior")
    data = CLASSES[cls]
    print()
    slow_print(col(f"  ✨ {name} the {cls} steps into the world...", GREEN))
    time.sleep(0.8)

    player = {
        "name": name, "class": cls,
        "hp": data["hp"], "max_hp": data["hp"],
        "mp": data["mp"], "max_mp": data["mp"],
        "atk": data["atk"], "def": data["def"], "spd": data["spd"],
        "gold": 20, "xp": 0, "level": 1,
        "kills": 0, "steps": 0, "total_damage": 0,
        "inventory": ["Rusty Sword", "Health Potion"],
        "materials": {},
        "status_effects": {},
        "spells": list(SPELLS.keys())[:3],
        "location": "forest_entrance",
        "visited": [],
        "quests": copy.deepcopy(QUESTS),
        "boss_defeated": False,
        "achievements": [],
    }
    return player

# ─── SAVE / LOAD ───────────────────────────────────────────────
def save_game(player):
    with open(SAVE_FILE, 'w') as f:
        json.dump(player, f, indent=2)
    print(col("  💾 Game saved!", GREEN)); time.sleep(0.5)

def load_game():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE) as f: return json.load(f)
        except: return None
    return None

# ─── COMBAT SYSTEM ─────────────────────────────────────────────
def apply_status(player, effect, source="enemy"):
    if effect and effect in STATUS_EFFECTS:
        player["status_effects"][effect] = STATUS_EFFECTS[effect]["duration"]

def tick_status(player):
    to_remove = []
    msgs = []
    for eff, turns in list(player["status_effects"].items()):
        se = STATUS_EFFECTS.get(eff, {})
        dot = se.get("dot", 0)
        if dot > 0:
            player["hp"] -= dot
            player["hp"] = max(0, player["hp"])
            msgs.append(col(f"  {se['msg']}: -{dot} HP", se.get("color", RED)))
        player["status_effects"][eff] = turns - 1
        if player["status_effects"][eff] <= 0:
            to_remove.append(eff)
    for e in to_remove:
        del player["status_effects"][e]
        msgs.append(col(f"  ✅ {e.capitalize()} wore off.", DIM))
    return msgs

def combat(player, enemy_template, is_boss=False):
    enemy = copy.deepcopy(enemy_template)
    enemy_status = {}
    phase_idx = 0
    phases = enemy.get("phases", [])

    print()
    if is_boss:
        print(col(f"╔{'═'*62}╗", RED))
        print(col(f"║  {'⚠️  BOSS FIGHT: ' + enemy['name'].upper():^58}  ║", RED + BOLD))
        print(col(f"╚{'═'*62}╝", RED))
    else:
        header(f"{enemy['emoji']}  ENCOUNTER: {enemy['name'].upper()}")
    time.sleep(0.4)

    turn = 0
    while player["hp"] > 0 and enemy["hp"] > 0:
        turn += 1

        # Boss phase check
        if is_boss and phase_idx < len(phases):
            phase = phases[phase_idx]
            if enemy["hp"] / enemy["max_hp"] <= phase["threshold"]:
                print()
                slow_print(col(f"  💥 {phase['msg']}", RED + BOLD), 0.025)
                enemy["atk"] += phase["atk_boost"]
                phase_idx += 1
                time.sleep(0.8)

        # Status ticks
        tick_msgs = tick_status(player)
        if tick_msgs:
            for m in tick_msgs: print(m)
        if player["hp"] <= 0:
            break

        # Paladin passive: divine favor
        if player["class"] == "Paladin" and turn % 2 == 0:
            player["hp"] = min(player["max_hp"], player["hp"] + 5)

        # Warrior passive: iron will (handled in damage calc)
        # Rogue passive: evasion (handled in damage calc)

        print()
        divider()
        print(f"  {col('YOU', GREEN):12} {hp_bar(player['hp'], player['max_hp'], 16)}")
        if player["status_effects"]:
            effs = "  ".join([col(STATUS_EFFECTS[e]["msg"], STATUS_EFFECTS[e]["color"]) for e in player["status_effects"]])
            print(f"  Status: {effs}")
        print(f"  {col(enemy['name'], RED):12} {hp_bar(enemy['hp'], enemy['max_hp'], 16)}")
        if enemy_status:
            effs = "  ".join([col(STATUS_EFFECTS[e]["msg"], STATUS_EFFECTS[e]["color"]) for e in enemy_status])
            print(f"  Enemy:  {effs}")
        print(f"  {col('MP', BLUE)}: {player['mp']}/{player['max_mp']}   {col('Turn', DIM)}: {turn}")
        divider()
        print(f"\n  {col('[a]', GREEN)} Attack   {col('[m]', BLUE)} Magic ({player['mp']} MP)   {col('[sp]', MAGENTA)} Special")
        print(f"  {col('[p]', CYAN)} Potion   {col('[r]', YELLOW)} Run    {col('[i]', DIM)} Inspect\n")
        action = input(col("  > ", CYAN)).strip().lower()

        player_acted = True
        if action == 'r':
            flee_chance = 0.4
            if "slow" in player["status_effects"]: flee_chance = 0.15
            if "Smoke Bomb" in player["inventory"]:
                player["inventory"].remove("Smoke Bomb"); flee_chance = 1.0
            if random.random() < flee_chance:
                slow_print(col("  💨 You escaped!", YELLOW)); return player, False
            else:
                slow_print(col("  ❌ Can't escape!", RED)); player_acted = False

        elif action == 'i':
            print(f"\n  {enemy['emoji']} {bold(enemy['name'])}")
            print(f"  HP: {enemy['hp']}/{enemy['max_hp']}   ATK: {enemy['atk']}   DEF: {enemy['def']}   SPD: {enemy['spd']}")
            print(f"  Skills: {', '.join(enemy.get('skills',[])) or 'None'}")
            pause()
            player_acted = False

        elif action == 'a':
            crit_chance = 0.15
            if player["class"] == "Rogue": crit_chance = 0.30
            base_dmg = random.randint(player["atk"] - 3, player["atk"] + 5)
            if "curse" in player["status_effects"]: base_dmg -= 5
            dmg = max(1, base_dmg - enemy["def"] // 3)
            crit = random.random() < crit_chance
            if crit: dmg = int(dmg * 1.8)
            enemy["hp"] -= dmg
            player["total_damage"] = player.get("total_damage", 0) + dmg
            line = f"  ⚔️  You deal {col(str(dmg) + ' dmg', GREEN)}"
            if crit: line += col("  ✨ CRITICAL!", YELLOW)
            slow_print(line)

        elif action == 'm':
            if not player.get("spells"):
                slow_print(col("  ❌ No spells known.", RED)); player_acted = False
            else:
                print(f"\n  {bold('Your spells:')}")
                sp_list = player["spells"]
                for si, sp in enumerate(sp_list, 1):
                    s = SPELLS[sp]
                    dmg_str = f"{s['dmg'][0]}-{s['dmg'][1]} dmg" if s["dmg"][1] > 0 else "utility"
                    print(f"  {col(f'[{si}]', CYAN)} {sp:<16} MP:{s['mp']}  {dmg_str}  {col(s['desc'], DIM)}")
                sc = input(col("  Spell # > ", CYAN)).strip()
                try:
                    sp_name = sp_list[int(sc)-1]
                    sp = SPELLS[sp_name]
                    if player["mp"] < sp["mp"]:
                        slow_print(col("  ❌ Not enough MP!", RED)); player_acted = False
                    else:
                        player["mp"] -= sp["mp"]
                        if sp.get("self_heal"):
                            player["hp"] = min(player["max_hp"], player["hp"] + sp["self_heal"])
                            slow_print(col(f"  ✨ {sp_name}: Restored {sp['self_heal']} HP!", GREEN))
                        elif sp["dmg"][1] > 0:
                            mult = 1.5 if player["class"] == "Mage" else 1.0
                            dmg = int(random.randint(*sp["dmg"]) * mult)
                            enemy["hp"] -= dmg
                            player["total_damage"] = player.get("total_damage", 0) + dmg
                            slow_print(col(f"  💫 {sp_name}: {dmg} dmg!", MAGENTA))
                            if sp.get("heal"):
                                heal = dmg // 3
                                player["hp"] = min(player["max_hp"], player["hp"] + heal)
                                slow_print(col(f"  🩸 Drained {heal} HP!", GREEN))
                            if sp["effect"]:
                                enemy_status[sp["effect"]] = STATUS_EFFECTS[sp["effect"]]["duration"]
                                slow_print(col(f"  ✨ {sp['effect'].capitalize()} applied!", YELLOW))
                except (ValueError, IndexError):
                    slow_print(col("  ❓ Invalid.", DIM)); player_acted = False

        elif action == 'sp':
            cls_data = CLASSES[player["class"]]
            sp_name = cls_data["special"]
            sp_mp   = cls_data["special_mp"]
            if player["mp"] < sp_mp:
                slow_print(col(f"  ❌ Need {sp_mp} MP for Special!", RED)); player_acted = False
            else:
                player["mp"] -= sp_mp
                if sp_name == "whirlwind":
                    dmg = random.randint(player["atk"] * 2, player["atk"] * 3)
                    enemy["hp"] -= dmg
                    slow_print(col(f"  🌀 Whirlwind! {dmg} dmg!", CYAN))
                elif sp_name == "backstab":
                    dmg = random.randint(player["atk"] * 2, player["atk"] * 4)
                    enemy["hp"] -= dmg
                    slow_print(col(f"  🗡️  Backstab! {dmg} dmg!", MAGENTA))
                elif sp_name == "arcane_burst":
                    dmg = random.randint(player["atk"] * 2, player["atk"] * 3 + 20)
                    dmg = int(dmg * 1.5)  # Mage boost
                    enemy["hp"] -= dmg
                    slow_print(col(f"  💥 Arcane Burst! {dmg} dmg!", BLUE))
                elif sp_name == "holy_strike":
                    dmg = random.randint(player["atk"] + 10, player["atk"] + 25)
                    enemy["hp"] -= dmg
                    heal = dmg // 2
                    player["hp"] = min(player["max_hp"], player["hp"] + heal)
                    slow_print(col(f"  ✝️  Holy Strike! {dmg} dmg + {heal} HP healed!", YELLOW))
                player["total_damage"] = player.get("total_damage", 0) + (dmg if sp_name != "holy_strike" else dmg)

        elif action == 'p':
            potions = [i for i in player["inventory"] if i in ("Health Potion", "Mega Potion", "Antidote", "Mana Crystal")]
            if not potions:
                slow_print(col("  ❌ No usable items!", RED)); player_acted = False
            else:
                for pi, pt in enumerate(set(potions), 1):
                    print(f"  {col(f'[{pi}]', CYAN)} {pt}")
                pc = input(col("  Use item # > ", CYAN)).strip()
                try:
                    pt_name = list(set(potions))[int(pc)-1]
                    player["inventory"].remove(pt_name)
                    if pt_name == "Health Potion":
                        player["hp"] = min(player["max_hp"], player["hp"] + 40)
                        slow_print(col("  🧪 +40 HP!", GREEN))
                    elif pt_name == "Mega Potion":
                        player["hp"] = min(player["max_hp"], player["hp"] + 100)
                        slow_print(col("  💊 +100 HP!", GREEN))
                    elif pt_name == "Antidote":
                        for ef in ["poison", "burn"]:
                            player["status_effects"].pop(ef, None)
                        slow_print(col("  💉 Cured!", GREEN))
                    elif pt_name == "Mana Crystal":
                        player["mp"] = min(player["max_mp"], player["mp"] + 30)
                        slow_print(col("  💎 +30 MP!", BLUE))
                except (ValueError, IndexError):
                    slow_print(col("  ❓ Invalid.", DIM)); player_acted = False
        else:
            slow_print(col("  ❓ Unknown command.", DIM)); player_acted = False

        if not player_acted: continue

        # Enemy status ticks
        e_to_remove = []
        for eff, turns in list(enemy_status.items()):
            dot = STATUS_EFFECTS[eff].get("dot", 0)
            if dot > 0:
                enemy["hp"] -= dot
                slow_print(col(f"  {STATUS_EFFECTS[eff]['msg']} ticks: -{dot} HP", STATUS_EFFECTS[eff]["color"]))
            enemy_status[eff] = turns - 1
            if enemy_status[eff] <= 0: e_to_remove.append(eff)
        for e in e_to_remove: del enemy_status[e]

        if enemy["hp"] <= 0: break

        # Enemy turn
        time.sleep(0.2)
        if "stun" in enemy_status:
            slow_print(col(f"  ⚡ {enemy['name']} is stunned!", YELLOW))
            del enemy_status["stun"]
            continue

        # Enemy picks a skill
        use_skill = enemy.get("skills") and random.random() < 0.35
        if use_skill:
            skill_name = random.choice(enemy["skills"])
            skill = ENEMY_SKILLS.get(skill_name, {"dmg_mult": 1.0, "msg": "attacks you", "effect": None})
            base_edm = random.randint(enemy["atk"] - 3, enemy["atk"] + 4)
            edm = max(0, int(base_edm * skill["dmg_mult"]) - player["def"])
        else:
            base_edm = random.randint(enemy["atk"] - 3, enemy["atk"] + 3)
            edm = max(0, base_edm - player["def"])
            skill = {"msg": "attacks you", "effect": None}

        # Warrior passive: iron will
        if player["class"] == "Warrior" and random.random() < 0.15:
            slow_print(col(f"  🛡️  Iron Will! You ignore the hit!", GREEN)); continue

        # Rogue passive: evasion
        if player["class"] == "Rogue" and random.random() < 0.20:
            slow_print(col(f"  💨 You evade the attack!", CYAN)); continue

        # Steal special
        if skill.get("effect") == "steal" and player["gold"] > 0:
            stolen = random.randint(1, min(10, player["gold"]))
            player["gold"] -= stolen
            slow_print(col(f"  💸 {enemy['name']} stole {stolen} gold!", RED))
        elif edm > 0:
            player["hp"] -= edm
            slow_print(f"  {enemy['emoji']} {enemy['name']} {skill['msg']} — {col(str(edm) + ' dmg', RED)}!")
            if skill.get("effect") and skill["effect"] != "steal":
                apply_status(player, skill["effect"])
                se = STATUS_EFFECTS.get(skill["effect"], {})
                slow_print(col(f"  You are {skill['effect']}ed!", se.get("color", RED)))
        else:
            slow_print(col(f"  💨 {enemy['name']}'s attack glances off your armor!", DIM))

    # ── Battle resolution ──
    if player["hp"] <= 0:
        player["hp"] = 0
        print()
        slow_print(col("  💀 You have been defeated!", RED), 0.04)
        slow_print(col("  You respawn in the village with half HP, losing some gold...", YELLOW))
        time.sleep(1.2)
        player["hp"] = max(1, player["max_hp"] // 2)
        lost_gold = player["gold"] // 4
        player["gold"] = max(0, player["gold"] - lost_gold)
        player["location"] = "village"
        player["status_effects"] = {}
        return player, False

    # Victory
    print()
    slow_print(col(f"  🏆 {enemy['name']} defeated!", GREEN), 0.022)
    player["xp"]    += enemy["xp"]
    player["gold"]  += enemy["gold"]
    player["kills"] += 1
    slow_print(f"  +{col(str(enemy['xp']) + ' XP', CYAN)}   +{col(str(enemy['gold']) + ' gold', YELLOW)}")

    # Loot drop
    room = ROOMS.get(player.get("location", ""), {})
    loot_table = room.get("loot_table", [])
    if loot_table and random.random() < 0.60:
        loot = random.choice(loot_table)
        player["materials"][loot] = player["materials"].get(loot, 0) + 1
        slow_print(col(f"  🎒 Loot: {loot}", MAGENTA))

    # Quest tracking — kill
    for qk, q in player["quests"].items():
        if q["status"] == "active" and q.get("target") == enemy["name"]:
            q["kills"] = q.get("kills", 0) + 1
            if q["kills"] >= q.get("count", 1):
                q["status"] = "complete"
                slow_print(col(f"  ✅ Quest complete: {q['name']}! +{q['reward_gold']}g +{q['reward_xp']} XP", YELLOW))
                player["gold"] += q["reward_gold"]
                player["xp"]   += q["reward_xp"]

    # Level up
    while player["xp"] >= player["level"] * 60:
        player["level"] += 1
        bonuses = CLASSES[player["class"]]["level_bonuses"]
        for stat, val in bonuses.items():
            player[stat] = player.get(stat, 0) + val
        player["hp"] = player["max_hp"]
        player["mp"] = player["max_mp"]
        print()
        slow_print(col(f"  🌟 LEVEL UP → Level {player['level']}!", YELLOW), 0.025)
        slow_print(f"  {col('HP', GREEN)}: {player['max_hp']}  {col('MP', BLUE)}: {player['max_mp']}  {col('ATK', RED)}: {player['atk']}  {col('DEF', CYAN)}: {player['def']}")

    # Achievements
    check_achievements(player)
    return player, True

# ─── SHOP SYSTEM ───────────────────────────────────────────────
def shop_menu(player, items, title="SHOP"):
    while True:
        clear()
        header(f"  🛒  {title}")
        print(f"\n  {col('💰 Gold:', YELLOW)} {player['gold']}\n")
        keys = list(items.keys())
        for i, (item, info) in enumerate(items.items(), 1):
            own = player["inventory"].count(item) + player["materials"].get(item, 0)
            print(f"  {col(f'[{i}]', CYAN)} {info['emoji']} {item:<22} {col(str(info['price'])+'g', YELLOW):<10} {col(info['desc'], DIM)}")
        print(f"\n  {col('[q]', RED)} Leave\n")
        ch = input(col("  Buy # > ", CYAN)).strip().lower()
        if ch == 'q': break
        try:
            idx = int(ch) - 1
            item = keys[idx]
            info = items[item]
            if player["gold"] < info["price"]:
                slow_print(col("  ❌ Not enough gold!", RED)); time.sleep(0.7)
            else:
                player["gold"] -= info["price"]
                stat = info["stat"]
                val  = info["val"]
                if stat == "heal":
                    player["inventory"].append(item)
                elif stat == "flee":
                    player["inventory"].append(item)
                elif stat == "cure":
                    player["inventory"].append(item)
                elif stat == "mp":
                    player["inventory"].append(item)
                elif stat in ("atk", "def"):
                    player[stat] += val
                    player["inventory"].append(item)
                elif stat == "max_hp":
                    player["max_hp"] += val
                    player["hp"]     += val
                elif stat == "max_mp":
                    player["max_mp"] += val
                    player["mp"]     += val
                slow_print(col(f"  ✅ Bought {item}!", GREEN)); time.sleep(0.6)
        except (ValueError, IndexError):
            slow_print(col("  ❓ Invalid.", DIM)); time.sleep(0.4)
    return player

# ─── CRAFTING ──────────────────────────────────────────────────
def crafting_menu(player):
    while True:
        clear()
        header("  ⚒️   CRAFTING BENCH")
        print(f"\n  {bold('Your materials:')}")
        if player["materials"]:
            for mat, qty in sorted(player["materials"].items()):
                print(f"  {col('·', DIM)} {mat}: {qty}")
        else:
            print(col("  (none)", DIM))
        print(f"\n  {bold('Recipes:')}")
        recipes_list = list(RECIPES.items())
        for i, (name, recipe) in enumerate(recipes_list, 1):
            ings = ", ".join([f"{v}x {k}" for k, v in recipe["ingredients"].items()])
            can_craft = all(player["materials"].get(k, 0) >= v for k, v in recipe["ingredients"].items())
            status = col("✅ Can craft", GREEN) if can_craft else col("❌ Missing", RED)
            print(f"  {col(f'[{i}]', CYAN)} {name:<22} {col(ings, DIM):<40} → {recipe['result_desc']}  {status}")
        print(f"\n  {col('[q]', RED)} Back\n")
        ch = input(col("  Craft # > ", CYAN)).strip().lower()
        if ch == 'q': break
        try:
            idx = int(ch) - 1
            item_name, recipe = recipes_list[idx]
            can_craft = all(player["materials"].get(k, 0) >= v for k, v in recipe["ingredients"].items())
            if not can_craft:
                slow_print(col("  ❌ Missing ingredients!", RED)); time.sleep(0.8)
            else:
                for k, v in recipe["ingredients"].items():
                    player["materials"][k] -= v
                    if player["materials"][k] <= 0: del player["materials"][k]
                player["inventory"].append(item_name)
                slow_print(col(f"  ⚒️  Crafted: {item_name}!", GREEN)); time.sleep(0.7)
        except (ValueError, IndexError):
            slow_print(col("  ❓ Invalid.", DIM)); time.sleep(0.4)
    return player

# ─── QUEST BOARD ───────────────────────────────────────────────
def quest_board(player):
    clear()
    header("  📋  QUEST BOARD")
    print()
    for qk, q in player["quests"].items():
        status_col = col(q["status"].upper(), GREEN if q["status"]=="complete" else YELLOW if q["status"]=="active" else DIM)
        print(f"  {col('►', CYAN)} {bold(q['name'])}  [{status_col}]")
        print(f"      {col(q['desc'], DIM)}")
        if q["status"] == "inactive":
            print(f"      {col('[accept]', GREEN)} to activate this quest")
        elif q["status"] == "active":
            if q.get("target"):
                print(f"      Progress: {q.get('kills',0)}/{q.get('count',1)} {q['target']}s killed")
            elif q.get("items"):
                for item, need in q["items"].items():
                    have = player["materials"].get(item, 0) + player["inventory"].count(item)
                    print(f"      {item}: {have}/{need}")
        print(f"      Reward: {col(str(q['reward_gold'])+'g', YELLOW)} + {col(str(q['reward_xp'])+' XP', CYAN)}")
        print()
    print(col("  [q] Back", RED))
    ch = input(col("  > ", CYAN)).strip().lower()
    if ch == 'q': return player
    # Accept quests
    for qk, q in player["quests"].items():
        if q["status"] == "inactive":
            q["status"] = "active"
            q["kills"] = 0
            slow_print(col(f"  ✅ Quest accepted: {q['name']}", GREEN))
    time.sleep(0.8)
    # Check item quests complete
    for qk, q in player["quests"].items():
        if q["status"] == "active" and q.get("items"):
            can_complete = all(
                player["materials"].get(k, 0) + player["inventory"].count(k) >= v
                for k, v in q["items"].items()
            )
            if can_complete:
                q["status"] = "complete"
                for item, need in q["items"].items():
                    for _ in range(need):
                        if item in player["materials"] and player["materials"][item] > 0:
                            player["materials"][item] -= 1
                player["gold"] += q["reward_gold"]
                player["xp"]   += q["reward_xp"]
                slow_print(col(f"  🏆 Quest complete: {q['name']}! +{q['reward_gold']}g +{q['reward_xp']} XP", YELLOW))
    return player

# ─── STATS SCREEN ──────────────────────────────────────────────
def show_stats(player):
    clear()
    header(f"  📊  {player['name'].upper()} — {player['class'].upper()}")
    print()
    print(f"  {col('Level', CYAN)}     {bold(str(player['level']))}    {col('Kills', RED)}    {player['kills']}")
    print(f"  {hp_bar(player['hp'], player['max_hp'], 20)}")
    print(f"  {mp_bar(player['mp'], player['max_mp'], 14)}")
    needed = player["level"] * 60
    print(f"  {xp_bar(player['xp'], needed, 20)}")
    print()
    print(f"  {col('⚔️  ATK', YELLOW)}    {player['atk']}    {col('🛡️  DEF', CYAN)}    {player['def']}    {col('⚡ SPD', GREEN)}    {player['spd']}")
    print(f"  {col('💰 Gold', YELLOW)}   {player['gold']}    {col('👣 Steps', DIM)}  {player['steps']}    {col('💥 Dmg', RED)}    {player.get('total_damage',0)}")
    print()
    zones_visited = len(player.get("visited", []))
    print(f"  {col('🗺️  Zones visited:', MAGENTA)} {zones_visited}/{len(ROOMS)}")
    print()
    print(f"  {bold('Inventory:')}  {', '.join(player['inventory']) if player['inventory'] else col('Empty', DIM)}")
    print()
    if player.get("materials"):
        mats = "  ".join([f"{k}:{v}" for k, v in player["materials"].items()])
        print(f"  {bold('Materials:')} {col(mats, DIM)}")
        print()
    print(f"  {bold('Spells:')} {', '.join(player.get('spells', []))}")
    if player.get("status_effects"):
        print(f"  {bold('Status:')} {', '.join(player['status_effects'].keys())}")
    print()
    achs = player.get("achievements", [])
    if achs:
        print(f"  {bold('Achievements:')} {col(', '.join(achs), YELLOW)}")
    pause()

# ─── ACHIEVEMENTS ──────────────────────────────────────────────
def check_achievements(player):
    achs = player.setdefault("achievements", [])
    def add(name):
        if name not in achs:
            achs.append(name)
            slow_print(col(f"  🏅 Achievement unlocked: {name}!", YELLOW))
            time.sleep(0.6)

    if player["kills"] >= 1   and "First Blood"        not in achs: add("First Blood")
    if player["kills"] >= 10  and "Warrior"            not in achs: add("Warrior")
    if player["kills"] >= 50  and "Monster Hunter"     not in achs: add("Monster Hunter")
    if player["kills"] >= 100 and "Legend"             not in achs: add("Legend")
    if player["level"] >= 5   and "Veteran"            not in achs: add("Veteran")
    if player["level"] >= 10  and "Elite"              not in achs: add("Elite")
    if player["gold"] >= 500  and "Merchant"           not in achs: add("Merchant")
    if player["gold"] >= 2000 and "Wealthy"            not in achs: add("Wealthy")
    if len(player.get("visited",[])) >= 7 and "Explorer" not in achs: add("Explorer")
    if len(player.get("visited",[])) >= len(ROOMS) and "Cartographer" not in achs: add("Cartographer")
    if player.get("boss_defeated") and "Dragonslayer"  not in achs: add("Dragonslayer")
    if player.get("total_damage",0) >= 10000 and "Damage Dealer" not in achs: add("Damage Dealer")

# ─── CHURCH REST ───────────────────────────────────────────────
def church_rest(player):
    cost = max(10, (player["max_hp"] - player["hp"] + player["max_mp"] - player["mp"]) // 2)
    print(f"\n  ⛪ The priest offers to restore your HP and MP fully for {col(str(cost) + 'g', YELLOW)}.")
    ch = input(col("  Accept? [y/n] > ", CYAN)).strip().lower()
    if ch == 'y':
        if player["gold"] >= cost:
            player["gold"] -= cost
            player["hp"] = player["max_hp"]
            player["mp"] = player["max_mp"]
            player["status_effects"] = {}
            slow_print(col("  ✨ Fully restored!", GREEN))
        else:
            slow_print(col("  ❌ Not enough gold. The priest nods apologetically.", RED))
    else:
        slow_print(col("  The priest bows and returns to the candles.", DIM))
    time.sleep(0.8)
    return player

# ─── AMBIENT + MINI-EVENTS ─────────────────────────────────────
def ambient_event(player, room):
    if random.random() < 0.25 and room.get("ambient"):
        msg = random.choice(room["ambient"])
        print()
        slow_print(col(f"  💭 {msg}", DIM), 0.012)
    # Small random events
    if random.random() < 0.08:
        events = [
            (f"You find a loose coin in the dirt. +{random.randint(1,5)} gold",  "gold",  random.randint(1,5)),
            ("You eat some trail rations. +10 HP",   "hp",   10),
            ("A cool breeze restores your focus. +5 MP", "mp", 5),
        ]
        ev_msg, ev_stat, ev_val = random.choice(events)
        if ev_stat == "gold":   player["gold"]  += ev_val
        elif ev_stat == "hp":   player["hp"]     = min(player["max_hp"], player["hp"] + ev_val)
        elif ev_stat == "mp":   player["mp"]     = min(player["max_mp"], player["mp"] + ev_val)
        slow_print(col(f"  ✨ {ev_msg}.", CYAN))
    return player

# ─── MAP ───────────────────────────────────────────────────────
def show_map(player):
    clear()
    header("  🗺️   WORLD MAP")
    visited = set(player.get("visited", []))
    MAP = [
        "                        [CHURCH]               ",
        "                           |                   ",
        "[MARSHLANDS]—[MEADOW]—[VILLAGE]—[DUNGEON GATE]—[THRONE]",
        "                  |         |         |              ",
        "            [F.ENTRANCE] [MARKET] [CRYPT]            ",
        "                  |                   |              ",
        "            [F.DEEP]———[CAVE MOUTH]—[CAVE DEPTHS]   ",
        "                |           |              |         ",
        "          [U.RIVER]—[MINE SHAFT]      [RUINS]       ",
    ]
    room_keys = list(ROOMS.keys())
    print()
    for line in MAP:
        out = ""
        for ch in line:
            out += ch
        print("  " + out)
    print()
    print(f"  {bold('Visited:')} {len(visited)}/{len(ROOMS)} zones")
    for rk in room_keys:
        marker = col("✅", GREEN) if rk in visited else col("❓", DIM)
        print(f"    {marker} {ROOMS[rk]['name']}")
    pause()

# ─── MAIN GAME LOOP ────────────────────────────────────────────
def main():
    player = title_screen()

    while True:
        clear()
        room_key = player["location"]
        room     = ROOMS.get(room_key, ROOMS["forest_entrance"])

        if room_key not in player.get("visited", []):
            player.setdefault("visited", []).append(room_key)

        player["steps"] = player.get("steps", 0) + 1

        # Render room
        header(room["name"], color=CYAN)
        print()
        wrap_print(room["desc"])
        print()

        # Ambient
        player = ambient_event(player, room)

        # Status bar
        divider()
        print(f"  {hp_bar(player['hp'], player['max_hp'], 14)}   {col('MP', BLUE)}: {player['mp']}/{player['max_mp']}")
        print(f"  {col('Lv', CYAN)}{player['level']}  {col(str(player['atk'])+'ATK', YELLOW)}  {col(str(player['def'])+'DEF', CYAN)}  {col(str(player['gold'])+'g', YELLOW)}  {col(player['class'], MAGENTA)}")
        if player.get("status_effects"):
            effs = "  ".join([col(STATUS_EFFECTS[e]["msg"], STATUS_EFFECTS[e]["color"]) for e in player["status_effects"]])
            print(f"  {effs}")
        divider()

        # Exits
        exits = room.get("exits", {})
        exit_str = "  ".join([f"{col('['+d[0].upper()+']', CYAN)} {d.capitalize()}" for d in exits])
        print(f"\n  📍 {exit_str}")

        # Commands
        print(f"\n  {col('[f]',RED)} Fight   {col('[i]',CYAN)} Stats   {col('[m]',BLUE)} Map   {col('[c]',YELLOW)} Craft   {col('[q_board]',GREEN)} Quests")
        if "shop"         in room: print(f"  {col('[b]', YELLOW)} Enter Shop")
        if "black_market" in room: print(f"  {col('[bm]', MAGENTA)} Black Market")
        if "healing"      in room: print(f"  {col('[rest]', GREEN)} Rest at the church")
        if "boss"         in room and not player.get("boss_defeated"):
            print(f"  {col('[boss]', RED + BOLD)} ⚠️  FIGHT THE BOSS: {room['boss']['name']}")
        if "item" in room and not room["item"].get("collected", True):
            print(f"  {col('[g]', MAGENTA)} Grab: {room['item']['name']}  — {col(room['item']['desc'], DIM)}")
        if "enemies"      in room: print(f"  {col('[f]', RED)} Fight (rate: {int(room['encounter_rate']*100)}%)")
        print(f"  {col('[s]',GREEN)} Save   {col('[q]',RED)} Quit\n")

        cmd = input(col("  > ", CYAN)).strip().lower()

        # ── Commands ──────────────────────────────────────────
        if cmd == 'q':
            save_game(player)
            slow_print(col("  👋 See you in Thornwick, adventurer.", CYAN))
            break

        elif cmd == 's':
            save_game(player)

        elif cmd == 'i':
            show_stats(player)

        elif cmd == 'm':
            show_map(player)

        elif cmd in ('q_board', 'qb', 'quests'):
            player = quest_board(player)

        elif cmd == 'c':
            player = crafting_menu(player)

        elif cmd == 'b' and "shop" in room:
            player = shop_menu(player, room["shop"], "THORNWICK SHOP")

        elif cmd == 'bm' and "black_market" in room:
            player = shop_menu(player, room["black_market"], "BLACK MARKET — NO QUESTIONS")

        elif cmd == 'rest' and "healing" in room:
            player = church_rest(player)

        elif cmd == 'g' and "item" in room and not room["item"].get("collected", True):
            item = room["item"]
            item["collected"] = True
            stat = item.get("stat")
            if stat == "multi":
                for s in ["atk", "def", "max_hp", "max_mp"]:
                    if s in item:
                        player[s] = player.get(s, 0) + item[s]
                slow_print(col(f"  ✨ {item['name']} absorbed!", MAGENTA))
            elif stat == "heal":
                player["hp"] = min(player["max_hp"], player["hp"] + item["val"])
                slow_print(col(f"  🌿 {item['name']} used! +{item['val']} HP", GREEN))
            elif stat and stat in player:
                player[stat] = player.get(stat, 0) + item.get("val", 0)
                slow_print(col(f"  ✨ {item['name']}! +{item['val']} {stat.upper()}", CYAN))
            elif item.get("gold"):
                player["gold"] += item["gold"]
                slow_print(col(f"  💰 {item['name']} sold for {item['gold']} gold!", YELLOW))
            else:
                player["inventory"].append(item["name"])
                slow_print(col(f"  🎒 Picked up {item['name']}!", CYAN))
            time.sleep(0.9)

        elif cmd == 'f' and "enemies" in room:
            enemy = random.choice(room["enemies"])
            player, won = combat(player, enemy)
            pause()

        elif cmd == 'boss' and "boss" in room and not player.get("boss_defeated"):
            slow_print(col("\n  🔥 The ground shakes... The Inferno Dragon rises!", RED + BOLD), 0.03)
            time.sleep(1)
            player, won = combat(player, room["boss"], is_boss=True)
            if won:
                player["boss_defeated"] = True
                player["quests"]["q_slay_dragon"]["status"] = "complete"
                clear()
                print(col(r"""
  ╔═══════════════════════════════════════════════════╗
  ║                                                   ║
  ║    🎉  THE INFERNO DRAGON HAS BEEN SLAIN!  🎉    ║
  ║                                                   ║
  ║     You are the Champion of Thornwick.            ║
  ║     Songs will be sung of your deeds.             ║
  ║                                                   ║
  ╚═══════════════════════════════════════════════════╝
""", YELLOW))
                print(f"  Final stats:")
                print(f"  Level: {player['level']}  Kills: {player['kills']}  Steps: {player['steps']}  Gold: {player['gold']}")
                print(f"  Zones visited: {len(player.get('visited',[]))}/{len(ROOMS)}")
                print(f"  Achievements: {', '.join(player.get('achievements',[]))}")
                save_game(player)
                pause("Press Enter to exit...")
                break
            pause()

        else:
            # Movement
            moved = False
            for direction, dest in exits.items():
                if cmd in (direction, direction[0]):
                    player["location"] = dest
                    moved = True
                    # Random encounter on move
                    new_room = ROOMS.get(dest, {})
                    enc_rate = new_room.get("encounter_rate", 0)
                    if enc_rate > 0 and "enemies" in new_room and random.random() < enc_rate * 0.35:
                        time.sleep(0.3)
                        e = random.choice(new_room["enemies"])
                        slow_print(col(f"\n  ⚠️  Ambushed by {e['emoji']} {e['name']}!", RED))
                        time.sleep(0.6)
                        player, _ = combat(player, e)
                        pause()
                    break
            if not moved:
                slow_print(col("  ❓ Can't go that way.", DIM)); time.sleep(0.5)

if __name__ == "__main__":
    main()

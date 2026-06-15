# TerminalQuest ⚔️

A fully-featured text-based RPG that runs in your terminal. Fight monsters, level up, explore 7 interconnected zones, and defeat the Inferno Dragon.

## Features

- **7 unique zones** — Forest, Village, Cave, Swamp, Mine, Ruins, Dungeon
- **3 playable classes** — Warrior, Rogue, Mage (each with different stats)
- **Turn-based combat** — Attack, Magic, Special, Potion, or Run
- **Critical hits & status effects** — Crits, stuns, boss fire breath
- **Full stat system** — ATK, DEF, HP, MP, XP, level-ups
- **Shop** — Buy weapons, shields, potions, mana crystals
- **Random encounters** — Enemies ambush you as you move
- **Save/Load** — Progress persists to `save.json`
- **ANSI color UI** — HP bars, XP bars, colored combat log
- **7 collectible items** scattered across the world
- **Final boss** — 120 HP Inferno Dragon with fire breath attack

## How to run

```bash
python3 main.py
```

Requires Python 3.6+. No external dependencies.

## Controls

| Key | Action |
|-----|--------|
| `n/s/e/w` | Move North/South/East/West |
| `up/down` | Move Up/Down (in cave/mine) |
| `f` | Fight a random enemy |
| `b` | Enter shop |
| `g` | Grab item |
| `boss` | Fight the final boss |
| `i` | View stats |
| `s` | Save game |
| `q` | Save and quit |

## Classes

| Class | HP | ATK | DEF | MP | Playstyle |
|-------|----|-----|-----|----|-----------|
| Warrior | 130 | 14 | 5 | 20 | Tank, high HP |
| Rogue | 100 | 20 | 2 | 20 | Glass cannon |
| Mage | 100 | 12 | 3 | 60 | Magic damage |

## World map

```
  [RUINS] ── [VILLAGE] ── [DUNGEON]
                │               │
              [FOREST] ── [CAVE]
                │               │
             [SWAMP] ── [MINE] ──┘
```

## Build an exe

```bash
pip install pyinstaller
pyinstaller --onefile main.py
# Output: dist/main (Linux/Mac) or dist/main.exe (Windows)
```

## About

Built for [Macondo](https://macondo.hackclub.com) by Hack Club. ~18 hours of development time logged via Hackatime.

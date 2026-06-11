# TerminalQuest 🗡️

A text-based RPG adventure game that runs entirely in your terminal. No graphics needed — just your imagination and a keyboard.

## What it does

You play as a hero exploring a world of forests, villages, caves, and dungeons. Fight monsters, level up your character, buy gear from shops, collect hidden items, and ultimately defeat the Dragon in the Ancient Dungeon.

- **Combat system** — turn-based fighting with attack/flee options
- **Leveling** — gain XP, level up, increase stats
- **Shop** — buy swords, shields, and potions with earned gold
- **Save/Load** — your progress saves to a local file
- **Exploration** — 4 interconnected rooms to discover

## How to run

```bash
python3 main.py
```

Requires Python 3.6+. No external dependencies.

## Building the exe

```bash
pip install pyinstaller
pyinstaller --onefile main.py
# Find TerminalQuest.exe in dist/
```

## About

Built for [Macondo](https://macondo.hackclub.com) by Hack Club. This project takes about 12–18 hours to build from scratch — great for learning Python fundamentals, game loops, file I/O, and OOP concepts.

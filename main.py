#!/usr/bin/env python3
"""
TerminalQuest - A text-based RPG adventure
Built for Macondo / Hack Club
"""
import json, os, random, sys, time

SAVE_FILE = "save.json"

ROOMS = {
    "forest": {
        "name": "Dark Forest",
        "desc": "Gnarled trees surround you. A narrow path leads north to the village, east to a cave.",
        "exits": {"north": "village", "east": "cave"},
        "enemy": {"name": "Wolf", "hp": 20, "atk": 5, "xp": 10, "gold": 5}
    },
    "village": {
        "name": "Riverside Village",
        "desc": "A peaceful village. A shop sign creaks in the wind. South leads back to the forest.",
        "exits": {"south": "forest", "east": "dungeon"},
        "shop": {"Sword": 30, "Shield": 20, "Potion": 10}
    },
    "cave": {
        "name": "Echoing Cave",
        "desc": "Dripping stalactites. Something glitters in the darkness. West leads back.",
        "exits": {"west": "forest", "north": "dungeon"},
        "item": {"name": "Magic Gem", "value": 50}
    },
    "dungeon": {
        "name": "Ancient Dungeon",
        "desc": "Torches flicker. The final boss awaits at the center.",
        "exits": {"west": "village", "south": "cave"},
        "enemy": {"name": "Dragon", "hp": 80, "atk": 20, "xp": 100, "gold": 200}
    }
}

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def slow_print(text, delay=0.03):
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()

def new_game():
    return {
        "name": input("Enter your hero's name: ").strip() or "Hero",
        "hp": 100, "max_hp": 100, "atk": 15, "gold": 10,
        "xp": 0, "level": 1,
        "inventory": ["Rusty Sword"],
        "location": "forest",
        "visited": []
    }

def save_game(player):
    with open(SAVE_FILE, 'w') as f:
        json.dump(player, f)
    print("Game saved!")

def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE) as f:
            return json.load(f)
    return None

def combat(player, enemy):
    enemy = dict(enemy)
    slow_print(f"\n⚔️  A wild {enemy['name']} appears! HP: {enemy['hp']}")
    while player['hp'] > 0 and enemy['hp'] > 0:
        print(f"\nYour HP: {player['hp']} | {enemy['name']} HP: {enemy['hp']}")
        action = input("[A]ttack / [R]un > ").strip().lower()
        if action == 'r':
            slow_print("You fled!")
            return player
        dmg = random.randint(player['atk'] - 3, player['atk'] + 3)
        enemy['hp'] -= dmg
        slow_print(f"You deal {dmg} damage!")
        if enemy['hp'] <= 0:
            slow_print(f"🏆 You defeated the {enemy['name']}! +{enemy['xp']} XP, +{enemy['gold']} gold")
            player['xp'] += enemy['xp']
            player['gold'] += enemy['gold']
            if player['xp'] >= player['level'] * 50:
                player['level'] += 1
                player['atk'] += 3
                player['max_hp'] += 10
                player['hp'] = player['max_hp']
                slow_print(f"🌟 LEVEL UP! You are now level {player['level']}!")
            return player
        edm = random.randint(enemy['atk'] - 2, enemy['atk'] + 2)
        player['hp'] -= edm
        slow_print(f"The {enemy['name']} hits you for {edm} damage!")
    if player['hp'] <= 0:
        slow_print("💀 You have been defeated... Game over.")
        sys.exit()
    return player

def shop(player, items):
    print("\n🛒 Shop:")
    for item, price in items.items():
        print(f"  {item}: {price} gold")
    choice = input("Buy what? (or Enter to leave) > ").strip()
    if choice in items:
        if player['gold'] >= items[choice]:
            player['gold'] -= items[choice]
            player['inventory'].append(choice)
            slow_print(f"Bought {choice}!")
            if choice == 'Sword': player['atk'] += 5
            elif choice == 'Potion': player['hp'] = min(player['hp'] + 30, player['max_hp'])
        else:
            slow_print("Not enough gold.")
    return player

def main():
    clear()
    slow_print("╔══════════════════════════════╗")
    slow_print("║       T E R M I N A L        ║")
    slow_print("║          Q U E S T           ║")
    slow_print("╚══════════════════════════════╝")
    print("\n[N] New Game  [L] Load Game  [Q] Quit")
    choice = input("> ").strip().lower()
    if choice == 'q': sys.exit()
    player = load_game() if choice == 'l' and load_game() else new_game()

    while True:
        clear()
        room = ROOMS[player['location']]
        if player['location'] not in player['visited']:
            player['visited'].append(player['location'])
        slow_print(f"\n📍 {room['name']}")
        slow_print(f"   {room['desc']}")
        print(f"\n❤️  HP: {player['hp']}/{player['max_hp']}  ⚔️  ATK: {player['atk']}  💰 Gold: {player['gold']}  ⭐ Lv{player['level']}")
        print(f"🎒 Inventory: {', '.join(player['inventory'])}")
        exits = ' | '.join([f"[{k.upper()[0]}] {k.capitalize()}" for k in room['exits']])
        print(f"\nExits: {exits}")
        print("[I] Info  [S] Save  [Q] Quit")

        if 'enemy' in room:
            print("[F] Fight")
        if 'shop' in room:
            print("[B] Buy")
        if 'item' in room:
            print("[G] Grab item")

        cmd = input("\n> ").strip().lower()
        if cmd == 'q': save_game(player); break
        elif cmd == 's': save_game(player)
        elif cmd == 'i':
            slow_print(f"Name: {player['name']} | Level: {player['level']} | XP: {player['xp']}")
        elif cmd == 'f' and 'enemy' in room:
            player = combat(player, room['enemy'])
        elif cmd == 'b' and 'shop' in room:
            player = shop(player, room['shop'])
        elif cmd == 'g' and 'item' in room:
            slow_print(f"Found {room['item']['name']}! Added to inventory.")
            player['inventory'].append(room['item']['name'])
            player['gold'] += room['item']['value']
            del room['item']
        else:
            for direction, dest in room['exits'].items():
                if cmd == direction[0]:
                    player['location'] = dest
                    break
        
        if player['location'] == 'dungeon' and len(player['visited']) >= 3:
            slow_print("\n🏰 You've conquered the dungeon and defeated the dragon!")
            slow_print("🎉 Congratulations! You've completed TerminalQuest!")
            input("Press Enter to exit...")
            break

if __name__ == "__main__":
    main()

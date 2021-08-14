_event_list = [
    "player.north",
    "player.south",
    "player.east",
    "player.west",
    "game.quit",
    "game.command",
    "game.autoplay",
]


# Enumerates game events
GameEvent = {}

# Contains non-in-game events (control keys etc.)
MetaEvents = set()

for i, event in enumerate(_event_list):
    GameEvent[event] = i
    if event.startswith("game."):
        MetaEvents.add(i)

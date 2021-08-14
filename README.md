# flood

Turn-based procedurally generated cave explorer game

## Concept

- "Reverse" dungeon crawler: The main objective is to escape the flooding dungeon.
- I want to port the result to android and make it available on play store and maybe F-droid.

## Todos and Ideas

### High-priority

- [ ] Add player.
- [ ] Add NPCs.
- [ ] Meaningful dungeon generation. (mines, caverns, skeleton settlements)

### Low-priority

- [ ] Add **flow** from high to low water levels. This doesn't affect water propagation, but it can drag entities.
- [ ] Separate queues for each water source or connected body of water. When two bodies of water meet, the queues are merged.
- [ ] Maximum water level per source. (Like limited pressure.) High water amount at source = lower pressure = less water released.
- [ ] **Mining**: using pickaxe to break soft walls. Or maybe a shovel would be better.
- [ ] Water displacement without source (breaking a dam). Use reversed queue to remove a water unit and regular queue to place it (expand). (Displace everytime the level difference between the top of the reservoir queue and the top of the expansion queue is larger than x. Or maybe displace all the time.)

### To consider

- Ways to interact with NPCs other than fighting.
- Status effects: wet, cold, fatigued, hungry. Campfire to heal status effects.
- Plants and fungi.
- Skills: water intuition (predict where water expands), botanist intuition, mycologist intuition, hunter intuition...
- Biomes?

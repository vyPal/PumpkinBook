# The world handle

`World` represents one loaded dimension, the overworld, the nether, an end, or a custom world a plugin created. You get one from `player.get_world()`, from an event's data, or from the server-wide lookups covered in [Server info & worlds](../server/server-info-and-worlds.md). This page covers blocks, time, weather, sound/particles, and the handful of world-scoped utilities, entities get their own chapters starting with [Entities: identity & movement](./entities-basics.md).

## Identity

### `.get_id()` / `.get_name()` / `.get_dimension()`

`get_id()` is the internal world identifier, `get_name()` is the friendlier name (`"world"`, `"world_nether"`, `"arena_1"`), and `get_dimension()` is the dimension type string (`"minecraft:overworld"`, `"minecraft:the_nether"`, and so on).

## Blocks

### `.get_block_state_id(pos)` / `.get_block_state(pos)` / `.set_block_state(pos, state, update_flags)`

`get_block_state_id` returns the raw numeric block state id at a `BlockPos`, `get_block_state` returns the fuller `BlockState` record (id, luminance, opacity, hardness, and more). `set_block_state` takes a numeric state id back and a `BlockFlags` flag set controlling side effects: `notify_neighbors`, `notify_listeners`, `force_state` (apply even if it's already that state), `skip_drops`.

### `.get_top_block_y(x, z)` / `.get_motion_blocking_height(x, z)`

The Y coordinate of the highest non-air block, or the highest block that blocks entity motion (these can differ, water and other non-solid-but-motion-affecting blocks count for the second one but not always the first).

### `.get_sky_light(pos)` / `.set_sky_light(pos, level)` / `.get_block_light(pos)` / `.set_block_light(pos, level)`

Reads or overrides the 0-15 light levels at a position. These are the raw lighting engine values, not a lighting effect you toggle, setting them doesn't create a persistent light source, the engine can recalculate and overwrite your value on the next lighting update.

### `.get_biome(pos)`

Returns the `Biome` at a position.

> [!NOTE]
> `Biome` isn't re-exported from the crate root or an obvious `biomes` module, the only public path to it is `pumpkin_plugin_api::worldgen::PluginBiome` (an alias defined inside the world-generation module, of all places, since that's the other place a `Biome` value is needed). Import it from there if you want to `match` on what `get_biome` returns.

### `.get_sea_level()` / `.get_min_y()`

The world's configured sea level and the lowest buildable Y coordinate.

## Chunks & the border

### `.get_chunk(x, z)` / `.get_world_border()`

Returns a `Chunk` handle for the given chunk coordinates (not block coordinates, divide by 16), or the world's `WorldBorder`. Both get their own methods in [Chunks & world borders](./chunks-and-borders.md).

## Time & weather

### `.get_time_of_day()` / `.set_time_of_day(time)` / `.get_world_age()`

The current time of day in ticks (0-24000 per day cycle) and the world's total age in ticks since creation. Setting `time_of_day` jumps the world's actual clock, if you only want to change what one specific player sees, use `set_player_time` from [Inventory & environment](../players/player-inventory-and-environment.md) instead.

### `.is_raining()` / `.set_raining(raining)` / `.is_thundering()` / `.set_thundering(thundering)`

Weather state for the whole world. Same distinction as above, these affect everyone in the world, `set_player_weather` affects one player.

## Game rules

### `.get_game_rule(rule)` / `.set_game_rule(rule, value)`

Reads or sets a vanilla game rule (`GameRule::MobGriefing`, `GameRule::KeepInventory`, and dozens more, see the [vanilla data reference](../advanced/vanilla-data-reference.md) for the full list). `value` is a `GameRuleValue`, either `GameRuleValue::Int(i32)` or `GameRuleValue::Bool(bool)`, matching whichever type that particular rule actually uses.

```rust
use pumpkin_plugin_api::{GameRule, GameRuleValue};

world.set_game_rule(GameRule::KeepInventory, GameRuleValue::Bool(true));
```

## Sound & particles

### `.play_sound(sound, category, pos, volume, pitch)`

> [!WARNING]
> Like `Biome`, the `Sound` enum isn't currently exported publicly by `pumpkin-plugin-api`, even though `SoundCategory` (a `world`-module type) is. Since `play_sound` requires a `Sound` value to call at all, there's currently no supported way to call this method from a plugin.

### `.spawn_particle(particle, pos, offset, max_speed, count)`

Unlike sounds, `Particle` is exported and usable. Spawns `count` particles of the given `Particle` kind at `pos`, randomized within `offset` on each axis, with `max_speed` controlling how fast they scatter.

```rust
use pumpkin_plugin_api::particles::Particle;

world.spawn_particle(Particle::HappyVillager, position, (0.5, 0.5, 0.5), 0.1, 10);
```

## Explosions & lightning

### `.create_explosion(pos, power, create_fire, interaction)`

Creates an explosion, `power` scales the blast radius the same way TNT/creeper power values do, `interaction` (an `ExplosionInteraction`) controls how it affects blocks: `None`, `Block` (destroys blocks, may drop loot), `Mob` (mob-explosion-style), or `Tnt`.

### `.strike_lightning(pos, effect_only)`

Strikes lightning at a position. `effect_only: true` gives the visual/sound effect without the gameplay side effects (fire, charged creepers, converting villagers, damage).

## Entities

### `.spawn_entity(entity_type, pos)` / `.get_entities()`

Spawns an `EntityType` at a position and returns the new `Entity`, or lists every entity currently loaded in the world. See [Entities: identity & movement](./entities-basics.md) for what you can do with the result.

### `.ray_trace_blocks(start, end)`

A block-only raycast between two positions (no entities), returns the position of the first block hit, or `None` if the ray reaches `end` unobstructed.

## Block entities

### `.get_block_entity(pos)` / `.get_block_entity_nbt(pos)` / `.set_block_entity_nbt(pos, nbt_data)`

Reads the typed block entity at a position, or works with its raw NBT directly. `set_block_entity_nbt` expects the NBT to contain a valid `id` field (e.g. `"minecraft:chest"`) and returns an error if it doesn't. See [Block entities](./block-entities.md) for the typed accessors.

## Messaging

### `.broadcast_system_message(message, overlay)`

Sends a `TextComponent` to every player currently in this world (not the whole server, use `server.broadcast()` for that). `overlay: true` shows it in the action bar instead of chat.

## Custom data & saving

### `.set_custom_data(namespace, key, value)` / `.get_custom_data(namespace, key)` / `.remove_custom_data(namespace, key)` / `.has_custom_data(namespace, key)`

Attaches your own namespaced NBT data to the world itself, persisted with it. See [Persistent Data](../persistent-data/persistent-data.md) for the friendlier `PersistentDataHolder` wrapper around these same calls.

### `.save()`

Saves all chunk data, block entities, and entities for this world to disk immediately, outside the normal autosave cycle.

## Custom generation

### `.set_chunk_generator(generator_id)`

Installs a custom chunk generator (by a registered generator id) for this world. Covered in full in [Custom chunk generation](../worldgen/custom-world-generation.md).

## Putting it together

A `/nightvision-zone` style toggle that freezes a world's time at midnight and turns off rain for the duration of an event:

```rust
use pumpkin_plugin_api::{command::CommandSender, text::TextComponent, world::World};

fn start_event(sender: &CommandSender, world: &World) {
  world.set_time_of_day(18000); // midnight
  world.set_raining(false);
  world.set_thundering(false);

  sender.send_message(TextComponent::text("Event conditions set: midnight, clear skies."));
}
```

# The world handle

`World` represents one loaded dimension, the overworld, the nether, an end, or a custom world a plugin created. You get one from `player.get_world()`, from an event's data, or from the server-wide lookups covered in [Server info & worlds](../server/server-info-and-worlds.md). This page covers blocks, time, weather, sound/particles, and the handful of world-scoped utilities, entities get their own chapters starting with [Entities: identity & movement](./entities-basics.md).

## Identity

### `.get_id()` / `.get_name()` / `.get_dimension()` { data-since=0.1 }

`get_id()` is the internal world identifier, `get_name()` is the friendlier name (`"world"`, `"world_nether"`, `"arena_1"`), and `get_dimension()` is the dimension type string (`"minecraft:overworld"`, `"minecraft:the_nether"`, and so on).

## Blocks

### `.get_block_state_id(pos)` / `.get_block_state(pos)` / `.set_block_state(pos, state, update_flags)` { data-since=0.1 }

`get_block_state_id` returns the raw numeric block state id at a `BlockPos`, `get_block_state` returns the fuller `BlockState` record (id, luminance, opacity, hardness, and more, now also carrying `block_id`, `block_name`, and `properties: Vec<(String, String)>`, the state's property key-value pairs like `facing=north`). `set_block_state` takes a numeric state id back and a `BlockFlags` flag set controlling side effects: `notify_neighbors`, `notify_listeners`, `force_state` (apply even if it's already that state), `skip_drops`.

### `.get_block(pos)` / `.get_block_id(pos)` / `.set_block(pos, block, update_flags)` / `.set_block_by_id(pos, block_id, update_flags)` / `.set_block_by_name(pos, name, update_flags)` { data-since=0.1 }

Alternatives to the state-id-based methods above that work with the higher-level `Block` type (a static block *definition*, see [Block registry](#block-registry) below) instead of a numeric state id, `set_block`/`set_block_by_id`/`set_block_by_name` all place the block's *default* state. `set_block_by_name` accepts a namespaced string (`"minecraft:oak_log"`) and returns `false` if the name wasn't recognized instead of placing anything.

### `.get_top_block_y(x, z)` / `.get_motion_blocking_height(x, z)` { data-since=0.1 }

The Y coordinate of the highest non-air block, or the highest block that blocks entity motion (these can differ, water and other non-solid-but-motion-affecting blocks count for the second one but not always the first).

### `.get_sky_light(pos)` / `.set_sky_light(pos, level)` / `.get_block_light(pos)` / `.set_block_light(pos, level)` { data-since=0.1 }

Reads or overrides the 0-15 light levels at a position. These are the raw lighting engine values, not a lighting effect you toggle, setting them doesn't create a persistent light source, the engine can recalculate and overwrite your value on the next lighting update.

### `.get_biome(pos)` { data-since=0.1 }

Returns the `Biome` at a position.

> [!NOTE]
> `Biome` isn't re-exported from the crate root or an obvious `biomes` module, the only public path to it is `pumpkin_plugin_api::worldgen::PluginBiome` (an alias defined inside the world-generation module, of all places, since that's the other place a `Biome` value is needed). Import it from there if you want to `match` on what `get_biome` returns.

### `.get_sea_level()` / `.get_min_y()` { data-since=0.1 }

The world's configured sea level and the lowest buildable Y coordinate.

## Block registry

Static definitions for every registered block type, as free functions (`pumpkin_plugin_api::world::get_block_by_id(...)`, and so on), not scoped to any particular `World` instance. A `Block` is `{ id, name, hardness, blast_resistance, map_color, slipperiness, velocity_multiplier, jump_velocity_multiplier, item_id, default_state_id, state_ids, is_solid, is_air, is_flammable, flammable }`, `flammable` is `Option<Flammable> { spread_chance, burn_chance }`. This is a static *type* definition (one entry per block, `"minecraft:oak_log"`), distinct from `BlockState` above (one entry per placed *variant* of a block, including its properties).

- `get_block_by_id(id)` / `get_block_by_name(name)` — look up one `Block` by numeric id or namespaced name.
- `get_all_blocks()` / `get_all_block_names()` — every registered `Block`, or just their names.
- `get_block_count()` / `get_block_state_count()` — total registered block types and total block states.
- `get_states_for_block(block)` / `get_states_for_block_id(block_id)` — every `BlockState` belonging to a block type.
- `get_state_ids_for_block_id(block_id)` — same, but just the raw numeric state ids.
- `get_block_properties(state_id)` — the property key-value pairs for one state id, without fetching the whole `BlockState`.
- `get_block_from_state_id(state_id)` / `get_block_from_state(state)` — the parent `Block` a state belongs to.
- `get_default_state_from_block(block)` / `get_default_state_from_block_id(block_id)` — the default (no extra properties) `BlockState` for a block type.
- `get_block_state_by_id(state_id)` — the full `BlockState` record for a numeric state id.

```rust
use pumpkin_plugin_api::world;

if let Some(stone) = world::get_block_by_name("minecraft:stone") {
  println!("stone hardness: {}", stone.hardness);
}
```

## Chunks & the border

### `.get_chunk(x, z)` / `.get_world_border()` { data-since=0.1 }

Returns a `Chunk` handle for the given chunk coordinates (not block coordinates, divide by 16), or the world's `WorldBorder`. Both get their own methods in [Chunks & world borders](./chunks-and-borders.md).

### `.get_spawn_location()` { data-since=0.1 }

Returns the world's configured shared spawn point as a `WorldSpawnLocation { pos, yaw, pitch }`.

## Time & weather

### `.get_time_of_day()` / `.set_time_of_day(time)` / `.get_world_age()` { data-since=0.1 }

The current time of day in ticks (0-24000 per day cycle) and the world's total age in ticks since creation. Setting `time_of_day` jumps the world's actual clock, if you only want to change what one specific player sees, use `set_player_time` from [Inventory & environment](../players/player-inventory-and-environment.md) instead.

### `.is_raining()` / `.set_raining(raining)` / `.is_thundering()` / `.set_thundering(thundering)` { data-since=0.1 }

Weather state for the whole world. Same distinction as above, these affect everyone in the world, `set_player_weather` affects one player.

## Game rules

### `.get_game_rule(rule)` / `.set_game_rule(rule, value)` { data-since=0.1 }

Reads or sets a vanilla game rule (`GameRule::MobGriefing`, `GameRule::KeepInventory`, and dozens more, see the [vanilla data reference](../advanced/vanilla-data-reference.md) for the full list). `value` is a `GameRuleValue`, either `GameRuleValue::Int(i32)` or `GameRuleValue::Bool(bool)`, matching whichever type that particular rule actually uses.

```rust
use pumpkin_plugin_api::{GameRule, GameRuleValue};

world.set_game_rule(GameRule::KeepInventory, GameRuleValue::Bool(true));
```

## Sound & particles

### `.play_sound(sound, category, pos, volume, pitch)` { data-since=0.1 }

> [!NOTE]
> The `Sound` enum isn't re-exported at the root of `pumpkin-plugin-api`, even though `SoundCategory` (a `world`-module type) is. Name it through the raw bindings module instead: `pumpkin_plugin_api::wit::pumpkin::plugin::sounds::Sound`. That module has been public since 2026-09-20, before that `play_sound` couldn't be called from a plugin at all.

```rust
use pumpkin_plugin_api::wit::pumpkin::plugin::sounds::Sound;
use pumpkin_plugin_api::world::SoundCategory;

world.play_sound(Sound::EntityPlayerLevelup, SoundCategory::Players, (0.0, 64.0, 0.0), 1.0, 1.0);
```

### `.play_custom_sound(sound_name, category, pos, volume, pitch)` { data-since=0.1 }

The workaround: takes a plain resource-pack sound identifier string instead of the unexported `Sound` enum, so unlike `play_sound` above, this one is fully callable today. See the same contrast on the per-player version in [Inventory & environment](../players/player-inventory-and-environment.md#audio--particles).

### `.spawn_particle(particle, pos, offset, max_speed, count)` { data-since=0.1 }

Unlike sounds, `Particle` is exported and usable. Spawns `count` particles of the given `Particle` kind at `pos`, randomized within `offset` on each axis, with `max_speed` controlling how fast they scatter.

```rust
use pumpkin_plugin_api::particles::Particle;

world.spawn_particle(Particle::HappyVillager, position, (0.5, 0.5, 0.5), 0.1, 10);
```

## Explosions & lightning

### `.create_explosion(pos, power, create_fire, interaction)` { data-since=0.1 }

Creates an explosion, `power` scales the blast radius the same way TNT/creeper power values do, `interaction` (an `ExplosionInteraction`) controls how it affects blocks: `None`, `Block` (destroys blocks, may drop loot), `Mob` (mob-explosion-style), `Tnt`, or `Trigger` (the mode vanilla uses for wind charges).

> [!NOTE]
> The `create_fire` parameter is accepted but currently ignored by the host, whatever you pass, the explosion doesn't start extra fires of its own.

### `.strike_lightning(pos, effect_only)` { data-since=0.1 }

Strikes lightning at a position. `effect_only: true` gives the visual/sound effect without the gameplay side effects (fire, charged creepers, converting villagers, damage).

## Entities

### `.spawn_entity(entity_type, pos)` / `.get_entities()` { data-since=0.1 }

Spawns an `EntityType` at a position and returns the new `Entity`, or lists every entity currently loaded in the world. See [Entities: identity & movement](./entities-basics.md) for what you can do with the result.

### `.ray_trace_blocks(start, end)` { data-since=0.1 }

A block-only raycast between two positions (no entities), returns the position of the first block hit, or `None` if the ray reaches `end` unobstructed.

### `.ray_trace_block(start, end, include_fluids)` / `.ray_trace_entity(start, end)` / `.ray_trace_entities(start, end)` { data-since=0.1 }

Richer versions of the raycast above. `ray_trace_block` returns the fuller `Option<RayTraceBlockResult> { pos, face, hit_pos }` (a `BlockPos`, the face hit, and the exact hit coordinates) instead of just a raw `Position`, and takes an `include_fluids` flag. `ray_trace_entity` finds the closest entity hit between the two points as `Option<RayTraceEntityResult> { entity, hit_pos, distance }`, `ray_trace_entities` returns every entity hit along the ray instead of just the closest. Same result types as the entity-side and player-side raycast APIs, see [Entities: identity & movement](./entities-basics.md#raycasting).

## Block entities

### `.get_block_entity(pos)` / `.get_block_entity_nbt(pos)` / `.set_block_entity_nbt(pos, nbt_data)` { data-since=0.1 }

Reads the typed block entity at a position, or works with its raw NBT directly. `set_block_entity_nbt` expects the NBT to contain a valid `id` field (e.g. `"minecraft:chest"`) and returns an error if it doesn't. See [Block entities](./block-entities.md) for the typed accessors.

## Messaging

### `.broadcast_system_message(message, overlay)` { data-since=0.1 }

Sends a `TextComponent` to every player currently in this world (not the whole server, use `server.broadcast()` for that). `overlay: true` shows it in the action bar instead of chat.

## Custom data & saving

### `.set_custom_data(namespace, key, value)` / `.get_custom_data(namespace, key)` / `.remove_custom_data(namespace, key)` / `.has_custom_data(namespace, key)` { data-since=0.1 }

Attaches your own namespaced NBT data to the world itself, persisted with it. See [Persistent Data](../persistent-data/persistent-data.md) for the friendlier `PersistentDataHolder` wrapper around these same calls.

### `.save()` { data-since=0.1 }

Saves all chunk data, block entities, and entities for this world to disk immediately, outside the normal autosave cycle.

## Custom generation

### `.set_chunk_generator(generator_id)` { data-since=0.1 }

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

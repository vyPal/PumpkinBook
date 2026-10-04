# Chunks & world borders

Two smaller resources that round out `World`: a `Chunk` handle for working with one 16x16 column directly, and a `WorldBorder` for the playable-area boundary.

## Chunks

Get one from `world.get_chunk(x, z)`, using chunk coordinates, not block coordinates (divide a block's X/Z by 16 to get its chunk). It returns `None` for a chunk that isn't currently loaded.

> [!WARNING]
> A `Chunk` is only a weak handle to a chunk that is loaded right now. If the chunk unloads while you still hold the handle, the next call on it fails with `Chunk unloaded`, and since a failing host call kills the plugin (see [Returning from an executor](../commands/executors.md#returning-from-an-executor)), that is a crash, not an error you can handle. Don't keep `Chunk` handles in your plugin's state or across scheduler ticks. Ask the world for the chunk again each time you need it, and use it right away.

### `.get_x()` / `.get_z()` { data-since=0.1 }

The chunk's own coordinates, handy when you're holding a `Chunk` without remembering which one you asked for.

### `.get_block_state_id(pos)` / `.get_block_state(pos)` / `.set_block_state(pos, state)` { data-since=0.1 }

Same shape as the equivalent `World` methods, but every position is chunk-relative, `x` and `z` must be in `[0, 15]`. Unlike `World::set_block_state`, there's no `update_flags` parameter here.

### `.get_block(pos)` / `.set_block(pos, block)` / `.set_block_by_id(pos, block_id)` { data-since=0.1 }

Chunk-relative versions of `World`'s `Block`-based accessors, see [Block registry](./world-and-time.md#block-registry). Same `[0, 15]` coordinate constraint as above.

### `.get_biome(pos)` { data-since=0.1 }

Same `Biome` type as `World::get_biome`, see the [world handle](./world-and-time.md#blocks) chapter for where to import it from.

### `.get_block_entity(pos)` { data-since=0.1 }

The typed block entity at a chunk-relative position, if any, see [Block entities](./block-entities.md).

### `.get_top_block_y(x, z)` / `.get_sky_light(pos)` / `.get_block_light(pos)` { data-since=0.1 }

Read-only chunk-relative versions of the same `World` queries.

### `.set_custom_data(namespace, key, value)` / `.get_custom_data(namespace, key)` / `.remove_custom_data(namespace, key)` / `.has_custom_data(namespace, key)` { data-since=0.1 }

Namespaced NBT storage attached to the chunk itself, see [Persistent Data](../persistent-data/persistent-data.md), `PersistentDataHolder` is implemented for `Chunk` too.

## World borders

Get one from `world.get_world_border()`.

### `.get_center_x()` / `.get_center_z()` / `.set_center(x, z)` / `.get_center()` { data-since=0.1 }

The border's center point. `get_center()` is a newer convenience returning both coordinates as one `Position` instead of two separate calls.

### `.get_diameter()` / `.set_diameter(diameter, speed)` / `.get_size()` / `.set_size(size)` / `.set_size_transition(new_size, time_seconds)` { data-since=0.1 }

Current diameter in blocks, and a setter that can optionally animate the change, `speed` is how many ticks the transition should take to reach the new diameter, `None` changes it instantly. `get_size`/`set_size` are newer aliases for `get_diameter`/an instant `set_diameter`, `set_size_transition` is an alias for the animated form of `set_diameter` that takes a duration in seconds instead of ticks, generally the more ergonomic one to reach for.

### `.get_target_diameter()` / `.get_target_speed()` { data-since=0.1 }

While a `set_diameter`/`set_size_transition` animation is in progress, these read back the diameter it's transitioning toward and the remaining ticks, so you can check on or display an in-progress shrink/grow without tracking it yourself.

### `.get_warning_distance()` / `.set_warning_distance(distance)` / `.get_warning_delay()` / `.set_warning_delay(delay)` / `.get_warning_time()` / `.set_warning_time(time)` { data-since=0.1 }

The visual warning effect players see as they approach the border: `warning_distance` is how many blocks out it starts showing, `warning_delay` is how many seconds before a shrinking border reaches a player that the warning starts (only relevant while the border is actively moving). `get_warning_time`/`set_warning_time` are newer aliases for `get_warning_delay`/`set_warning_delay`.

### Border damage

`.get_damage_buffer()` / `.set_damage_buffer(buffer)` and `.get_damage_amount()` / `.set_damage_amount(damage)` are new, previously unconfigurable settings: `damage_buffer` is how many blocks outside the border a player can stand before taking damage, `damage_amount` is how much damage per block per second they take once past that buffer, matching vanilla's `/worldborder damage buffer`/`/worldborder damage amount`.

### `.contains(x, z)` / `.contains_pos(pos)` { data-since=0.1 }

Checks whether a coordinate is within the border, useful for gating spawns, teleports, or explosions to the playable area. `contains_pos` is the same check taking a `Position` directly instead of two floats.

### `.reset()` { data-since=0.1 }

Resets every world border setting (center, diameter, warning distance/delay, damage buffer/amount) back to vanilla defaults.

## Putting it together

Shrinking the border toward a fixed arena center over two minutes, and confirming a player isn't already outside it before starting:

```rust
use pumpkin_plugin_api::{command::CommandSender, text::TextComponent, world::World};

fn start_shrinking_arena(sender: &CommandSender, world: &World) {
  let border = world.get_world_border();

  let (px, _, pz) = sender.as_player().map(|p| p.get_position()).unwrap_or((0.0, 0.0, 0.0));
  if !border.contains(px, pz) {
    sender.send_message(TextComponent::text("You need to be inside the border to start this."));
    return;
  }

  border.set_center(0.0, 0.0);
  border.set_diameter(50.0, Some(2400)); // 2 minutes at 20 ticks/sec
  border.set_warning_distance(10);

  sender.send_message(TextComponent::text("Arena border is closing in."));
}
```

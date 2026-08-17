# Chunks & world borders

Two smaller resources that round out `World`: a `Chunk` handle for working with one 16x16 column directly, and a `WorldBorder` for the playable-area boundary.

## Chunks

Get one from `world.get_chunk(x, z)`, using chunk coordinates, not block coordinates (divide a block's X/Z by 16 to get its chunk).

### `.get_x()` / `.get_z()`

The chunk's own coordinates, handy when you're holding a `Chunk` without remembering which one you asked for.

### `.get_block_state_id(pos)` / `.get_block_state(pos)` / `.set_block_state(pos, state)`

Same shape as the equivalent `World` methods, but every position is chunk-relative, `x` and `z` must be in `[0, 15]`. Unlike `World::set_block_state`, there's no `update_flags` parameter here.

### `.get_biome(pos)`

Same `Biome` type as `World::get_biome`, see the [world handle](./world-and-time.md#blocks) chapter for where to import it from.

### `.get_block_entity(pos)`

The typed block entity at a chunk-relative position, if any, see [Block entities](./block-entities.md).

### `.get_top_block_y(x, z)` / `.get_sky_light(pos)` / `.get_block_light(pos)`

Read-only chunk-relative versions of the same `World` queries.

### `.set_custom_data(namespace, key, value)` / `.get_custom_data(namespace, key)` / `.remove_custom_data(namespace, key)` / `.has_custom_data(namespace, key)`

Namespaced NBT storage attached to the chunk itself, see [Persistent Data](../persistent-data/persistent-data.md), `PersistentDataHolder` is implemented for `Chunk` too.

## World borders

Get one from `world.get_world_border()`.

### `.get_center_x()` / `.get_center_z()` / `.set_center(x, z)`

The border's center point.

### `.get_diameter()` / `.set_diameter(diameter, speed)`

Current diameter in blocks, and a setter that can optionally animate the change, `speed` is how many ticks the transition should take to reach the new diameter, `None` changes it instantly.

### `.get_warning_distance()` / `.set_warning_distance(distance)` / `.get_warning_delay()` / `.set_warning_delay(delay)`

The visual warning effect players see as they approach the border: `warning_distance` is how many blocks out it starts showing, `warning_delay` is how many seconds before a shrinking border reaches a player that the warning starts (only relevant while the border is actively moving).

### `.contains(x, z)`

Checks whether a coordinate is within the border, useful for gating spawns, teleports, or explosions to the playable area.

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

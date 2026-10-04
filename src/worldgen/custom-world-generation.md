# Custom chunk generation

Plugins can supply their own terrain generator for a world, taking over some or all of the four generation phases vanilla chunks normally go through. This is a genuinely advanced feature, most plugins won't need it, but it's fully implemented and usable end-to-end.

## The generation phases

Chunk generation happens in four steps, matching a `GenerationPhase`:

1. `Biomes`, assign which biome each column belongs to.
2. `Noise`, carve out the basic terrain shape.
3. `Surface`, apply surface layers (grass, sand, stone bands).
4. `Features`, populate with structures, ores, decorations.

## Implementing a generator

### `ChunkGenerator` { data-since=0.1 }

A trait with one method per phase, all optional (default to doing nothing), implement only the ones you actually want to override:

```rust
use pumpkin_plugin_api::worldgen::{ChunkBuffer, ChunkGenerator, PluginBiome};

struct FlatWorldGenerator;

impl ChunkGenerator for FlatWorldGenerator {
  fn generate_biomes(&self, chunk: &mut ChunkBuffer) {
    chunk.fill_biome(PluginBiome::Plains);
  }

  fn generate_surface(&self, chunk: &mut ChunkBuffer) {
    chunk.fill_layer(-64, 7); // bedrock state id
    chunk.fill_layer(-63, 8); // grass block state id
  }
}
```

> [!NOTE]
> `PluginBiome` is `Biome` under a different name, re-exported from the `worldgen` module specifically because that's where it's needed for `fill_biome`/`set_biome`, it isn't available anywhere else under its own name. It's the exact same type `World::get_biome`/`Chunk::get_biome` return elsewhere in this book.

### `ChunkBuffer` { data-since=0.1 }

The mutable 16x16 column your generator methods receive:

- `.x()` / `.z()`, the chunk's coordinates.
- `.min_y()` / `.height()`, the world's vertical bounds for this chunk.
- `.get_block(x, y, z)` / `.set_block(x, y, z, state_id)`, single-block access, local coordinates (`x`/`z` in `0..16`).
- `.fill_layer(y, state_id)`, an entire horizontal 16x16 slice at one Y.
- `.fill_range(x, min_y, max_y, z, state_id)`, a vertical column between two Y values at one `(x, z)`.
- `.fill_cuboid(min_x, min_y, min_z, max_x, max_y, max_z, state_id)`, a 3D box.
- `.set_biome(x, y, z, biome)` / `.fill_biome(biome)`, per-column or whole-chunk biome assignment.

All block state ids here are the same raw numeric ids used by `World::set_block_state`, look them up the same way.

## Registering & installing

### `GeneratorManager::register(generator)` { data-since=0.1 }

A static method (not tied to a `Server`/`Context` handle), registers your generator and returns a `u32` id.

```rust
use pumpkin_plugin_api::worldgen::GeneratorManager;

let generator_id = GeneratorManager::register(FlatWorldGenerator);
```

### `world.set_chunk_generator(generator_id)` { data-since=0.1 }

Installs the registered generator on a specific world (see [The world handle](../world/world-and-time.md)). New chunks generated for that world from this point on route through your `ChunkGenerator` methods instead of vanilla generation.

## Putting it together

Registering a superflat-style generator and applying it to a freshly created world:

```rust
use pumpkin_plugin_api::{
  worldgen::{ChunkBuffer, ChunkGenerator, GeneratorManager, PluginBiome},
  server::Dimension, Context, Result,
};

struct SuperflatGenerator;

impl ChunkGenerator for SuperflatGenerator {
  fn generate_biomes(&self, chunk: &mut ChunkBuffer) {
    chunk.fill_biome(PluginBiome::Plains);
  }

  fn generate_surface(&self, chunk: &mut ChunkBuffer) {
    chunk.fill_layer(-64, 7);  // bedrock
    chunk.fill_range(0, -63, -61, 0, 1); // stone
    chunk.fill_layer(-60, 2);  // dirt
    chunk.fill_layer(-59, 8);  // grass
  }
}

fn on_load(&self, context: Context) -> Result<()> {
  let generator_id = GeneratorManager::register(SuperflatGenerator);

  let server = context.get_server();
  let world = server.create_world("flat_world", Dimension::Overworld);
  world.set_chunk_generator(generator_id);

  Ok(())
}
```

# Block entities

Block entities are the "extra data" blocks that need more than just their block state, chests remembering their contents, signs remembering their text, furnaces tracking cook progress. Get one from `world.get_block_entity(pos)` or `chunk.get_block_entity(pos)`, both return an `Option<BlockEntityType>`, a variant covering every block entity kind that exists.

## The base resource

Every block entity, whatever its specific kind, gives you `.get_block_entity()` back to a shared base `BlockEntity`:

### `.resource_location()` / `.get_position()` / `.get_id()` { data-since=0.1 }

The block's registry key (`"minecraft:chest"`), its position, and a per-session numeric id.

### `.is_dirty()` / `.clear_dirty()` { data-since=0.1 }

Whether the block entity has unsaved changes pending. Mostly relevant if you're inspecting internal state rather than something you'd normally need to manage yourself.

### `.set_custom_data(namespace, key, value)` / `.get_custom_data(namespace, key)` / `.remove_custom_data(namespace, key)` / `.has_custom_data(namespace, key)` { data-since=0.1 }

Namespaced NBT storage on the block entity, same shape as everywhere else, see [Persistent Data](../persistent-data/persistent-data.md), `PersistentDataHolder` is implemented for `BlockEntity` too.

## Getting the specific type

`world.get_block_entity(pos)` returns a `BlockEntityType` variant, match on it to get at the specific resource for that block:

```rust
use pumpkin_plugin_api::block_entity::BlockEntityType;

if let Some(entity) = world.get_block_entity(pos) {
  match entity {
    BlockEntityType::ChestBlockEntity(chest) => {
      let container = chest.get_container();
      // ...
    }
    BlockEntityType::SignBlockEntity(sign) => {
      let text = sign.get_front_text();
      // ...
    }
    _ => {}
  }
}
```

## Containers

Most storage-holding block entities (chests, barrels, furnaces, hoppers, droppers, dispensers, and more) expose a `.get_container()` returning a shared `ContainerBlockEntity`:

### `.get_size()` / `.is_empty()` / `.get_stack(slot)` / `.set_stack(slot, stack)` / `.remove_stack(slot)` / `.clear()` { data-since=0.1 }

Standard inventory access, `Option<ItemStack>` per slot, same shape as `Player`'s inventory methods.

### `.get_inventory()` { data-since=0.1 }

Returns the container's contents as a generic `Inventory` handle, the same type used for player inventories and GUIs, see [Inventory & environment](../players/player-inventory-and-environment.md#inventory-handles). Same underlying slots as the methods above, useful when you're writing code generic over any `Inventory`-shaped thing.

## Common types, in full

A handful of the most frequently-used block entities, everything else follows the same shape (see the table below).

### Chests, trapped chests, barrels, shulker boxes

`get_container()` plus `.viewer_count()`, how many players currently have the container's screen open.

> [!WARNING]
> Only chests and trapped chests report a real `viewer_count()`. For barrels, ender chests and shulker boxes the host's implementation is hardcoded to return `0`, so don't use it to detect whether one of those is open.

### Signs & hanging signs

`.get_front_text()` / `.set_front_text(text)` / `.get_back_text()` / `.set_back_text(text)` / `.is_waxed()` / `.set_waxed(waxed)`. A `SignText` is `{ messages: Vec<String>, color: DyeColor, has_glowing_text: bool }`, `messages` is one entry per line (up to 4). Waxed signs can't be edited by right-clicking in-game, but you can still update them through this API regardless of the waxed flag.

### Furnaces, blast furnaces, smokers

`get_container()` plus `.get_cooking_time_spent()` / `.get_cooking_total_time()` / `.get_lit_time_remaining()` / `.get_lit_total_time()` / `.is_burning()`, everything you'd need to build a custom cooking-progress display.

### Beacons

`get_container()` plus `.get_primary_effect()` / `.get_secondary_effect()` (raw status effect ids, `-1` if unset) / `.get_levels()` (pyramid tier, `0`-`4`).

### Jukeboxes

`get_container()` (the disc slot) plus `.is_playing()` / `.stop_playing()` / `.start_playing(length_in_ticks)`.

## Everything else, at a glance

The rest are read-only accessors specific to that one block type, all reachable the same way, `entity.get_block_entity()` back to the shared base, plus:

| Block entity | Extra accessors |
|---|---|
| `MobSpawnerBlockEntity` | `get_spawn_count`, `get_spawn_range`, `get_delay` |
| `MapBlockEntity` | `get`/`set_map_id`, `get`/`set_colors`, `get`/`set_pixel(x, y[, color])`, `update`, `stream_frame(data)` (the only block entity with real write access beyond containers/signs) |
| `BannerBlockEntity` | `get_custom_name` |
| `BeehiveBlockEntity` | `get_bee_count` |
| `BellBlockEntity` | `is_ringing`, `get_ring_ticks` |
| `ChiseledBookshelfBlockEntity` | `get_container`, `get_last_interacted_slot` |
| `ComparatorBlockEntity` | `get_output_signal` |
| `CopperGolemStatueBlockEntity` | (base only) |
| `CrafterBlockEntity` | `get_container`, `get_crafting_ticks_remaining`, `is_triggered` |
| `CreakingHeartBlockEntity` | `get_creaking_uuid` |
| `EndGatewayBlockEntity` | `get_age`, `is_exact_teleport` |
| `EnderChestBlockEntity` | `viewer_count` (always `0` for now) |
| `HopperBlockEntity` | `get_container`, `get_cooldown` |
| `JigsawBlockEntity` | `get_name`, `get_target`, `get_pool`, `get_final_state`, `get_selection_priority`, `get_placement_priority` |
| `LecternBlockEntity` | `get_container`, `get_page` |
| `PistonBlockEntity` | `get_progress`, `is_extending`, `is_source` |
| `SculkShriekerBlockEntity` | `get_warning_level` |
| `SkullBlockEntity` | `get_note_block_sound` |
| `StructureBlockBlockEntity` | `get_name`, `get_author`, `get_mode`, `get_integrity`, `get_seed` |
| `CommandBlockEntity` | `last_output`, `track_output`, `success_count`, `command`, `auto`, `condition_met`, `powered` |
| `BrewingStandBlockEntity` | `get_container`, `get_brew_time`, `get_fuel` |
| `DispenserBlockEntity`, `DropperBlockEntity`, `ShelfBlockEntity`, `CampfireBlockEntity` | `get_container` only |
| `BedBlockEntity`, `BrushableBlockBlockEntity`, `CalibratedSculkSensorBlockEntity`, `ConduitBlockEntity`, `DaylightDetectorBlockEntity`, `DecoratedPotBlockEntity`, `EnchantingTableBlockEntity`, `EndPortalBlockEntity`, `PotentSulfurBlockEntity`, `SculkCatalystBlockEntity`, `SculkSensorBlockEntity`, `TestBlockBlockEntity`, `TestInstanceBlockBlockEntity`, `TrialSpawnerBlockEntity`, `VaultBlockEntity` | base `BlockEntity` only, no extra state exposed yet |

For the exact method signatures of any of these, `block-entity.wit` in the [WIT source](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/blob/master/v0.1/block-entity.wit) is short and readable enough to check directly.

## Putting it together

Reading a chest's contents and reporting whether it's empty, from a right-click event handler that already has a `block_pos`:

```rust
use pumpkin_plugin_api::{block_entity::BlockEntityType, common::BlockPos};

fn inspect_chest(world: &World, pos: BlockPos) {
  let Some(BlockEntityType::ChestBlockEntity(chest)) = world.get_block_entity(pos) else {
    return;
  };

  let container = chest.get_container();
  if container.is_empty() {
    tracing::info!("Chest at ({}, {}, {}) is empty.", pos.x, pos.y, pos.z);
  } else {
    tracing::info!("Chest has {} slots, not all empty.", container.get_size());
  }
}
```

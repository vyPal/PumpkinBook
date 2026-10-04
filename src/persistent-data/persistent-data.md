# The PersistentDataHolder API

[Data persistence](../plugin-101/data-persistence.md) covers *your own* files, a config, a database, anything you manage yourself in the plugin's data folder. `PersistentDataHolder` is a different thing: namespaced custom data attached directly to a specific game object, an item, an entity, a block entity, a chunk, a world, or a player, that gets saved and loaded automatically along with that object. Tag an item with a custom identifier and it survives being picked up, dropped, and traded, no extra bookkeeping required on your end.

```rust
use pumpkin_plugin_api::PersistentDataHolder;
```

Bringing the trait into scope is enough, its methods then show up directly on `ItemStack`, `Entity`, `BlockEntity`, `Chunk`, `World`, and `Player`.

## Typed values

For each primitive NBT type there's a `set_*`/`get_*` pair, both namespaced by a `(namespace, key)` string pair (use your plugin's name as the namespace to avoid colliding with other plugins):

- `set_string` / `get_string`
- `set_int` / `get_int`, `set_long` / `get_long`, `set_short` / `get_short`, `set_byte` / `get_byte`
- `set_bool` / `get_bool` (stored as an NBT byte, `0`/`1`, under the hood)
- `set_float` / `get_float`, `set_double` / `get_double`
- `set_byte_array` / `get_byte_array`, `set_int_array` / `get_int_array`, `set_long_array` / `get_long_array`

```rust
use pumpkin_plugin_api::{uuid, PersistentDataHolder};

item.set_string("my_plugin", "owner_uuid", &uuid::to_string(player.get_id()));
item.set_int("my_plugin", "charges", 3);

if let Some(charges) = item.get_int("my_plugin", "charges") {
  // ...
}
```

> [!NOTE]
> The getters are forgiving about narrower-to-wider conversions, `get_long` will happily read back a value that was stored with `set_int`, `set_short`, or `set_byte`, and `get_double` will read one stored with `set_float`. Reading with a *narrower* type than it was written with returns `None` instead, `get_int` won't read back a value stored with `set_long`.

## Checking & removing

### `.has_custom_data(namespace, key)` / `.remove_custom_data(namespace, key)` { data-since=0.1 }

Check whether a key is set at all (useful for distinguishing "never set" from "set to a default-looking value"), or remove it entirely.

## The raw NbtTree escape hatch

The typed helpers above all funnel through two lower-level methods that are also available directly: `.set_custom_data(namespace, key, value)` / `.get_custom_data(namespace, key)`, working with a raw `NbtTree` instead of a single primitive. Reach for these when you need a nested structure (a compound with multiple fields, or a list) instead of one flat value.

An `NbtTree` is `{ root: u32, tags: list<NbtTag> }`, a flat array of tags where `root` is the index of the "top" tag, and compound/list tags reference their children by index into that same array rather than nesting directly. Building one by hand looks like this:

```rust
use pumpkin_plugin_api::common::{NbtEntry, NbtTag, NbtTree};

let tree = NbtTree {
  root: 2, // the Compound tag below is the top-level value
  tags: vec![
    NbtTag::StringTag("Steve".to_string()), // index 0
    NbtTag::Int(42),                        // index 1
    NbtTag::Compound(vec![
      NbtEntry { key: "name".to_string(), value: 0 },
      NbtEntry { key: "score".to_string(), value: 1 },
    ]), // index 2, this is what `root` points at
  ],
};

item.set_custom_data("my_plugin", "profile", &tree);
```

## What this works on

`PersistentDataHolder` is implemented for `ItemStack`, `Entity`, `BlockEntity`, `Chunk`, `World`, and `Player`. It isn't a separate storage system for each, it's a thin, ergonomically-typed wrapper over the same `set_custom_data`/`get_custom_data`/`remove_custom_data`/`has_custom_data` calls documented directly on [entities](../world/entities-basics.md) and [the world handle](../world/world-and-time.md), calling either form reads and writes the same underlying data. `Player`'s implementation forwards to `player.as_entity()`, so a player's persistent data actually lives on their entity, the same storage a `PlayerJoinEvent`'s `event.player.as_entity()` would see.

## Putting it together

An item enchanter that limits a custom item to three uses, tracked directly on the item stack so the limit follows it even if it's dropped, picked up by someone else, or put in a chest:

```rust
use pumpkin_plugin_api::{ItemStack, PersistentDataHolder};

fn try_use_charged_item(item: &ItemStack) -> bool {
  let charges = item.get_int("my_plugin", "charges").unwrap_or(3);

  if charges <= 0 {
    return false;
  }

  item.set_int("my_plugin", "charges", charges - 1);
  true
}
```

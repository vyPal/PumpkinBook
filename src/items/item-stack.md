# Item stacks

`ItemStack` is what you build to put in an inventory slot, drop in the world, or check against what a player's holding, an item type plus a count plus whatever extra data (enchantments, lore, a custom name) makes that particular stack special.

## Creating one

### `ItemStack::new(registry_key, count)`

The constructor takes a registry key (`"minecraft:diamond_sword"`) and a stack count.

```rust
use pumpkin_plugin_api::ItemStack;

let sword = ItemStack::new("minecraft:diamond_sword", 1);
```

### `.get_registry_key()` / `.get_count()` / `.set_count(count)` / `.get_max_count()`

The item's registry key, its current stack size, a setter for the stack size, and the maximum stack size for this item type (`1` for tools and weapons, `64` for most blocks and materials, some items cap lower).

## Enchantments

### `.get_enchantments()` / `.add_enchantment(enchantment, level)` / `.remove_enchantment(enchantment)`

Vanilla enchantments, addressed by the `Enchantment` enum. `get_enchantments()` returns a list of `EnchantmentValue { enchantment, level }`.

```rust
use pumpkin_plugin_api::enchantments_wit::Enchantment;

sword.add_enchantment(Enchantment::Sharpness, 5);
sword.add_enchantment(Enchantment::FireAspect, 2);
```

### `.get_custom_enchantments()` / `.add_custom_enchantment(id, level)` / `.remove_custom_enchantment(id)` / `.get_custom_enchantment_level(id)` / `.has_custom_enchantment(id)`

The same shape, but for enchantments a plugin registered itself (see [Custom enchantments](./enchantments.md)), addressed by their string id rather than the `Enchantment` enum.

## Lore & display name

### `.get_lore()` / `.set_lore(lore)` / `.add_lore(line)`

The lore is a list of `TextComponent`s, one per line, shown below the item's name in its tooltip. `set_lore` replaces the whole list, `add_lore` appends a single line.

### `.get_custom_name()` / `.set_custom_name(name)`

An optional `TextComponent` overriding the item's displayed name (the same mechanic as an anvil rename, but done in code). Pass `None` to clear a custom name and fall back to the item's default display name.

```rust
use pumpkin_plugin_api::{common::NamedColor, text::TextComponent};

let name = TextComponent::text("Excalibur");
name.color_named(NamedColor::Aqua);
name.bold(true);
sword.set_custom_name(Some(name));
```

## Custom & persistent data

### `.set_custom_data(namespace, key, value)` / `.get_custom_data(namespace, key)` / `.remove_custom_data(namespace, key)` / `.has_custom_data(namespace, key)`

Raw namespaced NBT storage attached to this specific stack, persisted with it. See [Persistent Data](../persistent-data/persistent-data.md) for the typed `PersistentDataHolder` wrapper built on top of these same calls, it's implemented for `ItemStack` and is almost always the nicer way to use this.

## Data components

### `.get_components()` / `.set_component(component, value)` / `.remove_component(component)`

The lowest-level way to read or write an item's data components (Minecraft's post-1.20.5 item data model, `DataComponent::Unbreakable`, `DataComponent::MaxDamage`, `DataComponent::Rarity`, and so on), as raw serialized bytes rather than a strongly-typed value. Most of what you'd reach for this to do (enchantments, lore, custom name, custom data) already has a dedicated typed method above, use this only for a component that doesn't.

## Putting it together

A custom "starter sword" given to new players: a named, lightly enchanted item with a plugin-tracked identifier so it can be recognized later (for example, to stop it from being enchanted further at an enchanting table):

```rust
use pumpkin_plugin_api::{
  common::NamedColor, enchantments_wit::Enchantment, text::TextComponent,
  ItemStack, PersistentDataHolder,
};

fn starter_sword() -> ItemStack {
  let sword = ItemStack::new("minecraft:iron_sword", 1);

  let name = TextComponent::text("Starter Blade");
  name.color_named(NamedColor::Yellow);
  sword.set_custom_name(Some(name));

  sword.add_lore(TextComponent::text("A trusty first weapon."));
  sword.add_enchantment(Enchantment::Sharpness, 1);

  sword.set_bool("my_plugin", "starter_item", true);

  sword
}
```

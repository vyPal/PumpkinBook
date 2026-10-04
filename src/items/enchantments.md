# Custom enchantments

Register brand new enchantments (not just apply vanilla ones, covered in [Item stacks](./item-stack.md)) through the `EnchantmentManager`, reached via `context.get_enchantment_manager()` or `server.get_enchantment_manager()`.

## Defining one

### `EnchantmentBuilder::new(id, description)` { data-since=0.1 }

`description` is a `TextComponent`, the name shown for the enchantment in tooltips and the enchanting table.

```rust
use pumpkin_plugin_api::{enchantment::{AttributeModifierSlot, EnchantmentBuilder}, text::TextComponent};

fn register_enchantments(server: &Server) {
  let manager = server.get_enchantment_manager();

  manager.register(
    EnchantmentBuilder::new("my_plugin:lifesteal", TextComponent::text("Life Steal"))
      .max_level(3)
      .anvil_cost(4)
      .supported_items("#minecraft:enchantable/weapon")
      .weight(2)
      .slots([AttributeModifierSlot::MainHand])
      .exclusive_with("custom:poison_touch")
  ).expect("failed to register custom enchantment");
}
```

- `.max_level(n)` sets how high it can go (default `1`).
- `.anvil_cost(n)` sets the base anvil cost multiplier per level (default `4`).
- `.supported_items(tag_or_pattern)` restricts which items can receive it, usually a tag like `"#minecraft:enchantable/weapon"` (default), matching how vanilla enchantments gate themselves to weapons, armor, tools, and so on.
- `.weight(n)` sets rarity (`1`-`10`, higher is more common at the enchanting table, default `5`).
- `.slot(slot)` / `.slots([...])` sets which `AttributeModifierSlot`s the enchantment is actually active in when equipped (default `[MainHand]`), an enchantment on an item sitting in the wrong slot doesn't apply its effect.
- `.exclusive_with(id)` / `.exclusive_set([...])` marks other enchantment ids this one can't coexist with on the same item (mirrors how vanilla Sharpness/Smite/Bane of Arthropods exclude each other).

Registering validates first, `EnchantmentError::EmptyId` for a blank id, `InvalidMaxLevel` if `max_level` is `0`, or `RegistrationFailed(reason)` if the server rejects it (a duplicate id, for example).

Same shortcuts as recipes: `manager.register(builder)`, or `context.register_enchantment(builder)`/`server.register_enchantment(builder)` if you'd rather not fetch the manager first.

## Applying one to an item

Custom enchantments live on `ItemStack` the same way vanilla ones do, but addressed by id string instead of the `Enchantment` enum, see [Item stacks](./item-stack.md#enchantments):

```rust
fn give_sword() -> ItemStack {
  let sword = ItemStack::new("minecraft:diamond_sword", 1);
  sword.add_custom_enchantment("my_plugin:lifesteal", 2);

  assert!(sword.has_custom_enchantment("my_plugin:lifesteal"));
  assert_eq!(sword.get_custom_enchantment_level("my_plugin:lifesteal"), Some(2));

  sword
}
```

## Looking enchantments up

### `manager.get(id)` / `manager.has(id)` / `manager.get_all_ids()` { data-since=0.1 }

Friendlier-named aliases for `get_enchantment`/`has_enchantment`/`get_all_enchantment_ids`, work for both custom and vanilla enchantment ids.

## A small helper: Roman numerals

### `enchantment::to_roman_numeral(level)` { data-since=0.1 }

Converts a level number to the Roman numeral Minecraft tooltips traditionally use (`1` → `"I"`, `4` → `"IV"`, and so on, `1`-`10` covered, anything higher falls back to the plain number).

```rust
use pumpkin_plugin_api::enchantment::to_roman_numeral;

let label = format!("Life Steal {}", to_roman_numeral(3)); // "Life Steal III"
```

## Putting it together

Registering a two-level custom enchantment and applying it to a starter item:

```rust
use pumpkin_plugin_api::{
  enchantment::{to_roman_numeral, AttributeModifierSlot, EnchantmentBuilder},
  text::TextComponent, Context, ItemStack, Result,
};

fn on_load(&self, context: Context) -> Result<()> {
  context.register_enchantment(
    EnchantmentBuilder::new("my_plugin:vampiric", TextComponent::text("Vampiric"))
      .max_level(2)
      .weight(1)
      .supported_items("#minecraft:enchantable/sword")
      .slots([AttributeModifierSlot::MainHand])
  ).map_err(|e| e.to_string())?;

  Ok(())
}

fn starter_vampiric_sword() -> ItemStack {
  let sword = ItemStack::new("minecraft:iron_sword", 1);
  sword.add_custom_enchantment("my_plugin:vampiric", 1);

  let name = TextComponent::text(&format!("Vampiric Blade {}", to_roman_numeral(1)));
  sword.set_custom_name(Some(name));

  sword
}
```

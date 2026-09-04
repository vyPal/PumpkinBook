# Custom GUIs

`Gui` is an inventory-based custom UI, the same mechanism a chest or crafting table screen uses, but populated and controlled entirely by your plugin. Shown to a player with `player.open_gui(gui_ref)`, see [Inventory & environment](../players/player-inventory-and-environment.md).

## Creating one

### `Gui::new(type, title)`

`type` is a `Screen` (`Generic9x1` through `Generic9x6` for plain chest-style rows, `Generic3x3`/`Crafter3x3`, or a themed layout like `Anvil`, `Beacon`, `Merchant`, `Furnace`, `Hopper`, `Loom`, `Smithing`, `Stonecutter`, and others matching vanilla screen types), `title` is a `TextComponent` shown at the top.

```rust
use pumpkin_plugin_api::{gui::Gui, Screen, text::TextComponent};

let menu = Gui::new(Screen::Generic9x3, TextComponent::text("Shop"));
```

## Items

### `.set_item(slot, item)` / `.get_item(slot)` / `.clear_items()`

Places or reads an `ItemStack` in a slot (indexed left-to-right, top-to-bottom, `0`-based), or empties every slot at once. `.get_size()` tells you how many slots the current `Screen` type actually has, so you don't hardcode a slot count that only matches one layout.

```rust
use pumpkin_plugin_api::ItemStack;

menu.set_item(13, ItemStack::new("minecraft:diamond", 1));
```

### `.get_inventory()`

Returns the GUI's contents as a generic `Inventory` handle, the same type used for player inventories and containers (see [Inventory & environment](../players/player-inventory-and-environment.md#inventory-handles)). Useful if you're writing code that works against any `Inventory`-shaped thing rather than `Gui` specifically, `set_item`/`get_item` above are the more direct way to work with a GUI on its own.

## Interaction permissions

### `.set_allow_grab_items(allow)` / `.get_allow_grab_items()` / `.set_allow_put_items(allow)` / `.get_allow_put_items()`

By default a custom GUI behaves like a normal inventory, players can take items out and put their own items in. For a menu-style GUI (buttons, not storage), turn both off so the "items" act as inert, clickable icons instead of things players can walk away with.

```rust
menu.set_allow_grab_items(false);
menu.set_allow_put_items(false);
```

> [!NOTE]
> Locking grabbing/putting stops items moving in and out of the slots, but clicks still happen. You'll want an `InventoryClickEvent` handler (see the Inventory events listed in [Event handlers](../plugin-101/event-handlers.md)) to actually respond to which slot was clicked, this resource only covers the GUI's contents and permissions, not click handling.

## Putting it together

A simple two-item shop menu with grabbing disabled, so clicking is the only way to interact with it:

```rust
use pumpkin_plugin_api::{gui::Gui, Screen, text::TextComponent, ItemStack};

fn open_shop(player: &Player) {
  let menu = Gui::new(Screen::Generic9x1, TextComponent::text("Quick Shop"));
  menu.set_allow_grab_items(false);
  menu.set_allow_put_items(false);

  menu.set_item(2, ItemStack::new("minecraft:bread", 1));
  menu.set_item(6, ItemStack::new("minecraft:apple", 1));

  player.open_gui(menu);
}
```

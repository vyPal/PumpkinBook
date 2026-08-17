# Inventory & environment

The rest of what `Player` exposes: hotbar and inventory slots, the ender chest, skins, per-player time/weather/compass/respawn overrides, visibility between players, raycasting, and opening a GUI.

## Inventory

### `.get_selected_slot()`

The index (0-8) of the player's currently selected hotbar slot.

### `.get_item_in_hand(hand)` / `.set_item_in_hand(hand, stack)`

Reads or replaces whatever's in the player's main or off hand (a `Hand::Left`/`Hand::Right`). Both work with `Option<ItemStack>`, pass `None` to empty the hand. See [Item stacks](../items/item-stack.md) for building an `ItemStack`.

### `.get_inventory_item(slot)` / `.set_inventory_item(slot, stack)`

Reads or sets any slot in the player's main inventory by index (not just the hotbar), same `Option<ItemStack>` shape as above.

## Ender chest

### `.get_ender_chest_item(slot)` / `.set_ender_chest_item(slot, stack)`

Reads or sets one of the 27 ender chest slots (0-26).

### `.clear_ender_chest()` / `.open_ender_chest()`

Empties the ender chest entirely, or opens the ender chest screen for the player (as if they'd right-clicked one in the world).

## Skin & appearance

### `.get_skin()` / `.set_skin(skin)`

A `PlayerSkin` is just `value` (base64-encoded texture data, usually JSON containing skin/cape URLs) and an optional `signature`.

> [!NOTE]
> `set_skin` only updates the stored skin fields, it doesn't force the client to reload the skin on other players' screens by itself. Expect a delay or a manual re-join before the change is visible to others, the same limitation vanilla skin-changing plugins run into.

### `.get_skin_parts()` / `.set_skin_parts(parts)`

Which skin layers the player has toggled on in their client settings (cape, jacket, sleeves, pant legs, hat), as a `SkinParts` flag set. This reflects the player's own client-side choice, not something you'd normally override, but it's readable and settable.

## Per-player environment overrides

These override what a specific player sees, independent of the actual state of the world they're in.

### `.set_player_time(time, relative)` / `.reset_player_time()` / `.get_player_time()` / `.is_player_time_relative()`

Overrides the time of day shown to just this player. `relative: true` keeps it moving in sync with the world's real time offset by `time`, `relative: false` freezes it at that exact tick. `reset_player_time` goes back to showing the world's actual time.

### `.set_player_weather(weather)` / `.reset_player_weather()` / `.get_player_weather()`

Same idea for weather, a `PlayerWeather` of `Clear` or `Downfall`, shown only to this player regardless of what's actually happening in their world.

### `.set_compass_target(pos)` / `.get_compass_target()`

Where this player's compass points. Doesn't need a lodestone, works with a plain compass too.

### `.set_respawn_location(pos)` / `.get_respawn_location()`

The player's bed/respawn point override.

## Visibility

### `.hide_player(other)` / `.show_player(other)`

Hides or reveals `other` from this player's client (a "vanish" mechanic), the hidden player doesn't disappear from the world for anyone else, just from this specific viewer.

### `.can_see(other)` / `.can_see_player(other)`

> [!NOTE]
> These two methods currently do exactly the same thing, both check the same underlying visibility state. Use whichever name reads better in your code.

## Item cooldown overlay

### `.set_item_cooldown(item_id, ticks)` / `.get_item_cooldown(item_id)` / `.has_item_cooldown(item_id)`

A purely client-side cooldown swipe animation over an item, keyed by item id (e.g. `"minecraft:ender_pearl"`) rather than an arbitrary group name. This doesn't stop the player from using the item again, it's visual only, if you want an actual enforced cooldown, use `start_cooldown`/`is_on_cooldown` from [Health, effects & stats](./player-status.md) instead.

## Raycasting & projectiles

### `.get_target_block(max_distance)`

Raycasts from the player's eyes along their line of sight, up to `max_distance` blocks, and returns the position of the first block hit, or `None` if nothing's in range.

> [!NOTE]
> Despite the name, this returns a `Position` (the `(f64, f64, f64)` precise-coordinate tuple), not a `BlockPos`. Round the components down (`.floor()`) if you need the actual integer block coordinates to pass to something like `world.get_block_state`.

### `.launch_projectile(type)`

Spawns and launches a `ProjectileType` (`Arrow`, `Snowball`, `Egg`, `EnderPearl`, `SplashPotion`, `Fireball`, `SmallFireball`, `Trident`, `WindCharge`) from the player's eyes in their current facing direction, as if they'd thrown or shot it. Returns the spawned `Entity`, if the throw succeeded.

## Opening a GUI

### `.open_gui(gui_ref)`

Opens a custom inventory-based GUI for the player. Building the `Gui` itself is covered in [Custom GUIs](../ui/gui.md).

## Putting it together

A `/lookat` command that reports the block the sender is looking at, up to 100 blocks away:

```rust
use pumpkin_plugin_api::{command::CommandSender, text::TextComponent};

fn lookat(sender: &CommandSender) {
  let Some(player) = sender.as_player() else {
    sender.send_message(TextComponent::text("Players only."));
    return;
  };

  match player.get_target_block(100) {
    Some((x, y, z)) => {
      let msg = format!(
        "You're looking at block ({}, {}, {}).",
        x.floor(), y.floor(), z.floor()
      );
      sender.send_message(TextComponent::text(&msg));
    }
    None => sender.send_message(TextComponent::text("Nothing in range.")),
  }
}
```

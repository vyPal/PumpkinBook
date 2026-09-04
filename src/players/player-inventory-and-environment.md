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

## Inventory handles

### `.get_inventory()` / `.get_ender_chest()`

A newer, handle-based alternative to the flat slot methods above. `get_inventory()` returns a `PlayerInventory`, `get_ender_chest()` returns a plain `Inventory` (the same generic type used by GUIs and containers, see [Custom GUIs](../ui/gui.md) and [Block entities](../world/block-entities.md#containers)). Both remain valid, the flat methods are more convenient for a single slot, the handle is more convenient for bulk operations like iterating or counting items.

`Inventory` (also what `PlayerInventory::as_inventory()` and `get_ender_chest()` return): `.get_size()`, `.is_empty()`, `.get_item(slot)` / `.set_item(slot, item)` / `.remove_item(slot)`, `.clear()`, `.get_all_items()` / `.set_all_items(items)` (the whole inventory as one `Vec<Option<ItemStack>>`), `.count_item(item_id)` / `.contains_item(item_id)` (matches by registry key, summed or checked across every slot).

`PlayerInventory` adds equipment-specific accessors on top: `.as_inventory()` (the 36-slot hotbar + main storage, as a plain `Inventory`), `.get_item_in_hand(hand)` / `.set_item_in_hand(hand, item)`, `.get_selected_slot()` / `.set_selected_slot(slot)`, `.get_helmet()` / `.set_helmet(item)`, `.get_chestplate()` / `.set_chestplate(item)`, `.get_leggings()` / `.set_leggings(item)`, `.get_boots()` / `.set_boots(item)`, `.get_off_hand()` / `.set_off_hand(item)`, `.clear_armor()` / `.clear_main()` / `.clear_all()`.

```rust
use pumpkin_plugin_api::ItemStack;

fn count_diamonds(player: &Player) -> u32 {
  player.get_inventory().as_inventory().count_item("minecraft:diamond")
}
```

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

### `.get_target_block_exact(max_distance, include_fluids)` / `.ray_trace_block(max_distance, include_fluids)` / `.ray_trace_entity(max_distance)` / `.get_target_entity(max_distance)`

The richer versions of the raycast above. `get_target_block_exact` and `ray_trace_block` both return `Option<RayTraceBlockResult> { pos, face, hit_pos }`, a `BlockPos` (not the raw-coordinate `Position` that `get_target_block` returns), which face was hit, and the exact hit coordinates, `include_fluids` controls whether the ray stops on fluids as if solid. `ray_trace_entity`/`get_target_entity` do the entity equivalent, `ray_trace_entity` returns the fuller `Option<RayTraceEntityResult> { entity, hit_pos, distance }`, `get_target_entity` is the shortcut when you just want the `Entity`. Same result types as the entity-side raycast API, see [Entities: identity & movement](../world/entities-basics.md#raycasting).

### `.launch_projectile(type)`

Spawns and launches a `ProjectileType` (`Arrow`, `Snowball`, `Egg`, `EnderPearl`, `SplashPotion`, `Fireball`, `SmallFireball`, `Trident`, `WindCharge`) from the player's eyes in their current facing direction, as if they'd thrown or shot it. Returns the spawned `Entity`, if the throw succeeded.

## Camera & spectating

### `.set_camera(entity)` / `.set_camera_entity_id(entity_id)` / `.get_camera_entity_id()` / `.reset_camera()`

Overrides what the player's client renders from, the player's view attaches to `entity`'s position and rotation instead of their own, without actually changing the player's real position (the classic "spectator camera" trick, also usable for cutscenes). Pass `None` to `set_camera` (or the player's own entity id to `set_camera_entity_id`) to snap the view back, `reset_camera` is the explicit shortcut for that. `get_camera_entity_id` returns the player's own entity id when the camera hasn't been overridden.

## Audio & particles

### `.play_sound(sound, category, volume, pitch)` / `.play_sound_at(pos, sound, category, volume, pitch)` / `.stop_sound(sound, category)`

Plays or stops a vanilla sound for just this player, at their current location or an arbitrary position.

> [!WARNING]
> These three take a `Sound` value, and, same as `World::play_sound` (see [The world handle](../world/world-and-time.md#sound--particles)), `pumpkin-plugin-api` doesn't currently export the `Sound` enum publicly. There's no supported way to call `play_sound`, `play_sound_at`, or `stop_sound` from a plugin right now.

### `.play_custom_sound(sound_name, category, volume, pitch)` / `.play_custom_sound_at(pos, sound_name, category, volume, pitch)` / `.stop_custom_sound(sound_name, category)`

The workaround: these take a plain resource-pack sound identifier string instead of the unexported `Sound` enum, so they're fully callable today. Use these for any custom sound your resource pack ships, and for vanilla sounds until `Sound` is exported, by passing the vanilla sound's namespaced id as a string.

```rust
player.play_custom_sound("minecraft:entity.experience_orb.pickup", SoundCategory::Players, 1.0, 1.0);
```

### `.spawn_particles(particle, pos, count, offset, max_speed)`

Spawns particles visible only to this player (contrast with `World::spawn_particle`, visible to everyone). Same `Particle` enum, same parameter shape, see [The world handle](../world/world-and-time.md#sound--particles).

## Visuals & client overrides

### `.send_block_change(pos, block_id)` / `.reset_block_change(pos)`

Sends a fake block change visible only to this player's client, without touching the real world, ghost blocks, previews, that sort of thing. `reset_block_change` resends the block's actual server-side state to undo it.

### `.send_hurt_animation(yaw)`

Triggers the client's damage-tilt screen shake in the given facing direction, without dealing any actual damage.

### `.open_book(hand)` / `.open_sign_editor(pos, is_front_text)`

Forces open the written-book reading interface for whatever's in the given `Hand`, or forces open the sign-text editor for a sign at `pos` (front or back text).

## Velocity & physics

### `.set_velocity(velocity)` / `.apply_knockback(strength, x, z)`

`set_velocity` overwrites the player's motion vector outright, same shape as the entity version. `apply_knockback` applies a directional impulse instead, `strength` scaling the push and `x`/`z` giving the horizontal direction, matching how vanilla knockback enchantments and explosions push players.

## Movement lock & freezing

### `.set_movement_locked(locked)` / `.is_movement_locked()`

Freezes the player in place client-side, for cutscenes or NPC dialogue where you don't want them wandering off mid-conversation.

### `.set_freeze_ticks(ticks)` / `.get_freeze_ticks()`

The powdered-snow freeze effect's tick counter, driving the frostbite screen vignette. Same mechanic as the `Mob`/`LivingEntity` version, see [Entities: attributes & AI](../world/entities-attributes-and-ai.md#ai-goals).

## Server links & chat moderation

### `.set_server_links(links)`

Sets the custom links shown in this player's Esc pause menu (Java 1.21+), a per-player version of `Server::set_server_links`, see [Server info & worlds](../server/server-info-and-worlds.md#messaging) for the `ServerLink`/`ServerLinkLabel` shape.

### `.delete_message_by_signature(signature)` / `.delete_message_by_id(signature_id)`

Deletes a signed chat message from this player's chat window only, the per-player version of `Server::delete_message_by_signature`/`delete_message_by_id`, see [Server info & worlds](../server/server-info-and-worlds.md#messaging).

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

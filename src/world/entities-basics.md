# Entities: identity & movement

`Entity` covers every non-player thing that moves through a world: mobs, dropped items, projectiles, minecarts, and so on, players included, `player.as_entity()` gives you the same kind of handle (see [Identity, state & permissions](../players/player-basics.md)). You get an `Entity` from `world.spawn_entity(...)`, `world.get_entities()`, or from event data. This page covers identity, movement, naming, state flags, health, and passengers. Attributes, equipment, targeting, and AI goals get their own chapter, [Entities: attributes & AI](./entities-attributes-and-ai.md).

## Identity

### `.get_id()` / `.get_uuid()` / `.get_type()`

`get_id()` is a per-server-session numeric id (not stable across restarts), `get_uuid()` is the persistent UUID, `get_type()` returns the `EntityType` (`EntityType::Zombie`, `EntityType::Item`, and so on).

## Position & movement

### `.get_position()` / `.get_world()`

Current coordinates and the `World` this entity is in.

### `.get_yaw()` / `.get_pitch()` / `.get_head_yaw()` / `.set_rotation(yaw, pitch)`

Body yaw/pitch, plus a separate head yaw for entities that can look independently of their body (most mobs). `set_rotation` only sets body yaw/pitch, there's no separate head-yaw setter.

### `.teleport(pos, world_ref)`

Moves the entity, optionally across worlds, in one call (unlike `Player::teleport`/`Player::teleport_world` being two separate methods, entity teleport always takes a world).

### `.set_velocity(velocity)` / `.get_velocity()`

Reads or sets the entity's motion vector directly, as a `(f64, f64, f64)` per-axis speed, not a direction-and-magnitude.

### `.is_on_ground()`

Whether the entity is currently touching the ground.

## Naming

### `.get_name()`

The entity's default name as a `TextComponent` (for mobs without a custom name, this is their type name, e.g. "Zombie").

### `.set_custom_name(name)` / `.get_custom_name()` / `.set_custom_name_visible(visible)` / `.is_custom_name_visible()`

A custom nameplate independent of the entity's type name. Setting a custom name doesn't automatically make it visible above the entity's head, `set_custom_name_visible(true)` is a separate call for that (mirrors vanilla's `CustomName`/`CustomNameVisible` NBT split).

## State flags

Most of these are plain boolean getter/setter pairs, listed together since they all follow the same shape:

- `is_sneaking` / `set_sneaking`, `is_sprinting` / `set_sprinting`, `is_swimming` / `set_swimming`
- `is_invisible` / `set_invisible`, `is_glowing` / `set_glowing`, `is_fall_flying` / `set_fall_flying` (elytra gliding)
- `is_silent` / `set_silent` (suppresses ambient sounds), `has_gravity` / `set_has_gravity`
- `is_invulnerable` / `set_invulnerable`
- `is_on_fire` / `set_on_fire`, `has_visual_fire` / `set_visual_fire` (a fire render override independent of actually being on fire), `get_fire_ticks` / `set_fire_ticks`

### `.get_pose()`

The entity's current `EntityPose` (`Standing`, `Sleeping`, `Swimming`, `Crouching`, `Dying`, and others), read-only, driven by the entity's actual state rather than something you set directly.

### `.get_width()` / `.get_height()`

The entity's hitbox dimensions.

## Health & damage

### `.get_health()` / `.set_health(health)` / `.get_max_health()` / `.damage(amount, damage_type)` / `.is_dead()`

Same shape as the player health methods from [Health, effects & stats](../players/player-status.md), works on any entity, not just players. There's no `heal()` shortcut here like there is on `Player`, add to `get_health()` yourself and clamp to `get_max_health()`.

### `.get_absorption()` / `.set_absorption(amount)`

Absorption (extra) hearts, same concept as the player version.

## Other physical state

`get_age` / `set_age` (ticks since spawn, some mobs use this for baby/adult growth), `get_fall_distance` / `set_fall_distance`, `get_ticks_lived` / `set_ticks_lived`, `get_portal_cooldown` / `set_portal_cooldown`, `get_remaining_air` / `set_remaining_air` / `get_max_air` (drowning), `get_eye_height` / `get_eye_position`, `get_bounding_box`, `is_in_water` / `is_in_lava`.

## Messaging

### `.send_system_message(message)`

Sends a `TextComponent` to this entity, only meaningful for entities that are actually players under the hood, calling it on a non-player entity has no effect.

## Nearby entities & passengers

### `.get_nearby_entities(x, y, z)`

Returns every entity within `x`/`y`/`z` blocks on each axis of this entity's position (a box, not a sphere).

### `.get_vehicle()` / `.set_vehicle(vehicle)`

The entity this one is riding, if any. Setting `None` dismounts it.

### `.get_passengers()` / `.add_passenger(passenger)` / `.remove_passenger(passenger)` / `.eject_passengers()`

The entities riding this one, and controls for mounting/dismounting them.

## Custom data

### `.set_custom_data(namespace, key, value)` / `.get_custom_data(namespace, key)` / `.remove_custom_data(namespace, key)` / `.has_custom_data(namespace, key)`

Attaches your own namespaced NBT to the entity, persisted with it across saves. See [Persistent Data](../persistent-data/persistent-data.md) for the friendlier wrapper around these same calls.

## Removing an entity

### `.remove()`

Removes the entity from the world entirely, immediately, no drops, no death animation, no events. If you want a "real" death, use `.damage()` with enough force to bring health to zero instead.

## Putting it together

A lightning-rod style command that marks the entity the sender is looking at as permanently glowing and gives it a custom name, so it's easy to track:

```rust
use pumpkin_plugin_api::{command::CommandSender, text::TextComponent};

fn mark_target(sender: &CommandSender, target: &Entity) {
  target.set_glowing(true);
  target.set_custom_name(TextComponent::text("Marked"));
  target.set_custom_name_visible(true);

  sender.send_message(TextComponent::text("Target marked."));
}
```

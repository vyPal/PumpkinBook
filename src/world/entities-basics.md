# Entities: identity & movement

`Entity` covers every non-player thing that moves through a world: mobs, dropped items, projectiles, minecarts, and so on, players included, `player.as_entity()` gives you the same kind of handle (see [Identity, state & permissions](../players/player-basics.md)). You get an `Entity` from `world.spawn_entity(...)`, `world.get_entities()`, or from event data. This page covers identity, movement, naming, state flags, and passengers. Health, attributes, equipment, targeting, and AI goals live on two narrower handles you cast to, `LivingEntity` and `Mob`, covered in [Entities: attributes & AI](./entities-attributes-and-ai.md).

## Living entities & mobs

### `.as_living()` / `.is_living()` / `.as_mob()` / `.is_mob()` { data-since=0.1 }

Not every `Entity` has health or AI, a dropped item or a minecart doesn't. `as_living()` returns `Some(LivingEntity)` if this entity has health, attributes, and equipment (mobs, players, armor stands), `as_mob()` returns `Some(Mob)` if it's additionally an AI-driven mob (armor stands are living but not mobs). Both return `None` otherwise, and `is_living()`/`is_mob()` are the boolean-only versions when you don't need the handle itself.

```rust
use pumpkin_plugin_api::{text::TextComponent, world::Entity};

fn announce_hit(target: &Entity) {
  if let Some(living) = target.as_living() {
    let msg = format!("Hit for {} damage!", living.get_health());
    living.send_system_message(TextComponent::text(&msg));
  }
}
```

## Identity

### `.get_id()` / `.get_uuid()` / `.get_type()` { data-since=0.1 }

`get_id()` is a per-server-session numeric id (not stable across restarts), `get_uuid()` is the persistent UUID, `get_type()` returns the `EntityType` (`EntityType::Zombie`, `EntityType::Item`, and so on).

## Position & movement

### `.get_position()` / `.get_world()` { data-since=0.1 }

Current coordinates and the `World` this entity is in.

### `.get_yaw()` / `.get_pitch()` / `.get_head_yaw()` / `.set_rotation(yaw, pitch)` { data-since=0.1 }

Body yaw/pitch, plus a separate head yaw for entities that can look independently of their body (most mobs). `set_rotation` only sets body yaw/pitch, there's no separate head-yaw setter.

### `.teleport(pos, world_ref)` { data-since=0.1 }

Moves the entity, optionally across worlds, in one call (unlike `Player::teleport`/`Player::teleport_world` being two separate methods, entity teleport always takes a world).

### `.set_velocity(velocity)` / `.get_velocity()` { data-since=0.1 }

Reads or sets the entity's motion vector directly, as a `(f64, f64, f64)` per-axis speed, not a direction-and-magnitude.

### `.is_on_ground()` { data-since=0.1 }

Whether the entity is currently touching the ground.

## Naming

### `.get_name()` { data-since=0.1 }

The entity's default name as a `TextComponent` (for mobs without a custom name, this is their type name, e.g. "Zombie").

### `.set_custom_name(name)` / `.get_custom_name()` / `.set_custom_name_visible(visible)` / `.is_custom_name_visible()` { data-since=0.1 }

A custom nameplate independent of the entity's type name. Setting a custom name doesn't automatically make it visible above the entity's head, `set_custom_name_visible(true)` is a separate call for that (mirrors vanilla's `CustomName`/`CustomNameVisible` NBT split).

## State flags

Most of these are plain boolean getter/setter pairs, listed together since they all follow the same shape:

- `is_sneaking` / `set_sneaking`, `is_sprinting` / `set_sprinting`, `is_swimming` / `set_swimming`
- `is_invisible` / `set_invisible`, `is_glowing` / `set_glowing`, `is_fall_flying` / `set_fall_flying` (elytra gliding)
- `is_silent` / `set_silent` (suppresses ambient sounds), `has_gravity` / `set_has_gravity`
- `is_invulnerable` / `set_invulnerable`
- `is_on_fire` / `set_on_fire`, `has_visual_fire` / `set_visual_fire` (a fire render override independent of actually being on fire), `get_fire_ticks` / `set_fire_ticks`

### `.get_pose()` { data-since=0.1 }

The entity's current `EntityPose` (`Standing`, `Sleeping`, `Swimming`, `Crouching`, `Dying`, and others), read-only, driven by the entity's actual state rather than something you set directly.

### `.get_width()` / `.get_height()` { data-since=0.1 }

The entity's hitbox dimensions.

## Other physical state

`get_fall_distance` / `set_fall_distance`, `get_ticks_lived` / `set_ticks_lived`, `get_portal_cooldown` / `set_portal_cooldown`, `get_remaining_air` / `set_remaining_air` / `get_max_air` (drowning), `get_eye_height` / `get_eye_position`, `get_bounding_box`, `is_in_water` / `is_in_lava`.

> [!NOTE]
> Health, absorption, age, and `send_system_message` moved off the base `Entity` onto `LivingEntity` as of the entity-model split (see [Living entities & mobs](#living-entities--mobs) above). Cast with `.as_living()` first if you need any of those.

## Raycasting

### `.raycast(max_distance, fluid_handling)` / `.ray_trace_block(max_distance, include_fluids)` / `.ray_trace_entity(max_distance)` / `.get_target_entity(max_distance)` { data-since=0.1 }

Casts a ray from this entity's eye position in its facing direction, up to `max_distance` blocks. `raycast`/`ray_trace_block` take a `fluid_handling`/`include_fluids` flag that lets the ray stop on fluids as if they were solid; `raycast` returns the older `RaycastResult { pos, face }` (block position and `BlockDirection` face), while `ray_trace_block` returns the richer `RayTraceBlockResult { pos, face, hit_pos }` with the exact hit coordinates. `ray_trace_entity` finds the closest entity along the ray and returns `RayTraceEntityResult { entity, hit_pos, distance }`; `get_target_entity` is the shortcut when you just want the `Entity` itself.

## Nearby entities & passengers

### `.get_nearby_entities(x, y, z)` { data-since=0.1 }

Returns every entity within `x`/`y`/`z` blocks on each axis of this entity's position (a box, not a sphere).

### `.get_vehicle()` / `.set_vehicle(vehicle)` { data-since=0.1 }

The entity this one is riding, if any. Setting `None` dismounts it.

### `.get_passengers()` / `.add_passenger(passenger)` / `.remove_passenger(passenger)` / `.eject_passengers()` { data-since=0.1 }

The entities riding this one, and controls for mounting/dismounting them.

## Custom data

### `.set_custom_data(namespace, key, value)` / `.get_custom_data(namespace, key)` / `.remove_custom_data(namespace, key)` / `.has_custom_data(namespace, key)` { data-since=0.1 }

Attaches your own namespaced NBT to the entity, persisted with it across saves. See [Persistent Data](../persistent-data/persistent-data.md) for the friendlier wrapper around these same calls.

## Removing an entity

### `.remove()` { data-since=0.1 }

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

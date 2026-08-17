# Entities: attributes & AI

The rest of `Entity`: attribute modifiers, equipment slots, targeting, raycasting, and AI goals for mobs. Continues from [Entities: identity & movement](./entities-basics.md).

## Attributes

### `.get_attribute_value(attr)` / `.get_attribute_base(attr)` / `.set_attribute_base(attr, value)`

`get_attribute_value` returns the *computed* value of an `Attribute` (`MaxHealth`, `MovementSpeed`, `AttackDamage`, and dozens more) after all modifiers are applied, `get_attribute_base`/`set_attribute_base` work with the unmodified base value underneath.

### `.add_attribute_modifier(attr, modifier)` / `.remove_attribute_modifier(attr, id)` / `.get_attribute_modifiers(attr)`

An `AttributeModifier` is `{ id, amount, operation }`, where `operation` is `Add`, `MultiplyBase`, or `MultiplyTotal` (matching vanilla's additive/multiplicative attribute stacking rules). `remove_attribute_modifier` takes the modifier's `id` string, the same one it was added with.

### `.reset_attribute(attr)` / `.reset_all_attributes()`

Clears an attribute (or every attribute) back to its default base value with no modifiers.

> [!WARNING]
> `pumpkin-plugin-api` doesn't currently export `Attribute`, `AttributeModifier`, or `ModifierOperation` publicly (the same situation as `StatusEffectType`/`Sound`/`Biome` elsewhere in this book). There's no supported way to name these types from a plugin right now, which makes the entire attribute API above uncallable until they're exported.

## Equipment

### `.get_equipment(slot)` / `.set_equipment(slot, stack)` / `.clear_equipment()`

Reads, sets, or clears an equipped item in an `EquipmentSlot` (`MainHand`, `OffHand`, `Feet`, `Legs`, `Chest`, `Head`, `Body`, the last being for entities like horses with body armor). `set_equipment` broadcasts the visual change to nearby clients.

## Targeting

### `.set_target(target)` / `.get_target()`

The entity this mob is currently targeting (attacking or fleeing from, depending on its AI), as an `Option<Entity>`.

## Raycasting

### `.raycast(max_distance, fluid_handling)`

Casts a ray from this entity's eye position in its facing direction, up to `max_distance` blocks. `fluid_handling: true` lets the ray stop on fluids as if they were solid, `false` passes through them. Returns a `RaycastResult { pos, face }` (the block position hit, and which `BlockDirection` face was struck), or `None` if nothing's in range.

## AI goals

### `.add_ai_goal(priority, goal)`

Adds one of the built-in mob AI behaviors, a `BuiltinAiGoal` (`Swim`, `WanderAround(speed)`, `MeleeAttack(speed)`, `LookAtPlayer(range)`, `LookAround`, `EscapeDanger(speed)`, `AvoidEntity(distance)`, `BlazeAttack`, `CreeperIgnite`, `EatGrass`, `ZombieAttack(speed)`), at a given priority (lower numbers run first, mirroring vanilla goal priority).

```rust
use pumpkin_plugin_api::world::BuiltinAiGoal;

zombie.add_ai_goal(0, BuiltinAiGoal::ZombieAttack(1.0));
zombie.add_ai_goal(1, BuiltinAiGoal::WanderAround(0.8));
zombie.add_ai_goal(2, BuiltinAiGoal::LookAtPlayer(8.0));
```

### `.add_custom_ai_goal(priority, goal_id)` / `pumpkin_plugin_api::ai::AiGoal`

The `AiGoal` trait lets you implement fully custom mob behavior (`can_start`, `should_continue`, `start`, `tick`, `stop`, each given the `Server` and the `Entity` running the goal), and `add_custom_ai_goal` attaches one to an entity by a `u32` id the host looks up on each tick.

> [!WARNING]
> As of this version, there's no public function to register an `AiGoal` implementation and obtain the `goal_id` that `add_custom_ai_goal` expects. The registration machinery (`AI_GOAL_HANDLERS`, `LazyAiGoalHandlers::register`) exists internally and the host-side dispatch (`handle_ai_goal_can_start`/`should_continue`/`start`/`tick`/`stop`) is fully wired up, but unlike the task scheduler's equivalent private registry (which is reachable through public `schedule_delayed_task`/`schedule_repeating_task` functions), nothing in `pumpkin-plugin-api` currently exposes an equivalent entry point for AI goals. Until one is added, only the built-in goals via `add_ai_goal` are usable.

### `.clear_ai_goals()` / `.set_ai_disabled(disabled)` / `.is_ai_disabled()`

Removes every AI goal from the entity, or disables AI processing entirely (the entity stops acting on any goal, built-in or otherwise, without removing them).

## Putting it together

Spawning a zombie with a simple built-in behavior set, since custom AI goals aren't reachable yet:

```rust
use pumpkin_plugin_api::{world::{BuiltinAiGoal, World}, EntityType};

fn spawn_guard(world: &World, pos: (f64, f64, f64)) {
  let zombie = world.spawn_entity(EntityType::Zombie, pos);

  zombie.add_ai_goal(0, BuiltinAiGoal::ZombieAttack(1.0));
  zombie.add_ai_goal(1, BuiltinAiGoal::WanderAround(0.6));
  zombie.add_ai_goal(2, BuiltinAiGoal::LookAtPlayer(6.0));
  zombie.add_ai_goal(3, BuiltinAiGoal::LookAround);
}
```

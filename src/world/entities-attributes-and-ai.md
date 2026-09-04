# Entities: attributes & AI

Health, attributes, equipment, targeting, pathfinding, and AI goals all live on two narrower handles you cast to from `Entity`: `LivingEntity` (`.as_living()`) for anything with health, and `Mob` (`.as_mob()`) for anything additionally AI-driven. Continues from [Entities: identity & movement](./entities-basics.md), see [Living entities & mobs](./entities-basics.md#living-entities--mobs) there for the casting methods themselves.

## Health & combat

### `.get_health()` / `.set_health(health)` / `.get_max_health()` / `.set_max_health(max_health)` / `.damage(amount, damage_type)` / `.is_dead()`

Same shape as the player health methods from [Health, effects & stats](../players/player-status.md). There's no `heal()` shortcut here like there is on `Player`, add to `get_health()` yourself and clamp to `get_max_health()`.

### `.get_absorption()` / `.set_absorption(amount)`

Absorption (extra) hearts, same concept as the player version.

## Attributes

### `.get_attribute_value(attr)` / `.get_attribute_base(attr)` / `.set_attribute_base(attr, value)`

`get_attribute_value` returns the *computed* value of an `Attribute` (`MaxHealth`, `MovementSpeed`, `AttackDamage`, and dozens more) after all modifiers are applied, `get_attribute_base`/`set_attribute_base` work with the unmodified base value underneath.

### `.add_attribute_modifier(attr, modifier)` / `.remove_attribute_modifier(attr, id)` / `.get_attribute_modifiers(attr)`

An `AttributeModifier` is `{ id, amount, operation }`, where `operation` is `ModifierOperation::Add`, `MultiplyBase`, or `MultiplyTotal` (matching vanilla's additive/multiplicative attribute stacking rules). `remove_attribute_modifier` takes the modifier's `id` string, the same one it was added with.

```rust
use pumpkin_plugin_api::{Attribute, AttributeModifier, ModifierOperation};

if let Some(living) = zombie.as_living() {
  living.add_attribute_modifier(Attribute::MovementSpeed, AttributeModifier {
    id: "my_plugin:speed_boost".to_string(),
    amount: 0.5,
    operation: ModifierOperation::MultiplyTotal,
  });
}
```

### `.reset_attribute(attr)` / `.reset_all_attributes()`

Clears an attribute (or every attribute) back to its default base value with no modifiers.

> [!NOTE]
> `Attribute`, `AttributeModifier`, and `ModifierOperation` are exported from the crate root as of this version, so the attribute API above is fully callable. Earlier builds of this crate didn't export these types; if you're on an older `pumpkin-plugin-api`, upgrade first.

## Equipment

### `.get_equipment(slot)` / `.set_equipment(slot, stack)` / `.clear_equipment()`

Reads, sets, or clears an equipped item in an `EquipmentSlot` (`MainHand`, `OffHand`, `Feet`, `Legs`, `Chest`, `Head`, `Body`, the last being for entities like horses with body armor). `set_equipment` broadcasts the visual change to nearby clients.

## Age & messaging

`.get_age()` / `.set_age(age)` (ticks since spawn, some mobs use this for baby/adult growth), `.send_system_message(message)` (sends a `TextComponent`, only meaningful for a `LivingEntity` that's actually a player under the hood).

## Targeting

### `.set_target(target)` / `.get_target()`

The entity this mob is currently targeting (attacking or fleeing from, depending on its AI), as an `Option<Entity>`. Mob-only, not on `LivingEntity`, an armor stand can't target anything.

## Pathfinding & navigation

### `.navigate_to_pos(pos, speed)` / `.navigate_to_entity(target, speed)` / `.stop_navigation()`

Starts the mob walking toward a position or another entity using the built-in pathfinder, at `speed` (same units as `BuiltinAiGoal::WanderAround`'s speed). Both return `false` if no path could be found. `stop_navigation` cancels an in-progress path immediately.

### `.is_navigating()` / `.has_reached_destination()` / `.set_navigation_speed(speed)`

Checks whether the mob currently has an active path, whether it's arrived, and lets you change the speed of an in-progress navigation without restarting it.

### `.can_reach(pos, max_distance)`

Checks whether the pathfinder thinks it can reach `pos` within `max_distance` blocks, without actually starting navigation, useful for AI goals deciding whether a target is worth pursuing.

### `.set_pathfinding_malus(node_type, malus)` / `.get_pathfinding_malus(node_type)`

Tunes how much this mob avoids a given `PathNodeType` (`Lava`, `DangerFire`, `Water`, `Cocoa`, and dozens more terrain classifications), a higher malus makes the pathfinder route around it more aggressively, matching vanilla's per-mob pathfinding penalties (e.g. why villagers avoid open trapdoors over holes).

### `.look_at(pos)` / `.look_at_entity(target)`

Turns the mob's head and body to face a position or entity, independent of navigation.

## Specialized mob data

### `.get_mob_data()` / `.set_mob_data(data)`

Every `Mob` carries a `MobData` variant matching its actual type (`MobData::Zombie(ZombieData { is_baby, can_break_doors })`, `MobData::Wolf(WolfData { is_tamed, owner, is_sitting, collar_color, .. })`, `MobData::Creeper`, `MobData::Sheep`, `MobData::Villager`, and more), or `MobData::Generic` for mobs without specialized data. `set_mob_data` returns `false` if you pass a variant that doesn't match the mob's real type (you can't turn a zombie's data into `SheepData`).

Rather than matching on `MobData` by hand, `pumpkin-plugin-api` provides typed wrapper structs (`Sheep`, `Wolf`, `Cat`, `Villager`, `Creeper`, `Slime`, `Enderman`, `IronGolem`, `Fox`, `Ageable`, `Zombie`, `Shulker`) that `Deref` to `Mob` and add a typed `.get_data()`/`.set_data()`:

```rust
use pumpkin_plugin_api::{Wolf, uuid::Uuid, world::Entity};

fn tame_wolf(entity: &Entity, owner: Uuid) {
  if let Some(wolf) = Wolf::from_entity(entity) {
    if let Some(mut data) = wolf.get_data() {
      data.is_tamed = true;
      data.owner = Some(owner);
      wolf.set_data(data);
    }
  }
}
```

`Wolf::from_entity`/`from_mob`/`from_living` all return `None` if the underlying mob isn't actually a wolf, matching the `TryFrom` impls also provided for each wrapper.

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

The `AiGoal` trait lets you implement fully custom mob behavior (`can_start`, `should_continue`, `start`, `tick`, `stop`, each given the `Server` and the `Entity` running the goal), and `add_custom_ai_goal` attaches one to a `Mob` by a `u32` id the host looks up on each tick.

> [!WARNING]
> As of this version, there's still no public function to register an `AiGoal` implementation and obtain the `goal_id` that `add_custom_ai_goal` expects. The registration machinery (`AI_GOAL_HANDLERS`, `LazyAiGoalHandlers::register`) exists internally and the host-side dispatch (`handle_ai_goal_can_start`/`should_continue`/`start`/`tick`/`stop`) is fully wired up, but unlike the task scheduler's equivalent private registry (which is reachable through public `schedule_delayed_task`/`schedule_repeating_task` functions), nothing in `pumpkin-plugin-api` currently exposes an equivalent entry point for AI goals. Until one is added, only the built-in goals via `add_ai_goal` are usable. This is unchanged from earlier versions of this crate.

### `.clear_ai_goals()` / `.set_ai_disabled(disabled)` / `.is_ai_disabled()`

Removes every AI goal from the entity, or disables AI processing entirely (the entity stops acting on any goal, built-in or otherwise, without removing them).

### `.set_freeze_ticks(ticks)` / `.get_freeze_ticks()`

Ticks of exposure to powdered snow (0-140), controlling the mob's frostbite/freeze visual state, the same mechanic exposed for players in [Inventory & environment](../players/player-inventory-and-environment.md).

## Putting it together

Spawning a zombie with a simple built-in behavior set, since custom AI goals aren't reachable yet:

```rust
use pumpkin_plugin_api::{world::{BuiltinAiGoal, World}, EntityType};

fn spawn_guard(world: &World, pos: (f64, f64, f64)) {
  let zombie = world.spawn_entity(EntityType::Zombie, pos);
  let Some(mob) = zombie.as_mob() else { return; };

  mob.add_ai_goal(0, BuiltinAiGoal::ZombieAttack(1.0));
  mob.add_ai_goal(1, BuiltinAiGoal::WanderAround(0.6));
  mob.add_ai_goal(2, BuiltinAiGoal::LookAtPlayer(6.0));
  mob.add_ai_goal(3, BuiltinAiGoal::LookAround);
}
```

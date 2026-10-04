# Health, effects & stats

The rest of `player.wit`: status effects, health and food, experience, statistics, cooldowns, flight, and advancements. All of these are called the same way as the identity/state methods from the [previous chapter](./player-basics.md), directly on a `Player` handle.

## Status effects

### `.add_effect(effect)` / `.remove_effect(effect_type)` / `.clear_effects()` / `.has_effect(effect_type)` / `.get_effect(effect_type)` / `.get_active_effects()` { data-since=0.1 }

These give and read potion-style status effects (speed, regeneration, invisibility, and so on). `add_effect` takes a `StatusEffectInstance` (the effect type, duration in ticks, amplifier, and whether it's ambient/shows particles/shows an icon), the rest take just a `StatusEffectType`.

> [!NOTE]
> `pumpkin-plugin-api` doesn't re-export `StatusEffectType` or `StatusEffectInstance` at its root. Until it does, name them through the raw bindings module, which is public: `pumpkin_plugin_api::wit::pumpkin::plugin::status_effect::{StatusEffectInstance, StatusEffectType}`. (Before 2026-09-20 that module was private and these six methods couldn't be called at all, only `clear_effects()`.)

```rust
use pumpkin_plugin_api::wit::pumpkin::plugin::status_effect::{StatusEffectInstance, StatusEffectType};

player.add_effect(StatusEffectInstance {
  effect_type: StatusEffectType::Speed,
  duration: 200, // ticks
  amplifier: 1,  // 0 is level I
  ambient: false,
  show_particles: true,
  show_icon: true,
});
```

## Health & damage

### `.get_health()` / `.set_health(health)` / `.get_max_health()` / `.set_max_health(max_health)` { data-since=0.1 }

Current and maximum health, both `f32`. Setting health above the current max caps at the max, setting it to `0.0` or below kills the player the same as normal damage would.

### `.heal(amount)` / `.damage(amount, damage_type)` / `.kill()` { data-since=0.1 }

`heal` adds health directly (capped at max health), `damage` deals damage attributed to a specific `DamageType` (armor, enchantments, and absorption still apply, same as vanilla damage), and `kill` is an instant kill regardless of current health or invulnerability.

### `.get_food_level()` / `.set_food_level(food_level)` / `.get_saturation()` / `.set_saturation(saturation)` / `.get_exhaustion()` / `.set_exhaustion(exhaustion)` { data-since=0.1 }

The three-part hunger system: food level (0-20, the drumstick icons), saturation (a hidden buffer that gets drained before food level does), and exhaustion (accumulates from actions like sprinting or jumping, and converts to lost saturation once it crosses a threshold).

### `.get_absorption()` / `.set_absorption(absorption)` { data-since=0.1 }

Absorption hearts (the golden hearts from effects like the Absorption status effect or totems), on top of normal health.

### Experience

`.get_experience_level()` / `.set_experience_level(level)`, `.get_experience_progress()` / `.set_experience_progress(progress)` (0.0 to 1.0 toward the next level), `.get_experience_points()` / `.set_experience_points(points)`, and the additive helpers `.add_experience_levels(levels)` / `.add_experience_points(points)`.

> [!NOTE]
> Levels, progress, and points are three separate fields the client displays together, they aren't automatically kept in sync with each other. If you set `experience_points` directly, the level and progress bar won't update to match unless you also update them, or use `add_experience_points`/`add_experience_levels` instead, which handle the conversion for you.

## Statistics

### `.get_statistic(category, stat_id)` / `.set_statistic(category, stat_id, value)` / `.increment_statistic(category, stat_id, amount)` { data-since=0.1 }

Vanilla statistics (blocks mined, items crafted/used/broken/picked up, and so on), grouped by a `StatisticCategory` (`Mined`, `Crafted`, `Used`, `Broken`, `PickedUp`, ...). `stat_id` is a raw integer id into Pumpkin's internal statistic/registry data for that category, not a named constant exposed by this interface, you'll need to cross-reference Pumpkin's registry data for the id that corresponds to a specific block or item.

### `.get_custom_statistic(stat)` / `.set_custom_statistic(stat, value)` / `.increment_custom_statistic(stat, amount)` { data-since=0.1 }

The non-block/item statistics (play time, jumps, deaths, distance walked, and similar), addressed by the strongly-typed `CustomStatistic` enum instead of a raw id, much easier to use than the category-based methods above.

### `.send_stats()` { data-since=0.1 }

Pushes the player's current statistics to their client immediately (normally they sync periodically or when the stats screen is opened).

### `.get_team()` { data-since=0.1 }

Returns the name of the scoreboard team this player belongs to, if any, see [Teams](../scoreboard/teams.md).

## Cooldowns

### `.start_cooldown(group, duration_ticks)` / `.get_cooldown(group)` / `.is_on_cooldown(group)` { data-since=0.1 }

A real, server-enforced cooldown keyed by an arbitrary group name you choose, `get_cooldown` returns progress from `0.0` (just started) to `1.0` (finished). This is separate from vanilla per-item cooldowns and from the client-side cooldown overlay covered in [Inventory & environment](./player-inventory-and-environment.md), it's meant for your own plugin-defined cooldown groups (an ability, a kit, a custom item's effect).

## Abilities & flight

### `.is_flying()` / `.set_flying(flying)` { data-since=0.1 }

Whether the player is currently flying, and forcing them into or out of flight.

### `.set_allow_flight(allowed)` / `.set_fly_speed(speed)` / `.set_walk_speed(speed)` / `.set_invulnerable(invulnerable)` { data-since=0.1 }

Individual ability toggles: whether the player is permitted to fly at all, their flying and walking speeds, and whether they take damage.

### `.get_abilities()` / `.set_abilities(abilities)` { data-since=0.1 }

Reads or replaces the whole `PlayerAbilities` record at once (`invulnerable`, `flying`, `allow_flying`, `creative`, `allow_modify_world`, `fly_speed`, `walk_speed`), covering the same fields as the individual setters above plus `creative` and `allow_modify_world`. Reach for this when you want to change several ability flags together atomically instead of one call at a time.

## Advancements

### `.get_advancement_progress(advancement_id)` { data-since=0.1 }

Returns an `AdvancementProgress` (`done`, `awarded_criteria`, `remaining_criteria`) for the given advancement id, or `None` if no advancement with that id exists.

### `.award_advancement_criterion(advancement_id, criterion)` / `.revoke_advancement_criterion(advancement_id, criterion)` { data-since=0.1 }

Awards or revokes one specific criterion of a multi-criteria advancement. Both return `true` if the call actually changed something (the criterion wasn't already in that state).

### `.award_advancement(advancement_id)` / `.revoke_advancement(advancement_id)` { data-since=0.1 }

Awards or revokes every criterion of an advancement at once, completing or fully un-completing it.

### `.has_advancement(advancement_id)` / `.get_completed_advancements()` { data-since=0.1 }

Check a single advancement, or list every completed advancement id for this player.

### `.get_selected_advancement_tab()` / `.set_selected_advancement_tab(tab_id)` { data-since=0.1 }

The advancement tab currently open in the player's advancement screen, `tab_id` must be a root advancement's id.

## Putting it together

A `/heal` admin command that fully restores a player: health, hunger, and clears accumulated exhaustion.

```rust
use pumpkin_plugin_api::{command::CommandSender, text::TextComponent};

fn heal_command(sender: &CommandSender, target: &Player) {
  target.set_health(target.get_max_health());
  target.set_food_level(20);
  target.set_saturation(5.0);
  target.set_exhaustion(0.0);

  let name = target.get_name();
  sender.send_message(TextComponent::text(&format!("Healed {name}.")));
  target.send_system_message(TextComponent::text("You have been fully healed."), false);
}
```

# Vanilla data reference

A handful of WIT interfaces don't expose any behavior of their own, they're just exhaustive, typed enums mirroring vanilla Minecraft's registries: damage types, entity types, particles, sounds, biomes, status effects, statistics, and data components. Other APIs throughout this book take or return these types (`World::spawn_entity` wants an `EntityType`, `Entity::damage` wants a `DamageType`, and so on), this page is a quick orientation to all of them in one place, not a full list of every variant, that lives in the WIT source itself and would go stale here every time Minecraft adds new content.

## What's actually usable today

Not every one of these types has a public path in `pumpkin-plugin-api` yet. Quick status check before you reach for one:

| Catalog | Rust type | Accessible as | Status |
|---|---|---|---|
| Damage types | `DamageType` | `pumpkin_plugin_api::DamageType` | Usable |
| Entity types | `EntityType` | `pumpkin_plugin_api::EntityType` | Usable |
| Particles | `Particle` | `pumpkin_plugin_api::particles::Particle` | Usable |
| Screens | `Screen` | `pumpkin_plugin_api::Screen` | Usable |
| Data components | `DataComponent` | `pumpkin_plugin_api::data_components::DataComponent` | Usable |
| Statistics | `StatisticCategory`, `CustomStatistic` | `pumpkin_plugin_api::{StatisticCategory, CustomStatistic}` | Usable |
| Game rules | `GameRule`, `GameRuleValue` | `pumpkin_plugin_api::{GameRule, GameRuleValue}` | Usable, see [The world handle](../world/world-and-time.md#game-rules) |
| Biomes | `Biome` | `pumpkin_plugin_api::worldgen::PluginBiome` | Usable, but only via this non-obvious alias, see [Custom chunk generation](../worldgen/custom-world-generation.md) |
| Sounds | `Sound` | *(none)* | **Not exported**, `World::play_sound` can't currently be called, see [The world handle](../world/world-and-time.md#sound--particles) |
| Status effects | `StatusEffectType`, `StatusEffectInstance` | *(none)* | **Not exported**, `Player::add_effect` and friends can't currently be called, see [Health, effects & stats](../players/player-status.md#status-effects) |

## Damage types

`DamageType` covers every source of damage the game tracks (`Arrow`, `Cactus`, `Drown`, `Fall`, `Lava`, `LightningBolt`, `Magic`, `MobAttack`, `OnFire`, `Explosion`, `Generic`, and around 45 more), used by `Player::damage`/`Entity::damage`.

```rust
use pumpkin_plugin_api::DamageType;

player.damage(4.0, DamageType::InFire);
```

## Entity types

`EntityType` covers every spawnable entity (`Zombie`, `Skeleton`, `Item`, `Arrow`, `Boat`, `TextDisplay`, `Interaction`, and around 150 more), used by `World::spawn_entity` and returned by `Entity::get_type`.

## Particles

`Particle` covers every particle effect (`Flame`, `HappyVillager`, `Explosion`, `Heart`, `Crit`, and around 120 more), used by `World::spawn_particle`.

## Screens

`Screen` covers vanilla inventory-screen layouts (`Generic9x1` through `Generic9x6`, `Anvil`, `Beacon`, `Furnace`, `Merchant`, and more), used by `Gui::new`, see [Custom GUIs](../ui/gui.md).

## Data components

`DataComponent` covers the post-1.20.5 item data model's component keys (`CustomData`, `MaxStackSize`, `MaxDamage`, `Unbreakable`, `Enchantments`, `Rarity`, and around 100 more), used by `ItemStack::get_components`/`set_component`/`remove_component`, see [Item stacks](../items/item-stack.md#data-components).

## Statistics

`StatisticCategory` (`Mined`, `Crafted`, `Used`, `Broken`, `PickedUp`, and a few more) pairs with a raw numeric block/item id, `CustomStatistic` (`PlayTime`, `JumpCount`, `DeathCount`, `DamageDealt`, and around 80 more) is self-contained. See [Health, effects & stats](../players/player-status.md#statistics).

## Game rules

`GameRule` covers every vanilla game rule name (`MobGriefing`, `KeepInventory`, `DoFireTick`, `AnnounceAdvancements`, and around 60 more), paired with a `GameRuleValue::Bool`/`GameRuleValue::Int` matching whichever type that rule actually uses. See [The world handle](../world/world-and-time.md#game-rules) for the get/set calls.

## Putting it together

A "campfire" effect combining several of the *usable* catalogs at once: a particle, sound-free (since `Sound` isn't reachable yet), a fire damage tick, and a custom statistic bump:

```rust
use pumpkin_plugin_api::{particles::Particle, CustomStatistic, DamageType};

fn stand_in_fire(world: &World, player: &Player, pos: (f64, f64, f64)) {
  world.spawn_particle(Particle::Flame, pos, (0.3, 0.3, 0.3), 0.05, 8);
  player.damage(1.0, DamageType::InFire);
  player.increment_custom_statistic(CustomStatistic::TimeSinceDeath, 1);
}
```

## Full lists

The book intentionally doesn't reproduce every variant here, `sounds.wit` alone is nearly 2000 lines and would be stale the moment Minecraft ships new content. For the authoritative, current list of any catalog, check the corresponding file directly:

- [`damage-types.wit`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/blob/master/v0.1/damage-types.wit)
- [`entity-types.wit`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/blob/master/v0.1/entity-types.wit)
- [`particles.wit`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/blob/master/v0.1/particles.wit)
- [`sounds.wit`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/blob/master/v0.1/sounds.wit)
- [`biomes.wit`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/blob/master/v0.1/biomes.wit)
- [`status-effect.wit`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/blob/master/v0.1/status-effect.wit)
- [`statistics.wit`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/blob/master/v0.1/statistics.wit)
- [`data-components.wit`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/blob/master/v0.1/data-components.wit)
- [`game-rules.wit`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/blob/master/v0.1/game-rules.wit)
- [`screens.wit`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/blob/master/v0.1/screens.wit)

# Boss bars

The health bar shown at the top of the screen, the same UI element vanilla bosses use, available to any plugin for progress bars, event timers, or announcements.

## Creating one

### `BossBar::new(title, color, division)` { data-since=0.1 }

```rust
use pumpkin_plugin_api::{boss_bar::{BossBar, BossBarColor, BossBarDivision}, text::TextComponent};

let bar = BossBar::new(
  TextComponent::text("Event: Capture the Flag"),
  BossBarColor::Blue,
  BossBarDivision::Notches10,
);
```

`color` is one of `Pink`, `Blue`, `Red`, `Green`, `Yellow`, `Purple`, `White`. `division` splits the bar into visible segments, `NoDivision` for a smooth bar, or `Notches6`/`Notches10`/`Notches12`/`Notches20` for a segmented one (useful for a countdown with a fixed number of stages).

## Title, health & appearance

### `.get_title()` / `.set_title(title)` { data-since=0.1 }

### `.get_health()` / `.set_health(health)` { data-since=0.1 }

A fraction from `0.0` to `1.0`, not a raw number, if you're tracking something with its own scale (30 seconds remaining out of 60, for instance), normalize it yourself: `remaining / total`.

### `.get_color()` / `.set_color(color)` / `.get_division()` / `.set_division(division)` { data-since=0.1 }

## Metadata flags

### `.get_metadata()` / `.set_metadata(metadata)` { data-since=0.1 }

A `BossBarMetadata` record with three flags: `darken_sky` (dims the sky for viewers, like the Wither/Dragon fight), `dragon_bar` (marks it as the special "dragon bar" styling), `create_fog` (adds fog around viewers, another Dragon-fight effect). All three default to `false` if you build the record yourself.

## Who sees it

### `.add_player(player)` / `.remove_player(player)` / `.get_players()` { data-since=0.1 }

A boss bar isn't visible to anyone until you add them. `get_players()` lists everyone currently seeing it.

### `.remove_all()` { data-since=0.1 }

Removes the bar from every player currently seeing it and cleans it up, use this when the bar's purpose is over (an event ending, a boss dying) rather than removing players one at a time.

## Putting it together

A countdown timer bar shown to everyone in a world, ticking down over 30 seconds:

```rust
use pumpkin_plugin_api::{
  boss_bar::{BossBar, BossBarColor, BossBarDivision},
  context::Server, text::TextComponent, world::World,
};

fn start_countdown(server: &Server, world: World) {
  let bar = BossBar::new(
    TextComponent::text("Starting in..."),
    BossBarColor::Yellow,
    BossBarDivision::NoDivision,
  );

  // `get_players_in_world` takes the `World` handle by value, so `world` is spent here
  for player in server.get_players_in_world(world) {
    bar.add_player(player);
  }

  // In a repeating scheduled task (see Task scheduler), each tick:
  // bar.set_health(remaining_ticks as f32 / 600.0);
  // and bar.remove_all() once it hits zero.
}
```

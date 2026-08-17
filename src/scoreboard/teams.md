# Teams

Teams live on the same `Scoreboard` resource covered in [Scoreboards & objectives](./scoreboard.md), but `pumpkin-plugin-api` wraps them in a friendlier `Team` handle instead of leaving you to pass team names as raw strings to every call. Bring `ScoreboardTeamExt` into scope to get at it.

## Creating and settings

### `TeamSettingsBuilder`

Team appearance and behavior is one `TeamSettings` record (`display_name`, `friendly_fire`, `see_friendly_invisibles`, `nametag_visibility`, `collision_rule`, `color`, `prefix`, `suffix`), built with:

```rust
use pumpkin_plugin_api::{
  scoreboard::{CollisionRule, NametagVisibility},
  common::NamedColor,
  team::TeamSettingsBuilder,
  text::TextComponent,
};

let settings = TeamSettingsBuilder::new()
  .display_name(TextComponent::text("Red Team"))
  .color(NamedColor::Red)
  .prefix(TextComponent::text("[Red] "))
  .friendly_fire(false)
  .nametag_visibility(NametagVisibility::HideForOtherTeams)
  .collision_rule(CollisionRule::PushOwnTeam)
  .build();
```

Defaults (if you skip a setting): friendly fire on, invisible teammates not visible, nametags always shown, always-collide, white, no prefix/suffix.

### `scoreboard.register_new_team(name, settings)`

Creates the team on the scoreboard and hands you back a `Team` handle for it in one call, `ScoreboardTeamExt`'s main entry point.

```rust
use pumpkin_plugin_api::ScoreboardTeamExt;

let red_team = scoreboard.register_new_team("red", settings);
```

## Looking teams up

### `scoreboard.get_team_handle(name)` / `scoreboard.get_all_teams()` / `scoreboard.get_player_team_handle(player_name)`

`get_team_handle` returns `None` if no team with that name exists, `get_all_teams` lists every `Team` on the scoreboard, `get_player_team_handle` finds whichever team a given player name currently belongs to.

### `player.get_team_name()`

`PlayerTeamExt` adds this directly on `Player` (a friendlier name for the same `get_team` call from [Health, effects & stats](../players/player-status.md)), returning just the team name string rather than a full `Team` handle.

## Working with a `Team` handle

Every field on `TeamSettings` gets a matching getter/setter pair on `Team`, each one reads the current settings, changes just that field, and writes the whole record back: `.display_name()`/`.set_display_name(name)`, `.prefix()`/`.set_prefix(prefix)`, `.suffix()`/`.set_suffix(suffix)`, `.color()`/`.set_color(color)`, `.allow_friendly_fire()`/`.set_allow_friendly_fire(allow)`, `.can_see_friendly_invisibles()`/`.set_can_see_friendly_invisibles(see)`, `.nametag_visibility()`/`.set_nametag_visibility(vis)`, `.collision_rule()`/`.set_collision_rule(rule)`. Getters return `None`/a default if the team was removed out from under the handle since it was created.

If you need to change several fields at once, `.get_settings()` / `.update_settings(settings)` let you read the whole record, modify it, and write it back in one call instead of round-tripping per field.

### `.get_players()` / `.add_player(player_name)` / `.remove_player(player_name)` / `.has_player(player_name)` / `.clear_players()`

Membership, by plain name string (works for offline names too, same as scoreboard scores).

### `.unregister()`

Removes the team from the scoreboard entirely. Consumes the handle, since there's nothing left to point at afterward.

## Putting it together

Setting up two PvP teams with friendly fire off, and a command to join one:

```rust
use pumpkin_plugin_api::{
  common::NamedColor, scoreboard::NametagVisibility, team::TeamSettingsBuilder,
  text::TextComponent, world::World, ScoreboardTeamExt,
};

fn setup_teams(world: &World) {
  let scoreboard = world.get_scoreboard();

  let red = TeamSettingsBuilder::new()
    .display_name(TextComponent::text("Red"))
    .color(NamedColor::Red)
    .friendly_fire(false)
    .nametag_visibility(NametagVisibility::HideForOtherTeams)
    .build();
  scoreboard.register_new_team("red", red);

  let blue = TeamSettingsBuilder::new()
    .display_name(TextComponent::text("Blue"))
    .color(NamedColor::Blue)
    .friendly_fire(false)
    .nametag_visibility(NametagVisibility::HideForOtherTeams)
    .build();
  scoreboard.register_new_team("blue", blue);
}

fn join_team(world: &World, player_name: &str, team_name: &str) {
  let scoreboard = world.get_scoreboard();
  if let Some(team) = scoreboard.get_team_handle(team_name) {
    team.add_player(player_name);
  }
}
```

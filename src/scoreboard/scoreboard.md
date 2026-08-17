# Scoreboards & objectives

Get a world's `Scoreboard` with `world.get_scoreboard()` (see [The world handle](../world/world-and-time.md)). Team management lives on the same resource but gets its own chapter, [Teams](./teams.md), since it's big enough to warrant it.

## Objectives

### `.add_objective(name, display_name, render_type)` / `.update_objective(name, display_name, render_type)` / `.remove_objective(name)`

An objective is a named counter (kills, deaths, a custom stat) that scores get attached to. `render_type` is `RenderType::Integer` (a plain number) or `RenderType::Hearts` (rendered as half-heart icons, capped visually the way vanilla health objectives are). `update_objective` changes an existing objective's display name/render type without recreating it.

### `.set_display_slot(slot, objective_name)` / `.clear_display_slot(slot)`

Shows an objective in a `DisplaySlot`: `PlayerList` (next to names in the tab list), `Sidebar` (the classic right-side scoreboard), `BelowName` (under a player's nameplate), or one of the sixteen `SidebarTeamX` variants (a sidebar that only shows for members of a specific team color).

## Scores

### `.update_score(entity_name, objective_name, value)` / `.add_score(entity_name, objective_name, delta)` / `.remove_score(entity_name, objective_name)` / `.reset_entity_scores(entity_name)`

Scores are keyed by `entity_name`, a plain string (usually a player's username, but scoreboards support arbitrary named entries the same way vanilla `/scoreboard` commands do). `update_score` sets an absolute value, `add_score` adds a relative `delta` and returns the new total, `remove_score` clears one score, `reset_entity_scores` clears every objective's score for that name at once.

```rust
let scoreboard = world.get_scoreboard();

scoreboard.add_objective("kills", TextComponent::text("Kills"), RenderType::Integer);
scoreboard.set_display_slot(DisplaySlot::Sidebar, "kills");

let new_total = scoreboard.add_score(&player.get_name(), "kills", 1);
```

## Bedrock scoreboards

`world_ref` also exposes a parallel, simpler `BedrockScoreboard` for Bedrock clients (`add_objective`/`update_objective`/`remove_objective`/`set_display_slot`/`clear_display_slot`/`update_score`/`add_score`/`remove_score`/`reset_entity_scores`, the same shape minus team support), using a plain string display name and a `BedrockSortOrder` (`Ascending`/`Descending`) instead of a `RenderType`, and a three-slot `BedrockDisplaySlot` (`PlayerList`, `Sidebar`, `BelowName`) instead of the sixteen-variant Java one. Reach for it specifically when you're building a scoreboard experience tuned for Bedrock players rather than relying on Java-style objectives translating automatically.

## Putting it together

A simple kill-tracker: an objective shown in the sidebar, incremented on a kill, reset on join.

```rust
use pumpkin_plugin_api::{
  scoreboard::{DisplaySlot, RenderType},
  text::TextComponent,
  world::World,
};

fn setup_kill_scoreboard(world: &World) {
  let scoreboard = world.get_scoreboard();
  scoreboard.add_objective("kills", TextComponent::text("Kills"), RenderType::Integer);
  scoreboard.set_display_slot(DisplaySlot::Sidebar, "kills");
}

fn record_kill(world: &World, killer_name: &str) {
  world.get_scoreboard().add_score(killer_name, "kills", 1);
}
```

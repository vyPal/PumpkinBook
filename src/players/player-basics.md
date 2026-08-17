# Identity, state & permissions

`Player` is the resource you'll spend the most time with. You get one from an event's data (`event.player`, as seen in [Event handlers](../plugin-101/event-handlers.md)), from a `CommandSender` that turns out to be a player (see [Command executors](../commands/executors.md)), or from a server-wide lookup (covered in [Server info & worlds](../server/server-info-and-worlds.md)). This page covers identity, connection info, basic world state, and the player-permission API. Inventory, health, and other player-status methods each get their own page, since `player.wit` alone is too big for one.

## Identity & connection

### `.get_id()` / `.get_name()`

`get_id()` returns the player's `Uuid` (a `{ high: u64, low: u64 }` pair, not a string), `get_name()` returns their username. The UUID is the stable identifier, usernames can change.

> [!NOTE]
> To get a UUID as a familiar string (for display, logging, or storage), use the free functions in the `uuid` module: `uuid::to_string(id)` converts one to its standard string form, and `uuid::parse(s)` goes the other way, returning `None` if the string isn't a valid UUID.
>
> ```rust
> use pumpkin_plugin_api::uuid;
>
> let id_str = uuid::to_string(player.get_id());
> ```

### `.as_entity()`

Every player is also an entity underneath, movement, health, and physics all go through the same entity machinery other mobs use. `as_entity()` gives you that handle, see [Entities: identity & movement](../world/entities-basics.md) for what you can do with it.

### `.get_ip()`

Returns the player's connection IP as a string.

### `.get_ping()`

Returns the player's current ping in milliseconds.

### `.get_locale()`

Returns the player's client-side locale (e.g. `"en_us"`). Useful if you're picking which translation to send them yourself instead of relying on `TextComponent::translate`, see [Localization](../text/localization.md).

## Basic state

### `.get_position()` / `.get_yaw()` / `.get_pitch()`

The player's current coordinates and facing direction.

### `.get_world()`

The `World` the player is currently in.

### `.get_gamemode()` / `.set_gamemode(mode)`

Reads or changes the player's `GameMode` (`Survival`, `Creative`, `Adventure`, `Spectator`). `set_gamemode` returns a `bool`, check it, a change can fail (for example if another plugin's event handler cancels the underlying game mode change event).

```rust
use pumpkin_plugin_api::common::GameMode;

if !player.set_gamemode(GameMode::Spectator) {
  server.log("Couldn't switch that player to spectator.");
}
```

## Permissions

This is the player-facing half of the permission system, the resolution rules (wildcards, children, defaults) are explained in full in [Command permissions](../commands/permissions.md). Here you're just reading and writing this specific player's state.

### `.get_permission_level()` / `.set_permission_level(level)`

The player's op level, a `PermissionLevel` from `Zero` to `Four`, matching vanilla op levels.

### `.set_permission(node, value)` / `.unset_permission(node)`

Explicitly grants (`value: true`) or denies (`value: false`) a specific permission node for this player, overriding whatever the node's registered default would otherwise resolve to. `unset_permission` removes that explicit override, falling back to normal resolution again.

> [!WARNING]
> Like command permission grants, per-player overrides set with `set_permission` live only in memory. They don't survive a server restart or a plugin reload, if a plugin wants persistent per-player grants, it needs to save and reapply them itself (see [Persistent Data](../persistent-data/persistent-data.md) or [Data persistence](../plugin-101/data-persistence.md)).

### `.has_permission_set(node)`

Returns `Some(true)`/`Some(false)` if this exact node has an explicit override for this player, or `None` if it's never been explicitly set (meaning normal resolution applies).

### `.has_permission(node)`

The one you actually want for permission checks in most cases, it runs the node through full resolution (explicit grant, wildcard, children, then default) and gives you a plain `bool`.

## Display name & tab list

### `.get_display_name()` / `.set_display_name(name)`

The name shown for this player in chat and above their head, a `TextComponent` so it can carry color and formatting, not just plain text.

### `.get_tab_list_name()` / `.set_tab_list_name(name)`

An optional separate `TextComponent` for how the player appears in the tab list (pass `None` to fall back to the display name there).

### `.set_tab_list_header_footer(header, footer)`

Sets the text shown above and below the player list when a player opens their tab menu, this is set on a per-player basis, so different players can see different headers/footers.

### `.set_tab_list_order(order)` / `.set_tab_list_listed(listed)`

`set_tab_list_order` controls where this player sorts in the list (lower sorts first). `set_tab_list_listed` toggles whether the player shows up in the tab list at all.

### `.set_tab_list_latency(latency)` / `.set_tab_list_ping(latency_ms)`

Both control the connection-quality indicator shown next to a player's name in the tab list. Passing your own value here is how you'd fake a specific bar count instead of the client's real measured ping.

## Teleporting, respawning & moving on

### `.teleport(position, yaw, pitch, world)`

Moves the player within the same world (or explicitly re-specifying the world they're already in). `yaw`/`pitch` are optional, omit them to keep the player's current facing.

### `.teleport_world(world_ref, position, yaw, pitch)`

Same idea, but for crossing into a different `World` entirely.

### `.respawn()`

Forces the player to respawn immediately, as if they'd just died and clicked the respawn button.

### `.transfer(host, port)`

Sends the player to a different server entirely (a Minecraft server transfer, not a Pumpkin-internal world change), the client disconnects from this server and connects to `host:port`.

### `.ban(options)` / `.ban_ip(options)`

Bans the player (`BanPlayerOptions`) or their IP (`BanIpOptions`). Both option structs let you set a reason, a source string (who/what issued the ban, defaults to `"Plugin"`), an expiry (`expires_at_utc` as an RFC-3339 string, or `duration_seconds` from now), whether to immediately kick the player if they're online, and whether to log the ban to console. See [Ops, bans & whitelist](../server/ops-bans-and-whitelist.md) for the server-wide ban list API these feed into.

## Putting it together

A `/spectate` style command that drops the sender into spectator mode, hides them from the tab list, and gives them a colored display name while they're in that state:

```rust
use pumpkin_plugin_api::{command::CommandSender, common::GameMode, text::TextComponent};

fn spectate(sender: &CommandSender) {
  let Some(player) = sender.as_player() else {
    sender.send_message(TextComponent::text("Players only."));
    return;
  };

  if !player.set_gamemode(GameMode::Spectator) {
    sender.send_message(TextComponent::text("Couldn't switch to spectator mode."));
    return;
  }

  player.set_tab_list_listed(false);

  let name = player.get_name();
  let ghost_name = TextComponent::text(&format!("👻 {name}"));
  player.set_display_name(ghost_name);

  player.send_system_message(TextComponent::text("You are now spectating."), false);
}
```

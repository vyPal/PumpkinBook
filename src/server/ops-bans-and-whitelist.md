# Ops, bans & whitelist

Three global managers reached through `Server`: `.get_op_manager()`, `.get_ban_manager()`, and `.get_whitelist_manager()`. Unlike the per-player methods on `Player` from [Identity, state & permissions](../players/player-basics.md) (which only work on someone currently online), everything here works by UUID for both online and offline players, since ops/bans/whitelist entries need to exist whether or not the player is connected right now.

## Operators

### `.is_op(id)` / `.get_op(id)` / `.get_permission_level(id)`

Checks op status, fetches the full `OpEntry` (`uuid`, `name`, `level`, `bypasses_player_limit`) if the player is op, or just their effective `PermissionLevel` (`Zero` if they're not op at all).

### `.op_player(name, id, level, bypasses_player_limit)` / `.deop_player(id)`

Grants or revokes operator status. `bypasses_player_limit` lets an op join even when the server is already at its player cap. `deop_player` returns `true` if the player was actually op beforehand.

### `.list_ops()`

Every `OpEntry` currently in `ops.json`.

> [!WARNING]
> `PermissionLvl`'s deserialization (the type backing `ops.json`'s `level` field) is missing the match arm for value `1` (`Moderator`). An `ops.json` entry with `"level": 1` fails to load with an "Invalid value for OpLevel: 1" error, even though `PermissionLevel::One` is a real, usable value everywhere else in the plugin API (including `op_player`'s own `level` parameter). Avoid granting op level `1` through `op_player` until this is fixed, or the entry may fail to load back from disk on the next server restart.

## Bans

### `.is_player_banned(id)` / `.get_player_ban(id)`

Checks or fetches the `BannedPlayerEntry` (`uuid`, `name`, `created`, `source`, `expires`, `reason`) for a player.

### `.ban_player(name, id, options)` / `.unban_player(id)`

Same `BanPlayerOptions` shape as `Player::ban()` from [Identity, state & permissions](../players/player-basics.md), but works on offline players too since it's addressed by UUID instead of an online `Player` handle.

### `.list_player_bans()`

Every currently active player ban.

### `.is_ip_banned(ip)` / `.get_ip_ban(ip)` / `.ban_ip(ip, options)` / `.unban_ip(ip)` / `.list_ip_bans()`

The same shape again, for IP-based bans instead of player bans.

## Whitelist

### `.is_enabled()` / `.set_enabled(enabled)`

Reads or toggles whether the whitelist is active. Enabling it with server-side whitelist enforcement on will kick any currently-online, non-whitelisted players.

### `.is_whitelisted(id)` / `.add_player(name, id)` / `.remove_player(id)`

Checks, adds, or removes a whitelist entry by UUID. `add_player` returns `true` if the player was newly added (wasn't already whitelisted).

### `.list_entries()`

Every `WhitelistEntry` (`uuid`, `name`) currently whitelisted.

## Putting it together

A `/banhistory` command that reports whether a given UUID is currently banned, and why, working whether or not that player is online:

```rust
use pumpkin_plugin_api::{command::CommandSender, context::Server, text::TextComponent, uuid};

fn ban_history(sender: &CommandSender, server: &Server, id_str: &str) {
  let Some(id) = uuid::parse(id_str) else {
    sender.send_message(TextComponent::text("Not a valid UUID."));
    return;
  };

  let bans = server.get_ban_manager();
  match bans.get_player_ban(id) {
    Some(entry) => {
      let msg = format!("Banned: {} (by {}). Reason: {}", entry.name, entry.source, entry.reason);
      sender.send_message(TextComponent::text(&msg));
    }
    None => sender.send_message(TextComponent::text("No active ban found.")),
  }
}
```

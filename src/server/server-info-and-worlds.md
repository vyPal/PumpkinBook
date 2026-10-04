# Server info & worlds

`Server` is the top-level handle for everything that isn't scoped to one specific player, entity, or world: server-wide player and world lookups, performance stats, config, and the various manager resources (recipes, ops, bans, whitelist, enchantments). You get one from `context.get_server()` in `on_load`, or as an argument to most handler callbacks.

## System & performance

### `.get_sys_info()` { data-since=0.1 }

Returns a `SysInfo` record (`cpu_count`, `total_memory`, `used_memory`, `os_name`, `os_version`, `pumpkin_version`). The fields besides `pumpkin_version` are only populated if your plugin was granted the corresponding `sys.info.*` permission, see [Plugin permissions](../plugin-101/plugin-permissions.md), otherwise they come back `None`.

### `.get_tps()` / `.get_mspt()` { data-since=0.1 }

Effective ticks-per-second (ideally `20.0`) and the rolling average milliseconds-per-tick (should stay under `50.0` to hold a stable 20 TPS).

### `.get_difficulty()` { data-since=0.1 }

The server's current `Difficulty` (`Peaceful`, `Easy`, `Normal`, `Hard`).

## Players

### `.get_player_count()` / `.get_all_players()` { data-since=0.1 }

Total online player count, and the actual list of every online `Player` across all worlds.

### `.get_player_by_name(name)` / `.get_player_by_uuid(id)` { data-since=0.1 }

Look up a specific online player, `None` if they're not connected.

### `.get_players_in_world(world_ref)` / `.get_player_count_in_world(world_ref)` { data-since=0.1 }

Same lookups, scoped to one `World`.

### `.get_max_players()` { data-since=0.1 }

The server's configured player cap.

## Worlds

### `.get_all_worlds()` / `.get_world_by_name(name)` / `.has_world(name)` { data-since=0.1 }

Lists every loaded `World`, looks one up by dimension name (`"minecraft:overworld"`) or custom world name (`"world"`, `"arena_1"`), or checks whether one exists at all.

### `.create_world(name, dimension)` { data-since=0.1 }

Creates or loads a world with the given name and `Dimension` (`Overworld`, `Nether`, `End`). If a world with that name already exists, returns the existing one instead of erroring.

### `.unload_world(name)` { data-since=0.1 }

Unloads and saves a world. Fails if the world doesn't exist, is the primary/default world, or still has players in it.

### `.save_all()` { data-since=0.1 }

Saves every online player, their advancements, and every loaded world to disk immediately.

## Messaging

### `.broadcast(message)` / `.broadcast_tab_list_header_footer(header, footer)` { data-since=0.1 }

`broadcast` sends a plain string to every player's chat on the whole server (not just one world, contrast with `World::broadcast_system_message`, which takes a full `TextComponent` and is scoped to one world). `broadcast_tab_list_header_footer` sets the tab list header/footer for everyone at once.

### `.delete_message_by_signature(signature)` / `.delete_message_by_id(signature_id)` { data-since=0.1 }

Removes a previously-sent signed chat message from every player's chat window, either by its full 256-byte signature (`list<u8>`) or by the shorter signature cache id, the same mechanism vanilla uses when a moderator deletes a chat message. `Player` has the same two methods scoped to a single player's chat window, see [Identity, state & permissions](../players/player-basics.md).

### `.set_server_links(links)` { data-since=0.1 }

Sets the custom links shown in every connected client's Esc pause menu (Java 1.21+). A `ServerLink` is `{ label, url }`, where `label` is either `ServerLinkLabel::Known(KnownServerLink)` (a built-in recognized icon/label, `BugReport`, `CommunityGuidelines`, `Support`, `Status`, `Feedback`, `Community`, `Website`, `Forums`, `News`, `Announcements`) or `ServerLinkLabel::Custom(text_component)` for your own label. `Player.set_server_links` sets them for just one player instead.

## Running commands programmatically

### `.execute_command(command, sender)` { data-since=0.1 }

Runs `command` (without the leading `/`) as if `sender` had typed it. Useful for a plugin triggering another plugin's command, or your own, without duplicating its logic.

> [!NOTE]
> The `sender` argument here is `server::CommandSender`, a plain two-variant enum (`Console` or `Player(Player)`) declared in `server.wit`. It's a different type from the `CommandSender` **resource** covered in [Command executors](../commands/executors.md), which is what your own command handlers receive and has methods like `.send_message()`. Both happen to share the name `CommandSender`, so import one of them under an alias if you need both in the same file.

```rust
use pumpkin_plugin_api::server::CommandSender as ExecCommandSender;

server.execute_command("say Server restarting in 5 minutes!", ExecCommandSender::Console);
```

## Server configuration

Read-only getters for the server's static config: `.is_hardcore()`, `.is_online_mode()`, `.get_motd()`, `.has_whitelist()`, `.get_allow_nether()`, `.get_allow_end()`, `.get_view_distance()`, `.get_simulation_distance()`, `.get_default_gamemode()`.

## Managers

These return handles to server-wide subsystems, each covered in its own chapter:

- `.get_recipe_manager()`, see [Custom recipes](../items/recipes.md)
- `.get_op_manager()`, `.get_ban_manager()`, `.get_whitelist_manager()`, see [Ops, bans & whitelist](./ops-bans-and-whitelist.md)
- `.get_enchantment_manager()`, `.get_enchantment(id)`, `.get_all_enchantment_ids()`, see [Custom enchantments](../items/enchantments.md)
- `.get_datapack_manager()`, see [Datapacks](./datapacks.md)

### `.get_advancement(id)` / `.get_all_advancement_ids()` { data-since=0.1 }

Looks up an `AdvancementInfo` by id (accepts both the full form, `"minecraft:story/mine_stone"`, and the short form, `"story/mine_stone"`), or lists every registered advancement id on the server.

## Putting it together

A `/serverinfo` command reporting live performance and population stats:

```rust
use pumpkin_plugin_api::{command::CommandSender, context::Server, text::TextComponent};

fn server_info(sender: &CommandSender, server: &Server) {
  let tps = server.get_tps();
  let mspt = server.get_mspt();
  let players = server.get_player_count();
  let max_players = server.get_max_players();

  let msg = format!(
    "TPS: {tps:.1} | MSPT: {mspt:.1} | Players: {players}/{max_players}"
  );
  sender.send_message(TextComponent::text(&msg));
}
```

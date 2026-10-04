# Datapacks

`DatapackManager` inspects and controls the server's loaded datapacks, get one from `server.get_datapack_manager()`.

## Listing

### `.list_all_packs()` / `.list_enabled_packs()` / `.list_available_packs()` { data-since=0.1 }

Every known datapack, or just the enabled ones, or just the disabled-but-available ones. Each comes back as a `DatapackInfo { id, name, description, pack_format, is_enabled, recipe_count, function_count }`.

### `.get_pack(name)` / `.is_enabled(name)` { data-since=0.1 }

Looks up one datapack by name or id, or just checks whether it's currently enabled.

```rust
use pumpkin_plugin_api::Server;

fn log_datapacks(server: &Server) {
  let manager = server.get_datapack_manager();
  for pack in manager.list_all_packs() {
    println!("Datapack {}: enabled = {}", pack.name, pack.is_enabled);
  }
}
```

## Enabling & disabling

### `.enable_pack(name, position)` / `.disable_pack(name)` { data-since=0.1 }

Both return `Result<(), String>`. `position` is an `EnablePosition` controlling where the pack lands relative to the others in load order, `First`, `Last`, `Before(other_name)`, or `After(other_name)`, matching the same priority concept as the vanilla `/datapack enable` command.

```rust
use pumpkin_plugin_api::{Server, datapack::EnablePosition};

fn enable_custom_pack(server: &Server) -> Result<(), String> {
  let manager = server.get_datapack_manager();
  manager.enable_pack("my_custom_pack", &EnablePosition::Last)?;
  Ok(())
}
```

## Reloading & running functions

### `.reload()` { data-since=0.1 }

Reloads all enabled datapacks, recipes, and function tags, resyncs recipes with online players, and triggers the vanilla `#minecraft:load` function tag, the same thing `/reload` does. Returns `Result<(), String>`.

### `.execute_function(name)` { data-since=0.1 }

Runs a datapack function or function tag (`"namespace:fn"` or `"#namespace:tag"`) as if triggered by `/function`, returning the number of commands executed, or an error string if the function/tag doesn't exist.

## Putting it together

A `/datapacks` command listing enabled packs, and a `/reload-data` command for reloading them:

```rust
use pumpkin_plugin_api::{command::CommandSender, text::TextComponent, Server};

fn list_packs(sender: &CommandSender, server: &Server) {
  let manager = server.get_datapack_manager();
  let names: Vec<String> = manager.list_enabled_packs().into_iter().map(|p| p.name).collect();
  sender.send_message(TextComponent::text(&format!("Enabled: {}", names.join(", "))));
}

fn reload_data(sender: &CommandSender, server: &Server) {
  match server.get_datapack_manager().reload() {
    Ok(()) => sender.send_message(TextComponent::text("Datapacks reloaded.")),
    Err(e) => sender.send_message(TextComponent::text(&format!("Reload failed: {e}"))),
  }
}
```

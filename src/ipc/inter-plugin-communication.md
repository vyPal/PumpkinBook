# Sending and receiving IPC messages

Plugins can talk directly to each other, without going through commands or events, using a simple raw-bytes message-and-response protocol. This is what [Basic plugin logic](../plugin-101/plugin-logic.md) touched on for *receiving* messages, this chapter covers the full picture, including sending them.

## Receiving messages

Implement `handle_ipc_message` on your `Plugin`:

```rust
use pumpkin_plugin_api::{Context, Plugin, PluginMetadata, Result};

impl Plugin for ExamplePlugin {
  // ...

  fn handle_ipc_message(&self, sender: String, message: Vec<u8>) -> Result<Vec<u8>> {
    tracing::info!("Got a message from {sender}: {message:?}");
    Ok(vec![])
  }
}
```

`sender` is the name of the plugin the message came from, `message` is a raw byte payload, its structure is entirely up to whatever the sending plugin and yours agree on beforehand (a shared struct serialized with `serde`/`bincode`, a plain string, anything). Return the response bytes to send back (empty is fine if there's nothing to say), or an `Err(reason)` if you can't or won't handle it.

> [!NOTE]
> Unlike `on_load`/`on_unload`, doing nothing isn't the default behavior here. If you don't implement `handle_ipc_message` at all, the default implementation rejects every message it receives. Implement it if your plugin should be reachable over IPC.

## Sending messages

### `ipc::send_ipc_message(recipient, message)` { data-since=0.1 }

A free function, not a method on `Context` or `Server`, callable from anywhere.

```rust
use pumpkin_plugin_api::ipc;

let response = ipc::send_ipc_message("other-plugin", b"ping");
```

The return type is a nested result, `Result<Result<Vec<u8>, String>, ()>`:

- The **outer** `Result` is transport-level: `Err(())` means the message never reached a `handle_ipc_message` call at all, either because `recipient` doesn't match any loaded plugin, the target plugin exists but isn't currently running, or `recipient` is your own plugin's name (a plugin can't message itself).
- The **inner** `Result` is the target plugin's own response: `Ok(bytes)` is whatever it returned from `handle_ipc_message`, `Err(reason)` is whatever error string it chose to return (or the default rejection message, if it doesn't implement the handler).

```rust
use pumpkin_plugin_api::ipc;

match ipc::send_ipc_message("other-plugin", b"ping") {
  Ok(Ok(response)) => tracing::info!("Got a response: {response:?}"),
  Ok(Err(reason)) => tracing::warn!("Other plugin rejected the message: {reason}"),
  Err(()) => tracing::warn!("Couldn't deliver the message at all."),
}
```

> [!WARNING]
> The outer `Err(())` carries no detail about which of the three failure cases happened, sender-is-recipient, unknown recipient, or recipient not running all look identical from the caller's side. If you need to tell them apart, check `server.get_player_count()`-style existence first where relevant, or just treat any outer `Err(())` as "not currently reachable."

### It's synchronous

`send_ipc_message` blocks until the target plugin's `handle_ipc_message` returns (or the transport-level failure is determined), it isn't fire-and-forget and there's no separate polling step. Keep whatever you do inside `handle_ipc_message` fast, since it's now also blocking whichever plugin called you, the same one-call-at-a-time rule from [Task scheduler](../plugin-101/task-scheduler.md) applies across the whole chain.

The reply runs *inside* your call, so the reentrancy rules from [Basic plugin logic](../plugin-101/plugin-logic.md#plugin-state-handles-and-reentrancy) apply here too: if plugin A messages plugin B and B's handler messages A back, A's `handle_ipc_message` runs while A's original call is still in flight. Don't hold a lock across `send_ipc_message`, and don't let two plugins message each other in a loop, since nested calls are cut off at 64 levels and the call that crosses the limit kills its plugin.

### Plugins built against different API versions

The two plugin API versions (see [Plugin API versions](../api-versions.md)) can message each other. The payload is just bytes, so a v0.1 plugin and a v0.2 plugin on the same server talk to each other exactly like two plugins of the same version, in both directions.

## Putting it together

A small "economy" plugin exposing a balance-check message other plugins can call, and a second plugin using it:

```rust
// In the economy plugin:
fn handle_ipc_message(&self, sender: String, message: Vec<u8>) -> Result<Vec<u8>> {
  let Ok(player_id) = String::from_utf8(message) else {
    return Err("expected a UTF-8 player id".to_string());
  };

  let balance = self.get_balance(&player_id); // however you track it
  Ok(balance.to_string().into_bytes())
}
```

```rust
// In a shop plugin, checking a player's balance before a purchase:
use pumpkin_plugin_api::ipc;

fn check_balance(player_id: &str) -> Option<i64> {
  let response = ipc::send_ipc_message("economy", player_id.as_bytes());

  match response {
    Ok(Ok(bytes)) => String::from_utf8(bytes).ok()?.parse().ok(),
    _ => None,
  }
}
```

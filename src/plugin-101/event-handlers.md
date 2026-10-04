# Event handlers

As mentioned in [Basic plugin logic](./plugin-logic.md), the `Context` object passed to `on_load()` is how a plugin registers behavior with the server. Event handlers are the most common thing you'll register there: small pieces of code that the server calls whenever something happens in the game — a player joins, a block breaks, a chat message is sent, and so on.

Since a WASM plugin has no way to poll the game state on its own, events are the primary way your plugin finds out that something happened and gets a chance to react to (or even prevent) it.

## Registering a handler

To handle an event, define a type and implement the `EventHandler<E>` trait for it, where `E` is the event you want to listen for (for example `PlayerJoinEvent`). Then hand an instance of that type to `context.register_event_handler()` inside `on_load()`.

```rust
use pumpkin_plugin_api::{EventHandler, Server};
use pumpkin_plugin_api::events::{EventData, PlayerJoinEvent};

struct WelcomeHandler;

impl EventHandler<PlayerJoinEvent> for WelcomeHandler {
  fn handle(&self, _server: Server, event: EventData<PlayerJoinEvent>) -> EventData<PlayerJoinEvent> {
    // Do something with the event here
    event
  }
}
```

The `handle()` method receives a reference to the `Server` and the event's data, and **must** return the (possibly modified) data back. This mirrors the lower-level `handle_event(event_id, server, event) -> event` contract described in [Basic plugin logic](./plugin-logic.md), except the `EventHandler` trait lets you work with the concrete data type for your event instead of the generic `Event` variant.

### `context.register_event_handler(handler, priority, blocking) -> result<u32>` { data-since=0.1 }

This method, available on the `Context` object, registers a handler with the server.

```rust
fn on_load(&self, context: Context) -> Result<()> {
  context.register_event_handler(WelcomeHandler, EventPriority::Normal, true)?;
  Ok(())
}
```

- `handler` is any value whose type implements `EventHandler<E>`. The event type `E` is inferred from the handler, so you don't need to specify it explicitly.
- `priority` controls the order in which multiple handlers for the same event run, see [Event priority](#event-priority) below.
- `blocking` controls whether your handler can actually affect the outcome of the event, see [Blocking vs. non-blocking](#blocking-vs-non-blocking) below.

Like `handle_event`'s `event_id`, the returned `u32` uniquely identifies this specific handler registration.

## Event priority

`EventPriority` is a simple enum with five levels, from first to last:

```rust
pub enum EventPriority {
  Highest,
  High,
  Normal,
  Low,
  Lowest,
}
```

`priority` tells the server how this handler should be weighted against other handlers registered for the same event, from `Highest` down to `Lowest`. This matters when more than one plugin (or more than one handler in your own plugin) reacts to the same event, and you need your handler to run before or after another one.

If you don't have a specific reason to pick something else, `EventPriority::Normal` is a reasonable default.

## Blocking vs. non-blocking

The `blocking` flag decides whether the server waits for your handler to finish before moving on:

- A **blocking** handler pauses the corresponding action until it returns. Only a blocking handler can reliably cancel an event or have its modifications to the event data actually change what happens.
- A **non-blocking** handler runs without the server waiting on it. It gets its own copy of the event to inspect, and whatever it returns is thrown away: changes to the data, including setting `cancelled`, never reach the server, since it may already be done processing the event by the time the handler runs.

If your handler needs to cancel an event, or change data that affects gameplay (like a chat message or a join message), register it with `blocking: true`. Non-blocking handlers are a good fit for read-only side effects, like logging or updating your plugin's own state.

> [!WARNING]
> A blocking handler holds up the action it's attached to until it returns, so keep the work inside one fast. If you need to do something slow (a network request, heavy computation, disk I/O), consider deferring it to the task scheduler instead of doing it directly inside the handler. All plugins take turns, so a slow handler delays every other plugin's callbacks as well, see [Task scheduler](./task-scheduler.md#a-note-on-blocking).

### Events can arrive in the middle of your own calls

Events are delivered synchronously. If your code calls into the host and that action fires an event your plugin has a blocking handler for, the handler runs **inside** your call, before it returns. `server.broadcast_message()` is the easy one to trip over: it fires `ServerBroadcastEvent`, so a `ServerBroadcastEvent` handler that broadcasts a message of its own re-enters itself, and keeps doing so. The same goes for `server.execute_command()` re-entering your own command executors. Two consequences: don't hold a lock across host calls (the [Basic plugin logic](./plugin-logic.md#plugin-state-handles-and-reentrancy) chapter has the details), and guard against runaway recursion yourself. Nested calls are cut off at 64 levels, and the call that crosses the limit fails and kills the plugin.

If a handler fails at the WASM level (a panic, an `unwrap()` on `None`), the server logs `Wasm event handler failed` and carries on, but the plugin itself is dead from that point, see [Returning from an executor](../commands/executors.md#returning-from-an-executor).

## Reading and modifying event data

Each event has an associated data record, containing the details of what happened, alongside any fields that can be changed to affect it. Most (but not all) event data records also have a `cancelled: bool` field, letting you cancel the event outright.

```rust
use pumpkin_plugin_api::{EventHandler, Server};
use pumpkin_plugin_api::events::{BlockBreakEvent, EventData};

struct ProtectSpawnChest;

impl EventHandler<BlockBreakEvent> for ProtectSpawnChest {
  fn handle(&self, _server: Server, mut event: EventData<BlockBreakEvent>) -> EventData<BlockBreakEvent> {
    let pos = event.block_pos;
    let is_protected = pos.x == 0 && pos.y == 64 && pos.z == 0;

    if is_protected {
      event.cancelled = true;

      // block-break-event-data.player is `option<player>`, since some breaks
      // (e.g. explosions) aren't caused by a player at all
      if let Some(player) = &event.player {
        tracing::info!("Blocked a break attempt on the spawn chest by {}", player.get_name());
      }
    }

    event
  }
}
```

> [!NOTE]
> Refer to an event's data type through the `EventData<E>` alias (as shown above), rather than trying to name it directly (e.g. `PlayerJoinEventData`). The concrete data types aren't a stable part of the public API, `EventData<E>` always resolves to the correct one for whichever event `E` you're handling.

## Putting it together

### Example: greeting players

A minimal plugin that overwrites the default join message with its own.

```rust
use pumpkin_plugin_api::{
  register_plugin, Context, EventHandler, Plugin, PluginMetadata, Result, Server,
};
use pumpkin_plugin_api::events::{EventData, EventPriority, PlayerJoinEvent};
use pumpkin_plugin_api::text::TextComponent;

struct WelcomeHandler;

impl EventHandler<PlayerJoinEvent> for WelcomeHandler {
  fn handle(&self, _server: Server, mut event: EventData<PlayerJoinEvent>) -> EventData<PlayerJoinEvent> {
    let name = event.player.get_name();
    event.join_message = TextComponent::text(&format!("Welcome to the server, {name}!"));
    event
  }
}

struct WelcomePlugin;

impl Plugin for WelcomePlugin {
  fn new() -> Self { WelcomePlugin }

  fn metadata(&self) -> PluginMetadata {
    PluginMetadata {
      name: "WelcomePlugin".into(),
      version: "0.1.0".into(),
      authors: vec!["vyPal".into()],
      description: "Greets players with a custom message when they join".into(),
      dependencies: vec![],
      permissions: vec![],
    }
  }

  fn on_load(&self, context: Context) -> Result<()> {
    // blocking: true, since we need our replacement message to actually be used
    context.register_event_handler(WelcomeHandler, EventPriority::Normal, true)?;
    Ok(())
  }
}

register_plugin!(WelcomePlugin);
```

### Example: guarding a block

Building on the `ProtectSpawnChest` handler from earlier, here's the rest of the plugin that registers it.

```rust
use pumpkin_plugin_api::{
  register_plugin, Context, EventHandler, Plugin, PluginMetadata, Result, Server,
};
use pumpkin_plugin_api::events::{BlockBreakEvent, EventData, EventPriority};

struct ProtectSpawnChest;

impl EventHandler<BlockBreakEvent> for ProtectSpawnChest {
  fn handle(&self, _server: Server, mut event: EventData<BlockBreakEvent>) -> EventData<BlockBreakEvent> {
    let pos = event.block_pos;
    let is_protected = pos.x == 0 && pos.y == 64 && pos.z == 0;

    if is_protected {
      event.cancelled = true;

      if let Some(player) = &event.player {
        tracing::info!("Blocked a break attempt on the spawn chest by {}", player.get_name());
      }
    }

    event
  }
}

struct GuardPlugin;

impl Plugin for GuardPlugin {
  fn new() -> Self { GuardPlugin }

  fn metadata(&self) -> PluginMetadata {
    PluginMetadata {
      name: "GuardPlugin".into(),
      version: "0.1.0".into(),
      authors: vec!["vyPal".into()],
      description: "Protects the chest at spawn from being broken".into(),
      dependencies: vec![],
      permissions: vec![],
    }
  }

  fn on_load(&self, context: Context) -> Result<()> {
    // blocking: true, since our cancellation needs to actually stop the break
    context.register_event_handler(ProtectSpawnChest, EventPriority::Normal, true)?;
    Ok(())
  }
}

register_plugin!(GuardPlugin);
```

## Available events

The plugin WIT currently defines **273** events, covering most things a plugin might want to react to. A handful of the more commonly used ones, grouped by what they relate to:

- **Player**: `PlayerJoinEvent`, `PlayerLeaveEvent`, `PlayerChatEvent`, `PlayerMoveEvent`, `PlayerTeleportEvent`, `PlayerDeathEvent`, `PlayerRespawnEvent`, `PlayerInteractEvent`, `PlayerGamemodeChangeEvent`
- **Block**: `BlockBreakEvent`, `BlockPlaceEvent`, `BlockBurnEvent`, `BlockIgniteEvent`, `BlockRedstoneEvent`
- **Entity**: `EntityDamageEvent`, `EntityDeathEvent`, `EntitySpawnEvent`, `EntityCombustEvent`
- **Inventory**: `InventoryClickEvent`, `InventoryOpenEvent`, `CraftItemEvent`, `FurnaceSmeltEvent`
- **World**: `WorldLoadEvent`, `ChunkUnloadEvent`, `WeatherChangeEvent`
- **Server**: `ServerLoadEvent`, `ServerTickStartEvent`, `ServerBroadcastEvent`, `ServerCommandEvent`
- **Network**: `PacketReceivedEvent`, `PacketSentEvent`

Each one follows the exact same `FromIntoEvent`/`EventHandler` pattern shown above, just with a different associated data record. For the full, up to date list of events and the fields their data records carry, check the [event handler sources](https://github.com/Pumpkin-MC/Pumpkin/blob/master/crates/pumpkin-plugin-api/src/events) in the `pumpkin-plugin-api` crate, or the [`event` interface](https://github.com/Pumpkin-MC/pumpkin-plugin-wit) in the WIT definitions directly.

> [!WARNING]
> Not every event in the WIT is fired by the server yet. As of the commit this book was checked against, 58 of the 273 are declared and can be registered for, but nothing in the server ever creates them, so a handler for one of them simply never runs. Some of the notable ones are `PlayerCommandPreprocessEvent`, `AsyncPlayerChatEvent`, `PlayerPreLoginEvent`, `PlayerPortalEvent`, `EntityKnockbackEvent` and `HangingPlaceEvent`. The [Event reference](../advanced/event-reference.md) lists every event with its category and whether it fires.

Pumpkin is still working towards full parity with the Spigot/Bukkit event API — [issue #1609](https://github.com/Pumpkin-MC/Pumpkin/issues/1609) tracks which Spigot events have already been ported over, and is a good way to see what's still missing.

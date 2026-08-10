# Basic plugin logic

Each Pumpkin plugin is essentially just a single structure or class (depending on your programming language), that exposes a couple predefined methods, that the server can then invoke.

This structure can, but doesn't have to contain any actual data, this is purely up to the developer of the plugin. For now we will just use an empty struct:

```rust
use pumpkin_plugin_api::Plugin;

struct ExamplePlugin;

impl Plugin for ExamplePlugin {
  fn new() -> Self { ExamplePlugin }
}
```

## Primary plugin methods

### `metadata() -> plugin_metadata`

The plugin metadata are made up of a single structure that plugins must return, so that the server knows which plugin this is and what to do with it. The plugin struct **must** expose a method that returns this `PluginMetadata` object.

```rust
use pumpkin_plugin_api::{Plugin, PluginMetadata};

struct ExamplePlugin;

impl Plugin for ExamplePlugin {
  fn new() -> Self { ExamplePlugin }

  fn metadata(&self) -> PluginMetadata {
    PluginMetadata {
      // Name of the plugin
      // This name is case sensitive
      // The plugin's namespace will be tied to this name
      name: "ExamplePlugin".into(),
      // The version of the plugin
      // This is only used when displaying plugin info (/plugins)
      version: "0.1.0".into(),
      // The plugin's authors
      // Also only used when showing plugin info
      authors: vec!["vyPal".into()],
      // The plugin's description
      // Unexpectedly also only used when displaying plugin info
      description: "An example plugin in rust".into(),
      // The plugin's dependency list
      // These are the names of other plugins to be loaded before this one
      dependencies: vec![],
      // The plugin's permissions
      // These are used to give the plugin access to system resouces
      // Not to be confused with command permissions
      // More about permissions will be in a separate chapter
      permissions: vec![],
    }
  }
}
```

### `on_load(context) -> result<>`

This is the most important method of each plugin. It is the method that is executed by the server when it's this plugin's turn to initialize. The server also provides a `Context` object which is how plugins can register further behavior (like commands and event handlers) with the server.

It is recommended to _not keep_ a copy of the `Context` object past the return of this method, as it's lifetime is not guaranteed[^context-lifetime].

[^context-lifetime]: To the best of my knowledge, the `Context` object is destroyed on the server side after the method that created it (either `on_load()` or `on_unload()`) has returned. Developers should register all command executors and event handlers in the `on_load()` method, and if the path to the plugin data directory is needed outside these methods, it should be copied either to the plugin struct, or to some other variable

The `on_load()` method returns a `result` object, with either an empty success response, or a error string if an error occurred during loading.

> [!NOTE]
> The `on_load()` method is optional (doesn't have to be implemented), but without it the plugin won't exactly do anything.

```rust
use pumpkin_plugin_api::{Context, Plugin, PluginMetadata, Result};

struct ExamplePlugin;

impl Plugin for ExamplePlugin {
  fn new() -> Self { ExamplePlugin }

  fn metadata(&self) -> PluginMetadata {
    PluginMetadata {
      name: "ExamplePlugin".into(),
      version: "0.1.0".into(),
      authors: vec!["vyPal".into()],
      description: "An example plugin in rust".into(),
      dependencies: vec![],
      permissions: vec![],
    }
  }

  fn on_load(&mut self, context: Context) -> Result<()> {
    // This is where your plugin will register all command executors and event handlers
    // Both of these will be addressed later in individual chapters

    // Get the path to the plugin's dedicated data folder
    let data_dir = context.get_data_folder();

    // Check if data dir exists and return error if not
    if !std::fs::exists(data_dir).is_ok_and(|r| r) {
      return Err("Plugin data dir does not exist!".into());
    }

    Ok(())
  }
}
```

### `on_unload(context) -> result<>`

This method is similar to `on_load()`, except that it runs right before the plugin is unloaded (plugins can be unloaded for various reasons, like the server stopping, a crash, or just an admin running the unload command). The primary use of this method is to finalize and close out any open data sources (DBs, config/cache files, etc.), but can be used for anything the plugin author wants. No matter the result returned by this method, the plugin will be unloaded internally in the server, so when this method is called, it guarantees that no other methods of this plugin will be called later.

The arguments to this method are the same as `on_load()`, providing you with the same `Context` object.

```rust
use pumpkin_plugin_api::{Context, Plugin, PluginMetadata, Result};

struct ExamplePlugin;

impl Plugin for ExamplePlugin {
  fn new() -> Self { ExamplePlugin }

  fn metadata(&self) -> PluginMetadata {
    PluginMetadata {
      name: "ExamplePlugin".into(),
      version: "0.1.0".into(),
      authors: vec!["vyPal".into()],
      description: "An example plugin in rust".into(),
      dependencies: vec![],
      permissions: vec![],
    }
  }

  fn on_load(&mut self, context: Context) -> Result<()> {
    Ok(())
  }

  fn on_unload(&mut self, context: Context) -> Result<()> {
    // Save your database or anything else that needs persisting
    Ok(())
  }
}
```

### `handle_ipc_message(sender, message) -> result<message>`

This method is called by the host when another plugin sends yours a message directly, letting plugins talk to each other without going through events or commands. Unlike the handler methods further down, there's no separate registration step for this one, you implement it directly on your plugin, the same way as `on_load` and `on_unload`.

`sender` is the name of the plugin the message came from, and `message` is a raw byte payload, its structure is entirely up to whatever the sending plugin and yours agree on. Return the (possibly empty) response to send back, or an error string if the message couldn't be handled.

> [!NOTE]
> Unlike `on_load`/`on_unload`, doing nothing isn't the default behavior here, if you don't implement this method, the default implementation rejects every message it receives. Implement it if your plugin should be reachable over IPC.

```rust
use pumpkin_plugin_api::{Context, Plugin, PluginMetadata, Result};

struct ExamplePlugin;

impl Plugin for ExamplePlugin {
  fn new() -> Self { ExamplePlugin }

  fn metadata(&self) -> PluginMetadata {
    PluginMetadata {
      name: "ExamplePlugin".into(),
      version: "0.1.0".into(),
      authors: vec!["vyPal".into()],
      description: "An example plugin in rust".into(),
      dependencies: vec![],
      permissions: vec![],
    }
  }

  fn handle_ipc_message(&mut self, sender: String, message: Vec<u8>) -> Result<Vec<u8>> {
    tracing::info!("Got a message from {sender}: {message:?}");
    Ok(vec![])
  }
}
```

A full chapter on plugin-to-plugin IPC, including how to send messages to other plugins, is planned for later.

## Other methods

The Pumpkin plugin WIT contains many more methods that each plugin can implement to enable more functionality, however in most plugin frameworks (like [pumpkin-plugin-api](https://github.com/Pumpkin-MC/Pumpkin/blob/master/crates/pumpkin-plugin-api) for Rust, or [pumpkin-api-py](https://github.com/Pumpkin-MC/pumpkin-api-py) for Python) abstract these methods away and implement the automatically so that you don't have to worry about them.

> [!NOTE]
> This section will only be useful for some languages that don't yet have a wrapper library that handles these automatically (so this is primarily aimed at C/C++/C#, or other languages not listed in the official docs). But feel free to read on if you are interested in how the plugin API works under the hood

### `handle_event(event_id, server, event) -> event`

This method is called by the server when a event that your plugin has registered a handler for is fired by the server.

The `event_id` is equal to the id that was supplied by your plugin when registering the handler. Plugins are responsible for tracking which id belongs to which of it's internal handler methods (any function that you designate for event handling), and properly routing the even to it.

The `server` is a reference to the main `Server` object. Each event handler gets this reference.

The `event` is a reference to the event data. The `Event` type is a variant (also known as an enum in many languages). The plugin is responsible for remembering which type of event this handler was registered for and treating the `event` object as the corresponding type.

This method must also return the received `event` object. The data in the `event` object can be modified, however the modified data can be dropped by the server, based on whether the event was registered as blocking, and whether the event type allows modification.

### `handle_command(command_id, sender, server, args) -> result<s32>`

This handler is similar to the event handler but has some additional arguments, namely the command sender (variant/enum representing either a player, the console, command block, or RCON) and the command arguments (structure/class that exposes a `.get_value(key) -> arg` method to fetch the values of the arguments that were used when running the command).

One thing to keep in mind is that the `command_id` again corresponds to the id that the plugin used to register **the executor for the specific branch** of the command tree. The command tree of a specific command can have several executors at different parts of the tree, each needs it's own unique id. And like with the event handler, the plugin is responsible for tracking these ids and routing data to the proper internal handler for the command.

The returned result should either be `Ok(result_number)` if the command succeeded, or `Err(command_error)` if the command failed (the `CommandError` type is an enum with several reasons for why the command failed, which result in different errors being printed to the sender. If you want to send the sender a custom error, return `Ok(number)` instead and send your own message before returning). The `result_number` is a signed 32-bit integer corresponding to the result code of your command (like builtin java command handlers return). **If you do not know which value to return or don't care about this value, return `Ok(1)`.**

### `handle_task(handler_id, server)`

This method is used with [Pumpkin's task scheduler](./task-scheduler.md), and is called by the host when is time to run one of your plugin's scheduled tasks. It is yet again the plugin's responsibility to remember which handler was registered with which id and to call it.

### `handle_ipc_message(sender, message) -> result<message>`

This method is called by the host when another plugin sends yours a message directly, letting plugins talk to each other without going through events or commands. `sender` identifies which plugin the message came from, and `message` is a raw byte payload, its structure is entirely up to whatever the sending plugin and yours agree on. Return the (possibly empty) response to send back, or an error string if the message couldn't be handled. A full chapter on plugin-to-plugin IPC is planned for later.

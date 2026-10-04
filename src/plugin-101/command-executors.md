# Command executors

Alongside event handlers, the other thing you'll typically register in `on_load()` (as mentioned in [Basic plugin logic](./plugin-logic.md)) is commands. This chapter covers just enough to get a basic command up and running. Building the full command tree, with arguments and sub-commands, is a big enough topic that it gets [its own section](../commands/command-tree.md).

## Building a command

A `Command` is created with a primary name (plus any aliases) and a description:

```rust
use pumpkin_plugin_api::command::Command;

let command = Command::new(&["hello".to_string()], "Greets whoever runs it");
```

The first entry in the name list is the command's primary name, any further entries are aliases. Names are lowercased when the command is registered.

### `command.execute(handler)` { data-since=0.1 }

To actually do something when the command runs, attach a handler that implements `CommandHandler`:

```rust
use pumpkin_plugin_api::command::{CommandError, CommandSender, ConsumedArgs};
use pumpkin_plugin_api::commands::CommandHandler;
use pumpkin_plugin_api::{Result, Server};

struct HelloCommand;

impl CommandHandler for HelloCommand {
  fn handle(&self, sender: CommandSender, _server: Server, _args: ConsumedArgs) -> Result<i32, CommandError> {
    // 1 signals success, matching what built-in commands return
    Ok(1)
  }
}
```

`sender` is whoever ran the command (a player, the console, a command block, or RCON), `args` gives you access to any arguments the command tree consumed. Since our command doesn't declare any arguments yet, `args` is unused here, see [Command executors](../commands/executors.md#reading-arguments) for how to read them once you have some.

`execute()` attaches the handler and returns the command again, so it chains naturally:

```rust
let command = Command::new(&["hello".into()], "Greets whoever runs it")
  .execute(HelloCommand);
```

## Registering the command

### `context.register_command(command, permission)` { data-since=0.1 }

Like event handlers, commands are registered on the `Context` object inside `on_load()`. The second argument is the permission node required to run the command:

```rust
fn on_load(&self, context: Context) -> Result<()> {
  let command = Command::new(&["hello".into()], "Greets whoever runs it")
    .execute(HelloCommand);

  context.register_command(command, "HelloPlugin:use");

  Ok(())
}
```

## Command permissions

`register_command()` treats the permission argument as an opaque string — it doesn't check it against anything. You could point your command at a permission node belonging to another plugin, or an internal `minecraft:` one, and the server won't stop you. Namespacing your own permissions under your plugin's name, as above, is just a convention worth following to avoid stepping on other plugins' nodes.

The one thing it does do is fill the namespace in for you when you leave it out: a permission string with no colon in it gets your plugin's name prefixed automatically, so passing `"use"` here would land on the same `"HelloPlugin:use"` node as spelling it out.

That convention **is** enforced the moment you explicitly define one of your own permission nodes with `context.register_permission()`: the part before the colon must exactly match your plugin's `name` field from `PluginMetadata`, character for character, or registration fails.

> [!WARNING]
> Registering a command does **not** register its permission node. If `"HelloPlugin:use"` was never given to `context.register_permission()`, the node simply doesn't exist — and an unrecognized permission denies every player, including server operators. It doesn't deny the console, though, which passes every permission check before the node is ever looked up. So skipping the call below wouldn't make `/hello` look broken, it would make it look console-only. See [Command permissions](../commands/permissions.md#unregistered-nodes).

```rust
use pumpkin_plugin_api::permission::{Permission, PermissionDefault};

// Not to be confused with the `permissions` (plural) module used for
// PluginMetadata's sandbox permissions — this is a different system
context.register_permission(&Permission {
  node: "HelloPlugin:use".into(),
  description: "Allows running /hello".into(),
  default: PermissionDefault::Allow,
  children: vec![],
})?;
```

`PermissionDefault::Allow` grants the permission to everyone by default; `PermissionDefault::Op(level)` restricts it to operators of at least the given level, and `PermissionDefault::Deny` grants it to nobody until it's explicitly assigned. Managing permissions in more detail (wildcards, child nodes, checking them inside an executor, granting them at runtime) is covered in [Command permissions](../commands/permissions.md).

## Colliding with an existing command

`register_command()` doesn't check whether a name is already taken. Built-in commands and plugin commands all live in the same command tree, and registering a name that already exists **merges** your command into the existing one instead of replacing it. The rules, which are the same whether the first registration came from the server or from another plugin:

- Command names are lowercased when they're registered, so `Warp` and `warp` are the same command.
- New branches are added next to the existing ones. If you register a `/gamemode` that only has a `probe` literal under it, `/gamemode probe` becomes a working sub-command while `/gamemode survival` keeps running the built-in one. Same-named nodes merge recursively.
- Where both registrations put an executor on the same node, yours wins. Registering a bare `/list` with an executor takes over what a plain `/list` does, but anything under it stays as it was.
- **The first registration decides the permission for the whole command.** The permission requirement of an existing root node is kept, and the one you pass to your own `register_command()` is silently dropped. That includes the branches you added: a player who may run the original command can run your new sub-command too.

> [!WARNING]
> Because your permission string is ignored when you merge into a name someone else registered first, don't rely on it to protect a branch you add to a command you don't own. Check `sender.has_permission(...)` inside your executor instead, see [Checking permissions yourself](../commands/permissions.md#checking-permissions-yourself). Which registration comes first for two plugins depends on load order, so don't depend on that either.

Aliases are separate root entries that copy the primary command's permission requirement and executor and then redirect into the primary command's node, so anything merged into the primary node later (including by another plugin) shows up under the aliases too.

When your plugin unloads, the commands it registered under their own names (and their aliases) are switched off and answer "unknown command" until a plugin registers them again, for example after a reload. Branches you merged into a command that someone else registered are not removed, so make sure your executors cope with being called while your plugin is gone, or avoid merging into other commands in the first place.

## Putting it together

```rust
use pumpkin_plugin_api::command::{Command, CommandError, CommandSender, ConsumedArgs};
use pumpkin_plugin_api::commands::CommandHandler;
use pumpkin_plugin_api::permission::{Permission, PermissionDefault};
use pumpkin_plugin_api::{
  register_plugin, Context, Plugin, PluginMetadata, Result, Server,
};

struct HelloCommand;

impl CommandHandler for HelloCommand {
  fn handle(&self, sender: CommandSender, _server: Server, _args: ConsumedArgs) -> Result<i32, CommandError> {
    Ok(1)
  }
}

struct HelloPlugin;

impl Plugin for HelloPlugin {
  fn new() -> Self { HelloPlugin }

  fn metadata(&self) -> PluginMetadata {
    PluginMetadata {
      name: "HelloPlugin".into(),
      version: "0.1.0".into(),
      authors: vec!["vyPal".into()],
      description: "Adds a friendly /hello command".into(),
      dependencies: vec![],
      permissions: vec![],
    }
  }

  fn on_load(&self, context: Context) -> Result<()> {
    context.register_permission(&Permission {
      node: "HelloPlugin:use".into(),
      description: "Allows running /hello".into(),
      default: PermissionDefault::Allow,
      children: vec![],
    })?;

    let command = Command::new(&["hello".into()], "Greets whoever runs it")
      .execute(HelloCommand);

    context.register_command(command, "HelloPlugin:use");

    Ok(())
  }
}

register_plugin!(HelloPlugin);
```

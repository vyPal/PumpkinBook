# Command executors

Alongside event handlers, the other thing you'll typically register in `on_load()` (as mentioned in [Basic plugin logic](./plugin-logic.md)) is commands. This chapter covers just enough to get a basic command up and running — building the full command tree, with arguments, sub-commands and suggestions, is a big enough topic that it gets its own chapter later on.

## Building a command

A `Command` is created with a primary name (plus any aliases) and a description:

```rust
use pumpkin_plugin_api::command::Command;

let command = Command::new(vec!["hello".into()], "Greets whoever runs it".into());
```

The first entry in the name list is the command's primary name, any further entries are aliases.

### `command.execute(handler)`

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

`sender` is whoever ran the command (a player, the console, a command block, or RCON), `args` gives you access to any arguments the command tree consumed. Since our command doesn't declare any arguments yet, `args` is unused here — that's covered in the dedicated command tree chapter.

`execute()` attaches the handler and returns the command again, so it chains naturally:

```rust
let command = Command::new(&["hello".into()], "Greets whoever runs it")
  .execute(HelloCommand);
```

## Registering the command

### `context.register_command(command, permission)`

Like event handlers, commands are registered on the `Context` object inside `on_load()`. The second argument is the permission node required to run the command:

```rust
fn on_load(&mut self, context: Context) -> Result<()> {
  let command = Command::new(&["hello".into()], "Greets whoever runs it")
    .execute(HelloCommand);

  context.register_command(command, "HelloPlugin:use");

  Ok(())
}
```

## Command permissions

`register_command()` treats the permission argument as an opaque string — it doesn't check it against anything. You could point your command at a permission node belonging to another plugin, or an internal `minecraft:` one, and the server won't stop you. Namespacing your own permissions under your plugin's name, as above, is just a convention worth following to avoid stepping on other plugins' nodes.

That convention **is** enforced the moment you explicitly define one of your own permission nodes with `context.register_permission()`: the part before the colon must exactly match your plugin's `name` field from `PluginMetadata`, character for character, or registration fails.

> [!WARNING]
> Registering a command does **not** register its permission node. If `"HelloPlugin:use"` was never given to `context.register_permission()`, the node simply doesn't exist — and an unrecognized permission denies everyone, including server operators. Without the call below, nobody would be able to run `/hello` at all.

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

`PermissionDefault::Allow` grants the permission to everyone by default; `PermissionDefault::Op(level)` restricts it to operators of at least the given level, and `PermissionDefault::Deny` grants it to nobody until it's explicitly assigned. Managing permissions in more detail (wildcards, child nodes, checking them outside of commands) is covered together with the rest of the command tree in a later chapter.

## Overriding commands

`register_command()` doesn't check whether a name is already taken — register one that collides with an existing command, and yours can end up running instead. Exactly how depends on which system the existing command came from.

Built-ins like `/gamemode`, `/give`, `/effect`, and `/say` are registered through the exact same map plugins use, so a colliding registration simply replaces them outright, for every player — whichever one calls `register_command()` last wins, with no error or warning either way. The same applies if two plugins register the same name.

Built-ins like `/kill`, `/op`, `/scoreboard`, and `/advancement` go through a separate, newer command system that's checked before plugin commands ever get a chance to run, so your registration can never directly replace theirs.

> [!NOTE]
> That newer system still ends up indirectly shadowed, though: it reports "unknown command" — not "permission denied" — for a player who doesn't meet its own permission requirement, and the server treats that exactly like the command not existing there at all, falling through to check for a plugin's command with the same name. Since these built-ins are almost always gated to operators, this means a plugin can effectively take over `/kill` or `/op` for regular players, while operators still see the real thing. A command that's available to everyone by default, like `/help`, can never be shadowed this way, since it never fails its own permission check.

Aliases are their own, independent registrations that point back at a primary name, rather than owning a copy of the command tree. So if a later registration only replaces a primary name and not the aliases that originally came with it, those aliases don't stop working — they just start running whatever command currently owns that primary name, which may no longer be the one they were originally registered alongside.

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

  fn on_load(&mut self, context: Context) -> Result<()> {
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

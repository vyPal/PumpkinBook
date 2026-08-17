# Command executors

An executor is the code that actually runs when a player's input lands on one of your [command tree](./command-tree.md) nodes. In Rust that's any type implementing `CommandHandler`:

```rust
use pumpkin_plugin_api::{
  command::{CommandError, CommandSender, ConsumedArgs},
  commands::CommandHandler,
  Result, Server,
};

struct HelloCommand;

impl CommandHandler for HelloCommand {
  fn handle(&self, sender: CommandSender, server: Server, args: ConsumedArgs) -> Result<i32, CommandError> {
    Ok(1)
  }
}
```

Attach it with `.execute()` and you're done. The wrapper library assigns the handler an id, keeps it in a registry, and routes incoming invocations to the right one, which is the bookkeeping described in [Basic plugin logic](../plugin-101/plugin-logic.md#handle_commandcommand_id-sender-server-args---results32) if you're working in a language without a wrapper.

Because your executor is a struct rather than a bare function, it can carry state. That's the normal way to give a command access to your plugin's config or data:

```rust
struct SetPermissionCommand {
  plugin_data: Arc<PluginData>,
  plugin_config: Arc<RwLock<PluginConfig>>,
}
```

The same instance handles every invocation, and `handle()` only takes `&self`, so anything mutable needs to sit behind a `Mutex`, `RwLock` or `RefCell`.

## Reading arguments

### `args.get_value(key)`

The `key` is the **name you gave the argument node** when you built the tree. What comes back is an `Arg`, which you match on to get at the value:

```rust
if let Arg::Players(targets) = args.get_value("players") {
  for target in targets {
    target.set_gamemode(GameMode::Survival);
  }
}
```

> [!WARNING]
> `get_value` returns an `Arg`, not an `Option<Arg>`. There is no "argument missing" signal. A key that was never consumed, a key belonging to a branch the player didn't take, and a key you simply misspelled all give you the exact same thing: `Arg::Simple("")`, an empty string.

That has two practical consequences.

First, a typo in a key is silent. It doesn't panic, it doesn't log, your executor just quietly behaves as though the player left the argument out. Declaring the names as constants and using them in both places is the cheap fix, and it's what most plugins end up doing:

```rust
const PLAYERS_ARG: &str = "players";

// building
CommandNode::argument(PLAYERS_ARG, &ArgumentType::Players)

// reading
args.get_value(PLAYERS_ARG)
```

Second, "was this optional argument supplied?" is answered by whether the variant matches, not by an `Option`. That's what makes the [optional argument pattern](./command-tree.md#optional-arguments) work: the same executor sits on both branches, and a mismatched variant tells you the player took the short one.

```rust
// `/gamemode` or `/gamemode <players>`, same executor on both
let Arg::Players(targets) = args.get_value(PLAYERS_ARG) else {
  // no players given, so act on whoever ran it
  return self.apply_to_sender(&sender);
};
```

> [!WARNING]
> That trick does **not** work for string arguments, and this is worth stopping on. The "missing" value is itself an `Arg::Simple`, so a `String` argument matches `Arg::Simple` whether or not the player supplied it. The `else` branch above would simply never run, and you'd process an empty name as though it were real.
>
> For an optional `String`, match the variant and then check the value:
>
> ```rust
> let name = match args.get_value(HOME_NAME) {
>   Arg::Simple(name) if !name.is_empty() => name,
>   // not supplied, `/home` rather than `/home <name>`
>   _ => "home".to_string(),
> };
> ```
>
> Only the single word and quotable string types are affected, since those are the ones that produce `Arg::Simple`. A greedy string comes back as `Arg::Msg`, which doesn't collide with the missing value, so matching the variant is enough there.

### Reading several at once

Arguments consumed anywhere along the matched path are all in the same map, so a deep executor can pull several at once. Matching them as a tuple keeps the failure case in one place:

```rust
match (args.get_value("players"), args.get_value("node"), args.get_value("value")) {
  (Arg::Players(players), Arg::Simple(node), Arg::Bool(value)) => {
    for player in players {
      player.set_permission(&node, value);
    }
    Ok(1)
  }
  _ => Err(CommandError::CommandFailed(TextComponent::text("Invalid arguments."))),
}
```

Which `Arg` variant to expect for each argument type is on the [Argument types](./argument-types.md) page.

## The sender

`CommandSender` is whoever ran the command. It's not always a player, so most commands start by working out what they're dealing with.

### Finding out who it is

```rust
if let Some(player) = sender.as_player() {
  // a real player
} else {
  sender.send_message(TextComponent::text("This one is player only, sorry."));
  return Ok(1);
}
```

- `as_player()` returns `Option<Player>`, and is the one you'll reach for most.
- `is_player()` and `is_console()` are quick boolean checks.
- `get_command_sender_type()` gives you the full picture as an enum: a player, the console, RCON, a command block (along with the world it's in), or a dummy sender.
- `get_name()` works for all of them.

### Talking back

- `send_message(text)` is the normal reply.
- `send_system_message(text)` sends it as a system message.
- `send_error(text)` sends it as an error.

All three take a `TextComponent`, so you can colour and format them:

```rust
let text = TextComponent::text("You are not flying right now.");
text.color_named(NamedColor::Red);
sender.send_message(text);
```

### Where they are

`position()` and `world()` both return `Option`, since the console isn't anywhere in particular. `get_locale()` gives you the sender's language, which pairs with the i18n interface if you're translating your messages.

### What they're allowed to do

`has_permission(server, node)` checks a permission node, `permission_level()` and `has_permission_level(level)` check the op level. These are worth knowing about even though your command already has a permission attached, since they let you gate individual branches, which is otherwise impossible. See [Command permissions](./permissions.md).

### The rest

`set_success_count(count)` reports how many things your command affected, in the vanilla sense that command blocks and `/execute` can read back. `should_receive_feedback()`, `should_broadcast_console_to_ops()` and `should_track_output()` expose the vanilla gamerules around command output, if you want to be a good citizen about how chatty your command is.

## Returning from an executor

The return type is `Result<i32, CommandError>`.

### On success

The `i32` is the vanilla-style result code, the same number built-in commands return, and it's what `/execute store result` would pick up. If your command doesn't have a natural count to report, **return `Ok(1)`**. That's success.

### On failure

`Err(CommandError)` has four variants, and they are not equally useful:

| Variant | What the sender sees |
|---|---|
| `CommandFailed(TextComponent)` | your component, exactly as you built it |
| `PermissionDenied` | the standard red "you do not have permission" message |
| `InvalidConsumption(Option<String>)` | `Internal error (See logs for details)` |
| `InvalidRequirement` | `Internal error (See logs for details)` |

The bottom two also write an `error!` line to the server log. They exist to report that the command *system* did something impossible, like an argument that parsed but couldn't be read back. They are not for telling a player they typed the wrong thing, and using them that way gives the player a scary internal error and fills the log with noise.

> [!NOTE]
> For anything the player caused, send your own message and return `Ok(1)`. You get full control over the wording and formatting, and nothing lands in the log. `CommandFailed` is the reasonable middle ground when you want a one-line failure and don't need anything fancy. This is what most plugins settle on.

```rust
// Good: the player gets a clear, friendly message
let Some(player) = sender.as_player() else {
  let text = TextComponent::text("Only a player can use /home.");
  text.color_named(NamedColor::Red);
  sender.send_message(text);
  return Ok(1);
};

// Also fine
return Err(CommandError::CommandFailed(TextComponent::text("Home not found.")));

// Avoid: the player sees "Internal error (See logs for details)"
return Err(CommandError::InvalidRequirement);
```

If your executor panics or otherwise fails at the WASM level, the server catches it and shows the sender a red `Wasm command failed with following error: ...`. Useful while developing, not something you want players to ever see.

## Keep executors quick

Your executor runs while the server is waiting on the command, the same way a blocking [event handler](../plugin-101/event-handlers.md#blocking-vs-non-blocking) does. Slow work in there stalls things.

If a command kicks off something genuinely slow, like a network request or a big file read, acknowledge it immediately, hand the work to the [task scheduler](../plugin-101/task-scheduler.md), and message the player again when it's done.

## Commands you didn't register

Two events let you see commands going past, which is handy for logging, or for blocking a command from another plugin:

- `PlayerCommandSendEvent` fires when a player sends a command, with the command string (no leading `/`). Cancellable.
- `ServerCommandEvent` fires for commands run from the console. Also cancellable.

Both need a blocking handler if you intend to cancel them. See [Event handlers](../plugin-101/event-handlers.md).

Going the other way, `server.execute_command(command, sender)` runs a command string as a given sender, if you want your plugin to trigger one.

## Putting it together

A `/warp <name>` command carrying shared state, handling a missing argument, and replying properly in every failure case.

```rust
use std::{collections::HashMap, sync::{Arc, RwLock}};

use pumpkin_plugin_api::{
  command::{Command, CommandError, CommandNode, CommandSender, ConsumedArgs},
  command_wit::{Arg, ArgumentType, StringType},
  commands::CommandHandler,
  common::NamedColor,
  text::TextComponent,
  Context, Result, Server,
};

const NAME_ARG: &str = "name";

pub struct Warps(RwLock<HashMap<String, (f64, f64, f64)>>);

struct WarpCommand {
  warps: Arc<Warps>,
}

impl CommandHandler for WarpCommand {
  fn handle(&self, sender: CommandSender, _server: Server, args: ConsumedArgs) -> Result<i32, CommandError> {
    let Some(player) = sender.as_player() else {
      let text = TextComponent::text("Only a player can warp.");
      text.color_named(NamedColor::Red);
      sender.send_message(text);
      return Ok(1);
    };

    // A string argument always matches Arg::Simple, so check the value too:
    // an unconsumed argument comes back as an empty string, not as an Option
    let name = match args.get_value(NAME_ARG) {
      Arg::Simple(name) if !name.is_empty() => name,
      _ => {
        let text = TextComponent::text("Usage: /warp <name>");
        text.color_named(NamedColor::Red);
        sender.send_message(text);
        return Ok(1);
      }
    };

    let target = self.warps.0.read().unwrap().get(&name).copied();

    let Some(pos) = target else {
      let text = TextComponent::text(&format!("There is no warp called '{name}'."));
      text.color_named(NamedColor::Red);
      sender.send_message(text);
      return Ok(1);
    };

    player.teleport(pos, None, None, player.get_world());

    let text = TextComponent::text(&format!("Warped to {name}."));
    text.color_named(NamedColor::Green);
    sender.send_message(text);

    Ok(1)
  }
}

pub fn register(context: &Context, warps: Arc<Warps>) -> Result<()> {
  let warp = Command::new(&["warp".to_string()], "Teleport to a warp point");

  warp.then(
    CommandNode::argument(NAME_ARG, &ArgumentType::String(StringType::SingleWord))
      .execute(WarpCommand { warps: Arc::clone(&warps) }),
  );

  context.register_command(warp, "MyPlugin:warp");
  Ok(())
}
```

Note that every failure path returns `Ok(1)` after saying something useful. The player always knows what went wrong, and the server log stays clean.

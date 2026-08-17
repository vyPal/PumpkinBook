# Building a command tree

[Command executors](../plugin-101/command-executors.md) in the 101 section covered a command that does exactly one thing: you type `/hello`, something happens. Real commands are rarely that flat. You want `/home` and `/home <name>`, or `/uhc start` and `/uhc status`, or something as deep as `/gp user <players> permission set <node> <value>`.

Pumpkin builds those out of a *tree*. The command name is the root, and every word the player types after it walks one level further down. Each position in the tree is a node, and nodes come in two flavors:

- **Literal** nodes match one fixed word. The `start` in `/uhc start`.
- **Argument** nodes consume input and hand it to you as a value. The `<players>` in `/gp user <players>`.

Attach an executor to any node, and that executor runs when the player's input lands exactly on it.

## The pieces

### `Command::new(names, description)`

The root of the tree. The first name is the command's primary name, everything after it is an alias:

```rust
use pumpkin_plugin_api::command::Command;

let command = Command::new(
  &["balance".to_string(), "bal".to_string(), "money".to_string()],
  "Show a balance",
);
```

That registers `/balance`, with `/bal` and `/money` pointing at it.

Note the signature, it trips people up: the names are a **slice of `String`**, and the description is a plain `&str`. So `&["balance".to_string()]` rather than `vec!["balance".into()]`.

> [!NOTE]
> Aliases aren't copies of the tree, they're separate entries in the server's command registry that point back at the primary name. That has a consequence worth knowing about when several plugins fight over the same name, which is covered in [Overriding commands](../plugin-101/command-executors.md#overriding-commands).

### `CommandNode::literal(name)`

A fixed word:

```rust
use pumpkin_plugin_api::command::CommandNode;

let start = CommandNode::literal("start");
```

### `CommandNode::argument(name, type)`

A value the player supplies. The `name` is not shown to the player as such, it's the **key you'll use to read the value back** inside your executor, so pick something you'll recognise:

```rust
use pumpkin_plugin_api::{command::CommandNode, command_wit::ArgumentType};

let players = CommandNode::argument("players", &ArgumentType::Players);
```

The client does show the name in its tab-completion hint as `<players>`, so it's worth making it readable rather than cryptic.

The second parameter decides what the argument accepts and what type you get back. There are a lot of them, and they have opinions, so they get their own page: [Argument types](./argument-types.md).

### `parent.then(child)`

Attaches a node one level below another. It works on both `Command` and `CommandNode`:

```rust
let uhc = Command::new(&["uhc".to_string()], "Control the UHC minigame");
uhc.then(CommandNode::literal("start"));
uhc.then(CommandNode::literal("status"));
```

> [!WARNING]
> `then()` **consumes** the child node. On the server side the node handle is taken out of the resource table and moved into the parent, so the variable you passed in is spent. You can't attach the same node to two parents, and you can't keep configuring it afterwards. If you need the same branch in two places, build it twice (a small `fn` that returns a fresh `CommandNode` is the usual way, see [Sharing branches](#sharing-branches) below).

### `node.execute(handler)`

Attaches an executor, which is any type implementing `CommandHandler`. It works on `Command` and on `CommandNode`:

```rust
let status = CommandNode::literal("status").execute(StatusExecutor);
```

Every `execute()` call registers its own handler, so a single tree can have as many executors as it has branches. Which one runs depends on where the player's input stopped.

## The one ordering rule

`execute()` and `then()` don't chain the same way, and this is the single most common thing to get stuck on when building a tree:

- `execute()` takes the node **by value** and gives it back, so you can keep using the result.
- `then()` only **borrows**, so you can chain more `then()` calls, but you can't chain an `execute()` onto the end of one.

In practice: **build each branch with `execute()` first, then attach it with `then()`.**

```rust
// Works: execute() first, then hand the finished node to then()
parent.then(CommandNode::literal("start").execute(StartExecutor));

// Doesn't compile: then() gives back a borrow, execute() wants ownership
parent.then(CommandNode::literal("start")).execute(StartExecutor);
```

The same applies to the root. If you want an executor on the bare command *and* children under it, do the children first and reassign the root:

```rust
let mut fly = Command::new(&["fly".to_string()], "Toggle player flight mode");
fly.then(CommandNode::argument("players", &ArgumentType::Players).execute(FlyCommand));
fly = fly.execute(FlyCommand);
```

That `let mut` plus reassignment looks odd the first time you see it, but it's the normal shape and you'll find it in most Pumpkin plugins.

## How the server picks an executor

When a command runs, the server doesn't walk the tree one node at a time. It builds a list of every complete path from the root down to a node that has an executor, then tries those paths in order until one fits the input completely.

A path fits when:

- every literal node on it matched its word exactly,
- every argument node on it successfully consumed its input, and
- there's **nothing left over** once the path is exhausted.

That last point is the one to remember. An executor only runs if the player's input ran out at exactly the same time as the path did. Trailing junk doesn't get ignored, it makes the path fail and the server moves on to the next candidate. If nothing fits, the player gets the usual red syntax error pointing at where things went wrong.

### Optional arguments

There's no "optional" flag on an argument node. Instead you attach the same executor twice, once to the parent and once to the argument node below it:

```rust
let mut home = Command::new(&["home".to_string()], "Teleport to a home");
home.then(
  CommandNode::argument("HOME_NAME", &ArgumentType::String(StringType::SingleWord))
    .execute(HomeCommand),
);
home = home.execute(HomeCommand);
```

Now `/home` matches the short path and `/home base` matches the long one. Both end up in `HomeCommand`, which checks whether the argument is actually there. How to do that check is on the [Command executors](./executors.md) page, and it's less obvious than it looks.

### Sub-commands

Nested literals, as deep as you like:

```rust
let uhc = Command::new(&["uhc".to_string()], "Control the UHC minigame");
uhc.then(CommandNode::literal("start").execute(StartExecutor));
uhc.then(CommandNode::literal("status").execute(StatusExecutor));
```

### Sharing branches

Since `then()` eats the node you give it, a branch you want in several places should come from a function that builds a fresh one each time:

```rust
fn amount_node<H: CommandHandler + 'static>(handler: H) -> CommandNode {
  CommandNode::argument("amount", &ArgumentType::String(StringType::SingleWord))
    .execute(handler)
}

let eco = Command::new(&["eco".to_string()], "Manage balances");
for (verb, action) in [("give", Action::Give), ("take", Action::Take)] {
  let target = CommandNode::argument("player", &ArgumentType::Players);
  target.then(amount_node(EcoCommand(action)));

  let literal = CommandNode::literal(verb);
  literal.then(target);
  eco.then(literal);
}
```

That builds `/eco give <player> <amount>` and `/eco take <player> <amount>` without either branch stepping on the other.

## Arguments are shared along the whole path

Every argument consumed anywhere on the matched path ends up in **one flat map**, keyed by the node name, and that same map is handed to whichever executor runs. An argument consumed near the root is readable from a leaf several levels down.

That's what makes deep trees pleasant to work with. In a tree like this:

```text
/gp user <players> permission set <node> <value>
```

the executor sitting on `<value>` can read `players`, `node` and `value`, even though `players` was consumed four levels earlier.

> [!WARNING]
> Because it's one flat map keyed by name, two argument nodes on the same path with the same name will clobber each other. Keep names unique per path, and consider pulling them out into `const`s, since the same string has to match on both the building side and the reading side.

## What about requirements?

The underlying command system supports *requirements*, predicates attached to a node that decide whether that whole branch is visible and usable. The WIT interface even exposes a `require` hook on command nodes.

> [!WARNING]
> Don't use it. The host's implementation of `require_with_handler_id` returns an error, and an error coming back from a host call **traps your plugin instance** rather than failing gracefully. It can't work as things stand: there's no export in the plugin world for the server to call back into your plugin to evaluate a predicate, and the server-side predicate is synchronous while calling into WASM isn't. The Rust API deliberately offers no wrapper for it, so you'd have to reach for the raw bindings to hit this at all.

Gate access with the permission you pass to `register_command` instead. See [Command permissions](./permissions.md).

## Registering the finished tree

### `context.register_command(command, permission)`

Same call as in the 101 chapter, and it consumes the `Command` the same way `then()` consumes a node:

```rust
context.register_command(command, "MyPlugin:use");
```

Registering also pushes a fresh command graph to every player currently online, so the new command shows up in their tab completion right away without a reconnect.

## Putting it together

A plugin with a small nested tree, an optional argument, and two executors on different branches.

```rust
use pumpkin_plugin_api::{
  register_plugin, Context, Plugin, PluginMetadata, Result, Server,
  command::{Command, CommandError, CommandNode, CommandSender, ConsumedArgs},
  command_wit::{Arg, ArgumentType},
  commands::CommandHandler,
  permission::{Permission, PermissionDefault, PermissionLevel},
  text::TextComponent,
};

const PLAYERS_ARG: &str = "players";

struct HealCommand;

impl CommandHandler for HealCommand {
  fn handle(&self, sender: CommandSender, _server: Server, args: ConsumedArgs) -> Result<i32, CommandError> {
    // `/heal <players>` took this branch, so the argument is there
    if let Arg::Players(targets) = args.get_value(PLAYERS_ARG) {
      for target in targets {
        target.set_health(20.0);
      }
      return Ok(1);
    }

    // `/heal` on its own, heal whoever ran it
    let Some(player) = sender.as_player() else {
      sender.send_message(TextComponent::text("Only a player can heal themselves."));
      return Ok(1);
    };

    player.set_health(20.0);
    Ok(1)
  }
}

struct HealAllCommand;

impl CommandHandler for HealAllCommand {
  fn handle(&self, _sender: CommandSender, server: Server, _args: ConsumedArgs) -> Result<i32, CommandError> {
    for player in server.get_all_players() {
      player.set_health(20.0);
    }
    Ok(1)
  }
}

struct HealPlugin;

impl Plugin for HealPlugin {
  fn new() -> Self { HealPlugin }

  fn metadata(&self) -> PluginMetadata {
    PluginMetadata {
      name: "HealPlugin".into(),
      version: "0.1.0".into(),
      authors: vec!["vyPal".into()],
      description: "Adds /heal".into(),
      dependencies: vec![],
      permissions: vec![],
    }
  }

  fn on_load(&mut self, context: Context) -> Result<()> {
    context.register_permission(&Permission {
      node: "HealPlugin:heal".into(),
      description: "Allows running /heal".into(),
      default: PermissionDefault::Op(PermissionLevel::Two),
      children: vec![],
    })?;

    let mut heal = Command::new(&["heal".to_string()], "Restore health");

    // /heal all
    heal.then(CommandNode::literal("all").execute(HealAllCommand));

    // /heal <players>
    heal.then(
      CommandNode::argument(PLAYERS_ARG, &ArgumentType::Players).execute(HealCommand),
    );

    // /heal, on its own. Reassign, since execute() takes the command by value
    heal = heal.execute(HealCommand);

    context.register_command(heal, "HealPlugin:heal");

    Ok(())
  }
}

register_plugin!(HealPlugin);
```

Three paths, two executors, one permission node covering all of it.

Next up: [Argument types](./argument-types.md), which is where most of the surprises live.

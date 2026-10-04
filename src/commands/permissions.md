# Command permissions

Every command a plugin registers is gated behind exactly one permission node, given at registration time. That's the whole access control story for commands: there's no per-branch gating, no requirement predicates (see [why](./command-tree.md#what-about-requirements)), just one string per command.

The system behind that string is more interesting, and it has a couple of behaviors that will confuse you if you're coming from Bukkit.

> [!NOTE]
> These are **not** the same thing as the `permissions` field in your `PluginMetadata`. Those control what your plugin is allowed to do on the host system (file access, networking), and they're covered in [Plugin permissions](../plugin-101/plugin-permissions.md). The nodes on this page control what *players* are allowed to do. The two systems share a word and nothing else.

## Attaching a permission to a command

### `context.register_command(command, permission)` { data-since=0.1 }

```rust
context.register_command(command, "MyPlugin:warp");
```

The string is a permission node. Two things happen to it:

- If it **contains a colon**, it's used exactly as given. No validation at all. You can point your command at `minecraft:command.gamemode`, or at a node belonging to a completely different plugin, and the server won't object.
- If it **doesn't contain a colon**, your plugin's name is prefixed automatically. So `register_command(cmd, "warp")` from a plugin named `MyPlugin` gates the command behind `MyPlugin:warp`, the same node the explicit version above produces.

The check runs **once, before any parsing**, against the name the player actually typed. Aliases each get their own copy of the same node, so `/bal` is gated identically to `/balance`.

> [!WARNING]
> Attaching a node to a command does **not** create it. If you never call `register_permission` for it, the node doesn't exist, and the consequences of that are covered in [Unregistered nodes](#unregistered-nodes) below. They're weirder than "nobody can run it".

## Defining a node

### `context.register_permission(permission)` { data-since=0.1 }

```rust
use pumpkin_plugin_api::permission::{Permission, PermissionDefault, PermissionLevel};

context.register_permission(&Permission {
  node: "MyPlugin:warp".into(),
  description: "Allows teleporting to warp points".into(),
  default: PermissionDefault::Op(PermissionLevel::Zero),
  children: vec![],
})?;
```

Unlike `register_command`, this one is strict about namespacing. The part before the colon must **exactly** match the `name` field from your [`PluginMetadata`](../plugin-101/plugin-logic.md#metadata---plugin_metadata). Character for character, case sensitive, no trimming. Get it wrong and registration fails with:

```text
Permission MyPlugin:warp must use the plugin's namespace (myplugin)
```

Registering the same node twice also fails, with `Permission <node> is already registered`. Since `register_permission` returns a `Result`, both of these will propagate out of your `on_load` and stop the plugin loading, which is generally what you want.

### `default` { data-since=0.1 }

Decides who has the node when nothing else says otherwise:

- `PermissionDefault::Allow` gives it to everyone.
- `PermissionDefault::Deny` gives it to nobody until it's explicitly granted.
- `PermissionDefault::Op(level)` gives it to operators at or above the given level.

`PermissionLevel` runs `Zero` through `Four`, matching the vanilla op levels:

| Level | Vanilla meaning |
|---|---|
| `Zero` | normal player |
| `One` | can bypass spawn protection |
| `Two` | can use command blocks, and most gameplay commands |
| `Three` | multiplayer management commands |
| `Four` | full server management |

A plain player is level zero, so `Op(PermissionLevel::Zero)` is a slightly roundabout way of saying "everyone", and reads as "no op level required" rather than as a real restriction. If you mean everyone, `Allow` says it more clearly.

Note that a player's op level is stored in `ops.json` and survives restarts, unlike the nodes themselves.

### `children` { data-since=0.1 }

A list of other nodes that this node implies, each with a `bool`. The entries are `PermissionChild` values, from the same `permission` module as everything else here:

```rust
use pumpkin_plugin_api::permission::PermissionChild;

context.register_permission(&Permission {
  node: "MyPlugin:admin".into(),
  description: "Full access to MyPlugin".into(),
  default: PermissionDefault::Op(PermissionLevel::Four),
  children: vec![
    PermissionChild { node: "MyPlugin:warp".into(), value: true },
    PermissionChild { node: "MyPlugin:setwarp".into(), value: true },
  ],
})?;
```

Read the section on [how a check resolves](#how-a-check-actually-resolves) before leaning on these, because they only apply in a narrower set of circumstances than you'd expect.

## Who gets checked, and how

Not every sender goes through the same path.

- **Console and RCON always pass.** Unconditionally, before any node lookup happens. They're treated as permission level four and every check returns true, whether or not the node exists.
- **Command blocks and dummy senders** are treated as level two, and only ever consult the node's registered default. Explicit grants and wildcards don't apply to them.
- **Players** go through the full resolution below.

### How a check actually resolves

For a player, the server works through these in order and **returns on the first thing that matches**:

1. **An exact node set on the player.** If the player has the node explicitly granted or denied, that answer wins immediately, before anything else is consulted. This works even for a node that was never registered.

2. **Wildcards**, but only for nodes containing exactly one colon. For `myplugin:warp.create` the server checks, in order:
   - `myplugin:*`
   - `myplugin:warp`, then `myplugin:warp.*`
   - `myplugin:warp.create`

   So `myplugin:*` works and covers the whole namespace, and setting it to `false` denies the whole namespace just as effectively.

   > [!WARNING]
   > A bare `*` is never checked, so there's no "grant everything" node. Neither is a trailing wildcard on the complete node, so `myplugin:warp.create.*` does nothing. The `.*` form only means something on intermediate segments.

3. **Children**, and this is the one that catches people out. The server walks the nodes the player has **explicitly set**, looks each one up in the registry, and checks whether the queried node appears in its `children` map. Three limits worth internalising:
   - It's **one level deep only**. A child of a child is never followed.
   - Only nodes the player has *explicitly set* count. Nodes the player merely holds through a `PermissionDefault` don't pass their children on.
   - It returns on the first parent it finds, even when the answer is `false`, so a `false` here hard-denies rather than falling through to the default. And since it iterates a hash map, two parents both listing the same child means the winner is not deterministic.

4. **The node's registered `PermissionDefault`.** If the node isn't in the registry at all, the answer is `false`.

### Unregistered nodes

Step four is where the surprise lives. A node that was never registered denies every player, including a level four operator, and denies command blocks. But console and RCON never got that far, because they passed at the very first step.

> [!WARNING]
> If you forget `register_permission`, your command doesn't look broken. It looks **console-only**. It works perfectly when you test it from the server terminal and silently refuses for every single player, operator or not, with no error in the log explaining why. If a command of yours behaves like that, this is almost certainly the reason.

## Checking permissions yourself

Since a command carries only one node, finer-grained gating is something you do inside your executor.

On the sender:

```rust
if sender.has_permission(&server, "MyPlugin:warp.others") {
  // ...
}
```

On a `Player` directly, which doesn't need the server handle:

- `has_permission(node)` runs the full resolution above.
- `has_permission_set(node)` returns `Option<bool>`, telling you whether the node is *explicitly* set on that player and to what, rather than what the check resolves to.
- `set_permission(node, value)` grants or denies a node.
- `unset_permission(node)` removes an explicit setting, falling back to the default.
- `get_permission_level()` and `set_permission_level(level)` read and write the op level.

`set_permission` accepts any string, including nodes that were never registered and wildcards like `myplugin:*`.

> [!WARNING]
> Explicit permissions are held **in memory only**. Nothing writes them to disk, nothing reloads them at login, and they're gone when the server restarts. There is no `permissions.json`, no group system and no built-in inheritance beyond the one level of `children` described above.
>
> So a plugin that hands out permissions has to store and reapply them itself, typically by saving to its own data folder and calling `set_permission` again on `PlayerJoinEvent`. That's exactly what a dedicated permissions plugin does, and it's a large part of why one is worth having.

Op levels, on the other hand, do persist, since those live in `ops.json`.

### Overriding checks entirely

`PlayerPermissionCheckEvent` fires on every permission check for a player and carries the result as a mutable field. A blocking handler can rewrite it, which is the hook a permissions plugin uses to replace the built-in resolution wholesale. See [Event handlers](../plugin-101/event-handlers.md).

## What players see

The permission check isn't only about running the command. The same check gates:

- **The command graph** sent to each player, so a player without the node doesn't see your command in tab completion at all. It appears the moment they gain it, since registering or unregistering a command reloads the graph for everyone.
- **Server-side suggestions**, which return nothing for a player who fails the check.

A player who fails the check and types the command anyway gets the standard red message: *"I'm sorry, but you do not have permission to perform this command..."*.

## Putting it together

A plugin with a public command and an admin command, showing both default styles and an in-executor check for a privileged branch.

```rust
use pumpkin_plugin_api::{
  register_plugin, Context, Plugin, PluginMetadata, Result, Server,
  command::{Command, CommandError, CommandNode, CommandSender, ConsumedArgs},
  command_wit::{Arg, ArgumentType},
  commands::CommandHandler,
  common::NamedColor,
  permission::{Permission, PermissionDefault, PermissionLevel},
  text::TextComponent,
};

const TARGET: &str = "target";

const USE_NODE: &str = "WarpPlugin:warp";
const OTHERS_NODE: &str = "WarpPlugin:warp.others";

struct WarpCommand;

impl CommandHandler for WarpCommand {
  fn handle(&self, sender: CommandSender, server: Server, args: ConsumedArgs) -> Result<i32, CommandError> {
    // The command's own node got us this far. Warping someone else needs more,
    // and a per-branch check is the only way to express that
    if let Arg::Players(targets) = args.get_value(TARGET) {
      if !sender.has_permission(&server, OTHERS_NODE) {
        let text = TextComponent::text("You can only warp yourself.")
          .color_named(NamedColor::Red);
        sender.send_message(text);
        return Ok(1);
      }

      for target in targets {
        tracing::info!("Warping {}", target.get_name());
      }
      return Ok(1);
    }

    let Some(player) = sender.as_player() else {
      sender.send_message(TextComponent::text("Only a player can warp themselves."));
      return Ok(1);
    };

    tracing::info!("Warping {}", player.get_name());
    Ok(1)
  }
}

struct WarpPlugin;

impl Plugin for WarpPlugin {
  fn new() -> Self { WarpPlugin }

  fn metadata(&self) -> PluginMetadata {
    PluginMetadata {
      // The namespace of every node below has to match this exactly
      name: "WarpPlugin".into(),
      version: "0.1.0".into(),
      authors: vec!["vyPal".into()],
      description: "Warp points".into(),
      dependencies: vec![],
      permissions: vec![],
    }
  }

  fn on_load(&self, context: Context) -> Result<()> {
    // Everyone can warp themselves
    context.register_permission(&Permission {
      node: USE_NODE.into(),
      description: "Allows using /warp".into(),
      default: PermissionDefault::Allow,
      children: vec![],
    })?;

    // Warping other people is for moderators
    context.register_permission(&Permission {
      node: OTHERS_NODE.into(),
      description: "Allows warping other players".into(),
      default: PermissionDefault::Op(PermissionLevel::Two),
      children: vec![],
    })?;

    let warp = Command::new(&["warp".to_string()], "Teleport to a warp point")
      .then(CommandNode::argument(TARGET, &ArgumentType::Players).execute(WarpCommand))
      .execute(WarpCommand);

    context.register_command(warp, USE_NODE);

    Ok(())
  }
}

register_plugin!(WarpPlugin);
```

Both nodes are registered before the command that depends on them, which is the habit worth building. A missing `register_permission` is the single easiest way to end up with a command that only works from the console.

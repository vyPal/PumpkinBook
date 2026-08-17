# Argument types

Every argument node in a [command tree](./command-tree.md) is created with an `ArgumentType`, which decides three separate things:

1. **What the player is allowed to type** there, and how much of the input the argument eats.
2. **What your executor gets back** when it reads that argument.
3. **What the client does** with it, since the argument type is also sent to the player's game in the command graph. That's what drives tab completion and the red/green highlighting as they type.

Those three don't always line up as neatly as you'd hope, which is most of what this page is about.

## How input gets split up

Before any argument is parsed, the server splits the whole command line into tokens. That split happens once, up front, and it does understand structure: `"double quotes"`, `'single quotes'`, `{curly braces}` and `[square brackets]` all keep their contents together, and a `\` escapes the next character. Unbalanced quotes or brackets fail the command outright.

What it does **not** do is strip anything. If the player types `"hello world"`, the token your argument receives still has the quote characters on it. Keep that in mind when you read a string argument back.

Argument nodes then take tokens off the front, left to right. Most take exactly one. A few (positions, rotations) take two or three. One (`String(Greedy)`) takes everything that's left.

## Declaring an argument

```rust
use pumpkin_plugin_api::{command::CommandNode, command_wit::{ArgumentType, StringType}};

let node = CommandNode::argument("amount", &ArgumentType::Integer((Some(1), Some(64))));
```

The type is passed by reference, and the variants that take configuration take it inline, as you can see with the bounds above.

## The types that work

| `ArgumentType` | Player types | Configuration | You get back |
|---|---|---|---|
| `Bool` | `true` or `false`, nothing else | none | `Arg::Bool(bool)` |
| `Integer((min, max))` | a whole number | inclusive bounds, each optional | `Arg::Num(Ok(Number::Int32))` |
| `Long((min, max))` | a whole number | inclusive bounds, each optional | `Arg::Num(Ok(Number::Int64))` |
| `Float((min, max))` | a decimal number | inclusive bounds, each optional | `Arg::Num(Ok(Number::Float32))` |
| `Double((min, max))` | a decimal number | inclusive bounds, each optional | `Arg::Num(Ok(Number::Float64))` |
| `String(StringType::SingleWord)` | one token | none | `Arg::Simple(String)` |
| `String(StringType::Quotable)` | one token | none | `Arg::Simple(String)` |
| `String(StringType::Greedy)` | the entire rest of the line | none | `Arg::Msg(String)` |
| `Players` | a player name or a target selector | none | `Arg::Players(Vec<Player>)` |
| `GameProfile` | a player name or a target selector | none | `Arg::Players(Vec<Player>)` |
| `Entities` | a target selector | none | `Arg::Simple("")`, see below |
| `Entity` | a target selector matching one entity | none | `Arg::Simple("")`, see below |
| `BlockPos` | three whole numbers, `~` and `^` allowed | none | `Arg::BlockPos(BlockPos)` |
| `Position3d` | three numbers, `~` and `^` allowed | none | `Arg::Pos3d((f64, f64, f64))` |
| `Position2d` | two numbers (x and z) | none | `Arg::Pos2d((f64, f64))` |
| `Rotation` | two numbers (yaw and pitch), `~` allowed | none | `Arg::Rotation((f32, bool, f32, bool))` |
| `BlockState` | a block id | none | `Arg::Block(String)` |
| `BlockPredicate` | a block id or `#tag` | none | `Arg::BlockPredicate(String)` |
| `Item` | an item id | none | `Arg::Item(String)` |
| `ItemPredicate` | an item id or `#tag` | none | `Arg::Item(String)` |
| `ResourceLocation` | a `namespace:path` id | none | `Arg::ResourceLocation(String)` |
| `Resource(namespace)` | a `namespace:path` id | a namespace string, ignored | `Arg::ResourceLocation(String)` |
| `Component` | a JSON text component, or a quoted string | none | `Arg::TextComponent(TextComponent)` |
| `Gamemode` | `survival`, `creative`, `adventure`, `spectator`, or `0` to `3` | none | `Arg::Gamemode(GameMode)` |
| `Difficulty` | `peaceful`, `easy`, `normal`, `hard` | none | `Arg::Difficulty(Difficulty)` |
| `EntityAnchor` | `feet` or `eyes` | none | `Arg::EntityAnchor(EntityAnchor)` |
| `Time(min)` | a duration like `30`, `10s`, `2d` | optional minimum, in ticks | `Arg::Time(i32)`, in ticks |

Reading those values out of `ConsumedArgs` is covered on the [Command executors](./executors.md) page.

## The types that don't

The `ArgumentType` enum lists a lot more than the table above. Most of the rest aren't wired up on the server side yet.

> [!WARNING]
> Using an unwired argument type isn't a soft failure. The server returns an error to your plugin from inside `CommandNode::argument`, and an error coming back from a host call **traps your plugin instance**. You don't get a `Result` to handle, your plugin dies while it's still loading, and the log line to look for is `Unimplemented argument type: ...`.

As of writing, these all trap:

`ColumnPos`, `Color`, `Style`, `Message`, `NbtCompoundTag`, `NbtTag`, `NbtPath`, `Objective`, `ObjectiveCriteria`, `Operation`, `Particle`, `Angle`, `ScoreboardSlot`, `ScoreHolder`, `Swizzle`, `Team`, `ItemSlot`, `MobEffect`, `Function`, `IntRange`, `FloatRange`, `Dimension`, `ResourceOrTag`, `ResourceOrTagKey`, `ResourceKey`, `TemplateMirror`, `TemplateRotation`, `Uuid`.

Some of these are only missing the bridge, not the implementation. `Message`, `Particle`, `MobEffect` and `ItemSlot` all have perfectly functional parsers on the server that plugins simply can't reach yet. So it's worth rechecking this list against a newer Pumpkin rather than assuming it's permanent, and worth opening an issue if one of them is blocking you.

Until then, the general workaround is `String(SingleWord)` plus your own parsing. You lose client-side completion and validation, but you get the raw text and can do whatever you want with it.

## Notes on individual types

### Numbers are always a `Result`

`Arg::Num` doesn't hand you a number, it hands you a `Result<Number, NotInBounds>`, and `Number` is itself an enum over the four numeric widths. So reading an integer argument is a double unwrap:

```rust
let Arg::Num(Ok(Number::Int32(amount))) = args.get_value("amount") else {
  sender.send_message(TextComponent::text("Give me a whole number."));
  return Ok(1);
};
```

The reason for the inner `Result` is that **bounds don't reject input**. If you declared `Integer((Some(1), Some(64)))` and the player types `500`, parsing still succeeds, and you get `Err(NotInBounds::UpperBound((limit, value)))` instead of the number. That's your cue to tell them off, and it's easy to forget, because the `Ok` path looks like it covers everything.

Bounds are inclusive on both ends, and each side is independently optional. `(None, None)` is a perfectly good unbounded number.

If you don't care which width you got, match `Number` broadly:

```rust
let speed = match speed {
  Number::Float32(f) => f,
  Number::Float64(f) => f as f32,
  Number::Int32(n) => n as f32,
  Number::Int64(n) => n as f32,
};
```

### `Quotable` strings aren't quotable yet

`StringType` has three modes, but only two distinct behaviors right now. `SingleWord` and `Quotable` are both wired to the same server-side parser, so `Quotable` gives you a single raw token with any quote characters still attached, exactly like `SingleWord` would.

`Greedy` is genuinely different: it swallows every remaining token, joined with single spaces, and gives you `Arg::Msg`. Since it consumes the rest of the line, a greedy argument can only ever be the last node on its branch. Anything you attach below it is unreachable.

### `Entities` and `Entity` are not usable

Both parse correctly on the server, and both will happily accept `@e[type=zombie]`. But entities have no representation in the plugin interface yet, so by the time the value reaches your executor it has been flattened to an empty `Arg::Simple("")`. There's nothing you can do with that.

If you need players, use `Players`, which works properly. If you need arbitrary entities, that's not currently reachable through a command argument.

### `GameProfile` gives you players

It's wired to the same parser as `Players`, so despite the name you get `Arg::Players`, and only players who are currently online. There's no way to resolve an offline player's profile through a command argument.

### `ItemPredicate` gives you `Arg::Item`

The predicate parser accepts `#tag` syntax and produces the same `Arg::Item(String)` variant a plain item argument does. There is an `Arg::ItemPredicate` variant in the interface, but nothing currently produces it. Match on `Arg::Item` for both.

### `Resource` ignores its namespace

`ArgumentType::Resource("minecraft:mob_effect".to_string())` looks like it should restrict input to effect ids and offer them in tab completion. It doesn't. The namespace string is discarded and the argument behaves as a plain `ResourceLocation`, so you're validating the string yourself either way.

### Ids aren't validated

`BlockState`, `BlockPredicate`, `Item`, `ResourceLocation` and `Resource` all hand you the raw token without checking that it names anything real. `/give @s notarealitem` will reach your executor with `Arg::Item("notarealitem")` quite happily. Validate before you use it.

### Positions and rotations

`BlockPos` and `Position3d` both accept the three vanilla coordinate styles: absolute (`100 64 -20`), relative to the sender (`~ ~5 ~`), and local to the sender's facing (`^ ^ ^3`). They're resolved against the sender before you see them, so you get plain numbers.

`Rotation` gives you a four-element tuple rather than two numbers: `(yaw, yaw_is_relative, pitch, pitch_is_relative)`. The booleans tell you whether the player used `~`, which matters if you want to apply the value as an offset rather than an absolute.

### `Time`

Accepts a bare number of ticks, or a number with a unit suffix: `t` for ticks, `s` for seconds (20 ticks), `d` for in-game days (24000 ticks). You always get ticks back as an `i32`, rounded. The optional configuration value is a minimum, also in ticks, and input below it is rejected before it reaches you. `Time(Some(0))` is a good way to say "no negative durations".

## What the client sees

The argument type is also part of the command graph the server sends to each connected player, so it decides the client-side experience: whether the input turns red as they type, what tab completion offers, and whether the client can resolve a selector locally.

This is why using `String(SingleWord)` as a stand-in for a missing type costs you something real. It works, but the player gets no completion and no feedback until they press enter and your executor rejects it. Worth a friendly error message to make up for it.

## Putting it together

A `/warp` command with a name, an optional destination, and a bounded number, showing how each value comes back.

```rust
use pumpkin_plugin_api::{
  command::{Command, CommandError, CommandNode, CommandSender, ConsumedArgs},
  command_wit::{Arg, ArgumentType, Number, StringType},
  commands::CommandHandler,
  text::TextComponent,
  Context, Result, Server,
};

const NAME: &str = "name";
const POS: &str = "position";
const DELAY: &str = "delay";

struct SetWarpCommand;

impl CommandHandler for SetWarpCommand {
  fn handle(&self, sender: CommandSender, _server: Server, args: ConsumedArgs) -> Result<i32, CommandError> {
    // A string argument always matches Arg::Simple, even when it wasn't
    // supplied, so the value has to be checked as well
    let name = match args.get_value(NAME) {
      Arg::Simple(name) if !name.is_empty() => name,
      _ => {
        sender.send_message(TextComponent::text("A warp needs a name."));
        return Ok(1);
      }
    };

    // Position3d resolves ~ and ^ against the sender for you
    let Arg::Pos3d((x, y, z)) = args.get_value(POS) else {
      sender.send_message(TextComponent::text("Give me a position."));
      return Ok(1);
    };

    // Bounds don't reject input, they come back as an Err
    let delay = match args.get_value(DELAY) {
      Arg::Num(Ok(Number::Int32(ticks))) => ticks,
      Arg::Num(Err(_)) => {
        sender.send_message(TextComponent::text("Delay has to be between 0 and 200 ticks."));
        return Ok(1);
      }
      // Not supplied at all, since this branch is optional
      _ => 0,
    };

    tracing::info!("Warp {name} at {x} {y} {z}, delay {delay}");
    Ok(1)
  }
}

pub fn register(context: &Context) -> Result<()> {
  let setwarp = Command::new(&["setwarp".to_string()], "Create a warp point");

  let name = CommandNode::argument(NAME, &ArgumentType::String(StringType::SingleWord));
  let position = CommandNode::argument(POS, &ArgumentType::Position3d).execute(SetWarpCommand);

  position.then(
    CommandNode::argument(DELAY, &ArgumentType::Integer((Some(0), Some(200))))
      .execute(SetWarpCommand),
  );

  name.then(position);
  setwarp.then(name);

  context.register_command(setwarp, "MyPlugin:setwarp");
  Ok(())
}
```

That gives you `/setwarp <name> <x> <y> <z>` and `/setwarp <name> <x> <y> <z> <delay>`, both landing in the same executor.

# Text components

You've already been using `TextComponent` throughout this book, in command error messages, chat messages, and titles, without it ever getting its own explanation. It's Pumpkin's rich text type: the thing that lets a string carry color, bold/italic formatting, a click action, a hover tooltip, all at once, and it's what every player-facing message ultimately gets built out of, whether that's a chat line, a boss bar title, a GUI slot name, or a form label.

A `TextComponent` is a resource, not a plain struct, so the component itself lives on the host side and your plugin only holds a handle to it. In Rust, every call that changes the component (styling, `add_text`, `add_child`, click and hover actions) takes the handle **by value and gives it back**, so you chain the calls and keep the result:

```rust
use pumpkin_plugin_api::{common::NamedColor, text::TextComponent};

let text = TextComponent::text("Hello there!")
  .color_named(NamedColor::Gold)
  .bold(true);
```

> [!WARNING]
> Calling one of these as a standalone statement, `text.color_named(NamedColor::Gold);`, moves `text` into the call and throws the returned handle away, so the next line that uses `text` fails with `use of moved value`. Either chain the calls, or rebind with `let text = text.color_named(...)`. Methods that only read the component (`get_text`, `to_json`, `encode`, `to_pretty_console`) borrow it and don't have this problem.

## Creating text

### `TextComponent::text(plain)` { data-since=0.1 }

The basic constructor. Wraps a plain string with no formatting.

### `TextComponent::translate(key, with)` { data-since=0.1 }

Builds a component from a translation key instead of literal text, the client resolves `key` against its own language file (or one your plugin registered, see the [Localization](./localization.md) chapter) and substitutes the `TextComponent`s in `with` into the key's placeholders, in order. Useful when you want a message that's already localized in the client's own language rather than hardcoding English.

### `TextComponent::translate_cross(java_key, bedrock_key, with)` { data-since=0.1 }

Same idea, but with separate translation keys for Java and Bedrock clients, since the two editions' language files don't always share key names. The host picks whichever key matches the receiving client's platform.

### `TextComponent::entity_names(selector, separator)` { data-since=0.1 }

Builds a component that resolves a target selector (e.g. `"@a"`, `"@e[type=zombie]"`) client-side into the matched entities' names, joined by `separator` (defaults to a comma if `None`). The same mechanic vanilla uses for `@s`-style output in scoreboard/team text.

### `TextComponent::keybind(keybind)` { data-since=0.1 }

Builds a component showing the client's currently bound key for a keybind identifier (e.g. `"key.jump"`), rendered as whatever key that player has it bound to, not a hardcoded key name.

### `TextComponent::custom(namespace, key, locale, with)` { data-since=0.1 }

A lower-level translation constructor for a custom-registered translation, see [Localization](./localization.md) for how a plugin registers its own translation keys.

### `TextComponent::from_legacy_string(input)` / `TextComponent::from_legacy_string_with_code(input, code_symbol)` { data-since=0.1 }

Parses an old-style formatted string (section-sign color codes, `"§cHello"`) into a `TextComponent`. The `_with_code` variant lets you use a different marker character than `§`, `'&'` is the common choice for strings coming from a config file, since `§` isn't easy to type.

### `TextComponent::from_json(json)` / `.to_json()` { data-since=0.1 }

Parses a standard Minecraft JSON text component string into a `TextComponent` (`from_json` returns a `Result<TextComponent, String>`), or serializes one back out to that same JSON format. Useful for round-tripping through config files or interop with tools that already speak vanilla's text JSON.

## Composing text

### `.add_text(text)` { data-since=0.1 }

Appends plain text directly onto the component, inheriting its style.

### `.add_child(child)` { data-since=0.1 }

Appends another `TextComponent` as a child, keeping the child's own styling. This is how you build a message with mixed formatting, a plain sentence with one colored word in the middle, for example.

> [!WARNING]
> `add_child` **consumes** the child component. On the server side its handle is taken out of the resource table and moved into the parent, so the variable you passed in is spent, you can't add the same component to two parents, and you can't keep styling it afterward. Build a fresh component for each place you want to use it.

```rust
use pumpkin_plugin_api::{common::NamedColor, text::TextComponent};

let name = TextComponent::text("Steve").color_named(NamedColor::Gold);

let greeting = TextComponent::text("Welcome, ")
  .add_child(name) // `name` is spent from here on
  .add_text("!");
```

### `.get_text()` { data-since=0.1 }

Reads back the plain-text content of the component (no styling, no children's text). Mostly useful for logging or debugging, not for anything player-facing.

### `.encode()` { data-since=0.1 }

Serializes the component to the raw byte format the server uses internally to send it over the network. Plugin authors building normal messages never need this, it exists for the rare case of assembling a packet by hand, see [Raw packets](../advanced/raw-packets.md).

### `.to_pretty_console()` { data-since=0.1 }

Renders the component (styling included, as ANSI escape codes) for printing to a terminal, useful if you're logging a `TextComponent` and want the colors to actually show up in the console rather than being silently dropped.

## Styling

Each of these sets one property on the component and hands the component back, so they chain (see the note at the top of this page).

### `.color_named(color)` / `.color_rgb(color)` { data-since=0.1 }

Sets the text color, either to one of the 16 named Minecraft colors (`NamedColor::Gold`, `NamedColor::DarkRed`, and so on) or to an exact `RgbColor { r, g, b }`. Setting one overwrites whichever color was set before, including by the other method, there's no way to have both.

### `.gradient_named(colors)` / `.gradient(colors)` / `.rainbow()` { data-since=0.1 }

Applies a per-character color gradient across the component's text instead of one flat color, `gradient_named` takes a list of `NamedColor`, `gradient` a list of exact `RgbColor`, `rainbow()` is a shortcut for the classic rainbow gradient. Like the plain color setters, these overwrite whatever color/gradient was set before.

```rust
use pumpkin_plugin_api::common::RgbColor;

let title = TextComponent::text("EPIC LOOT").gradient(&[
  RgbColor { r: 255, g: 0, b: 128 },
  RgbColor { r: 128, g: 0, b: 255 },
]);
```

### `.bold(value)` / `.italic(value)` / `.underlined(value)` / `.strikethrough(value)` / `.obfuscated(value)` { data-since=0.1 }

Standard text formatting toggles, all take a `bool`. `obfuscated` is the "magic"/scrambled-text effect (the same one enchantment tables use).

### `.insertion(text)` { data-since=0.1 }

Text that gets inserted into the player's chat input box when they shift-click the component. Doesn't run or send anything by itself, it just populates their chat box for them to send (or edit) manually.

### `.font(font)` { data-since=0.1 }

Sets a custom font resource location (e.g. `"minecraft:alt"`), for resource packs that ship alternate fonts.

### `.shadow_color(color)` { data-since=0.1 }

Sets the text's shadow color as an `ArgbColor { a, r, g, b }`. This is a newer Minecraft rendering feature, most components can leave it unset and get the default shadow.

## Click actions

### `.click_open_url(url)` { data-since=0.1 }

Opens `url` in the player's default browser when clicked (subject to their client-side "open link" confirmation prompt).

### `.click_run_command(command)` { data-since=0.1 }

Runs `command` as if the player typed and sent it themselves, including the leading `/`.

### `.click_suggest_command(command)` { data-since=0.1 }

Populates the player's chat box with `command`, same as `insertion`, but triggered by a click instead of shift-click.

### `.click_open_file(path)` { data-since=0.1 }

Opens a local file path in the player's client-side file handler when clicked. Client-side only, has no effect related to anything on the server's filesystem.

### `.click_change_page(page)` { data-since=0.1 }

For a component shown inside a written book, flips the book to `page` when clicked. Has no effect outside a book UI.

### `.click_copy_to_clipboard(text)` { data-since=0.1 }

Copies `text` to the player's clipboard when clicked.

> [!NOTE]
> There's only one click action slot per component. Calling a second `click_*` method overwrites the first, it doesn't stack them. If you need different parts of a message to do different things on click, split it across multiple `add_child` components, one per click action.

## Hover actions

### `.hover_show_text(text)` { data-since=0.1 }

Shows `text` (another `TextComponent`) as a tooltip when the player hovers over this component. Like `add_child`, this **consumes** the `text` argument, its handle is moved into the parent's style.

### `.hover_show_item(item)` { data-since=0.1 }

Shows an item tooltip, in the same style as hovering over an item in an inventory. `item` isn't an `ItemStack` resource here, it's a raw SNBT string describing the item (e.g. `"minecraft:diamond_sword{Enchantments:[...]}"`), so you're responsible for formatting it yourself.

### `.hover_show_entity(entity_type, id, name)` { data-since=0.1 }

Shows an entity tooltip. `entity_type` is a resource location string (`"minecraft:zombie"`), `id` is the entity's UUID as a string, and `name` is an optional `TextComponent` for a custom display name in the tooltip, if given, it's consumed the same way `hover_show_text`'s argument is.

> [!NOTE]
> Only one hover action slot exists per component, same as click actions: the last `hover_*` call wins.

## Putting it together

A warp confirmation message: plain text, a colored and clickable warp name that shows a preview on hover, and a shift-clickable "run it again" hint.

```rust
use pumpkin_plugin_api::{common::NamedColor, text::TextComponent};

fn warp_confirmation(warp_name: &str) -> TextComponent {
  let preview = TextComponent::text(&format!("Teleport to '{warp_name}'"));

  let name = TextComponent::text(warp_name)
    .color_named(NamedColor::Aqua)
    .bold(true)
    .click_run_command(&format!("/warp {warp_name}"))
    .hover_show_text(preview)
    .insertion(&format!("/warp {warp_name}"));

  TextComponent::text("Warped to ")
    .add_child(name)
    .add_text(".")
}
```

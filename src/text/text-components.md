# Text components

You've already been using `TextComponent` throughout this book, in command error messages, chat messages, and titles, without it ever getting its own explanation. It's Pumpkin's rich text type: the thing that lets a string carry color, bold/italic formatting, a click action, a hover tooltip, all at once, and it's what every player-facing message ultimately gets built out of, whether that's a chat line, a boss bar title, a GUI slot name, or a form label.

A `TextComponent` is a resource, not a plain struct. Every styling call below mutates it in place on the host side, there's no builder pattern here, no chaining, just a sequence of calls against the same handle.

```rust
use pumpkin_plugin_api::text::TextComponent;

let text = TextComponent::text("Hello there!");
```

## Creating text

### `TextComponent::text(plain)`

The basic constructor. Wraps a plain string with no formatting.

### `TextComponent::translate(key, with)`

Builds a component from a translation key instead of literal text, the client resolves `key` against its own language file (or one your plugin registered, see the [Localization](./localization.md) chapter) and substitutes the `TextComponent`s in `with` into the key's placeholders, in order. Useful when you want a message that's already localized in the client's own language rather than hardcoding English.

## Composing text

### `.add_text(text)`

Appends plain text directly onto the component, inheriting its style.

### `.add_child(child)`

Appends another `TextComponent` as a child, keeping the child's own styling. This is how you build a message with mixed formatting, a plain sentence with one colored word in the middle, for example.

> [!WARNING]
> `add_child` **consumes** the child component. On the server side its handle is taken out of the resource table and moved into the parent, so the variable you passed in is spent, you can't add the same component to two parents, and you can't keep styling it afterward. Build a fresh component for each place you want to use it.

```rust
use pumpkin_plugin_api::{common::NamedColor, text::TextComponent};

let name = TextComponent::text("Steve");
name.color_named(NamedColor::Gold);

let greeting = TextComponent::text("Welcome, ");
greeting.add_child(name); // `name` is spent from here on
greeting.add_text("!");
```

### `.get_text()`

Reads back the plain-text content of the component (no styling, no children's text). Mostly useful for logging or debugging, not for anything player-facing.

### `.encode()`

Serializes the component to the raw byte format the server uses internally to send it over the network. Plugin authors building normal messages never need this, it exists for the rare case of assembling a packet by hand, see [Raw packets](../advanced/raw-packets.md).

## Styling

Each of these sets one property on the component and returns nothing, call them as separate statements on the same `let` binding.

### `.color_named(color)` / `.color_rgb(color)`

Sets the text color, either to one of the 16 named Minecraft colors (`NamedColor::Gold`, `NamedColor::DarkRed`, and so on) or to an exact `RgbColor { r, g, b }`. Setting one overwrites whichever color was set before, including by the other method, there's no way to have both.

### `.bold(value)` / `.italic(value)` / `.underlined(value)` / `.strikethrough(value)` / `.obfuscated(value)`

Standard text formatting toggles, all take a `bool`. `obfuscated` is the "magic"/scrambled-text effect (the same one enchantment tables use).

### `.insertion(text)`

Text that gets inserted into the player's chat input box when they shift-click the component. Doesn't run or send anything by itself, it just populates their chat box for them to send (or edit) manually.

### `.font(font)`

Sets a custom font resource location (e.g. `"minecraft:alt"`), for resource packs that ship alternate fonts.

### `.shadow_color(color)`

Sets the text's shadow color as an `ArgbColor { a, r, g, b }`. This is a newer Minecraft rendering feature, most components can leave it unset and get the default shadow.

## Click actions

### `.click_open_url(url)`

Opens `url` in the player's default browser when clicked (subject to their client-side "open link" confirmation prompt).

### `.click_run_command(command)`

Runs `command` as if the player typed and sent it themselves, including the leading `/`.

### `.click_suggest_command(command)`

Populates the player's chat box with `command`, same as `insertion`, but triggered by a click instead of shift-click.

### `.click_copy_to_clipboard(text)`

Copies `text` to the player's clipboard when clicked.

> [!NOTE]
> There's only one click action slot per component. Calling a second `click_*` method overwrites the first, it doesn't stack them. If you need different parts of a message to do different things on click, split it across multiple `add_child` components, one per click action.

## Hover actions

### `.hover_show_text(text)`

Shows `text` (another `TextComponent`) as a tooltip when the player hovers over this component. Like `add_child`, this **consumes** the `text` argument, its handle is moved into the parent's style.

### `.hover_show_item(item)`

Shows an item tooltip, in the same style as hovering over an item in an inventory. `item` isn't an `ItemStack` resource here, it's a raw SNBT string describing the item (e.g. `"minecraft:diamond_sword{Enchantments:[...]}"`), so you're responsible for formatting it yourself.

### `.hover_show_entity(entity_type, id, name)`

Shows an entity tooltip. `entity_type` is a resource location string (`"minecraft:zombie"`), `id` is the entity's UUID as a string, and `name` is an optional `TextComponent` for a custom display name in the tooltip, if given, it's consumed the same way `hover_show_text`'s argument is.

> [!NOTE]
> Only one hover action slot exists per component, same as click actions: the last `hover_*` call wins.

## Putting it together

A warp confirmation message: plain text, a colored and clickable warp name that shows a preview on hover, and a shift-clickable "run it again" hint.

```rust
use pumpkin_plugin_api::{common::NamedColor, text::TextComponent};

fn warp_confirmation(warp_name: &str) -> TextComponent {
  let preview = TextComponent::text(&format!("Teleport to '{warp_name}'"));

  let name = TextComponent::text(warp_name);
  name.color_named(NamedColor::Aqua);
  name.bold(true);
  name.click_run_command(&format!("/warp {warp_name}"));
  name.hover_show_text(preview);
  name.insertion(&format!("/warp {warp_name}"));

  let message = TextComponent::text("Warped to ");
  message.add_child(name);
  message.add_text(".");
  message
}
```

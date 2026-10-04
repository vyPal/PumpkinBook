# Java dialogs

Java Edition's rich dialog screens (introduced for server-side menus, forms, and confirmation prompts), shown with `java_player.show_dialog(dialog)` and cleared with `java_player.clear_dialog()`. Unlike Bedrock forms, there's no dedicated builder here, you construct a `Dialog` record directly, `java_dialogs` (and the smaller `java_dialog` re-export) are both bare data types.

## The dialog shape

A `Dialog` has: `title`, a `DialogType` (`Notice` for a single OK button, `Confirmation` for Yes/No, `MultiAction` for a scrollable button list, `DialogList` for buttons that open other dialogs, `ServerLinks` for a dedicated links menu), `body` (a list of `DialogBody`, either `PlainMessage(text)` or `Item(item_stack)`), `inputs` (interactive controls, only meaningful for some dialog types), `buttons` (for `MultiAction`), `links` (for `ServerLinks`), `after_action` (`Peek` to return to the previous screen, `Pop` to close everything), `can_close_with_escape`, and `external_title` (the label used on buttons that open this dialog from elsewhere).

```rust
use pumpkin_plugin_api::{java_dialogs::{Dialog, DialogBody, DialogType}, text::TextComponent};

let dialog = Dialog {
  title: TextComponent::text("Server Rules"),
  type_: DialogType::Notice,
  body: vec![DialogBody::PlainMessage(TextComponent::text("Be respectful. No griefing."))],
  inputs: vec![],
  buttons: vec![],
  links: vec![],
  after_action: None,
  can_close_with_escape: true,
  external_title: None,
};

java_player.show_dialog(dialog);
```

> [!WARNING]
> `DialogBody::Item(item_stack)` doesn't work correctly yet, the host currently maps any item body to a hardcoded placeholder item id regardless of what `ItemStack` you actually pass in. Stick to `PlainMessage` bodies until this is fixed.

## Inputs

`inputs` takes a list of `DialogInput` variants: `Bool(DialogInputBool { label, default_value })` for a checkbox, `Text(DialogInputText { label, placeholder, default_value })` for a text field, `NumberRange(DialogInputNumberRange { label, min_value, max_value, initial_value, step, label_format })` for a slider, `SingleOption(DialogInputSingleOption { label, options, initial_index })` for a multiple-choice picker.

> [!NOTE]
> The WIT contract declares these input types, but unlike forms, there's currently no documented event that returns a dialog's submitted input values back to the plugin, only button clicks (via `Action::CustomClick`, below) are wired up to an event. The click event carries an optional `payload`, raw bytes forwarded from the client, but this book hasn't verified that it contains the input values, so don't build on it without testing. Treat inputs as reflecting real client-side dialog capability that may not be fully round-trippable to your plugin yet.

## Buttons & custom actions

`buttons` (for `MultiAction`) is a list of `ActionButton { text, tooltip, width, action }`, where `action` is either `Action::OpenUrl(url)` or `Action::CustomClick(CustomClickAction { id, payload })`.

```rust
use pumpkin_plugin_api::java_dialogs::{Action, ActionButton, CustomClickAction, Dialog, DialogType};

let dialog = Dialog {
  title: TextComponent::text("Server Menu"),
  type_: DialogType::MultiAction,
  body: vec![],
  inputs: vec![],
  buttons: vec![
    ActionButton {
      text: TextComponent::text("Teleport to Spawn"),
      tooltip: None,
      width: None,
      action: Action::CustomClick(CustomClickAction {
        id: "my_plugin:tp_spawn".to_string(),
        payload: None,
      }),
    },
    ActionButton {
      text: TextComponent::text("Website"),
      tooltip: None,
      width: None,
      action: Action::OpenUrl("https://example.com".to_string()),
    },
  ],
  links: vec![],
  after_action: Some(pumpkin_plugin_api::java_dialogs::AfterAction::Pop),
  can_close_with_escape: true,
  external_title: None,
};
```

A `CustomClick` button fires a `DialogClickActionEvent` when pressed, carrying `player`, `id` (matching what you set on the button), an optional `payload`, and `cancelled`, that's how you find out which button in a `MultiAction` dialog got clicked.

```rust
use pumpkin_plugin_api::events::{DialogClickActionEvent, EventData};

impl EventHandler<DialogClickActionEvent> for MenuHandler {
  fn handle(&self, _server: Server, event: EventData<DialogClickActionEvent>) -> EventData<DialogClickActionEvent> {
    if event.id == "my_plugin:tp_spawn" {
      // teleport event.player to spawn
    }
    event
  }
}
```

> [!NOTE]
> This event was renamed from `CustomClickActionEvent` in earlier versions of this crate. Two more dialog events are declared alongside it, `DialogShowEvent` (`player`, `dialog`, `cancelled`, meant to fire when a dialog is about to be shown) and `DialogClearEvent` (`player`, `cancelled`, meant to fire when a dialog is cleared).

> [!WARNING]
> Those two never fire. You can register handlers for them, but nothing in the server creates either event, so a handler for `DialogShowEvent` can't be used to suppress a dialog. Only `DialogClickActionEvent` is wired up. See the [Event reference](../advanced/event-reference.md#dialog-events).

## Links

`links` (for `ServerLinks`) is a list of `Link { label, url }`, where `label` is a `LinkLabel`, either `BuiltIn(LinkType)` (a recognized icon/label like `BugReport`, `Community`, `Website`, `Forums`, `Status`) or `Custom(text_component)` for your own label text.

## Putting it together

A rules dialog that also offers a "Teleport to Spawn" action button:

```rust
use pumpkin_plugin_api::{
  java_dialogs::{Action, ActionButton, AfterAction, CustomClickAction, Dialog, DialogBody, DialogType},
  text::TextComponent,
};

fn show_welcome_dialog(java_player: &JavaPlayer) {
  let dialog = Dialog {
    title: TextComponent::text("Welcome!"),
    type_: DialogType::MultiAction,
    body: vec![DialogBody::PlainMessage(TextComponent::text("Glad to have you here."))],
    inputs: vec![],
    buttons: vec![ActionButton {
      text: TextComponent::text("Teleport to Spawn"),
      tooltip: None,
      width: None,
      action: Action::CustomClick(CustomClickAction {
        id: "my_plugin:tp_spawn".to_string(),
        payload: None,
      }),
    }],
    links: vec![],
    after_action: Some(AfterAction::Pop),
    can_close_with_escape: true,
    external_title: None,
  };

  java_player.show_dialog(dialog);
}
```

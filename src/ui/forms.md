# Bedrock forms

Forms are Bedrock Edition's client-native UI, simpler and more limited than a Java custom GUI or dialog, but the standard way to get structured input (a menu choice, a checkbox, a text field) from a Bedrock player. Build one with the fluent builders in the `forms` module, you never need to name the underlying `Form`/`FormImage`/`SimpleFormButton` WIT types directly, just chain the builder and hand its `.build()` output straight to `open_form`.

## Simple forms

### `SimpleFormBuilder::new(title, content)` / `.button(text, image)` / `.build()` { data-since=0.1 }

A title, a body message, and a list of buttons the player picks one of.

```rust
use pumpkin_plugin_api::{forms::SimpleFormBuilder, text::TextComponent};

let form = SimpleFormBuilder::new(
  TextComponent::text("Choose a class"),
  TextComponent::text("Pick your starting class."),
)
  .button(TextComponent::text("Warrior"), None)
  .button(TextComponent::text("Mage"), None)
  .build();

bedrock_player.open_form(form);
```

`image` is `Option<FormImage>`, build one with `forms::url_image(url)` or `forms::path_image(path)` instead of constructing the type by hand.

## Modal forms

### `ModalFormBuilder::new(title, content)` / `.button1(text)` / `.button2(text)` / `.build()` { data-since=0.1 }

A yes/no or confirm/cancel style prompt, exactly two buttons. They default to localized "Yes"/"No" labels if you don't override them.

```rust
use pumpkin_plugin_api::{forms::ModalFormBuilder, text::TextComponent};

let form = ModalFormBuilder::new(
  TextComponent::text("Leave the party?"),
  TextComponent::text("You'll need an invite to rejoin."),
)
  .button1(TextComponent::text("Leave"))
  .button2(TextComponent::text("Cancel"))
  .build();
```

## Custom forms

### `CustomFormBuilder::new(title)` / `.label(text)` / `.toggle(text, default)` / `.slider(text, min, max, step, default)` / `.step_slider(text, steps, default_index)` / `.dropdown(text, options, default_index)` / `.input(text, placeholder, default)` / `.build()` { data-since=0.1 }

Actual structured input, chain as many elements as you need in display order.

```rust
use pumpkin_plugin_api::{forms::CustomFormBuilder, text::TextComponent};

let form = CustomFormBuilder::new(TextComponent::text("Character settings"))
  .toggle(TextComponent::text("Enable PvP"), true)
  .slider(TextComponent::text("Volume"), 0.0, 1.0, 0.05, 0.8)
  .input(TextComponent::text("Nickname"), "Enter a name", "")
  .build();
```

## Showing one

### `bedrock_player.open_form(form)` { data-since=0.1 }

Returns a `u32` form id, hold onto it, it's how you'll match the response back to this specific form.

```rust
let form_id = bedrock_player.open_form(form);
```

## Reading the response

Forms don't have a callback method, the response comes back through an event: `BedrockFormResponseEvent`, carrying `player`, `form_id` (matching what `open_form` returned), and `response_data`, the raw `Option<String>` JSON payload the client sent back. Parse it with `forms::FormResponse::parse`, rather than hand-rolling the JSON matching yourself, it already knows the response shape differs by form kind.

```rust
use pumpkin_plugin_api::{
  events::{BedrockFormResponseEvent, EventData},
  forms::FormResponse,
};

impl EventHandler<BedrockFormResponseEvent> for FormResponseHandler {
  fn handle(&self, _server: Server, event: EventData<BedrockFormResponseEvent>) -> EventData<BedrockFormResponseEvent> {
    match FormResponse::parse(event.response_data.clone()) {
      FormResponse::Simple(index) => tracing::info!("Form {}: button {index} clicked", event.form_id),
      FormResponse::Modal(confirmed) => tracing::info!("Form {}: {confirmed}", event.form_id),
      FormResponse::Custom(values) => tracing::info!("Form {}: {values:?}", event.form_id),
      FormResponse::Closed => tracing::info!("Form {} was closed without a response.", event.form_id),
    }
    event
  }
}
```

> [!NOTE]
> `FormResponse::parse` guesses the form kind from the shape of the JSON it receives (a bare number for `Simple`, a bare boolean for `Modal`, an array for `Custom`), it isn't told which form you originally sent. Track `form_id` to `Form` kind yourself if you need to be certain rather than inferring it from the response shape, especially since a `Custom` form with a single numeric element could otherwise look like a `Simple` response.

## Putting it together

Sending a class-select form and handling the response by form id:

```rust
use pumpkin_plugin_api::{
  events::{BedrockFormResponseEvent, EventData},
  forms::{FormResponse, SimpleFormBuilder},
  text::TextComponent,
};

fn open_class_select(bedrock_player: &BedrockPlayer) -> u32 {
  let form = SimpleFormBuilder::new(
    TextComponent::text("Choose a class"),
    TextComponent::text("Pick your starting class."),
  )
    .button(TextComponent::text("Warrior"), None)
    .button(TextComponent::text("Mage"), None)
    .build();

  bedrock_player.open_form(form)
}

fn handle_response(event: EventData<BedrockFormResponseEvent>, class_select_form_id: u32) {
  if event.form_id != class_select_form_id {
    return; // not our form
  }

  if let FormResponse::Simple(index) = FormResponse::parse(event.response_data.clone()) {
    let class = if index == 0 { "Warrior" } else { "Mage" };
    tracing::info!("{} picked {class}", event.player.get_name());
  }
}
```

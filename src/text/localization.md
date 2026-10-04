# Localization

A small, free-function interface for server-side translation lookups, addressed by `Locale` (the full Minecraft locale list, `EnUs`, `DeDe`, `FrFr`, and so on, from the `common` module).

## Looking up a translation

### `i18n::translate(key, locale)` { data-since=0.1 }

Resolves a translation key to plain text, server-side, for a specific `Locale`. This is different from `TextComponent::translate` (see [Text components](./text-components.md)), which sends a key to the *client* and lets it resolve the key using its own language file, `i18n::translate` resolves the key on the server and gives you back a plain `String`, useful when you need the actual resolved text yourself (building a log message, a console command's feedback, or anything that isn't rendered by a Minecraft client).

```rust
use pumpkin_plugin_api::{common::Locale, i18n};

let text = i18n::translate("multiplayer.player.joined", Locale::EnUs);
```

> [!WARNING]
> The host's `Locale`-to-internal-locale conversion is broken for every locale whose code has more than one part (basically all of them, `EnUs`, `DeDe`, `FrFr`, and so on). It converts the WIT enum variant to a lowercase string without restoring the underscore (`EnUs` becomes `"enus"`, not `"en_us"`), which fails to parse and silently falls back to `EnUs`. In practice, calling `translate` with any locale other than `EnUs` currently returns the **English** translation anyway. The handful of genuinely single-word locale codes (`Bar`, `Brb`, `Isv`, `Ksh`, and similar) aren't affected, since there's no underscore to lose for those.

## Registering your own translations

### `i18n::load_translations(namespace, json, locale)` { data-since=0.1 }

Loads a flat JSON map of your own translation keys for a given namespace and locale, so `i18n::translate("my_plugin:welcome_message", locale)` resolves to whatever you registered instead of erroring or falling through to a vanilla key.

```rust
use pumpkin_plugin_api::{common::Locale, i18n};

let translations = r#"{
  "my_plugin:welcome_message": "Welcome to the server!"
}"#;

i18n::load_translations("my_plugin", translations, Locale::EnUs);
```

Load your translation files early, in `on_load`, before anything might try to resolve a key from them.

## Putting it together

Loading a couple of custom keys at startup, then using one to build a system message:

```rust
use pumpkin_plugin_api::{common::Locale, i18n, text::TextComponent, Context, Result};

fn on_load(&self, context: Context) -> Result<()> {
  let translations = r#"{
    "my_plugin:shop_closed": "The shop is currently closed."
  }"#;
  i18n::load_translations("my_plugin", translations, Locale::EnUs);

  Ok(())
}

fn notify_shop_closed(sender: &CommandSender) {
  let message = i18n::translate("my_plugin:shop_closed", Locale::EnUs);
  sender.send_message(TextComponent::text(&message));
}
```

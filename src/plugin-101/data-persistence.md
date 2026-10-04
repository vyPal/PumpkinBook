# Data persistence

Most plugins need to remember something between restarts: a config file, some player stats, a small local database. Pumpkin doesn't expose its own storage API for this: the plugin sandbox just gives you a private folder, and you read and write files in it with your language's normal file API (`std::fs` in Rust), gated behind the `fs.read.data` / `fs.write.data` permissions from [Plugin permissions](./plugin-permissions.md).

```rust
use pumpkin_plugin_api::permissions;

fn metadata(&self) -> PluginMetadata {
  PluginMetadata {
    // ...
    permissions: vec![permissions::FS_WRITE_DATA.into()],
  }
}
```

`fs.write.data` includes reading, so a plugin that writes only needs that one. Without either permission, `context.get_data_folder()` still returns a path, but any read or write against it fails (with `No such file or directory`, since the folder simply isn't mounted into the sandbox).

The string you get back is `data`, the folder's name *inside* the sandbox. The real folder is `plugins/data/<plugin name>` on the server, and the server creates it for you, but you can't see or use that path: the sandbox has no working directory and no other folders, so a relative path like `config.toml` fails too. Always build your paths from `get_data_folder()`.

## Example: a config file with serde and toml

A common pattern is a small struct, (de)serialized with [`serde`](https://serde.rs) and stored as TOML:

```toml
[dependencies]
serde = { version = "1", features = ["derive"] }
toml = "0.8"
```

```rust
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct Config {
  greeting: String,
}

impl Default for Config {
  fn default() -> Self {
    Self { greeting: "Welcome to the server!".into() }
  }
}
```

Load it in `on_load()`, writing out the defaults the first time there's nothing to read:

```rust
fn load_config(data_dir: &str) -> Config {
  let path = format!("{data_dir}/config.toml");

  match std::fs::read_to_string(&path) {
    Ok(raw) => toml::from_str(&raw).unwrap_or_default(),
    Err(_) => {
      let config = Config::default();
      let _ = std::fs::write(&path, toml::to_string_pretty(&config).unwrap_or_default());
      config
    }
  }
}

fn on_load(&self, context: Context) -> Result<()> {
  let config = load_config(&context.get_data_folder());
  // store `config` on your plugin struct so other handlers can use it
  Ok(())
}
```

> [!NOTE]
> This isn't Rust- or TOML-specific, the same shape works with any language's file API and any format your ecosystem offers (JSON, SQLite, etc.). The only Pumpkin-specific parts are the two `fs.*` permissions and getting the folder path from `context.get_data_folder()`.

# General code snippets

## Load metadata from `Cargo.toml`

```rust
fn metadata(&self) -> PluginMetadata {
  PluginMetadata {
    name: env!("CARGO_PKG_NAME").into(),
    version: env!("CARGO_PKG_VERSION").into(),
    authors: env!("CARGO_PKG_AUTHORS")
      .split(",")
      .map(|v| v.to_string())
      .collect(),
    description: env!("CARGO_PKG_DESCRIPTION").into(),
    dependencies: vec![],
    permissions: vec!["fs.read.data".into(), "fs.write.data".into()],
  }
}
```

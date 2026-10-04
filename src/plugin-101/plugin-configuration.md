# Plugin loading & server configuration

Most of this book is about what your plugin can do once it's running. This chapter is about the part before that: what the server does with a `.wasm` file between you dropping it into `plugins/` and your `on_load()` being called, and which switches the server owner has to change that. If you write plugins, it explains a lot of "why didn't my plugin load" moments. If you run a server, the [configuration reference](#the-plugins-section-of-pumpkintoml) is the part you want.

## What happens at startup

1. **The `plugins/` folder is scanned**, non-recursively, for `.wasm` files. Sub-folders are ignored, and so is any file whose name ends in `.deactivated`, which makes renaming a plugin to `something.wasm.deactivated` the quickest way to switch it off.
2. **Each file is compiled and inspected.** Compiled output is cached in `plugins/cache/`, keyed by a hash of the file and the server version, so only the first start after a change is slow. The server reads which [plugin API version](../api-versions.md) the plugin was built against, and rejects it if it's one it doesn't know.
3. **The per-plugin settings are applied.** A plugin disabled in the configuration, or an unsigned one when unsigned plugins aren't allowed, is skipped here.
4. **Dependencies are sorted out.** Plugins are ordered so that everything listed in a plugin's `dependencies` comes first. See [Dependencies and load order](./plugin-logic.md#dependencies-and-load-order) for the one sharp edge here.
5. **Permissions are checked** and, if needed, the server owner is asked. More on that below.
6. **`on_load()` runs**, one plugin at a time, in dependency order.

## The `[plugins]` section of `pumpkin.toml`

Everything the server owner can tune lives in the `[plugins]` section of the server's main `pumpkin.toml`. These are the defaults:

```toml
[plugins]
enabled = true
hot_reload = false
ask_permission_confirmation = true
allow_unsigned = true
verify_signatures = true
allowed_permissions = []
blocked_permissions = []
inherit_env = false
loopback_only = false
# max_memory_mb = 256        # no limit when this is left out

[plugins.overrides]
```

| Option | Default | What it does |
|---|---|---|
| `enabled` | `true` | Master switch. With `false` no plugin is loaded at all. |
| `hot_reload` | `false` | Watches `plugins/` and reloads a plugin whenever its `.wasm` file changes. |
| `ask_permission_confirmation` | `true` | Asks in the console before a plugin that requests permissions is loaded. With `false` the request is approved automatically. |
| `allow_unsigned` | `true` | Whether plugins without a valid marketplace signature may load. |
| `verify_signatures` | `true` | Whether signatures are checked at all. With `false`, nothing is verified and `context.get_marketplace_metadata()` returns `None` for every plugin. |
| `allowed_permissions` | `[]` | Permissions approved for every plugin without asking. |
| `blocked_permissions` | `[]` | Permissions no plugin is ever given. |
| `inherit_env` | `false` | Hands every plugin the server's environment variables without a permission. |
| `loopback_only` | `false` | Restricts every plugin's sockets to localhost. |
| `max_memory_mb` | none | Caps how much memory one plugin instance may use. |

### Per-plugin overrides

A `[plugins.overrides.<PluginName>]` table changes the settings for one plugin, matched against the `name` in its metadata:

```toml
[plugins.overrides.MyPlugin]
enabled = true
allow_unsigned = true
max_memory_mb = 128
allowed_permissions = ["fs.read.data", "fs.write.data"]
blocked_permissions = ["network.outbound"]
loopback_only = true

[plugins.overrides.MyPlugin.environment]
MY_API_KEY = "secret_key"
```

`enabled`, `allow_unsigned`, `max_memory_mb` and `loopback_only` replace the global value for that plugin. The two permission lists add to the global ones. The `environment` table injects variables into that plugin's environment regardless of any permission, which is the clean way to hand a plugin a secret without giving it access to everything else the server's environment contains.

> [!WARNING]
> Permission names in these lists use dots, like the constants in the `permissions` module: `fs.read.data`, `network.outbound`. The example in the server's own source comments writes them with colons (`fs:read:data`). Those never match anything, so a list written that way silently does nothing.

## Permission prompts

When a plugin's metadata asks for permissions (see [Plugin permissions](./plugin-permissions.md)), the server decides in this order:

1. Anything in `blocked_permissions` (global or per-plugin) is removed from the request first. The plugin still loads, it just doesn't get that permission, and nothing is logged about it. Its reads or writes fail the same way they would if it had never asked.
2. If everything that's left is in `allowed_permissions`, or the plugin asked for nothing, it loads without a question.
3. Otherwise, if `ask_permission_confirmation` is off, the request is approved and a line saying so is logged.
4. Otherwise the console lists the permissions with a description each and asks `[y/N]`. Only `y` or `yes` approves.

The answer is remembered in `plugins/permission_cache.json`, keyed by a hash of the plugin file and the exact list of permissions it asked for. **A denial is remembered too.** A denied plugin stays denied on every start until its file changes, its permission list changes, or the entry is removed from the cache. Updating the plugin asks again.

> [!NOTE]
> The prompt needs a console that can read input. On a main-thread start with no terminal attached (a Docker container without `-it`, a service manager), the server logs that it can't prompt and denies the plugin. Headless servers should pre-approve with `allowed_permissions`, or turn the prompt off with `ask_permission_confirmation = false`. A plugin that needs the prompt while the server is already running (for example one picked up by hot reload) is denied as well, since prompts are only supported on the main thread.

## Signatures

Plugins distributed through a Pumpkin plugin marketplace are signed. With `verify_signatures` on, the server checks that signature when the file is loaded. A valid signature unlocks `context.get_marketplace_metadata()` for the plugin (see [Basic plugin logic](./plugin-logic.md)), and `allow_unsigned = false` refuses everything else:

```text
ERROR Plugin "MyPlugin" ("./plugins/my_plugin.wasm") is unsigned or invalid and allow_unsigned is disabled in configuration, skipping.
```

Unsigned plugins that are allowed still load, with a warning that unsigned plugins may come from untrusted sources.

## Memory, environment and network limits

- **Memory.** `max_memory_mb` (global or per plugin) limits how much memory one plugin instance can grow to.
- **Environment variables.** A plugin sees none of the server's environment unless it holds the `sys.env` permission (all of it), `sys.env.<NAME>` (one variable), or the server sets `inherit_env = true`. Variables from a per-plugin `environment` table are always present.
- **Network.** Sockets need the `network.*` permissions. `loopback_only = true` (or the `network.loopback` permission for one plugin) doesn't grant anything by itself, it narrows whatever the plugin was granted down to loopback addresses (`127.0.0.0/8` and `::1`).

## Managing plugins while the server runs

Two commands are built in:

- `/plugins` lists the loaded plugins, with their version, authors and requested permissions on hover.
- `/plugin list`, `/plugin load <name>`, `/plugin unload <name>` and `/plugin hotreload enable|disable` manage them. This command needs the `pumpkin:command.plugin` permission, and `/plugins` needs `pumpkin:command.plugins`.

With `hot_reload = true` (or after `/plugin hotreload enable`) the server watches the `plugins/` folder. When a `.wasm` file is created or modified, a loaded plugin with that path is unloaded first, and the new file is then loaded like at startup. Unloading runs your `on_unload()` and removes the handlers, tasks and commands the plugin registered, see [Basic plugin logic](./plugin-logic.md#on_unloadcontext---result).

## Putting it together

A server owner who wants a trusted plugin to read and write its own files without a prompt, a second plugin to be allowed no network at all, and a third one switched off:

```toml
[plugins]
allow_unsigned = true
ask_permission_confirmation = true

[plugins.overrides.Economy]
allowed_permissions = ["fs.read.data", "fs.write.data"]

[plugins.overrides.ChatBridge]
allowed_permissions = ["http.outbound"]
blocked_permissions = ["network.outbound", "network.tcp", "network.udp"]

[plugins.overrides.OldExperiment]
enabled = false
```

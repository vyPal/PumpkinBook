# API changelog

A commit-by-commit summary of what changed in the plugin WIT, the contract between the server and your plugin. Breaking changes are called out first, since those are the ones that stop a plugin from loading or compiling.

> [!WARNING]
> **v0.1 is now officially frozen.** It was first declared frozen on 2026-09-29, but it still changed three times in October, the last time on 2026-10-11. A plugin built against an earlier revision is rejected at load time (`Plugin was built against a different iteration of the API: type-checking export func `handle-event``). **Rebuild every plugin that was compiled before 2026-10-11**, and any built between 2026-10-29 and 2026-10-31. Details are on [Plugin API versions](./api-versions.md#what-frozen-means).

> [!WARNING]
> **Breaking changes in v0.1 since 2026-08-29** (the checkpoint this changelog starts from), newest first. Every one of them changes the shared `event` type, packet records included, so each one breaks **every** plugin built before it, not just those that use the changed part:
> - 2026-10-29 to 2026-10-31: a Bedrock packet change landed in v0.1 and was reverted two days later. Only plugins built in that window are affected.
> - 2026-10-11: `s-spectate-entity.target` went from `uuid` to `s32`.
> - 2026-10-07: several Java and Bedrock packet fields that held NBT as a `string` are now `nbt-tree`.
> - 2026-10-06: `block-burn-event-data` gained `block-pos` and `target-world`.
> - 2026-09-29: one Bedrock packet field changed type (`action` is now a `player-action-type`).
> - 2026-09-28: `creature-spawn-event-data` gained a `player` field.
> - 2026-09-19 and 2026-09-18: Java and Bedrock packet records changed (removed, renamed and re-typed records), data component enum cases were removed and added.
> - 2026-09-04: the scoreboard's `add-objective`, `update-objective` and `update-score` gained a `number-format` parameter. Every plugin that calls them.

> [!NOTE]
> **v0.2 is where breaking changes go from now on.** Nothing in it is a stable promise yet, and a default server build doesn't load v0.2 plugins at all (see [Plugin API versions](./api-versions.md#how-the-server-picks-a-version)). When an entry below is tagged v0.2 and breaking, it doesn't affect any v0.1 plugin.

Entries start at 2026-08-29 (`f481f56`). The checkpoint before this one ended at `de0cfdb` (2026-10-04). Before that, the previous revision of this book left off. Earlier history lives in the git log of the [`pumpkin-plugin-wit`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit) repository. Each entry names the commit in that repository, which mirrors the `crates/pumpkin-plugin-wit` folder of the main Pumpkin repository on every push to `master`.

## v0.2 (in development)

### 2026-10-29 to 2026-11-02 · Bedrock 26.60 and more Bedrock packets

[`68d1217`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/68d1217) (pull request #4407), [`c3af8a6`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/c3af8a6) (#4428), [`7876442`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/7876442), [`51dbdc7`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/51dbdc7), and before them [`c30a96e`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/c30a96e) and [`182c4c8`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/182c4c8) (2026-10-23).

- **Changed (v0.2 Bedrock packets):** ported to Bedrock 1.26.60, with packets added for resource pack streaming, block actor data and sign editing, cursor item drags, item stack requests, container properties, entity equipment and entity links. One Java packet record was added too.
- **Breaking:** raw packet users of v0.2. [`68d1217`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/68d1217) also touched v0.1, see [below](#2026-10-29--68d1217-and-fb86e00--bedrock-2660-in-v01-reverted).

### 2026-10-30 · [`15d751b`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/15d751b) · protocol `i8` fields are `s8`

Pull request #4413.

- **Changed (v0.2 packets):** about thirty Java and Bedrock packet fields that the protocol encodes as a signed byte were declared with the wrong integer type. They are now `s8`.
- **Breaking:** raw packet users of v0.2.

### 2026-10-29 · [`27401e3`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/27401e3) · mob AI event details

Pull request #4107.

- **Added (v0.2):** `entity-toggle-sit-event` (`entity-id`, `sitting`, `cancelled`), fired when a tameable mob sits down or stands up.
- **Changed (v0.2):** `entity-target-event-data` gained `reason: target-reason` (closest player, attacked, owner attacked, angry, forgot target, and so on), and `entity-breed-event-data` gained `experience`.
- **Breaking:** yes, for every v0.2 plugin built earlier.

### 2026-10-26 · [`332fd86`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/332fd86) · more player and inventory API

Described as "Bukkit parity".

- **Added (v0.2):** inventory helpers (`add-item`, `remove-matching`, `contains-at-least`, `first-empty`, `has-space-for`, `give-item`, cursor item access, storage and armor contents), item stack helpers (damage, unbreakable, repair cost, item model, enchantment glint), player methods (`perform-command`, `chat`, custom chat completions, `look-at`, sneaking and sprinting, sleeping, `close-inventory`, `drop-item`, post effects), world methods (`is-chunk-loaded`, `break-block`, `drop-item-naturally`, `spawn-experience-orb`, entity lookup by id, UUID and box), item entity access, and `get-score`/`get-objectives` on scoreboards.
- **Breaking:** no, additions only. None of it exists in v0.1.

### 2026-10-16 · [`deb215c`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/deb215c) · async ABI

Pull request #3713.

- **Changed (v0.2):** every plugin export except `init-plugin` and `metadata` is now an `async func` (`on-load`, `on-unload`, `handle-event`, `handle-command`, `handle-task`, `handle-ipc-message`, the AI goal and world generation callbacks). Host calls that may wait on the server became `async` too, among them `send-ipc-message`, `set-gamemode` and most inventory and item stack writes.
- **Changed (v0.2):** `command-sender.has-permission` no longer takes a `server` argument.
- **Documented:** `get-metadata` must not call into the host, and `init-plugin` only wires up the plugin, so setup that needs host calls belongs in `on-load`. A non-blocking event handler's returned event is ignored, and returning a different event case than the one dispatched counts as an error.
- **Breaking:** yes, for every v0.2 plugin. A toolchain targeting v0.2 now needs component-model async support throughout.

### 2026-10-16 · [`79cc4f0`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/79cc4f0) · v0.1 no longer generated

Pull request #4074.

- **Changed:** the code generator now only produces v0.2. The v0.1 WIT is left as it is from here on, which is what finally makes the freeze stick.
- **Added (v0.2):** a placeholder enum `inexpressible-host-type` in `common.wit`, used where a server type has no WIT equivalent yet, and adjustments to several v0.2 packet records.
- **Breaking:** raw packet users of v0.2.

### 2026-10-04 · [`de0cfdb`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/de0cfdb) · GameTest interface

Pull request #3770.

- **Added** `gametest.wit`: an interface for registering in-game tests, simulated players and test sequences, plus the callback interface `gametest-callbacks` that the server calls back into.
- **Added** to the v0.2 plugin world: `import gametest` and `export gametest-callbacks`. Every v0.2 plugin must now export the callbacks, even if it never uses GameTest, and one of them is an `async` function.
- **Not usable yet.** The host methods all return a "not implemented" error, and a failing host call kills the plugin that made it.
- **Breaking:** not for v0.1. Anything built against v0.2 before this commit needs the new export.

### 2026-09-29 · [`8e38811`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/8e38811) · v0.2 branched from v0.1

Pull request #3766. Copies the entire v0.1 WIT into a new `v0.2` folder, stamped `pumpkin:plugin@0.2.0`, and teaches the server to load both. See [Plugin API versions](./api-versions.md).

- **Added** the whole `v0.2` folder. At this commit it is identical to v0.1 apart from the package version.
- **Changed (v0.1):** in `bedrock-packets.wit`, a packet's `action` field went from `s32` to the new `player-action-type` enum.
- **Breaking (v0.1):** raw Bedrock packet users, for that one field. v0.1 has not changed since.

## v0.1 (frozen)

### 2026-10-29 · [`68d1217`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/68d1217) and [`fb86e00`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/fb86e00) · Bedrock 26.60 in v0.1, reverted

Pull request #4407 changed nine lines of the v0.1 `bedrock-packets.wit` as part of porting the protocol to Bedrock 1.26.60. That was a mistake for a frozen version, and [`fb86e00`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/fb86e00) reverted it on 2026-10-31.

- **Net change:** none. The v0.1 WIT after the revert is identical to the one from 2026-10-11.
- **Breaking:** only for plugins built between the two commits. Those are rejected by servers on either side of the window, rebuild them.

### 2026-10-11 · [`ddcc88d`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/ddcc88d) · spectate packet

Pull request #3705.

- **Changed (Java packets):** `s-spectate-entity.target` went from `uuid` to `s32`, matching what 26.3 clients actually send: `0` for no target, otherwise the entity id plus one.
- **Breaking:** yes, for every plugin. This was the last change to v0.1.

### 2026-10-07 · [`75f96e9`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/75f96e9) · NBT as `nbt-tree` in packets

- **Changed (Java and Bedrock packets):** fields that carried NBT as a `string` are now the structured `nbt-tree` from `common.wit` (the same type [persistent data](./persistent-data/persistent-data.md#the-raw-nbttree-escape-hatch) uses). A Bedrock record called `gg` was replaced with `block-property`, and a `block-properties-size` count with the list itself.
- **Added:** doc comments on hundreds of packet records and fields. No effect on the API.
- **Breaking:** yes, for every plugin.

### 2026-10-06 · [`2576829`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/2576829) · block burn event knows where it is

Pull request #3857.

- **Changed** `block-burn-event-data`: new fields `block-pos` and `target-world`, so a handler can find out which block is burning. Before this, the event only carried two block names.
- **Breaking:** yes, for every plugin.

### 2026-09-28 · [`39bf330`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/39bf330) · creature spawn event knows the player

Pull request #3568, mob AI fixes.

- **Changed** `creature-spawn-event-data`: new field `player: option<player>`, set when a player caused the spawn.
- **Breaking:** yes, for every plugin. The `event` variant is part of every plugin's `handle-event` signature, so any new field in any event record changes the type for all of them.

### 2026-09-19 · [`4d7a501`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/4d7a501) · multi-version support moved out of the server

Refactor, moving older-client support into a separate plugin.

- **Changed (Bedrock packets):** `item-descriptor-count` now holds a `descriptor: recipe-item-descriptor` (a variant of `empty`, `item` or `tag`) instead of a plain `item-identifier` string.
- **Added (Java packets):** `c-post-effects` and `config-c-config-post-effects`.
- **Removed (Java packets):** `c-spawn-living-entity`, `c-spawn-painting` and `c-use-bed`.
- **Breaking:** raw packet users only.

### 2026-09-18 · [`64f4610`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/64f4610) · Minecraft 26.3

Pull request #3495.

- **Added** `v-26-3` to `java-minecraft-version`.
- **Added** content to the vanilla catalogs: about two dozen sounds (cushion, shelf mushroom, poplar leaves, straw bed, red shrub), three poplar leaf particles, three entity types, two entity statuses, one biome (`dappled-forest`) and the `sleep-in-straw-bed` statistic.
- **Changed** `data-components.wit`: `swing-animation` and `map-color` were removed, and several cases were added (`attack-animation`, `interact-animation`, `block-transformer`, `villager-food`, `compostable`, `cooking-fuel`, `brewing-fuel`, `mob-visibility`, `provides-pottery-pattern`, `sign-text-front`, `sign-text-back`, `waxed`, `cushion-color`, `boat-launch`, `boat-sink`, `cushion`, `poplar-boat`, `poplar-chest-boat`).
- **Changed (Java packets):** a `hand` field went from `u8` to a new `hand-slot` enum, a `seed` went from `f64` to `s64`, the client platform case `nx` was renamed `nintendo`, `s-swing-arm` was removed in favor of a new `c-swing-arm`, and several records were added (`c-chunk-data` with `chunk-heightmaps` and `chunk-block-entity`, among others).
- **Breaking:** yes. Enum cases were removed and re-typed, and since the WIT type check is structural, enums that gained cases are different types too. Plugins built earlier need a rebuild, and code that used the removed data components or packets needs updating.

### 2026-09-18 · [`2366bb9`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/2366bb9) · Bedrock 26.51

Pull request #3472.

- **Changed (Bedrock packets):** the `c-level-chunk` packet was removed. `c-jigsaw-structure-data` and `c-voxel-shapes` were added. Fields were added or removed on a few records (a `hand` field, a `tick` field, and a `player-entity-id` that is gone).
- **Breaking:** raw Bedrock packet users only.

### 2026-09-16 · [`bbd7690`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/bbd7690) and [`3115779`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/3115779) · CI

Pull requests #3454 and #3486. Changes to the continuous integration of the WIT repository (the first added a workflow that closed pull requests, the second removed it again). No API change.

### 2026-09-04 · [`1ad73ff`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/1ad73ff) · scoreboard number formats

Pull request #41 (and #3228 in the main repository).

- **Added** the `number-format` variant to `scoreboard.wit`: `blank` (hide the number) or `fixed(text-component)` (show this text instead).
- **Changed** `add-objective`, `update-objective` and `update-score`: each gained a trailing `number-format: option<number-format>` parameter. Pass `None` for the old behavior. See [Scoreboards & objectives](./scoreboard/scoreboard.md).
- **Breaking:** yes, for every plugin that calls one of those three functions.

### 2026-08-29 · [`f481f56`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/f481f56) · last revision covered by the previous checkpoint

This is where the book's earlier checkpoint stopped, so it's not an entry in itself. It is listed so you can see where the list above starts.

## Server and SDK changes outside the WIT

Not part of the contract, but they changed how plugins behave or how Rust plugins are written. A few predate the previous checkpoint and are listed here because the book didn't reflect them until now. Newest first.

| Date | Commit | What changed |
|---|---|---|
| 2026-10-22 | `9c04f714b` | **v0.1 plugins run on their own engine.** v0.1 is now loaded on a Wasm engine without concurrency support, v0.2 on a concurrent one, which allowed the move to Wasmtime 50. A v0.1 plugin that imports WASI 0.3 is refused. |
| 2026-10-21 | `8ea2b7d1c` | **GUI and inventory fixes.** Plugin GUIs now include the player's own inventory slots, `Generic9x1` has 9 slots instead of 5 (the other layouts got correct sizes too), and inventory writes from plugins update the right client slot, the held item and any open GUI. |
| 2026-10-18 | `1e5f0ed09` | The server no longer fetches the marketplace key when every plugin is unsigned, which speeds up startup. |
| 2026-10-14 | `5b53f064a` | **v0.2 is opt-in.** The v0.2 host is only built with the `plugin-v0_2` feature, off by default. |
| 2026-10-07 | `5f0a165de` | A **blocking** `BlockDamageAbortEvent` handler no longer crashes the server's handling of the event with `Cannot construct BlockDamageAbortEvent from WASM`. Register it as blocking or non-blocking, either works now. |
| 2026-10-05 | `34a85ae94` | **RCON removed.** The server replaced RCON with the Minecraft server management protocol, which doesn't run commands. The `rcon` command sender type can no longer occur, see [Finding out who it is](./commands/executors.md#finding-out-who-it-is). |
| 2026-10-03 | `a06daf06a` | **Command aliases keep their permission.** An alias of a command whose root has no executor of its own used to skip the command's permission check. Aliases now always inherit it. |
| 2026-10-01 | `1859221e7` | **Crate split.** The server library is now `pumpkin-core`, and `pumpkin` is only the binary. The Wasm host moved into `pumpkin-wasm-host`, `-common`, `-v0_1` and `-v0_2`. No plugin-facing change. |
| 2026-09-27 | `b0371559e` | `ops.json` uses vanilla's `bypassesPlayerLimit` field name and treats a missing `level` as `0`. |
| 2026-09-25 | `a4d6465ed` | Resource handles that a plugin hands back to the server are now properly released. Makes the "this call consumes the handle" rule actually hold. |
| 2026-09-20 | `9bab5ea4f` | **SDK:** `pumpkin_plugin_api::wit` (the raw bindings) is public, which makes `Sound`, `StatusEffectType` and every other type nameable. `JavaPlayer`, `BedrockPlayer` and the version enums are exported from the crate root. |
| 2026-09-14 | `f40c08ca2` | The WIT is now a subtree inside the main repository instead of a submodule, still mirrored to its own repository. |
| 2026-09-08 | `906fbc5af`, `23542ea9d` | Operator level `1` can be loaded again. Position and rotation command arguments are converted according to the argument type that was declared. |
| 2026-09-04 | `4c4cf0668` | **SDK, breaking for Rust:** the server can re-enter a plugin while one of its calls is still running. `on_load`, `on_unload` and `handle_ipc_message` take `&self`, scheduler closures must be `Fn + Send + Sync`, `AiGoal` methods take `&self`. Plugin state needs interior mutability. |
| 2026-09-03 | `8da04492e` | Unloading a plugin now removes its event handlers, cancels its scheduled tasks and switches off its commands. |
| 2026-09-03 | `f8d162769` | Events are now fired from many more places in the server (blocks, entities, projectiles, items, login), so handlers that rarely ran before may start running. |
| 2026-08-30 | `e393751b8` | **New command system.** Built-ins and plugin commands share one tree, and registering an existing name merges into it. |
| 2026-08-24 | `67eaa9140` | **SDK, breaking for Rust:** `TextComponent`, `Command` and `CommandNode` methods take `self` and return `Self`. A bare `x.then(...);` statement moves `x` and no longer works. |

# Plugin API versions

Everything a plugin can ask of the server is defined by one contract, the WIT package `pumpkin:plugin`, and that contract has a version. There are currently two of them side by side, and a few things about how they relate are worth knowing before you build anything long-lived.

## At a glance

| Version | Status | Rust SDK | In short |
|---|---|---|---|
| **v0.1** | Stable, frozen since 2026-09-29 | `pumpkin-plugin-api` | The API this whole book documents. Its WIT no longer changes. |
| **v0.2** | In development, branched 2026-09-29 | none yet | A copy of v0.1 plus GameTest. This is where future breaking changes go. |

> [!NOTE]
> The version of the **`pumpkin-plugin-api` crate** is not the API version. The crate's version follows the server's (`0.2.0+26.3-26.51` at the time of writing), while the API it implements is still **v0.1**. If a tool asks you which plugin API version you target, the answer for any Rust plugin is v0.1.

## What "frozen" means

When v0.2 was branched off (pull request #3766, 2026-09-29), the description said that "v0.1 is kept for stability and backwards compatibility while we make future breaking changes to v0.2 instead". Nothing in the v0.1 WIT has changed since the day of the branch, and everything new lands in the `v0.2` folder. In practice:

- A plugin built against the final v0.1 should keep loading on future servers for as long as they keep shipping the v0.1 host. The server's bug fixes still go into that host, but the contract stays as it is.
- Fixes to behavior, like the ones in the [API changelog](./changelog.md#server-and-sdk-changes-outside-the-wit), do not make a v0.1 plugin stale.

> [!WARNING]
> Frozen only counts from 2026-09-29. v0.1 changed several times in the weeks before, and the WIT type check is structural: a plugin whose idea of a type differs from the server's, even by one new field in one event record, is rejected at load time with an error starting `Plugin was built against a different iteration of the API`. Because every plugin's `handle-event` export mentions the full `event` type, a change to *any* event record breaks *every* plugin built earlier. **Rebuild anything compiled before 2026-09-29** against the final v0.1.

## How the server picks a version

The server reads the version from the plugin itself: the first export named `pumpkin:plugin/metadata@<version>` decides.

- `0.1.x` loads as v0.1, `0.2.x` loads as v0.2. The patch number is ignored. (A plugin built against the WIT stamped `0.2.7` loaded without trouble.)
- Any other version is refused with `Plugin is built against an unsupported version of the API: 0.3.0`.
- A component without that export isn't treated as a plugin at all: `Could not identify the plugin API version`.

Each version has its own host implementation and its own set of interfaces offered to the plugin, so a v0.1 plugin never sees anything of v0.2.

## Can a plugin mix versions?

No. One plugin is one version, from its metadata export to every interface it imports. The server only offers a plugin the interfaces of its own version, so a component that imports something from the other version can't be instantiated and is rejected with the same `different iteration of the API` error. There's no way to use a v0.2 interface from a v0.1 plugin, or the other way round.

What **does** work is running plugins of different versions on the same server. They share the same commands, permissions and events, and they can talk to each other: in a test, a v0.1 plugin and a v0.2 plugin loaded side by side and exchanged [IPC messages](./ipc/inter-plugin-communication.md) in both directions, since the payload is plain bytes. So a v0.2 plugin can depend on a v0.1 plugin's IPC protocol (or the reverse) without either one noticing.

## Which version should you target?

- **Rust:** v0.1, since `pumpkin-plugin-api` implements it and nothing else yet. See [Creating a new plugin](./plugin-101/creating-plugin.md).
- **Other languages:** generate bindings from the WIT folder of the version you want, [`v0.1`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/tree/master/v0.1) unless you specifically need something that only exists in v0.2. Keep the package version in the WIT you generate from (`pumpkin:plugin@0.1.0`) exactly as it is in the repository.
- **Either way:** build in release mode, see [Building and installing](./plugin-101/creating-plugin.md#building-and-installing).

## What v0.2 has that v0.1 doesn't

As of 2026-10-04, only one thing: **GameTest**, an interface for registering automated in-game tests (`gametest`) together with an export the server calls back into (`gametest-callbacks`). The host side is not implemented yet. Every GameTest call currently fails with a "not implemented" error, and a failing host call kills the plugin that made it (see [Returning from an executor](./commands/executors.md#returning-from-an-executor)), so there's nothing to build on yet, and it isn't covered further in this book.

One consequence is already visible: `gametest-callbacks` is part of the v0.2 plugin world, so *every* v0.2 plugin has to export it, whether it uses GameTest or not. It also contains an `async` function, so a toolchain targeting v0.2 needs component-model async support. A v0.2 plugin that leaves it out won't load (and in Rust won't even compile).

Everything else in v0.2 is currently identical to v0.1, down to the last line.

## How this book marks versions

Every API item in this book that has its own heading carries a small badge on the right-hand side of that heading, so you can tell at a glance which version introduced it:

- **since v0.1** appears on everything that existed when v0.1 was frozen, so for now on nearly every API heading.
- **since v0.2** marks something that only exists from v0.2 on.
- **changed in vX**, **deprecated in vX** and **removed in vX** appear next to it when a later version altered, deprecated or removed the item. The text under such a heading says what differs between versions.

Today almost every badge says *since v0.1*, because v0.2 hasn't diverged yet. The badges are there so that the book doesn't have to be restructured the day it does. Pages that are written for a single version will be called out at the top, and a bigger redesign gets its own migration page. The running list of what changed, commit by commit, is the [API changelog](./changelog.md).

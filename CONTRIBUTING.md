# Contributing to PumpkinBook

Thanks for helping build the knowledge base for [Pumpkin](https://pumpkinmc.org) WASM plugins! This project is a [mdBook](https://rust-lang.github.io/mdBook/) site, and its content is licensed under the [MIT License](./LICENSE) — by contributing, you agree that your contributions are licensed the same way.

## Getting set up

1. Install [mdBook](https://rust-lang.github.io/mdBook/guide/installation.html):
   ```sh
   cargo install mdbook
   ```
2. Fork and clone the repo.
3. Preview the site locally with live-reload:
   ```sh
   mdbook serve
   ```
   This serves the book at http://localhost:3000 and rebuilds automatically as you edit files in `src/`.

## Adding or editing a page

- Content lives in `src/` as Markdown files.
- Every page must be listed in [`src/SUMMARY.md`](./src/SUMMARY.md) to show up in the table of contents and be included in the build. If you add a new file and it's not linked there, it won't be published.
- Use nesting in `SUMMARY.md` to place a page under the right chapter/section.
- Don't edit anything under `book/` — it's generated build output and gets overwritten by `mdbook build`.

## Writing guidelines

- Prefer clear, direct explanations over exhaustive prose. Assume the reader knows Rust (or their language of choice) but is new to Pumpkin's WASM plugin APIs.
- Use fenced code blocks with a language tag (` ```rust `, etc.) so syntax highlighting and doctests work correctly.
- Rust examples have to match the real SDK. They can't be run as doctests (they depend on `pumpkin-plugin-api`, which isn't on crates.io, so `mdbook test` can't build them), and CI only runs `mdbook build`, so check them with the tool described under [Checking the Rust examples](#checking-the-rust-examples) below. Use `# ` line prefixes to hide boilerplate (imports, `fn main`) that isn't relevant to the example.
- Link to related pages instead of duplicating explanations.
- Keep terminology consistent with Pumpkin's own docs and source where possible.

## Version tags on headings

The plugin API is versioned (see [Plugin API versions](./src/api-versions.md)), and every heading that documents an API item (a function, method, type, event, permission and so on) carries a tag saying which version it belongs to. The tag is an attribute block at the end of the heading line:

```md
### `.kick(options)` { data-since=0.1 }
```

mdBook renders it as a small badge on the right of the heading. The available attributes, all written without quotes:

| Attribute | Meaning | Badge |
|---|---|---|
| `data-since=0.1` | The WIT version that first had the item. Required on API headings. | *since v0.1* |
| `data-changed=0.2` | A later version changed the item's signature or behavior. | *changed in v0.2* |
| `data-deprecated=0.2` | A later version deprecated it. | *deprecated in v0.2* |
| `data-removed=0.2` | A later version removed it. | *removed in v0.2* |
| `data-status=unimplemented` | It's in the WIT but the host doesn't implement it yet. | *not implemented yet* |

Only one badge besides *since* shows. If a heading has several of the other attributes, the most severe one wins (`removed`, then `deprecated`, then `changed`, then `status`), so explain the details in the text under the heading, usually in a `> [!NOTE]` that says what each version does.

Some rules that come from how mdBook renders headings:

- Write the value without quotes, `data-since=0.1`. With quotes the quote characters become part of the value.
- Never put inline HTML in a heading to get a badge. It changes the generated anchor id and breaks every link to that heading. The attribute block doesn't affect the id.
- Don't tag prose headings ("Putting it together", "How input gets split up"), only headings that document one API item.
- GitHub shows the attribute block as literal text in the heading, the book shows the badge. That's expected.
- The styling is `assets/api-tags.css`, registered as `additional-css` in `book.toml`.

When a later API version changes an existing item: if only the behavior changed, keep one heading, add `data-changed=<version>` and describe both behaviors. If the signature changed, use two headings, the old one with `data-removed=<version>` and the new one with `data-since=<version>`. Anything bigger than a handful of items gets its own migration page. Either way, add an entry to the [API changelog](./src/changelog.md).

## Checking the Rust examples

`tools/check-samples/check_samples.py` extracts every Rust block from `src/` and type-checks it against a real checkout of the Pumpkin repository (it needs the `wasm32-wasip2` target and writes only to a scratch directory). Complete plugins are checked as they are. Fragments are wrapped in a function with a few common variables in scope (`player`, `world`, `server`, and so on), and errors that only say "cannot find value/type" are hidden, since examples often leave out their `use` lines. What it reports is almost always a real mistake: a wrong argument type, a method that doesn't exist, a value used after it moved.

A few reports are expected and can be ignored: examples that deliberately show only part of a plugin (a bare `impl Plugin` without `metadata`), and blocks that rely on a variable whose type the tool guessed differently than the prose does.

## Checking claims against the source

The book describes behavior, not just signatures, and the WIT overstates what the server implements. Before documenting something, check the host implementation, `crates/pumpkin-wasm-host-v0_1/src` in the Pumpkin repository (the API is frozen, so that is the one that matters), and look for stubs and error returns. Where it's cheap, run a small plugin against a real server instead of trusting a reading of the code.

## Submitting changes

1. Create a branch for your change.
2. Verify the site builds cleanly, and that the Rust examples still compile:
   ```sh
   mdbook build
   python3 tools/check-samples/check_samples.py --pumpkin /path/to/Pumpkin
   ```
3. Open a pull request against `master` describing what you added or changed and why.
4. Small fixes (typos, broken links, clarifications) are welcome without prior discussion. For larger additions (new chapters, restructuring), consider opening an issue first to align on scope.

## Reporting issues

Found something inaccurate, outdated, or confusing? Open an issue on [GitHub](https://github.com/vyPal/PumpkinBook/issues) — even if you don't have time to fix it yourself, flagging it helps.

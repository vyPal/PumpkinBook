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
- Rust code blocks are run as doctests via `mdbook test` — make sure examples actually compile. Use `# ` line prefixes to hide boilerplate (imports, `fn main`) that isn't relevant to the example.
- Link to related pages instead of duplicating explanations.
- Keep terminology consistent with Pumpkin's own docs and source where possible.

## Submitting changes

1. Create a branch for your change.
2. Verify the site builds cleanly:
   ```sh
   mdbook build
   mdbook test
   ```
3. Open a pull request against `master` describing what you added or changed and why.
4. Small fixes (typos, broken links, clarifications) are welcome without prior discussion. For larger additions (new chapters, restructuring), consider opening an issue first to align on scope.

## Reporting issues

Found something inaccurate, outdated, or confusing? Open an issue on [GitHub](https://github.com/vyPal/PumpkinBook/issues) — even if you don't have time to fix it yourself, flagging it helps.

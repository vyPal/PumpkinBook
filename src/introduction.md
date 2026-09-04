# Introduction

This website serves as a knowledge base for any information related to _WASM_ plugins built for the [Pumpkin](https://pumpkinmc.org) Minecraft server software.

Since these plugins are compiled to WASM, they can be written in many languages. The programming language of choice for this website will be Rust, but the general principles and APIs can be used in the same way in other languages as well.

For a list of supported languages and basic instructions on how to get started with them, please check out the [Pumpkin Plugin Development guide](https://docs.pumpkinmc.org/plugin-dev/introduction) on the official website.

## Source commits this book is verified against

Since the plugin API is under active development, every claim in this book is checked directly against the source rather than assumed, see the [Pumpkin](https://github.com/Pumpkin-MC/Pumpkin) and [pumpkin-plugin-wit](https://github.com/Pumpkin-MC/pumpkin-plugin-wit) repositories. This book was last brought up to date against:

- `Pumpkin` (main repo): [`c7d4c08d9`](https://github.com/Pumpkin-MC/Pumpkin/commit/c7d4c08d9d740b79cad7a435849832022a3bf4a6) (2026-09-03)
- `pumpkin-plugin-wit`: [`f481f5677`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/f481f5677dd0c36788288378b7b1f650ed2266e9) (2026-08-29)

The previous checkpoint, for reference, was `Pumpkin` [`14337d528`](https://github.com/Pumpkin-MC/Pumpkin/commit/14337d5285ce712d1a8603bdc1defac3f8ab300d) / `pumpkin-plugin-wit` [`54f158f10`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/commit/54f158f102bdc7f1131451664b86cfd041033afb) (both 2026-08-16/17). If you're reading this well after the date above, treat anything not covered here as unverified, and check the WIT source directly, `git diff` between the pinned commit and current `master` is the fastest way to see what moved.

## Contributing

Contributions are always welcome. The contents of this website are written in the markdown language and hosted publicly on [GitHub](https://github.com/vyPal/PumpkinBook). Before contributing, please make sure to review the [Contribution guidelines](https://github.com/vyPal/PumpkinBook/blob/master/CONTRIBUTING.md).

## Licence

This project is licensed under the [MIT License](https://github.com/vyPal/PumpkinBook/blob/master/LICENSE).

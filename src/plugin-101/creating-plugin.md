# Creating a new plugin

> [!NOTE]
> This quick guide is a extension of the official [tutorial for creating a new plugin **in rust**](https://docs.pumpkinmc.org/plugin-dev/rust/creating-project). To create a new plugin in another language, see [the official plugin development guide](https://docs.pumpkinmc.org/plugin-dev/introduction), or if your language is not listed there but has support for WASM compilation, you can generate bindings for our [wit interface](https://github.com/Pumpkin-MC/pumpkin-plugin-wit)

## Installing the toolchain

Since we are going to be compiling our plugin to Web Assembly (WASM for short), we need to make sure that the rust compiler knows how to compile to the `wasm32-wasip2` target[^wasi].

[^wasi]: The Pumpkin Plugin API currently uses v2 of the Web Assembly System Interface (WASI). This version has many limitation that we will talk about later in the knowledge base. At the time of writing, WASI version 3 (`wasip3`) has been approved by the WASM Foundation, but does not yet have mainstream compilation support. Once the rust compiler has support for this target, Pumpkin will switch to using `wasip3`

To install the toolchain, simply run this command in your terminal (requires [rustup](https://rustup.rs/) to be installed):

```bash
rustup target add wasm32-wasip2
```

## Creating a new rust project

Before we can actually start writing our plugin, we must first initialize a new cargo project and prepare it for WASM compilation.

To create a new project with the basic library template, simply run this command:

```bash
cargo new <project-name> --lib
```

This will create most of the necessary files for our project, but we still need to tell the compiler that we will be using the `wasm32-wasip2` target that we installed. To do that, first create the `.cargo/` directory in the new project, then inside it create a new file named `config.toml` and put this inside:

```toml
[build]
target = "wasm32-wasip2"
```

After you have completed both these steps, you will be left with a directory layout looking roughly like this:

```
├── .cargo/
│   └── config.toml
├── src/
│   └── lib.rs
├── Cargo.toml
└── Cargo.lock
```

## Configuring project

Since Pumpkin plugins are loaded at runtime as dynamic libraries, we need to tell Cargo to build this crate as one. Modify your `Cargo.toml` file to look like this:

```toml
[package]
name = "hello-pumpkin-wasm"
version = "0.1.0"
edition = "2024"

[lib]
crate-type = ["cdylib"]

[dependencies]
```

Next we need to add some basic dependencies. Since Pumpkin is still in early development, the internal crates aren't published to crates.io, so we need to tell Cargo to download the dependencies directly from GitHub.

```toml
[package]
name = "hello-pumpkin"
version = "0.1.0"
edition = "2024"

[lib]
crate-type = ["cdylib"]

[dependencies]
# This is the api crate that makes creating plugins easier, and has wit definitions
pumpkin-plugin-api = { version = "0.1.0", git = "https://github.com/Pumpkin-MC/Pumpkin", package = "pumpkin-plugin-api" }
tracing = "0.1"
```

For improved performance and smaller file sizes, we recommend enabling Link-Time Optimization (LTO). Be aware that this will increase compilation time.

```toml [Cargo.toml]
[profile.release]
lto = true
```

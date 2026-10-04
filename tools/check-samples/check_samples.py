#!/usr/bin/env python3
"""Compile-check the Rust examples in the book against a real pumpkin-plugin-api checkout.

CI only runs `mdbook build`, so nothing else stops an example from drifting away from the
SDK. This script pulls every ```rust block out of src/**/*.md and type-checks it:

  * blocks that contain `register_plugin!` are complete plugins and are checked one crate each,
  * every other block is wrapped in a module (item-level blocks) or a function (statement-level
    blocks, with a handful of common free variables like `player` and `world` in scope), and
    all of them are checked together in one crate.

It is deliberately forgiving. Blocks with unbalanced brackets or syntax errors are skipped,
and errors that only say "cannot find value/type ..." are hidden, because many examples leave
out their `use` lines or refer to variables the surrounding prose introduced. What is left
(wrong argument types, missing methods, moved values, wrong arity) is almost always a real
mistake in the book.

Usage:
    python3 tools/check-samples/check_samples.py --pumpkin ~/Documents/GitHub/Pumpkin

Needs the `wasm32-wasip2` rust target (`rustup target add wasm32-wasip2`) and network access
for crates.io on the first run. Everything is written to a scratch directory
(`$TMPDIR/pumpkinbook-check-samples` by default), never into the book or the Pumpkin checkout.
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import tempfile

BOOK_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src")

ITEM_START = re.compile(r"^\s*(pub\s+)?(fn|impl|struct|enum|trait|const|static|type|mod|use|register_plugin!|#\[|extern|unsafe)\b")
STATEMENT_START = re.compile(r"(let|if|for|match|while|[a-z_]+\.|[a-z_]+\()")
USE_STMT = re.compile(r"^[ \t]*use [^;]*;[ \t]*\n?", re.M)
NOISE = re.compile(
    r"cannot find (value|type|struct|trait|function|macro|module or crate)|`self` parameter|"
    r"unresolved import `(serde|toml)`|use of undeclared type|use of unresolved module|"
    r"expected value, found module `self`"
)

# Names most examples assume to be in scope. Adjust when the SDK's public paths move.
PRELUDE = """
#[allow(ambiguous_glob_reexports, unused_imports)]
pub mod prelude {
    pub use pumpkin_plugin_api::{Player, World, Server, Entity, Mob, LivingEntity, ItemStack, Context, Plugin, PluginMetadata, Result};
    pub use pumpkin_plugin_api::text::TextComponent;
    pub use pumpkin_plugin_api::command::{Arg, ArgumentType, Command, CommandError, CommandNode, CommandSender, ConsumedArgs, StringType};
    pub use pumpkin_plugin_api::command_wit::Number;
    pub use pumpkin_plugin_api::commands::CommandHandler;
    pub use pumpkin_plugin_api::common::{NamedColor, RgbColor};
    pub use pumpkin_plugin_api::permission::{Permission, PermissionDefault, PermissionLevel};
    pub use pumpkin_plugin_api::events::{EventPriority, EventData};
    pub use pumpkin_plugin_api::EventHandler;
    pub use pumpkin_plugin_api::scoreboard::{DisplaySlot, RenderType, Scoreboard};
    pub use pumpkin_plugin_api::server::Difficulty;
    pub use pumpkin_plugin_api::{JavaPlayer, BedrockPlayer, EntityType, GameRule, GameRuleValue, Item, Inventory, PlayerInventory, TeamSettings};
    pub use pumpkin_plugin_api::world::{BuiltinAiGoal, SoundCategory};
    pub use pumpkin_plugin_api::gui::Gui;
    pub use pumpkin_plugin_api::recipe::RecipeManager;
    pub use pumpkin_plugin_api::common::BlockPos;
    pub use pumpkin_plugin_api::display::{DisplayEntity, TextDisplayEntity};
    pub use pumpkin_plugin_api::command_wit::GameMode;
    pub use std::sync::{Arc, Mutex, RwLock};
}
"""

# Free variables available inside statement-level blocks.
PARAMS = (
    "player: &Player, target: &Player, world: &World, server: &Server, entity: &Entity, mob: &Mob, "
    "living: &LivingEntity, item: &ItemStack, context: &Context, sender: &CommandSender, args: &ConsumedArgs, "
    "sword: &ItemStack, java_player: &JavaPlayer, bedrock_player: &BedrockPlayer, menu: &Gui, "
    "manager: &RecipeManager, position: (f64, f64, f64), zombie: &Entity, pos: BlockPos, "
    "scoreboard: &Scoreboard, settings: TeamSettings, display: &DisplayEntity, "
    "text_display: &TextDisplayEntity, speed: Number"
)


def balanced(code):
    t = re.sub(r"//[^\n]*", "", code)
    t = re.sub(r'"(\\.|[^"\\])*"', '""', t)
    t = re.sub(r"'(\\.|[^'\\])'", "''", t)
    return all(t.count(a) == t.count(b) for a, b in ("{}", "()", "[]"))


def extract_blocks(only):
    blocks = []
    for f in sorted(glob.glob(os.path.join(BOOK_SRC, "**", "*.md"), recursive=True)):
        rel = os.path.relpath(f, BOOK_SRC)
        if only and not any(o in rel for o in only):
            continue
        text = open(f).read()
        for m in re.finditer(r"```rust\n(.*?)```", text, re.S):
            code = "\n".join(l[2:] if l.startswith("# ") else l for l in m.group(1).split("\n"))
            blocks.append((rel, text[: m.start()].count("\n") + 2, code))
    return blocks


def write_cargo(workdir, pumpkin, members=None, name="bookcheck", lib=False):
    dep = f'pumpkin-plugin-api = {{ path = "{pumpkin}/crates/pumpkin-plugin-api" }}\ntracing = "0.1"\n'
    os.makedirs(os.path.join(workdir, ".cargo"), exist_ok=True)
    with open(os.path.join(workdir, ".cargo", "config.toml"), "w") as fh:
        fh.write('[build]\ntarget = "wasm32-wasip2"\n')
    if members is None:
        with open(os.path.join(workdir, "Cargo.toml"), "w") as fh:
            fh.write(f'[package]\nname = "{name}"\nversion = "0.1.0"\nedition = "2024"\n[dependencies]\n{dep}[workspace]\n')
    else:
        with open(os.path.join(workdir, "Cargo.toml"), "w") as fh:
            fh.write('[workspace]\nresolver = "2"\nmembers = [' + ",".join(f'"{m}"' for m in members) + "]\n")


def generate_fragments(blocks, skip):
    out = ["#![allow(unused, dead_code, unused_mut, unused_variables, unused_imports, unreachable_code)]\n", PRELUDE]
    skipped = []
    for n, (rel, line, code) in enumerate(blocks):
        key = f"{rel}:{line}"
        if "register_plugin!" in code:
            continue
        if not balanced(code) or key in skip:
            skipped.append(key)
            continue
        uses = "".join(m.group(0) for m in USE_STMT.finditer(code))
        rest = USE_STMT.sub("", code)
        lines = [l for l in rest.split("\n") if l.strip() and not l.strip().startswith("//")]
        item_level = bool(lines) and bool(ITEM_START.match(lines[0])) and not any(STATEMENT_START.match(l) for l in lines)
        out.append(f"\n// ==== BLOCK {n} {key}\n")
        if item_level:
            out.append(f"mod b{n} {{\n#[allow(unused_imports)] use super::prelude::*;\n{code}\n}}\n")
        else:
            out.append(
                f"mod b{n} {{\n#[allow(unused_imports)] use super::prelude::*;\n{uses}\n"
                f"pub fn __f({PARAMS}) {{\n let _r = (|| -> Result<(), String> {{\n{rest}\n ; Ok(()) }})();\n}}\n}}\n"
            )
    return "".join(out), skipped


def cargo_check(workdir):
    return subprocess.run(["cargo", "check", "--message-format=short"], cwd=workdir, capture_output=True, text=True)


def block_for_line(src, ln):
    i = ln - 1
    while i >= 0 and not src[i].startswith("// ==== BLOCK"):
        i -= 1
    return src[i].split()[-1] if i >= 0 else "PRELUDE"


def check_fragments(workdir, pumpkin, only):
    blocks = extract_blocks(only)
    write_cargo(workdir, pumpkin)
    os.makedirs(os.path.join(workdir, "src"), exist_ok=True)
    skip = set()
    skipped = []
    for _ in range(20):
        code, skipped = generate_fragments(blocks, skip)
        with open(os.path.join(workdir, "src", "lib.rs"), "w") as fh:
            fh.write(code)
        res = cargo_check(workdir)
        src = code.split("\n")
        syntax = []
        for l in res.stderr.split("\n"):
            m = re.match(r"src/lib.rs:(\d+):\d+: error: (expected|unexpected|mismatched|unclosed|this file contains)", l)
            if m:
                syntax.append(int(m.group(1)))
        if not syntax:
            break
        for ln in syntax:
            skip.add(block_for_line(src, ln))
    real = []
    for l in res.stderr.split("\n"):
        m = re.match(r"src/lib.rs:(\d+):(\d+): error(\[E\d+\])?: (.*)", l)
        if not m or NOISE.search(m.group(4)):
            continue
        ln = int(m.group(1))
        real.append((block_for_line(src, ln), m.group(3) or "", m.group(4)[:170], src[ln - 1].strip()[:100]))
    return len(blocks), sorted(set(skipped) | skip), real


def check_full_plugins(workdir, pumpkin, only):
    blocks = [b for b in extract_blocks(only) if "register_plugin!" in b[2]]
    members = []
    for i, (rel, line, code) in enumerate(blocks):
        name = f"plugin{i}"
        os.makedirs(os.path.join(workdir, name, "src"), exist_ok=True)
        with open(os.path.join(workdir, name, "Cargo.toml"), "w") as fh:
            fh.write(
                f'[package]\nname = "{name}"\nversion = "0.1.0"\nedition = "2024"\n[lib]\ncrate-type = ["cdylib"]\n'
                f'[dependencies]\npumpkin-plugin-api = {{ path = "{pumpkin}/crates/pumpkin-plugin-api" }}\ntracing = "0.1"\n'
            )
        with open(os.path.join(workdir, name, "src", "lib.rs"), "w") as fh:
            fh.write(code)
        with open(os.path.join(workdir, name, "WHERE"), "w") as fh:
            fh.write(f"{rel}:{line}\n")
        members.append(name)
    if not members:
        return 0, ""
    write_cargo(workdir, pumpkin, members=members)
    res = subprocess.run(["cargo", "check", "--message-format=short"], cwd=workdir, capture_output=True, text=True)
    errors = [l for l in res.stderr.split("\n") if ": error" in l or l.startswith("error")]
    where = {m: open(os.path.join(workdir, m, "WHERE")).read().strip() for m in members}
    pretty = "\n".join(re.sub(r"^(plugin\d+)/", lambda m: f"{where[m.group(1)]} ({m.group(1)})/", l) for l in errors)
    return len(members), pretty


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pumpkin", required=True, help="path to a Pumpkin checkout")
    ap.add_argument("--workdir", default=os.path.join(tempfile.gettempdir(), "pumpkinbook-check-samples"))
    ap.add_argument("--only", nargs="*", default=[], help="only check pages whose path contains one of these")
    args = ap.parse_args()
    pumpkin = os.path.abspath(os.path.expanduser(args.pumpkin))
    if not os.path.isdir(os.path.join(pumpkin, "crates", "pumpkin-plugin-api")):
        sys.exit(f"{pumpkin} does not look like a Pumpkin checkout")

    n_plugins, plugin_errors = check_full_plugins(os.path.join(args.workdir, "full"), pumpkin, args.only)
    print(f"== complete plugins: {n_plugins} checked")
    print(plugin_errors or "   no errors")

    total, skipped, real = check_fragments(os.path.join(args.workdir, "fragments"), pumpkin, args.only)
    print(f"\n== fragments: {total} blocks, {len(skipped)} skipped (unbalanced or syntax errors)")
    for s in skipped:
        print(f"   skipped {s}")
    print(f"\n== likely real errors: {len(real)}")
    for loc, code, msg, line in real:
        print(f"{loc} {code} {msg} | {line}")
    sys.exit(1 if real or plugin_errors else 0)


if __name__ == "__main__":
    main()

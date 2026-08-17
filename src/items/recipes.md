# Custom recipes

Register shaped, shapeless, and cooking (furnace/blast furnace/smoker/campfire) recipes through the `RecipeManager`, reached via `context.get_recipe_manager()` or `server.get_recipe_manager()`. The three builders below are the intended way to build one, they validate their own shape and produce a clear `RecipeError` instead of a confusing host-side failure.

## Ingredients

Every recipe slot takes an `Ingredient`, which is one of:

- `Ingredient::item("diamond")`, a specific item. No namespace needed, `"minecraft:"` is prepended automatically if you don't include one.
- `Ingredient::tag("logs")`, a tag group (matches any item in that tag). A leading `#` is stripped if present, so `"#logs"` and `"logs"` are equivalent.
- `Ingredient::one_of(["coal", "charcoal"])`, any one of several specific items.

You rarely need to call these directly, everywhere a builder takes `impl Into<Ingredient>`, a plain `&str` or `String` converts automatically (a leading `#` is enough to make it a tag).

## Shaped recipes

### `ShapedRecipeBuilder::new(id, output)`

Builds a crafting-grid-shaped recipe (up to 3x3).

```rust
use pumpkin_plugin_api::{recipe::{RecipeCategory, ShapedRecipeBuilder}, ItemStack};

fn register_recipes(server: &Server) {
  let manager = server.get_recipe_manager();

  manager.register(
    ShapedRecipeBuilder::new("my_plugin:super_sword", ItemStack::new("minecraft:diamond_sword", 1))
      .pattern([
        " D ",
        " D ",
        " S ",
      ])
      .key('D', "minecraft:diamond_block")
      .key('S', "minecraft:stick")
      .category(RecipeCategory::Equipment)
      .group("swords")
      .show_notification(true)
  ).expect("failed to register shaped recipe");
}
```

`.pattern(rows)` (or its alias `.shape(rows)`) sets the whole grid at once, `.row(row)` appends one row at a time if you'd rather build it incrementally. `.key(symbol, ingredient)` maps a pattern character to what it should match, spaces are always empty regardless of key mappings. `.group(...)` groups recipes together in the recipe book, `.category(...)` picks which recipe-book tab it shows under, and `.show_notification(bool)` controls the toast when a player unlocks it.

## Shapeless recipes

### `ShapelessRecipeBuilder::new(id, output)`

Same idea, but order and position in the grid don't matter, just which ingredients are present.

```rust
use pumpkin_plugin_api::recipe::{RecipeCategory, ShapelessRecipeBuilder};

manager.register(
  ShapelessRecipeBuilder::new("my_plugin:flint_from_gravel", ItemStack::new("minecraft:flint", 1))
    .ingredient_count("minecraft:gravel", 3)
    .category(RecipeCategory::Misc)
).expect("failed to register shapeless recipe");
```

`.ingredient(ing)` adds one, `.ingredient_count(ing, n)` adds the same ingredient `n` times, and `.ingredients([...])` adds several at once. Up to 9 total.

## Cooking recipes

### `CookingRecipeBuilder::smelting/blasting/smoking/campfire(id, ingredient, output)`

One constructor per cooking station, each with a sensible default cooking time (200 ticks for smelting, 100 for blasting/smoking, 600 for campfire), overridable with `.cooking_time(ticks)`.

```rust
use pumpkin_plugin_api::recipe::{CookingRecipeBuilder, RecipeCategory};

manager.register(
  CookingRecipeBuilder::smelting(
    "my_plugin:fast_iron",
    "minecraft:raw_iron",
    ItemStack::new("minecraft:iron_ingot", 1),
  )
  .cooking_time(100)
  .experience(0.7)
  .category(RecipeCategory::Misc)
).expect("failed to register smelting recipe");
```

`.experience(xp)` sets how much experience the player gets for collecting the cooked output.

## Registering

`manager.register(builder)` works for all three builder types (it's generic over a `RegistrableRecipe` trait each of them implements), and validates before registering, `RecipeError` covers empty ids, empty/oversized patterns, mismatched row widths, unmapped pattern characters, empty/oversized ingredient lists, and a missing cooking input.

`Context`, `Server`, and `RecipeManager` all also expose the same thing under more specific names (`register_shaped_recipe`, `register_shapeless_recipe`, `register_cooking_recipe`) if you'd rather call it on whichever handle you already have instead of fetching the manager first, they all end up doing the same validation and registration.

## Putting it together

Registering a small recipe pack in `on_load`, one of each kind:

```rust
use pumpkin_plugin_api::{
  recipe::{CookingRecipeBuilder, RecipeCategory, ShapedRecipeBuilder, ShapelessRecipeBuilder},
  Context, ItemStack, Result,
};

fn on_load(&mut self, context: Context) -> Result<()> {
  context.register_shaped_recipe(
    ShapedRecipeBuilder::new("my_plugin:ruby_pickaxe", ItemStack::new("minecraft:diamond_pickaxe", 1))
      .pattern(["RRR", " S ", " S "])
      .key('R', "my_plugin:ruby")
      .key('S', "minecraft:stick")
      .category(RecipeCategory::Equipment)
  ).map_err(|e| e.to_string())?;

  context.register_shapeless_recipe(
    ShapelessRecipeBuilder::new("my_plugin:ruby_from_shards", ItemStack::new("my_plugin:ruby", 1))
      .ingredient_count("my_plugin:ruby_shard", 4)
      .category(RecipeCategory::Misc)
  ).map_err(|e| e.to_string())?;

  context.register_cooking_recipe(
    CookingRecipeBuilder::smelting("my_plugin:ruby_shard_from_ore", "my_plugin:ruby_ore", ItemStack::new("my_plugin:ruby_shard", 1))
      .experience(1.0)
  ).map_err(|e| e.to_string())?;

  Ok(())
}
```

# Display entities

Block, item, and text display entities are the invisible-hitbox, no-AI entities Minecraft uses for floating holograms, model showcases, and decorative blocks/items, along with a related "interaction" entity for giving an invisible hitbox its own click handling. All four are regular `Entity`s underneath, spawned the normal way and then viewed through a more specific resource.

## Getting a display handle

Spawn one like any other entity, then downcast it with the `EntityDisplayExt` trait:

```rust
use pumpkin_plugin_api::{EntityDisplayExt, EntityType};

let entity = world.spawn_entity(EntityType::TextDisplay, position);
let Some(text_display) = entity.as_text_display() else {
  return; // wasn't actually a text display entity
};
```

`as_display()`, `as_block_display()`, `as_item_display()`, `as_text_display()`, and `as_interaction()` each return `None` if the entity isn't actually that kind, this is how you'd handle an `Entity` from `world.get_entities()` or an event without already knowing its concrete type. Every specific resource also has `.get_entity()` to go back the other way.

## Shared display properties

Every display entity (block, item, or text) also has a base `DisplayEntity` view, reachable via `.as_display()` or a specific display resource's `.get_display()`, covering the properties they all share:

### `.get_transformation()` / `.set_transformation(transformation)` { data-since=0.1 }

A `DisplayTransformation` (translation, scale, and left/right rotation quaternions). Building one field-by-field is tedious, use `TransformationBuilder` instead:

```rust
use pumpkin_plugin_api::TransformationBuilder;

let transform = TransformationBuilder::new()
  .translation(0.0, 1.0, 0.0)
  .uniform_scale(1.5)
  .build();

display.set_transformation(transform);
```

Or skip the builder entirely for the common case of just moving/resizing, `DisplayEntityExt` adds `.set_translation(x, y, z)` and `.set_scale(x, y, z)` directly on `DisplayEntity`, each reading the current transformation, updating just that part, and writing it back.

### `.get_interpolation_duration()` / `.set_interpolation_duration(duration)` / `.get_interpolation_start()` / `.set_interpolation_start(delta_ticks)` { data-since=0.1 }

Controls smooth client-side animation between transformation changes, `interpolation_duration` is how many ticks a change takes to visually complete, rather than snapping instantly.

### `.get_teleport_duration()` / `.set_teleport_duration(duration)` { data-since=0.1 }

Same idea, but for position changes (smoothly gliding to a new position instead of teleporting instantly).

### `.get_billboard()` / `.set_billboard(mode)` { data-since=0.1 }

A `BillboardMode` controlling how the display faces the camera: `Fixed` (doesn't rotate), `Vertical`, `Horizontal`, or `Center` (always fully faces the viewer, like a vanilla text display's default).

### `.get_view_range()` / `.set_view_range(range)` { data-since=0.1 }

How far away (as a multiplier of the default render distance) the display stays visible.

### `.get_shadow_radius()` / `.set_shadow_radius(radius)` / `.get_shadow_strength()` / `.set_shadow_strength(strength)` { data-since=0.1 }

The size and darkness of the entity's ground shadow, `0.0` radius removes the shadow entirely.

### `.get_display_width()` / `.set_display_width(width)` / `.get_display_height()` / `.set_display_height(height)` { data-since=0.1 }

Overrides the bounding box used for culling (deciding whether the client bothers rendering it at all), independent of the transformation's scale.

### `.get_glow_color_override()` / `.set_glow_color_override(color)` / `.get_brightness()` / `.set_brightness(brightness)` { data-since=0.1 }

A packed color overriding the glow outline color (when the entity is glowing), and a light-level override so the display doesn't dim in dark areas.

## Block displays

### `.get_block_state_id()` / `.set_block_state_id(state_id)` { data-since=0.1 }

The single block state this entity renders, as the same raw numeric id used by `World::get_block_state_id`/`set_block_state`.

## Item displays

### `.get_item()` / `.set_item(item)` { data-since=0.1 }

The `ItemStack` shown, or `None` for nothing. `ItemDisplayEntityExt` adds `.set_item_stack(item)` as a slightly friendlier-named alias for the same call.

### `.get_item_display_mode()` / `.set_item_display_mode(mode)` { data-since=0.1 }

An `ItemDisplayMode` matching the perspectives vanilla items render in (`Gui`, `Ground`, `Head`, `Fixed`, `ThirdpersonLefthand`/`ThirdpersonRighthand`, `FirstpersonLefthand`/`FirstpersonRighthand`), changes the item's pose (a sword lying flat for `Ground` vs standing for `Fixed`, for example).

## Text displays

### `.get_text()` / `.set_text(text)` { data-since=0.1 }

The displayed `TextComponent`. `TextDisplayEntityExt` adds `.set_plain_text(&str)` as a shortcut when you don't need any formatting.

```rust
use pumpkin_plugin_api::TextDisplayEntityExt;

text_display.set_plain_text("Guild Hall");
```

### `.get_line_width()` / `.set_line_width(width)` { data-since=0.1 }

The pixel width text wraps at.

### `.get_background()` / `.set_background(color)` / `.get_default_background()` / `.set_default_background(default_background)` { data-since=0.1 }

A packed ARGB background color, or fall back to the client's default translucent background with `default_background`.

### `.get_text_opacity()` / `.set_text_opacity(opacity)` { data-since=0.1 }

Text transparency, `-1` (full opacity) down toward `0`.

### `.get_shadow()` / `.set_shadow(shadow)` { data-since=0.1 }

Whether the text has a drop shadow.

### `.get_see_through()` / `.set_see_through(see_through)` { data-since=0.1 }

Whether the text renders through blocks (like a vanilla "see through walls" text display).

### `.get_alignment()` / `.set_alignment(alignment)` { data-since=0.1 }

A `TextAlignment` of `Center`, `Left`, or `Right`, for multi-line text.

## Interaction entities

A special invisible-model entity that only exists to catch clicks, no rendering, no display properties.

### `.get_width()` / `.set_width(width)` / `.get_height()` / `.set_height(height)` { data-since=0.1 }

The size of its (invisible) interactable hitbox.

### `.get_response()` / `.set_response(response)` { data-since=0.1 }

Whether interacting with it produces the normal client-side hit feedback (arm swing, hit particle).

### `.get_last_attacker()` / `.get_last_interaction()` { data-since=0.1 }

The UUID of the last player to attack it or right-click it, `None` if it hasn't happened yet. Combine with an interaction event handler if you need to react immediately rather than polling.

## Putting it together

A floating nameplate above a shop stall, positioned slightly above the counter and always facing whoever's looking at it:

```rust
use pumpkin_plugin_api::{world::World, BillboardMode, EntityDisplayExt, EntityType, TextDisplayEntityExt};

fn place_shop_sign(world: &World, counter_pos: (f64, f64, f64)) {
  let (x, y, z) = counter_pos;
  let entity = world.spawn_entity(EntityType::TextDisplay, (x, y + 1.5, z));

  let Some(sign) = entity.as_text_display() else {
    return;
  };

  sign.set_plain_text("Bob's General Store");
  let display = sign.get_display();
  display.set_billboard(BillboardMode::Center);
}
```

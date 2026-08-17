# Java & Bedrock specifics

Pumpkin serves both Java and Bedrock Edition clients through the same `Player` resource for everything covered so far, but each platform also has its own handle for platform-exclusive features: `player.as_java()` and `player.as_bedrock()`, each returning `Option<JavaPlayer>`/`Option<BedrockPlayer>` (`None` if the player is connected via the other platform).

```rust
if let Some(java) = player.as_java() {
  // Java-only features
}

if let Some(bedrock) = player.as_bedrock() {
  // Bedrock-only features
}
```

## Java-specific

### `.get_version()` / `.get_brand()` / `.get_server_address()`

The player's Java protocol version, client brand string (`"vanilla"`, `"fabric"`, and so on, self-reported by the client), and the address they used to connect (useful behind a proxy or for virtual-host-based routing).

### `.get_settings()`

A `JavaPlayerSettings` snapshot: `locale`, `view_distance`, `chat_mode` (a `ChatMode`), `chat_colors`, `skin_parts`, and more, this is the client-reported settings panel, distinct from the server-controlled skin/visibility APIs on `Player` itself.

### `.send_packet(packet)` / `.send_custom_payload(channel, data)`

`send_packet` sends a fully-typed Java clientbound packet, see [Raw packets](../advanced/raw-packets.md). `send_custom_payload` sends a plugin-message-style payload on a named channel, the same mechanism Bukkit/Spigot plugin messaging channels use, for talking to a matching client-side mod or another server-side integration that listens on that channel.

### `.show_dialog(dialog)` / `.clear_dialog()`

See [Java dialogs](../ui/java-dialogs.md).

### `.get_scoreboard()` / `.reset_scoreboard()`

A per-player Java scoreboard override, distinct from the world's shared scoreboard (see [Scoreboards & objectives](../scoreboard/scoreboard.md)), lets you show this one player a different sidebar/objectives than everyone else. `reset_scoreboard` reverts back to the world's shared one.

### `.send_resource_pack(pack)` / `.remove_resource_pack(id)` / `.clear_resource_packs()`

Sends a `JavaResourcePack` (`id`, `url`, `hash`, `forced`, an optional prompt message), removes one by id, or clears every custom pack sent this session.

### `.kick(options)`

A `JavaKickOptions` (`reason` as a `TextComponent`, `log_to_console`, a `teardown_policy` controlling how gracefully the connection closes).

## Bedrock-specific

### `.get_version()` / `.get_settings()`

The player's Bedrock protocol version, and a much larger `BedrockPlayerSettings` snapshot covering device info (`device_os`, `device_id`, `device_model`), input mode, UI profile, GUI scale, memory tier, graphics mode, and skin metadata (persona/premium/trusted flags, skin id, arm size).

> [!NOTE]
> `get_settings()` can fail (trapping the call) with a "client data not available" error if called before the Bedrock client's initial handshake data has fully arrived, this is mostly a concern right at connection time, calling it from a `PlayerJoinEvent` handler or later should be safe.

### `.get_ability(ability)` / `.set_ability(ability, value)`

Reads or sets one of the Bedrock-only `BedrockAbility` flags (`Build`, `Mine`, `DoorsAndSwitches`, `OpenContainers`, `AttackPlayers`, `AttackMobs`, `OperatorCommands`, `Teleport`, `Invulnerable`, `Flying`, `MayFly`, `Instabuild`, `NoClip`, and more), a finer-grained permission set than Java's `PlayerAbilities`.

### `.get_status_flag(flag)` / `.set_status_flag(flag, value)`

Reads or sets a Bedrock-only `BedrockStatusFlag`, client-side rendering/behavior flags (there are well over a hundred, covering things like `Sneaking`, `Sprinting`, `OnFire`, `Sleeping`, `Gliding`, and many mob-specific ones). Setting one manually triggers the corresponding visual state client-side without necessarily changing the underlying game state, useful for cosmetic effects.

### `.send_packet(packet)`

The Bedrock equivalent of `JavaPlayer::send_packet`, see [Raw packets](../advanced/raw-packets.md).

### `.open_form(form)`

See [Bedrock forms](../ui/forms.md).

### `.get_scoreboard()` / `.reset_scoreboard()`

The Bedrock equivalent of the Java per-player scoreboard override, returning a `BedrockScoreboard` instead (see [Scoreboards & objectives](../scoreboard/scoreboard.md)).

### `.send_resource_packs_info(info)`

Sends a `BedrockResourcePacksInfo` (whether packs are required, addon-pack/script flags, and the list of `BedrockResourcePackEntry` packs to offer).

### `.kick(options)`

A `BedrockKickOptions` (a protocol-level `BedrockDisconnectReason`, a display message, a flag to suppress showing that message, a separately-filtered message for parental controls, and `log_to_console`).

## Putting it together

Greeting a player differently depending on which platform they connected from:

```rust
use pumpkin_plugin_api::{events::{EventData, PlayerJoinEvent}, text::TextComponent};

fn handle(&self, _server: Server, event: EventData<PlayerJoinEvent>) -> EventData<PlayerJoinEvent> {
  let player = &event.player;

  if let Some(java) = player.as_java() {
    let brand = java.get_brand();
    tracing::info!("{} joined via Java Edition, client: {brand}", player.get_name());
  } else if let Some(bedrock) = player.as_bedrock() {
    let settings = bedrock.get_settings();
    tracing::info!("{} joined via Bedrock Edition on {}", player.get_name(), settings.device_model);
  }

  event
}
```

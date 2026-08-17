# Raw packets

An escape hatch for when nothing else in this book covers what you need: direct access to the Minecraft network protocol, both Java and Bedrock. This is genuinely low-level, most plugins never need it, everything from chat to inventories to entity movement already has a higher-level API elsewhere in this book, reach for raw packets only when you're implementing something the plugin API doesn't expose at all (a custom plugin-channel protocol, a niche protocol quirk, or mirroring/proxying traffic).

## Sending packets

### `java_player.send_packet(packet)` / `bedrock_player.send_packet(packet)`

See [Java & Bedrock specifics](../players/java-and-bedrock-players.md). Each takes a fully-typed clientbound packet record from `java_packets`/`bedrock_packets`, hundreds of record types, one per packet, covering every phase of the protocol (login, configuration, play). Building one means matching the exact field layout the protocol expects, get it wrong and the client can desync or disconnect.

```rust
use pumpkin_plugin_api::java_packets::{CKeepAlive, ClientboundPacket};

java_player.send_packet(ClientboundPacket::CKeepAlive(CKeepAlive { keep_alive_id: 0 }));
```

For plugin-to-mod or plugin-to-plugin communication over the wire (rather than the actual protocol), `java_player.send_custom_payload(channel, data)` is usually what you want instead, see [Java & Bedrock specifics](../players/java-and-bedrock-players.md#java-specific), it's a plain byte channel rather than a protocol packet.

## Reading and intercepting packets

### `PacketReceivedEvent` / `PacketSentEvent`

Two events (see [Event handlers](../plugin-101/event-handlers.md)) fire for every packet crossing the wire in either direction, carrying `player`, a structured `packet` (a `ServerboundPacket`/`ClientboundPacket` variant you can match on to read its fields), `packet_id`, `raw_payload` (the packet's raw bytes), and `cancelled`.

```rust
use pumpkin_plugin_api::events::{EventData, PacketReceivedEvent};

impl EventHandler<PacketReceivedEvent> for PacketLogger {
  fn handle(&self, _server: Server, mut event: EventData<PacketReceivedEvent>) -> EventData<PacketReceivedEvent> {
    tracing::debug!("packet id {} from {}, {} bytes", event.packet_id, event.player.get_name(), event.raw_payload.len());
    event
  }
}
```

> [!WARNING]
> You can read the structured `packet` field and cancel the event, and you can overwrite `raw_payload` with your own bytes, that part works. What doesn't work is editing the structured `packet` field and having that change actually get sent, modifying a packet's typed fields and returning it currently panics on the host side ("Modifying packets from WASM is not yet supported"). If you need to change what gets sent, replace `raw_payload` with your own correctly-encoded bytes instead of mutating `packet`.

## Putting it together

Blocking a specific inbound packet type by id, and logging everything else:

```rust
use pumpkin_plugin_api::events::{EventData, PacketReceivedEvent};

impl EventHandler<PacketReceivedEvent> for PacketFilter {
  fn handle(&self, _server: Server, mut event: EventData<PacketReceivedEvent>) -> EventData<PacketReceivedEvent> {
    const BLOCKED_PACKET_ID: i32 = 0x1A; // whatever id you're filtering

    if event.packet_id == BLOCKED_PACKET_ID {
      event.cancelled = true;
    } else {
      tracing::trace!("packet {} from {}", event.packet_id, event.player.get_name());
    }

    event
  }
}
```

## Full packet lists

`java-packets.wit` and `bedrock-packets.wit` are each over a thousand lines, covering every packet in their respective protocols across login, configuration, and play phases. This book won't reproduce them here, check the source directly when you need an exact record shape:

- [`java-packets.wit`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/blob/master/v0.1/java-packets.wit)
- [`bedrock-packets.wit`](https://github.com/Pumpkin-MC/pumpkin-plugin-wit/blob/master/v0.1/bedrock-packets.wit)

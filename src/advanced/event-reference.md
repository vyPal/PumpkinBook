# Event reference

Every event the plugin WIT declares, grouped the way the server's source groups them, with two facts that the WIT itself can't tell you:

- **Cancellable** means the event's data record has a `cancelled` field. Setting it only has an effect in a [blocking handler](../plugin-101/event-handlers.md#blocking-vs-non-blocking), and only if the server checks it at that spot.
- **Fired** means that, as of the commit this book was checked against (see the [introduction](../introduction.md#source-commits-this-book-is-verified-against)), some code path in the server creates the event. A bold **no** means a handler for it can be registered but will never run.

Fired is worked out by searching the server for code that constructs each event, so it says nothing about *when* an event fires, or whether every action that should fire it does. Treat it as a floor: an event marked `yes` fires somewhere, an event marked `no` fires nowhere. It goes out of date as new firing sites land, so check the [API changelog](../changelog.md) and the source if an event you depend on is marked `no`.

All names are the Rust marker types from `pumpkin_plugin_api::events`. The WIT spells them in kebab case (`player-join-event`), and its data records carry a `-data` suffix.

In numbers: 273 events, 215 fired somewhere, 58 never fired, 246 cancellable.


## Player events

77 events, 10 never fired.

| Event | Cancellable | Fired |
|---|---|---|
| `AsyncPlayerChatEvent` | yes | **no** |
| `AsyncPlayerPreLoginEvent` | yes | yes |
| `BedrockFormResponseEvent` | no | yes |
| `InventoryClickEvent` | yes | yes |
| `InventoryCloseEvent` | no | yes |
| `PlayerAdvancementDoneEvent` | yes | yes |
| `PlayerAnimationEvent` | yes | yes |
| `PlayerArmorStandManipulateEvent` | yes | **no** |
| `PlayerBedEnterEvent` | yes | yes |
| `PlayerBedLeaveEvent` | no | yes |
| `PlayerBucketEmptyEvent` | yes | yes |
| `PlayerBucketEntityEvent` | yes | yes |
| `PlayerBucketFillEvent` | yes | yes |
| `PlayerChangeWorldEvent` | yes | yes |
| `PlayerChangedMainHandEvent` | no | yes |
| `PlayerChangedWorldEvent` | yes | yes |
| `PlayerChannelEvent` | yes | yes |
| `PlayerChatEvent` | yes | yes |
| `PlayerCommandPreprocessEvent` | yes | **no** |
| `PlayerCommandSendEvent` | yes | yes |
| `PlayerCustomPayloadEvent` | no | yes |
| `PlayerDropItemEvent` | yes | yes |
| `PlayerEditBookEvent` | yes | yes |
| `PlayerEggThrowEvent` | yes | yes |
| `PlayerElytraBoostEvent` | yes | yes |
| `PlayerExpChangeEvent` | no | yes |
| `PlayerExpCooldownChangeEvent` | yes | **no** |
| `PlayerFishEvent` | yes | yes |
| `PlayerGamemodeChangeEvent` | yes | yes |
| `PlayerHarvestBlockEvent` | yes | yes |
| `PlayerHideEntityEvent` | yes | **no** |
| `PlayerInputEvent` | yes | yes |
| `PlayerInteractAtEntityEvent` | yes | yes |
| `PlayerInteractEntityEvent` | yes | yes |
| `PlayerInteractEvent` | yes | yes |
| `PlayerInteractUnknownEntityEvent` | yes | yes |
| `PlayerItemBreakEvent` | no | yes |
| `PlayerItemConsumeEvent` | yes | yes |
| `PlayerItemDamageEvent` | yes | yes |
| `PlayerItemHeldEvent` | yes | yes |
| `PlayerItemMendEvent` | yes | yes |
| `PlayerJoinEvent` | yes | yes |
| `PlayerKickEvent` | yes | yes |
| `PlayerLeashEntityEvent` | yes | yes |
| `PlayerLeaveEvent` | yes | yes |
| `PlayerLevelChangeEvent` | no | yes |
| `PlayerLinksSendEvent` | yes | yes |
| `PlayerLocaleChangeEvent` | yes | yes |
| `PlayerLoginEvent` | yes | yes |
| `PlayerMoveEvent` | yes | yes |
| `PlayerNameEntityEvent` | yes | **no** |
| `PlayerOpenSignEvent` | yes | yes |
| `PlayerPermissionCheckEvent` | no | yes |
| `PlayerPickupArrowEvent` | yes | yes |
| `PlayerPortalEvent` | yes | **no** |
| `PlayerPreLoginEvent` | yes | **no** |
| `PlayerRecipeBookClickEvent` | yes | yes |
| `PlayerRecipeBookSettingsChangeEvent` | yes | yes |
| `PlayerRecipeDiscoverEvent` | yes | yes |
| `PlayerRegisterChannelEvent` | yes | yes |
| `PlayerResourcePackStatusEvent` | yes | yes |
| `PlayerRespawnEvent` | no | yes |
| `PlayerRiptideEvent` | yes | yes |
| `PlayerShearEntityEvent` | yes | yes |
| `PlayerShowEntityEvent` | yes | **no** |
| `PlayerSpawnChangeEvent` | yes | yes |
| `PlayerSpawnLocationEvent` | yes | yes |
| `PlayerStatisticIncrementEvent` | yes | yes |
| `PlayerSwapHandsEvent` | yes | yes |
| `PlayerTakeLecternBookEvent` | yes | **no** |
| `PlayerTeleportEvent` | yes | yes |
| `PlayerToggleFlightEvent` | yes | yes |
| `PlayerToggleSneakEvent` | yes | yes |
| `PlayerToggleSprintEvent` | yes | yes |
| `PlayerUnleashEntityEvent` | yes | yes |
| `PlayerUnregisterChannelEvent` | yes | yes |
| `PlayerVelocityEvent` | yes | yes |

## Block events

45 events, 12 never fired.

| Event | Cancellable | Fired |
|---|---|---|
| `BellResonateEvent` | yes | **no** |
| `BellRingEvent` | yes | yes |
| `BlockBreakEvent` | yes | yes |
| `BlockBrushEvent` | yes | yes |
| `BlockBurnEvent` | yes | yes |
| `BlockCanBuildEvent` | yes | yes |
| `BlockCookEvent` | yes | yes |
| `BlockDamageAbortEvent` | no | yes |
| `BlockDamageEvent` | yes | yes |
| `BlockDispenseArmorEvent` | yes | **no** |
| `BlockDispenseEvent` | yes | yes |
| `BlockDispenseLootEvent` | yes | **no** |
| `BlockDropItemEvent` | yes | yes |
| `BlockExpEvent` | no | yes |
| `BlockExplodeEvent` | yes | yes |
| `BlockFadeEvent` | yes | **no** |
| `BlockFertilizeEvent` | yes | yes |
| `BlockFormEvent` | yes | yes |
| `BlockFromToEvent` | yes | yes |
| `BlockGrowEvent` | yes | yes |
| `BlockIgniteEvent` | yes | yes |
| `BlockMultiPlaceEvent` | yes | **no** |
| `BlockPhysicsEvent` | yes | yes |
| `BlockPistonExtendEvent` | yes | yes |
| `BlockPistonRetractEvent` | yes | yes |
| `BlockPlaceEvent` | yes | yes |
| `BlockReceiveGameEvent` | yes | **no** |
| `BlockRedstoneEvent` | yes | yes |
| `BlockShearEntityEvent` | yes | **no** |
| `BlockSpreadEvent` | yes | yes |
| `BrewingStartEvent` | yes | yes |
| `CampfireStartEvent` | yes | yes |
| `CauldronLevelChangeEvent` | yes | yes |
| `CrafterCraftEvent` | yes | yes |
| `EntityBlockFormEvent` | yes | **no** |
| `FluidLevelChangeEvent` | yes | **no** |
| `InventoryBlockStartEvent` | no | **no** |
| `LeavesDecayEvent` | yes | yes |
| `MoistureChangeEvent` | yes | yes |
| `NotePlayEvent` | yes | yes |
| `SculkBloomEvent` | yes | **no** |
| `SignChangeEvent` | yes | yes |
| `SpongeAbsorbEvent` | yes | yes |
| `TntPrimeEvent` | yes | yes |
| `VaultDisplayItemEvent` | yes | **no** |

## Entity events

77 events, 28 never fired.

| Event | Cancellable | Fired |
|---|---|---|
| `AreaEffectCloudApplyEvent` | yes | **no** |
| `ArrowBodyCountChangeEvent` | yes | **no** |
| `BatToggleSleepEvent` | yes | **no** |
| `CreatureSpawnEvent` | yes | yes |
| `CreeperPowerEvent` | yes | **no** |
| `EnderDragonChangePhaseEvent` | yes | **no** |
| `EntityAirChangeEvent` | yes | yes |
| `EntityBreakDoorEvent` | yes | yes |
| `EntityBreedEvent` | yes | yes |
| `EntityChangeBlockEvent` | yes | yes |
| `EntityCombustByBlockEvent` | yes | **no** |
| `EntityCombustByEntityEvent` | yes | **no** |
| `EntityCombustEvent` | yes | yes |
| `EntityDamageByBlockEvent` | yes | yes |
| `EntityDamageByEntityEvent` | yes | yes |
| `EntityDamageEvent` | yes | yes |
| `EntityDeathEvent` | no | yes |
| `EntityDismountEvent` | yes | yes |
| `EntityDropItemEvent` | yes | yes |
| `EntityDyeEvent` | yes | yes |
| `EntityEnterBlockEvent` | yes | yes |
| `EntityEnterLoveModeEvent` | yes | yes |
| `EntityExhaustionEvent` | yes | yes |
| `EntityExplodeEvent` | yes | yes |
| `EntityInteractEvent` | yes | yes |
| `EntityKnockbackByEntityEvent` | yes | **no** |
| `EntityKnockbackEvent` | yes | **no** |
| `EntityMountEvent` | yes | yes |
| `EntityPickupItemEvent` | yes | yes |
| `EntityPlaceEvent` | yes | yes |
| `EntityPortalEnterEvent` | yes | **no** |
| `EntityPortalEvent` | yes | yes |
| `EntityPortalExitEvent` | yes | **no** |
| `EntityPoseChangeEvent` | yes | yes |
| `EntityPotionEffectEvent` | yes | yes |
| `EntityRegainHealthEvent` | yes | yes |
| `EntityRemoveEvent` | yes | **no** |
| `EntityResurrectEvent` | yes | yes |
| `EntityShootBowEvent` | yes | yes |
| `EntitySpawnEvent` | yes | yes |
| `EntitySpellCastEvent` | yes | **no** |
| `EntityTameEvent` | yes | yes |
| `EntityTargetBlockEvent` | yes | **no** |
| `EntityTargetEvent` | yes | yes |
| `EntityTargetLivingEntityEvent` | yes | **no** |
| `EntityTeleportEvent` | yes | yes |
| `EntityToggleGlideEvent` | yes | yes |
| `EntityToggleSwimEvent` | yes | yes |
| `EntityTransformEvent` | yes | yes |
| `EntityUnleashEvent` | yes | yes |
| `ExpBottleEvent` | yes | **no** |
| `ExplosionPrimeEvent` | yes | yes |
| `FireworkExplodeEvent` | yes | yes |
| `FoodLevelChangeEvent` | yes | yes |
| `HorseJumpEvent` | yes | **no** |
| `ItemDespawnEvent` | yes | yes |
| `ItemMergeEvent` | yes | yes |
| `ItemSpawnEvent` | yes | yes |
| `LingeringPotionSplashEvent` | yes | yes |
| `PigZapEvent` | yes | **no** |
| `PigZombieAngerEvent` | yes | **no** |
| `PiglinBarterEvent` | yes | yes |
| `PlayerDeathEvent` | yes | yes |
| `PotionSplashEvent` | yes | yes |
| `ProjectileHitEvent` | yes | yes |
| `ProjectileLaunchEvent` | yes | yes |
| `SheepDyeWoolEvent` | yes | **no** |
| `SheepRegrowWoolEvent` | yes | **no** |
| `SlimeSplitEvent` | yes | **no** |
| `SpawnerSpawnEvent` | yes | yes |
| `StriderTemperatureChangeEvent` | yes | **no** |
| `TrialSpawnerSpawnEvent` | yes | yes |
| `VillagerAcquireTradeEvent` | yes | **no** |
| `VillagerCareerChangeEvent` | yes | **no** |
| `VillagerReplenishTradeEvent` | yes | **no** |
| `VillagerReputationChangeEvent` | yes | **no** |
| `WardenAngerChangeEvent` | yes | **no** |

## Inventory events

21 events, all fired.

| Event | Cancellable | Fired |
|---|---|---|
| `BrewEvent` | yes | yes |
| `BrewingStandFuelEvent` | yes | yes |
| `CraftItemEvent` | yes | yes |
| `FurnaceBurnEvent` | yes | yes |
| `FurnaceExtractEvent` | no | yes |
| `FurnaceSmeltEvent` | yes | yes |
| `FurnaceStartSmeltEvent` | yes | yes |
| `HopperInventorySearchEvent` | yes | yes |
| `InventoryCreativeEvent` | yes | yes |
| `InventoryDragEvent` | yes | yes |
| `InventoryInteractEvent` | yes | yes |
| `InventoryMoveItemEvent` | yes | yes |
| `InventoryOpenEvent` | yes | yes |
| `InventoryPickupItemEvent` | yes | yes |
| `PrepareAnvilEvent` | no | yes |
| `PrepareGrindstoneEvent` | no | yes |
| `PrepareInventoryResultEvent` | no | yes |
| `PrepareItemCraftEvent` | yes | yes |
| `PrepareSmithingEvent` | no | yes |
| `SmithItemEvent` | yes | yes |
| `TradeSelectEvent` | yes | yes |

## World events

22 events, 2 never fired.

| Event | Cancellable | Fired |
|---|---|---|
| `AsyncStructureGenerateEvent` | yes | yes |
| `AsyncStructureSpawnEvent` | yes | yes |
| `ChunkLoadEvent` | yes | **no** |
| `ChunkPopulateEvent` | yes | yes |
| `ChunkSaveEvent` | yes | **no** |
| `ChunkSendEvent` | yes | yes |
| `ChunkUnloadEvent` | yes | yes |
| `EntitiesLoadEvent` | yes | yes |
| `EntitiesUnloadEvent` | yes | yes |
| `GenericGameEvent` | yes | yes |
| `LightningStrikeEvent` | yes | yes |
| `LootGenerateEvent` | yes | yes |
| `PortalCreateEvent` | yes | yes |
| `SpawnChangeEvent` | no | yes |
| `StructureGrowEvent` | yes | yes |
| `ThunderChangeEvent` | yes | yes |
| `TimeSkipEvent` | yes | yes |
| `WeatherChangeEvent` | yes | yes |
| `WorldInitEvent` | no | yes |
| `WorldLoadEvent` | no | yes |
| `WorldSaveEvent` | yes | yes |
| `WorldUnloadEvent` | yes | yes |

## Server events

9 events, 1 never fired.

| Event | Cancellable | Fired |
|---|---|---|
| `MapInitializeEvent` | no | **no** |
| `PacketReceivedEvent` | yes | yes |
| `PacketSentEvent` | yes | yes |
| `ServerBroadcastEvent` | yes | yes |
| `ServerCommandEvent` | yes | yes |
| `ServerListPingEvent` | no | yes |
| `ServerLoadEvent` | no | yes |
| `ServerTickEndEvent` | no | yes |
| `ServerTickStartEvent` | no | yes |

## Hanging events

3 events, 3 never fired.

| Event | Cancellable | Fired |
|---|---|---|
| `HangingBreakByEntityEvent` | yes | **no** |
| `HangingBreakEvent` | yes | **no** |
| `HangingPlaceEvent` | yes | **no** |

## Vehicle events

10 events, all fired.

| Event | Cancellable | Fired |
|---|---|---|
| `VehicleBlockCollisionEvent` | yes | yes |
| `VehicleCollisionEvent` | yes | yes |
| `VehicleCreateEvent` | yes | yes |
| `VehicleDamageEvent` | yes | yes |
| `VehicleDestroyEvent` | yes | yes |
| `VehicleEnterEvent` | yes | yes |
| `VehicleEntityCollisionEvent` | yes | yes |
| `VehicleExitEvent` | yes | yes |
| `VehicleMoveEvent` | yes | yes |
| `VehicleUpdateEvent` | yes | yes |

## Enchantment events

2 events, all fired.

| Event | Cancellable | Fired |
|---|---|---|
| `EnchantItemEvent` | yes | yes |
| `PrepareItemEnchantEvent` | yes | yes |

## Raid events

4 events, all fired.

| Event | Cancellable | Fired |
|---|---|---|
| `RaidFinishEvent` | yes | yes |
| `RaidSpawnWaveEvent` | yes | yes |
| `RaidStopEvent` | yes | yes |
| `RaidTriggerEvent` | yes | yes |

## Dialog events

3 events, 2 never fired.

| Event | Cancellable | Fired |
|---|---|---|
| `DialogClearEvent` | yes | **no** |
| `DialogClickActionEvent` | yes | yes |
| `DialogShowEvent` | yes | **no** |

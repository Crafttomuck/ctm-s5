# Changelog

## 0.0.6

### Added
- spark, Observable, Crash Utilities — performance profiling and crash diagnostics
- Entity Culling — entity render-culling optimization
- ServerCore — server-side performance optimizations, with dynamic performance scaling and activation range enabled

## 0.0.5

### Added
- AE2 × Create integration: Create: Applied Kinetics, Polymorphic Energistics, Create Stock Bridge
- TooManyRecipeViewers — recipes from JEI-only mods now show in EMI
- Create Aeronautics ecosystem: Delivery Required, Transmission & Linkage, Propulsion: Simulated, Sable Pallets, Sound of Steam, VS/Sable Hose Connectors
- Create: Garnished, Steam 'n' Rails
- Luki's structures: Ancient Cities, Strongholds, Woodland Mansions, Crazy Chambers
- Star Worm Equestrian (SWEM), Exposure, Copper Age Backport
- Ragdoll Reactions, Ragdoll Revive, Sable: Player Ragdoll
- Player Animation Library, playerAnimator, Fancy Entity Renderer, MoreCulling
- Ponder for KubeJS, MoreJS, Crash Assistant
- Lithosphere — overworld terrain generation
- BlueMap web map (server), Essential Core (server)

### Removed
- Create: Numismatics suite (Numismatics, Numismatic Bounties, Create 6.0 integration)
- Kaleidoscope Cookery suite (Cookery, Automation, Ponder)
- Macaw's Doors & Trapdoors; Every Compat (Wood Good) & Stone Zone
- Create: Copper & Zinc, Create: Trading Floor, Create Railways Navigator
- Configured & Configured Defaults, Map Atlases
- spark, BetterF3, Better Advancements, Better Mods Button, Better Third Person
- Toast Control, Stylish Effects, Drippy Loading Screen, Freecam, Observable, Log Begone, Remove Reloading Screen
- Hang Glider, Armor Statues, NetherPortalFix, Leaves Be Gone, Let Me Despawn, [Let's Do] Furniture
- YUNG's Better Strongholds, Vista Aeronautics Fix

### Changed
- NeoForge 21.1.228 → 21.1.233
- AE2 meteorites now generate only in the End
- AE2 Fluix Researcher villager no longer sells meteorite-gated items (inscriber presses, certus quartz, sky stone, fluix)
- Disabled the Quark "Configure Quark Here" onboarding popup (the config button is kept)
- Title screen: logo re-centered over the menu, and the player now lines up with the rope at any window size
- Synced server-tuned config values (Create Aeronautics rope range, Create schematic limits, voice chat, artifacts, relics, and more)
- 60+ mods updated to current versions
- Updated bundled server list

## 0.0.4

### Added
- Croptopia and Farmer's Croptopia
- Every Compat (Wood Good) and Stone Zone
- Vanilla Backport
- Vista and Vista Aeronautics Fix
- Epic Structures: Villages
- Epic Terrain Compatible (server)
- Lake Feature Fix (server)
- Platform
- Create Curios Jetpack
- EpheroLib
- Drippy Loading Screen (client)
- Configured Defaults — default keybinds shipped with pack (Map Atlases minimap and voice chat mute unbound from M)
- Quark config: inventory sort buttons disabled
- Dev server added to server list

### Removed
- Civillis (server overhead — full-world entity scan every tick)
- ChoiceTheorem's Overhauled Village
- Terralith and Terralith ReStoned
- Lithostitched
- Dark Mode Everywhere (crash on button click, no fix for 1.21.1)
- Angel Islands

### Updated
- Moonlight Lib 3.0.10 → 3.0.13 (fixes server crash)
- Supplementaries 3.6.4 → 3.6.5
- Puzzles Lib 21.1.39 → 21.1.44
- Sophisticated Core, Backpacks, Storage, Storage in Motion
- Almost Unified 1.4.1 → 1.4.2
- C2ME 0.92 → 0.93
- LDLib 2.2.10 → 2.2.11
- Relics 0.12.6 → 0.12.7
- Create Rail Grinding 1.0.0 → 1.1.2
- Moog's End Structures, Moog's Voyager Structures

## 0.0.3

- Downgraded Sodium to 0.6.13 (Sable 1.2.2 incompatible with 0.8.x)
- Removed MoreCulling (incompatible with Sodium 0.6.x)
- Fixed client zip missing NeoForge modloader in manifest (packwiz bug workaround)

## 0.0.2

- Removed Create Encased (server crash — broken JEI mixin with EMI-only packs)
- Removed Dye Depot, Envelope, Vista, Vista Aeronautics Fix
- Marked Ponder for Kaleidoscope Cookery as client-only
- Fixed GuideME missing from server (required by AE2)
- Marked 38 client-only mods (minimap, shaders, etc.)
- Added local build script for client and server zips

## 0.0.1

Initial modpack build. Pack is in active development — mod list is not final.

- Added all mods

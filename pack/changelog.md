# Changelog

## 1.0.7

### Added
- Frequency Create — symbol items for configuring Redstone Link frequencies
- Simple Voice Radio (+ Lexiconfig) — radios for Simple Voice Chat
- Reliquified Artifacts — integrates Artifacts items into the Relics leveling system
- Lever drugster — reworks stepped levers from Create / Design n' Decor / Supplementaries
- Sable CleanUp — find and manage every Sable sub-level on the server
- Sable x Xaero Bridge — Sable ships on Xaero's map
- Default server list entry for the creative server (creative.crafttomuck.com)
- Create recipes for ManyIdeas panels and plates (pressing/deploying)
- Rustic doors via deploying, with stonecutting style variants
- Bulk dyeing of any planks to red planks via splashing
- TFMG concrete from Diesel Generators cement fluids (heated compacting)
- SWEM oat/timothy/alfalfa seeds tagged as `c:seeds`

### Changed
- Limesand crushing reworked: crushes Create limestone (by recipe id) into limesand,
  crushed salt, and iron/zinc nuggets
- Removed Star Worm Light Mod colored-glass conversion recipes
- Create: Delivery Required economy rebalanced — expanded contract/market price lists
  (Create sheets and mechanisms, Big Cannons ingots, Propulsion platinum, fuels,
  Farmer's Delight crates, fish, stones), longer travel/pickup distances, slower
  rank progression, price multiplier normalized to 1.0
- Create Stuff & Additions jetpacks tuned down: height caps (9–16 blocks),
  reduced speeds, Above Cloud enchant disabled
- Immersive Furniture interact distance raised to 128
- Title screen layout updated, with a separate compact layout for windows
  narrower than 1400px

### Removed
- Create Jetpack and Create: Curios Jetpack & Backtank

## 1.0.6

### Added
- Building Gadgets and Construction Sticks — building and placement tools
- Create: Numismatics — currency and economy
- In Control! — mob spawn and difficulty control
- Sodium Extra — extra client-side render options and tweaks for Sodium
- Create: Some Assembly Required — build-your-own sandwiches and food
- Star Worm Lighting and Star Worm Decor — SWEM lighting and decoration addons

### Changed
- Create: schematicannon delay lowered (4 → 1) and max track placement length raised (32 → 64)
- Quark: Automatic Tool Restock disabled
- TFMG limestone crushing now also drops limesand
- Removed the Synaxis compact flap recipe and the Farm & Charm feeding/water trough recipes
- SWEM star worm cobble no longer drops XP
- Create: Delivery Required contract and market prices retuned
- Added custom chat formatting plus /broadcast and /titlecast commands

### Updated
- 40 mods updated to current versions (Supplementaries, Sophisticated Backpacks /
  Core / Storage, Create: Connected, Vista, Reese's Sodium Options, Amendments,
  GeckoLib, ModernFix, and more)
- Steam 'n' Rails moved to the 0.3.0-alpha.2 build
- Create Slice & Dice switched to its native NeoForge build
- Held on their stable versions: Create: Garnished, Create: Enchantment Industry,
  Moog's Structure Lib

## 1.0.5

### Removed
- Essential Core (server-side inspection tool)

## 1.0.4

### Removed
- Ragdoll Reactions and Sable: Ragdolls — all ragdoll mods removed (the suite was causing stuck/soft-lock states)

## 1.0.3

### Removed
- Ragdoll Revive — its downed/revive state could leave players stuck after ragdolling (cosmetic ragdolls kept)

## 1.0.2

### Removed
- Carry On — was causing frequent crashes

## 1.0.1

### Fixed
- Opening Video Settings no longer crashes — removed Sodium Options API, which was built for an older Sodium and broke on the pack's version (dynamic lights and Reese's Sodium Options are unaffected)

## 1.0.0

Initial release for Season 5 — CTM: Cogs and Canvas.

## 0.0.9

### Changed
- Carry On: pickup is now limited to players, villagers, and animals (vanilla + modded) — hostiles, golems, and other utility mobs can no longer be carried

## 0.0.8

### Updated
- 15 mods updated to current versions: Sable, LDLib, Fusion, Simple Voice Chat,
  Sophisticated Backpacks / Core / Create Integration, Create: The Factory Must Grow,
  Create Aeronautics: Transmission & Linkage, Supplementaries Squared, Ragdoll
  Reactions, Ragdoll Revive, Sable: Player Ragdoll, Crash Assistant, Lake Feature Fix
- Held back pre-release builds: Steam 'n' Rails, Create: Enchantment Industry,
  Moog's Structure Lib, and Create: Garnished stay on their stable versions

## 0.0.7

### Added
- Create Big Cannons (+ Ritchie's Projectile Library)
- Create Deep Seas — physics-based submarines
- Create Aeronautics: Toolgun
- RightClickHarvest — harvest and replant crops with right-click
- Toast Control (client) — re-added

### Changed
- Create Big Cannons: cannon projectiles no longer damage blocks (entity damage only)
- Create Deep Seas: first-launch welcome/update screens disabled
- Vista: FFmpeg disabled by default (no first-launch download prompt)
- Xaero's: update-notification popup disabled
- Quark: inventory sorting re-enabled (buttons + keybind)

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

# pfviewer — CONFIG reference

Generated 2026-10-09 from `config.js` (current values, including your edits). Each row is a key path you can change in `config.js`, e.g. `signs.doorHeightM` means `CONFIG.signs.doorHeightM`. Change numbers there, not in `index.html`. A `mobile:` block is deep-merged over everything on touch devices (or `?profile=mobile`).

**Sections:** [`dataFiles`](#datafiles) · [`start`](#start) · [`materials`](#materials) · [`palettes`](#palettes) · [`scene`](#scene) · [`lighting`](#lighting) · [`camera`](#camera) · [`altitude`](#altitude) · [`orbitControls`](#orbitcontrols) · [`glass`](#glass) · [`windows`](#windows) · [`dormers`](#dormers) · [`building`](#building) · [`facade`](#facade) · [`roadWidths`](#roadwidths) · [`fences`](#fences) · [`chimneys`](#chimneys) · [`terrain`](#terrain) · [`water`](#water) · [`rail`](#rail) · [`bridges`](#bridges) · [`steamboats`](#steamboats) · [`roadHistory`](#roadhistory) · [`nightLights`](#nightlights) · [`streetLights`](#streetlights) · [`parades`](#parades) · [`mosquitoes`](#mosquitoes) · [`postcards`](#postcards) · [`utilityPoles`](#utilitypoles) · [`cues`](#cues) · [`shanties`](#shanties) · [`autos`](#autos) · [`fireEngines`](#fireengines) · [`docks`](#docks) · [`smallCraft`](#smallcraft) · [`ferryTiming`](#ferrytiming) · [`windmills`](#windmills) · [`construction`](#construction) · [`trees`](#trees) · [`sidewalks`](#sidewalks) · [`signs`](#signs) · [`cemetery`](#cemetery) · [`marsh`](#marsh) · [`tipis`](#tipis) · [`earlyVegetation`](#earlyvegetation) · [`timeline`](#timeline) · [`storms`](#storms) · [`seasons`](#seasons) · [`streetcars`](#streetcars) · [`carts`](#carts) · [`trains`](#trains) · [`audio`](#audio) · [`mobile`](#mobile) · [`minimap`](#minimap) · [`fpsControls`](#fpscontrols)


## Quick guide — recent additions (what to tweak first)

| Key | What it does |
|---|---|
| `signs.doorHeightM` | Height of the ground-floor sign's centre above the building base (capped at 75% of wall height for short buildings). |
| `signs.wallHeightM` / `signs.windowHeightM` | Sign board height / gilt window-lettering height (m). Width follows the text. |
| `signs.share` / `signs.windowShare` / `signs.windowMax` | How many buildings get a ground sign / window lettering / most window signs per building. |
| `signs.radiusM`, `signs.max`, `signs.maxAltitudeM` | Show distance, hard cap on visible signs, camera altitude above which signs hide. |
| `signs.turnoverYears` | How often a building's trade changes (deterministic per building). |
| `signs.occupants` | The generic trade list: `t` text, `s` style (`wall` / `window` / `anvil` / `horseshoe`), `y` year range, `a` footprint m², `f` floors. Add lines to add trades. |
| `signs.byName` | Building-name patterns that force a sign (e.g. stable, smithy, hotel). `signs.exclude` = names that never get one. |
| `cemetery.grassColor` | Elmwood lawn base colour (the shader also mottles it and lets 30% of the prairie show through). |
| `cemetery.fence.height` / `.fadeNear` / `.fadeFar` / `.color` | Iron fence height, and the distances (m) between which it dithers out. |
| `cemetery.gate.halfWidthM` / `.pierSize` / `.pierHeight` / `.pierColor` / `.capColor` | Gate opening half-width and the stone piers at the east entrance. |
| `fpsControls.pinchMetresPerPx` | Walk-mode pinch/spread speed (metres per pixel of finger movement). |
| `fpsControls.touchLookSensitivity` | Touch look speed. |
| `chimneys.brick.tubeBaseH` / `.tubePerFloor` / `.tubePerSqrtArea` / `.tubeMaxH` | Height of the big round brick stacks on tall/industrial buildings. |
| `mobile.signs` | Phone overrides for signs (radius, max, atlas size). |

URL switches: `?input=touch|mouse|auto` (controls), `?profile=mobile|desktop`, `?off=signs,fences,cemetery,…`, `?debug=1`.


## dataFiles

Data files GeoJSON layers loaded automatically on startup. Add/remove/rename entries to change what loads — paths are relative to index.html.

| Key | Default | Notes |
|---|---|---|
| `dataFiles.autoload` | `(list of 14)` |  |
| `dataFiles.optionalLayers` | `(list of 2)` | growth master + assessment/heritage dates (matching/merge_assessment.py) — no OSM data new pre-1907 buildings with OSM footprints — ODbL, kept as a separate database Upper Fort Garry: the NE-wall gap + the angled fence that replac… |
| `dataFiles.facadeConfig` | `"./data/facades.json"` | ground-truth "as digitized" 1880 view ground-truth "as digitized" 1906 view |
| `dataFiles.buildingHistory` | `"./data/building_history.json"` | Per-building phase overrides (storey additions, fires…) keyed by uid — see applyBuildingHistory |
| `dataFiles.railHistory` | `"./data/rail_history.json"` | Born/died per rail feature (tools/date_rails.py) — rails and trains appear when their line was built |
| `dataFiles.facadeImageDir` | `"./images/"` |  |
| `dataFiles.bumpFallbackDir` | `"./images"` | Building-material stems that get an auto-loaded bump/texture map (looked for at `./data/bump_<stem>.png`). wall bump maps are also looked for here (null = only ./data/) |
| `dataFiles.bumpMapStems` | `(list of 9)` |  |

## start

Start behaviour

| Key | Default | Notes |
|---|---|---|
| `start.timeOfDay` | `0.42` | Time of day at load, 0..1 spans 04:00–22:00 (0.42 ≈ 11:34am). |
| `start.winterMode` | `false` | Start in winter (snow) mode? |
| `start.layer` | `"pastforward"` | layer shown on load: 'pastforward' \| '1906' \| '1880' \| 'all' \| 'combined' (falls back if not loaded) |
| **`start.cameraPosition`** | *(group)* | Initial camera position and look-at target, in world metres. (World X=east, Y=up, Z=south — see coordinate-system note in index.html.) Default: over St Boniface, looking northwest across the Forks (Red–Assiniboine confluence ≈ wor… |
| `start.cameraPosition.x` | `830` |  |
| `start.cameraPosition.y` | `330` |  |
| `start.cameraPosition.z` | `1415` |  |
| **`start.cameraLookAt`** | *(group)* |  |
| `start.cameraLookAt.x` | `453` |  |
| `start.cameraLookAt.y` | `0` |  |
| `start.cameraLookAt.z` | `1038` |  |

## materials

Building material colours Base colour + specular "shininess" (0=matte, 100=very glossy) per material type. `label` is what's shown in the on-screen legend.

| Key | Default | Notes |
|---|---|---|
| **`materials.brick`** | *(group)* |  |
| `materials.brick.color` | `0xC0604A` |  |
| `materials.brick.label` | `"Brick"` |  |
| `materials.brick.shininess` | `20` |  |
| **`materials.brick_veneer`** | *(group)* |  |
| `materials.brick_veneer.color` | `0xC07858` |  |
| `materials.brick_veneer.label` | `"Brick Veneer"` |  |
| `materials.brick_veneer.shininess` | `18` |  |
| **`materials.wood`** | *(group)* |  |
| `materials.wood.color` | `0xCFA840` |  |
| `materials.wood.label` | `"Wood / Frame"` |  |
| `materials.wood.shininess` | `6` |  |
| **`materials.wood_industrial`** | *(group)* |  |
| `materials.wood_industrial.color` | `0x687888` |  |
| `materials.wood_industrial.label` | `"Wood / Industrial"` |  |
| `materials.wood_industrial.shininess` | `8` |  |
| **`materials.iron`** | *(group)* |  |
| `materials.iron.color` | `0x687888` |  |
| `materials.iron.label` | `"Iron / Metal"` |  |
| `materials.iron.shininess` | `45` |  |
| **`materials.stone`** | *(group)* |  |
| `materials.stone.color` | `0xE8DFC8` |  |
| `materials.stone.label` | `"Stone"` |  |
| `materials.stone.shininess` | `55` |  |
| **`materials.blue`** | *(group)* |  |
| `materials.blue.color` | `0x3A6898` |  |
| `materials.blue.label` | `"Railway Siding"` |  |
| `materials.blue.shininess` | `35` |  |
| **`materials.concrete`** | *(group)* |  |
| `materials.concrete.color` | `0x989890` |  |
| `materials.concrete.label` | `"Concrete"` |  |
| `materials.concrete.shininess` | `18` |  |
| **`materials.unknown`** | *(group)* |  |
| `materials.unknown.color` | `0x808078` |  |
| `materials.unknown.label` | `"Unknown"` |  |
| `materials.unknown.shininess` | `5` |  |
| **`materials.log`** | *(group)* |  |
| `materials.log.color` | `0x807040` |  |
| `materials.log.label` | `"Log"` |  |
| `materials.log.shininess` | `4` |  |
| **`materials.lumber`** | *(group)* |  |
| `materials.lumber.color` | `0xC0A040` |  |
| `materials.lumber.label` | `"Stacked Lumber"` |  |
| `materials.lumber.shininess` | `6` |  |

## palettes

Per-material colour *palettes* — small random variation pools so not every brick building is the exact same red. Each entry is [base, alt] or a [min,max] range depending on material; see index.html comments near "BRICK_PALETTES" e…

| Key | Default | Notes |
|---|---|---|
| **`palettes.named`** | *(group)* | Named wall colours a building can be given by hand with a `wall_color` property (in data/building_history.json → `set`). A building's wall_color may also be a hex string like "#A0452E". |
| `palettes.named.darkRed` | `10500136` |  |
| `palettes.named.red` | `12077620` |  |
| `palettes.named.orangeRed` | `13132868` |  |
| `palettes.named.buff` | `13412424` | yellow/buff brick |
| `palettes.named.cream` | `14207120` | pale cream brick |
| `palettes.named.tyndall` | `13812890` | Tyndall limestone |
| `palettes.named.sandstone` | `10246720` | red sandstone |
| `palettes.named.grey` | `9209984` | grey stone / painted brick |
| `palettes.named.slate` | `4870232` | slate roofing (default for dome/bell/conical roofs) |
| `palettes.named.copper` | `6200454` | weathered (verdigris) copper |
| `palettes.named.newCopper` | `11561020` | fresh copper |
| **`palettes.brick`** | *(group)* | Each [lo,hi] pair is a colour range a building of this material is randomly lerped within. `weights` are cumulative percentages (must end at 100) controlling how common each pair is — e.g. brick's first entry (dark red) is picked … |
| `palettes.brick.pairs` | `(list of 5)` |  |
| `palettes.brick.weights` | `[35,60,70,90,100]` | dark red mid red orange-red yellow/buff brick pale limestone-yellow |
| **`palettes.woodComm`** | *(group)* |  |
| `palettes.woodComm.pairs` | `(list of 7)` |  |
| `palettes.woodComm.weights` | `[20,35,50,60,72,82,100]` | ochre (most common Victorian exterior) sage green cream/buff barn red dark green French grey (later fashion) raw/weathered wood (small buildings) |
| **`palettes.ironIndustrial`** | *(group)* |  |
| `palettes.ironIndustrial.pairs` | `(list of 4)` |  |
| `palettes.ironIndustrial.weights` | `[40,65,85,100]` |  |
| **`palettes.stone`** | *(group)* |  |
| `palettes.stone.min` | `14536880` |  |
| `palettes.stone.max` | `15788240` |  |
| **`palettes.log`** | *(group)* |  |
| `palettes.log.min` | `8413242` |  |
| `palettes.log.max` | `9992280` |  |
| **`palettes.lumber`** | *(group)* |  |
| `palettes.lumber.fresh` | `13150272` |  |
| `palettes.lumber.aged` | `10522736` |  |
| **`palettes.concrete`** | *(group)* |  |
| `palettes.concrete.min` | `8947840` |  |
| `palettes.concrete.max` | `10526872` |  |
| **`palettes.unknown`** | *(group)* |  |
| `palettes.unknown.min` | `7893096` |  |
| `palettes.unknown.max` | `9472128` |  |

## scene

Sky / scene colours & atmosphere

| Key | Default | Notes |
|---|---|---|
| `scene.buildingOffsetX` | `0` | Registration offset for building/road data relative to river GeoJSON + LiDAR DEM. Positive offsetX = shift buildings east (metres); positive offsetZ = shift south. Set to 0 to establish baseline — adjust once misalignment is measu… |
| `scene.buildingOffsetZ` | `0` |  |
| `scene.terrainOffsetX` | `-29` | DEM terrain offset — shifts the terrain mesh in world space (no reprocessing needed). Positive terrainOffsetZ = shift terrain south; negative = shift north. −29.0 E / +19.6 S = 35 m along bearing 236° from the old (0, −5): terrain… |
| `scene.terrainOffsetZ` | `14.6` |  |
| `scene.terrainRotationDeg` | `1.5` | DEM terrain rotation — rotates the terrain mesh around a geographic pivot. terrainRotationDeg: clockwise-positive degrees around world Y axis. 0 = no rotation. Pivot is the tip of land at The Forks (west of the Red, south of the A… |
| `scene.terrainRotationPivotLon` | `-97.1283` |  |
| `scene.terrainRotationPivotLat` | `49.8843` |  |
| `scene.backgroundColor` | `0x8AB8D0` |  |
| **`scene.fog`** | *(group)* |  |
| `scene.fog.color` | `0x8AB8D0` |  |
| `scene.fog.density` | `0.00032` | Exponential fog density — higher = haze sets in closer to camera. Try 0.0001 (very clear, see for miles) to 0.0008 (thick haze). |
| **`scene.ground`** | *(group)* |  |
| `scene.ground.summerColor` | `0x2D4A1A` |  |
| `scene.ground.winterColor` | `0xF5F6FA` |  |
| `scene.ground.droughtColor` | `0x6A6436` | Summer moisture (data/moisture.json — season-to-date rainfall vs normal, + flood years): the summer colour leans toward these. parched, straw-olive |
| `scene.ground.lushColor` | `0x2A5E1E` | wet-year green |
| **`scene.grid`** | *(group)* | Reference grid lines drawn over the ground. |
| `scene.grid.colorCenterLine` | `0x3A5A22` |  |
| `scene.grid.colorGrid` | `0x324A1C` |  |
| `scene.grid.summerTint` | `0x3A5A22` |  |
| `scene.grid.summerOpacity` | `0.18` |  |
| `scene.grid.winterTint` | `0xC8C8D8` |  |
| `scene.grid.winterOpacity` | `0.12` |  |
| `scene.roadFade` | `[1800,3200]` | Road vertex-colour gradient: edge = dry/snowy shoulder, centre = wet/mud wheel-rut tracks. Each is an [r,g,b] byte triple (0-255). metres from camera: roads full → gone (only the most distant roads alias and z-fight) |
| **`scene.roadColors`** | *(group)* |  |
| `scene.roadColors.summerEdge` | `[18,17,15]` |  |
| `scene.roadColors.summerCentre` | `[5,5,4]` |  |
| `scene.roadColors.winterEdge` | `[245,246,250]` |  |
| `scene.roadColors.winterCentre` | `[32,28,24]` |  |

## skyKeyframes

Time-of-day keyframes the sky/fog/sun smoothly blend between. Each entry: [day phase (0..1: sunrise ≈ 0.10, sunset ≈ 0.90 — stretched to the date's real sunrise/sunset, see lighting.solarNoonClock), skyColor, fogColor, sunColor, s…

| Key | Default | Notes |
|---|---|---|
| `skyKeyframes` | `(list of 10)` | Time-of-day keyframes the sky/fog/sun smoothly blend between. Each entry: [day phase (0..1: sunrise ≈ 0.10, sunset ≈ 0.90 — stretched to the date's real sunrise/sunset, see lighting.solarNoonClock), skyColor, fogColor, sunColor, s… |

## lighting

pre-dawn early sunrise sunrise early morning mid-morning late morning / noon afternoon sunset late sunset night

| Key | Default | Notes |
|---|---|---|
| `lighting.solarNoonClock` | `12.48` | Sun follows the real clock: solar noon in local standard time (CST) at Winnipeg's longitude, 97.14°W → 12:00 + 7.14°×4 min ≈ 12:29. Sky keyframes above are stretched to each date's actual sunrise→sunset, with twilightHours of dusk… |
| `lighting.twilightHours` | `1.5` |  |
| **`lighting.hemisphere`** | *(group)* |  |
| `lighting.hemisphere.skyColor` | `0x88C0E8` |  |
| `lighting.hemisphere.groundColor` | `0x3A5A20` |  |
| `lighting.hemisphere.intensity` | `0.55` |  |
| **`lighting.ambient`** | *(group)* |  |
| `lighting.ambient.color` | `0xFFFFFF` |  |
| `lighting.ambient.intensity` | `0.12` |  |
| **`lighting.sun`** | *(group)* |  |
| `lighting.sun.color` | `0xFFF4DC` |  |
| `lighting.sun.intensity` | `1.3` |  |
| `lighting.sun.shadowMapSize` | `2048` | higher = sharper shadows, slower to render |
| `lighting.sun.shadowNear` | `10` |  |
| `lighting.sun.shadowFar` | `2200` |  |
| **`lighting.sun.shadowBounds`** | *(group)* |  |
| `lighting.sun.shadowBounds.left` | `-900` |  |
| `lighting.sun.shadowBounds.right` | `900` |  |
| `lighting.sun.shadowBounds.top` | `900` |  |
| `lighting.sun.shadowBounds.bottom` | `-900` |  |
| `lighting.sun.shadowBias` | `-0.0003` |  |

## camera

| Key | Default | Notes |
|---|---|---|
| `camera.fov` | `68` |  |
| `camera.near` | `0.5` |  |
| `camera.far` | `30000` |  |
| `camera.pixelRatioCap` | `2` | caps device pixel ratio for perf on hi-DPI screens |
| `camera.homeAltitude` | `1500` | metres above ground for H key top-down overview |

## altitude

Altitude maxM: the ceiling (default = the orbit's maxDistance). Haze (city smoke haze + distance fog) is full below hazeFadeFromM and gone at hazeGoneFrac × maxM. Flying (walk mode, E/Q) speeds up with height: ×flySpeedAtMax at ma…

| Key | Default | Notes |
|---|---|---|
| `altitude.maxM` | `3000` |  |
| `altitude.hazeFadeFromM` | `150` |  |
| `altitude.hazeGoneFrac` | `0.8` |  |
| `altitude.fadePower` | `2` |  |
| `altitude.fogToo` | `true` |  |
| `altitude.flySpeedAtMax` | `5` |  |
| `altitude.flySpeedCurve` | `0.6` | fly speed ×(1+4·(alt/max)^curve): ×2 at 300 m, ×3 at 1 km, ×5 at the ceiling (curve 1 would be linear: only ×1.4 at 300 m) // fog ×(1−t)² with t = 0 at 150 m, 1 at 2400 m: ~40% left at 1 km, ~15% at 1.5 km |

## orbitControls

| Key | Default | Notes |
|---|---|---|
| `orbitControls.dampingFactor` | `0.07` |  |
| `orbitControls.maxPolarAngle` | `0.98` | × Math.PI — 1.0 would let you flip under the ground |
| `orbitControls.minDistance` | `2` |  |
| `orbitControls.maxDistance` | `6000` | generous: the ceiling is on ALTITUDE (CONFIG.altitude.maxM = 3000) — a distance cap alone stopped oblique views at ~half that height |
| `orbitControls.dollyIn` | `0.94` | zoom-in factor per scroll/tap |

## glass

Window/glass "shader" look The window-glass material — this is the closest thing to a shader effect in this renderer (a tinted, glossy, semi-transparent surface).

| Key | Default | Notes |
|---|---|---|
| `glass.color` | `0x283038` | opaque now (was 0x1A2530 at 72% opacity over the wall) — a touch lighter to compensate |
| `glass.shininess` | `90` |  |
| `glass.specular` | `0x4868A0` |  |
| `glass.tileMetres` | `400` | windows are grouped in map tiles of this size… |
| `glass.maxDistance` | `1800` | …and tiles farther than this (3D) from the camera are hidden, nearest first… |
| `glass.maxPanes` | `150000` | …up to this many real panes at once (the painted windows take over beyond); 0-cost cap on close-up work |
| `glass.tilesPerFrame` | `2` | new tiles switched on per frame (spreads GPU uploads) |
| **`glass.nightGlowColor`** | *(group)* | Warm amber glow added to glass at night, scaled by darkness (0..1). |
| `glass.nightGlowColor.r` | `0.47` |  |
| `glass.nightGlowColor.g` | `0.19` |  |
| `glass.nightGlowColor.b` | `0.02` |  |

## windows

Procedural window dimensions/density

| Key | Default | Notes |
|---|---|---|
| **`windows.church`** | *(group)* |  |
| `windows.church.spacing` | `4` |  |
| `windows.church.width` | `1` |  |
| `windows.church.sill` | `1.6` |  |
| `windows.church.heightShare` | `0.6` | lancet windows on churches (false = none) |
| `windows.width` | `1` | standard window width (m) |
| `windows.height` | `1.75` | standard window height (m) |
| `windows.sillHeight` | `0.9` | sill height above floor (m) |
| `windows.gap` | `0.9` | horizontal gap between windows (m) — smaller = denser |
| `windows.margin` | `0.7` | margin kept clear at wall ends (m) |
| `windows.inset` | `0.06` | how far glass sits back from the wall face (m) |
| `windows.groundFloorWidth` | `1.5` | wider ground-floor "shopfront" windows |
| `windows.groundFloorHeightFrac` | `0.78` | ground floor window height, as a fraction of floor height |
| `windows.halfFloorRoundUpThreshold` | `0.9` | A half-floor fraction at/above this is treated as a full floor of windows (e.g. floors=2.93 gets windows like floors=3). Below this, the partial floor gets dormers (or nothing) instead of overrun windows. |

## dormers

Dormers (added to peaked-roof buildings with a half-storey)

| Key | Default | Notes |
|---|---|---|
| `dormers.width` | `1.5` | dormer footprint width along the wall (m) |
| `dormers.depth` | `0.55` | dormer footprint depth, front-to-back (m) |
| `dormers.wallHeight` | `1.15` | dormer wall height below its own little roof (m) |
| `dormers.roofHeight` | `0.55` | dormer roof peak height above its wall (m) |
| `dormers.embed` | `0.15` | how far the dormer sits back into the main wall/roof mass |
| `dormers.windowWidth` | `0.8` |  |
| `dormers.windowHeight` | `0.85` |  |
| `dormers.windowSill` | `0.15` |  |
| `dormers.maxPerBuilding` | `3` | cap on dormers per qualifying wall |
| `dormers.spacingMetres` | `6` | ~1 dormer per this many metres of wall |
| `dormers.minFloorsForDormer` | `0` | floors must be > this to qualify |
| `dormers.maxFloorsForDormer` | `2.5` | floors must be <= this to qualify (low-rise only) |

## building

Building heights & roads

| Key | Default | Notes |
|---|---|---|
| `building.tileMetres` | `1000` | building meshes are merged per map tile (culling; shadow pass only draws nearby tiles) |
| `building.deferSliceMs` | `6` | while a deferred chunk builds, yield to the frame loop every this many ms (lower = smoother, slower to appear) |
| `building.deferOverdueSliceMs` | `40` | same, when the clock has already passed the chunk's start (date jumps): finish sooner, accept a few hitches |
| `building.deferFuture` | `true` | PastForward buildings are built only once the clock nears their construction start (false = all at launch) |
| `building.detailDistance` | `1500` | parapets, roof caps, chimneys hidden beyond this (m) |
| `building.keepProps` | `(list of 49)` | Feature properties kept in memory after load (everything else in the data files is dropped at load — add a name here if new code needs it) |
| `building.floorHeight` | `4.2` | metres per floor (Victorian commercial average) |
| **`building.wingRoof`** | *(group)* | Roofs over complex outlines (> 14 points, or roof_type 'wings'): one ridge per convex wing, ridge height = pitch × half the wing's short side, capped at maxRidgeM |
| `building.wingRoof.auto` | `true` |  |
| `building.wingRoof.pitch` | `0.6` |  |
| `building.wingRoof.maxRidgeM` | `9` | auto: false = complex outlines stay flat unless roof_type 'wings' |
| `building.platformHeight` | `0.6` | low platform/loading-dock structures |
| `building.minHeight` | `2` |  |
| `building.eyeHeight` | `1.75` | walk-mode eye level |
| **`building.parapet`** | *(group)* |  |
| `building.parapet.width` | `0.38` |  |
| `building.parapet.height` | `0.5` |  |
| `building.parapet.stoneWidth` | `0.55` |  |
| `building.parapet.stoneHeight` | `0.8` |  |
| **`building.wallSpecular`** | *(group)* | Specular highlight colour for wall materials (how glossy/shiny under direct light) — most walls use `default`, iron-clad walls are shinier. |
| `building.wallSpecular.default` | `1710618` |  |
| `building.wallSpecular.iron` | `3160120` |  |
| `building.roofSpecular` | `0x080808` |  |
| **`building.roofCap`** | *(group)* | Flat tar-paper roof caps (most common roof type) and stone parapet caps. |
| `building.roofCap.tarPaperColor` | `0x38342E` |  |
| `building.roofCap.tarPaperWinterColor` | `0xF5F6FA` |  |
| `building.roofCap.stoneColor` | `0x505050` |  |
| `building.roofCap.bigAreaM2` | `400` | roofs this big (m², inside the parapet ring) count as "big"… |
| `building.roofCap.bigDistance` | `5000` | …and their gravel caps stay visible this far (others: detailDistance) |
| **`building.parapetSpecular`** | *(group)* | Specular for the upright parapet wall above brick/stone buildings. |
| `building.parapetSpecular.brick` | `1710618` |  |
| `building.parapetSpecular.stone` | `0xC8B890` |  |
| `building.fenceSpecular` | `0x111111` | Shared specular for fence meshes and exposed-lumber stacked-wood walls. |
| **`building.bumpScale`** | *(group)* | UV tiling repeat [u,v] for wall bump/texture maps, per material — how many times the bump image tiles per metre of wall. Bump strength = scale × height change per screen pixel (three r160), so it needs to be several units, not ~0.… |
| `building.bumpScale.default` | `5` |  |
| `building.bumpScale.lumber` | `6` |  |
| `building.bumpScale.iron` | `4` |  |
| `building.bumpScale.roofpeak` | `-6` |  |
| `building.bumpScale.roofgravel` | `6` |  |
| **`building.bumpRepeat`** | *(group)* | repeats per metre = 1 / (size in metres one bump_*.png tile covers) — [along the wall, up] |
| `building.bumpRepeat.brick` | `[0.57,1]` | ~1.75 m × 1.0 m: 13 courses of 7.5 cm, bricks ~22 cm |
| `building.bumpRepeat.brick_veneer` | `[0.57,1]` |  |
| `building.bumpRepeat.stone` | `[0.4,0.4]` | 2.5 m tile, 8 courses ≈ 30 cm |
| `building.bumpRepeat.wood` | `[0.67,0.67]` | 1.5 m tile, 10 clapboards ≈ 15 cm |
| `building.bumpRepeat.log` | `[0.5,0.5]` | 2 m tile, 8 logs ≈ 25 cm |
| `building.bumpRepeat.iron` | `[0.8,0.8]` | 1.25 m tile, 16 ribs ≈ 8 cm |
| `building.bumpRepeat.concrete` | `[0.5,0.5]` |  |
| `building.bumpRepeat.unknown` | `[0.5,0.5]` |  |
| `building.bumpRepeat.lumber` | `[0.67,0.67]` |  |
| `building.bumpRepeat.roofpeak` | `[1,1]` |  |
| `building.bumpRepeat.roofgravel` | `[1,1]` | roofs: 1 m tiles (peaked roofs do their own UVs in the shader) // lumber: 30 boards ≈ 5 cm |

## facade

Building-front facade images (photo overlays + bump maps)

| Key | Default | Notes |
|---|---|---|
| `facade.panelSpecular` | `0x222222` | specular on the photo-textured facade panel |
| `facade.bumpSpecular` | `0x444444` | specular once a normal/bump map is applied |

## roadWidths

metres, by street-type suffix

| Key | Default | Notes |
|---|---|---|
| `roadWidths.BLVD` | `18` |  |
| `roadWidths.HWY` | `16` |  |
| `roadWidths.AVE` | `12` |  |
| `roadWidths.ST` | `10` |  |
| `roadWidths.RD` | `10` |  |
| `roadWidths.DR` | `10` |  |
| `roadWidths.CRES` | `9` |  |
| `roadWidths.WAY` | `9` |  |
| `roadWidths.ROW` | `8` |  |
| `roadWidths.LANE` | `6` |  |
| `roadWidths.PL` | `9` |  |
| `roadWidths.BAY` | `9` |  |
| `roadWidths.PATH` | `5` |  |
| `roadWidths.TRAIL` | `5` |  |

## fences

Fences

| Key | Default | Notes |
|---|---|---|
| **`fences.picket`** | *(group)* | White picket — used for wood fences and the (residential) unknown-material ones. Gap between pickets = width * gapRatio. Height is fixed (the feature's floors value is ignored) — these are ~1 m garden fences. |
| `fences.picket.color` | `0xEEEEE0` |  |
| `fences.picket.width` | `0.09` |  |
| `fences.picket.gapRatio` | `0.5` |  |
| `fences.picket.thickness` | `0.022` |  |
| `fences.picket.height` | `1` |  |
| `fences.picket.postSpacing` | `2.4` |  |
| `fences.picket.postSize` | `0.1` |  |
| `fences.picket.railHeights` | `[0.22,0.72]` |  |
| `fences.picket.railSize` | `[0.04,0.08]` |  |
| `fences.picket.whitenessJitter` | `0.06` | per-fence brightness variation (weathered paint) |
| **`fences.iron`** | *(group)* |  |
| `fences.iron.postColor` | `0x554433` |  |
| `fences.iron.railColor` | `0x665544` |  |
| **`fences.log`** | *(group)* |  |
| `fences.log.postColor` | `0x7A5C3A` |  |
| `fences.log.railColor` | `0x8A6845` |  |
| `fences.log.postSpacing` | `2` |  |
| `fences.log.leanRadians` | `0.3` |  |

## chimneys

Chimneys & building smoke Procedural brick/iron chimney stacks with animated coal-smoke puffs. All distances in world metres (Up≠N: X=east, Y=up, Z=south).

| Key | Default | Notes |
|---|---|---|
| **`chimneys.materials`** | *(group)* | Per-material chimney stack geometry. count: [min,max] shafts placed (max used only for large/tall buildings). radius: [bottomR, topR] in metres. height: [minH, maxH] shaft height in metres (scales with building floors). color: sha… |
| **`chimneys.materials.brick`** | *(group)* |  |
| `chimneys.materials.brick.count` | `[1,2]` |  |
| `chimneys.materials.brick.radius` | `[0.22,0.3]` |  |
| `chimneys.materials.brick.height` | `[1.8,3.5]` |  |
| `chimneys.materials.brick.color` | `0x3A1A0A` |  |
| `chimneys.materials.brick.type` | `"light"` |  |
| **`chimneys.materials.brick_veneer`** | *(group)* |  |
| `chimneys.materials.brick_veneer.count` | `[1,2]` |  |
| `chimneys.materials.brick_veneer.radius` | `[0.2,0.28]` |  |
| `chimneys.materials.brick_veneer.height` | `[1.5,3]` |  |
| `chimneys.materials.brick_veneer.color` | `0x3A1A0A` |  |
| `chimneys.materials.brick_veneer.type` | `"light"` |  |
| **`chimneys.materials.stone`** | *(group)* |  |
| `chimneys.materials.stone.count` | `[1,2]` |  |
| `chimneys.materials.stone.radius` | `[0.28,0.38]` |  |
| `chimneys.materials.stone.height` | `[2,4.5]` |  |
| `chimneys.materials.stone.color` | `0x504030` |  |
| `chimneys.materials.stone.type` | `"light"` |  |
| **`chimneys.materials.wood`** | *(group)* |  |
| `chimneys.materials.wood.count` | `[1,1]` |  |
| `chimneys.materials.wood.radius` | `[0.15,0.22]` |  |
| `chimneys.materials.wood.height` | `[1,2]` |  |
| `chimneys.materials.wood.color` | `0x3A2010` |  |
| `chimneys.materials.wood.type` | `"light"` |  |
| **`chimneys.materials.iron`** | *(group)* |  |
| `chimneys.materials.iron.count` | `[1,2]` |  |
| `chimneys.materials.iron.radius` | `[0.4,0.55]` |  |
| `chimneys.materials.iron.height` | `[3.5,7]` |  |
| `chimneys.materials.iron.color` | `0x1C1C1C` |  |
| `chimneys.materials.iron.type` | `"dark"` |  |
| **`chimneys.materials.wood_industrial`** | *(group)* |  |
| `chimneys.materials.wood_industrial.count` | `[1,2]` |  |
| `chimneys.materials.wood_industrial.radius` | `[0.3,0.45]` |  |
| `chimneys.materials.wood_industrial.height` | `[2.5,5.5]` |  |
| `chimneys.materials.wood_industrial.color` | `0x252018` |  |
| `chimneys.materials.wood_industrial.type` | `"dark"` |  |
| **`chimneys.materials.concrete`** | *(group)* |  |
| `chimneys.materials.concrete.count` | `[0,1]` |  |
| `chimneys.materials.concrete.radius` | `[0.25,0.35]` |  |
| `chimneys.materials.concrete.height` | `[2,4]` |  |
| `chimneys.materials.concrete.color` | `0x383830` |  |
| `chimneys.materials.concrete.type` | `"light"` |  |
| **`chimneys.materials.unknown`** | *(group)* |  |
| `chimneys.materials.unknown.count` | `[0,1]` |  |
| `chimneys.materials.unknown.radius` | `[0.18,0.25]` |  |
| `chimneys.materials.unknown.height` | `[1.2,2.5]` |  |
| `chimneys.materials.unknown.color` | `0x302820` |  |
| `chimneys.materials.unknown.type` | `"light"` |  |
| **`chimneys.materials.log`** | *(group)* |  |
| `chimneys.materials.log.count` | `[1,1]` |  |
| `chimneys.materials.log.radius` | `[0.14,0.18]` |  |
| `chimneys.materials.log.height` | `[0.8,1.5]` |  |
| `chimneys.materials.log.color` | `0x382810` |  |
| `chimneys.materials.log.type` | `"light"` |  |
| **`chimneys.brick`** | *(group)* | Stack styles: footprint under pipeMaxArea (huts, log cabins) keeps the plain stovepipe; heavy-industry buildings over tubeMinAreaDark m², or multi-storey ones (tubeMinFloors, tubeMinArea) get a round tapering brick tube whose heig… |
| `chimneys.brick.pipeMaxArea` | `30` |  |
| `chimneys.brick.tubeMinAreaDark` | `300` |  |
| `chimneys.brick.tubeMinFloors` | `3` |  |
| `chimneys.brick.tubeMinArea` | `500` |  |
| `chimneys.brick.colors` | `[0x8E4A36, 0x9A5240, 0x7C3F2E, 0x6E3A2C, 0x84503C]` |  |
| `chimneys.brick.rectW0` | `0.4` |  |
| `chimneys.brick.rectWPerSqrtArea` | `0.025` |  |
| `chimneys.brick.rectMaxW` | `1.1` |  |
| `chimneys.brick.rectAspect` | `0.7` |  |
| `chimneys.brick.rectExtraH` | `0.5` |  |
| `chimneys.brick.tubeBaseH` | `3.5` |  |
| `chimneys.brick.tubePerFloor` | `0.75` |  |
| `chimneys.brick.tubePerSqrtArea` | `0.075` |  |
| `chimneys.brick.tubeMaxH` | `12` |  |
| `chimneys.brick.tubeR0` | `0.5` |  |
| `chimneys.brick.tubeRPerSqrtArea` | `0.04` |  |
| `chimneys.brick.tubeMinR` | `0.7` |  |
| `chimneys.brick.tubeMaxR` | `2` |  |
| `chimneys.brick.tubeTopRatio` | `0.7` |  |
| `chimneys.minFloors` | `0.5` | Minimum floors before a chimney is placed. |
| `chimneys.placementRadius` | `0.22` | Offset chimneys from building centroid by up to this fraction of √(area_m2). |
| `chimneys.smokePoolSize` | `360` | Shared sprite pool — hard cap on simultaneous smoke sprites city-wide. |
| **`chimneys.smoke`** | *(group)* | Smoke behaviour per type. Ranges are [min,max]; values are randomised per puff. rateBase: seconds between puffs — lower = faster, more overlap, less cartoon-puff look. scaleStart close to scaleEnd means puffs are born large and bl… |
| **`chimneys.smoke.light`** | *(group)* |  |
| `chimneys.smoke.light.opacityRange` | `[0.14,0.28]` |  |
| `chimneys.smoke.light.scaleStart` | `2.2` |  |
| `chimneys.smoke.light.scaleEnd` | `5.5` |  |
| `chimneys.smoke.light.life` | `[3.5,6.5]` |  |
| `chimneys.smoke.light.riseSpeed` | `[1.6,2.8]` |  |
| `chimneys.smoke.light.drift` | `0.4` |  |
| `chimneys.smoke.light.rateBase` | `[0.3,0.65]` |  |
| **`chimneys.smoke.dark`** | *(group)* |  |
| `chimneys.smoke.dark.opacityRange` | `[0.28,0.48]` |  |
| `chimneys.smoke.dark.scaleStart` | `2.8` |  |
| `chimneys.smoke.dark.scaleEnd` | `7.5` |  |
| `chimneys.smoke.dark.life` | `[4,8]` |  |
| `chimneys.smoke.dark.riseSpeed` | `[1,2]` |  |
| `chimneys.smoke.dark.drift` | `0.5` |  |
| `chimneys.smoke.dark.rateBase` | `[0.18,0.4]` |  |
| `chimneys.todCurve` | `[[4,0.35],[6,1.4],[9,0.95],[17,1.2],[20,0.4],[22,0.25]]` | Time-of-day activity curve — multiplier on smoke emission rate. [hour_24h, multiplier] pairs linearly interpolated. |
| **`chimneys.vapor`** | *(group)* | pre-dawn: fires banked overnight morning stoke: coal shovelled, stoves lit daytime: steady industrial + commercial evening: suppers cooking, domestic heating late evening: fires banked night Electrification / gas: residential & co… |
| `chimneys.vapor.yearFrom` | `1915` |  |
| `chimneys.vapor.yearTo` | `1950` |  |
| `chimneys.vapor.heatOn` | `[274,288]` |  |
| `chimneys.vapor.heatOff` | `[121,151]` |  |
| `chimneys.vapor.tint` | `0xDDE0E2` |  |
| `chimneys.vapor.opacity` | `0.8` |  |
| `chimneys.vapor.domesticShare` | `0.75` |  |
| `chimneys.winterMultiplier` | `1.8` | heating load roughly doubles smoke in winter |
| `chimneys.summerMultiplier` | `0.7` | hot months — industrial/cooking only |
| `chimneys.nearDist` | `150` | LOD. Per-chimney puffs come from the nearest in-view chimneys within farDist (3D metres from the camera); the count tapers from maxNearEmitters as the camera climbs from nearDist to farDist above the ground. The city haze layers c… |
| `chimneys.farDist` | `900` |  |
| `chimneys.maxNearEmitters` | `50` |  |
| **`chimneys.cityHaze`** | *(group)* | City-wide coal/wood smoke haze — a few stacked horizontal shader layers over the whole city (see buildCityHaze in index.html). Intensity comes from a source map: building footprint coverage within `radius`, per year from born date… |
| `chimneys.cityHaze.wind` | `[1,0]` | direction smoke travels, world XZ (+X = east): west → east |
| `chimneys.cityHaze.windSpeed` | `14` | m/s the wisps drift (faster than real so it reads as motion) |
| `chimneys.cityHaze.evolve` | `0.025` | how fast wisps change shape as they travel |
| `chimneys.cityHaze.radius` | `100` | metres — neighbourhood for source coverage |
| `chimneys.cityHaze.thresholds` | `[0.03,0.08,0.16,0.3]` | coverage fractions → 4 intensity steps |
| `chimneys.cityHaze.yardWeight` | `45` | m² of "building" per metre of siding track (locomotive smoke) |
| `chimneys.cityHaze.texelMetres` | `20` |  |
| `chimneys.cityHaze.layers` | `(list of 3)` | height (m), opacity scale, upwind reach (m) |
| `chimneys.cityHaze.strength` | `3` | speed: × windSpeed — upper layers faster (parallax) overall opacity at full density & multiplier 1 |
| `chimneys.cityHaze.maxAlpha` | `0.65` |  |
| `chimneys.cityHaze.color` | `0x57534B` | sooty warm grey — the shaded underside, seen from below against the sky |
| `chimneys.cityHaze.colorAbove` | `0x8A7F6C` | seen from above over bare ground: brownish coal smoke, lighter than the dark roofs |
| `chimneys.cityHaze.colorAboveSnow` | `0x3E3830` | seen from above over snow: dark soot (blended by the season's snow cover) |
| `chimneys.cityHaze.aboveBoost` | `0.15` | opacity multiplier when seen from above (<1: looking down through all layers stacks up fast) |
| `chimneys.cityHaze.fadeYears` | `3` | a source ramps up over this many years after its buildings appear |
| `chimneys.cityHaze.nearFade` | `[40,220]` | metres from camera: transparent → full |

## terrain

Terrain Subdivided ground mesh with gentle prairie noise + river channel deformation. After water GeoJSON loads, terrain vertices near river paths are depressed so the flood plane (water) becomes visible in the channel at low wate…

| Key | Default | Notes |
|---|---|---|
| `terrain.segments` | `600` | mesh subdivisions (20 m grid; the 1201² DEM is resampled) — was 1200, ~2.2M triangles more |
| **`terrain.smooth`** | *(group)* | DEM smoothing at load: removes modern street/lot relief (the "waffle" the dirt line traced) while keeping riverbanks — see smoothDEM in index.html |
| `terrain.smooth.radiusM` | `30` |  |
| `terrain.smooth.keepBelowM` | `0.5` |  |
| `terrain.smooth.keepAboveM` | `1.5` |  |
| **`terrain.smooth.flatten`** | *(group)* | then: everything away from the riverbanks (slope > bankSlope, +bufferM) pulled toward a wide average of that ground — bumps halve, banks untouched, regional rise kept (strength 0 = off; see flattenDEM) |
| `terrain.smooth.flatten.radiusM` | `300` |  |
| `terrain.smooth.flatten.strength` | `0.85` |  |
| `terrain.smooth.flatten.bankSlope` | `0.08` |  |
| `terrain.smooth.flatten.bufferM` | `40` |  |
| `terrain.smooth.flatten.featherM` | `20` |  |
| `terrain.smooth.flatten.minAboveWater` | `1` |  |
| `terrain.smooth.flatten.maxMoveM` | `2.5` | minAboveWater: below startY+this = river channel (St Boniface ground sits ~2 m above normal water) |
| `terrain.riverGaps` | `(list of 7)` | Brown's Creek: a shallow valley carved along its line while it exists (filled in since — the LiDAR is flat there); cosine profile, metres Short segments a→b [lon,lat] along the Seine through the spots where bridge decks cut the Li… |
| **`terrain.creek`** | *(group)* | the viewer-mesh check above had left Provencher out of its window; the real break is ~45 m south-east of the first cut: found by labelling the water cells of the viewer's own terrain mesh (what you actually see), after the cuts ab… |
| `terrain.creek.marshFile` | `"./data/early_marshes.json"` |  |
| **`terrain.creek.bridge`** | *(group)* |  |
| `terrain.creek.bridge.roads` | `null` |  |
| `terrain.creek.bridge.creeks` | `"."` |  |
| `terrain.creek.bridge.length` | `22` |  |
| `terrain.creek.bridge.width` | `12` |  |
| `terrain.creek.bridge.minWidth` | `5` |  |
| `terrain.creek.bridge.clusterM` | `30` |  |
| `terrain.creek.bridge.color` | `0x5D4A36` |  |
| `terrain.creek.bridge.file` | `"./data/early_bridges.json"` | bridges listed in data (centre, span axis, length, width) — Mike's, from satellite imagery; extra: [] would hand-list more by creek + metres from its mouth // timber bridge wherever a street crosses a creek while both exist (roads… |
| `terrain.creek.toRiver` | `true` |  |
| `terrain.creek.eastOfLon` | `-97.1328` |  |
| `terrain.creek.riverEdgeAbove` | `0.3` |  |
| `terrain.creek.extendStepM` | `6` |  |
| `terrain.creek.extendMaxM` | `400` |  |
| `terrain.creek.seekRiver` | `["fort rouge"]` |  |
| `terrain.creek.seekMaxM` | `250` | creeks whose end is carried down the low ground to the river's edge |
| `terrain.creek.depth` | `1.3` |  |
| `terrain.creek.halfWidth` | `8` |  |
| `terrain.creek.stepM` | `3` |  |
| `terrain.creek.across` | `10` |  |
| `terrain.creek.cutShare` | `0.9` |  |
| `terrain.creek.endTaperM` | `15` |  |
| `terrain.creek.dirt` | `1` | shallower and narrower (was 2.5 m deep, 28 m wide) // one valley field over all pieces; terrain cut over the inner 90%; free ends ease out over endTaperM; bank-dirt floor (0 = grass) |
| **`terrain.oxbow`** | *(group)* | The cut-off oxbow east of the Forks (St Boniface/Norwood): found in the LiDAR (relBelowM under a contextM-wide average, inside bbox lon/lat [W, S, E, N], clear of the river banks), kept out of the flattening, deepened (deepenM at … |
| `terrain.oxbow.bbox` | `[-97.12826,49.87671,-97.10972,49.88839]` |  |
| `terrain.oxbow.contextM` | `300` |  |
| `terrain.oxbow.relBelowM` | `-0.35` |  |
| `terrain.oxbow.deepenM` | `1.5` |  |
| `terrain.oxbow.deepenRampM` | `0.8` |  |
| **`terrain.oxbow.lake`** | *(group)* |  |
| `terrain.oxbow.lake.fill` | `(list of 8)` | fill 0..1 of the basin by date — spring melt, draining through summer, a little fall rain |
| `terrain.oxbow.lake.wetEffect` | `0.7` | × (1 + moisture·wetEffect): wet summers fuller, drought dry |
| `terrain.oxbow.lake.maxDepthM` | `1.6` |  |
| `terrain.oxbow.lake.color` | `0x4A5236` |  |
| `terrain.oxbow.lake.opacity` | `0.88` |  |
| `terrain.oxbow.lake.iceColor` | `0xC8D2DC` |  |
| `terrain.oxbow.lake.mosquitoAnchors` | `70` |  |
| `terrain.oxbow.lake.until` | `"1910-04-15"` | filled in: ground back to today's levels from spring 1910, no lake |
| `terrain.noiseAmplitude` | `0.8` | metres of prairie undulation — enough for interesting flood spread |
| `terrain.noiseBaseY` | `0` | baseline Y for terrain surface (buildings sit at y=0) |
| `terrain.channelDepth` | `5.5` | metres the channel floor sits below bank level (y=0) |
| `terrain.channelBlendWidth` | `160` | metres from river CENTERLINE to flat prairie (covers bank + slope) |
| **`terrain.bankDirt`** | *(group)* | Bare riverbank: terrain below (water.startY + aboveWater) fades from grass to dirt over `blend` metres. Tied to the INITIAL water level, not the flood slider. `jitter` wobbles the line so it isn't a contour ring. Summer only — ban… |
| `terrain.bankDirt.color` | `0x3F3427` |  |
| `terrain.bankDirt.aboveWater` | `3` |  |
| `terrain.bankDirt.blend` | `1.5` |  |
| `terrain.bankDirt.jitter` | `0.4` |  |
| **`terrain.groundCover`** | *(group)* | Summer ground cover — breaks the flat green up (shader, no textures). Base grass tone is scene.ground.summerColor; noise at a few scales mixes in a second green, dry straw patches and brightness mottling. Around buildings, a densi… |
| `terrain.groundCover.grassAlt` | `3822112` | second green mixed in at ~400 m patch scale |
| `terrain.groundCover.grassDry` | `7236154` | late-summer straw / dry prairie grass patches |
| `terrain.groundCover.dryAmount` | `0.55` | 0 = no straw patches |
| `terrain.groundCover.mottle` | `0.22` | ± brightness variation at ~15 m scale |
| `terrain.groundCover.yardDirt` | `5524275` | trampled yards / lanes: patchy with grass |
| `terrain.groundCover.coreDirt` | `5129528` | packed mud, cinders, manure — dense downtown |
| `terrain.groundCover.radius` | `40` | metres — neighbourhood for footprint coverage |
| `terrain.groundCover.yardCoverage` | `0.1` | footprint fraction where yards start going to dirt |
| `terrain.groundCover.coreCoverage` | `0.35` | footprint fraction treated as dense core |
| `terrain.groundCover.fadeYears` | `4` | years for a spot to wear from grass to dirt |
| `terrain.groundCover.texelMetres` | `10` | density-map resolution (capped at 1024 texels/side) |

## water

Water

| Key | Default | Notes |
|---|---|---|
| `water.color` | `0x7A5230` |  |
| `water.specular` | `0x3A2810` |  |
| `water.winterColor` | `0xBBCCE8` |  |
| `water.winterSpecular` | `0x8899CC` |  |
| `water.floodPeakColor` | `0x5A3A20` | Colour the water tints toward as the flood slider is dragged to its maximum (muddier, browner) — lerped with `color` at slider value. |
| `water.baseY` | `-10` | baseY: the Y level of the flood plane at slider=0. With real LiDAR DEM: Red River valley floor is ~3–5m below bank level. Set low enough that the plane starts fully inside the channel at rest. flood plane Y at slider=0 (fully dry … |
| `water.startY` | `-5.8` | reference ("normal") river level, world Y — date levels below are relative to this |
| **`water.levels`** | *(group)* | River level by date. levelAt(date) = historical record if one is near the date, else the fake seasonal curve below; the flood slider adds a manual offset on top. Everything that floats (boats, floes) follows. |
| `water.levels.seasonal` | `[["04-14",-0.8],["04-22",2.5],["11-25",-0.8]]` | Fake seasonal curve, metres relative to startY: low under the ice, quick rise at break-up to the spring high, then a straight decline to the lowest level just before freeze-up. ['MM-DD', metres]. |
| `water.levels.yearVariation` | `0.35` | ± fraction on the spring rise, seeded by year (same year → same level) |
| `water.levels.historyFile` | `"./data/water_levels.json"` | Optional real data, loaded if present. Format: { "datum": "relative" \| "asl" \| "james_ft", "records": [["1913-04-28", 12.4], ...] } relative: metres vs startY · asl: metres above sea level (via the DEM's refElev) james_ft: feet on… |
| `water.levels.maxGapDays` | `75` | interpolate between records at most this far apart; else fall back to seasonal |
| `water.levels.trueAbove` | `-2` | One flat water surface serves both rivers, and the Assiniboine's bed sits ~2 m above the Red's — so at normal/low water the surface is held at startY (the real level + an offset), blending to the TRUE elevation as the river rises … |
| **`water.confluence`** | *(group)* | Assiniboine → Red confluence plume (faked in the water shader). The lighter, siltier Assiniboine water hugs the Red's west bank heading north and has mixed out by Esplanade Riel. Path is lon/lat (modern, like the river data — offs… |
| `water.confluence.path` | `(list of 6)` |  |
| `water.confluence.widthStart` | `60` |  |
| `water.confluence.widthEnd` | `120` | metres, full plume width |
| `water.confluence.edgeNoise` | `18` | metres of wobble on the plume edge |
| `water.confluence.color` | `0x8A6A45` | Assiniboine water — a touch lighter/tanner than the Red |
| `water.confluence.colorMix` | `0.35` | how far toward `color` at full strength (subtle) |
| `water.confluence.specularMult` | `1.8` |  |
| `water.confluence.shininessMult` | `0.55` | siltier water: broader, brighter sheen |
| `water.confluence.flowSpeed` | `0.35` | m/s the edge noise drifts downstream |
| `water.riverHalfWidth` | `120` |  |
| `water.creekHalfWidth` | `8` |  |
| **`water.widths`** | *(group)* |  |
| `water.widths.brownsCreek` | `3` |  |
| `water.widths.redRiver` | `220` |  |
| `water.widths.assiniboineRiver` | `85` |  |
| `water.widths.seineRiver` | `22` |  |
| `water.brownsCreekColor` | `0x2E6058` | Brown's Creek: a small clear prairie creek — no glacial silt, no Red River brown. Dark teal-green reads as shallow moving water in a 3D scene. |
| `water.floodMaxRiseMetres` | `12.5` | historic 1826-flood-scale peak at slider=1.0 → water at +9.5m |
| `water.offsetZ` | `-30` | Geographic registration offset applied to all river/water geometry. The NHD river data (modern GPS) is slightly north of the Goad's Atlas building data (historically georeferenced ~1906). Positive values shift water SOUTH (increas… |

## rail

Rail / tracks

| Key | Default | Notes |
|---|---|---|
| `rail.color` | `0x24262C` |  |
| `rail.specular` | `0xB8BEC8` |  |
| `rail.shininess` | `90` | train rails: dark steel, polished running surface catches the light |
| `rail.streetcarRailColor` | `0x1C1C1E` |  |
| `rail.streetcarRailSpecular` | `0x9EA4AC` |  |
| `rail.streetcarRailShininess` | `80` |  |
| `rail.railHeadWidth` | `0.12` | Streetcar rails — one mesh per route, bucketed by streetcar_start year: |
| `rail.railHeight` | `0.22` |  |
| `rail.trainRailHeadWidth` | `0.1` | Freight/passenger train rails (slightly slimmer in this model): |
| `rail.trainRailHeight` | `0.2` |  |
| `rail.gaugeHalfWidth` | `0.7175` |  |
| `rail.throughLineBedWidth` | `4` |  |
| `rail.sidingBedWidth` | `2.4` |  |
| `rail.minVisibleYear` | `1881` | The freight/passenger rail network is hidden before this year on the timeline. ~1881 = the CPR main line reaching Winnipeg (approximate — not a hard historical date; adjust here). NOTE: the full 1906 network is drawn from this yea… |

## bridges

Bridges (type:'bridge' features) Rectangular bridge footprints with a long side ≥ minSpan are drawn as open structures instead of solid slabs: a steel through-truss when the span crosses water (ground under it dips below water.sta…

| Key | Default | Notes |
|---|---|---|
| **`bridges.truss`** | *(group)* |  |
| `bridges.truss.maxSpan` | `60` | metres between stone piers |
| `bridges.truss.pierThickness` | `3` |  |
| `bridges.truss.panelLength` | `7` | target panel width; rounded to an even panel count per span |
| `bridges.truss.heightRatio` | `7` | truss height ≈ span / heightRatio, clamped below |
| `bridges.truss.minHeight` | `5` |  |
| `bridges.truss.maxHeight` | `9` |  |
| `bridges.truss.camelbackSpan` | `45` | spans at least this long get a curved (Parker) top chord |
| `bridges.truss.maxOverheadWidth` | `16` | wider decks skip overhead lateral bracing (would look absurd) |
| `bridges.truss.chordSize` | `0.45` |  |
| `bridges.truss.verticalSize` | `0.3` |  |
| `bridges.truss.diagonalSize` | `0.22` |  |
| `bridges.truss.lateralSize` | `0.16` |  |
| **`bridges.fit`** | *(group)* |  |
| `bridges.fit.bankAboveWaterM` | `1.5` |  |
| `bridges.fit.marginM` | `14` |  |
| `bridges.fit.maxHalfM` | `500` | bridge_fit: ends land where ground rises this far above normal water, + margin |
| `bridges.rampLength` | `40` | metres past each deck end over which roads/rails ease back to grade |
| `bridges.rampGrade` | `0.04` | 1:25 approach slope |
| `bridges.alignCos` | `0.8` | \|cos\| between travel direction and span to count as "on" the bridge (~37°) |
| `bridges.minSpan` | `15` | metres — long side below this → plain slab |
| `bridges.bentSpacing` | `12` | metres between trestle bents along the span |
| `bridges.maxLegSpacing` | `6` | metres between legs across a bent (wide decks get more legs) |
| `bridges.braceLevel` | `4` | metres between horizontal bracing levels on a bent |
| `bridges.minClearance` | `4.5` | deck underside at least this far above the lowest ground under it |
| `bridges.deckThickness` | `0.35` |  |
| `bridges.girderDepth` | `1` |  |
| `bridges.railingHeight` | `1.1` |  |
| `bridges.railingPostSpacing` | `2.5` |  |
| `bridges.legSize` | `0.35` |  |
| `bridges.braceSize` | `0.14` |  |
| `bridges.railSize` | `0.1` |  |
| `bridges.batter` | `0.08` | outer-leg splay per metre of leg height |
| `bridges.abutmentLength` | `3` |  |
| **`bridges.colors`** | *(group)* |  |
| `bridges.colors.steel` | `3093560` | dark painted steel |
| `bridges.colors.timber` | `5981746` | members for wood-material bridges |
| `bridges.colors.deck` | `4867392` |  |
| `bridges.colors.stone` | `0x8A8378` | abutments + footings |

## steamboats

River steamboats Sternwheelers plying the Red/Assiniboine, with stack smoke and a foam + Kelvin-arm wake. `boats` = how many can be out at once (by year); `presence` = fraction of time each of those is on the river (linear between…

| Key | Default | Notes |
|---|---|---|
| `steamboats.presence` | `(list of 14)` |  |
| `steamboats.boats` | `(list of 12)` |  |
| `steamboats.dockedYears` | `[1859.44,1890]` |  |
| `steamboats.assiniboineShare` | `(list of 6)` | Share of trips that come down the Assiniboine (then continue down the Red) rather than running the Red — Assiniboine boom 1879–85 (to Portage/Brandon). |
| **`steamboats.speed`** | *(group)* |  |
| `steamboats.speed.upstream` | `3` |  |
| `steamboats.speed.downstream` | `4.2` | m/s; the Red flows north, the Assiniboine east |
| `steamboats.draft` | `0.45` | metres of hull below the waterline |
| **`steamboats.dock`** | *(group)* |  |
| `steamboats.dock.lon` | `-97.13226` |  |
| `steamboats.dock.lat` | `49.8859` |  |
| `steamboats.dock.heading` | `90` | moored against the landing's T-head; heading ° (0=N, 90=E) |
| **`steamboats.colors`** | *(group)* |  |
| `steamboats.colors.hull` | `0xE6E0CE` |  |
| `steamboats.colors.cabin` | `0xF1EDE1` |  |
| `steamboats.colors.roof` | `0x6B6255` |  |
| `steamboats.colors.trim` | `0x3A3530` |  |
| `steamboats.colors.stack` | `1973274` |  |
| `steamboats.colors.wheel` | `0x8B2A1E` |  |
| **`steamboats.wake`** | *(group)* |  |
| `steamboats.wake.length` | `160` |  |
| `steamboats.wake.foamColor` | `0xD9D2BF` |  |
| `steamboats.wake.foamAlpha` | `0.45` |  |
| `steamboats.wake.armAlpha` | `0.28` |  |
| `steamboats.wake.armAngleDeg` | `19.5` |  |
| `steamboats.smokeTint` | `0x8C8883` | wood-fired: greyer than the locomotives |
| **`steamboats.smoke`** | *(group)* |  |
| `steamboats.smoke.puffs` | `24` |  |
| `steamboats.smoke.life` | `[4.5,6.5]` |  |
| `steamboats.smoke.size0` | `3` |  |
| `steamboats.smoke.grow` | `9` |  |
| `steamboats.smoke.opacity` | `0.6` |  |
| `steamboats.smoke.rise` | `2.2` |  |
| `steamboats.smoke.interval` | `0.28` | plume per stack: puff pool, life s, start size m, growth m, opacity, climb m/s, s between puffs |
| **`steamboats.routes`** | *(group)* | River centrelines (lon/lat, modern river data — water offsetZ applied), derived by marching perpendicular cross-sections of wpg_rivers.geojson. Index order is downstream (Red south→north; Assiniboine west→Forks). |
| `steamboats.routes.red` | `(list of 102)` |  |
| `steamboats.routes.assiniboine` | `(list of 48)` |  |

## roadHistory

Road history segments: segment_id (wpg_roads_streetcar.geojson) → [born, died] ISO dates (null = open), intersected with the usual nearby-building span. extra: period roads that aren't in the modern data — lon/lat path. Main St ra…

| Key | Default | Notes |
|---|---|---|
| **`roadHistory.bend`** | *(group)* | Early streets wander: a smooth displacement field (amp metres) that fades out between fromYear and toYear as the town straightens its streets. amp 0 = off. |
| `roadHistory.bend.amp` | `7` |  |
| `roadHistory.bend.fromYear` | `1880` |  |
| `roadHistory.bend.toYear` | `1905` |  |
| `roadHistory.bend.corner` | `12` | corner = how far back (m) the inside of junction corners is filled |
| **`roadHistory.segments`** | *(group)* |  |
| `roadHistory.segments.12728` | `["1881-01-01",null]` |  |
| `roadHistory.segments.12729` | `["1881-01-01",null]` |  |
| `roadHistory.extra` | `(list of 1)` | Main St, bridge head → through the SE wall Main St, through the NE bastion → north |

## nightLights

Window lights through the night litShare of windows are lit after dark; of those above the ground floor, `lateness` (by clock hour, the TIME slider runs 04:00–22:00) are switched off — each window at its own random point, so build…

| Key | Default | Notes |
|---|---|---|
| `nightLights.litShare` | `0.62` |  |
| `nightLights.lateness` | `[[4,0.85],[5.5,0.85],[6.5,0.55],[8,0.3],[17,0],[20,0.1],[22,0.45]]` |  |
| `nightLights.paneCellM` | `2.2` | real glass panes: windows hashed on this grid |

## streetLights

Street lights First electric arc street lamps: Main St, October 1882 (Manitoba Electric Light & Power, P.V. Carroll); the North West Electric Light & Power Co. lit the streets from June 1883 (MHS). Arc lamps on tall poles at inter…

| Key | Default | Notes |
|---|---|---|
| `streetLights.arcFrom` | `"1883-06-01"` |  |
| `streetLights.postsFrom` | `"1908-01-01"` |  |
| `streetLights.radius` | `2600` | metres from the scene origin |
| `streetLights.spacing` | `45` | metres between block lamps (alternating sides) |
| `streetLights.poolOpacity` | `0.55` |  |
| **`streetLights.arc`** | *(group)* |  |
| `streetLights.arc.height` | `9` |  |
| `streetLights.arc.arm` | `1.6` |  |
| `streetLights.arc.headSize` | `0.32` |  |
| `streetLights.arc.color` | `0x2A2622` |  |
| `streetLights.arc.glow` | `0xF2F0FF` |  |
| `streetLights.arc.poolRadius` | `16` | arc light: bluish white |
| **`streetLights.post`** | *(group)* |  |
| `streetLights.post.height` | `4.6` |  |
| `streetLights.post.arm` | `0.5` |  |
| `streetLights.post.headSize` | `0.24` |  |
| `streetLights.post.color` | `0x1E2A22` |  |
| `streetLights.post.glow` | `0xFFD49A` |  |
| `streetLights.post.poolRadius` | `9` | incandescent: warm |

## parades

Parades (recorded dates) A marching column (band in front, flags) loops the route all day, with crowds lining both sidewalks. Slow play lingers on parade days like storms (timeline.events). Routes are lon/lat along the street cent…

| Key | Default | Notes |
|---|---|---|
| **`parades.routes`** | *(group)* |  |
| `parades.routes.mainFromCPR` | `(list of 10)` |  |
| `parades.routes.cityHallToPortage` | `(list of 9)` |  |
| `parades.halfWidth` | `15` |  |
| `parades.speed` | `1.3` | m/s marching |
| **`parades.decor`** | *(group)* |  |
| `parades.decor.spacing` | `30` |  |
| `parades.decor.poleHeight` | `7` |  |
| `parades.decor.colors` | `[0xB02020, 0xF2F2F2, 0x1A3A8A]` | flag poles + pennant strings along the route |
| **`parades.fadeIn`** | *(group)* |  |
| `parades.fadeIn.crowdSeconds` | `4` |  |
| `parades.fadeIn.flagStepSeconds` | `0.06` |  |
| `parades.fadeIn.rankStepSeconds` | `0.04` | staggered arrival |
| `parades.trafficClearM` | `25` | streetcars/carts this close to the route are off the street during a parade |
| `parades.list` | `(list of 9)` |  |

## mosquitoes

Mosquitoes Faint swirling specks over still water (Brown's Creek, while it exists), only visible within `fade` metres. seasonDays = day-of-year ramp [start, full, full-until, end] (≈ May 20 · Jun 10 · Aug 10 · Sep 5).

| Key | Default | Notes |
|---|---|---|
| `mosquitoes.perAnchor` | `40` |  |
| `mosquitoes.maxAnchors` | `2400` | (was 400 — the early creeks pushed the oxbow's anchors past the cap, so its clouds never drew) |
| `mosquitoes.color` | `0x121212` |  |
| `mosquitoes.opacity` | `0.8` |  |
| `mosquitoes.fade` | `[30,160]` | metres from the camera: fully drawn inside the first, gone by the second |
| **`mosquitoes.cloud`** | *(group)* |  |
| `mosquitoes.cloud.puffs` | `4` |  |
| `mosquitoes.cloud.size` | `4.5` |  |
| `mosquitoes.cloud.opacity` | `0.2` |  |
| `mosquitoes.cloud.maxPx` | `140` |  |
| `mosquitoes.cloud.fade` | `[40,260]` |  |
| `mosquitoes.cloud.color` | `0x1A1816` | the smoky band over standing water, ~1–3 m up: puffs per anchor, metres across, peak opacity, px cap, fade distances, colour |
| `mosquitoes.sizeK` | `60` |  |
| `mosquitoes.size` | `[1.6,3.6]` | point size in px = sizeK/distance, clamped (× pixel ratio) — was 26/d clamped to 1–2.2 px: easy to miss |
| `mosquitoes.seasonDays` | `[140,161,222,248]` |  |
| `mosquitoes.wetBoost` | `0.8` | × (1 + wet) in wet summers (seasons.moisture) |
| `mosquitoes.dayLevel` | `0.35` |  |
| `mosquitoes.duskBoost` | `1.6` |  |

## postcards

Postcard views data/postcard_views.json (optional) — see tools/postcard_views_FORMAT.md. A badge shows when the camera is within matchRadiusM of a card's viewpoint and looking within matchAzDeg / matchElDeg of its heading / pitch;…

| Key | Default | Notes |
|---|---|---|
| `postcards.file` | `"./data/postcard_views.json"` |  |
| `postcards.matchRadiusM` | `40` |  |
| `postcards.matchAzDeg` | `35` |  |
| `postcards.matchElDeg` | `25` |  |
| `postcards.nearbyRadiusM` | `400` |  |
| `postcards.listMax` | `8` |  |
| `postcards.matchListMax` | `20` |  |
| `postcards.sameDateDays` | `7` | listMax = nearby rows; matchListMax = matching rows |
| `postcards.defaultHeightM` | `2.5` |  |
| `postcards.defaultOpacity` | `0.5` |  |
| `postcards.jumpDate` | `true` |  |
| `postcards.eraFilter` | `true` | Photo era (year_low..year_high): a card matches a view only while the viewer's year is inside it (± dateSlackYears); cards with no years match any era. Records farther than maxDistanceKm from the model are skipped as bad data. |
| `postcards.dateSlackYears` | `2` |  |
| `postcards.maxDistanceKm` | `500` |  |
| `postcards.checkEveryMs` | `250` |  |

## utilityPoles

Utility poles and wires (walk mode only, around the camera) Telegraph reached the settlement in 1871 (Main St here); Winnipeg's first telephone exchange 1881 — early lines ran roof to roof, poles only "when the phone people ran ou…

| Key | Default | Notes |
|---|---|---|
| `utilityPoles.telegraphFrom` | `1871.85` |  |
| `utilityPoles.majorFrom` | `1882` |  |
| `utilityPoles.allFrom` | `1900` |  |
| `utilityPoles.majorStreets` | `(list of 18)` |  |
| **`utilityPoles.wires`** | *(group)* |  |
| `utilityPoles.wires.telegraph` | `2` |  |
| `utilityPoles.wires.major` | `4` |  |
| `utilityPoles.wires.all` | `8` |  |
| `utilityPoles.radius` | `350` |  |
| `utilityPoles.rebuildDistance` | `90` |  |
| `utilityPoles.orbitMaxAltitude` | `120` | the orbit camera also shows poles/wires when it is within this height of the ground (walk mode always does) |
| `utilityPoles.spacing` | `38` |  |
| `utilityPoles.kerbOffset` | `1` |  |
| `utilityPoles.height` | `9.5` |  |
| `utilityPoles.armLength` | `2.2` |  |
| `utilityPoles.sag` | `0.7` |  |
| `utilityPoles.sagSegments` | `4` |  |
| `utilityPoles.color` | `0x5A4A3A` |  |
| `utilityPoles.wireColor` | `0x1A1816` |  |

## cues

Event cues When a parade or a fire starts, a pulsing column of light rises over it for a few seconds so you can find it; the caption under the date bar names it — click it to fly there.

| Key | Default | Notes |
|---|---|---|
| `cues.beacon` | `true` |  |
| `cues.beaconHeight` | `160` |  |
| `cues.beaconRadius` | `7` |  |
| `cues.beaconSeconds` | `6` |  |
| `cues.beaconOpacity` | `0.35` |  |

## shanties

Shantytown in the CNR East Yards Ramshackle huts and cabins beside the yard tracks (areaWorld = world x0,z0,x1,z1 box around the East Yards at the Forks). Each goes up in `years`, lasts `lifeYears`, and is displaced early by any b…

| Key | Default | Notes |
|---|---|---|
| `shanties.areaWorld` | `[-700,-700,900,1100]` | areaWorld = world x0,z0,x1,z1: the East Yards at the Forks plus open ground west and north of them. Huts go beside yard tracks (trackShare) or on open ground, up to permanentClearM from any permanent structure that stands at the t… |
| `shanties.count` | `170` |  |
| `shanties.trackShare` | `0.45` | was 70 — more huts (the clearance rules still thin them out) |
| `shanties.years` | `[1882,1938]` |  |
| `shanties.lifeYears` | `[4,18]` |  |
| `shanties.trackClearM` | `6` |  |
| `shanties.spreadM` | `22` |  |
| `shanties.minSpacingM` | `7` |  |
| `shanties.permanentClearM` | `100` |  |
| `shanties.size` | `[2.4,4.2]` |  |
| `shanties.colors` | `[0x6A6058, 0x5A4E42, 0x7A6E60, 0x4A4440, 0x6E5A44, 0x3A3632]` |  |

## autos

Automobiles First cars in Winnipeg c. 1901–03; common by the 1910s–20s. count = cars on the road by year (around the camera — they respawn within spawnRadiusM). Early: tall, boxy, mostly black; from modernFrom: lower, longer, colo…

| Key | Default | Notes |
|---|---|---|
| `autos.count` | `[[1902,0],[1905,3],[1912,20],[1920,45],[1930,70],[1945,95],[1955,140]]` |  |
| `autos.max` | `150` |  |
| `autos.scale` | `1` |  |
| `autos.spawnRadiusM` | `900` |  |
| `autos.modernFrom` | `1928` |  |
| `autos.speedEarly` | `6` |  |
| `autos.speedLate` | `10` |  |
| `autos.colorsEarly` | `[0x141414, 0x1E2A3A, 0x3A1E1E, 0x2A3A2A]` |  |
| `autos.colorsLate` | `[0x141414, 0x5A6E8A, 0x7A2A24, 0x2E4A3A, 0xB8B0A0, 0x8A7A5A, 0x3A4A6A]` |  |

## fireEngines

Fire engines Run in along the nearest street when a building catches fire and park there until it's out. Winnipeg: volunteer brigade 1874 (from); first motorised apparatus 1910 (a Webb hose wagon); all first-line apparatus motor b…

| Key | Default | Notes |
|---|---|---|
| `fireEngines.from` | `1874` |  |
| `fireEngines.motorFrom` | `1910` |  |
| `fireEngines.motorShare` | `[[1910,0.05],[1920,0.4],[1929,0.95],[1934.5,1]]` |  |
| `fireEngines.lightsFrom` | `1930` |  |
| `fireEngines.beaconFrom` | `1946` |  |
| `fireEngines.sirenFrom` | `1915` |  |
| `fireEngines.approach` | `180` | metres driven in along the street |
| `fireEngines.horseSpeed` | `6` |  |
| `fireEngines.motorSpeed` | `11` |  |
| `fireEngines.maxPerFire` | `3` |  |
| `fireEngines.maxRoadDistance` | `40` |  |
| `fireEngines.stayUntil` | `0.8` | fraction of the fire window they stay for |
| `fireEngines.red` | `11018266` |  |

## docks

Floating docks Flat (floors ≤ 0.2) river structures named dock / landing / wharf / pier are pulled out of the merged city mesh and ride the river level. In a major flood they break loose and drift downstream (spinning slowly), and…

| Key | Default | Notes |
|---|---|---|
| `docks.freeboard` | `0.35` | deck height above the water |
| `docks.thickness` | `0.55` |  |
| `docks.color` | `0x7A6448` |  |
| `docks.breakAboveMetres` | `4.5` |  |
| `docks.replaceBelowMetres` | `2` |  |
| `docks.driftSpeed` | `1.8` | m/s downstream |
| `docks.spin` | `0.06` | rad/s while adrift |

## smallCraft

Small craft Canoes (birchbark to ~1900, painted canvas after), HBC York boats (Red River brigades, fading out once steamboats took the freight, gone by the late 1870s), rowboats / skiffs (pleasure boating from the 1870s; Winnipeg …

| Key | Default | Notes |
|---|---|---|
| **`smallCraft.canoe`** | *(group)* |  |
| `smallCraft.canoe.count` | `[[1850,6],[1880,3],[1900,4],[1960,5]]` |  |
| `smallCraft.canoe.speed` | `1.3` |  |
| `smallCraft.canoe.length` | `5.2` |  |
| `smallCraft.canoe.beam` | `0.9` |  |
| `smallCraft.canoe.birchUntil` | `1900` |  |
| `smallCraft.canoe.birch` | `10123858` |  |
| `smallCraft.canoe.canvas` | `[3038778,9120286,13220239,2771562,7236190]` |  |
| **`smallCraft.york`** | *(group)* |  |
| `smallCraft.york.count` | `[[1850,2],[1865,2],[1872,1],[1878,0]]` |  |
| `smallCraft.york.speed` | `1.1` |  |
| `smallCraft.york.length` | `12` |  |
| `smallCraft.york.beam` | `3` |  |
| `smallCraft.york.color` | `0x7A5E3E` |  |
| `smallCraft.york.sail` | `14867656` |  |
| **`smallCraft.rowboat`** | *(group)* |  |
| `smallCraft.rowboat.count` | `[[1868,0],[1882,3],[1912,5],[1935,3],[1960,2]]` |  |
| `smallCraft.rowboat.speed` | `0.9` |  |
| `smallCraft.rowboat.length` | `4.4` |  |
| `smallCraft.rowboat.beam` | `1.3` |  |
| `smallCraft.rowboat.colors` | `[0xE6E0CE, 0x3E5A6E, 0x7A5E3E, 0x8B2A1E]` |  |
| **`smallCraft.launch`** | *(group)* |  |
| `smallCraft.launch.count` | `[[1904,0],[1910,2],[1930,3],[1960,3]]` |  |
| `smallCraft.launch.speed` | `3.5` |  |
| `smallCraft.launch.length` | `8` |  |
| `smallCraft.launch.beam` | `2.1` |  |
| `smallCraft.launch.color` | `0xEDE8DA` |  |
| `smallCraft.launch.cabin` | `0x7A5E3E` |  |
| `smallCraft.redShare` | `0.65` | share on the Red (rest on the Assiniboine) |
| `smallCraft.stretch` | `[350,1400]` | metres of river each boat works back and forth |
| `smallCraft.rower` | `2762274` | people |

## ferries

Ferries Crossings before the bridges. lon/lat = a point mid-river on the crossing (midpoints of the landings in trees.ferries, which keep the banks clear); the ferry runs perpendicular to the river there, bank to bank. • Winnipeg–…

| Key | Default | Notes |
|---|---|---|
| `ferries` | `(list of 3)` | Ferries Crossings before the bridges. lon/lat = a point mid-river on the crossing (midpoints of the landings in trees.ferries, which keep the banks clear); the ferry runs perpendicular to the river there, bank to bank. • Winnipeg–… |

## ferryTiming

north landing 30 m east of the Main St line: Dept. of Resources & Development 1952 plan A-68 (Upper Fort Garry); estimated from the sheet

| Key | Default | Notes |
|---|---|---|
| `ferryTiming.crossSeconds` | `70` |  |
| `ferryTiming.dwellSeconds` | `25` |  |
| `ferryTiming.bankAboveWaterM` | `0.4` | a landing is where the ground rises this far above normal water |
| `ferryTiming.onBankM` | `1` | …plus this far onto it (the ramp touches the bank) |

## windmills

Windmills Red River Settlement tower mills (18 by 1856, 13 of them in St John, St Paul and St Andrew north of the Forks). Only those I could place from the sources are listed; positions are APPROXIMATE (±200 m). • Robert Logan's m…

| Key | Default | Notes |
|---|---|---|
| `windmills.list` | `(list of 2)` |  |
| **`windmills.tower`** | *(group)* |  |
| `windmills.tower.baseR` | `3.3` |  |
| `windmills.tower.topR` | `2.1` |  |
| `windmills.tower.height` | `10.5` |  |
| `windmills.tower.capH` | `3` |  |
| `windmills.tower.color` | `0xD6CEBB` |  |
| `windmills.tower.capColor` | `0x3B3128` |  |
| **`windmills.sail`** | *(group)* |  |
| `windmills.sail.length` | `9.5` |  |
| `windmills.sail.cloth` | `6` |  |
| `windmills.sail.width` | `1.9` |  |
| `windmills.sail.color` | `0xE9E2CF` |  |
| **`windmills.wind`** | *(group)* |  |
| `windmills.wind.base` | `4.5` |  |
| `windmills.wind.swing` | `2.5` |  |
| `windmills.wind.prevailingFromDeg` | `315` | m/s breeze, and where it blows from (NW) |
| `windmills.spinPerMs` | `0.13` |  |
| `windmills.maxSpin` | `2.2` | sail rad/s per m/s of wind, and its cap |

## construction

Construction / demolition / fire Buildings with a born date go up over [born − duration, born] (so they are finished on their born date): walls, windows and roof rise bottom → top. Small wood buildings show stud framing first, cla…

| Key | Default | Notes |
|---|---|---|
| `construction.minMonths` | `1` | smallest wood buildings |
| `construction.maxMonths` | `24` | largest/tallest |
| `construction.masonryFactor` | `1.3` | brick/stone/concrete take longer (capped at maxMonths) |
| `construction.frameMaxHeight` | `10` | m — non-masonry buildings up to this height show stud framing; others scaffolding |
| `construction.demolitionMonths` | `1` |  |
| `construction.fireDays` | `20` | burn + charred ruin (stylised — long enough to see at slow play) |
| `construction.randomFireShare` | `0` | fraction of dated demolitions shown as fires anyway (0 = only when the data says so) |
| `construction.frameColor` | `0xC8A66E` | fresh lumber |
| **`construction.stacks`** | *(group)* | Material stacks at the kerb of the nearest road while a building goes up |
| `construction.stacks.maxRoadDistance` | `25` | metres past the building's half-size to look for a road |
| `construction.stacks.kerbInset` | `1.2` | metres in from the road edge |
| `construction.stacks.metresPerStack` | `7` | bigger building → more stacks |
| `construction.stacks.maxPerSite` | `5` |  |
| `construction.stacks.gap` | `0.6` |  |
| **`construction.stacks.brick`** | *(group)* |  |
| `construction.stacks.brick.size` | `[1.1,0.9,1.2]` |  |
| `construction.stacks.brick.color` | `0xA0503A` | [across, high, along the road] metres |
| **`construction.stacks.stone`** | *(group)* |  |
| `construction.stacks.stone.size` | `[1.2,0.8,1.4]` |  |
| `construction.stacks.stone.color` | `0x9A948A` |  |
| **`construction.stacks.lumber`** | *(group)* |  |
| `construction.stacks.lumber.size` | `[1.3,0.7,4.2]` |  |
| `construction.stacks.lumber.color` | `0xC8A66E` |  |
| **`construction.stacks.sand`** | *(group)* |  |
| `construction.stacks.sand.radius` | `1.3` |  |
| `construction.stacks.sand.height` | `1` |  |
| `construction.stacks.sand.color` | `0xB8A080` |  |
| **`construction.sound`** | *(group)* | Hammering / sawing one-shots from the nearest sites (sfx constructionHammer / constructionSaw) |
| `construction.sound.every` | `[0.5,2.5]` |  |
| `construction.sound.hours` | `[7,18]` |  |
| `construction.sound.hammerShare` | `0.75` |  |
| `construction.scaffoldColor` | `0x8B7B60` | weathered timber poles |
| `construction.maxFires` | `6` | simultaneous fires with flame/smoke particles (nearest first) |
| **`construction.fire`** | *(group)* |  |
| `construction.fire.flameEnd` | `0.45` | fraction of the fire window with open flames (the rest smoulders) |
| `construction.fire.flameRate` | `140` | flame sprites/s per fire at peak (scaled up for big buildings) |
| `construction.fire.sparkRate` | `40` |  |
| `construction.fire.smokeRate` | `45` | plume puffs/s at peak |
| `construction.fire.smokeTail` | `0.25` | plume strength while smouldering after the flames, fading to the end |
| `construction.fire.smokeLife` | `11` | s — long-lived puffs make a tall column |
| `construction.fire.smokeRise` | `9` | m/s initial climb |
| `construction.fire.smokeDrift` | `3.5` | m/s eastward drift (grows as it rises) |
| `construction.fire.smokeEndSize` | `55` | m — puff size at the top of the plume |
| `construction.fire.smokeOpacity` | `0.75` |  |
| `construction.fire.smokeColor` | `0x221E1A` |  |
| `construction.fire.lightIntensity` | `60` |  |
| `construction.fire.lightRange` | `140` | flickering orange glow on the nearest blaze |
| `construction.fire.poolFlames` | `300` |  |
| `construction.fire.poolSparks` | `120` |  |
| `construction.fire.poolSmoke` | `420` |  |

## trees

Riverbank trees Instanced trees in a thin band just outside the river polygons (the riparian elm/ash/maple/cottonwood fringe). Rows are offsets from the water's edge; each row has its own chance of a tree at each station, so the b…

| Key | Default | Notes |
|---|---|---|
| `trees.spacing` | `9` | metres between stations along the bank |
| `trees.rows` | `(list of 3)` |  |
| `trees.jitter` | `3` | metres of random scatter per tree |
| `trees.maxRadius` | `3500` | only within this distance of the scene origin |
| `trees.minAboveWater` | `0.8` | tree base must be at least this far above water.startY |
| `trees.clearBuilding` | `4` |  |
| `trees.clearRoad` | `3` |  |
| `trees.clearRail` | `4` |  |
| `trees.clearBridge` | `25` |  |
| `trees.clearRiverStructure` | `60` |  |
| `trees.ferries` | `(list of 4)` | Historic ferry landings to keep clear [lon, lat, radius m] — APPROXIMATE positions from written accounts, adjust against the Goad sheets: |
| `trees.species` | `(list of 4)` | Winnipeg–St. Boniface steam ferry, west landing (foot of Notre Dame E / Pioneer) — until 1882 …east landing (Provencher) Assiniboine pontoon crossing near Upper Fort Garry (early 1870s), north side …south side weight = share of tr… |
| `trees.crownColors` | `[0x2E4A1C, 0x365421, 0x2A4418, 0x3D5A26, 0x33501F]` |  |
| `trees.barkColor` | `0x4A4036` |  |

## sidewalks

Sidewalks Plank walks on both sides of a street where enough has been built (see buildSidewalks): `minBuildings` within radiusM of a 10 m stretch earns a walk (from residentialFrom — the 1882 boom — or eraStart, 1873, on business …

| Key | Default | Notes |
|---|---|---|
| `sidewalks.enabled` | `true` |  |
| `sidewalks.radiusM` | `28` |  |
| `sidewalks.minBuildings` | `3` |  |
| `sidewalks.businessBuildings` | `9` |  |
| `sidewalks.eraStart` | `1873` |  |
| `sidewalks.residentialFrom` | `1882` |  |
| `sidewalks.delayYears` | `1` |  |
| `sidewalks.businessEnd` | `[1898,1920]` |  |
| `sidewalks.residentialEnd` | `[1920,1935]` |  |
| `sidewalks.concrete` | `true` |  |
| `sidewalks.concreteEverywhere` | `true` | concrete everywhere once the planks go (off on phones: fewer quads) |
| `sidewalks.width` | `1.7` |  |
| `sidewalks.gapM` | `0.35` |  |
| `sidewalks.lift` | `0.16` |  |
| `sidewalks.bizInset` | `3.4` | business streets: walks sit bizInset m closer to the street centre (buildings stand right at the kerb line) |
| `sidewalks.minRoadWidth` | `8` |  |
| `sidewalks.excludeTypes` | `["LANE","PATH","TRAIL","HWY","RD"]` |  |
| **`sidewalks.streetStarts`** | *(group)* | streets that had board walks early (Main's small stretches by 1871, the city's own from 1874) even where the buildings beside them are only dated later: |
| `sidewalks.streetStarts.Main` | `1872` |  |
| `sidewalks.streetStarts.Portage` | `1874` |  |
| `sidewalks.streetStarts.Notre Dame` | `1875` |  |
| `sidewalks.streetStarts.Water` | `0x000753` |  |
| `sidewalks.streetStarts.McDermot` | `1875` |  |
| `sidewalks.streetStarts.Bannatyne` | `1875` |  |
| `sidewalks.streetStarts.Princess` | `1876` |  |
| `sidewalks.streetStarts.Albert` | `1876` |  |
| `sidewalks.streetStarts.Ross` | `1877` |  |
| `sidewalks.streetStarts.William` | `1877` |  |
| `sidewalks.streetStarts.Market` | `1876` |  |
| `sidewalks.plankColor` | `0x7A6A55` |  |
| `sidewalks.stoneColor` | `0xA9A59B` |  |

## signs

Shop / office signs (prototype: generic trades; later fed from Henderson-directory occupants) Signs are drawn at runtime into ONE canvas atlas (slots of slotPx, shared by every sign with the same text/style/colours, least-recently…

| Key | Default | Notes |
|---|---|---|
| `signs.enabled` | `true` |  |
| `signs.radiusM` | `70` |  |
| `signs.maxAltitudeM` | `90` |  |
| `signs.max` | `300` |  |
| `signs.minAreaM2` | `25` |  |
| `signs.share` | `0.32` |  |
| `signs.windowShare` | `0.35` |  |
| `signs.windowMax` | `3` |  |
| `signs.turnoverYears` | `12` |  |
| `signs.wallHeightM` | `0.6` |  |
| `signs.windowHeightM` | `0.34` |  |
| `signs.doorHeightM` | `4.65` |  |
| `signs.atlasPx` | `[2048,1024]` |  |
| `signs.slotPx` | `[256,64]` |  |
| `signs.exclude` | `/church\|cathedral\|school\|convent\|hospital\|cemetery\|station\|e…` |  |
| `signs.byName` | `(list of 5)` |  |
| `signs.occupants` | `(list of 40)` | t = lettering, s = style: 'wall' (painted board over the door) \| 'window' (gilt lettering on glass) \| 'anvil' \| 'horseshoe' (icon boards) |

## cemetery

Marshes (the ellipses on the 1881 map)

| Key | Default | Notes |
|---|---|---|
| `cemetery.treesFile` | `"./data/cemetery_trees.json"` |  |
| `cemetery.treeSpreadYears` | `55` |  |
| `cemetery.treeJitterYears` | `8` |  |
| `cemetery.treeTauYears` | `60` |  |
| `cemetery.treeMinScale` | `0.5` |  |
| `cemetery.treeScalePerRating` | `0.9` |  |
| `cemetery.grassColor` | `0x4A6330` |  |
| **`cemetery.fence`** | *(group)* |  |
| `cemetery.fence.height` | `1.8` |  |
| `cemetery.fence.spacing` | `2.4` |  |
| `cemetery.fence.fadeNear` | `70` |  |
| `cemetery.fence.fadeFar` | `150` |  |
| `cemetery.fence.color` | `0x16161A` | black iron fence round the grounds (a texture card per ~2.4 m, dithered out with distance) |
| **`cemetery.gate`** | *(group)* |  |
| `cemetery.gate.halfWidthM` | `3.2` |  |
| `cemetery.gate.pierSize` | `0.8` |  |
| `cemetery.gate.pierHeight` | `2.7` |  |
| `cemetery.gate.pierColor` | `0xB9AA84` |  |
| `cemetery.gate.capColor` | `0x8A8068` | stone piers at the east entrance (where the path meets the east edge) |
| `cemetery.moundLength` | `2` |  |
| `cemetery.moundWidth` | `0.9` |  |
| `cemetery.moundHeight` | `0.22` |  |
| `cemetery.moundYears` | `0.5` |  |
| `cemetery.moundSoil` | `0x4A3828` |  |
| `cemetery.minGroundY` | `-3.5` |  |
| `cemetery.fullYear` | `1990` |  |
| `cemetery.fillPower` | `0.8` |  |
| `cemetery.rowGapM` | `3.2` |  |
| `cemetery.stoneGapM` | `1.5` | Elmwood headstones follow data/elmwood_years.json (cumulative interments); rowGapM = east-west spacing of rows, stoneGapM = spacing along a row; fullYear/fillPower are only the fallback if that file is missing |

## marsh

| Key | Default | Notes |
|---|---|---|
| `marsh.color` | `0x5A6A38` |  |
| `marsh.dormantColor` | `0x7A6A44` |  |
| `marsh.lift` | `0.07` |  |
| `marsh.mosquitoAnchors` | `30` | wet ground draped on the terrain |

## tipis

Tipis at the Forks Camps on the point at the Forks until about 1870. Each tipi goes up within appearDays after the snow is gone, comes down within leaveDays before the next snow, and yearRoundShare of them stay all year. until = e…

| Key | Default | Notes |
|---|---|---|
| `tipis.camps` | `(list of 2)` | the point itself, and the east bank opposite |
| `tipis.yearRoundShare` | `0.2` |  |
| `tipis.appearDays` | `30` |  |
| `tipis.leaveDays` | `30` |  |
| `tipis.until` | `[1864,1872]` |  |
| `tipis.size` | `[0.9,1.15]` |  |
| `tipis.minSpacingM` | `7` |  |
| `tipis.minAboveWater` | `1.5` |  |

## earlyVegetation

Early vegetation (stands traced from early plans; see tools/early_vegetation.py)

| Key | Default | Notes |
|---|---|---|
| `earlyVegetation.file` | `"./data/early_vegetation.json"` |  |
| `earlyVegetation.density` | `1` | × each stand's per1000m2 (trees per 1000 m²) — the big willow wood is thousands of trees |
| **`earlyVegetation.kinds`** | *(group)* | crown archetype, autumn-colour key and leaf colours per kind |
| **`earlyVegetation.kinds.willow`** | *(group)* |  |
| `earlyVegetation.kinds.willow.shape` | `"round"` |  |
| `earlyVegetation.kinds.willow.species` | `"willow"` |  |
| `earlyVegetation.kinds.willow.colors` | `[0x6E8B3A, 0x7A9440, 0x688232, 0x5F7A30]` |  |
| **`earlyVegetation.kinds.poplar`** | *(group)* |  |
| `earlyVegetation.kinds.poplar.shape` | `"tall"` |  |
| `earlyVegetation.kinds.poplar.species` | `"cottonwood"` |  |
| `earlyVegetation.kinds.poplar.colors` | `[0x4F7A2A, 0x5C8A32, 0x46702A, 0x7FA037]` |  |
| **`earlyVegetation.kinds.oak`** | *(group)* |  |
| `earlyVegetation.kinds.oak.shape` | `"round"` |  |
| `earlyVegetation.kinds.oak.species` | `"oak"` |  |
| `earlyVegetation.kinds.oak.colors` | `[0x2F4A1A, 0x3A5A22, 0x34501E]` |  |

## timeline

Timeline / date slider Drives the top-of-screen date scrubber. `currentViewDate` (module-scope in index.html, mirrored on `window.currentViewDate`) is the single source of truth for "what date is being viewed" — read today by the …

| Key | Default | Notes |
|---|---|---|
| `timeline.minYear` | `1850` |  |
| `timeline.maxYear` | `1960` |  |
| `timeline.startDate` | `"1850-01-01"` | date shown on first load (YYYY-MM-DD, local) |
| `timeline.playSpeedDaysPerSecond` | `45` | ⏩ fast-forward rate (years pass) |
| **`timeline.seasonCycle`** | *(group)* | ▶ slow play: 2 days/s ≈ 3 minutes per year. wrapWithinYear loops Dec 31 → Jan 1 of the SAME year so the seasons cycle without buildings changing. enabled = start playing on load (false = start paused). |
| `timeline.seasonCycle.enabled` | `true` |  |
| `timeline.seasonCycle.daysPerSecond` | `2` |  |
| `timeline.seasonCycle.wrapWithinYear` | `true` |  |
| **`timeline.yearsFly`** | *(group)* | ▶▶▶▶ years fly by: one summer day shown per year; 10/s → 1850–1960 in ~11 s |
| `timeline.yearsFly.yearsPerSecond` | `10` |  |
| `timeline.yearsFly.day` | `"07-15"` |  |
| **`timeline.dayCycle`** | *(group)* | ☀ day by day: the clock runs 04:00→22:00 in secondsPerDay, then the next morning |
| `timeline.dayCycle.secondsPerDay` | `6` |  |
| **`timeline.yearsWalk`** | *(group)* | ▶▶▶ in between: a frame per month (each 1/12 s), 1 year/s (~2 min for 1850–1960) |
| `timeline.yearsWalk.yearsPerSecond` | `1` |  |
| **`timeline.events`** | *(group)* | Events (storms, parades, floods from the river levels, fires within fireRadiusM of the camera) slow the continuous modes and stop the jumping ones. Rates in days per second; fires take fireSeconds whatever their length. Jump modes… |
| `timeline.events.floodAboveMetres` | `3.5` |  |
| `timeline.events.fireRadiusM` | `4000` |  |
| **`timeline.events.play`** | *(group)* |  |
| `timeline.events.play.stormDaysPerSecond` | `0.04` |  |
| `timeline.events.play.paradeDaysPerSecond` | `0.04` |  |
| `timeline.events.play.floodDaysPerSecond` | `0.25` |  |
| `timeline.events.play.fireSeconds` | `40` |  |
| **`timeline.events.fast`** | *(group)* |  |
| `timeline.events.fast.stormDaysPerSecond` | `0.5` |  |
| `timeline.events.fast.paradeDaysPerSecond` | `0.5` |  |
| `timeline.events.fast.floodDaysPerSecond` | `3` |  |
| `timeline.events.fast.fireSeconds` | `5` |  |
| `timeline.events.walkHoldSeconds` | `0.8` |  |
| `timeline.events.flyHoldSeconds` | `0.5` |  |
| `timeline.events.jumpStormMinIntensity` | `0.8` |  |
| `timeline.events.jumpFloodAboveMetres` | `4` |  |

## storms

Historic storms (data/storms.json) Thunderstorms and blizzards on real dates (tools: see the file's "source"). Each storm fades in over rampHours before its start day and out after its end day; days other than the peak run at offP…

| Key | Default | Notes |
|---|---|---|
| `storms.file` | `"./data/storms.json"` |  |
| `storms.rampHours` | `6` |  |
| `storms.offPeak` | `0.75` |  |
| `storms.snowAfterDays` | `5` | a blizzard leaves snow cover this long (melting) even out of season |
| **`storms.roadWet`** | *(group)* |  |
| `storms.roadWet.darken` | `0.45` |  |
| `storms.roadWet.drySeconds` | `25` | thunderstorm rain darkens the roads by this much; they dry over ~drySeconds after |
| `storms.fadeSeconds` | `0.1` | time constant of the storm fade in/out (~3× this to settle) |
| `storms.fogHalfHeight` | `180` | storm fog halves at this camera height above ground (so zoomed-out views don't white/black out) |
| `storms.boxSize` | `180` | metres — precipitation volume that travels with the camera |
| **`storms.rain`** | *(group)* |  |
| `storms.rain.count` | `14000` | streaks at intensity 1 |
| `storms.rain.fallSpeed` | `11` | m/s |
| `storms.rain.windSpeed` | `4` | m/s sideways drift |
| `storms.rain.streakLength` | `1.6` | metres |
| `storms.rain.color` | `0xB8C4D0` |  |
| `storms.rain.opacity` | `0.35` |  |
| **`storms.snow`** | *(group)* |  |
| `storms.snow.count` | `22000` |  |
| `storms.snow.fallSpeed` | `1.6` |  |
| `storms.snow.windSpeed` | `16` | blizzard: driven mostly sideways |
| `storms.snow.gust` | `3.5` | metres of turbulent swirl |
| `storms.snow.size` | `2.2` | point size scale |
| `storms.snow.color` | `0xF4F6FA` |  |
| `storms.snow.opacity` | `0.85` |  |
| **`storms.thunderstorm`** | *(group)* |  |
| `storms.thunderstorm.skyColor` | `0x3A4250` | sky/fog tint at full strength |
| `storms.thunderstorm.fogDensity` | `0.0014` |  |
| `storms.thunderstorm.sunMult` | `0.2` | sun intensity multiplier at full strength |
| `storms.thunderstorm.ambientMult` | `0.55` |  |
| `storms.thunderstorm.lightningEvery` | `[2.5,9]` | seconds between strikes (random in range, shorter when stronger) |
| `storms.thunderstorm.boltDistance` | `[350,2600]` |  |
| `storms.thunderstorm.flashColor` | `0xDDE4FF` |  |
| `storms.thunderstorm.windGain` | `0.14` | extra wind-noise gain |
| `storms.thunderstorm.rainGain` | `0.07` | rain hiss gain |
| `storms.thunderstorm.thunderGain` | `0.6` |  |
| **`storms.blizzard`** | *(group)* |  |
| `storms.blizzard.skyColor` | `0xC6CBD2` |  |
| `storms.blizzard.fogDensity` | `0.0055` | ~500 m visibility at full strength |
| `storms.blizzard.sunMult` | `0.3` |  |
| `storms.blizzard.ambientMult` | `0.9` |  |
| `storms.blizzard.windGain` | `0.3` |  |
| `storms.blizzard.windLowpassHz` | `700` | wind howls higher-pitched in a blizzard |

## seasons

Seasons (driven by the view date) Each channel is ['MM-DD', value] keyframes, linear between, wrapping over New Year. Rough Winnipeg norms: snow gone ~mid-April, river ice holds a few days longer then breaks up (floes drift for ~2…

| Key | Default | Notes |
|---|---|---|
| **`seasons.moisture`** | *(group)* | Summer moisture index: -1 drought … +1 wet (data/moisture.json). |
| `seasons.moisture.file` | `"./data/moisture.json"` |  |
| `seasons.moisture.strength` | `0.85` | how far the summer colour moves toward drought/lush at ±1 |
| `seasons.moisture.dryPatches` | `0.9` | extra straw patches at -1 (× groundCover.dryAmount) |
| `seasons.moisture.treeYellowing` | `0.3` | early autumn tint in trees at -1 |
| `seasons.snow` | `[["01-01",1],["03-25",1],["04-12",0],["10-28",0],["11-20",1]]` |  |
| `seasons.green` | `(list of 6)` | ~3 weeks of bare brown after melt |
| `seasons.ice` | `[["01-01",1],["04-14",1],["04-17",0],["11-25",0],["11-30",1]]` |  |
| `seasons.floes` | `(list of 7)` |  |
| `seasons.leaf` | `[["05-01",0],["05-22",1],["10-02",1],["10-24",0]]` |  |
| `seasons.autumn` | `[["09-10",0],["10-02",1],["10-25",1],["10-26",0]]` | leaf colour turn; reset once bare |
| `seasons.heating` | `[["01-01",1],["04-01",1],["05-10",0],["09-25",0],["11-15",1]]` | chimney smoke multiplier blend |
| `seasons.dormantColor` | `0x7A5F35` | winter-killed / not-yet-green prairie grass — matted straw brown |
| `seasons.springLeafColor` | `0x8FAE4A` | fresh May leaves |
| `seasons.lateAutumnColor` | `0x6E4E2C` | brown leaves hanging on before they drop |
| **`seasons.autumnColors`** | *(group)* |  |
| `seasons.autumnColors.American elm` | `12096564` |  |
| `seasons.autumnColors.green ash` | `13150266` |  |
| `seasons.autumnColors.Manitoba maple` | `13610558` |  |
| `seasons.autumnColors.cottonwood` | `13215292` |  |
| `seasons.floeCount` | `1100` |  |
| `seasons.floeSpeed` | `6` |  |
| `seasons.floeColor` | `0xDCE3EA` | break-up / freeze-up ice pans |

## streetcars

Streetcars

| Key | Default | Notes |
|---|---|---|
| `streetcars.speed` | `4.5` | m/s (~16 km/h) |
| `streetcars.carSpacingMeters` | `900` | (was 400 — ~730 cars; now about 40%) target distance (map units/metres) between cars along a |
| `streetcars.carsPerDirectionMin` | `1` | route, each direction — car count per direction = route length / this value (floored by carsPerDirectionMin below). Shorter routes get fewer cars, longer ones get more. Lower this for denser traffic; raise it if frame rate suffers… |
| `streetcars.laneOffset` | `2.5` | metres from centreline |
| `streetcars.electrificationYear` | `1891` | horse carts (below) vanish at this year — a global |
| **`streetcars.dimensions`** | *(group)* | "streetcar era begins" cutoff, separate from each route's own streetcar_start (see data/wpg_roads_streetcar.geojson) |
| `streetcars.dimensions.width` | `2.4` |  |
| `streetcars.dimensions.height` | `2.8` |  |
| `streetcars.dimensions.length` | `12` |  |
| `streetcars.dimensions.skirtHeight` | `0.75` |  |
| `streetcars.dimensions.roofHeight` | `0.55` |  |
| `streetcars.dimensions.roadOffsetY` | `0.18` |  |
| **`streetcars.colors`** | *(group)* |  |
| `streetcars.colors.body` | `15771648` |  |
| `streetcars.colors.skirt` | `3807754` |  |
| `streetcars.colors.roof` | `0x3A2E22` |  |
| `streetcars.colors.window` | `1714741` |  |
| `streetcars.colors.headlight` | `16777164` |  |
| `streetcars.colors.taillight` | `14487808` |  |
| `streetcars.colors.bodySpecular` | `0x332200` |  |
| `streetcars.colors.windowSpecular` | `0x334455` |  |
| **`streetcars.routeClips`** | *(group)* | index along route where streetcars are allowed to run, by route name |
| **`streetcars.routeClips.Portage`** | *(group)* |  |
| `streetcars.routeClips.Portage.min` | `1` |  |
| `streetcars.routeClips.Portage.max` | `558` |  |
| **`streetcars.routeClips.Main`** | *(group)* |  |
| `streetcars.routeClips.Main.min` | `54` |  |
| `streetcars.routeClips.Main.max` | `960` |  |

## carts

Horse/ox carts (pre-electric era)

| Key | Default | Notes |
|---|---|---|
| `carts.speed` | `1.2` | m/s (~4.3 km/h, walking pace) |
| `carts.laneOffset` | `2` |  |
| `carts.intervalSeconds` | `90` |  |
| `carts.countPerDirection` | `2` |  |
| **`carts.dimensions`** | *(group)* |  |
| `carts.dimensions.width` | `1.6` |  |
| `carts.dimensions.height` | `1.2` |  |
| `carts.dimensions.length` | `3` |  |
| `carts.dimensions.roadOffsetY` | `0.18` |  |
| **`carts.colors`** | *(group)* |  |
| `carts.colors.body` | `9133610` |  |
| `carts.colors.horse` | `7027231` |  |
| `carts.colors.ox` | `10261636` |  |
| `carts.colors.oxHorn` | `15261384` |  |
| `carts.colors.wagonRut` | `6969930` |  |
| **`carts.routeClips`** | *(group)* |  |
| **`carts.routeClips.Main`** | *(group)* |  |
| `carts.routeClips.Main.min` | `54` |  |
| `carts.routeClips.Main.max` | `260` |  |
| `carts.oxChance` | `0.35` | fraction of carts drawn by an ox team instead of a horse |
| **`carts.wheels`** | *(group)* | Spoked cart wheels — one shared merged geometry, instanced per wheel. Rotation speed is derived from actual travel speed each tick (not baked in), so faster carts spin their wheels faster automatically. |
| `carts.wheels.radius` | `0.42` |  |
| `carts.wheels.tubeThickness` | `0.05` | rim cross-section radius |
| `carts.wheels.spokeCount` | `8` |  |
| `carts.wheels.spokeThickness` | `0.045` | box cross-section (both axes) of each spoke |
| `carts.wheels.hubRadius` | `0.11` |  |
| `carts.wheels.hubLength` | `0.2` | hub cylinder length along the axle |
| `carts.wheels.color` | `0x2A1E14` |  |
| **`carts.cargo`** | *(group)* | Cargo loads — a shared geometry per kind, 1–3 chosen per cart at spawn time (seeded, so stable across ticks) and stacked on the flatbed. |
| `carts.cargo.maxPerCart` | `3` |  |
| `carts.cargo.minPerCart` | `1` |  |
| `carts.cargo.kinds` | `["barrel","sack","crate","hayBale"]` |  |
| **`carts.cargo.barrel`** | *(group)* |  |
| `carts.cargo.barrel.radius` | `0.28` |  |
| `carts.cargo.barrel.height` | `0.55` |  |
| `carts.cargo.barrel.color` | `0x6E4A28` |  |
| **`carts.cargo.sack`** | *(group)* |  |
| `carts.cargo.sack.radius` | `0.3` |  |
| `carts.cargo.sack.color` | `0xC2B280` |  |
| **`carts.cargo.crate`** | *(group)* |  |
| `carts.cargo.crate.size` | `0.5` |  |
| `carts.cargo.crate.color` | `0x8A6A3E` |  |
| **`carts.cargo.hayBale`** | *(group)* |  |
| `carts.cargo.hayBale.radius` | `0.3` |  |
| `carts.cargo.hayBale.length` | `0.65` |  |
| `carts.cargo.hayBale.color` | `0xD9B84A` |  |
| **`carts.driver`** | *(group)* | Seated driver figure + reins running to the horse's head anchor. |
| `carts.driver.torsoColor` | `0x3A3428` |  |
| `carts.driver.headColor` | `0xC49A6C` |  |
| `carts.driver.armColor` | `0x3A3428` |  |
| `carts.driver.reinColor` | `0x2A1E14` |  |
| `carts.driver.reinThickness` | `0.015` |  |
| **`carts.droppings`** | *(group)* | Occasional road droppings — small fading discs left behind a moving horse. Pool-based like chimney smoke, so no per-frame allocation. |
| `carts.droppings.poolSize` | `24` |  |
| `carts.droppings.chancePerSecond` | `0.06` | per moving cart, average one every ~17s |
| `carts.droppings.life` | `6` | seconds visible before fully faded |
| `carts.droppings.radius` | `0.09` |  |
| `carts.droppings.color` | `0x4A3420` |  |

## trains

Trains

| Key | Default | Notes |
|---|---|---|
| **`trains.speedMps`** | *(group)* |  |
| `trains.speedMps.passenger` | `9` |  |
| `trains.speedMps.freight` | `6.5` |  |
| `trains.speedMps.switcher` | `2.3` | stylised, not literal scale |
| **`trains.dwellSecondsRange`** | *(group)* |  |
| `trains.dwellSecondsRange.passenger` | `[6,12]` |  |
| `trains.dwellSecondsRange.freight` | `[14,26]` |  |
| `trains.dwellSecondsRange.switcher` | `[10,24]` |  |
| `trains.passengerRouteCount` | `12` | top-N longest segments get passenger service |
| `trains.freightThroughMinLengthM` | `900` | mainline-scale threshold for through freight |
| `trains.smokePuffsPerLocomotive` | `7` |  |
| **`trains.carsByYear`** | *(group)* | Cars per train by year (linear between; each train ±20%, capped by its route) — trains got much longer as locomotives got bigger. |
| `trains.carsByYear.passenger` | `[[1880,3],[1900,6],[1930,10],[1960,12]]` |  |
| `trains.carsByYear.freight` | `[[1880,8],[1900,20],[1930,40],[1960,55]]` |  |
| `trains.carsByYear.switcher` | `[[1880,2],[1960,6]]` |  |
| `trains.maxCars` | `45` | cap per train (draw calls) — mobile profile lowers it |
| **`trains.colors`** | *(group)* |  |
| `trains.colors.locoBody` | `1315087` |  |
| `trains.colors.locoCab` | `2761760` |  |
| `trains.colors.tender` | `1841172` |  |
| `trains.colors.tenderCoal` | `789516` |  |
| `trains.colors.headlight` | `16773824` |  |
| `trains.colors.passengerCars` | `[7220268,5909032,5056036]` |  |
| `trains.colors.freightCars` | `[9124398,5591628,7037783,8014387]` |  |
| `trains.colors.passengerWindow` | `1712165` |  |
| `trains.colors.passengerRoof` | `3814188` |  |
| `trains.colors.locoSpecular` | `0x444444` |  |
| **`trains.dimensions`** | *(group)* |  |
| `trains.dimensions.locoBodyLength` | `9.5` |  |
| `trains.dimensions.locoBodyWidth` | `2.5` |  |
| `trains.dimensions.locoBodyHeight` | `2.9` |  |
| `trains.dimensions.tenderLength` | `6` |  |
| `trains.dimensions.tenderWidth` | `2.4` |  |
| `trains.dimensions.tenderHeight` | `2.3` |  |
| `trains.dimensions.carGap` | `0.6` |  |
| `trains.dimensions.passengerCarLength` | `18` |  |
| `trains.dimensions.passengerCarWidth` | `2.7` |  |
| `trains.dimensions.passengerCarHeight` | `3.2` |  |
| `trains.dimensions.freightCarLength` | `11.5` |  |
| `trains.dimensions.freightCarWidth` | `2.6` |  |
| `trains.dimensions.freightCarHeight` | `2.5` |  |
| `trains.dimensions.switcherCarLength` | `10` |  |

## audio

Audio Two kinds of sound here: real audio *files* (just the locomotive, for now — add more by giving them a name/path/volume below and wiring the name in index.html's loadTrainAudio-style code), and small synthesized ambient sound…

| Key | Default | Notes |
|---|---|---|
| **`audio.files`** | *(group)* |  |
| **`audio.files.locomotive`** | *(group)* |  |
| `audio.files.locomotive.path` | `"./sounds/locomotive-loop.mp3"` |  |
| `audio.files.locomotive.maxConcurrent` | `4` | concurrent locomotive loops across all trains |
| `audio.files.locomotive.rangeMetres` | `450` | beyond this distance, a train doesn't get an audio slot |
| `audio.files.locomotive.refDistance` | `15` | metres at which volume is "full" |
| `audio.files.locomotive.rolloffFactor` | `1.2` | how fast volume falls off with distance |
| **`audio.files.locomotive.gainByKind`** | *(group)* |  |
| `audio.files.locomotive.gainByKind.passenger` | `1.66` |  |
| `audio.files.locomotive.gainByKind.freight` | `1.99` |  |
| `audio.files.locomotive.gainByKind.switcher` | `1.45` |  |
| **`audio.sfx`** | *(group)* | Add more entries here later, e.g.: streetcarBell: { path: './sounds/streetcar-bell.mp3', maxConcurrent: 3, rangeMetres: 200, refDistance: 10, rolloffFactor: 1.0, gain: 1.0 }, Sound-effect hooks: playSfx(name, x, y, z) (one-shot). … |
| **`audio.sfx.dockBreak`** | *(group)* |  |
| `audio.sfx.dockBreak.path` | `"./sounds/dock-break.mp3"` |  |
| `audio.sfx.dockBreak.gain` | `1` |  |
| `audio.sfx.dockBreak.refDistance` | `25` |  |
| `audio.sfx.dockBreak.rolloffPower` | `2` |  |
| `audio.sfx.dockBreak.maxDistance` | `900` |  |
| **`audio.sfx.constructionHammer`** | *(group)* |  |
| `audio.sfx.constructionHammer.path` | `"./sounds/construction-hammer.mp3"` |  |
| `audio.sfx.constructionHammer.gain` | `0.7` |  |
| `audio.sfx.constructionHammer.refDistance` | `12` |  |
| `audio.sfx.constructionHammer.rolloffPower` | `3` |  |
| `audio.sfx.constructionHammer.maxDistance` | `250` |  |
| **`audio.sfx.constructionSaw`** | *(group)* |  |
| `audio.sfx.constructionSaw.path` | `"./sounds/construction-saw.mp3"` |  |
| `audio.sfx.constructionSaw.gain` | `0.6` |  |
| `audio.sfx.constructionSaw.refDistance` | `12` |  |
| `audio.sfx.constructionSaw.rolloffPower` | `3` |  |
| `audio.sfx.constructionSaw.maxDistance` | `250` |  |
| **`audio.sfx.cartHooves`** | *(group)* | Mobs — loop: true = a looping voice on the nearest maxConcurrent sources |
| `audio.sfx.cartHooves.path` | `"./sounds/cart-hooves.mp3"` |  |
| `audio.sfx.cartHooves.loop` | `true` |  |
| `audio.sfx.cartHooves.maxConcurrent` | `3` |  |
| `audio.sfx.cartHooves.gain` | `0.6` |  |
| `audio.sfx.cartHooves.refDistance` | `8` |  |
| `audio.sfx.cartHooves.rolloffPower` | `2` |  |
| `audio.sfx.cartHooves.maxDistance` | `150` |  |
| **`audio.sfx.cartHooves.gate`** | *(group)* |  |
| `audio.sfx.cartHooves.gate.mud` | `[0,0.4]` | mudWalkHorse/Ox take over when it's muddy |
| **`audio.sfx.horseWhinny`** | *(group)* |  |
| `audio.sfx.horseWhinny.path` | `"./sounds/horse-whinny.mp3"` |  |
| `audio.sfx.horseWhinny.gain` | `0.7` |  |
| `audio.sfx.horseWhinny.refDistance` | `10` |  |
| `audio.sfx.horseWhinny.rolloffPower` | `2` |  |
| `audio.sfx.horseWhinny.maxDistance` | `250` |  |
| **`audio.sfx.streetcarRun`** | *(group)* |  |
| `audio.sfx.streetcarRun.path` | `"./sounds/streetcar-run.mp3"` |  |
| `audio.sfx.streetcarRun.loop` | `true` |  |
| `audio.sfx.streetcarRun.maxConcurrent` | `2` |  |
| `audio.sfx.streetcarRun.gain` | `0.6` |  |
| `audio.sfx.streetcarRun.refDistance` | `12` |  |
| `audio.sfx.streetcarRun.rolloffPower` | `2` |  |
| `audio.sfx.streetcarRun.maxDistance` | `300` |  |
| **`audio.sfx.streetcarBell`** | *(group)* |  |
| `audio.sfx.streetcarBell.path` | `"./sounds/streetcar-bell.mp3"` |  |
| `audio.sfx.streetcarBell.gain` | `0.7` |  |
| `audio.sfx.streetcarBell.refDistance` | `15` |  |
| `audio.sfx.streetcarBell.rolloffPower` | `1.5` |  |
| `audio.sfx.streetcarBell.maxDistance` | `400` |  |
| `audio.sfx.streetcarBell.minGap` | `2` |  |
| `audio.sfx.streetcarBell.duck` | `0.2` | replaces the synth bell if present |
| **`audio.sfx.trainRun`** | *(group)* |  |
| `audio.sfx.trainRun.path` | `"./sounds/train-run.mp3"` |  |
| `audio.sfx.trainRun.loop` | `true` |  |
| `audio.sfx.trainRun.maxConcurrent` | `2` |  |
| `audio.sfx.trainRun.gain` | `0.7` |  |
| `audio.sfx.trainRun.refDistance` | `20` |  |
| `audio.sfx.trainRun.rolloffPower` | `1.5` |  |
| `audio.sfx.trainRun.maxDistance` | `600` |  |
| **`audio.sfx.trainWhistle`** | *(group)* |  |
| `audio.sfx.trainWhistle.path` | `"./sounds/train-whistle.mp3"` |  |
| `audio.sfx.trainWhistle.gain` | `1` |  |
| `audio.sfx.trainWhistle.refDistance` | `60` |  |
| `audio.sfx.trainWhistle.rolloffPower` | `1.2` |  |
| `audio.sfx.trainWhistle.maxDistance` | `3000` |  |
| `audio.sfx.trainWhistle.minGap` | `10` |  |
| `audio.sfx.trainWhistle.duck` | `0.5` |  |
| **`audio.sfx.steamboatEngine`** | *(group)* |  |
| `audio.sfx.steamboatEngine.path` | `"./sounds/steamboat-engine.mp3"` |  |
| `audio.sfx.steamboatEngine.loop` | `true` |  |
| `audio.sfx.steamboatEngine.maxConcurrent` | `2` |  |
| `audio.sfx.steamboatEngine.gain` | `0.7` |  |
| `audio.sfx.steamboatEngine.refDistance` | `20` |  |
| `audio.sfx.steamboatEngine.rolloffPower` | `2` |  |
| `audio.sfx.steamboatEngine.maxDistance` | `500` |  |
| **`audio.sfx.steamboatWhistle`** | *(group)* |  |
| `audio.sfx.steamboatWhistle.path` | `"./sounds/steamboat-whistle.mp3"` |  |
| `audio.sfx.steamboatWhistle.gain` | `1` |  |
| `audio.sfx.steamboatWhistle.refDistance` | `80` |  |
| `audio.sfx.steamboatWhistle.rolloffPower` | `1.2` |  |
| `audio.sfx.steamboatWhistle.maxDistance` | `3500` |  |
| `audio.sfx.steamboatWhistle.minGap` | `10` |  |
| `audio.sfx.steamboatWhistle.duck` | `0.5` |  |
| **`audio.sfx.launchEngine`** | *(group)* |  |
| `audio.sfx.launchEngine.path` | `"./sounds/launch-engine.mp3"` |  |
| `audio.sfx.launchEngine.loop` | `true` |  |
| `audio.sfx.launchEngine.maxConcurrent` | `2` |  |
| `audio.sfx.launchEngine.gain` | `0.5` |  |
| `audio.sfx.launchEngine.refDistance` | `10` |  |
| `audio.sfx.launchEngine.rolloffPower` | `2` |  |
| `audio.sfx.launchEngine.maxDistance` | `300` |  |
| **`audio.sfx.paddleSplash`** | *(group)* |  |
| `audio.sfx.paddleSplash.path` | `"./sounds/paddle-splash.mp3"` |  |
| `audio.sfx.paddleSplash.gain` | `0.4` |  |
| `audio.sfx.paddleSplash.refDistance` | `5` |  |
| `audio.sfx.paddleSplash.rolloffPower` | `3` |  |
| `audio.sfx.paddleSplash.maxDistance` | `120` |  |
| `audio.sfx.paddleSplash.variants` | `4` |  |
| **`audio.sfx.ferryEngine`** | *(group)* |  |
| `audio.sfx.ferryEngine.path` | `"./sounds/ferry-engine.mp3"` |  |
| `audio.sfx.ferryEngine.loop` | `true` |  |
| `audio.sfx.ferryEngine.maxConcurrent` | `1` |  |
| `audio.sfx.ferryEngine.gain` | `0.6` |  |
| `audio.sfx.ferryEngine.refDistance` | `15` |  |
| `audio.sfx.ferryEngine.rolloffPower` | `2` |  |
| `audio.sfx.ferryEngine.maxDistance` | `400` |  |
| **`audio.sfx.fireCrackle`** | *(group)* |  |
| `audio.sfx.fireCrackle.path` | `"./sounds/fire-crackle.mp3"` |  |
| `audio.sfx.fireCrackle.loop` | `true` |  |
| `audio.sfx.fireCrackle.maxConcurrent` | `2` |  |
| `audio.sfx.fireCrackle.gain` | `0.9` |  |
| `audio.sfx.fireCrackle.refDistance` | `25` |  |
| `audio.sfx.fireCrackle.rolloffPower` | `2` |  |
| `audio.sfx.fireCrackle.maxDistance` | `600` |  |
| **`audio.sfx.fireBell`** | *(group)* |  |
| `audio.sfx.fireBell.path` | `"./sounds/fire-bell.mp3"` |  |
| `audio.sfx.fireBell.gain` | `0.9` |  |
| `audio.sfx.fireBell.refDistance` | `25` |  |
| `audio.sfx.fireBell.rolloffPower` | `1.5` |  |
| `audio.sfx.fireBell.maxDistance` | `900` |  |
| `audio.sfx.fireBell.duck` | `0.3` |  |
| **`audio.sfx.fireGallop`** | *(group)* |  |
| `audio.sfx.fireGallop.path` | `"./sounds/fire-gallop.mp3"` |  |
| `audio.sfx.fireGallop.loop` | `true` |  |
| `audio.sfx.fireGallop.maxConcurrent` | `2` |  |
| `audio.sfx.fireGallop.gain` | `0.8` |  |
| `audio.sfx.fireGallop.refDistance` | `12` |  |
| `audio.sfx.fireGallop.rolloffPower` | `2` |  |
| `audio.sfx.fireGallop.maxDistance` | `300` |  |
| **`audio.sfx.fireSirenLoop`** | *(group)* |  |
| `audio.sfx.fireSirenLoop.path` | `"./sounds/fire-siren.mp3"` |  |
| `audio.sfx.fireSirenLoop.loop` | `true` |  |
| `audio.sfx.fireSirenLoop.bus` | `"main"` |  |
| `audio.sfx.fireSirenLoop.maxConcurrent` | `2` |  |
| `audio.sfx.fireSirenLoop.gain` | `1` |  |
| `audio.sfx.fireSirenLoop.refDistance` | `40` |  |
| `audio.sfx.fireSirenLoop.rolloffPower` | `1.3` |  |
| `audio.sfx.fireSirenLoop.maxDistance` | `2500` |  |
| **`audio.sfx.firePump`** | *(group)* |  |
| `audio.sfx.firePump.path` | `"./sounds/fire-pump.mp3"` |  |
| `audio.sfx.firePump.loop` | `true` |  |
| `audio.sfx.firePump.maxConcurrent` | `2` |  |
| `audio.sfx.firePump.gain` | `0.6` |  |
| `audio.sfx.firePump.refDistance` | `12` |  |
| `audio.sfx.firePump.rolloffPower` | `2` |  |
| `audio.sfx.firePump.maxDistance` | `300` |  |
| **`audio.sfx.paradeBand`** | *(group)* |  |
| `audio.sfx.paradeBand.path` | `"./sounds/parade-band.mp3"` |  |
| `audio.sfx.paradeBand.loop` | `true` |  |
| `audio.sfx.paradeBand.bus` | `"main"` |  |
| `audio.sfx.paradeBand.maxConcurrent` | `1` |  |
| `audio.sfx.paradeBand.gain` | `0.9` |  |
| `audio.sfx.paradeBand.refDistance` | `25` |  |
| `audio.sfx.paradeBand.rolloffPower` | `1.5` |  |
| `audio.sfx.paradeBand.maxDistance` | `900` |  |
| **`audio.sfx.crowdCheer`** | *(group)* |  |
| `audio.sfx.crowdCheer.path` | `"./sounds/crowd-cheer.mp3"` |  |
| `audio.sfx.crowdCheer.loop` | `true` |  |
| `audio.sfx.crowdCheer.maxConcurrent` | `2` |  |
| `audio.sfx.crowdCheer.gain` | `0.7` |  |
| `audio.sfx.crowdCheer.refDistance` | `20` |  |
| `audio.sfx.crowdCheer.rolloffPower` | `1.5` |  |
| `audio.sfx.crowdCheer.maxDistance` | `600` |  |
| **`audio.sfx.mosquitoes`** | *(group)* |  |
| `audio.sfx.mosquitoes.path` | `"./sounds/mosquitoes.mp3"` |  |
| `audio.sfx.mosquitoes.loop` | `true` |  |
| `audio.sfx.mosquitoes.maxConcurrent` | `1` |  |
| `audio.sfx.mosquitoes.gain` | `0.5` |  |
| `audio.sfx.mosquitoes.refDistance` | `3` |  |
| `audio.sfx.mosquitoes.rolloffPower` | `3` |  |
| `audio.sfx.mosquitoes.maxDistance` | `40` |  |
| **`audio.sfx.trainIdle`** | *(group)* | Wired from the sound wiring map (files optional: a missing file is skipped quietly) Per hook: loop/maxConcurrent (nearest sources get a voice) · minGap (s, rate limit) · variants: N (files name.mp3, name-2.mp3 … name-N.mp3, random… |
| `audio.sfx.trainIdle.path` | `"./sounds/train-idle.mp3"` |  |
| `audio.sfx.trainIdle.refDistance` | `18` |  |
| `audio.sfx.trainIdle.rolloffPower` | `1.7` |  |
| `audio.sfx.trainIdle.maxDistance` | `400` |  |
| `audio.sfx.trainIdle.loop` | `true` |  |
| `audio.sfx.trainIdle.maxConcurrent` | `2` |  |
| `audio.sfx.trainIdle.gain` | `0.5` |  |
| **`audio.sfx.trainRails`** | *(group)* |  |
| `audio.sfx.trainRails.path` | `"./sounds/train-rails.mp3"` |  |
| `audio.sfx.trainRails.refDistance` | `15` |  |
| `audio.sfx.trainRails.rolloffPower` | `1.7` |  |
| `audio.sfx.trainRails.maxDistance` | `450` |  |
| `audio.sfx.trainRails.loop` | `true` |  |
| `audio.sfx.trainRails.maxConcurrent` | `2` |  |
| `audio.sfx.trainRails.gain` | `0.45` |  |
| **`audio.sfx.trainOnboard`** | *(group)* |  |
| `audio.sfx.trainOnboard.path` | `"./sounds/train-onboard.mp3"` |  |
| `audio.sfx.trainOnboard.bed` | `true` |  |
| `audio.sfx.trainOnboard.gain` | `0.6` |  |
| **`audio.sfx.streetcarCruise`** | *(group)* | — Streetcars (streetcarRun above is the old pass-by-heavy hook: retire it when streetcarCruise is chosen) |
| `audio.sfx.streetcarCruise.path` | `"./sounds/streetcar-cruise.mp3"` |  |
| `audio.sfx.streetcarCruise.refDistance` | `12` |  |
| `audio.sfx.streetcarCruise.rolloffPower` | `1.7` |  |
| `audio.sfx.streetcarCruise.maxDistance` | `300` |  |
| `audio.sfx.streetcarCruise.loop` | `true` |  |
| `audio.sfx.streetcarCruise.maxConcurrent` | `2` |  |
| `audio.sfx.streetcarCruise.gain` | `0.5` |  |
| **`audio.sfx.streetcarIdle`** | *(group)* |  |
| `audio.sfx.streetcarIdle.path` | `"./sounds/streetcar-idle.mp3"` |  |
| `audio.sfx.streetcarIdle.refDistance` | `10` |  |
| `audio.sfx.streetcarIdle.rolloffPower` | `1.7` |  |
| `audio.sfx.streetcarIdle.maxDistance` | `200` |  |
| `audio.sfx.streetcarIdle.loop` | `true` |  |
| `audio.sfx.streetcarIdle.maxConcurrent` | `2` |  |
| `audio.sfx.streetcarIdle.gain` | `0.4` |  |
| **`audio.sfx.harnessJingle`** | *(group)* | — Horses, carts, sleighs |
| `audio.sfx.harnessJingle.path` | `"./sounds/harness-jingle.mp3"` |  |
| `audio.sfx.harnessJingle.refDistance` | `6` |  |
| `audio.sfx.harnessJingle.rolloffPower` | `2.5` |  |
| `audio.sfx.harnessJingle.maxDistance` | `120` |  |
| `audio.sfx.harnessJingle.loop` | `true` |  |
| `audio.sfx.harnessJingle.maxConcurrent` | `3` |  |
| `audio.sfx.harnessJingle.gain` | `0.3` |  |
| **`audio.sfx.harnessJingle.gate`** | *(group)* |  |
| `audio.sfx.harnessJingle.gate.snow` | `[0,0.5]` |  |
| **`audio.sfx.mudWalkHorse`** | *(group)* |  |
| `audio.sfx.mudWalkHorse.path` | `"./sounds/mud-walk-horse.mp3"` |  |
| `audio.sfx.mudWalkHorse.refDistance` | `8` |  |
| `audio.sfx.mudWalkHorse.rolloffPower` | `2.5` |  |
| `audio.sfx.mudWalkHorse.maxDistance` | `150` |  |
| `audio.sfx.mudWalkHorse.loop` | `true` |  |
| `audio.sfx.mudWalkHorse.maxConcurrent` | `3` |  |
| `audio.sfx.mudWalkHorse.gain` | `0.6` |  |
| **`audio.sfx.mudWalkHorse.gate`** | *(group)* |  |
| `audio.sfx.mudWalkHorse.gate.mud` | `[0.4,1]` |  |
| **`audio.sfx.mudWalkOx`** | *(group)* |  |
| `audio.sfx.mudWalkOx.path` | `"./sounds/mud-walk-ox.mp3"` |  |
| `audio.sfx.mudWalkOx.refDistance` | `8` |  |
| `audio.sfx.mudWalkOx.rolloffPower` | `2.5` |  |
| `audio.sfx.mudWalkOx.maxDistance` | `150` |  |
| `audio.sfx.mudWalkOx.loop` | `true` |  |
| `audio.sfx.mudWalkOx.maxConcurrent` | `2` |  |
| `audio.sfx.mudWalkOx.gain` | `0.6` |  |
| **`audio.sfx.mudWalkOx.gate`** | *(group)* |  |
| `audio.sfx.mudWalkOx.gate.mud` | `[0.4,1]` |  |
| **`audio.sfx.sleighBells`** | *(group)* |  |
| `audio.sfx.sleighBells.path` | `"./sounds/sleigh-bells.mp3"` |  |
| `audio.sfx.sleighBells.refDistance` | `8` |  |
| `audio.sfx.sleighBells.rolloffPower` | `2.5` |  |
| `audio.sfx.sleighBells.maxDistance` | `200` |  |
| `audio.sfx.sleighBells.loop` | `true` |  |
| `audio.sfx.sleighBells.maxConcurrent` | `3` |  |
| `audio.sfx.sleighBells.gain` | `0.45` |  |
| **`audio.sfx.sleighBells.gate`** | *(group)* |  |
| `audio.sfx.sleighBells.gate.snow` | `[0.5,1]` |  |
| **`audio.sfx.carModelTDrive`** | *(group)* | — Motor vehicles (which one plays is picked by year: audio.vehicleEras) |
| `audio.sfx.carModelTDrive.path` | `"./sounds/car-model-t-drive.mp3"` |  |
| `audio.sfx.carModelTDrive.refDistance` | `16` |  |
| `audio.sfx.carModelTDrive.rolloffPower` | `1.7` |  |
| `audio.sfx.carModelTDrive.maxDistance` | `450` |  |
| `audio.sfx.carModelTDrive.loop` | `true` |  |
| `audio.sfx.carModelTDrive.maxConcurrent` | `3` |  |
| `audio.sfx.carModelTDrive.gain` | `0.5` |  |
| **`audio.sfx.carModelTIdle`** | *(group)* |  |
| `audio.sfx.carModelTIdle.path` | `"./sounds/car-model-t-idle.mp3"` |  |
| `audio.sfx.carModelTIdle.refDistance` | `16` |  |
| `audio.sfx.carModelTIdle.rolloffPower` | `1.7` |  |
| `audio.sfx.carModelTIdle.maxDistance` | `450` |  |
| `audio.sfx.carModelTIdle.loop` | `true` |  |
| `audio.sfx.carModelTIdle.maxConcurrent` | `2` |  |
| `audio.sfx.carModelTIdle.gain` | `0.4` |  |
| **`audio.sfx.car1930s40sDrive`** | *(group)* |  |
| `audio.sfx.car1930s40sDrive.path` | `"./sounds/car-1930s-40s-drive.mp3"` |  |
| `audio.sfx.car1930s40sDrive.refDistance` | `16` |  |
| `audio.sfx.car1930s40sDrive.rolloffPower` | `1.7` |  |
| `audio.sfx.car1930s40sDrive.maxDistance` | `450` |  |
| `audio.sfx.car1930s40sDrive.loop` | `true` |  |
| `audio.sfx.car1930s40sDrive.maxConcurrent` | `3` |  |
| `audio.sfx.car1930s40sDrive.gain` | `0.5` |  |
| **`audio.sfx.car1930s40sIdle`** | *(group)* |  |
| `audio.sfx.car1930s40sIdle.path` | `"./sounds/car-1930s-40s-idle.mp3"` |  |
| `audio.sfx.car1930s40sIdle.refDistance` | `16` |  |
| `audio.sfx.car1930s40sIdle.rolloffPower` | `1.7` |  |
| `audio.sfx.car1930s40sIdle.maxDistance` | `450` |  |
| `audio.sfx.car1930s40sIdle.loop` | `true` |  |
| `audio.sfx.car1930s40sIdle.maxConcurrent` | `2` |  |
| `audio.sfx.car1930s40sIdle.gain` | `0.4` |  |
| **`audio.sfx.car1950sDrive`** | *(group)* |  |
| `audio.sfx.car1950sDrive.path` | `"./sounds/car-1950s-drive.mp3"` |  |
| `audio.sfx.car1950sDrive.refDistance` | `16` |  |
| `audio.sfx.car1950sDrive.rolloffPower` | `1.7` |  |
| `audio.sfx.car1950sDrive.maxDistance` | `450` |  |
| `audio.sfx.car1950sDrive.loop` | `true` |  |
| `audio.sfx.car1950sDrive.maxConcurrent` | `3` |  |
| `audio.sfx.car1950sDrive.gain` | `0.5` |  |
| **`audio.sfx.car1950sIdle`** | *(group)* |  |
| `audio.sfx.car1950sIdle.path` | `"./sounds/car-1950s-idle.mp3"` |  |
| `audio.sfx.car1950sIdle.refDistance` | `16` |  |
| `audio.sfx.car1950sIdle.rolloffPower` | `1.7` |  |
| `audio.sfx.car1950sIdle.maxDistance` | `450` |  |
| `audio.sfx.car1950sIdle.loop` | `true` |  |
| `audio.sfx.car1950sIdle.maxConcurrent` | `2` |  |
| `audio.sfx.car1950sIdle.gain` | `0.4` |  |
| **`audio.sfx.busDieselDrive`** | *(group)* |  |
| `audio.sfx.busDieselDrive.path` | `"./sounds/bus-diesel-drive.mp3"` |  |
| `audio.sfx.busDieselDrive.refDistance` | `16` |  |
| `audio.sfx.busDieselDrive.rolloffPower` | `1.7` |  |
| `audio.sfx.busDieselDrive.maxDistance` | `450` |  |
| `audio.sfx.busDieselDrive.loop` | `true` |  |
| `audio.sfx.busDieselDrive.maxConcurrent` | `2` |  |
| `audio.sfx.busDieselDrive.gain` | `0.6` |  |
| **`audio.sfx.busDieselIdle`** | *(group)* |  |
| `audio.sfx.busDieselIdle.path` | `"./sounds/bus-diesel-idle.mp3"` |  |
| `audio.sfx.busDieselIdle.refDistance` | `16` |  |
| `audio.sfx.busDieselIdle.rolloffPower` | `1.7` |  |
| `audio.sfx.busDieselIdle.maxDistance` | `450` |  |
| `audio.sfx.busDieselIdle.loop` | `true` |  |
| `audio.sfx.busDieselIdle.maxConcurrent` | `2` |  |
| `audio.sfx.busDieselIdle.gain` | `0.5` |  |
| **`audio.sfx.carHorn`** | *(group)* |  |
| `audio.sfx.carHorn.path` | `"./sounds/car-horn.mp3"` |  |
| `audio.sfx.carHorn.refDistance` | `20` |  |
| `audio.sfx.carHorn.rolloffPower` | `1.6` |  |
| `audio.sfx.carHorn.maxDistance` | `500` |  |
| `audio.sfx.carHorn.gain` | `0.7` |  |
| `audio.sfx.carHorn.minGap` | `4` |  |
| `audio.sfx.carHorn.variants` | `4` |  |
| `audio.sfx.carHorn.duck` | `0.2` |  |
| **`audio.sfx.bicycleBell`** | *(group)* |  |
| `audio.sfx.bicycleBell.path` | `"./sounds/bicycle-bell.mp3"` |  |
| `audio.sfx.bicycleBell.refDistance` | `8` |  |
| `audio.sfx.bicycleBell.rolloffPower` | `2.5` |  |
| `audio.sfx.bicycleBell.maxDistance` | `180` |  |
| `audio.sfx.bicycleBell.gain` | `0.5` |  |
| `audio.sfx.bicycleBell.minGap` | `8` |  |
| **`audio.sfx.footstepsPlank`** | *(group)* | — Footsteps of the walker (walk mode), by surface under the camera |
| `audio.sfx.footstepsPlank.path` | `"./sounds/footsteps-plank.mp3"` |  |
| `audio.sfx.footstepsPlank.refDistance` | `4` |  |
| `audio.sfx.footstepsPlank.rolloffPower` | `3` |  |
| `audio.sfx.footstepsPlank.maxDistance` | `40` |  |
| `audio.sfx.footstepsPlank.gain` | `0.5` |  |
| `audio.sfx.footstepsPlank.variants` | `4` |  |
| **`audio.sfx.footstepsStone`** | *(group)* |  |
| `audio.sfx.footstepsStone.path` | `"./sounds/footsteps-stone.mp3"` |  |
| `audio.sfx.footstepsStone.refDistance` | `4` |  |
| `audio.sfx.footstepsStone.rolloffPower` | `3` |  |
| `audio.sfx.footstepsStone.maxDistance` | `40` |  |
| `audio.sfx.footstepsStone.gain` | `0.5` |  |
| `audio.sfx.footstepsStone.variants` | `4` |  |
| **`audio.sfx.footstepsGravel`** | *(group)* |  |
| `audio.sfx.footstepsGravel.path` | `"./sounds/footsteps-gravel.mp3"` |  |
| `audio.sfx.footstepsGravel.refDistance` | `4` |  |
| `audio.sfx.footstepsGravel.rolloffPower` | `3` |  |
| `audio.sfx.footstepsGravel.maxDistance` | `40` |  |
| `audio.sfx.footstepsGravel.gain` | `0.5` |  |
| `audio.sfx.footstepsGravel.variants` | `4` |  |
| **`audio.sfx.snowFootsteps`** | *(group)* |  |
| `audio.sfx.snowFootsteps.path` | `"./sounds/snow-footsteps.mp3"` |  |
| `audio.sfx.snowFootsteps.refDistance` | `4` |  |
| `audio.sfx.snowFootsteps.rolloffPower` | `3` |  |
| `audio.sfx.snowFootsteps.maxDistance` | `40` |  |
| `audio.sfx.snowFootsteps.gain` | `0.55` |  |
| `audio.sfx.snowFootsteps.variants` | `4` |  |
| **`audio.sfx.mudWalkHuman`** | *(group)* |  |
| `audio.sfx.mudWalkHuman.path` | `"./sounds/mud-walk-human.mp3"` |  |
| `audio.sfx.mudWalkHuman.refDistance` | `4` |  |
| `audio.sfx.mudWalkHuman.rolloffPower` | `3` |  |
| `audio.sfx.mudWalkHuman.maxDistance` | `40` |  |
| `audio.sfx.mudWalkHuman.gain` | `0.55` |  |
| `audio.sfx.mudWalkHuman.variants` | `4` |  |
| **`audio.sfx.kidsPlaying`** | *(group)* | — People |
| `audio.sfx.kidsPlaying.path` | `"./sounds/kids-playing.mp3"` |  |
| `audio.sfx.kidsPlaying.refDistance` | `15` |  |
| `audio.sfx.kidsPlaying.rolloffPower` | `1.7` |  |
| `audio.sfx.kidsPlaying.maxDistance` | `400` |  |
| `audio.sfx.kidsPlaying.loop` | `true` |  |
| `audio.sfx.kidsPlaying.maxConcurrent` | `2` |  |
| `audio.sfx.kidsPlaying.gain` | `0.6` |  |
| **`audio.sfx.woodChop`** | *(group)* | schools gate it to recess/after school (audio.sites.school); the parade plays it ungated |
| `audio.sfx.woodChop.path` | `"./sounds/wood-chop.mp3"` |  |
| `audio.sfx.woodChop.refDistance` | `10` |  |
| `audio.sfx.woodChop.rolloffPower` | `2.5` |  |
| `audio.sfx.woodChop.maxDistance` | `250` |  |
| `audio.sfx.woodChop.gain` | `0.7` |  |
| `audio.sfx.woodChop.minGap` | `1` |  |
| `audio.sfx.woodChop.variants` | `3` |  |
| **`audio.sfx.woodChop.gate`** | *(group)* |  |
| `audio.sfx.woodChop.gate.hour` | `[7,18]` |  |
| `audio.sfx.woodChop.gate.dow` | `[1,6]` |  |
| **`audio.sfx.newsboyCry`** | *(group)* |  |
| `audio.sfx.newsboyCry.path` | `"./sounds/newsboy-cry.mp3"` |  |
| `audio.sfx.newsboyCry.refDistance` | `14` |  |
| `audio.sfx.newsboyCry.rolloffPower` | `2.5` |  |
| `audio.sfx.newsboyCry.maxDistance` | `200` |  |
| `audio.sfx.newsboyCry.gain` | `0.6` |  |
| `audio.sfx.newsboyCry.minGap` | `25` |  |
| `audio.sfx.newsboyCry.variants` | `3` |  |
| `audio.sfx.newsboyCry.every` | `[25,70]` |  |
| `audio.sfx.newsboyCry.dist` | `[12,70]` |  |
| **`audio.sfx.newsboyCry.gate`** | *(group)* |  |
| `audio.sfx.newsboyCry.gate.hour` | `[7,18]` |  |
| `audio.sfx.newsboyCry.gate.year` | `[1880,1950]` |  |
| `audio.sfx.newsboyCry.gate.built` | `[0.5,1]` |  |
| **`audio.sfx.cattleHerd`** | *(group)* | — Animals |
| `audio.sfx.cattleHerd.path` | `"./sounds/cattle-herd.mp3"` |  |
| `audio.sfx.cattleHerd.refDistance` | `15` |  |
| `audio.sfx.cattleHerd.rolloffPower` | `1.7` |  |
| `audio.sfx.cattleHerd.maxDistance` | `500` |  |
| `audio.sfx.cattleHerd.loop` | `true` |  |
| `audio.sfx.cattleHerd.maxConcurrent` | `2` |  |
| `audio.sfx.cattleHerd.gain` | `0.6` |  |
| **`audio.sfx.cattleMoo`** | *(group)* |  |
| `audio.sfx.cattleMoo.path` | `"./sounds/cattle-moo.mp3"` |  |
| `audio.sfx.cattleMoo.refDistance` | `15` |  |
| `audio.sfx.cattleMoo.rolloffPower` | `2.5` |  |
| `audio.sfx.cattleMoo.maxDistance` | `500` |  |
| `audio.sfx.cattleMoo.gain` | `0.7` |  |
| `audio.sfx.cattleMoo.minGap` | `8` |  |
| `audio.sfx.cattleMoo.variants` | `3` |  |
| **`audio.sfx.chickens`** | *(group)* |  |
| `audio.sfx.chickens.path` | `"./sounds/chickens.mp3"` |  |
| `audio.sfx.chickens.refDistance` | `8` |  |
| `audio.sfx.chickens.rolloffPower` | `2.5` |  |
| `audio.sfx.chickens.maxDistance` | `200` |  |
| `audio.sfx.chickens.gain` | `0.5` |  |
| `audio.sfx.chickens.minGap` | `6` |  |
| `audio.sfx.chickens.variants` | `2` |  |
| **`audio.sfx.chickens.gate`** | *(group)* |  |
| `audio.sfx.chickens.gate.hour` | `[5,20]` |  |
| **`audio.sfx.roosterCrow`** | *(group)* |  |
| `audio.sfx.roosterCrow.path` | `"./sounds/rooster-crow.mp3"` |  |
| `audio.sfx.roosterCrow.refDistance` | `20` |  |
| `audio.sfx.roosterCrow.rolloffPower` | `2.5` |  |
| `audio.sfx.roosterCrow.maxDistance` | `700` |  |
| `audio.sfx.roosterCrow.gain` | `0.7` |  |
| `audio.sfx.roosterCrow.minGap` | `120` |  |
| `audio.sfx.roosterCrow.variants` | `2` |  |
| `audio.sfx.roosterCrow.every` | `[60,160]` |  |
| `audio.sfx.roosterCrow.dist` | `[60,300]` |  |
| **`audio.sfx.roosterCrow.gate`** | *(group)* |  |
| `audio.sfx.roosterCrow.gate.hour` | `[4,6.5]` |  |
| `audio.sfx.roosterCrow.gate.built` | `[0,0.7]` |  |
| **`audio.sfx.dogsBarking`** | *(group)* |  |
| `audio.sfx.dogsBarking.path` | `"./sounds/dogs-barking.mp3"` |  |
| `audio.sfx.dogsBarking.refDistance` | `12` |  |
| `audio.sfx.dogsBarking.rolloffPower` | `2.5` |  |
| `audio.sfx.dogsBarking.maxDistance` | `400` |  |
| `audio.sfx.dogsBarking.gain` | `0.6` |  |
| `audio.sfx.dogsBarking.minGap` | `10` |  |
| `audio.sfx.dogsBarking.variants` | `2` |  |
| `audio.sfx.dogsBarking.every` | `[25,80]` |  |
| `audio.sfx.dogsBarking.dist` | `[40,250]` |  |
| **`audio.sfx.dogsBarking.gate`** | *(group)* |  |
| `audio.sfx.dogsBarking.gate.built` | `[0.05,1]` |  |
| **`audio.sfx.coyotes`** | *(group)* |  |
| `audio.sfx.coyotes.path` | `"./sounds/coyotes.mp3"` |  |
| `audio.sfx.coyotes.gain` | `0.6` |  |
| `audio.sfx.coyotes.refDistance` | `80` |  |
| `audio.sfx.coyotes.rolloffPower` | `1.2` |  |
| `audio.sfx.coyotes.maxDistance` | `1500` |  |
| `audio.sfx.coyotes.minGap` | `40` |  |
| `audio.sfx.coyotes.every` | `[45,140]` |  |
| `audio.sfx.coyotes.dist` | `[250,900]` |  |
| **`audio.sfx.coyotes.gate`** | *(group)* |  |
| `audio.sfx.coyotes.gate.hour` | `[20,5]` |  |
| `audio.sfx.coyotes.gate.built` | `[0,0.5]` |  |
| `audio.sfx.coyotes.gate.snow` | `[0,1]` |  |
| **`audio.sfx.wolves`** | *(group)* |  |
| `audio.sfx.wolves.path` | `"./sounds/wolves.mp3"` |  |
| `audio.sfx.wolves.gain` | `0.6` |  |
| `audio.sfx.wolves.refDistance` | `80` |  |
| `audio.sfx.wolves.rolloffPower` | `1.2` |  |
| `audio.sfx.wolves.maxDistance` | `1800` |  |
| `audio.sfx.wolves.minGap` | `60` |  |
| `audio.sfx.wolves.every` | `[60,200]` |  |
| `audio.sfx.wolves.dist` | `[400,1200]` |  |
| **`audio.sfx.wolves.gate`** | *(group)* |  |
| `audio.sfx.wolves.gate.hour` | `[21,4]` |  |
| `audio.sfx.wolves.gate.built` | `[0,0.25]` |  |
| `audio.sfx.wolves.gate.year` | `[1800,1900]` |  |
| **`audio.sfx.birdsCrow`** | *(group)* |  |
| `audio.sfx.birdsCrow.path` | `"./sounds/birds-crow.mp3"` |  |
| `audio.sfx.birdsCrow.refDistance` | `20` |  |
| `audio.sfx.birdsCrow.rolloffPower` | `2.5` |  |
| `audio.sfx.birdsCrow.maxDistance` | `500` |  |
| `audio.sfx.birdsCrow.gain` | `0.5` |  |
| `audio.sfx.birdsCrow.minGap` | `12` |  |
| `audio.sfx.birdsCrow.variants` | `2` |  |
| `audio.sfx.birdsCrow.every` | `[12,40]` |  |
| `audio.sfx.birdsCrow.dist` | `[30,200]` |  |
| **`audio.sfx.birdsCrow.gate`** | *(group)* |  |
| `audio.sfx.birdsCrow.gate.hour` | `[5,20]` |  |
| `audio.sfx.birdsCrow.gate.snow` | `[0,0.6]` |  |
| **`audio.sfx.birdsGeese`** | *(group)* |  |
| `audio.sfx.birdsGeese.path` | `"./sounds/birds-geese.mp3"` |  |
| `audio.sfx.birdsGeese.gain` | `0.6` |  |
| `audio.sfx.birdsGeese.refDistance` | `60` |  |
| `audio.sfx.birdsGeese.rolloffPower` | `1.3` |  |
| `audio.sfx.birdsGeese.maxDistance` | `1500` |  |
| `audio.sfx.birdsGeese.minGap` | `60` |  |
| `audio.sfx.birdsGeese.variants` | `2` |  |
| `audio.sfx.birdsGeese.every` | `[40,130]` |  |
| `audio.sfx.birdsGeese.dist` | `[100,600]` |  |
| **`audio.sfx.birdsGeese.gate`** | *(group)* |  |
| `audio.sfx.birdsGeese.gate.month` | `[[3,5],[9,10]]` |  |
| `audio.sfx.birdsGeese.gate.hour` | `[6,20]` |  |
| **`audio.sfx.birdsGulls`** | *(group)* |  |
| `audio.sfx.birdsGulls.path` | `"./sounds/birds-gulls.mp3"` |  |
| `audio.sfx.birdsGulls.bed` | `true` |  |
| `audio.sfx.birdsGulls.gain` | `0.35` |  |
| **`audio.sfx.birdsGulls.gate`** | *(group)* |  |
| `audio.sfx.birdsGulls.gate.hour` | `[5,21]` |  |
| `audio.sfx.birdsGulls.gate.snow` | `[0,0.6]` |  |
| **`audio.sfx.birdsSongbirds`** | *(group)* |  |
| `audio.sfx.birdsSongbirds.path` | `"./sounds/birds-songbirds.mp3"` |  |
| `audio.sfx.birdsSongbirds.bed` | `true` |  |
| `audio.sfx.birdsSongbirds.gain` | `0.35` |  |
| **`audio.sfx.birdsSongbirds.gate`** | *(group)* |  |
| `audio.sfx.birdsSongbirds.gate.snow` | `[0,0.2]` |  |
| `audio.sfx.birdsSongbirds.gate.green` | `[0.25,1]` |  |
| **`audio.sfx.crickets`** | *(group)* |  |
| `audio.sfx.crickets.path` | `"./sounds/crickets.mp3"` |  |
| `audio.sfx.crickets.bed` | `true` |  |
| `audio.sfx.crickets.gain` | `0.35` |  |
| **`audio.sfx.crickets.gate`** | *(group)* |  |
| `audio.sfx.crickets.gate.snow` | `[0,0.2]` |  |
| `audio.sfx.crickets.gate.green` | `[0.5,1]` |  |
| **`audio.sfx.factoryAmbience`** | *(group)* | — Places |
| `audio.sfx.factoryAmbience.path` | `"./sounds/factory-ambience.mp3"` |  |
| `audio.sfx.factoryAmbience.refDistance` | `20` |  |
| `audio.sfx.factoryAmbience.rolloffPower` | `1.7` |  |
| `audio.sfx.factoryAmbience.maxDistance` | `400` |  |
| `audio.sfx.factoryAmbience.loop` | `true` |  |
| `audio.sfx.factoryAmbience.maxConcurrent` | `2` |  |
| `audio.sfx.factoryAmbience.gain` | `0.6` |  |
| **`audio.sfx.factoryAmbience.gate`** | *(group)* |  |
| `audio.sfx.factoryAmbience.gate.hour` | `[[7,12],[13,17]]` |  |
| `audio.sfx.factoryAmbience.gate.dow` | `[1,6]` |  |
| **`audio.sfx.factoryWhistle`** | *(group)* |  |
| `audio.sfx.factoryWhistle.path` | `"./sounds/factory-whistle.mp3"` |  |
| `audio.sfx.factoryWhistle.refDistance` | `45` |  |
| `audio.sfx.factoryWhistle.rolloffPower` | `1.3` |  |
| `audio.sfx.factoryWhistle.maxDistance` | `2200` |  |
| `audio.sfx.factoryWhistle.gain` | `1` |  |
| `audio.sfx.factoryWhistle.minGap` | `30` |  |
| `audio.sfx.factoryWhistle.duck` | `0.6` |  |
| `audio.sfx.factoryWhistle.variants` | `2` |  |
| **`audio.sfx.lumberMill`** | *(group)* |  |
| `audio.sfx.lumberMill.path` | `"./sounds/lumber-mill.mp3"` |  |
| `audio.sfx.lumberMill.refDistance` | `20` |  |
| `audio.sfx.lumberMill.rolloffPower` | `1.7` |  |
| `audio.sfx.lumberMill.maxDistance` | `450` |  |
| `audio.sfx.lumberMill.loop` | `true` |  |
| `audio.sfx.lumberMill.maxConcurrent` | `2` |  |
| `audio.sfx.lumberMill.gain` | `0.6` |  |
| **`audio.sfx.lumberMill.gate`** | *(group)* |  |
| `audio.sfx.lumberMill.gate.hour` | `[7,17]` |  |
| `audio.sfx.lumberMill.gate.dow` | `[1,6]` |  |
| **`audio.sfx.windmill`** | *(group)* |  |
| `audio.sfx.windmill.path` | `"./sounds/windmill.mp3"` |  |
| `audio.sfx.windmill.refDistance` | `15` |  |
| `audio.sfx.windmill.rolloffPower` | `1.7` |  |
| `audio.sfx.windmill.maxDistance` | `300` |  |
| `audio.sfx.windmill.loop` | `true` |  |
| `audio.sfx.windmill.maxConcurrent` | `1` |  |
| `audio.sfx.windmill.gain` | `0.5` |  |
| **`audio.sfx.wellPump`** | *(group)* |  |
| `audio.sfx.wellPump.path` | `"./sounds/well-pump.mp3"` |  |
| `audio.sfx.wellPump.refDistance` | `8` |  |
| `audio.sfx.wellPump.rolloffPower` | `2.5` |  |
| `audio.sfx.wellPump.maxDistance` | `180` |  |
| `audio.sfx.wellPump.gain` | `0.5` |  |
| `audio.sfx.wellPump.minGap` | `20` |  |
| **`audio.sfx.wellPump.gate`** | *(group)* |  |
| `audio.sfx.wellPump.gate.hour` | `[6,19]` |  |
| **`audio.sfx.gateCreak`** | *(group)* |  |
| `audio.sfx.gateCreak.path` | `"./sounds/gate-creak.mp3"` |  |
| `audio.sfx.gateCreak.refDistance` | `8` |  |
| `audio.sfx.gateCreak.rolloffPower` | `2.5` |  |
| `audio.sfx.gateCreak.maxDistance` | `180` |  |
| `audio.sfx.gateCreak.gain` | `0.45` |  |
| `audio.sfx.gateCreak.minGap` | `30` |  |
| `audio.sfx.gateCreak.variants` | `2` |  |
| **`audio.sfx.doorCreak`** | *(group)* |  |
| `audio.sfx.doorCreak.path` | `"./sounds/door-creak.mp3"` |  |
| `audio.sfx.doorCreak.refDistance` | `8` |  |
| `audio.sfx.doorCreak.rolloffPower` | `2.5` |  |
| `audio.sfx.doorCreak.maxDistance` | `180` |  |
| `audio.sfx.doorCreak.gain` | `0.45` |  |
| `audio.sfx.doorCreak.minGap` | `30` |  |
| `audio.sfx.doorCreak.variants` | `2` |  |
| **`audio.sfx.telegraphKey`** | *(group)* |  |
| `audio.sfx.telegraphKey.path` | `"./sounds/telegraph-key.mp3"` |  |
| `audio.sfx.telegraphKey.refDistance` | `5` |  |
| `audio.sfx.telegraphKey.rolloffPower` | `2.5` |  |
| `audio.sfx.telegraphKey.maxDistance` | `60` |  |
| `audio.sfx.telegraphKey.gain` | `0.45` |  |
| `audio.sfx.telegraphKey.minGap` | `6` |  |
| **`audio.sfx.telegraphKey.gate`** | *(group)* |  |
| `audio.sfx.telegraphKey.gate.hour` | `[7,20]` |  |
| `audio.sfx.telegraphKey.gate.year` | `[1860,1960]` |  |
| **`audio.sfx.blacksmithForge`** | *(group)* |  |
| `audio.sfx.blacksmithForge.path` | `"./sounds/blacksmith-forge.mp3"` |  |
| `audio.sfx.blacksmithForge.refDistance` | `6` |  |
| `audio.sfx.blacksmithForge.rolloffPower` | `2.5` |  |
| `audio.sfx.blacksmithForge.maxDistance` | `120` |  |
| `audio.sfx.blacksmithForge.loop` | `true` |  |
| `audio.sfx.blacksmithForge.maxConcurrent` | `2` |  |
| `audio.sfx.blacksmithForge.gain` | `0.5` |  |
| **`audio.sfx.blacksmithForge.gate`** | *(group)* |  |
| `audio.sfx.blacksmithForge.gate.hour` | `[7,18]` |  |
| `audio.sfx.blacksmithForge.gate.dow` | `[1,6]` |  |
| **`audio.sfx.blacksmithAnvil`** | *(group)* |  |
| `audio.sfx.blacksmithAnvil.path` | `"./sounds/blacksmith-anvil.mp3"` |  |
| `audio.sfx.blacksmithAnvil.refDistance` | `10` |  |
| `audio.sfx.blacksmithAnvil.rolloffPower` | `2.5` |  |
| `audio.sfx.blacksmithAnvil.maxDistance` | `250` |  |
| `audio.sfx.blacksmithAnvil.gain` | `0.7` |  |
| `audio.sfx.blacksmithAnvil.minGap` | `2` |  |
| `audio.sfx.blacksmithAnvil.variants` | `3` |  |
| **`audio.sfx.blacksmithAnvil.gate`** | *(group)* |  |
| `audio.sfx.blacksmithAnvil.gate.hour` | `[7,18]` |  |
| `audio.sfx.blacksmithAnvil.gate.dow` | `[1,6]` |  |
| **`audio.sfx.blacksmithQuench`** | *(group)* |  |
| `audio.sfx.blacksmithQuench.path` | `"./sounds/blacksmith-quench.mp3"` |  |
| `audio.sfx.blacksmithQuench.refDistance` | `8` |  |
| `audio.sfx.blacksmithQuench.rolloffPower` | `2.5` |  |
| `audio.sfx.blacksmithQuench.maxDistance` | `150` |  |
| `audio.sfx.blacksmithQuench.gain` | `0.6` |  |
| `audio.sfx.blacksmithQuench.minGap` | `30` |  |
| **`audio.sfx.blacksmithQuench.gate`** | *(group)* |  |
| `audio.sfx.blacksmithQuench.gate.hour` | `[7,18]` |  |
| `audio.sfx.blacksmithQuench.gate.dow` | `[1,6]` |  |
| **`audio.sfx.tinsmith`** | *(group)* |  |
| `audio.sfx.tinsmith.path` | `"./sounds/tinsmith.mp3"` |  |
| `audio.sfx.tinsmith.refDistance` | `8` |  |
| `audio.sfx.tinsmith.rolloffPower` | `2.5` |  |
| `audio.sfx.tinsmith.maxDistance` | `180` |  |
| `audio.sfx.tinsmith.gain` | `0.6` |  |
| `audio.sfx.tinsmith.minGap` | `3` |  |
| `audio.sfx.tinsmith.variants` | `2` |  |
| **`audio.sfx.tinsmith.gate`** | *(group)* |  |
| `audio.sfx.tinsmith.gate.hour` | `[7,18]` |  |
| `audio.sfx.tinsmith.gate.dow` | `[1,6]` |  |
| **`audio.sfx.printingPress`** | *(group)* |  |
| `audio.sfx.printingPress.path` | `"./sounds/printing-press.mp3"` |  |
| `audio.sfx.printingPress.refDistance` | `8` |  |
| `audio.sfx.printingPress.rolloffPower` | `2.5` |  |
| `audio.sfx.printingPress.maxDistance` | `150` |  |
| `audio.sfx.printingPress.loop` | `true` |  |
| `audio.sfx.printingPress.maxConcurrent` | `2` |  |
| `audio.sfx.printingPress.gain` | `0.5` |  |
| **`audio.sfx.printingPress.gate`** | *(group)* |  |
| `audio.sfx.printingPress.gate.hour` | `[7,18]` |  |
| `audio.sfx.printingPress.gate.dow` | `[1,6]` |  |
| **`audio.sfx.typewriterTyping`** | *(group)* |  |
| `audio.sfx.typewriterTyping.path` | `"./sounds/typewriter-typing.mp3"` |  |
| `audio.sfx.typewriterTyping.refDistance` | `5` |  |
| `audio.sfx.typewriterTyping.rolloffPower` | `2.5` |  |
| `audio.sfx.typewriterTyping.maxDistance` | `60` |  |
| `audio.sfx.typewriterTyping.gain` | `0.35` |  |
| `audio.sfx.typewriterTyping.minGap` | `6` |  |
| **`audio.sfx.typewriterTyping.gate`** | *(group)* |  |
| `audio.sfx.typewriterTyping.gate.year` | `[1885,1999]` |  |
| `audio.sfx.typewriterTyping.gate.hour` | `[8,18]` |  |
| `audio.sfx.typewriterTyping.gate.dow` | `[1,6]` |  |
| **`audio.sfx.typewriterBell`** | *(group)* |  |
| `audio.sfx.typewriterBell.path` | `"./sounds/typewriter-bell.mp3"` |  |
| `audio.sfx.typewriterBell.refDistance` | `5` |  |
| `audio.sfx.typewriterBell.rolloffPower` | `2.5` |  |
| `audio.sfx.typewriterBell.maxDistance` | `60` |  |
| `audio.sfx.typewriterBell.gain` | `0.35` |  |
| `audio.sfx.typewriterBell.minGap` | `15` |  |
| **`audio.sfx.typewriterBell.gate`** | *(group)* |  |
| `audio.sfx.typewriterBell.gate.year` | `[1885,1999]` |  |
| `audio.sfx.typewriterBell.gate.hour` | `[8,18]` |  |
| `audio.sfx.typewriterBell.gate.dow` | `[1,6]` |  |
| **`audio.sfx.cashRegister`** | *(group)* |  |
| `audio.sfx.cashRegister.path` | `"./sounds/cash-register.mp3"` |  |
| `audio.sfx.cashRegister.refDistance` | `6` |  |
| `audio.sfx.cashRegister.rolloffPower` | `2.5` |  |
| `audio.sfx.cashRegister.maxDistance` | `80` |  |
| `audio.sfx.cashRegister.gain` | `0.5` |  |
| `audio.sfx.cashRegister.minGap` | `10` |  |
| **`audio.sfx.cashRegister.gate`** | *(group)* |  |
| `audio.sfx.cashRegister.gate.year` | `[1885,1999]` |  |
| `audio.sfx.cashRegister.gate.hour` | `[8,18]` |  |
| `audio.sfx.cashRegister.gate.dow` | `[1,6]` |  |
| **`audio.sfx.barAmbience`** | *(group)* |  |
| `audio.sfx.barAmbience.path` | `"./sounds/bar-ambience.mp3"` |  |
| `audio.sfx.barAmbience.refDistance` | `6` |  |
| `audio.sfx.barAmbience.rolloffPower` | `2.5` |  |
| `audio.sfx.barAmbience.maxDistance` | `120` |  |
| `audio.sfx.barAmbience.loop` | `true` |  |
| `audio.sfx.barAmbience.maxConcurrent` | `2` |  |
| `audio.sfx.barAmbience.gain` | `0.7` |  |
| **`audio.sfx.barAmbience.gate`** | *(group)* |  |
| `audio.sfx.barAmbience.gate.hour` | `[11,22]` |  |
| **`audio.sfx.saloonPiano`** | *(group)* |  |
| `audio.sfx.saloonPiano.path` | `"./sounds/saloon-piano.mp3"` |  |
| `audio.sfx.saloonPiano.refDistance` | `6` |  |
| `audio.sfx.saloonPiano.rolloffPower` | `2.5` |  |
| `audio.sfx.saloonPiano.maxDistance` | `120` |  |
| `audio.sfx.saloonPiano.loop` | `true` |  |
| `audio.sfx.saloonPiano.maxConcurrent` | `1` |  |
| `audio.sfx.saloonPiano.gain` | `0.5` |  |
| **`audio.sfx.saloonPiano.gate`** | *(group)* |  |
| `audio.sfx.saloonPiano.gate.hour` | `[17,22]` |  |
| **`audio.sfx.barGlassClink`** | *(group)* |  |
| `audio.sfx.barGlassClink.path` | `"./sounds/bar-glass-clink.mp3"` |  |
| `audio.sfx.barGlassClink.refDistance` | `6` |  |
| `audio.sfx.barGlassClink.rolloffPower` | `2.5` |  |
| `audio.sfx.barGlassClink.maxDistance` | `100` |  |
| `audio.sfx.barGlassClink.gain` | `0.4` |  |
| `audio.sfx.barGlassClink.minGap` | `4` |  |
| `audio.sfx.barGlassClink.variants` | `3` |  |
| **`audio.sfx.barGlassClink.gate`** | *(group)* |  |
| `audio.sfx.barGlassClink.gate.hour` | `[11,22]` |  |
| **`audio.sfx.dishesBreak`** | *(group)* |  |
| `audio.sfx.dishesBreak.path` | `"./sounds/dishes-break.mp3"` |  |
| `audio.sfx.dishesBreak.refDistance` | `8` |  |
| `audio.sfx.dishesBreak.rolloffPower` | `2.5` |  |
| `audio.sfx.dishesBreak.maxDistance` | `120` |  |
| `audio.sfx.dishesBreak.gain` | `0.6` |  |
| `audio.sfx.dishesBreak.minGap` | `90` |  |
| **`audio.sfx.cookingSizzle`** | *(group)* |  |
| `audio.sfx.cookingSizzle.path` | `"./sounds/cooking-sizzle.mp3"` |  |
| `audio.sfx.cookingSizzle.refDistance` | `4` |  |
| `audio.sfx.cookingSizzle.rolloffPower` | `2.5` |  |
| `audio.sfx.cookingSizzle.maxDistance` | `50` |  |
| `audio.sfx.cookingSizzle.loop` | `true` |  |
| `audio.sfx.cookingSizzle.maxConcurrent` | `2` |  |
| `audio.sfx.cookingSizzle.gain` | `0.3` |  |
| **`audio.sfx.cookingSizzle.gate`** | *(group)* |  |
| `audio.sfx.cookingSizzle.gate.hour` | `[[6.5,8.5],[11.5,13.5],[17,19.5]]` |  |
| **`audio.sfx.cookingBoil`** | *(group)* |  |
| `audio.sfx.cookingBoil.path` | `"./sounds/cooking-boil.mp3"` |  |
| `audio.sfx.cookingBoil.refDistance` | `4` |  |
| `audio.sfx.cookingBoil.rolloffPower` | `2.5` |  |
| `audio.sfx.cookingBoil.maxDistance` | `50` |  |
| `audio.sfx.cookingBoil.loop` | `true` |  |
| `audio.sfx.cookingBoil.maxConcurrent` | `2` |  |
| `audio.sfx.cookingBoil.gain` | `0.3` |  |
| **`audio.sfx.cookingBoil.gate`** | *(group)* |  |
| `audio.sfx.cookingBoil.gate.hour` | `[[6.5,8.5],[11.5,13.5],[17,19.5]]` |  |
| **`audio.sfx.cookingChop`** | *(group)* |  |
| `audio.sfx.cookingChop.path` | `"./sounds/cooking-chop.mp3"` |  |
| `audio.sfx.cookingChop.refDistance` | `4` |  |
| `audio.sfx.cookingChop.rolloffPower` | `2.5` |  |
| `audio.sfx.cookingChop.maxDistance` | `50` |  |
| `audio.sfx.cookingChop.gain` | `0.3` |  |
| `audio.sfx.cookingChop.minGap` | `3` |  |
| **`audio.sfx.cookingChop.gate`** | *(group)* |  |
| `audio.sfx.cookingChop.gate.hour` | `[[6.5,8.5],[11.5,13.5],[17,19.5]]` |  |
| **`audio.sfx.sewingMachine`** | *(group)* |  |
| `audio.sfx.sewingMachine.path` | `"./sounds/sewing-machine.mp3"` |  |
| `audio.sfx.sewingMachine.refDistance` | `4` |  |
| `audio.sfx.sewingMachine.rolloffPower` | `2.5` |  |
| `audio.sfx.sewingMachine.maxDistance` | `50` |  |
| `audio.sfx.sewingMachine.loop` | `true` |  |
| `audio.sfx.sewingMachine.maxConcurrent` | `2` |  |
| `audio.sfx.sewingMachine.gain` | `0.35` |  |
| **`audio.sfx.sewingMachine.gate`** | *(group)* |  |
| `audio.sfx.sewingMachine.gate.hour` | `[9,16]` |  |
| `audio.sfx.sewingMachine.gate.year` | `[1860,2000]` |  |
| **`audio.sfx.loomWeaving`** | *(group)* |  |
| `audio.sfx.loomWeaving.path` | `"./sounds/loom-weaving.mp3"` |  |
| `audio.sfx.loomWeaving.refDistance` | `4` |  |
| `audio.sfx.loomWeaving.rolloffPower` | `2.5` |  |
| `audio.sfx.loomWeaving.maxDistance` | `50` |  |
| `audio.sfx.loomWeaving.loop` | `true` |  |
| `audio.sfx.loomWeaving.maxConcurrent` | `2` |  |
| `audio.sfx.loomWeaving.gain` | `0.35` |  |
| **`audio.sfx.loomWeaving.gate`** | *(group)* |  |
| `audio.sfx.loomWeaving.gate.hour` | `[9,16]` |  |
| `audio.sfx.loomWeaving.gate.year` | `[1700,1900]` |  |
| **`audio.sfx.spinningWheel`** | *(group)* |  |
| `audio.sfx.spinningWheel.path` | `"./sounds/spinning-wheel.mp3"` |  |
| `audio.sfx.spinningWheel.refDistance` | `4` |  |
| `audio.sfx.spinningWheel.rolloffPower` | `2.5` |  |
| `audio.sfx.spinningWheel.maxDistance` | `50` |  |
| `audio.sfx.spinningWheel.loop` | `true` |  |
| `audio.sfx.spinningWheel.maxConcurrent` | `2` |  |
| `audio.sfx.spinningWheel.gain` | `0.35` |  |
| **`audio.sfx.spinningWheel.gate`** | *(group)* |  |
| `audio.sfx.spinningWheel.gate.hour` | `[9,16]` |  |
| `audio.sfx.spinningWheel.gate.year` | `[1700,1890]` |  |
| **`audio.sfx.churchBell`** | *(group)* |  |
| `audio.sfx.churchBell.path` | `"./sounds/church-bell.mp3"` |  |
| `audio.sfx.churchBell.refDistance` | `60` |  |
| `audio.sfx.churchBell.rolloffPower` | `1.3` |  |
| `audio.sfx.churchBell.maxDistance` | `2500` |  |
| `audio.sfx.churchBell.gain` | `0.9` |  |
| `audio.sfx.churchBell.minGap` | `60` |  |
| `audio.sfx.churchBell.duck` | `0.6` |  |
| `audio.sfx.churchBell.variants` | `2` |  |
| **`audio.sfx.churchBell.gate`** | *(group)* |  |
| `audio.sfx.churchBell.gate.dow` | `[0,0]` |  |
| `audio.sfx.churchBell.gate.hour` | `[9.5,11]` |  |
| **`audio.sfx.schoolBell`** | *(group)* |  |
| `audio.sfx.schoolBell.path` | `"./sounds/school-bell.mp3"` |  |
| `audio.sfx.schoolBell.refDistance` | `40` |  |
| `audio.sfx.schoolBell.rolloffPower` | `1.3` |  |
| `audio.sfx.schoolBell.maxDistance` | `1200` |  |
| `audio.sfx.schoolBell.gain` | `0.7` |  |
| `audio.sfx.schoolBell.minGap` | `30` |  |
| `audio.sfx.schoolBell.duck` | `0.4` |  |
| **`audio.sfx.schoolBell.gate`** | *(group)* |  |
| `audio.sfx.schoolBell.gate.dow` | `[1,5]` |  |
| **`audio.sfx.waterLapping`** | *(group)* |  |
| `audio.sfx.waterLapping.path` | `"./sounds/water-lapping.mp3"` |  |
| `audio.sfx.waterLapping.bed` | `true` |  |
| `audio.sfx.waterLapping.gain` | `0.4` |  |
| **`audio.sfx.buildingFire`** | *(group)* | — Events |
| `audio.sfx.buildingFire.path` | `"./sounds/building-fire.mp3"` |  |
| `audio.sfx.buildingFire.refDistance` | `25` |  |
| `audio.sfx.buildingFire.rolloffPower` | `2` |  |
| `audio.sfx.buildingFire.maxDistance` | `700` |  |
| `audio.sfx.buildingFire.loop` | `true` |  |
| `audio.sfx.buildingFire.maxConcurrent` | `2` |  |
| `audio.sfx.buildingFire.gain` | `0.9` |  |
| **`audio.sfx.photoFlash`** | *(group)* |  |
| `audio.sfx.photoFlash.path` | `"./sounds/photo-flash.mp3"` |  |
| `audio.sfx.photoFlash.gain` | `0.6` |  |
| `audio.sfx.photoFlash.minGap` | `1` |  |
| **`audio.sfx.pistolCock`** | *(group)* |  |
| `audio.sfx.pistolCock.path` | `"./sounds/pistol-cock.mp3"` |  |
| `audio.sfx.pistolCock.refDistance` | `10` |  |
| `audio.sfx.pistolCock.rolloffPower` | `2.5` |  |
| `audio.sfx.pistolCock.maxDistance` | `300` |  |
| `audio.sfx.pistolCock.gain` | `0.6` |  |
| **`audio.sfx.pistolShot`** | *(group)* |  |
| `audio.sfx.pistolShot.path` | `"./sounds/pistol-shot.mp3"` |  |
| `audio.sfx.pistolShot.refDistance` | `40` |  |
| `audio.sfx.pistolShot.rolloffPower` | `1.3` |  |
| `audio.sfx.pistolShot.maxDistance` | `1500` |  |
| `audio.sfx.pistolShot.gain` | `0.9` |  |
| `audio.sfx.pistolShot.variants` | `2` |  |
| **`audio.sfx.rifleAction`** | *(group)* |  |
| `audio.sfx.rifleAction.path` | `"./sounds/rifle-action.mp3"` |  |
| `audio.sfx.rifleAction.refDistance` | `10` |  |
| `audio.sfx.rifleAction.rolloffPower` | `2.5` |  |
| `audio.sfx.rifleAction.maxDistance` | `300` |  |
| `audio.sfx.rifleAction.gain` | `0.6` |  |
| **`audio.sfx.rifleShot`** | *(group)* |  |
| `audio.sfx.rifleShot.path` | `"./sounds/rifle-shot.mp3"` |  |
| `audio.sfx.rifleShot.refDistance` | `50` |  |
| `audio.sfx.rifleShot.rolloffPower` | `1.3` |  |
| `audio.sfx.rifleShot.maxDistance` | `2200` |  |
| `audio.sfx.rifleShot.gain` | `1` |  |
| `audio.sfx.rifleShot.variants` | `2` |  |
| **`audio.sfx.thunder`** | *(group)* |  |
| `audio.sfx.thunder.path` | `"./sounds/thunder.mp3"` |  |
| `audio.sfx.thunder.refDistance` | `45` |  |
| `audio.sfx.thunder.rolloffPower` | `1.3` |  |
| `audio.sfx.thunder.maxDistance` | `1000000000` |  |
| `audio.sfx.thunder.gain` | `1` |  |
| `audio.sfx.thunder.variants` | `3` |  |
| `audio.sfx.thunder.duck` | `0.5` |  |
| **`audio.sfx.rainstorm`** | *(group)* |  |
| `audio.sfx.rainstorm.path` | `"./sounds/rainstorm.mp3"` |  |
| `audio.sfx.rainstorm.bed` | `true` |  |
| `audio.sfx.rainstorm.gain` | `0.7` |  |
| **`audio.sfx.rainRoofDrip`** | *(group)* |  |
| `audio.sfx.rainRoofDrip.path` | `"./sounds/rain-roof-drip.mp3"` |  |
| `audio.sfx.rainRoofDrip.refDistance` | `4` |  |
| `audio.sfx.rainRoofDrip.rolloffPower` | `2.5` |  |
| `audio.sfx.rainRoofDrip.maxDistance` | `40` |  |
| `audio.sfx.rainRoofDrip.loop` | `true` |  |
| `audio.sfx.rainRoofDrip.maxConcurrent` | `3` |  |
| `audio.sfx.rainRoofDrip.gain` | `0.4` |  |
| **`audio.sfx.rainRoofDrip.gate`** | *(group)* |  |
| `audio.sfx.rainRoofDrip.gate.wet` | `[0.05,1]` |  |
| `audio.sfx.rainRoofDrip.gate.storm` | `[0,0.3]` |  |
| **`audio.sfx.windWinter`** | *(group)* |  |
| `audio.sfx.windWinter.path` | `"./sounds/wind-winter.mp3"` |  |
| `audio.sfx.windWinter.bed` | `true` |  |
| `audio.sfx.windWinter.gain` | `0.5` |  |
| **`audio.sfx.windWinter.gate`** | *(group)* |  |
| `audio.sfx.windWinter.gate.snow` | `[0.4,1]` |  |
| **`audio.sfx.iceCracking`** | *(group)* |  |
| `audio.sfx.iceCracking.path` | `"./sounds/ice-cracking.mp3"` |  |
| `audio.sfx.iceCracking.refDistance` | `40` |  |
| `audio.sfx.iceCracking.rolloffPower` | `1.8` |  |
| `audio.sfx.iceCracking.maxDistance` | `900` |  |
| `audio.sfx.iceCracking.gain` | `0.6` |  |
| `audio.sfx.iceCracking.minGap` | `15` |  |
| `audio.sfx.iceCracking.variants` | `3` |  |
| `audio.sfx.iceCracking.every` | `[12,40]` |  |
| `audio.sfx.iceCracking.dist` | `[60,400]` |  |
| **`audio.sfx.iceCracking.gate`** | *(group)* |  |
| `audio.sfx.iceCracking.gate.ice` | `[0.4,1]` |  |
| `audio.sfx.iceCracking.gate.river` | `[0.15,1]` |  |
| **`audio.global`** | *(group)* | Global rules for the sfx hooks (wiring rules in the sound map) |
| `audio.global.maxOneShots` | `16` | simultaneous one-shot voices; extra ones are dropped |
| `audio.global.maxLoops` | `14` | simultaneous looping voices across all hooks (nearest/loudest win) |
| `audio.global.duckSeconds` | `1.5` | how long ambience stays ducked under a loud signal (a hook's `duck` = how far it dips, 0–1) |
| `audio.global.duckRecover` | `0.8` | seconds to swell back |
| `audio.global.siteRadius` | `450` | sites (places) farther than this from the camera are ignored |
| `audio.global.tickSeconds` | `0.1` | how often mob/site hooks are gathered |
| **`audio.vehicleEras`** | *(group)* | Motor vehicles: which loop plays for an auto by year (first row containing the year wins). busShare = share of autos (from the bus year on) that sound like a diesel bus — there is no bus model yet, so 0. |
| `audio.vehicleEras.rows` | `(list of 3)` |  |
| `audio.vehicleEras.busFrom` | `1950` |  |
| `audio.vehicleEras.busShare` | `0` |  |
| `audio.vehicleEras.hornChance` | `0.08` | chance an auto honks when it turns at a junction near the camera (carHorn) |
| **`audio.train`** | *(group)* | Trains: idle ↔ running crossfade, whistle at departure/arrival, onboard bed near a moving train |
| `audio.train.fadeSeconds` | `2.5` |  |
| `audio.train.whistleOnDepart` | `0.7` |  |
| `audio.train.whistleOnArrive` | `0.5` |  |
| `audio.train.whistleRandomPerSec` | `0.004166666666666667` |  |
| `audio.train.onboardRadius` | `14` |  |
| `audio.train.onboardFade` | `22` |  |
| **`audio.footsteps`** | *(group)* | Walk-mode footsteps. Surface under the camera: board walks/docks → plank (until the planks go: sidewalks.businessEnd), later sidewalks → stone, roadway or yard → gravel; snow cover and mud override. metresPerStep: stride; the spri… |
| `audio.footsteps.metresPerStep` | `0.8` |  |
| `audio.footsteps.sprintMetresPerStep` | `1.1` |  |
| `audio.footsteps.snowAbove` | `0.45` |  |
| `audio.footsteps.mudAbove` | `0.4` |  |
| `audio.footsteps.offRoad` | `"footstepsGravel"` |  |
| `audio.footsteps.plankUntilYear` | `0x000780` |  |
| `audio.footsteps.sidewalkBand` | `[0.5,3.2]` |  |
| **`audio.mud`** | *(group)* | Mud: after rain (roadWet) or in the thaw months, when there's no snow cover |
| `audio.mud.thawMonths` | `[3,4]` |  |
| `audio.mud.thawLevel` | `0.7` |  |
| `audio.fireLoudFlames` | `0.5` | Fires: the big-flame loop plays above this flame strength; and the roof-fall crack (dockBreak) when a fire's shell collapses |
| **`audio.sites`** | *(group)* | Places that make sound. `match` is tested (case-insensitive) against a building's name, first kind to match wins; kind `home` = any unnamed building of homeArea m². loops = looping hooks (nearest maxConcurrent get voices; hook gat… |
| **`audio.sites.factory`** | *(group)* |  |
| `audio.sites.factory.match` | `"factory\|foundry\|manufactur\|brewery\|packing\|\\bworks\\b\|\\bmi…` |  |
| `audio.sites.factory.loops` | `["factoryAmbience"]` |  |
| **`audio.sites.factory.at`** | *(group)* |  |
| `audio.sites.factory.at.factoryWhistle` | `[7,12,17]` |  |
| **`audio.sites.sawmill`** | *(group)* |  |
| `audio.sites.sawmill.match` | `"saw ?mill\|lumber\|planing\|sash and door"` |  |
| `audio.sites.sawmill.loops` | `["lumberMill"]` |  |
| **`audio.sites.sawmill.random`** | *(group)* |  |
| `audio.sites.sawmill.random.woodChop` | `0.15` |  |
| **`audio.sites.blacksmith`** | *(group)* |  |
| `audio.sites.blacksmith.match` | `"blacksmith\|smithy\|\\bforge\\b\|farrier\|horseshoe"` |  |
| `audio.sites.blacksmith.loops` | `["blacksmithForge"]` |  |
| **`audio.sites.blacksmith.random`** | *(group)* |  |
| `audio.sites.blacksmith.random.blacksmithAnvil` | `0.25` |  |
| `audio.sites.blacksmith.random.blacksmithQuench` | `0.015` |  |
| **`audio.sites.tinsmith`** | *(group)* |  |
| `audio.sites.tinsmith.match` | `"tinsmith\|tinner\|sheet metal\|plumb"` |  |
| **`audio.sites.tinsmith.random`** | *(group)* |  |
| `audio.sites.tinsmith.random.tinsmith` | `0.15` |  |
| **`audio.sites.print`** | *(group)* |  |
| `audio.sites.print.match` | `"printing\|printer\|press\\b\|newspaper\|tribune\|telegram\|free pr…` |  |
| `audio.sites.print.loops` | `["printingPress"]` |  |
| **`audio.sites.print.random`** | *(group)* |  |
| `audio.sites.print.random.typewriterTyping` | `0.08` |  |
| `audio.sites.print.random.typewriterBell` | `0.02` |  |
| **`audio.sites.depot`** | *(group)* |  |
| `audio.sites.depot.match` | `"station\|depot\|telegraph\|c\\.? ?p\\.? ?r\\.?\\b"` |  |
| **`audio.sites.depot.random`** | *(group)* |  |
| `audio.sites.depot.random.telegraphKey` | `0.1` |  |
| **`audio.sites.saloon`** | *(group)* |  |
| `audio.sites.saloon.match` | `"saloon\|hotel\|tavern\|\\bbar\\b\|\\bpub\\b\|brewery tap\|beer"` |  |
| `audio.sites.saloon.loops` | `["barAmbience","saloonPiano"]` |  |
| **`audio.sites.saloon.random`** | *(group)* |  |
| `audio.sites.saloon.random.barGlassClink` | `0.12` |  |
| `audio.sites.saloon.random.dishesBreak` | `0.003` |  |
| **`audio.sites.shop`** | *(group)* |  |
| `audio.sites.shop.match` | `"store\|shop\|grocer\|bakery\|butcher\|market\|emporium\|merchant\|…` |  |
| **`audio.sites.shop.random`** | *(group)* |  |
| `audio.sites.shop.random.cashRegister` | `0.04` |  |
| **`audio.sites.church`** | *(group)* |  |
| `audio.sites.church.match` | `"church\|cathedral\|chapel\|presbyterian\|methodist\|baptist\|angli…` |  |
| **`audio.sites.church.random`** | *(group)* |  |
| `audio.sites.church.random.churchBell` | `0.03` |  |
| **`audio.sites.school`** | *(group)* |  |
| `audio.sites.school.match` | `"school\|college\|academy\|collegiate\|university"` |  |
| `audio.sites.school.loops` | `(list of 1)` |  |
| **`audio.sites.school.at`** | *(group)* |  |
| `audio.sites.school.at.schoolBell` | `[8.75,10.25,10.5,12,13,15.25]` |  |
| **`audio.sites.livery`** | *(group)* |  |
| `audio.sites.livery.match` | `"livery\|stable\|\\bbarn\\b\|feed\|horse"` |  |
| **`audio.sites.livery.random`** | *(group)* |  |
| `audio.sites.livery.random.horseWhinny` | `0.01` |  |
| `audio.sites.livery.random.dogsBarking` | `0.01` |  |
| **`audio.sites.farm`** | *(group)* |  |
| `audio.sites.farm.match` | `"farm\|ranch\|dairy"` |  |
| `audio.sites.farm.loops` | `["cattleHerd"]` |  |
| **`audio.sites.farm.random`** | *(group)* |  |
| `audio.sites.farm.random.cattleMoo` | `0.03` |  |
| `audio.sites.farm.random.chickens` | `0.05` |  |
| `audio.sites.farm.random.dogsBarking` | `0.02` |  |
| `audio.sites.farm.random.wellPump` | `0.02` |  |
| `audio.sites.farm.random.gateCreak` | `0.01` |  |
| `audio.sites.farm.random.horseWhinny` | `0.01` |  |
| `audio.sites.farm.random.roosterCrow` | `0.01` |  |
| **`audio.sites.home`** | *(group)* |  |
| `audio.sites.home.match` | `null` |  |
| `audio.sites.home.homeArea` | `[30,300]` |  |
| `audio.sites.home.homeMaxFloors` | `3` |  |
| `audio.sites.home.loops` | `(list of 6)` |  |
| **`audio.sites.home.random`** | *(group)* |  |
| `audio.sites.home.random.cookingChop` | `0.1` |  |
| **`audio.extraSites`** | *(group)* | Fixed places not in the building data (farm = the two windmill sites, from CONFIG.windmills.list) |
| **`audio.extraSites.windmills`** | *(group)* |  |
| `audio.extraSites.windmills.kind` | `"farm"` |  |
| `audio.extraSites.windmills.loops` | `["windmill"]` |  |
| **`audio.ambient`** | *(group)* |  |
| **`audio.ambient.windNoise`** | *(group)* |  |
| `audio.ambient.windNoise.lowpassFrequencyHz` | `280` |  |
| `audio.ambient.windNoise.lowpassQ` | `0.6` |  |
| `audio.ambient.windNoise.gain` | `0` | general ambience MUTED for now (was 0.09) — to return once it's better and has better assets; storms still swell it (weather.windGain) |

## mobile

churchBell: { toneFrequenciesHz: [220, 330, 440, 550], gainPerTone: 0.04, // amplitude of the loudest (first) tone; others scale down decaySeconds: 4, repeatMinMs: 20000, repeatMaxMs: 40000, startDelayMinMs: 6000, startDelayMaxMs:…

| Key | Default | Notes |
|---|---|---|
| **`mobile.sidewalks`** | *(group)* |  |
| `mobile.sidewalks.concreteEverywhere` | `false` |  |
| **`mobile.mosquitoes`** | *(group)* |  |
| `mobile.mosquitoes.perAnchor` | `24` |  |
| `mobile.mosquitoes.maxAnchors` | `1200` |  |
| **`mobile.mosquitoes.cloud`** | *(group)* |  |
| `mobile.mosquitoes.cloud.puffs` | `3` |  |
| `mobile.mosquitoes.cloud.size` | `4.5` |  |
| `mobile.mosquitoes.cloud.opacity` | `0.2` |  |
| `mobile.mosquitoes.cloud.maxPx` | `100` |  |
| `mobile.mosquitoes.cloud.fade` | `[40,200]` |  |
| `mobile.mosquitoes.cloud.color` | `0x1A1816` |  |
| **`mobile.earlyVegetation`** | *(group)* |  |
| `mobile.earlyVegetation.density` | `0.4` | fewer trees in the early stands |
| **`mobile.signs`** | *(group)* |  |
| `mobile.signs.radiusM` | `45` |  |
| `mobile.signs.max` | `120` |  |
| `mobile.signs.atlasPx` | `[1024,512]` |  |
| **`mobile.terrain`** | *(group)* |  |
| `mobile.terrain.segments` | `300` | 40 m grid (DEM is resampled) |
| **`mobile.building`** | *(group)* | Only buildings within 3 km. Small details and real window glass only near the camera: meshes are uploaded to the GPU the first time they're visible, so far tiles never use GPU memory (painted windows cover the distance). Phones sh… |
| `mobile.building.loadRadius` | `3000` |  |
| `mobile.building.detailDistance` | `600` |  |
| **`mobile.building.roofCap`** | *(group)* |  |
| `mobile.building.roofCap.bigDistance` | `2500` |  |
| **`mobile.glass`** | *(group)* |  |
| `mobile.glass.maxDistance` | `700` |  |
| `mobile.glass.maxPanes` | `45000` |  |
| **`mobile.camera`** | *(group)* |  |
| `mobile.camera.pixelRatioCap` | `1.25` |  |
| **`mobile.lighting`** | *(group)* |  |
| **`mobile.lighting.sun`** | *(group)* |  |
| `mobile.lighting.sun.shadowMapSize` | `1024` |  |
| **`mobile.trees`** | *(group)* |  |
| `mobile.trees.spacing` | `14` |  |
| **`mobile.seasons`** | *(group)* |  |
| `mobile.seasons.floeCount` | `450` |  |
| **`mobile.streetLights`** | *(group)* |  |
| `mobile.streetLights.spacing` | `70` |  |
| `mobile.streetLights.radius` | `1800` |  |
| **`mobile.trains`** | *(group)* |  |
| `mobile.trains.maxCars` | `25` |  |
| **`mobile.autos`** | *(group)* |  |
| `mobile.autos.max` | `50` |  |
| `mobile.autos.scale` | `0.4` |  |

## minimap

Minimap

| Key | Default | Notes |
|---|---|---|
| `minimap.canvasSizePx` | `200` |  |
| `minimap.worldRangeMetres` | `2500` |  |
| `minimap.backgroundColor` | `"rgba(14,12,10,0.92)"` |  |
| `minimap.borderColor` | `"#2a1e0e"` |  |
| `minimap.headingColor` | `"#FFD080"` |  |
| `minimap.riverColor` | `"#2B4A5C"` | muted river blue (static — doesn't follow the flood level) |
| `minimap.drawOrder` | `(list of 8)` | Dot draw order, bottom → top (dots overlap at this scale; unlisted draw first) |
| **`minimap.materialColors`** | *(group)* | Building dots in Goad's fire-insurance atlas colours (others: their material colour) |
| `minimap.materialColors.wood` | `"#E8CF5A"` | frame — yellow |
| `minimap.materialColors.log` | `"#E8CF5A"` |  |
| `minimap.materialColors.lumber` | `"#E8CF5A"` |  |
| `minimap.materialColors.brick` | `"#E89AA4"` | brick — pink |
| `minimap.materialColors.brick_veneer` | `"#E89AA4"` |  |
| `minimap.materialColors.stone` | `"#9CC9E4"` | stone — light blue |
| `minimap.materialColors.wood_industrial` | `"#A6A6A6"` | industrial frame — grey |
| `minimap.materialColors.iron` | `"#7E8286"` | iron-clad — darker grey |
| `minimap.crosshairColor` | `"#3a2a10"` |  |

## fpsControls

FPS / walk-mode controls

| Key | Default | Notes |
|---|---|---|
| `fpsControls.mouseLookSensitivity` | `0.0016` |  |
| `fpsControls.touchLookSensitivity` | `0.004` |  |
| `fpsControls.pinchMetresPerPx` | `0.12` | walk mode: metres moved along the view direction per pixel of pinch/spread |
| `fpsControls.pitchClampRadians` | `1.48` |  |
| `fpsControls.minCameraY` | `1` |  |

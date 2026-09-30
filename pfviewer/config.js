// ═══════════════════════════════════════════════════════════════════════
// PastForward 3D — CONFIG
//
// Every value a non-coder is likely to want to tweak lives in this file.
// index.html imports this as `CONFIG` and reads from it at startup — you
// do NOT need to touch index.html to change a colour, a sound volume, a
// fog density, how many streetcars run, etc. Just edit a number or a hex
// colour below, save, and reload the page in your browser.
//
// Colours are written as 0xRRGGBB (hex). If you're not familiar with hex
// colour codes, any "colour picker" website (search "hex color picker")
// will let you click a colour and copy the code — just keep the 0x prefix
// already on each line and replace the 6 digits after it.
//
// This file must be served over a local web server (the same way you
// already run index.html) — opening it directly as a file:// URL will not
// work, the same restriction that already applies to index.html.
// ═══════════════════════════════════════════════════════════════════════

export const CONFIG = {

  // ── Data files ──────────────────────────────────────────────────────
  // GeoJSON layers loaded automatically on startup. Add/remove/rename
  // entries to change what loads — paths are relative to index.html.
  dataFiles: {
    autoload: [
      './data/pastforward_2026_assessment.geojson',  // growth master + assessment/heritage dates (matching/merge_assessment.py) — no OSM data
      './data/pastforward_2026_osm.geojson',         // new pre-1907 buildings with OSM footprints — ODbL, kept as a separate database
      // './data/pastforward_2026.geojson',  // dated growth master without assessment data (no OSM) — swap back by un-commenting
      './data/wpg_rivers.geojson',
      './data/wpg_roads_streetcar.geojson',
      './data/wpg_rails_1906.geojson',
    ],
    // Snapshot layers NOT loaded at start (memory — phones lose the WebGL
    // context). Offered as "+ 1880" / "+ 1906" in the advanced (Ctrl+A) layer bar.
    optionalLayers: [
      { label: '1880', file: './data/mcphillips_1880.geojson' },   // ground-truth "as digitized" 1880 view
      { label: '1906', file: './data/goad_1906.geojson' },         // ground-truth "as digitized" 1906 view
    ],
    facadeConfig: './data/facades.json',
    // Per-building phase overrides (storey additions, fires…) keyed by uid — see applyBuildingHistory
    buildingHistory: './data/building_history.json',
    facadeImageDir: './images/',
    // Building-material stems that get an auto-loaded bump/texture map
    // (looked for at `./data/bump_<stem>.png`).
    bumpMapStems: ['brick', 'wood', 'stone', 'log', 'iron', 'concrete', 'lumber'],
  },

  // ── Start behaviour ─────────────────────────────────────────────────
  start: {
    // Time of day at load, 0..1 spans 04:00–22:00 (0.42 ≈ 11:34am).
    timeOfDay: 0.42,
    // Start in winter (snow) mode?
    winterMode: false,
    layer: 'pastforward',   // layer shown on load: 'pastforward' | '1906' | '1880' | 'all' | 'combined' (falls back if not loaded)
    // Initial camera position and look-at target, in world metres.
    // (World X=east, Y=up, Z=south — see coordinate-system note in index.html.)
    cameraPosition: { x: 600, y: 450, z: 900 },
    cameraLookAt:   { x: 0,   y: 0,   z: 0 },
  },

  // ── Building material colours ──────────────────────────────────────
  // Base colour + specular "shininess" (0=matte, 100=very glossy) per
  // material type. `label` is what's shown in the on-screen legend.
  materials: {
    brick:           { color: 0xC0604A, label: 'Brick',            shininess: 20 },
    brick_veneer:    { color: 0xC07858, label: 'Brick Veneer',     shininess: 18 },
    wood:            { color: 0xCFA840, label: 'Wood / Frame',     shininess: 6  },
    wood_industrial: { color: 0x687888, label: 'Wood / Industrial',shininess: 8  },
    iron:            { color: 0x687888, label: 'Iron / Metal',     shininess: 45 },
    stone:           { color: 0xE8DFC8, label: 'Stone',            shininess: 55 },
    blue:            { color: 0x3A6898, label: 'Railway Siding',   shininess: 35 },
    concrete:        { color: 0x989890, label: 'Concrete',         shininess: 18 },
    unknown:         { color: 0x808078, label: 'Unknown',          shininess: 5  },
    log:             { color: 0x807040, label: 'Log',              shininess: 4  },
    lumber:          { color: 0xC0A040, label: 'Stacked Lumber',   shininess: 6  },
  },

  // Per-material colour *palettes* — small random variation pools so not
  // every brick building is the exact same red. Each entry is [base, alt]
  // or a [min,max] range depending on material; see index.html comments
  // near "BRICK_PALETTES" etc. if you want to understand how these are
  // consumed. Safe to add/remove/edit entries.
  palettes: {
    // Named wall colours a building can be given by hand with a `wall_color`
    // property (in data/building_history.json → `set`). A building's
    // wall_color may also be a hex string like "#A0452E".
    named: {
      darkRed:   0xA03828,
      red:       0xB84A34,
      orangeRed: 0xC86444,
      buff:      0xCCA848,   // yellow/buff brick
      cream:     0xD8C890,   // pale cream brick
      tyndall:   0xD2C49A,   // Tyndall limestone
      sandstone: 0x9C5A40,   // red sandstone
      grey:      0x8C8880,   // grey stone / painted brick
      slate:     0x4A5058,   // slate roofing (default for dome/bell/conical roofs)
      copper:    0x5E9C86,   // weathered (verdigris) copper
      newCopper: 0xB0683C,   // fresh copper
    },
    // Each [lo,hi] pair is a colour range a building of this material is
    // randomly lerped within. `weights` are cumulative percentages (must
    // end at 100) controlling how common each pair is — e.g. brick's first
    // entry (dark red) is picked for the first 35% of buildings.
    brick: {
      pairs: [
        [0x9A3020, 0xC05838],  // dark red
        [0xB84030, 0xCC5840],  // mid red
        [0xC86040, 0xD87050],  // orange-red
        [0xC8A030, 0xD8B850],  // yellow/buff brick
        [0xD4C070, 0xE0CF90],  // pale limestone-yellow
      ],
      weights: [35, 60, 70, 90, 100],
    },
    woodComm: {
      pairs: [
        [0xC49A30, 0xD4AA40],  // ochre (most common Victorian exterior)
        [0x6A7A50, 0x7A8A60],  // sage green
        [0xCDC0A0, 0xDDD0B0],  // cream/buff
        [0x8B3020, 0xA04030],  // barn red
        [0x3A5A30, 0x4A6A40],  // dark green
        [0x8090A0, 0x909AB0],  // French grey (later fashion)
        [0xA89070, 0xBEA888],  // raw/weathered wood (small buildings)
      ],
      weights: [20, 35, 50, 60, 72, 82, 100],
    },
    ironIndustrial: {
      pairs: [
        [0x707870, 0x909890], [0x806858, 0x907060], [0xA07050, 0x985840], [0xD0D4D0, 0xE0E4E0],
      ],
      weights: [40, 65, 85, 100],
    },
    stone:    { min: 0xDDD0B0, max: 0xF0E8D0 },
    log:      { min: 0x80603A, max: 0x987858 },
    lumber:   { fresh: 0xC8A840, aged: 0xA09070 },
    concrete: { min: 0x888880, max: 0xA0A098 },
    unknown:  { min: 0x787068, max: 0x908880 },
  },

  // ── Sky / scene colours & atmosphere ───────────────────────────────
  scene: {
    // Registration offset for building/road data relative to river GeoJSON + LiDAR DEM.
    // Positive offsetX = shift buildings east (metres); positive offsetZ = shift south.
    // Set to 0 to establish baseline — adjust once misalignment is measured.
    buildingOffsetX:   0,
    buildingOffsetZ:   0,
    // DEM terrain offset — shifts the terrain mesh in world space (no reprocessing needed).
    // Positive terrainOffsetZ = shift terrain south; negative = shift north.
    terrainOffsetX:    0,
    terrainOffsetZ:  -5,
    // DEM terrain rotation — rotates the terrain mesh around a geographic pivot.
    // terrainRotationDeg: clockwise-positive degrees around world Y axis.  0 = no rotation.
    // Pivot is the tip of land at The Forks (west of the Red, south of the Assiniboine).
    // Adjust lon/lat to move the fixed point; adjust deg to dial in alignment.
    terrainRotationDeg:         1.5,
    terrainRotationPivotLon:   -97.1283,
    terrainRotationPivotLat:    49.8843,
    backgroundColor: 0x8AB8D0,
    fog: {
      color: 0x8AB8D0,
      // Exponential fog density — higher = haze sets in closer to camera.
      // Try 0.0001 (very clear, see for miles) to 0.0008 (thick haze).
      density: 0.00032,
    },
    ground: {
      summerColor: 0x2D4A1A,
      winterColor: 0xF5F6FA,
    },
    // Reference grid lines drawn over the ground.
    grid: {
      colorCenterLine: 0x3A5A22, colorGrid: 0x324A1C,
      summerTint: 0x3A5A22, summerOpacity: 0.18,
      winterTint: 0xC8C8D8, winterOpacity: 0.12,
    },
    // Road vertex-colour gradient: edge = dry/snowy shoulder, centre = wet/mud
    // wheel-rut tracks. Each is an [r,g,b] byte triple (0-255).
    roadFade: [1800, 3200],  // metres from camera: roads full → gone (only the most distant roads alias and z-fight)
    roadColors: {
      summerEdge: [18, 17, 15], summerCentre: [5, 5, 4],
      winterEdge: [245, 246, 250], winterCentre: [32, 28, 24],
    },
  },

  // Time-of-day keyframes the sky/fog/sun smoothly blend between.
  // Each entry: [day phase (0..1: sunrise ≈ 0.10, sunset ≈ 0.90 — stretched to
  //              the date's real sunrise/sunset, see lighting.solarNoonClock),
  //              skyColor, fogColor, sunColor, sunIntensity, ambientIntensity]
  skyKeyframes: [
    [0.00, 0x0A0510, 0x0A0510, 0xFF6020, 0.00, 0.04], // pre-dawn
    [0.10, 0xFF7030, 0xE85010, 0xFF9040, 0.50, 0.08], // early sunrise
    [0.18, 0xF0A060, 0xD08040, 0xFFD080, 1.00, 0.14], // sunrise
    [0.28, 0x88C0E8, 0x88C0E8, 0xFFF0D0, 1.35, 0.18], // early morning
    [0.42, 0x7AB8E0, 0x7AB8E0, 0xFFF4DC, 1.45, 0.20], // mid-morning
    [0.52, 0x6AAED8, 0x6AAED8, 0xFFFAF0, 1.50, 0.22], // late morning / noon
    [0.70, 0x88B0D8, 0x88B0D8, 0xFFF0C0, 1.30, 0.18], // afternoon
    [0.82, 0xF08030, 0xD06020, 0xFF8030, 0.90, 0.12], // sunset
    [0.90, 0xC04020, 0x902010, 0xFF5010, 0.40, 0.06], // late sunset
    [1.00, 0x080310, 0x080310, 0xFF3000, 0.00, 0.03], // night
  ],

  lighting: {
    // Sun follows the real clock: solar noon in local standard time (CST) at
    // Winnipeg's longitude, 97.14°W → 12:00 + 7.14°×4 min ≈ 12:29. Sky
    // keyframes above are stretched to each date's actual sunrise→sunset,
    // with twilightHours of dusk/dawn either side.
    solarNoonClock: 12.48,
    twilightHours: 1.5,
    hemisphere: { skyColor: 0x88C0E8, groundColor: 0x3A5A20, intensity: 0.55 },
    ambient:    { color: 0xffffff, intensity: 0.12 },
    sun: {
      color: 0xFFF4DC,
      intensity: 1.3,
      shadowMapSize: 2048,     // higher = sharper shadows, slower to render
      shadowNear: 10, shadowFar: 2200,
      shadowBounds: { left: -900, right: 900, top: 900, bottom: -900 },
      shadowBias: -0.0003,
    },
  },

  camera: {
    fov: 68,
    near: 0.5,
    far: 30000,
    pixelRatioCap: 2,    // caps device pixel ratio for perf on hi-DPI screens
    homeAltitude: 1500,  // metres above ground for H key top-down overview
  },

  orbitControls: {
    dampingFactor: 0.07,
    maxPolarAngle: 0.98,   // × Math.PI — 1.0 would let you flip under the ground
    minDistance: 2,
    maxDistance: 3000,
    dollyIn: 0.94,         // zoom-in factor per scroll/tap
  },

  // ── Window/glass "shader" look ─────────────────────────────────────
  // The window-glass material — this is the closest thing to a shader
  // effect in this renderer (a tinted, glossy, semi-transparent surface).
  glass: {
    color: 0x283038,   // opaque now (was 0x1A2530 at 72% opacity over the wall) — a touch lighter to compensate
    shininess: 90,
    specular: 0x4868A0,
    tileMetres: 400,      // windows are grouped in map tiles of this size…
    maxDistance: 1800,    // …and tiles farther than this from the camera are hidden
    // Warm amber glow added to glass at night, scaled by darkness (0..1).
    nightGlowColor: { r: 0.47, g: 0.19, b: 0.02 },
  },

  // ── Procedural window dimensions/density ───────────────────────────
  windows: {
    width: 1.00,           // standard window width (m)
    height: 1.75,          // standard window height (m)
    sillHeight: 0.90,      // sill height above floor (m)
    gap: 0.90,             // horizontal gap between windows (m) — smaller = denser
    margin: 0.70,          // margin kept clear at wall ends (m)
    inset: 0.06,           // how far glass sits back from the wall face (m)
    groundFloorWidth: 1.50,       // wider ground-floor "shopfront" windows
    groundFloorHeightFrac: 0.78,  // ground floor window height, as a fraction of floor height
    // A half-floor fraction at/above this is treated as a full floor of
    // windows (e.g. floors=2.93 gets windows like floors=3). Below this,
    // the partial floor gets dormers (or nothing) instead of overrun windows.
    halfFloorRoundUpThreshold: 0.9,
  },

  // ── Dormers (added to peaked-roof buildings with a half-storey) ────
  dormers: {
    width: 1.5,        // dormer footprint width along the wall (m)
    depth: 0.55,        // dormer footprint depth, front-to-back (m)
    wallHeight: 1.15,   // dormer wall height below its own little roof (m)
    roofHeight: 0.55,   // dormer roof peak height above its wall (m)
    embed: 0.15,        // how far the dormer sits back into the main wall/roof mass
    windowWidth: 0.80,
    windowHeight: 0.85,
    windowSill: 0.15,
    maxPerBuilding: 3,         // cap on dormers per qualifying wall
    spacingMetres: 6,          // ~1 dormer per this many metres of wall
    minFloorsForDormer: 0,     // floors must be > this to qualify
    maxFloorsForDormer: 2.5,   // floors must be <= this to qualify (low-rise only)
  },

  // ── Building heights & roads ───────────────────────────────────────
  building: {
    tileMetres: 1000,      // building meshes are merged per map tile (culling; shadow pass only draws nearby tiles)
    deferFuture: true,     // PastForward buildings are built only once the clock nears their construction start (false = all at launch)
    detailDistance: 1500,  // parapets, roof caps, chimneys hidden beyond this (m)
    // Feature properties kept in memory after load (everything else in the
    // data files is dropped at load — add a name here if new code needs it)
    keepProps: ['id','uid','pf_uid','name','address','material','floors','type','roof_type','area_m2',
                'born','died','born_basis','died_basis','died_by','died_cause','cause_of_death','replaced_by',
                'base_floors','parapet','construction_months','no_windows','source_file','group','cohort',
                'heritage_name','heritage_date','heritage_url','footprint_source','osm_id',
                'st_name','st_type','streetcar_start','rail_class','wall_color','wall_stripes',
                'roof_height','roof_color'],
    floorHeight: 4.2,    // metres per floor (Victorian commercial average)
    platformHeight: 0.6, // low platform/loading-dock structures
    minHeight: 2.0,
    eyeHeight: 1.75,     // walk-mode eye level
    parapet: { width: 0.38, height: 0.50, stoneWidth: 0.55, stoneHeight: 0.80 },
    // Specular highlight colour for wall materials (how glossy/shiny under
    // direct light) — most walls use `default`, iron-clad walls are shinier.
    wallSpecular: { default: 0x1a1a1a, iron: 0x303838 },
    roofSpecular: 0x080808,
    // Flat tar-paper roof caps (most common roof type) and stone parapet caps.
    roofCap: {
      tarPaperColor: 0x38342E, tarPaperWinterColor: 0xF5F6FA,
      stoneColor: 0x505050,
      bigAreaM2: 400,      // roofs this big (m², inside the parapet ring) count as "big"…
      bigDistance: 5000,   // …and their gravel caps stay visible this far (others: detailDistance)
    },
    // Specular for the upright parapet wall above brick/stone buildings.
    parapetSpecular: { brick: 0x1a1a1a, stone: 0xC8B890 },
    // Shared specular for fence meshes and exposed-lumber stacked-wood walls.
    fenceSpecular: 0x111111,
    // UV tiling repeat [u,v] for wall bump/texture maps, per material —
    // how many times the bump image tiles per metre of wall.
    bumpRepeat: {
      brick: [4, 13], stone: [1.5, 1.5], wood: [1, 5], log: [0.8, 3],
      iron: [2, 2], concrete: [1, 1], unknown: [2, 2], lumber: [0.3, 0.66],
    },
  },

  // ── Building-front facade images (photo overlays + bump maps) ───────
  facade: {
    panelSpecular: 0x222222,   // specular on the photo-textured facade panel
    bumpSpecular: 0x444444,    // specular once a normal/bump map is applied
  },
  roadWidths: { // metres, by street-type suffix
    BLVD: 18, HWY: 16, AVE: 12, ST: 10, RD: 10, DR: 10,
    CRES: 9, WAY: 9, ROW: 8, LANE: 6, PL: 9, BAY: 9, PATH: 5, TRAIL: 5,
  },

  // ── Fences ──────────────────────────────────────────────────────────
  fences: {
    // White picket — used for wood fences and the (residential) unknown-material
    // ones. Gap between pickets = width * gapRatio. Height is fixed (the
    // feature's floors value is ignored) — these are ~1 m garden fences.
    picket: {
      color: 0xEEEEE0, width: 0.09, gapRatio: 0.5, thickness: 0.022, height: 1.0,
      postSpacing: 2.4, postSize: 0.1, railHeights: [0.22, 0.72], railSize: [0.04, 0.08],
      whitenessJitter: 0.06,   // per-fence brightness variation (weathered paint)
    },
    iron:   { postColor: 0x554433, railColor: 0x665544 },
    log:    { postColor: 0x7A5C3A, railColor: 0x8A6845, postSpacing: 2.0, leanRadians: 0.30 },
  },

  // ── Chimneys & building smoke ────────────────────────────────────
  // Procedural brick/iron chimney stacks with animated coal-smoke puffs.
  // All distances in world metres (Up≠N: X=east, Y=up, Z=south).
  chimneys: {
    // Per-material chimney stack geometry.
    // count: [min,max] shafts placed (max used only for large/tall buildings).
    // radius: [bottomR, topR] in metres.
    // height: [minH, maxH] shaft height in metres (scales with building floors).
    // color: shaft vertex colour.
    // type: 'light'=coal/wood smoke (grey-white), 'dark'=heavy industrial (dark grey).
    materials: {
      brick:           { count:[1,2], radius:[0.22,0.30], height:[1.8,3.5], color:0x3A1A0A, type:'light' },
      brick_veneer:    { count:[1,2], radius:[0.20,0.28], height:[1.5,3.0], color:0x3A1A0A, type:'light' },
      stone:           { count:[1,2], radius:[0.28,0.38], height:[2.0,4.5], color:0x504030, type:'light' },
      wood:            { count:[1,1], radius:[0.15,0.22], height:[1.0,2.0], color:0x3A2010, type:'light' },
      iron:            { count:[1,2], radius:[0.40,0.55], height:[3.5,7.0], color:0x1C1C1C, type:'dark'  },
      wood_industrial: { count:[1,2], radius:[0.30,0.45], height:[2.5,5.5], color:0x252018, type:'dark'  },
      concrete:        { count:[0,1], radius:[0.25,0.35], height:[2.0,4.0], color:0x383830, type:'light' },
      unknown:         { count:[0,1], radius:[0.18,0.25], height:[1.2,2.5], color:0x302820, type:'light' },
      log:             { count:[1,1], radius:[0.14,0.18], height:[0.8,1.5], color:0x382810, type:'light' },
    },
    // Minimum floors before a chimney is placed.
    minFloors: 0.5,
    // Offset chimneys from building centroid by up to this fraction of √(area_m2).
    placementRadius: 0.22,
    // Shared sprite pool — hard cap on simultaneous smoke sprites city-wide.
    smokePoolSize: 360,
    // Smoke behaviour per type. Ranges are [min,max]; values are randomised per puff.
    // rateBase: seconds between puffs — lower = faster, more overlap, less cartoon-puff look.
    // scaleStart close to scaleEnd means puffs are born large and blend into the column.
    smoke: {
      light: { opacityRange:[0.14,0.28], scaleStart:2.2, scaleEnd:5.5, life:[3.5,6.5], riseSpeed:[1.6,2.8], drift:0.40, rateBase:[0.30,0.65] },
      dark:  { opacityRange:[0.28,0.48], scaleStart:2.8, scaleEnd:7.5, life:[4.0,8.0], riseSpeed:[1.0,2.0], drift:0.50, rateBase:[0.18,0.40] },
    },
    // Time-of-day activity curve — multiplier on smoke emission rate.
    // [hour_24h, multiplier] pairs linearly interpolated.
    todCurve: [
      [4,  0.35],  // pre-dawn: fires banked overnight
      [6,  1.40],  // morning stoke: coal shovelled, stoves lit
      [9,  0.95],  // daytime: steady industrial + commercial
      [17, 1.20],  // evening: suppers cooking, domestic heating
      [20, 0.40],  // late evening: fires banked
      [22, 0.25],  // night
    ],
    winterMultiplier: 1.80,   // heating load roughly doubles smoke in winter
    summerMultiplier: 0.70,   // hot months — industrial/cooking only
    // LOD. Per-chimney puffs come from the nearest in-view chimneys within
    // farDist (3D metres from the camera); the count tapers from
    // maxNearEmitters as the camera climbs from nearDist to farDist above
    // the ground. The city haze layers cover everything beyond.
    nearDist: 150,
    farDist:  900,
    maxNearEmitters: 50,
    // City-wide coal/wood smoke haze — a few stacked horizontal shader layers
    // over the whole city (see buildCityHaze in index.html). Intensity comes
    // from a source map: building footprint coverage within `radius`, per
    // year from born dates (so no smoke before the city exists), plus rail
    // sidings (yards) from rail.minVisibleYear. Each fragment looks `reach`
    // metres upwind, so smoke streams downwind of dense areas; wind-advected
    // noise breaks it into drifting wisps. Scaled by the chimney
    // time-of-day × heating multiplier. Fades out near the camera.
    cityHaze: {
      wind: [1, 0],          // direction smoke travels, world XZ (+X = east): west → east
      windSpeed: 14,         // m/s the wisps drift (faster than real so it reads as motion)
      evolve: 0.025,         // how fast wisps change shape as they travel
      radius: 100,           // metres — neighbourhood for source coverage
      thresholds: [0.03, 0.08, 0.16, 0.30],   // coverage fractions → 4 intensity steps
      yardWeight: 45,        // m² of "building" per metre of siding track (locomotive smoke)
      texelMetres: 20,
      layers: [              // height (m), opacity scale, upwind reach (m)
        { y: 16, opacity: 1.0,  reach: 350, speed: 0.8 },   // speed: × windSpeed — upper layers faster (parallax)
        { y: 30, opacity: 0.75, reach: 600, speed: 1.1 },
        { y: 48, opacity: 0.5,  reach: 950, speed: 1.5 },
      ],
      strength: 3,         // overall opacity at full density & multiplier 1
      maxAlpha: 0.65,
      color: 0x57534B,       // sooty warm grey — the shaded underside, seen from below against the sky
      colorAbove: 0x8A7F6C,  // seen from above over bare ground: brownish coal smoke, lighter than the dark roofs
      colorAboveSnow: 0x3E3830,   // seen from above over snow: dark soot (blended by the season's snow cover)
      aboveBoost: 0.15,       // opacity multiplier when seen from above (<1: looking down through all layers stacks up fast)
      fadeYears: 3,          // a source ramps up over this many years after its buildings appear
      nearFade: [40, 220],   // metres from camera: transparent → full
    },
  },

  // ── Terrain ─────────────────────────────────────────────────────────
  // Subdivided ground mesh with gentle prairie noise + river channel deformation.
  // After water GeoJSON loads, terrain vertices near river paths are depressed
  // so the flood plane (water) becomes visible in the channel at low water levels.
  terrain: {
    segments: 600,          // mesh subdivisions (20 m grid; the 1201² DEM is resampled) — was 1200, ~2.2M triangles more
    // DEM smoothing at load: removes modern street/lot relief (the "waffle" the
    // dirt line traced) while keeping riverbanks — see smoothDEM in index.html
    smooth: { radiusM: 30, keepBelowM: 0.5, keepAboveM: 1.5 },
    noiseAmplitude: 0.80,   // metres of prairie undulation — enough for interesting flood spread
    noiseBaseY: 0.0,        // baseline Y for terrain surface (buildings sit at y=0)
    channelDepth: 5.5,      // metres the channel floor sits below bank level (y=0)
    channelBlendWidth: 160, // metres from river CENTERLINE to flat prairie (covers bank + slope)
    // Bare riverbank: terrain below (water.startY + aboveWater) fades from
    // grass to dirt over `blend` metres. Tied to the INITIAL water level, not
    // the flood slider. `jitter` wobbles the line so it isn't a contour ring.
    // Summer only — banks go to snow with the rest of the ground in winter.
    bankDirt: { color: 0x3F3427, aboveWater: 3.0, blend: 1.5, jitter: 0.4 },
    // Summer ground cover — breaks the flat green up (shader, no textures).
    // Base grass tone is scene.ground.summerColor; noise at a few scales mixes
    // in a second green, dry straw patches and brightness mottling. Around
    // buildings, a density map (footprint coverage within `radius`, per year
    // using born dates) fades grass to trampled yard dirt, then bare packed
    // mud/cinder in the dense core. Off in winter.
    groundCover: {
      grassAlt:  0x3A5220,   // second green mixed in at ~400 m patch scale
      grassDry:  0x6E6A3A,   // late-summer straw / dry prairie grass patches
      dryAmount: 0.55,       // 0 = no straw patches
      mottle:    0.22,       // ± brightness variation at ~15 m scale
      yardDirt:  0x544B33,   // trampled yards / lanes: patchy with grass
      coreDirt:  0x4E4538,   // packed mud, cinders, manure — dense downtown
      radius: 40,            // metres — neighbourhood for footprint coverage
      yardCoverage: 0.10,    // footprint fraction where yards start going to dirt
      coreCoverage: 0.35,    // footprint fraction treated as dense core
      fadeYears: 4,          // years for a spot to wear from grass to dirt
      texelMetres: 10,       // density-map resolution (capped at 1024 texels/side)
    },
  },

  // ── Water ───────────────────────────────────────────────────────────
  water: {
    color: 0x7A5230, specular: 0x3A2810,
    winterColor: 0xBBCCE8, winterSpecular: 0x8899CC,
    // Colour the water tints toward as the flood slider is dragged to its
    // maximum (muddier, browner) — lerped with `color` at slider value.
    floodPeakColor: 0x5A3A20,
    // baseY: the Y level of the flood plane at slider=0.
    // With real LiDAR DEM: Red River valley floor is ~3–5m below bank level.
    // Set low enough that the plane starts fully inside the channel at rest.
    baseY:  -10.0,   // flood plane Y at slider=0 (fully dry / below channel)
    startY:  -5.8,   // reference ("normal") river level, world Y — date levels below are relative to this
    // River level by date. levelAt(date) = historical record if one is near
    // the date, else the fake seasonal curve below; the flood slider adds a
    // manual offset on top. Everything that floats (boats, floes) follows.
    levels: {
      // Fake seasonal curve, metres relative to startY: low under the ice,
      // quick rise at break-up to the spring high, then a straight decline to
      // the lowest level just before freeze-up. ['MM-DD', metres].
      seasonal: [['04-14', -0.8], ['04-22', 2.5], ['11-25', -0.8]],
      yearVariation: 0.35,     // ± fraction on the spring rise, seeded by year (same year → same level)
      // Optional real data, loaded if present. Format:
      //   { "datum": "relative" | "asl" | "james_ft", "records": [["1913-04-28", 12.4], ...] }
      //   relative: metres vs startY · asl: metres above sea level (via the DEM's refElev)
      //   james_ft: feet on the James Avenue gauge (datum 727.57 ft ASL — verify before relying on it)
      historyFile: './data/water_levels.json',
      maxGapDays: 45,          // interpolate between records at most this far apart; else fall back to seasonal
    },
    // Assiniboine → Red confluence plume (faked in the water shader). The
    // lighter, siltier Assiniboine water hugs the Red's west bank heading
    // north and has mixed out by Esplanade Riel. Path is lon/lat (modern, like
    // the river data — offsetZ below is applied to it too), mouth → downstream.
    // Width/strength interpolate start → end along the path. Summer only.
    confluence: {
      path: [[-97.1292,49.8858],[-97.1277,49.8864],[-97.1266,49.8875],[-97.1263,49.8890],[-97.1267,49.8903],[-97.1274,49.8910]],
      widthStart: 60, widthEnd: 120,   // metres, full plume width
      edgeNoise: 18,                    // metres of wobble on the plume edge
      color: 0x8A6A45,                  // Assiniboine water — a touch lighter/tanner than the Red
      colorMix: 0.35,                   // how far toward `color` at full strength (subtle)
      specularMult: 1.8, shininessMult: 0.55,  // siltier water: broader, brighter sheen
      flowSpeed: 0.35,                  // m/s the edge noise drifts downstream
    },
    riverHalfWidth: 120, creekHalfWidth: 8,
    widths: { brownsCreek: 3, redRiver: 220, assiniboineRiver: 85, seineRiver: 22 },
    // Brown's Creek: a small clear prairie creek — no glacial silt, no Red River brown.
    // Dark teal-green reads as shallow moving water in a 3D scene.
    brownsCreekColor: 0x2E6058,
    floodMaxRiseMetres: 12.5, // historic 1826-flood-scale peak at slider=1.0 → water at +9.5m
    // Geographic registration offset applied to all river/water geometry.
    // The NHD river data (modern GPS) is slightly north of the Goad's Atlas
    // building data (historically georeferenced ~1906).  Positive values shift
    // water SOUTH (increasing worldZ); negative values shift it NORTH.
    // ~30 m southward corrects the observed ~100-foot northward misalignment.
    offsetZ: -30,
  },

  // ── Rail / tracks ───────────────────────────────────────────────────
  rail: {
    color: 0x4e5060, specular: 0x2c2c2c,                  // train (freight/passenger) rails
    streetcarRailColor: 0x222222, streetcarRailSpecular: 0x333333,
    // Streetcar rails — one mesh per route, bucketed by streetcar_start year:
    railHeadWidth: 0.12, railHeight: 0.22,
    // Freight/passenger train rails (slightly slimmer in this model):
    trainRailHeadWidth: 0.10, trainRailHeight: 0.20,
    gaugeHalfWidth: 0.7175,
    throughLineBedWidth: 4.0, sidingBedWidth: 2.4,
    // The freight/passenger rail network is hidden before this year on the
    // timeline. ~1881 = the CPR main line reaching Winnipeg (approximate — not
    // a hard historical date; adjust here). NOTE: the full 1906 network is
    // drawn from this year on, so early rail looks more developed than it
    // really was — per-segment build dates are a future refinement.
    minVisibleYear: 1881,
  },

  // ── Bridges (type:'bridge' features) ─────────────────────────────────
  // Rectangular bridge footprints with a long side ≥ minSpan are drawn as
  // open structures instead of solid slabs: a steel through-truss when the
  // span crosses water (ground under it dips below water.startY) and isn't
  // timber, otherwise a trestle (lattice railings + braced bents on
  // footings). Shorter ones (e.g. the little Ogilvie mill connectors) keep
  // the old slab. Roads/rails/vehicles heading along a bridge's span ride on
  // its deck (see bridgeDeckY in index.html).
  bridges: {
    truss: {
      maxSpan: 60,          // metres between stone piers
      pierThickness: 3,
      panelLength: 7,       // target panel width; rounded to an even panel count per span
      heightRatio: 7,       // truss height ≈ span / heightRatio, clamped below
      minHeight: 5, maxHeight: 9,
      camelbackSpan: 45,    // spans at least this long get a curved (Parker) top chord
      maxOverheadWidth: 16, // wider decks skip overhead lateral bracing (would look absurd)
      chordSize: 0.45, verticalSize: 0.3, diagonalSize: 0.22, lateralSize: 0.16,
    },
    rampLength: 40,         // metres past each deck end over which roads/rails ease back to grade
    rampGrade: 0.04,        // 1:25 approach slope
    alignCos: 0.8,          // |cos| between travel direction and span to count as "on" the bridge (~37°)
    minSpan: 15,            // metres — long side below this → plain slab
    bentSpacing: 12,        // metres between trestle bents along the span
    maxLegSpacing: 6,       // metres between legs across a bent (wide decks get more legs)
    braceLevel: 4,          // metres between horizontal bracing levels on a bent
    minClearance: 4.5,      // deck underside at least this far above the lowest ground under it
    deckThickness: 0.35,
    girderDepth: 1.0,
    railingHeight: 1.1, railingPostSpacing: 2.5,
    legSize: 0.35, braceSize: 0.14, railSize: 0.1,
    batter: 0.08,           // outer-leg splay per metre of leg height
    abutmentLength: 3,
    colors: {
      steel: 0x2f3438,      // dark painted steel
      timber: 0x5b4632,     // members for wood-material bridges
      deck: 0x4a4540,
      stone: 0x8a8378,      // abutments + footings
    },
  },

  // ── River steamboats ─────────────────────────────────────────────────
  // Sternwheelers plying the Red/Assiniboine, with stack smoke and a foam +
  // Kelvin-arm wake. One roaming boat at most; `presence` is the fraction of
  // time one is on the river for a given year (linear between keyframes):
  // first boat 1859 (Anson Northup), ~50% through the 1860s, ~90% at the
  // 1872–78 peak, collapsing after the Pembina Branch rail link (Dec 1878)
  // and CPR (1881), then occasional Assiniboine freight / excursion boats.
  // Only while the river is open (CONFIG.seasons ice/floes). One boat is
  // always moored at the Steamboat Landing south of Upper Fort Garry while
  // presence > 0 (frozen in over winter, no smoke).
  steamboats: {
    presence: [[1858,0],[1859,0.5],[1869,0.5],[1872,0.9],[1878,0.9],[1879,0.5],[1882,0.3],[1886,0.12],[1905,0.08],[1912,0.04],[1913,0]],
    // Share of trips that come down the Assiniboine (then continue down the
    // Red) rather than running the Red — Assiniboine boom 1879–85 (to Portage/Brandon).
    assiniboineShare: [[1859,0.15],[1878,0.2],[1879,0.55],[1885,0.55],[1887,0.3]],
    speed: { upstream: 3.0, downstream: 4.2 },   // m/s; the Red flows north, the Assiniboine east
    draft: 0.45,                                 // metres of hull below the waterline
    dock: { lon: -97.13226, lat: 49.88590, heading: 90 },   // moored against the landing's T-head; heading ° (0=N, 90=E)
    colors: { hull: 0xE6E0CE, cabin: 0xF1EDE1, roof: 0x6B6255, trim: 0x3A3530, stack: 0x1E1C1A, wheel: 0x8B2A1E },
    wake: { length: 160, foamColor: 0xD9D2BF, foamAlpha: 0.45, armAlpha: 0.28, armAngleDeg: 19.5 },
    smokeTint: 0x8C8883,                         // wood-fired: greyer than the locomotives
    // River centrelines (lon/lat, modern river data — water offsetZ applied),
    // derived by marching perpendicular cross-sections of wpg_rivers.geojson.
    // Index order is downstream (Red south→north; Assiniboine west→Forks).
    routes: {
      red: [
        [-97.11365,49.8682], [-97.11344,49.86909], [-97.11443,49.86988], [-97.11548,49.87036], [-97.11664,49.87068], [-97.11784,49.87092],
        [-97.11908,49.87105], [-97.12033,49.8711], [-97.12159,49.87113], [-97.12284,49.87106], [-97.12408,49.87095], [-97.12533,49.87084],
        [-97.12656,49.87068], [-97.12779,49.87053], [-97.12902,49.87035], [-97.13025,49.87019], [-97.13149,49.87008], [-97.13275,49.87009],
        [-97.13398,49.87026], [-97.13513,49.8706], [-97.13614,49.8711], [-97.13683,49.87179], [-97.1372,49.87257], [-97.13749,49.87336],
        [-97.1374,49.87418], [-97.13726,49.87498], [-97.13702,49.87578], [-97.13661,49.87654], [-97.13617,49.8773], [-97.13563,49.87803],
        [-97.13502,49.87874], [-97.13427,49.87939], [-97.13347,49.88001], [-97.13277,49.88068], [-97.13206,49.88135], [-97.1313,49.882],
        [-97.13053,49.88263], [-97.12972,49.88325], [-97.12893,49.88388], [-97.12819,49.88454], [-97.12748,49.8852], [-97.1268,49.88588],
        [-97.12607,49.88654], [-97.12567,49.88732], [-97.12563,49.88813], [-97.12574,49.88894], [-97.12597,49.88974], [-97.12651,49.89048],
        [-97.1272,49.89115], [-97.1278,49.89186], [-97.12832,49.8926], [-97.12892,49.89331], [-97.12955,49.89401], [-97.13016,49.89472],
        [-97.13073,49.89544], [-97.13119,49.8962], [-97.13139,49.897], [-97.13121,49.89781], [-97.13072,49.89856], [-97.12991,49.89919],
        [-97.1289,49.89967], [-97.1278,49.90007], [-97.12667,49.90043], [-97.12546,49.90066], [-97.12425,49.90086], [-97.12298,49.90084],
        [-97.12173,49.90075], [-97.12048,49.90069], [-97.11923,49.90063], [-97.11798,49.90056], [-97.11673,49.90049], [-97.11548,49.90042],
        [-97.11423,49.90036], [-97.11297,49.90034], [-97.11173,49.90051], [-97.11054,49.90077], [-97.10953,49.90127], [-97.10889,49.90199],
        [-97.10864,49.90279], [-97.10885,49.90362], [-97.10967,49.90429], [-97.11077,49.90471], [-97.1119,49.90507], [-97.1131,49.90531],
        [-97.11424,49.90566], [-97.11538,49.906], [-97.11649,49.90637], [-97.11751,49.90685], [-97.11852,49.90733], [-97.11952,49.90782],
        [-97.1205,49.90832], [-97.12147,49.90884], [-97.12243,49.90936], [-97.1234,49.90987], [-97.12434,49.91041], [-97.12522,49.91098],
        [-97.12592,49.91166], [-97.12645,49.9124], [-97.12664,49.9132], [-97.12703,49.914], [-97.12702,49.91482], [-97.12725,49.91508],
      ],
      assiniboine: [
        [-97.1695,49.87645], [-97.16837,49.87704], [-97.1673,49.87746], [-97.16626,49.87792], [-97.16516,49.87831], [-97.16402,49.87864],
        [-97.16271,49.87851], [-97.16157,49.87815], [-97.16068,49.87756], [-97.16008,49.87684], [-97.15956,49.87611], [-97.15895,49.8754],
        [-97.15828,49.87472], [-97.15737,49.87415], [-97.1562,49.87383], [-97.15493,49.87378], [-97.15373,49.87407], [-97.15277,49.87461],
        [-97.15239,49.87541], [-97.1527,49.87622], [-97.15298,49.87701], [-97.15342,49.87777], [-97.15418,49.87842], [-97.15486,49.87911],
        [-97.15501,49.87993], [-97.15449,49.8807], [-97.15341,49.88116], [-97.15228,49.88151], [-97.15106,49.88172], [-97.14979,49.8817],
        [-97.14854,49.88176], [-97.14729,49.88182], [-97.14604,49.88187], [-97.14479,49.88199], [-97.14358,49.88219], [-97.14238,49.88244],
        [-97.14123,49.88277], [-97.14019,49.88323], [-97.13917,49.8837], [-97.13816,49.88417], [-97.13711,49.88461], [-97.136,49.885],
        [-97.13486,49.88533], [-97.13365,49.88557], [-97.1324,49.8857], [-97.13116,49.88583], [-97.1299,49.88576], [-97.12863,49.88576],
      ],
    },
  },

  // ── Construction / demolition / fire ─────────────────────────────────
  // Buildings with a born date go up over [born − duration, born] (so they
  // are finished on their born date): walls, windows and roof rise bottom → top.
  // Small wood buildings show stud framing first, cladding following;
  // larger/masonry ones get timber scaffolding kept just above the walls.
  // Buildings with a died date come down over the month before it, top down
  // — or burn: charred black, upper shell collapses, flames + heavy smoke,
  // ruin cleared by the died date. A feature burns if props.died_by is
  // 'fire' (or died_cause mentions fire), or by randomFireShare.
  construction: {
    minMonths: 1,            // smallest wood buildings
    maxMonths: 24,           // largest/tallest
    masonryFactor: 1.3,      // brick/stone/concrete take longer (capped at maxMonths)
    frameMaxHeight: 10,      // m — non-masonry buildings up to this height show stud framing; others scaffolding
    demolitionMonths: 1,
    fireDays: 20,            // burn + charred ruin (stylised — long enough to see at slow play)
    randomFireShare: 0,      // fraction of dated demolitions shown as fires anyway (0 = only when the data says so)
    frameColor: 0xC8A66E,    // fresh lumber
    scaffoldColor: 0x8B7B60, // weathered timber poles
    maxFires: 6,             // simultaneous fires with flame/smoke particles (nearest first)
    fire: {
      flameEnd: 0.45,        // fraction of the fire window with open flames (the rest smoulders)
      flameRate: 140,        // flame sprites/s per fire at peak (scaled up for big buildings)
      sparkRate: 40,
      smokeRate: 45,         // plume puffs/s at peak
      smokeTail: 0.25,       // plume strength while smouldering after the flames, fading to the end
      smokeLife: 11,         // s — long-lived puffs make a tall column
      smokeRise: 9,          // m/s initial climb
      smokeDrift: 3.5,       // m/s eastward drift (grows as it rises)
      smokeEndSize: 55,      // m — puff size at the top of the plume
      smokeOpacity: 0.75,
      smokeColor: 0x221E1A,
      lightIntensity: 60, lightRange: 140,   // flickering orange glow on the nearest blaze
      poolFlames: 300, poolSparks: 120, poolSmoke: 420,
    },
  },

  // ── Riverbank trees ──────────────────────────────────────────────────
  // Instanced trees in a thin band just outside the river polygons (the
  // riparian elm/ash/maple/cottonwood fringe). Rows are offsets from the
  // water's edge; each row has its own chance of a tree at each station, so
  // the band averages ~2–3 deep. Kept clear of buildings, roads, rails,
  // bridges, named river structures (boat houses, landings, docks, piers,
  // wharves) and the ferry landings below. Crowns hide in winter.
  trees: {
    spacing: 9,                 // metres between stations along the bank
    rows: [ { offset: 6, chance: 0.9 }, { offset: 14, chance: 0.7 }, { offset: 23, chance: 0.4 } ],
    jitter: 3,                  // metres of random scatter per tree
    maxRadius: 3500,            // only within this distance of the scene origin
    minAboveWater: 0.8,         // tree base must be at least this far above water.startY
    clearBuilding: 4, clearRoad: 3, clearRail: 4, clearBridge: 25, clearRiverStructure: 60,
    // Historic ferry landings to keep clear [lon, lat, radius m] — APPROXIMATE
    // positions from written accounts, adjust against the Goad sheets:
    ferries: [
      [-97.1293, 49.8923, 70],  // Winnipeg–St. Boniface steam ferry, west landing (foot of Notre Dame E / Pioneer) — until 1882
      [-97.1253, 49.8916, 70],  //   …east landing (Provencher)
      [-97.1340, 49.8862, 60],  // Assiniboine pontoon crossing near Upper Fort Garry (early 1870s), north side
      [-97.1330, 49.8843, 60],  //   …south side
    ],
    species: [                  // weight = share of trees; shape = crown archetype
      { name: 'American elm',   weight: 0.55, shape: 'vase',  scale: [0.85, 1.2] },
      { name: 'green ash',      weight: 0.15, shape: 'round', scale: [0.8, 1.1] },
      { name: 'Manitoba maple', weight: 0.15, shape: 'round', scale: [0.7, 1.0] },
      { name: 'cottonwood',     weight: 0.15, shape: 'tall',  scale: [0.9, 1.25] },
    ],
    crownColors: [0x2E4A1C, 0x365421, 0x2A4418, 0x3D5A26, 0x33501F],
    barkColor: 0x4A4036,
  },

  // ── Timeline / date slider ───────────────────────────────────────────
  // Drives the top-of-screen date scrubber. `currentViewDate` (module-scope
  // in index.html, mirrored on `window.currentViewDate`) is the single
  // source of truth for "what date is being viewed" — read today by the
  // streetcar traffic system below (tickStreetcars/tickCarts), and intended
  // for building born/died visibility once that hookup exists (see the
  // design note above buildCity() in index.html for why that's not a
  // one-line change).
  timeline: {
    minYear: 1850,
    maxYear: 1960,
    startDate: '1906-07-01',      // date shown on first load (YYYY-MM-DD, local)
    playSpeedDaysPerSecond: 45,   // ⏩ fast-forward rate (years pass)
    // ▶ slow play: 2 days/s ≈ 3 minutes per year. wrapWithinYear loops
    // Dec 31 → Jan 1 of the SAME year so the seasons cycle without buildings
    // changing. enabled = start playing on load (false = start paused).
    seasonCycle: { enabled: true, daysPerSecond: 2, wrapWithinYear: true },
    // ▸▸▸ years fly by: one summer day shown per year; 10/s → 1850–1960 in ~11 s
    yearsFly: { yearsPerSecond: 10, day: '07-15' },
  },

  // ── Seasons (driven by the view date) ────────────────────────────────
  // Each channel is ['MM-DD', value] keyframes, linear between, wrapping over
  // New Year. Rough Winnipeg norms: snow gone ~mid-April, river ice holds a few
  // days longer then breaks up (floes drift for ~2 weeks); grass greens
  // through May, browns from September; elms leaf out in May, colour late
  // Sept–early Oct, bare by late Oct; snow builds through November while the
  // river stays open until freeze-up at month's end.
  seasons: {
    snow:    [['01-01',1],['03-25',1],['04-12',0],['10-28',0],['11-20',1]],
    green:   [['04-12',0],['05-02',0.05],['05-28',1],['09-05',1],['10-10',0.35],['11-01',0.2]],   // ~3 weeks of bare brown after melt
    ice:     [['01-01',1],['04-14',1],['04-17',0],['11-25',0],['11-30',1]],
    floes:   [['04-13',0],['04-16',1],['04-24',0.35],['05-01',0],['11-19',0],['11-24',0.45],['11-30',0]],
    leaf:    [['05-01',0],['05-22',1],['10-02',1],['10-24',0]],
    autumn:  [['09-10',0],['10-02',1],['10-25',1],['10-26',0]],   // leaf colour turn; reset once bare
    heating: [['01-01',1],['04-01',1],['05-10',0],['09-25',0],['11-15',1]],   // chimney smoke multiplier blend
    dormantColor: 0x7A5F35,       // winter-killed / not-yet-green prairie grass — matted straw brown
    springLeafColor: 0x8FAE4A,    // fresh May leaves
    lateAutumnColor: 0x6E4E2C,    // brown leaves hanging on before they drop
    autumnColors: { 'American elm': 0xB89434, 'green ash': 0xC8A83A, 'Manitoba maple': 0xCFAE3E, 'cottonwood': 0xC9A63C },
    floeCount: 450, floeSpeed: 6, floeColor: 0xDCE3EA,   // break-up / freeze-up ice pans
  },

  // ── Streetcars ───────────────────────────────────────────────────────
  streetcars: {
    speed: 4.5,              // m/s (~16 km/h)
    carSpacingMeters: 400,   // target distance (map units/metres) between cars along a
                             // route, each direction — car count per direction = route
                             // length / this value (floored by carsPerDirectionMin below).
                             // Shorter routes get fewer cars, longer ones get more. Lower
                             // this for denser traffic; raise it if frame rate suffers
                             // across all ~29 matched routes (~170km combined).
    carsPerDirectionMin: 1,  // floor so even the shortest routes still get a car
    laneOffset: 2.5,         // metres from centreline
    electrificationYear: 1891, // horse carts (below) vanish at this year — a global
                                // "streetcar era begins" cutoff, separate from each
                                // route's own streetcar_start (see data/wpg_roads_streetcar.geojson)
    dimensions: { width: 2.4, height: 2.8, length: 12.0, skirtHeight: 0.75, roofHeight: 0.55, roadOffsetY: 0.18 },
    colors: {
      body: 0xF0A800, skirt: 0x3A1A0A, roof: 0x3A2E22, window: 0x1A2A35,
      headlight: 0xFFFFCC, taillight: 0xDD1100,
      bodySpecular: 0x332200, windowSpecular: 0x334455,
    },
    routeClips: { // index along route where streetcars are allowed to run, by route name
      Portage: { min: 1,  max: 558 },
      Main:    { min: 54, max: 960 },
    },
  },

  // ── Horse/ox carts (pre-electric era) ───────────────────────────────
  carts: {
    speed: 1.2,            // m/s (~4.3 km/h, walking pace)
    laneOffset: 2.0,
    intervalSeconds: 90,
    countPerDirection: 2,
    dimensions: { width: 1.6, height: 1.2, length: 3.0, roadOffsetY: 0.18 },
    colors: { body: 0x8B5E2A, horse: 0x6B3A1F, ox: 0x9C9484, oxHorn: 0xE8DEC8, wagonRut: 0x6A5A4A },
    routeClips: { Main: { min: 54, max: 260 } },
    oxChance: 0.35,   // fraction of carts drawn by an ox team instead of a horse

    // Spoked cart wheels — one shared merged geometry, instanced per wheel.
    // Rotation speed is derived from actual travel speed each tick (not
    // baked in), so faster carts spin their wheels faster automatically.
    wheels: {
      radius: 0.42,
      tubeThickness: 0.05,   // rim cross-section radius
      spokeCount: 8,
      spokeThickness: 0.045, // box cross-section (both axes) of each spoke
      hubRadius: 0.11,
      hubLength: 0.20,       // hub cylinder length along the axle
      color: 0x2A1E14,
    },

    // Cargo loads — a shared geometry per kind, 1–3 chosen per cart at spawn
    // time (seeded, so stable across ticks) and stacked on the flatbed.
    cargo: {
      maxPerCart: 3,
      minPerCart: 1,
      kinds: ['barrel', 'sack', 'crate', 'hayBale'],
      barrel:  { radius: 0.28, height: 0.55, color: 0x6E4A28 },
      sack:    { radius: 0.30, color: 0xC2B280 },
      crate:   { size: 0.5, color: 0x8A6A3E },
      hayBale: { radius: 0.30, length: 0.65, color: 0xD9B84A },
    },

    // Seated driver figure + reins running to the horse's head anchor.
    driver: {
      torsoColor: 0x3A3428,
      headColor:  0xC49A6C,
      armColor:   0x3A3428,
      reinColor:  0x2A1E14,
      reinThickness: 0.015,
    },

    // Occasional road droppings — small fading discs left behind a moving
    // horse. Pool-based like chimney smoke, so no per-frame allocation.
    droppings: {
      poolSize: 24,
      chancePerSecond: 0.06,  // per moving cart, average one every ~17s
      life: 6.0,              // seconds visible before fully faded
      radius: 0.09,
      color: 0x4A3420,
    },
  },

  // ── Trains ────────────────────────────────────────────────────────
  trains: {
    speedMps: { passenger: 9.0, freight: 6.5, switcher: 2.3 },       // stylised, not literal scale
    dwellSecondsRange: { passenger: [6, 12], freight: [14, 26], switcher: [10, 24] },
    passengerRouteCount: 12,        // top-N longest segments get passenger service
    freightThroughMinLengthM: 900,  // mainline-scale threshold for through freight
    smokePuffsPerLocomotive: 7,
    colors: {
      locoBody: 0x14110f, locoCab: 0x2a2420,
      tender: 0x1c1814, tenderCoal: 0x0c0c0c,
      headlight: 0xfff2c0,
      passengerCars: [0x6e2c2c, 0x5a2a28, 0x4d2624],
      freightCars:   [0x8b3a2e, 0x55524c, 0x6b6357, 0x7a4a33],
      passengerWindow: 0x1a2025, passengerRoof: 0x3a332c,
      locoSpecular: 0x444444,
    },
    dimensions: {
      locoBodyLength: 9.5, locoBodyWidth: 2.5, locoBodyHeight: 2.9,
      tenderLength: 6.0, tenderWidth: 2.4, tenderHeight: 2.3,
      carGap: 0.6,
      passengerCarLength: 18.0, passengerCarWidth: 2.7, passengerCarHeight: 3.2,
      freightCarLength: 11.5, freightCarWidth: 2.6, freightCarHeight: 2.5,
      switcherCarLength: 10.0,
    },
  },

  // ── Audio ───────────────────────────────────────────────────────────
  // Two kinds of sound here: real audio *files* (just the locomotive, for
  // now — add more by giving them a name/path/volume below and wiring the
  // name in index.html's loadTrainAudio-style code), and small synthesized
  // ambient sounds (church bell, hoofbeats) generated in-browser with no
  // sound file needed — their pitch/volume/timing is still fully tunable here.
  audio: {
    files: {
      locomotive: {
        path: './sounds/locomotive-loop.mp3',
        maxConcurrent: 4,     // concurrent locomotive loops across all trains
        rangeMetres: 450,     // beyond this distance, a train doesn't get an audio slot
        refDistance: 15,      // metres at which volume is "full"
        rolloffFactor: 1.2,   // how fast volume falls off with distance
        gainByKind: { passenger: 1.66, freight: 1.99, switcher: 1.45 },
      },
      // Add more entries here later, e.g.:
      // streetcarBell: { path: './sounds/streetcar-bell.mp3', maxConcurrent: 3, rangeMetres: 200, refDistance: 10, rolloffFactor: 1.0, gain: 1.0 },
    },
    ambient: {
      windNoise: {
        lowpassFrequencyHz: 280,
        lowpassQ: 0.6,
        gain: 0.09,
      },
      // churchBell: {
      //   toneFrequenciesHz: [220, 330, 440, 550],
      //   gainPerTone: 0.04,         // amplitude of the loudest (first) tone; others scale down
      //   decaySeconds: 4,
      //   repeatMinMs: 20000, repeatMaxMs: 40000,
      //   startDelayMinMs: 6000, startDelayMaxMs: 8000,
      // },
      // hoofbeats: {
      //   stepGapSeconds: 0.22,
      //   gain: 0.15,
      //   decaySeconds: 0.18,
      //   repeatMinMs: 8000, repeatMaxMs: 15000,
      //   startDelayMs: 12000,
      // },
    },
  },

  // ── Low-memory (mobile) profile ──────────────────────────────────────
  // Deep-merged over this config on touch devices (or ?profile=mobile);
  // ?profile=desktop skips it. Same shape as the settings it overrides.
  mobile: {
    terrain:  { segments: 300 },                 // 40 m grid (DEM is resampled)
    // Only buildings within 3 km. Small details and real window glass only near the camera:
    // meshes are uploaded to the GPU the first time they're visible, so far tiles never use GPU memory
    // (painted windows cover the distance). Phones share one GPU process across all tabs.
    building: { loadRadius: 3000, detailDistance: 600, roofCap: { bigDistance: 2500 } },
    glass:    { maxDistance: 700 },
    camera:   { pixelRatioCap: 1.25 },
    lighting: { sun: { shadowMapSize: 1024 } },
    trees:    { spacing: 14 },
    seasons:  { floeCount: 200 },
  },

  // ── Minimap ─────────────────────────────────────────────────────────
  minimap: {
    canvasSizePx: 200,
    worldRangeMetres: 2500,
    backgroundColor: 'rgba(14,12,10,0.92)',
    borderColor: '#2a1e0e',
    headingColor: '#FFD080',
    riverColor: '#2B4A5C',   // muted river blue (static — doesn't follow the flood level)
    // Dot draw order, bottom → top (dots overlap at this scale; unlisted draw first)
    drawOrder: ['wood_industrial', 'iron', 'wood', 'log', 'lumber', 'brick_veneer', 'brick', 'stone'],
    // Building dots in Goad's fire-insurance atlas colours (others: their material colour)
    materialColors: {
      wood:            '#E8CF5A',   // frame — yellow
      log:             '#E8CF5A',
      lumber:          '#E8CF5A',
      brick:           '#E89AA4',   // brick — pink
      brick_veneer:    '#E89AA4',
      stone:           '#9CC9E4',   // stone — light blue
      wood_industrial: '#A6A6A6',   // industrial frame — grey
      iron:            '#7E8286',   // iron-clad — darker grey
    },
    crosshairColor: '#3a2a10',
  },

  // ── FPS / walk-mode controls ─────────────────────────────────────────
  fpsControls: {
    mouseLookSensitivity: 0.0016,
    touchLookSensitivity: 0.004,
    pitchClampRadians: 1.48,
    minCameraY: 1.0,
  },
};

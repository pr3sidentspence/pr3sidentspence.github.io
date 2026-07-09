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
      './data/mcphillips_1880.geojson',
      './data/goad_1906.geojson',
      './data/combined.geojson',
      './data/wpg_rivers.geojson',
      './data/wpg_roads.geojson',
      './data/wpg_rails_1906.geojson',
    ],
    facadeConfig: './data/facades.json',
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
    buildingOffsetX:  20,   // parcel data is ~10 m west of modern GPS reference
    buildingOffsetZ:   0,
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
    roadColors: {
      summerEdge: [18, 17, 15], summerCentre: [5, 5, 4],
      winterEdge: [245, 246, 250], winterCentre: [32, 28, 24],
    },
  },

  // Time-of-day keyframes the sky/fog/sun smoothly blend between.
  // Each entry: [t (0..1, where the day cycle runs 04:00–22:00),
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
    color: 0x1A2530,
    shininess: 90,
    specular: 0x4868A0,
    opacity: 0.72,
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
    picket: { color: 0xEEEEE0, width: 0.12, spacing: 0.22 },
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
    // LOD distance thresholds (horizontal XZ distance from camera to world origin).
    // < nearDist: per-chimney sprites, up to maxNearEmitters active.
    // > farDist:  city-wide haze sprites only, individual smoke hidden.
    nearDist: 150,
    farDist:  520,
    maxNearEmitters: 50,
    // City-wide haze mode (far view) — flat horizontal smoke layers.
    // Each layer is a PlaneGeometry lying flat so it reads as a blanket of
    // haze from the zoomed-out camera angle, not a billboarded orb.
    // Up≠N: positions are [worldX, worldZ].
    cityHaze: {
      positions: [[-270,210],[-160,310],[50,-20],[160,-120],[-80,80],[20,200],
                  [-220,80],[120,260],[-40,-110],[230,130],[-300,340],[70,110]],
      baseY:   22,         // metres above ground — haze hugs rooftops
      yRange:   6,         // ± vertical wander; layers stay fairly flat
      scale: [220, 380],   // plane diameter in metres
      scaleZ:  0.55,       // depth:width ratio — gives an elliptical footprint
      opacity: [0.38, 0.58],
      life:    28,         // seconds before respawn
      drift:   0.9,        // horizontal wander speed (m/s)
    },
  },

  // ── Terrain ─────────────────────────────────────────────────────────
  // Subdivided ground mesh with gentle prairie noise + river channel deformation.
  // After water GeoJSON loads, terrain vertices near river paths are depressed
  // so the flood plane (water) becomes visible in the channel at low water levels.
  terrain: {
    segments: 1200,         // mesh subdivisions — higher = smoother channel edges, heavier
    noiseAmplitude: 0.80,   // metres of prairie undulation — enough for interesting flood spread
    noiseBaseY: 0.0,        // baseline Y for terrain surface (buildings sit at y=0)
    channelDepth: 5.5,      // metres the channel floor sits below bank level (y=0)
    channelBlendWidth: 160, // metres from river CENTERLINE to flat prairie (covers bank + slope)
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
    startY:  -5.8,   // default water level on page load (inside channel, not overbank)
    riverHalfWidth: 120, creekHalfWidth: 8,
    widths: { brownsCreek: 2.5, redRiver: 220, assiniboineRiver: 85, seineRiver: 22 },
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
    // Streetcar rails (Portage/Main only):
    railHeadWidth: 0.12, railHeight: 0.22,
    // Freight/passenger train rails (slightly slimmer in this model):
    trainRailHeadWidth: 0.10, trainRailHeight: 0.20,
    gaugeHalfWidth: 0.7175,
    throughLineBedWidth: 4.0, sidingBedWidth: 2.4,
    minVisibleYear: 1900,  // rail layer hidden before this year
  },

  // ── Streetcars ───────────────────────────────────────────────────────
  streetcars: {
    speed: 4.5,              // m/s (~16 km/h)
    intervalSeconds: 60,     // seconds between cars, each direction
    laneOffset: 2.5,         // metres from centreline
    electrificationYear: 1891, // streetcars only run from this year onward
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
    colors: { body: 0x8B5E2A, horse: 0x6B3A1F, wagonRut: 0x6A5A4A },
    routeClips: { Main: { min: 54, max: 260 } },
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

  // ── Minimap ─────────────────────────────────────────────────────────
  minimap: {
    canvasSizePx: 200,
    worldRangeMetres: 2500,
    backgroundColor: 'rgba(14,12,10,0.92)',
    borderColor: '#2a1e0e',
    headingColor: '#FFD080',
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

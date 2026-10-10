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

// Sound-hook presets for CONFIG.audio.sfx: distance behaviour by kind of sound (from the sound wiring map).
// _sfx(preset, 'file-name', {overrides}) → { path, refDistance, rolloffPower, maxDistance, …overrides }
const _SFX_CLASS = {
  vehicle: { refDistance: 16, rolloffPower: 1.7, maxDistance: 450 },    // engines, wheels, hooves
  foley:   { refDistance: 8,  rolloffPower: 2.5, maxDistance: 180 },    // hammers, splashes, domestic
  signal:  { refDistance: 45, rolloffPower: 1.3, maxDistance: 2500 },   // whistles, bells, sirens, thunder
  crowd:   { refDistance: 30, rolloffPower: 1.7, maxDistance: 750 },    // bands, crowds, fires
  insect:  { refDistance: 3,  rolloffPower: 3,   maxDistance: 40 },
  step:    { refDistance: 4,  rolloffPower: 3,   maxDistance: 40 },     // the walker's own footsteps
  bed:     {},                                                          // non-positional ambience
};
const _sfx = (cls, file, o = {}) => ({ path: `./sounds/${file}.mp3`, ..._SFX_CLASS[cls], ...o });

export const CONFIG = {

  // ── Data files ──────────────────────────────────────────────────────
  // GeoJSON layers loaded automatically on startup. Add/remove/rename
  // entries to change what loads — paths are relative to index.html.
  dataFiles: {
    autoload: [
      './data/pastforward_2026_assessment.geojson',  // growth master + assessment/heritage dates (matching/merge_assessment.py) — no OSM data
      './data/pastforward_2026_osm.geojson',         // new pre-1907 buildings with OSM footprints — ODbL, kept as a separate database
      './data/pastforward_2026_ufg_walls.geojson',        // Upper Fort Garry: the NE-wall gap + the angled fence that replaced it (tools/ufg_walls.py)
      './data/pastforward_2026_fort_douglas.geojson',    // Fort Douglas (1813-1826/52): PLACEHOLDER footprints (tools/fort_douglas.py)
      './data/pastforward_2026_mcphillips1910.geojson',   // 1910 McPhillips map outside the Goad sheets (Mike's digitization; tools/mcphillips1910_ingest.py)
      './data/pastforward_2026_stb1880.geojson',          // St Boniface buildings from the 1880 bird's-eye view (tools/stb1880_ingest.py; deduped against the master)
      './data/pastforward_2026_ogilvie_stack.geojson',    // Ogilvie Flour Mill smoke stack 1897–2005 (Mike's digitization; demolished by implosion — fire animation, fire_days)
      './data/pastforward_2026_bridges.geojson',          // generated bridge succession per crossing (City chronology + MHS)
      './data/pastforward_2026_seine_bridges.geojson',    // timber bridges over the Seine at Provencher, the railway and Marion (tools/seine_bridges.py)
      './data/pastforward_2026_legislature_osm.geojson',   // Legislative Building + dome, Government House, outbuildings, drives/paths — OSM (ODbL)
      // './data/pastforward_2026.geojson',  // dated growth master without assessment data (no OSM) — swap back by un-commenting
      './data/early_creeks.geojson',                 // creeks of 1874 traced from Graham (1984) Fig. 1 — tools/early_creeks.py
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
    // Born/died per rail feature (tools/date_rails.py) — rails and trains appear when their line was built
    railHistory: './data/rail_history.json',
    facadeImageDir: './images/',
    // Building-material stems that get an auto-loaded bump/texture map
    // (looked for at `./data/bump_<stem>.png`).
    bumpFallbackDir: './images',   // wall bump maps are also looked for here (null = only ./data/)
    bumpMapStems: ['brick', 'roofpeak', 'roofgravel', 'wood', 'stone', 'log', 'iron', 'concrete', 'lumber'],
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
    // Default: over St Boniface, looking northwest across the Forks
    // (Red–Assiniboine confluence ≈ world 453, 1038) toward downtown.
    cameraPosition: { x: 830, y: 330, z: 1415 },
    cameraLookAt:   { x: 453, y: 0,   z: 1038 },
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
    terrainOffsetX:   -29.0,   // −29.0 E / +19.6 S = 35 m along bearing 236° from the old (0, −5): terrain was 35 m too far WSW of the map data
    terrainOffsetZ:   14.6,
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
      // Summer moisture (data/moisture.json — season-to-date rainfall vs
      // normal, + flood years): the summer colour leans toward these.
      droughtColor: 0x6A6436,   // parched, straw-olive
      lushColor:    0x2A5E1E,   // wet-year green
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

  // ── Altitude ────────────────────────────────────────────────────────
  // maxM: the ceiling (default = the orbit's maxDistance). Haze (city smoke haze + distance fog) is full below
  // hazeFadeFromM and gone at hazeGoneFrac × maxM. Flying (walk mode, E/Q) speeds up with height: ×flySpeedAtMax at maxM.
  altitude: { maxM: 3000, hazeFadeFromM: 150, hazeGoneFrac: 0.8, fadePower: 2, fogToo: true, flySpeedAtMax: 5, flySpeedCurve: 0.6 },   // fly speed ×(1+4·(alt/max)^curve): ×2 at 300 m, ×3 at 1 km, ×5 at the ceiling (curve 1 would be linear: only ×1.4 at 300 m)   // fog ×(1−t)² with t = 0 at 150 m, 1 at 2400 m: ~40% left at 1 km, ~15% at 1.5 km

  orbitControls: {
    dampingFactor: 0.07,
    maxPolarAngle: 0.98,   // × Math.PI — 1.0 would let you flip under the ground
    minDistance: 2,
    maxDistance: 6000,     // generous: the ceiling is on ALTITUDE (CONFIG.altitude.maxM = 3000) — a distance cap alone stopped oblique views at ~half that height
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
    maxDistance: 1800,    // …and tiles farther than this (3D) from the camera are hidden, nearest first…
    maxPanes: 150000,     // …up to this many real panes at once (the painted windows take over beyond); 0-cost cap on close-up work
    tilesPerFrame: 2,     // new tiles switched on per frame (spreads GPU uploads)
    // Warm amber glow added to glass at night, scaled by darkness (0..1).
    nightGlowColor: { r: 0.47, g: 0.19, b: 0.02 },
  },

  // ── Procedural window dimensions/density ───────────────────────────
  windows: {
    church: { spacing: 4, width: 1.0, sill: 1.6, heightShare: 0.6 },   // lancet windows on churches (false = none)
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
    deferSliceMs: 6,       // while a deferred chunk builds, yield to the frame loop every this many ms (lower = smoother, slower to appear)
    deferOverdueSliceMs: 40,   // same, when the clock has already passed the chunk's start (date jumps): finish sooner, accept a few hitches
    deferFuture: true,     // PastForward buildings are built only once the clock nears their construction start (false = all at launch)
    detailDistance: 1500,  // parapets, roof caps, chimneys hidden beyond this (m)
    // Feature properties kept in memory after load (everything else in the
    // data files is dropped at load — add a name here if new code needs it)
    keepProps: ['id','uid','pf_uid','name','address','material','floors','type','roof_type','area_m2',
                'born','died','born_basis','died_basis','died_by','died_cause','cause_of_death','fire_days','taper_top','smoke_stack','replaced_by','fires',
                'base_floors','parapet','construction_months','no_windows','source_file','group','cohort',
                'heritage_name','heritage_date','heritage_url','footprint_source','osm_id',
                'st_name','st_type','streetcar_start','rail_class','wall_color','wall_stripes',
                'roof_height','roof_color','bridge_style','bridge_fit','fence_height','fence_gap','fence_width','fence_thickness','fence_color'],
    floorHeight: 4.2,    // metres per floor (Victorian commercial average)
    // Roofs over complex outlines (> 14 points, or roof_type 'wings'): one ridge per convex wing,
    // ridge height = pitch × half the wing's short side, capped at maxRidgeM
    wingRoof: { auto: true, pitch: 0.6, maxRidgeM: 9 },   // auto: false = complex outlines stay flat unless roof_type 'wings'
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
    // Bump strength = scale × height change per screen pixel (three r160), so it needs to be several units, not ~0.5.
    // If a wall looks plain at street level, raise its number; if it looks like sandpaper, lower it.
    bumpScale: { default: 5, lumber: 6, iron: 4, roofpeak: -6, roofgravel: 6 },
    bumpRepeat: {   // repeats per metre = 1 / (size in metres one bump_*.png tile covers) — [along the wall, up]
      brick: [0.57, 1.0],      // ~1.75 m × 1.0 m: 13 courses of 7.5 cm, bricks ~22 cm
      brick_veneer: [0.57, 1.0],
      stone: [0.4, 0.4],       // 2.5 m tile, 8 courses ≈ 30 cm
      wood: [0.67, 0.67],      // 1.5 m tile, 10 clapboards ≈ 15 cm
      log: [0.5, 0.5],         // 2 m tile, 8 logs ≈ 25 cm
      iron: [0.8, 0.8],        // 1.25 m tile, 16 ribs ≈ 8 cm
      concrete: [0.5, 0.5], unknown: [0.5, 0.5], lumber: [0.67, 0.67],
      roofpeak: [1, 1], roofgravel: [1, 1],   // roofs: 1 m tiles (peaked roofs do their own UVs in the shader)   // lumber: 30 boards ≈ 5 cm
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
    // Stack styles: footprint under pipeMaxArea (huts, log cabins) keeps the plain stovepipe; heavy-industry buildings over tubeMinAreaDark m², or
    // multi-storey ones (tubeMinFloors, tubeMinArea) get a round tapering brick tube whose height/radius grow with floors and footprint; everything else
    // a rectangular brick stack (width = rectW0 + rectWPerSqrtArea·√area, depth = width·rectAspect) rising rectExtraH above the roof clearance.
    brick: { pipeMaxArea: 30, tubeMinAreaDark: 300, tubeMinFloors: 3, tubeMinArea: 500,
      colors: [0x8E4A36, 0x9A5240, 0x7C3F2E, 0x6E3A2C, 0x84503C],
      rectW0: 0.4, rectWPerSqrtArea: 0.025, rectMaxW: 1.1, rectAspect: 0.7, rectExtraH: 0.5,
      tubeBaseH: 3.5, tubePerFloor: 0.75, tubePerSqrtArea: 0.075, tubeMaxH: 12, tubeR0: 0.5, tubeRPerSqrtArea: 0.04, tubeMinR: 0.7, tubeMaxR: 2.0, tubeTopRatio: 0.7 },
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
    // Electrification / gas: residential & commercial stacks stop smoking in summer, each at its own year between yearFrom
    // and yearTo; afterwards they only run in the heating season (heatOn: Oct 1→15 ramps in, heatOff: May 1→31 ramps out,
    // day of year) and emit pale vapour (tint, opacity). domesticShare = how much of the city haze is domestic.
    vapor: { yearFrom: 1915, yearTo: 1950, heatOn: [274, 288], heatOff: [121, 151], tint: 0xDDE0E2, opacity: 0.8, domesticShare: 0.75 },
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
    smooth: { radiusM: 30, keepBelowM: 0.5, keepAboveM: 1.5,
      // then: everything away from the riverbanks (slope > bankSlope, +bufferM)
      // pulled toward a wide average of that ground — bumps halve, banks
      // untouched, regional rise kept (strength 0 = off; see flattenDEM)
      flatten: { radiusM: 300, strength: 0.85, bankSlope: 0.08, bufferM: 40, featherM: 20,
                 minAboveWater: 1, maxMoveM: 2.5 } },   // minAboveWater: below startY+this = river channel (St Boniface ground sits ~2 m above normal water)
    // Brown's Creek: a shallow valley carved along its line while it exists
    // (filled in since — the LiDAR is flat there); cosine profile, metres
    // Short segments a→b [lon,lat] along the Seine through the spots where bridge decks cut the LiDAR channel (carved to bedY — deliberately below the
    // neighbouring channel bed so the gap holds water whenever the reaches either side do — see carveRiverGaps)
    riverGaps: [
      // the viewer-mesh check above had left Provencher out of its window; the real break is ~45 m south-east of the first cut:
      { name: 'Seine at Provencher (lower)', a: [-97.10941, 49.89561], b: [-97.10913, 49.89534], halfWidthM: 14, bedY: -9.0 },
      { name: 'Seine at Provencher',   a: [-97.10986, 49.89598], b: [-97.10972, 49.89562], halfWidthM: 12, bedY: -7.0 },
      { name: 'Seine at the railway',  a: [-97.10404, 49.89040], b: [-97.10424, 49.89000], halfWidthM: 12, bedY: -7.0 },
      { name: 'Seine at Marion',       a: [-97.10442, 49.88295], b: [-97.10442, 49.88251], halfWidthM: 12, bedY: -7.0 },
      // found by labelling the water cells of the viewer's own terrain mesh (what you actually see), after the cuts above:
      { name: 'Seine at Marion (north)', a: [-97.10338, 49.88308], b: [-97.10366, 49.88290], halfWidthM: 12, bedY: -7.0 },
      { name: 'Seine at Marion (south)', a: [-97.10443, 49.88245], b: [-97.10450, 49.88209], halfWidthM: 12, bedY: -7.0 },
      { name: 'Seine, south reach',      a: [-97.10394, 49.87967], b: [-97.10394, 49.87949], halfWidthM: 10, bedY: -7.0 },
    ],
    creek: { marshFile: './data/early_marshes.json',
           bridge: { roads: null, creeks: '.', length: 22, width: 12, minWidth: 5, clusterM: 30, color: 0x5d4a36,
               file: './data/early_bridges.json' },   // bridges listed in data (centre, span axis, length, width) — Mike's, from satellite imagery; extra: [] would hand-list more by creek + metres from its mouth   // timber bridge wherever a street crosses a creek while both exist (roads: a list of street names limits it; width = widest deck)
           toRiver: true, eastOfLon: -97.1328, riverEdgeAbove: 0.3, extendStepM: 6, extendMaxM: 400,
           seekRiver: ['fort rouge'], seekMaxM: 250,   // creeks whose end is carried down the low ground to the river's edge
           depth: 1.3, halfWidth: 8, stepM: 3, across: 10, cutShare: 0.9, endTaperM: 15, dirt: 1 },   // shallower and narrower (was 2.5 m deep, 28 m wide)   // one valley field over all pieces; terrain cut over the inner 90%; free ends ease out over endTaperM; bank-dirt floor (0 = grass)
    // The cut-off oxbow east of the Forks (St Boniface/Norwood): found in the
    // LiDAR (relBelowM under a contextM-wide average, inside bbox lon/lat
    // [W, S, E, N], clear of the river banks), kept out of the flattening,
    // deepened (deepenM at the old channel's middle, ramping over
    // deepenRampM of depth), and given a seasonal "sometimes lake".
    oxbow: {
      bbox: [-97.12826, 49.87671, -97.10972, 49.88839],
      contextM: 300, relBelowM: -0.35, deepenM: 1.5, deepenRampM: 0.8,
      lake: {
        // fill 0..1 of the basin by date — spring melt, draining through summer, a little fall rain
        fill: [['03-25',0.1],['04-15',0.35],['04-30',0.9],['06-10',0.75],['07-20',0.35],['08-31',0.1],['10-15',0.2],['11-20',0.3]],
        wetEffect: 0.7,          // × (1 + moisture·wetEffect): wet summers fuller, drought dry
        maxDepthM: 1.6,
        color: 0x4A5236, opacity: 0.88, iceColor: 0xC8D2DC,
        mosquitoAnchors: 70,
        until: '1910-04-15',     // filled in: ground back to today's levels from spring 1910, no lake
      },
    },
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
      historyFile: './data/water_levels.json',   // real Red River levels 1912–, pre-1912 great floods (tools/build_water_climate.py)
      maxGapDays: 75,          // interpolate between records at most this far apart; else fall back to seasonal
      // One flat water surface serves both rivers, and the Assiniboine's bed
      // sits ~2 m above the Red's — so at normal/low water the surface is held
      // at startY (the real level + an offset), blending to the TRUE elevation
      // as the river rises to `trueAbove` (world Y). Floods rise to real heights.
      trueAbove: -2.0,
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
    color: 0x24262C, specular: 0xB8BEC8, shininess: 90,   // train rails: dark steel, polished running surface catches the light
    streetcarRailColor: 0x1C1C1E, streetcarRailSpecular: 0x9EA4AC, streetcarRailShininess: 80,
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
    fit: { bankAboveWaterM: 1.5, marginM: 14, maxHalfM: 500 },   // bridge_fit: ends land where ground rises this far above normal water, + margin
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
  // Kelvin-arm wake. `boats` = how many can be out at once (by year);
  // `presence` = fraction of time each of those is on the river (linear
  // between keyframes). First boat: the Anson Northup reached Fort Garry
  // 10 June 1859 (nothing before). ~50% through the 1860s (International
  // from 1862), the 1872–78 peak (several boats), collapse after the Pembina
  // Branch rail link (Dec 1878) and CPR (1881); Assiniboine freight boom
  // 1879–85; occasional freight / excursion boats after, with Hyland's
  // excursion steamers Winnitoba (launched 7 July 1909) and Bonnitoba (1910)
  // busy until the 1915 season. Only while the river is open (CONFIG.seasons
  // ice/floes). A boat is moored at the Steamboat Landing south of Upper Fort
  // Garry through `dockedYears` (frozen in over winter, no smoke).
  steamboats: {
    presence: [[1859.43,0],[1859.44,0.5],[1869,0.5],[1872,0.9],[1878,0.9],[1879,0.6],[1882,0.45],[1886,0.3],
               [1905,0.25],[1909.5,0.25],[1909.52,0.55],[1915.7,0.55],[1916.2,0.15],[1960,0.1]],
    boats: [[1859,1],[1869.9,1],[1870,2],[1872,3],[1878.9,3],[1879,2],[1886,2],[1886.1,1],[1909.5,1],[1909.52,2],[1915.7,2],[1916.2,1]],
    dockedYears: [1859.44, 1890],
    // Share of trips that come down the Assiniboine (then continue down the
    // Red) rather than running the Red — Assiniboine boom 1879–85 (to Portage/Brandon).
    assiniboineShare: [[1859,0.15],[1878,0.2],[1879,0.55],[1885,0.55],[1887,0.3],[1900,0.15]],
    speed: { upstream: 3.0, downstream: 4.2 },   // m/s; the Red flows north, the Assiniboine east
    draft: 0.45,                                 // metres of hull below the waterline
    dock: { lon: -97.13226, lat: 49.88590, heading: 90 },   // moored against the landing's T-head; heading ° (0=N, 90=E)
    colors: { hull: 0xE6E0CE, cabin: 0xF1EDE1, roof: 0x6B6255, trim: 0x3A3530, stack: 0x1E1C1A, wheel: 0x8B2A1E },
    wake: { length: 160, foamColor: 0xD9D2BF, foamAlpha: 0.45, armAlpha: 0.28, armAngleDeg: 19.5 },
    smokeTint: 0x8C8883,                         // wood-fired: greyer than the locomotives
    smoke: { puffs: 24, life: [4.5, 6.5], size0: 3, grow: 9, opacity: 0.6, rise: 2.2, interval: 0.28 },   // plume per stack: puff pool, life s, start size m, growth m, opacity, climb m/s, s between puffs
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

  // ── Road history ────────────────────────────────────────────────────
  // segments: segment_id (wpg_roads_streetcar.geojson) → [born, died] ISO
  //   dates (null = open), intersected with the usual nearby-building span.
  // extra: period roads that aren't in the modern data — lon/lat path.
  // Main St ran through the site of Upper Fort Garry's east wall/bastions,
  // which came down at the start of 1881 (Main St straightened, 1881–82);
  // until then the road went round the outside of the east wall.
  roadHistory: {
    // Early streets wander: a smooth displacement field (amp metres) that fades out
    // between fromYear and toYear as the town straightens its streets. amp 0 = off.
    bend: { amp: 7, fromYear: 1880, toYear: 1905, corner: 12 },   // corner = how far back (m) the inside of junction corners is filled
    segments: {
      12728: ['1881-01-01', null],   // Main St, bridge head → through the SE wall
      12729: ['1881-01-01', null],   // Main St, through the NE bastion → north
    },
    extra: [
      { name: 'Main St detour east of Upper Fort Garry', born: null, died: '1881-01-01', width: 9,
        path: [[-97.13347,49.88643],[-97.13290,49.88668],[-97.13280,49.88700],[-97.13370,49.88772],[-97.13446,49.88808]] },
    ],
  },

  // ── Window lights through the night ─────────────────────────────────
  // litShare of windows are lit after dark; of those above the ground floor,
  // `lateness` (by clock hour, the TIME slider runs 04:00–22:00) are switched
  // off — each window at its own random point, so buildings darken gradually
  // and are mostly dark by the small hours. Ground floors stay lit.
  nightLights: {
    litShare: 0.62,
    lateness: [[4,0.85],[5.5,0.85],[6.5,0.55],[8,0.3],[17,0],[20,0.1],[22,0.45]],
    paneCellM: 2.2,            // real glass panes: windows hashed on this grid
  },

  // ── Street lights ───────────────────────────────────────────────────
  // First electric arc street lamps: Main St, October 1882 (Manitoba
  // Electric Light & Power, P.V. Carroll); the North West Electric Light &
  // Power Co. lit the streets from June 1883 (MHS). Arc lamps on tall poles
  // at intersections from arcFrom; smaller lamp posts along the blocks from
  // postsFrom (approximate). Heads glow and the ground under them is lit
  // (additive discs) after dark — no real lights, so they're cheap.
  streetLights: {
    arcFrom: '1883-06-01',
    postsFrom: '1908-01-01',
    radius: 2600,              // metres from the scene origin
    spacing: 45,               // metres between block lamps (alternating sides)
    poolOpacity: 0.55,
    arc:  { height: 9.0, arm: 1.6, headSize: 0.32, color: 0x2A2622, glow: 0xF2F0FF, poolRadius: 16 },   // arc light: bluish white
    post: { height: 4.6, arm: 0.5, headSize: 0.24, color: 0x1E2A22, glow: 0xFFD49A, poolRadius: 9 },     // incandescent: warm
  },

  // ── Parades (recorded dates) ────────────────────────────────────────
  // A marching column (band in front, flags) loops the route all day, with
  // crowds lining both sidewalks. Slow play lingers on parade days like
  // storms (timeline.events). Routes are lon/lat along the street
  // centrelines; halfWidth = metres from centreline to where crowds stand.
  parades: {
    routes: {
      mainFromCPR: [[-97.13454,49.90449],[-97.13503,49.90362],[-97.13585,49.90258],[-97.13661,49.90163],[-97.13734,49.90077],
                    [-97.13792,49.90008],[-97.13853,49.89938],[-97.13921,49.89858],[-97.13885,49.89706],[-97.13848,49.89553]],
      cityHallToPortage: [[-97.13853,49.89938],[-97.13921,49.89858],[-97.13885,49.89706],[-97.13848,49.89553],[-97.13982,49.89501],
                    [-97.14227,49.89411],[-97.14472,49.8932],[-97.14718,49.8923],[-97.14962,49.8914]],
    },
    halfWidth: 15,
    speed: 1.3,                 // m/s marching
    decor: { spacing: 30, poleHeight: 7, colors: [0xB02020, 0xF2F2F2, 0x1A3A8A] },   // flag poles + pennant strings along the route
    fadeIn: { crowdSeconds: 4, flagStepSeconds: 0.06, rankStepSeconds: 0.04 },   // staggered arrival
    trafficClearM: 25,         // streetcars/carts this close to the route are off the street during a parade
    list: [
      { date: '1885-07-15', to: '1885-07-17', route: 'mainFromCPR', marchers: 400, uniforms: [0x1E2E22, 0x9A2A22, 0x1A1C22], crowd: 1600,
        note: 'North West Field Force returns from the 1885 Resistance — the 17th: "the biggest day Winnipeg has ever seen"' },
      { date: '1914-08-06', route: 'cityHallToPortage', marchers: 350, uniforms: [0x2A3A2A], crowd: 2000, kilts: true,
        note: '79th Cameron Highlanders parade before 50,000, two days after war is declared' },
      { date: '1914-08-23', route: 'cityHallToPortage', marchers: 400, uniforms: [0x6E6446], crowd: 1800, kilts: true,
        note: 'The 79th Cameron Highlanders leave Winnipeg for Valcartier' },
      { date: '1918-11-11', route: 'cityHallToPortage', marchers: 500, uniforms: [0x6E6446], crowd: 2200,
        note: 'Armistice — 3,000 in uniform march from Market Square past City Hall to Portage and Main' },
      { date: '1919-03-24', route: 'cityHallToPortage', marchers: 450, uniforms: [0x6E6446], crowd: 1800, kilts: true,
        note: 'The 43rd Cameron Highlanders come home, parade, and march to Minto Armoury for discharge' },
      { date: '1924-06-18', route: 'cityHallToPortage', marchers: 450, uniforms: [0x6E6446, 0x2A3450, 0x1A2A4A], crowd: 3000,
        note: "Winnipeg's 50th anniversary (Jubilee) parade, a civic holiday — bands and floats (CPR, HBC, Rotary, the Icelandic community …) on Main Street and Portage Avenue" },
      { date: '1942-02-19', route: 'cityHallToPortage', marchers: 250, uniforms: [0x3A3A3A, 0x6E6446], crowd: 1600,
        note: 'If Day — mock Nazi occupation, then the Victory Bond parade down Portage ("It MUST Not Happen Here!")' },
      { date: '1945-05-08', route: 'cityHallToPortage', marchers: 400, uniforms: [0x6E6446, 0x2A3450], crowd: 2400,
        note: 'VE Day — crowds at Portage and Main' },
      { date: '1945-08-14', route: 'cityHallToPortage', marchers: 300, uniforms: [0x6E6446, 0x2A3450], crowd: 2600,
        note: 'VJ Day — "a jammed Portage Avenue and Main Street … well on past midnight"' },
    ],
  },

  // ── Mosquitoes ──────────────────────────────────────────────────────
  // Faint swirling specks over still water (Brown's Creek, while it exists),
  // only visible within `fade` metres. seasonDays = day-of-year ramp
  // [start, full, full-until, end] (≈ May 20 · Jun 10 · Aug 10 · Sep 5).
  mosquitoes: {
    perAnchor: 40, maxAnchors: 2400,   // (was 400 — the early creeks pushed the oxbow's anchors past the cap, so its clouds never drew)
    color: 0x121212, opacity: 0.8,
    fade: [30, 160],          // metres from the camera: fully drawn inside the first, gone by the second
    cloud: { puffs: 4, size: 4.5, opacity: 0.2, maxPx: 140, fade: [40, 260], color: 0x1A1816 },   // the smoky band over standing water, ~1–3 m up: puffs per anchor, metres across, peak opacity, px cap, fade distances, colour
    sizeK: 60, size: [1.6, 3.6],   // point size in px = sizeK/distance, clamped (× pixel ratio) — was 26/d clamped to 1–2.2 px: easy to miss
    seasonDays: [140, 161, 222, 248],
    wetBoost: 0.8,            // × (1 + wet) in wet summers (seasons.moisture)
    dayLevel: 0.35, duskBoost: 1.6,
  },

  // ── Postcard views ──────────────────────────────────────────────────
  // data/postcard_views.json (optional) — see tools/postcard_views_FORMAT.md.
  // A badge shows when the camera is within matchRadiusM of a card's
  // viewpoint and looking within matchAzDeg / matchElDeg of its heading /
  // pitch; key P (or the badge) opens the list; "On this date" lists cards
  // dated within sameDateDays of the viewer's date. jumpDate: "go to view"
  // also sets the viewer to the card's date. fov = vertical degrees.
  postcards: {
    file: './data/postcard_views.json',
    matchRadiusM: 40, matchAzDeg: 35, matchElDeg: 25,
    nearbyRadiusM: 400, listMax: 8, matchListMax: 20, sameDateDays: 7,   // listMax = nearby rows; matchListMax = matching rows
    defaultHeightM: 2.5, defaultOpacity: 0.5, jumpDate: true,
    // Photo era (year_low..year_high): a card matches a view only while the viewer's
    // year is inside it (± dateSlackYears); cards with no years match any era.
    // Records farther than maxDistanceKm from the model are skipped as bad data.
    eraFilter: true, dateSlackYears: 2, maxDistanceKm: 500,
    checkEveryMs: 250,
  },

  // ── Utility poles and wires (walk mode only, around the camera) ──────
  // Telegraph reached the settlement in 1871 (Main St here); Winnipeg's
  // first telephone exchange 1881 — early lines ran roof to roof, poles only
  // "when the phone people ran out of roofs" (MHS) — and electric light
  // 1882–83: poles on the major streets from majorFrom, every street from
  // allFrom (approximate).
  utilityPoles: {
    telegraphFrom: 1871.85, majorFrom: 1882, allFrom: 1900,
    majorStreets: ['Main','Portage','Provencher','Broadway','Notre Dame','William','Logan','Higgins','Princess','Market','Bannatyne','McDermot','Graham','Donald','Fort','Garry','Kennedy','Selkirk'],
    wires: { telegraph: 2, major: 4, all: 8 },
    radius: 350, rebuildDistance: 90,
    orbitMaxAltitude: 120,     // the orbit camera also shows poles/wires when it is within this height of the ground (walk mode always does)
    spacing: 38, kerbOffset: 1.0,
    height: 9.5, armLength: 2.2,
    sag: 0.7, sagSegments: 4,
    color: 0x5A4A3A, wireColor: 0x1A1816,
  },

  // ── Event cues ──────────────────────────────────────────────────────
  // When a parade or a fire starts, a pulsing column of light rises over it
  // for a few seconds so you can find it; the caption under the date bar
  // names it — click it to fly there.
  cues: { beacon: true, beaconHeight: 160, beaconRadius: 7, beaconSeconds: 6, beaconOpacity: 0.35 },

  // ── Shantytown in the CNR East Yards ────────────────────────────────
  // Ramshackle huts and cabins beside the yard tracks (areaWorld = world
  // x0,z0,x1,z1 box around the East Yards at the Forks). Each goes up in
  // `years`, lasts `lifeYears`, and is displaced early by any building built
  // within buildingClearM.
  shanties: {
    // areaWorld = world x0,z0,x1,z1: the East Yards at the Forks plus open ground west
    // and north of them. Huts go beside yard tracks (trackShare) or on open ground, up
    // to permanentClearM from any permanent structure that stands at the time; each
    // stands `lifeYears` and is displaced early when a permanent building is built
    // within permanentClearM.
    areaWorld: [-700, -700, 900, 1100],
    count: 170, trackShare: 0.45,          // was 70 — more huts (the clearance rules still thin them out)
    years: [1882, 1938], lifeYears: [4, 18],
    trackClearM: 6, spreadM: 22, minSpacingM: 7, permanentClearM: 100,
    size: [2.4, 4.2],
    colors: [0x6A6058, 0x5A4E42, 0x7A6E60, 0x4A4440, 0x6E5A44, 0x3A3632],
  },

  // ── Automobiles ─────────────────────────────────────────────────────
  // First cars in Winnipeg c. 1901–03; common by the 1910s–20s. count =
  // cars on the road by year (around the camera — they respawn within
  // spawnRadiusM). Early: tall, boxy, mostly black; from modernFrom:
  // lower, longer, coloured. Speeds m/s (stylised).
  autos: {
    count: [[1902,0],[1905,3],[1912,20],[1920,45],[1930,70],[1945,95],[1955,140]],
    max: 150, scale: 1,
    spawnRadiusM: 900,
    modernFrom: 1928,
    speedEarly: 6, speedLate: 10,
    colorsEarly: [0x141414, 0x1E2A3A, 0x3A1E1E, 0x2A3A2A],
    colorsLate:  [0x141414, 0x5A6E8A, 0x7A2A24, 0x2E4A3A, 0xB8B0A0, 0x8A7A5A, 0x3A4A6A],
  },

  // ── Fire engines ────────────────────────────────────────────────────
  // Run in along the nearest street when a building catches fire and park
  // there until it's out. Winnipeg: volunteer brigade 1874 (from); first
  // motorised apparatus 1910 (a Webb hose wagon); all first-line apparatus
  // motor by 1929; last fire horses sold 1934 (Winnipeg Firefighters
  // Museum). Red lamps on apparatus from the 1930s, rotating beacons from the
  // late 1940s (approximate, North American practice). Not shown in the
  // fast timeline modes.
  fireEngines: {
    from: 1874,
    motorFrom: 1910,
    motorShare: [[1910,0.05],[1920,0.4],[1929,0.95],[1934.5,1]],
    lightsFrom: 1930, beaconFrom: 1946, sirenFrom: 1915,
    approach: 180,             // metres driven in along the street
    horseSpeed: 6, motorSpeed: 11,
    maxPerFire: 3, maxRoadDistance: 40,
    stayUntil: 0.8,            // fraction of the fire window they stay for
    red: 0xA8201A,
  },

  // ── Floating docks ──────────────────────────────────────────────────
  // Flat (floors ≤ 0.2) river structures named dock / landing / wharf / pier
  // are pulled out of the merged city mesh and ride the river level. In a
  // major flood they break loose and drift downstream (spinning slowly),
  // and are rebuilt once the river is back down. Levels are real metres
  // above normal (same as the flood label).
  docks: {
    freeboard: 0.35,           // deck height above the water
    thickness: 0.55,
    color: 0x7A6448,
    breakAboveMetres: 4.5,
    replaceBelowMetres: 2.0,
    driftSpeed: 1.8,           // m/s downstream
    spin: 0.06,                // rad/s while adrift
  },

  // ── Small craft ─────────────────────────────────────────────────────
  // Canoes (birchbark to ~1900, painted canvas after), HBC York boats
  // (Red River brigades, fading out once steamboats took the freight, gone by
  // the late 1870s), rowboats / skiffs (pleasure boating from the 1870s;
  // Winnipeg Rowing Club 1881) and gasoline launches (from ~1905). Each boat
  // works a stretch of river back and forth, off the centreline. Open water
  // only. count = [[year, boats], …] (linear, rounded).
  smallCraft: {
    canoe:   { count: [[1850,6],[1880,3],[1900,4],[1960,5]],  speed: 1.3, length: 5.2, beam: 0.9,
               birchUntil: 1900, birch: 0x9A7A52, canvas: [0x2E5E3A,0x8B2A1E,0xC9B98F,0x2A4A6A,0x6E6A5E] },
    york:    { count: [[1850,2],[1865,2],[1872,1],[1878,0]],     speed: 1.1, length: 12, beam: 3.0, color: 0x7A5E3E, sail: 0xE2DCC8 },
    rowboat: { count: [[1868,0],[1882,3],[1912,5],[1935,3],[1960,2]], speed: 0.9, length: 4.4, beam: 1.3,
               colors: [0xE6E0CE,0x3E5A6E,0x7A5E3E,0x8B2A1E] },
    launch:  { count: [[1904,0],[1910,2],[1930,3],[1960,3]],      speed: 3.5, length: 8, beam: 2.1, color: 0xEDE8DA, cabin: 0x7A5E3E },
    redShare: 0.65,          // share on the Red (rest on the Assiniboine)
    stretch: [350, 1400],    // metres of river each boat works back and forth
    rower: 0x2A2622,         // people
  },

  // ── Ferries ─────────────────────────────────────────────────────────
  // Crossings before the bridges. lon/lat = a point mid-river on the crossing
  // (midpoints of the landings in trees.ferries, which keep the banks clear);
  // the ferry runs perpendicular to the river there, bank to bank.
  //  • Winnipeg–St Boniface (Red): scow ferry by the 1860s (Duncan
  //    Macdougall), west landing at the foot of Notre Dame East (Pioneer
  //    Ave) → Provencher side; Robert Tait's franchise from 15 Mar 1878 and
  //    his steam ferry Adelaide (side-wheel double-ender, 90×30 ft) from
  //    9 June 1878; ended when the Broadway Bridge opened 16 Apr 1882.
  //    (Start year approximate — "1860s".)
  //  • Assiniboine, just below Upper Fort Garry (Main St line): replaced by
  //    the first Main Street Bridge, 1881. Start date not found — assumed in
  //    service from the start of the timeline.
  ferries: [
    { name: 'St Boniface ferry', river: 'red',         lon: -97.1273, lat: 49.8920, from: '1860-01-01', to: '1878-06-09', kind: 'scow' },
    { name: 'Adelaide',          river: 'red',         lon: -97.1273, lat: 49.8920, from: '1878-06-09', to: '1882-04-16', kind: 'steam' },
    { name: 'Assiniboine ferry', river: 'assiniboine', lon: -97.1335, lat: 49.8852, from: '1850-01-01', to: '1881-06-01', kind: 'scow', northEndEastM: 30 },   // north landing 30 m east of the Main St line: Dept. of Resources & Development 1952 plan A-68 (Upper Fort Garry); estimated from the sheet
  ],
  ferryTiming: { crossSeconds: 70, dwellSeconds: 25,
    bankAboveWaterM: 0.4,   // a landing is where the ground rises this far above normal water
    onBankM: 1 },            // …plus this far onto it (the ramp touches the bank)

  // ── Windmills ───────────────────────────────────────────────────────
  // Red River Settlement tower mills (18 by 1856, 13 of them in St John, St Paul
  // and St Andrew north of the Forks). Only those I could place from the
  // sources are listed; positions are APPROXIMATE (±200 m).
  //  • Robert Logan's mill: ground first 1 Oct 1825 — "a big round building like a tower,
  //    broader at the bottom than at the top, and it had great sails" (his daughter, MHS
  //    Manitoba History 2); on the southern edge of Point Douglas, about a mile north of
  //    Upper Fort Garry, with the old Fort Douglas site.
  //  • Narcisse Marion's mill, St Boniface, built 1840–43 south of the mission church.
  // End dates: windmills gave way to steam/water mills from the 1870s — assumed 1880.
  // Dimensions follow the St Peter's mill (1835): 21.5 ft base, 37 ft tall, sails 17.5 × 6 ft.
  windmills: {
    list: [
      { name: "Logan's windmill (Point Douglas)", lon: -97.1288, lat: 49.9021, from: '1825-10-01', to: '1880-01-01' },
      { name: "Marion's windmill (St Boniface)",  lon: -97.1232, lat: 49.8872, from: '1840-06-01', to: '1880-01-01' },
    ],
    tower: { baseR: 3.3, topR: 2.1, height: 10.5, capH: 3.0, color: 0xD6CEBB, capColor: 0x3B3128 },
    sail:  { length: 9.5, cloth: 6.0, width: 1.9, color: 0xE9E2CF },
    wind:  { base: 4.5, swing: 2.5, prevailingFromDeg: 315 },   // m/s breeze, and where it blows from (NW)
    spinPerMs: 0.13, maxSpin: 2.2,                                  // sail rad/s per m/s of wind, and its cap
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
    // Material stacks at the kerb of the nearest road while a building goes up
    stacks: {
      maxRoadDistance: 25,     // metres past the building's half-size to look for a road
      kerbInset: 1.2,          // metres in from the road edge
      metresPerStack: 7,       // bigger building → more stacks
      maxPerSite: 5,
      gap: 0.6,
      brick:  { size: [1.1, 0.9, 1.2], color: 0xA0503A },   // [across, high, along the road] metres
      stone:  { size: [1.2, 0.8, 1.4], color: 0x9A948A },
      lumber: { size: [1.3, 0.7, 4.2], color: 0xC8A66E },
      sand:   { radius: 1.3, height: 1.0, color: 0xB8A080 },
    },
    // Hammering / sawing one-shots from the nearest sites (sfx constructionHammer / constructionSaw)
    sound: { every: [0.5, 2.5], hours: [7, 18], hammerShare: 0.75 },
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

  // ── Sidewalks ───────────────────────────────────────────────────────
  // Plank walks on both sides of a street where enough has been built (see buildSidewalks): `minBuildings` within radiusM of a 10 m stretch
  // earns a walk (from residentialFrom — the 1882 boom — or eraStart, 1873, on business streets), `businessBuildings` makes it a business street whose
  // planks give way to granolithic in businessEnd years (spread by place); other walks are renewed in concrete by residentialEnd. delayYears after the
  // buildings. Sources: Artibise 'Gateway City' (MHS), City of Winnipeg Archives. No business data yet: building density stands in for businesses.
  sidewalks: { enabled: true, radiusM: 28, minBuildings: 3, businessBuildings: 9, eraStart: 1873, residentialFrom: 1882, delayYears: 1,
    businessEnd: [1898, 1920], residentialEnd: [1920, 1935], concrete: true, concreteEverywhere: true,   // concrete everywhere once the planks go (off on phones: fewer quads)
   
    width: 1.7, gapM: 0.35, lift: 0.16, bizInset: 3.4,   // business streets: walks sit bizInset m closer to the street centre (buildings stand right at the kerb line)
 minRoadWidth: 8, excludeTypes: ['LANE', 'PATH', 'TRAIL', 'HWY', 'RD'],
    // streets that had board walks early (Main's small stretches by 1871, the city's own from 1874) even where the buildings beside them are only dated later:
    streetStarts: { Main: 1872, Portage: 1874, 'Notre Dame': 1875, Water: 1875, McDermot: 1875, Bannatyne: 1875, Princess: 1876, Albert: 1876, Ross: 1877, William: 1877, Market: 1876 },
    plankColor: 0x7A6A55, stoneColor: 0xA9A59B },

  // ── Shop / office signs (prototype: generic trades; later fed from Henderson-directory occupants) ──
  // Signs are drawn at runtime into ONE canvas atlas (slots of slotPx, shared by every sign with the same text/style/colours, least-recently-used
  // eviction) and shown as ONE instanced mesh, so a few hundred cost a single draw call. Only buildings within radiusM of the camera get signs.
  // A building gets a sign (share, weighted up for big footprints) and, if it has floors, a few gilt window lettering signs (windowShare/windowMax).
  // What it says is picked deterministically from `occupants` (filtered by year y, footprint a, floors f) and changes every turnoverYears.
  signs: {
    enabled: true, radiusM: 70, maxAltitudeM: 90, max: 300, minAreaM2: 25, share: 0.32, windowShare: 0.35, windowMax: 3, turnoverYears: 12,
    wallHeightM: 0.6, windowHeightM: 0.34, doorHeightM: 4.65, atlasPx: [2048, 1024], slotPx: [256, 64],
    exclude: /church|cathedral|school|convent|hospital|cemetery|station|elevator|mill\b|works|factory|synagogue|temple|college|university|armou?ry|gaol|jail/i,
    byName: [[/stable|livery/i, 'STABLE', 'wall'], [/blacksmith|smithy|forge/i, '', 'anvil'], [/hotel|house\b/i, 'HOTEL', 'wall'], [/bank/i, 'BANK', 'wall'], [/drug|apothec|pharmac/i, 'DRUGS', 'wall']],
    // t = lettering, s = style: 'wall' (painted board over the door) | 'window' (gilt lettering on glass) | 'anvil' | 'horseshoe' (icon boards)
    occupants: [
      { t: 'STABLE', s: 'wall', y: [1870, 1940], a: [50, 1200], f: [1, 2] },
      { t: 'LIVERY & FEED', s: 'wall', y: [1870, 1930], a: [100, 1200], f: [1, 2] },
      { t: 'GENERAL STORE', s: 'wall', y: [1870, 1940], f: [1, 2] },
      { t: 'FURNITURE', s: 'wall', y: [1880, 1990], a: [80, 2500] },
      { t: 'SECOND HAND', s: 'wall', a: [20, 300], f: [1, 2] },
      { t: 'TAILOR', s: 'wall', a: [20, 260] },
      { t: 'DRESSMAKER', s: 'wall', a: [20, 260] },
      { t: '', s: 'anvil', y: [1870, 1935], a: [30, 500], f: [1, 1] },
      { t: '', s: 'horseshoe', y: [1870, 1935], a: [30, 500], f: [1, 1] },
      { t: 'REAL ESTATE', s: 'wall', y: [1880, 1990] },
      { t: 'TICKETS', s: 'wall', y: [1880, 1970], a: [20, 400] },
      { t: 'APOTHECARY', s: 'wall', y: [1870, 1915] },
      { t: 'PHARMACY', s: 'wall', y: [1905, 1990] },
      { t: 'DRUGS', s: 'wall', y: [1900, 1990] },
      { t: 'LAUNDRY', s: 'wall', y: [1885, 1990], a: [30, 600] },
      { t: 'PHOTOS', s: 'wall', y: [1880, 1960], a: [30, 600] },
      { t: 'BAKERY', s: 'wall', a: [30, 500] },
      { t: 'BUTCHER', s: 'wall', a: [30, 500] },
      { t: 'BARBER', s: 'wall', a: [15, 250] },
      { t: 'HARDWARE', s: 'wall', y: [1875, 1990] },
      { t: 'GROCERIES', s: 'wall', y: [1885, 1990] },
      { t: 'BOOTS & SHOES', s: 'wall', y: [1880, 1990], a: [20, 400] },
      { t: 'MILLINERY', s: 'wall', y: [1885, 1945], a: [20, 400] },
      { t: 'JEWELLER', s: 'wall', y: [1880, 1990], a: [20, 400] },
      { t: 'TOBACCO', s: 'wall', y: [1885, 1990], a: [15, 300] },
      { t: 'RESTAURANT', s: 'wall', y: [1890, 1990], a: [60, 900] },
      { t: 'LAWYER', s: 'window', f: [2, 12] }, { t: 'DOCTOR', s: 'window', f: [2, 12] }, { t: 'DENTIST', s: 'window', y: [1885, 1990], f: [2, 12] },
      { t: 'REAL ESTATE', s: 'window', y: [1880, 1990], f: [2, 12] }, { t: 'INSURANCE', s: 'window', y: [1885, 1990], f: [2, 12] },
      { t: 'NOTARY', s: 'window', f: [2, 12] }, { t: 'ARCHITECT', s: 'window', y: [1880, 1990], f: [3, 12] }, { t: 'ACCOUNTANT', s: 'window', y: [1885, 1990], f: [2, 12] },
      { t: 'TAILOR', s: 'window', f: [2, 6] }, { t: 'DRESSMAKER', s: 'window', f: [2, 6] }, { t: 'PHOTOS', s: 'window', y: [1880, 1960], f: [2, 6] },
      { t: 'TICKETS', s: 'window', y: [1880, 1970], f: [2, 12] }, { t: 'AGENTS', s: 'window', f: [2, 12] }, { t: 'MILLINERY', s: 'window', y: [1885, 1945], f: [2, 6] },
    ],
  },

  // ── Marshes (the ellipses on the 1881 map) ───────────────────────────
  cemetery: { treesFile: './data/cemetery_trees.json', treeSpreadYears: 55, treeJitterYears: 8, treeTauYears: 60, treeMinScale: 0.5, treeScalePerRating: 0.9, grassColor: 0x4A6330, fence: { height: 1.8, spacing: 2.4, fadeNear: 70, fadeFar: 150, color: 0x16161A },   // black iron fence round the grounds (a texture card per ~2.4 m, dithered out with distance)
    gate: { halfWidthM: 3.2, pierSize: 0.8, pierHeight: 2.7, pierColor: 0xB9AA84, capColor: 0x8A8068 },   // stone piers at the east entrance (where the path meets the east edge)
    moundLength: 2, moundWidth: 0.9, moundHeight: 0.22, moundYears: 0.5, moundSoil: 0x4A3828, minGroundY: -3.5, fullYear: 1990, fillPower: 0.8, rowGapM: 3.2, stoneGapM: 1.5 },   // Elmwood headstones follow data/elmwood_years.json (cumulative interments); rowGapM = east-west spacing of rows, stoneGapM = spacing along a row; fullYear/fillPower are only the fallback if that file is missing
  marsh: { color: 0x5A6A38, dormantColor: 0x7A6A44, lift: 0.07, mosquitoAnchors: 30 },   // wet ground draped on the terrain

  // ── Tipis at the Forks ──────────────────────────────────────────────
  // Camps on the point at the Forks until about 1870. Each tipi goes up within appearDays after the snow is gone, comes down
  // within leaveDays before the next snow, and yearRoundShare of them stay all year. until = each tipi's own last year.
  tipis: {
    camps: [ { lon: -97.1308, lat: 49.8881, n: 14, radius: 70 }, { lon: -97.1240, lat: 49.8868, n: 8, radius: 45 } ],   // the point itself, and the east bank opposite
    yearRoundShare: 0.2, appearDays: 30, leaveDays: 30, until: [1864, 1872],
    size: [0.9, 1.15], minSpacingM: 7, minAboveWater: 1.5,
  },

  // ── Early vegetation (stands traced from early plans; see tools/early_vegetation.py) ──
  earlyVegetation: {
    file: './data/early_vegetation.json',
    density: 1,                       // × each stand's per1000m2 (trees per 1000 m²) — the big willow wood is thousands of trees
    kinds: {                          // crown archetype, autumn-colour key and leaf colours per kind
      willow: { shape: 'round', species: 'willow', colors: [0x6E8B3A, 0x7A9440, 0x688232, 0x5F7A30] },
      poplar: { shape: 'tall',  species: 'cottonwood', colors: [0x4F7A2A, 0x5C8A32, 0x46702A, 0x7FA037] },
      oak:    { shape: 'round', species: 'oak', colors: [0x2F4A1A, 0x3A5A22, 0x34501E] },
    },
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
    startDate: '1850-01-01',      // date shown on first load (YYYY-MM-DD, local)
    playSpeedDaysPerSecond: 45,   // ⏩ fast-forward rate (years pass)
    // ▶ slow play: 2 days/s ≈ 3 minutes per year. wrapWithinYear loops
    // Dec 31 → Jan 1 of the SAME year so the seasons cycle without buildings
    // changing. enabled = start playing on load (false = start paused).
    seasonCycle: { enabled: true, daysPerSecond: 2, wrapWithinYear: true },
    // ▶▶▶▶ years fly by: one summer day shown per year; 10/s → 1850–1960 in ~11 s
    yearsFly: { yearsPerSecond: 10, day: '07-15' },
    // ☀ day by day: the clock runs 04:00→22:00 in secondsPerDay, then the next morning
    dayCycle: { secondsPerDay: 6 },
    // ▶▶▶ in between: a frame per month (each 1/12 s), 1 year/s (~2 min for 1850–1960)
    yearsWalk: { yearsPerSecond: 1 },
    // Events (storms, parades, floods from the river levels, fires within
    // fireRadiusM of the camera) slow the continuous modes and stop the
    // jumping ones. Rates in days per second; fires take fireSeconds whatever
    // their length. Jump modes hold each event walk/flyHoldSeconds, playing
    // its span through (storms ≥ jumpStormMinIntensity, floods ≥ jumpFloodAboveMetres).
    events: {
      floodAboveMetres: 3.5, fireRadiusM: 4000,
      play: { stormDaysPerSecond: 0.04, paradeDaysPerSecond: 0.04, floodDaysPerSecond: 0.25, fireSeconds: 40 },
      fast: { stormDaysPerSecond: 0.5,  paradeDaysPerSecond: 0.5,  floodDaysPerSecond: 3,    fireSeconds: 5 },
      walkHoldSeconds: 0.8, flyHoldSeconds: 0.5,
      jumpStormMinIntensity: 0.8, jumpFloodAboveMetres: 4.0,
    },
  },

  // ── Historic storms (data/storms.json) ──────────────────────────────
  // Thunderstorms and blizzards on real dates (tools: see the file's
  // "source"). Each storm fades in over rampHours before its start day and
  // out after its end day; days other than the peak run at offPeak strength.
  storms: {
    file: './data/storms.json',
    rampHours: 6,
    offPeak: 0.75,
    snowAfterDays: 5,          // a blizzard leaves snow cover this long (melting) even out of season
    roadWet: { darken: 0.45, drySeconds: 25 },   // thunderstorm rain darkens the roads by this much; they dry over ~drySeconds after
    fadeSeconds: 0.1,          // time constant of the storm fade in/out (~3× this to settle)
    fogHalfHeight: 180,        // storm fog halves at this camera height above ground (so zoomed-out views don't white/black out)
    boxSize: 180,              // metres — precipitation volume that travels with the camera
    rain: {
      count: 14000,            // streaks at intensity 1
      fallSpeed: 11,           // m/s
      windSpeed: 4,            // m/s sideways drift
      streakLength: 1.6,       // metres
      color: 0xB8C4D0, opacity: 0.35,
    },
    snow: {
      count: 22000,
      fallSpeed: 1.6,
      windSpeed: 16,           // blizzard: driven mostly sideways
      gust: 3.5,               // metres of turbulent swirl
      size: 2.2,               // point size scale
      color: 0xF4F6FA, opacity: 0.85,
    },
    thunderstorm: {
      skyColor: 0x3A4250,      // sky/fog tint at full strength
      fogDensity: 0.0014,
      sunMult: 0.2,            // sun intensity multiplier at full strength
      ambientMult: 0.55,
      lightningEvery: [2.5, 9], // seconds between strikes (random in range, shorter when stronger)
      boltDistance: [350, 2600],
      flashColor: 0xDDE4FF,
      windGain: 0.14,          // extra wind-noise gain
      rainGain: 0.07,          // rain hiss gain
      thunderGain: 0.6,
    },
    blizzard: {
      skyColor: 0xC6CBD2,
      fogDensity: 0.0055,      // ~500 m visibility at full strength
      sunMult: 0.3,
      ambientMult: 0.9,
      windGain: 0.3,
      windLowpassHz: 700,      // wind howls higher-pitched in a blizzard
    },
  },

  // ── Seasons (driven by the view date) ────────────────────────────────
  // Each channel is ['MM-DD', value] keyframes, linear between, wrapping over
  // New Year. Rough Winnipeg norms: snow gone ~mid-April, river ice holds a few
  // days longer then breaks up (floes drift for ~2 weeks); grass greens
  // through May, browns from September; elms leaf out in May, colour late
  // Sept–early Oct, bare by late Oct; snow builds through November while the
  // river stays open until freeze-up at month's end.
  seasons: {
    // Summer moisture index: -1 drought … +1 wet (data/moisture.json).
    moisture: {
      file: './data/moisture.json',
      strength: 0.85,          // how far the summer colour moves toward drought/lush at ±1
      dryPatches: 0.9,         // extra straw patches at -1 (× groundCover.dryAmount)
      treeYellowing: 0.3,      // early autumn tint in trees at -1
    },
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
    floeCount: 1100, floeSpeed: 6, floeColor: 0xDCE3EA,   // break-up / freeze-up ice pans
  },

  // ── Streetcars ───────────────────────────────────────────────────────
  streetcars: {
    speed: 4.5,              // m/s (~16 km/h)
    carSpacingMeters: 900,   // (was 400 — ~730 cars; now about 40%) target distance (map units/metres) between cars along a
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
    // Cars per train by year (linear between; each train ±20%, capped by its
    // route) — trains got much longer as locomotives got bigger.
    carsByYear: {
      passenger: [[1880,3],[1900,6],[1930,10],[1960,12]],
      freight:   [[1880,8],[1900,20],[1930,40],[1960,55]],
      switcher:  [[1880,2],[1960,6]],
    },
    maxCars: 45,                    // cap per train (draw calls) — mobile profile lowers it
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
    // Sound-effect hooks: playSfx(name, x, y, z) (one-shot). Drop the file in
    // ./sounds/ and it plays — a missing file is skipped quietly (logged once).
    // Volume = gain × min(1, (refDistance / d) ^ rolloffPower), silent past
    // maxDistance; rolloffPower 3 = inverse-cube (sharp, local sounds).
    sfx: {
      dockBreak: { path: './sounds/dock-break.mp3', gain: 1.0, refDistance: 25, rolloffPower: 2, maxDistance: 900 },
      constructionHammer: { path: './sounds/construction-hammer.mp3', gain: 0.7, refDistance: 12, rolloffPower: 3, maxDistance: 250 },
      constructionSaw:    { path: './sounds/construction-saw.mp3',    gain: 0.6, refDistance: 12, rolloffPower: 3, maxDistance: 250 },
      // Mobs — loop: true = a looping voice on the nearest maxConcurrent sources
      cartHooves:      { path: './sounds/cart-hooves.mp3',      loop: true, maxConcurrent: 3, gain: 0.6, refDistance: 8,  rolloffPower: 2, maxDistance: 150, gate: { mud: [0, 0.4] } }   /* mudWalkHorse/Ox take over when it's muddy */,
      horseWhinny:     { path: './sounds/horse-whinny.mp3',     gain: 0.7, refDistance: 10, rolloffPower: 2, maxDistance: 250 },
      streetcarRun:    { path: './sounds/streetcar-run.mp3',    loop: true, maxConcurrent: 2, gain: 0.6, refDistance: 12, rolloffPower: 2, maxDistance: 300 },
      streetcarBell:   { path: './sounds/streetcar-bell.mp3',   gain: 0.7, refDistance: 15, rolloffPower: 1.5, maxDistance: 400, minGap: 2, duck: 0.2 },   // replaces the synth bell if present
      trainRun:        { path: './sounds/train-run.mp3',        loop: true, maxConcurrent: 2, gain: 0.7, refDistance: 20, rolloffPower: 1.5, maxDistance: 600 },
      trainWhistle:    { path: './sounds/train-whistle.mp3',    gain: 1.0, refDistance: 60, rolloffPower: 1.2, maxDistance: 3000, minGap: 10, duck: 0.5 },
      steamboatEngine: { path: './sounds/steamboat-engine.mp3', loop: true, maxConcurrent: 2, gain: 0.7, refDistance: 20, rolloffPower: 2, maxDistance: 500 },
      steamboatWhistle:{ path: './sounds/steamboat-whistle.mp3',gain: 1.0, refDistance: 80, rolloffPower: 1.2, maxDistance: 3500, minGap: 10, duck: 0.5 },
      launchEngine:    { path: './sounds/launch-engine.mp3',    loop: true, maxConcurrent: 2, gain: 0.5, refDistance: 10, rolloffPower: 2, maxDistance: 300 },
      paddleSplash:    { path: './sounds/paddle-splash.mp3',    gain: 0.4, refDistance: 5,  rolloffPower: 3, maxDistance: 120, variants: 4 },
      ferryEngine:     { path: './sounds/ferry-engine.mp3',     loop: true, maxConcurrent: 1, gain: 0.6, refDistance: 15, rolloffPower: 2, maxDistance: 400 },
      fireCrackle:     { path: './sounds/fire-crackle.mp3',     loop: true, maxConcurrent: 2, gain: 0.9, refDistance: 25, rolloffPower: 2, maxDistance: 600 },
      fireBell:        { path: './sounds/fire-bell.mp3',        gain: 0.9, refDistance: 25, rolloffPower: 1.5, maxDistance: 900, duck: 0.3 },
      fireGallop:      { path: './sounds/fire-gallop.mp3',      loop: true, maxConcurrent: 2, gain: 0.8, refDistance: 12, rolloffPower: 2, maxDistance: 300 },
      fireSirenLoop:   { path: './sounds/fire-siren.mp3',       loop: true, bus: 'main', maxConcurrent: 2, gain: 1.0, refDistance: 40, rolloffPower: 1.3, maxDistance: 2500 },
      firePump:        { path: './sounds/fire-pump.mp3',        loop: true, maxConcurrent: 2, gain: 0.6, refDistance: 12, rolloffPower: 2, maxDistance: 300 },
      paradeBand:      { path: './sounds/parade-band.mp3',      loop: true, bus: 'main', maxConcurrent: 1, gain: 0.9, refDistance: 25, rolloffPower: 1.5, maxDistance: 900 },
      crowdCheer:      { path: './sounds/crowd-cheer.mp3',      loop: true, maxConcurrent: 2, gain: 0.7, refDistance: 20, rolloffPower: 1.5, maxDistance: 600 },
      mosquitoes:      { path: './sounds/mosquitoes.mp3',       loop: true, maxConcurrent: 1, gain: 0.5, refDistance: 3,  rolloffPower: 3, maxDistance: 40 },

      // ═══ Wired from the sound wiring map (files optional: a missing file is skipped quietly) ═══
      // Per hook:  loop/maxConcurrent (nearest sources get a voice) · minGap (s, rate limit) · variants: N (files name.mp3, name-2.mp3 … name-N.mp3, random pick)
      //   bed: true (non-positional, level set by code) · every:[min,max] + dist:[min,max] (random event around the camera) · duck (0–1: dips ambience under it)
      //   gate: {key:[min,max] …} on the world state — year, hour, month, dow (0=Sun), snow, ice, green, wet, mud, storm, night, built (0 country … 1 downtown), river.
      //   A range may be a list of ranges ([[7,12],[13,17]]); hour/month ranges wrap (min>max). Era and hour gates live here, not in code.
      // — Trains (trainRun/trainWhistle above)
      trainIdle:        _sfx('vehicle', 'train-idle',        { loop: true, maxConcurrent: 2, gain: 0.5, refDistance: 18, maxDistance: 400 }),
      trainRails:       _sfx('vehicle', 'train-rails',       { loop: true, maxConcurrent: 2, gain: 0.45, refDistance: 15, maxDistance: 450 }),
      trainOnboard:     _sfx('bed',     'train-onboard',     { bed: true, gain: 0.6 }),   // level = how close the camera is to a moving train (train.onboardRadius)
      // — Streetcars (streetcarRun above is the old pass-by-heavy hook: retire it when streetcarCruise is chosen)
      streetcarCruise:  _sfx('vehicle', 'streetcar-cruise',  { loop: true, maxConcurrent: 2, gain: 0.5, refDistance: 12, maxDistance: 300 }),
      streetcarIdle:    _sfx('vehicle', 'streetcar-idle',    { loop: true, maxConcurrent: 2, gain: 0.4, refDistance: 10, maxDistance: 200 }),   // not wired: streetcars never stop
      // — Horses, carts, sleighs
      harnessJingle:    _sfx('foley',   'harness-jingle',    { loop: true, maxConcurrent: 3, gain: 0.3, refDistance: 6, maxDistance: 120, gate: { snow: [0, 0.5] } }),
      mudWalkHorse:     _sfx('foley',   'mud-walk-horse',    { loop: true, maxConcurrent: 3, gain: 0.6, refDistance: 8, maxDistance: 150, gate: { mud: [0.4, 1] } }),
      mudWalkOx:        _sfx('foley',   'mud-walk-ox',       { loop: true, maxConcurrent: 2, gain: 0.6, refDistance: 8, maxDistance: 150, gate: { mud: [0.4, 1] } }),
      sleighBells:      _sfx('foley',   'sleigh-bells',      { loop: true, maxConcurrent: 3, gain: 0.45, refDistance: 8, maxDistance: 200, gate: { snow: [0.5, 1] } }),
      // — Motor vehicles (which one plays is picked by year: audio.vehicleEras)
      carModelTDrive:   _sfx('vehicle', 'car-model-t-drive', { loop: true, maxConcurrent: 3, gain: 0.5 }),
      carModelTIdle:    _sfx('vehicle', 'car-model-t-idle',  { loop: true, maxConcurrent: 2, gain: 0.4 }),   // not wired: autos never stop
      car1930s40sDrive: _sfx('vehicle', 'car-1930s-40s-drive', { loop: true, maxConcurrent: 3, gain: 0.5 }),
      car1930s40sIdle:  _sfx('vehicle', 'car-1930s-40s-idle',  { loop: true, maxConcurrent: 2, gain: 0.4 }),  // not wired
      car1950sDrive:    _sfx('vehicle', 'car-1950s-drive',   { loop: true, maxConcurrent: 3, gain: 0.5 }),
      car1950sIdle:     _sfx('vehicle', 'car-1950s-idle',    { loop: true, maxConcurrent: 2, gain: 0.4 }),   // not wired
      busDieselDrive:   _sfx('vehicle', 'bus-diesel-drive',  { loop: true, maxConcurrent: 2, gain: 0.6 }),   // only if audio.vehicleEras.busShare > 0
      busDieselIdle:    _sfx('vehicle', 'bus-diesel-idle',   { loop: true, maxConcurrent: 2, gain: 0.5 }),   // not wired
      carHorn:          _sfx('foley',   'car-horn',          { gain: 0.7, refDistance: 20, rolloffPower: 1.6, maxDistance: 500, minGap: 4, variants: 4, duck: 0.2 }),
      bicycleBell:      _sfx('foley',   'bicycle-bell',      { gain: 0.5, minGap: 8 }),                       // not wired: no cyclists
      // — Footsteps of the walker (walk mode), by surface under the camera
      footstepsPlank:   _sfx('step', 'footsteps-plank',  { gain: 0.5, variants: 4 }),
      footstepsStone:   _sfx('step', 'footsteps-stone',  { gain: 0.5, variants: 4 }),
      footstepsGravel:  _sfx('step', 'footsteps-gravel', { gain: 0.5, variants: 4 }),
      snowFootsteps:    _sfx('step', 'snow-footsteps',   { gain: 0.55, variants: 4 }),
      mudWalkHuman:     _sfx('step', 'mud-walk-human',   { gain: 0.55, variants: 4 }),
      // — People
      kidsPlaying:      _sfx('crowd', 'kids-playing',    { loop: true, maxConcurrent: 2, gain: 0.6, refDistance: 15, maxDistance: 400,
                                                           }),   // schools gate it to recess/after school (audio.sites.school); the parade plays it ungated
      woodChop:         _sfx('foley', 'wood-chop',       { gain: 0.7, refDistance: 10, maxDistance: 250, minGap: 1, variants: 3, gate: { hour: [7, 18], dow: [1, 6] } }),
      newsboyCry:       _sfx('foley', 'newsboy-cry',     { gain: 0.6, refDistance: 14, maxDistance: 200, minGap: 25, variants: 3, every: [25, 70], dist: [12, 70],
                                                           gate: { hour: [7, 18], year: [1880, 1950], built: [0.5, 1] } }),
      // — Animals
      cattleHerd:       _sfx('crowd', 'cattle-herd',     { loop: true, maxConcurrent: 2, gain: 0.6, refDistance: 15, maxDistance: 500 }),
      cattleMoo:        _sfx('foley', 'cattle-moo',      { gain: 0.7, refDistance: 15, maxDistance: 500, minGap: 8, variants: 3 }),
      chickens:         _sfx('foley', 'chickens',        { gain: 0.5, refDistance: 8, maxDistance: 200, minGap: 6, variants: 2, gate: { hour: [5, 20] } }),
      roosterCrow:      _sfx('foley', 'rooster-crow',    { gain: 0.7, refDistance: 20, maxDistance: 700, minGap: 120, variants: 2, every: [60, 160], dist: [60, 300],
                                                           gate: { hour: [4, 6.5], built: [0, 0.7] } }),   // a dawn event near farms/backyards; farms also call it directly
      dogsBarking:      _sfx('foley', 'dogs-barking',    { gain: 0.6, refDistance: 12, maxDistance: 400, minGap: 10, variants: 2, every: [25, 80], dist: [40, 250], gate: { built: [0.05, 1] } }),
      coyotes:          { path: './sounds/coyotes.mp3',  gain: 0.6, refDistance: 80, rolloffPower: 1.2, maxDistance: 1500, minGap: 40, every: [45, 140], dist: [250, 900],
                          gate: { hour: [20, 5], built: [0, 0.5], snow: [0, 1] } },
      wolves:           { path: './sounds/wolves.mp3',   gain: 0.6, refDistance: 80, rolloffPower: 1.2, maxDistance: 1800, minGap: 60, every: [60, 200], dist: [400, 1200],
                          gate: { hour: [21, 4], built: [0, 0.25], year: [1800, 1900] } },
      birdsCrow:        _sfx('foley', 'birds-crow',      { gain: 0.5, refDistance: 20, maxDistance: 500, minGap: 12, variants: 2, every: [12, 40], dist: [30, 200], gate: { hour: [5, 20], snow: [0, 0.6] } }),
      birdsGeese:       { path: './sounds/birds-geese.mp3', gain: 0.6, refDistance: 60, rolloffPower: 1.3, maxDistance: 1500, minGap: 60, variants: 2, every: [40, 130], dist: [100, 600],
                          gate: { month: [[3, 5], [9, 10]], hour: [6, 20] } },
      birdsGulls:       _sfx('bed', 'birds-gulls',       { bed: true, gain: 0.35, gate: { hour: [5, 21], snow: [0, 0.6] } }),     // level = riverfront × daylight
      birdsSongbirds:   _sfx('bed', 'birds-songbirds',   { bed: true, gain: 0.35, gate: { snow: [0, 0.2], green: [0.25, 1] } }),  // level = daylight × green × (less in town)
      crickets:         _sfx('bed', 'crickets',          { bed: true, gain: 0.35, gate: { snow: [0, 0.2], green: [0.5, 1] } }),   // level = night × green × (less in town)
      // — Places
      factoryAmbience:  _sfx('crowd', 'factory-ambience', { loop: true, maxConcurrent: 2, gain: 0.6, refDistance: 20, maxDistance: 400, gate: { hour: [[7, 12], [13, 17]], dow: [1, 6] } }),
      factoryWhistle:   _sfx('signal', 'factory-whistle', { gain: 1.0, maxDistance: 2200, minGap: 30, duck: 0.6, variants: 2 }),
      lumberMill:       _sfx('crowd', 'lumber-mill',     { loop: true, maxConcurrent: 2, gain: 0.6, refDistance: 20, maxDistance: 450, gate: { hour: [7, 17], dow: [1, 6] } }),
      windmill:         _sfx('vehicle', 'windmill',      { loop: true, maxConcurrent: 1, gain: 0.5, refDistance: 15, maxDistance: 300 }),
      wellPump:         _sfx('foley', 'well-pump',       { gain: 0.5, minGap: 20, gate: { hour: [6, 19] } }),
      gateCreak:        _sfx('foley', 'gate-creak',      { gain: 0.45, minGap: 30, variants: 2 }),
      doorCreak:        _sfx('foley', 'door-creak',      { gain: 0.45, minGap: 30, variants: 2 }),                  // not wired: no door/entrance logic
      telegraphKey:     _sfx('foley', 'telegraph-key',   { gain: 0.45, refDistance: 5, maxDistance: 60, minGap: 6, gate: { hour: [7, 20], year: [1860, 1960] } }),
      blacksmithForge:  _sfx('foley', 'blacksmith-forge', { loop: true, maxConcurrent: 2, gain: 0.5, refDistance: 6, maxDistance: 120, gate: { hour: [7, 18], dow: [1, 6] } }),
      blacksmithAnvil:  _sfx('foley', 'blacksmith-anvil', { gain: 0.7, refDistance: 10, maxDistance: 250, minGap: 2, variants: 3, gate: { hour: [7, 18], dow: [1, 6] } }),
      blacksmithQuench: _sfx('foley', 'blacksmith-quench', { gain: 0.6, refDistance: 8, maxDistance: 150, minGap: 30, gate: { hour: [7, 18], dow: [1, 6] } }),
      tinsmith:         _sfx('foley', 'tinsmith',        { gain: 0.6, minGap: 3, variants: 2, gate: { hour: [7, 18], dow: [1, 6] } }),
      printingPress:    _sfx('foley', 'printing-press',  { loop: true, maxConcurrent: 2, gain: 0.5, refDistance: 8, maxDistance: 150, gate: { hour: [7, 18], dow: [1, 6] } }),
      typewriterTyping: _sfx('foley', 'typewriter-typing', { gain: 0.35, refDistance: 5, maxDistance: 60, minGap: 6, gate: { year: [1885, 1999], hour: [8, 18], dow: [1, 6] } }),
      typewriterBell:   _sfx('foley', 'typewriter-bell', { gain: 0.35, refDistance: 5, maxDistance: 60, minGap: 15, gate: { year: [1885, 1999], hour: [8, 18], dow: [1, 6] } }),
      cashRegister:     _sfx('foley', 'cash-register',   { gain: 0.5, refDistance: 6, maxDistance: 80, minGap: 10, gate: { year: [1885, 1999], hour: [8, 18], dow: [1, 6] } }),
      barAmbience:      _sfx('foley', 'bar-ambience',    { loop: true, maxConcurrent: 2, gain: 0.7, refDistance: 6, maxDistance: 120, gate: { hour: [11, 22] } }),
      saloonPiano:      _sfx('foley', 'saloon-piano',    { loop: true, maxConcurrent: 1, gain: 0.5, refDistance: 6, maxDistance: 120, gate: { hour: [17, 22] } }),
      barGlassClink:    _sfx('foley', 'bar-glass-clink', { gain: 0.4, refDistance: 6, maxDistance: 100, minGap: 4, variants: 3, gate: { hour: [11, 22] } }),
      dishesBreak:      _sfx('foley', 'dishes-break',    { gain: 0.6, refDistance: 8, maxDistance: 120, minGap: 90 }),
      cookingSizzle:    _sfx('foley', 'cooking-sizzle',  { loop: true, maxConcurrent: 2, gain: 0.3, refDistance: 4, maxDistance: 50, gate: { hour: [[6.5, 8.5], [11.5, 13.5], [17, 19.5]] } }),
      cookingBoil:      _sfx('foley', 'cooking-boil',    { loop: true, maxConcurrent: 2, gain: 0.3, refDistance: 4, maxDistance: 50, gate: { hour: [[6.5, 8.5], [11.5, 13.5], [17, 19.5]] } }),
      cookingChop:      _sfx('foley', 'cooking-chop',    { gain: 0.3, refDistance: 4, maxDistance: 50, minGap: 3, gate: { hour: [[6.5, 8.5], [11.5, 13.5], [17, 19.5]] } }),
      sewingMachine:    _sfx('foley', 'sewing-machine',  { loop: true, maxConcurrent: 2, gain: 0.35, refDistance: 4, maxDistance: 50, gate: { hour: [9, 16], year: [1860, 2000] } }),
      loomWeaving:      _sfx('foley', 'loom-weaving',    { loop: true, maxConcurrent: 2, gain: 0.35, refDistance: 4, maxDistance: 50, gate: { hour: [9, 16], year: [1700, 1900] } }),
      spinningWheel:    _sfx('foley', 'spinning-wheel',  { loop: true, maxConcurrent: 2, gain: 0.35, refDistance: 4, maxDistance: 50, gate: { hour: [9, 16], year: [1700, 1890] } }),
      churchBell:       _sfx('signal', 'church-bell',    { gain: 0.9, refDistance: 60, maxDistance: 2500, minGap: 60, duck: 0.6, variants: 2, gate: { dow: [0, 0], hour: [9.5, 11] } }),
      schoolBell:       _sfx('signal', 'school-bell',    { gain: 0.7, refDistance: 40, maxDistance: 1200, minGap: 30, duck: 0.4, gate: { dow: [1, 5] } }),
      waterLapping:     _sfx('bed', 'water-lapping',     { bed: true, gain: 0.4 }),                                   // level = riverfront × (quieter when frozen)
      // — Events
      buildingFire:     _sfx('crowd', 'building-fire',   { loop: true, maxConcurrent: 2, gain: 0.9, refDistance: 25, rolloffPower: 2, maxDistance: 700 }),   // big flames only (audio.fireLoudFlames)
      photoFlash:       _sfx('bed', 'photo-flash',       { gain: 0.6, minGap: 1 }),
      pistolCock:       _sfx('foley', 'pistol-cock',     { gain: 0.6, refDistance: 10, maxDistance: 300 }),           // scripted only: playScriptedShot('pistol', x, y, z)
      pistolShot:       _sfx('signal', 'pistol-shot',    { gain: 0.9, refDistance: 40, maxDistance: 1500, variants: 2 }),
      rifleAction:      _sfx('foley', 'rifle-action',    { gain: 0.6, refDistance: 10, maxDistance: 300 }),
      rifleShot:        _sfx('signal', 'rifle-shot',     { gain: 1.0, refDistance: 50, maxDistance: 2200, variants: 2 }),
      thunder:          _sfx('signal', 'thunder',        { gain: 1.0, maxDistance: 1e9, variants: 3, duck: 0.5 }),    // replaces the synthesized thunder if the file exists
      rainstorm:        _sfx('bed', 'rainstorm',         { bed: true, gain: 0.7 }),                                   // replaces the synthesized rain hiss if the file exists
      rainRoofDrip:     _sfx('foley', 'rain-roof-drip',  { loop: true, maxConcurrent: 3, gain: 0.4, refDistance: 4, maxDistance: 40, gate: { wet: [0.05, 1], storm: [0, 0.3] } }),
      windWinter:       _sfx('bed', 'wind-winter',       { bed: true, gain: 0.5, gate: { snow: [0.4, 1] } }),
      iceCracking:      _sfx('foley', 'ice-cracking',    { gain: 0.6, refDistance: 40, rolloffPower: 1.8, maxDistance: 900, minGap: 15, variants: 3, every: [12, 40], dist: [60, 400],
                                                           gate: { ice: [0.4, 1], river: [0.15, 1] } }),
    },
    // Global rules for the sfx hooks (wiring rules in the sound map)
    global: {
      maxOneShots: 16,        // simultaneous one-shot voices; extra ones are dropped
      maxLoops: 14,           // simultaneous looping voices across all hooks (nearest/loudest win)
      duckSeconds: 1.5,       // how long ambience stays ducked under a loud signal (a hook's `duck` = how far it dips, 0–1)
      duckRecover: 0.8,       // seconds to swell back
      siteRadius: 450,        // sites (places) farther than this from the camera are ignored
      tickSeconds: 0.1,       // how often mob/site hooks are gathered
    },
    // Motor vehicles: which loop plays for an auto by year (first row containing the year wins).
    // busShare = share of autos (from the bus year on) that sound like a diesel bus — there is no bus model yet, so 0.
    vehicleEras: { rows: [[1900, 1927, 'carModelTDrive'], [1928, 1949, 'car1930s40sDrive'], [1950, 2100, 'car1950sDrive']], busFrom: 1950, busShare: 0,
                   hornChance: 0.08 },   // chance an auto honks when it turns at a junction near the camera (carHorn)
    // Trains: idle ↔ running crossfade, whistle at departure/arrival, onboard bed near a moving train
    train: { fadeSeconds: 2.5, whistleOnDepart: 0.7, whistleOnArrive: 0.5, whistleRandomPerSec: 1 / 240, onboardRadius: 14, onboardFade: 22 },
    // Walk-mode footsteps. Surface under the camera: board walks/docks → plank (until the planks go: sidewalks.businessEnd), later sidewalks → stone,
    // roadway or yard → gravel; snow cover and mud override. metresPerStep: stride; the sprint stride is longer.
    footsteps: { metresPerStep: 0.8, sprintMetresPerStep: 1.1, snowAbove: 0.45, mudAbove: 0.4, offRoad: 'footstepsGravel', plankUntilYear: 1920, sidewalkBand: [0.5, 3.2] },
    // Mud: after rain (roadWet) or in the thaw months, when there's no snow cover
    mud: { thawMonths: [3, 4], thawLevel: 0.7 },
    // Fires: the big-flame loop plays above this flame strength; and the roof-fall crack (dockBreak) when a fire's shell collapses
    fireLoudFlames: 0.5,
    // Places that make sound. `match` is tested (case-insensitive) against a building's name, first kind to match wins; kind `home` = any unnamed
    // building of homeArea m². loops = looping hooks (nearest maxConcurrent get voices; hook gates apply); random = hooks fired about N times/second
    // from the nearest 3 sites; at = hooks fired at those clock hours (every site kind has its own list, nearest 2 ring). A loop/random may be written
    // {name, gate:{…}} to add a gate for just this kind. Sites exist only while the building stands (born/died).
    sites: {
      factory:    { match: 'factory|foundry|manufactur|brewery|packing|\\bworks\\b|\\bmill\\b|\\bplant\\b|cannery|creamery|elevator', loops: ['factoryAmbience'], at: { factoryWhistle: [7, 12, 17] } },
      sawmill:    { match: 'saw ?mill|lumber|planing|sash and door', loops: ['lumberMill'], random: { woodChop: 0.15 } },
      blacksmith: { match: 'blacksmith|smithy|\\bforge\\b|farrier|horseshoe', loops: ['blacksmithForge'], random: { blacksmithAnvil: 0.25, blacksmithQuench: 0.015 } },
      tinsmith:   { match: 'tinsmith|tinner|sheet metal|plumb', random: { tinsmith: 0.15 } },
      print:      { match: 'printing|printer|press\\b|newspaper|tribune|telegram|free press|publish', loops: ['printingPress'], random: { typewriterTyping: 0.08, typewriterBell: 0.02 } },
      depot:      { match: 'station|depot|telegraph|c\\.? ?p\\.? ?r\\.?\\b', random: { telegraphKey: 0.1 } },
      saloon:     { match: 'saloon|hotel|tavern|\\bbar\\b|\\bpub\\b|brewery tap|beer', loops: ['barAmbience', 'saloonPiano'], random: { barGlassClink: 0.12, dishesBreak: 0.003 } },
      shop:       { match: 'store|shop|grocer|bakery|butcher|market|emporium|merchant|dry goods|hardware', random: { cashRegister: 0.04 } },
      church:     { match: 'church|cathedral|chapel|presbyterian|methodist|baptist|anglican|parish|synagogue|temple', random: { churchBell: 0.03 } },
      school:     { match: 'school|college|academy|collegiate|university', loops: [{ name: 'kidsPlaying', gate: { dow: [1, 5], hour: [[10.25, 10.5], [12, 13], [15.25, 16]] } }],
                    at: { schoolBell: [8.75, 10.25, 10.5, 12, 13, 15.25] } },
      livery:     { match: 'livery|stable|\\bbarn\\b|feed|horse', random: { horseWhinny: 0.01, dogsBarking: 0.01 } },
      farm:       { match: 'farm|ranch|dairy', loops: ['cattleHerd'], random: { cattleMoo: 0.03, chickens: 0.05, dogsBarking: 0.02, wellPump: 0.02, gateCreak: 0.01, horseWhinny: 0.01, roosterCrow: 0.01 } },
      home:       { match: null, homeArea: [30, 300], homeMaxFloors: 3, loops: ['cookingSizzle', 'cookingBoil', 'sewingMachine', 'loomWeaving', 'spinningWheel', 'rainRoofDrip'],
                    random: { cookingChop: 0.1 } },
    },
    // Fixed places not in the building data (farm = the two windmill sites, from CONFIG.windmills.list)
    extraSites: { windmills: { kind: 'farm', loops: ['windmill'] } },
    ambient: {
      windNoise: {
        lowpassFrequencyHz: 280,
        lowpassQ: 0.6,
        gain: 0,          // general ambience MUTED for now (was 0.09) — to return once it's better and has better assets; storms still swell it (weather.windGain)
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
    sidewalks: { concreteEverywhere: false },
    mosquitoes: { perAnchor: 24, maxAnchors: 1200, cloud: { puffs: 3, size: 4.5, opacity: 0.2, maxPx: 100, fade: [40, 200], color: 0x1A1816 } },
    earlyVegetation: { density: 0.4 },            // fewer trees in the early stands
    signs: { radiusM: 45, max: 120, atlasPx: [1024, 512] },
    terrain:  { segments: 300 },                 // 40 m grid (DEM is resampled)
    // Only buildings within 3 km. Small details and real window glass only near the camera:
    // meshes are uploaded to the GPU the first time they're visible, so far tiles never use GPU memory
    // (painted windows cover the distance). Phones share one GPU process across all tabs.
    building: { loadRadius: 3000, detailDistance: 600, roofCap: { bigDistance: 2500 } },
    glass:    { maxDistance: 700, maxPanes: 45000 },
    camera:   { pixelRatioCap: 1.25 },
    lighting: { sun: { shadowMapSize: 1024 } },
    trees:    { spacing: 14 },
    seasons:  { floeCount: 450 },
    streetLights: { spacing: 70, radius: 1800 },
    trains:   { maxCars: 25 },
    autos:    { max: 50, scale: 0.4 },
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
    pinchMetresPerPx: 0.12,   // walk mode: metres moved along the view direction per pixel of pinch/spread
    pitchClampRadians: 1.48,
    minCameraY: 1.0,
  },
};

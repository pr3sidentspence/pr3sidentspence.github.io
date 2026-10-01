# data/postcard_views.json — postcard ↔ camera pairs

Optional file; if it's absent pfviewer simply shows no 📮 UI. One JSON array
(or `{ "views": [ … ] }`) of records, one per postcard that has a comparable
modern street view:

```json
{ "id": "rm_0123",
  "lon": -97.13826, "lat": 49.89558,     // camera position of the street-view match (WGS84)
  "h": 2.5,                               // camera height above ground, m (optional, default 2.5)
  "az": 255,                              // heading, degrees clockwise from north
  "el": 3,                                // pitch, degrees (+ up) (optional, default 0)
  "fov": 60,                              // VERTICAL field of view, degrees (optional: keep the current one)
  "title": "Portage Ave looking west, 1912",
  "date": "1912-07-04",                   // sent / postmark / photo date (optional; enables "On this date")
  "url": "https://pastforward.winnipeg.ca/digital/collection/…/id/…",   // the card on CONTENTdm (opens in a new tab)
  "img": "https://…/full/1000,/0/default.jpg",                           // image to overlay on the 3D view (optional)
  "thumb": "https://…/full/160,/0/default.jpg" }                         // list thumbnail (optional)
```

Behaviour (all tunable under `CONFIG.postcards`):
- The camera is checked ≤ 4×/s, only when it has moved or turned. A **badge**
  lights up when it is within `matchRadiusM` (40 m) of a record's position and
  within `matchAzDeg` (35°) / `matchElDeg` (25°) of its heading / pitch.
- **P** (or the badge) opens the list: *Here* = matches, then nearby views (within
  400 m, with distance and "ahead / 40° left"); *On this date* = records dated
  within `sameDateDays` of the viewer's date.
- **go to view** moves the camera to the record's position / heading / pitch / fov
  (and the viewer's date to the record's date if `jumpDate`); **overlay** also
  lays `img` over the 3D view with an opacity slider and a flip button;
  **card ↗** opens `url`.
- Cost: brute force over typed arrays — measured (slow laptop) 0.09 ms/query at
  5,000 views, 0.4 ms at 20,000, 2 ms at 100,000 (`window._pcBench(n)`).

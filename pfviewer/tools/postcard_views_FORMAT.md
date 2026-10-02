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
  "year_low": 1909, "year_high": 1913,    // the PHOTO's year range (optional; either may be missing → that one year)
  "date": "1912-07-04",                   // date MAILED (optional; can be long after the photo; feeds "On this date")
  "url": "https://pastforward.winnipeg.ca/digital/collection/…/id/…",   // the card on CONTENTdm (opens in a new tab)
  "img": "https://…/full/1000,/0/default.jpg",                           // image to overlay on the 3D view (optional)
  "thumb": "https://…/full/160,/0/default.jpg" }                         // list thumbnail (optional)
```

Dates: **matching a card to a view uses the photo years** (`year_low`/`year_high`):
the card matches while the viewer's year is inside them (± `dateSlackYears`, 2).
A card with a single year is that year ± slack. A card with no photo years but a
mailed `date` is treated as "no later than the year mailed" (mailing can be long
after the photo, so it is only an upper bound); no years and no date → any era.
Years outside 1800–2030 are ignored as bad data. A card that is at the right spot
and heading but in the wrong era appears under "same view, other era" in the list
(and as "N here, other era" on the badge); the **era filter** toggle in the panel
turns the date test off. "go to view" jumps to the mailed date if it falls inside
the photo years, else mid-range (1 July), else the mailed date. The "On this date"
tab uses only the mailed `date`. Records more than `maxDistanceKm` (500) from the
model are skipped as bad coordinates (logged).

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

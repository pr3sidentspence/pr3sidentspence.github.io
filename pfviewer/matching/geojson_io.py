"""GeoJSON writing shared by the data scripts.

dump_geojson_lines writes a FeatureCollection with ONE FEATURE PER LINE:
the same JSON (loads identically in the viewer), but text editors can open
it (a single 15 MB line hangs nano) and git diffs show just the changed
buildings. Extra keyword args (cls=..., ensure_ascii=...) go to json.dumps.
"""
import json


def dump_geojson_lines(fc, f, **kw):
    kw.setdefault('separators', (',', ':'))
    head = [f'{json.dumps(k)}:{json.dumps(v, **kw)}' for k, v in fc.items() if k != 'features']
    f.write('{' + ''.join(h + ',' for h in head) + '"features":[\n')
    f.write(',\n'.join(json.dumps(feat, **kw) for feat in fc.get('features', [])))
    f.write('\n]}\n')

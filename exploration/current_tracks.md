---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.1
  kernelspec:
    display_name: ds-contingency-hurricanes
    language: python
    name: ds-contingency-hurricanes
---

# Current tracks

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

from src.datasources import nhc, codab
```

```python
jam = codab.load_codab("jam")
vct = codab.load_codab("vct")
grd = codab.load_codab("grd")
```

```python
jam
```

```python
df_existing = nhc.load_recent_glb_obsv()
df_existing = df_existing[df_existing["basin"] == "al"]
df_existing = df_existing[df_existing["name"] == "Beryl"]
# df_existing["intensity"] = df_existing["maxwind"].astype(int)
```

```python
df_existing
```

```python
cols = ["latitude", "longitude", "intensity", "pressure"]
df_interp = (
    df_existing.set_index("lastUpdate")[cols]
    .resample("30min")
    .interpolate()
    .reset_index()
)
```

```python
gdf = gpd.GeoDataFrame(
    data=df_interp,
    geometry=gpd.points_from_xy(df_interp["longitude"], df_interp["latitude"]),
    crs=4326,
)
```

```python
gdf
```

```python
for adm in [jam, vct, grd]:
    gdf[f"{adm.iloc[0]['ADM0_PCODE']}_distance"] = (
        gdf.to_crs(3857).geometry.distance(adm.to_crs(3857).iloc[0].geometry)
        / 1000
    )
```

```python
gdf
```

```python
dicts = []
for d_thresh in range(0, 501, 10):
    for pcode in ["JM", "VC", "GD"]:
        gdff = gdf[gdf[f"{pcode}_distance"] < d_thresh]
        max_wind = gdff["intensity"].max()
        dicts.append(
            {"ADM0_PCODE": pcode, "d_thresh": d_thresh, "max_s": max_wind}
        )

threshs = pd.DataFrame(dicts)
threshs
```

```python
threshs[threshs["ADM0_PCODE"] == "GD"]
```

```python
threshs[threshs["ADM0_PCODE"] == "JM"]
```

```python
threshs[threshs["ADM0_PCODE"] == "VC"]
```

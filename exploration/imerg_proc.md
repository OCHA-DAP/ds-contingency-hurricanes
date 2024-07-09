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

# IMERG processing

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import rioxarray as rxr

from src.datasources import nhc, codab
from src.utils import blob, raster
```

```python
jam = codab.load_codab("jam")
vct = codab.load_codab("vct")
grd = codab.load_codab("grd")
```

```python
df_existing = nhc.load_recent_glb_obsv()
df_existing = df_existing[df_existing["basin"] == "al"]
df_existing = df_existing[df_existing["name"] == "Beryl"]
```

```python
# Beryl only

dates = list(df_existing["lastUpdate"].dt.date.unique())
dates.append(min(dates) - pd.Timedelta(days=1))
dates.sort()

dicts = []

for date in dates[:-1]:
    blob_name = f"imerg/v7/imerg-daily-late-{date}.tif"
    date_in = pd.to_datetime(blob_name.split(".")[0][-10:])
    cog_url = (
        f"https://imb0chd0dev.blob.core.windows.net/global/"
        f"{blob_name}?{blob.DEV_BLOB_SAS}"
    )
    da_in = rxr.open_rasterio(
        cog_url, masked=True, chunks={"band": 1, "x": 3600, "y": 1800}
    )
    print(date)
    for adm in [jam, vct, grd]:
        minx, miny, maxx, maxy = adm.total_bounds
        da_box = da_in.sel(x=slice(minx, maxx), y=slice(miny, maxy))
        da_box_up = raster.upsample_dataarray(
            da_box, lat_dim="y", lon_dim="x", resolution=0.05
        )
        da_box_up = da_box_up.rio.write_crs(4326)
        da_clip = da_box_up.rio.clip(adm.geometry, all_touched=True)
        da_mean = da_clip.mean()
        mean_val = float(da_mean.compute())
        dicts.append(
            {
                "date": date_in,
                "mean": mean_val,
                "ADM0_PCODE": adm.iloc[0]["ADM0_PCODE"],
            }
        )
```

```python
df = pd.DataFrame(dicts)
```

```python
df
```

```python
# compare with Haiti
D_THRESH = 20
HTI_CERF_SIDS = [
    "2016273N13300",  # Matthew
    "2008245N17323",  # Ike
    "2008238N13293",  # Gustav
    "2008241N19303",  # Hanna
    "2008229N18293",  # Fay
    "2012296N14283",  # Sandy
]
stats = blob.load_csv_from_blob(
    blob_name=f"ds-aa-hti-hurricanes/processed/stats_{D_THRESH}km.csv"
)
```

```python
rain_col = "max_roll2_sum_rain_imerg"
current_p = 91
current_s = 131
current_name = "Beryl"
CHD_GREEN = "#1bb580"


def sid_color(sid):
    color = "blue"
    if sid in HTI_CERF_SIDS:
        color = "red"
    # elif sid in ibtracs.IMPACT_SIDS:
    #     color = "orange"
    return color


stats["marker_size"] = stats["affected_population"] / 6e2
stats["marker_size"] = stats["marker_size"].fillna(1)
stats["color"] = stats["sid"].apply(sid_color)

fig, ax = plt.subplots(figsize=(8, 8), dpi=300)

ax.scatter(
    stats["max_wind"],
    stats[rain_col],
    s=stats["marker_size"],
    c=stats["color"],
    alpha=0.5,
    edgecolors="none",
)

for j, txt in enumerate(
    stats["name"].str.capitalize() + "\n" + stats["year"].astype(str)
):
    ax.annotate(
        txt.capitalize(),
        (stats["max_wind"][j] + 0.5, stats[rain_col][j]),
        ha="left",
        va="center",
        fontsize=7,
    )

ax.scatter(
    [current_s],
    [current_p],
    marker="x",
    color=CHD_GREEN,
    linewidths=3,
    s=100,
)
ax.annotate(
    f"   {current_name}, observationnel\n",
    (current_s, current_p),
    va="center",
    ha="left",
    color=CHD_GREEN,
    fontweight="bold",
)
ax.annotate(
    "\n   (pour St-Vincent, pas pour Haïti)",
    (current_s, current_p),
    va="center",
    ha="left",
    color=CHD_GREEN,
    fontstyle="italic",
)

if D_THRESH == 230:
    rain_thresh = 60
    ax.axvline(x=50, color="lightgray", linewidth=0.5)
    ax.axhline(y=rain_thresh, color="lightgray", linewidth=0.5)
    ax.fill_between(
        np.arange(50, 200, 1),
        rain_thresh,
        200,
        color="gold",
        alpha=0.2,
        zorder=-1,
    )

    ax.annotate(
        "\nZone de déclenchement   ",
        (155, 170),
        ha="right",
        va="top",
        color="orange",
        fontweight="bold",
    )
ax.annotate(
    "\n\nAllocations CERF en rouge   ",
    (155, 170),
    ha="right",
    va="top",
    color="crimson",
    fontstyle="italic",
)

ax.set_xlim(right=155, left=0)
ax.set_ylim(bottom=0, top=170)

ax.set_xlabel("Vitesse de vent maximum (noeuds)")
ax.set_ylabel(
    "Précipitations pendant deux jours consécutifs maximum, "
    "moyenne sur toute la superficie (mm)"
)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_title(
    f"Comparaison de précipitations, vent, et impact\n"
    f"Seuil de distance = {D_THRESH} km"
)
```

```python

```

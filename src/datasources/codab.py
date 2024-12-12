from typing import Literal

import requests

from src.utils import blob


def download_codab(iso3: Literal["jam", "vct", "grd"]):
    url = f"https://data.fieldmaps.io/cod/originals/{iso3}.shp.zip"
    response = requests.get(url)
    response.raise_for_status()
    blob_name = f"{blob.PROJECT_PREFIX}/raw/codab/{iso3}.shp.zip"
    blob.upload_blob_data(blob_name, response.content)


def load_codab(iso3: Literal["jam", "vct"], admin_level: int = 0):
    shapefile = f"{iso3}_adm{admin_level}.shp"
    gdf = blob.load_gdf_from_blob(
        f"{blob.PROJECT_PREFIX}/raw/codab/{iso3}.shp.zip",
        shapefile=shapefile,
        prod_dev="dev",
    )
    return gdf

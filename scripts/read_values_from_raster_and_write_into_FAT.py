from osgeo import ogr, gdal
import numpy as np
import os
from clip_raster_to_polygon_and_plot_histogram_qq_pdf import get_array_of_raster_values_clipped_to_polygon

vector_path = r"su_benchmark.shp"
raster_path = r"slope.tif"

raster_handle = gdal.Open(raster_path)

vector_handle = ogr.Open(vector_path, True)
layer = vector_handle.GetLayer()

mem = gdal.GetDriverByName("MEM")

fields_and_types = [("slope_med", ogr.OFTReal),
                    ("slope_max", ogr.OFTReal),
                    ("slope_min", ogr.OFTReal),
                    ("slope_25q", ogr.OFTReal),
                    ("slope_75q", ogr.OFTReal)]
                     
for field_name, FAT_type in fields_and_types:
    field_def = ogr.FieldDefn(field_name, FAT_type)
    layer.CreateField(field_def)

for polygon in layer:
    polygon_id = polygon.GetFieldAsInteger("ID")
    array = get_array_of_raster_values_clipped_to_polygon(raster_handle, polygon, vector_path, mem, polygon_id)
    array = array[~np.isin(array, -9999)]
    polygon.SetField("slope_med", float(np.median(array)))
    polygon.SetField("slope_max", float(array.max()))
    polygon.SetField("slope_min", float(array.min()))
    polygon.SetField("slope_25q", float(np.quantile(array, 0.25)))
    polygon.SetField("slope_75q", float(np.quantile(array, 0.75)))
    layer.SetFeature(polygon)
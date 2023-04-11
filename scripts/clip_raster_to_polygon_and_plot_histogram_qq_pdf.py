from osgeo import ogr, gdal
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy

def get_array_of_raster_values_clipped_to_polygon(raster_handle, polygon, vector_path, mem, polygon_id):
    memory_handle = mem.Create("tmp", raster_handle.RasterXSize, raster_handle.RasterYSize, 1, gdal.GDT_Float32)
    clipped_handle = gdal.Warp("tmp", raster_handle, format="MEM", cutlineDSName=vector_path, cutlineWhere=f"ID={polygon_id}", cropToCutline=True, dstNodata=-9999)
    return clipped_handle.GetRasterBand(1).ReadAsArray()

def plot_hist(array, raster_filename, polygon_id):
    mean = np.mean(array)
    std = np.std(array)
    plt.hist(array,
        bins=100,
        histtype="stepfilled")
    plt.axvline(mean, color='black', linestyle='dashed', linewidth=1, label="Mean")
    plt.legend(loc='upper right')
    plt.xlabel("Raster values")
    plt.ylabel("Counts")
    plt.title(f"Histogram of values of {raster_filename} in Polygon {polygon_id}\n$\mu$ = {str(round(mean, 3))}, $\sigma$ = {str(round(std, 3))} ")
    
def plot_QQ(array, raster_filename, polygon_id):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    scipy.stats.probplot(array, dist="norm", plot=ax)
    ax.set_title(f"Probability Plot of values of {raster_filename} in Polygon {polygon_id}") 

def plot_kde(array, raster_filename, polygon_id):
    kernel = scipy.stats.gaussian_kde(array)
    cont = np.linspace(np.min(array), np.max(array))
    pdf = kernel.pdf(cont)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(cont, pdf)
    plt.title(f"Probability Density Function of values of {raster_filename} in Polygon {polygon_id}")
    plt.xlabel("Raster value")
    plt.ylabel("Density")
    
if __name__ == "__main__":
    TO_PLOT = "kde" # QQ or hist or kde
    SHOW_OR_SAVE = "save" # show or save
    vector_path = r"su_benchmark.shp"
    raster_path = r"slope.tif"

    raster_handle = gdal.Open(raster_path)
    raster_filename = os.path.basename(raster_path)

    vector_handle = ogr.Open(vector_path)
    layer = vector_handle.GetLayer()

    mem = gdal.GetDriverByName("MEM")

    for polygon in layer:
        plt.close()
        polygon_id = polygon.GetFieldAsInteger("ID")
        array = get_array_of_raster_values_clipped_to_polygon(raster_handle, polygon, vector_path, mem, polygon_id)
        array = array[~np.isin(array, -9999)]

        if TO_PLOT == "QQ":
            plot_QQ(array, raster_filename, polygon_id)
        elif TO_PLOT == "hist":
            plot_hist(array, raster_filename, polygon_id)
        elif TO_PLOT == "kde":
            plot_kde(array, raster_filename, polygon_id)

        if SHOW_OR_SAVE == "show":
            plt.show()
        elif SHOW_OR_SAVE == "save":
            plt.savefig(os.path.join("out", f"{polygon_id}_{TO_PLOT}.png"))
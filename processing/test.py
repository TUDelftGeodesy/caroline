from locale import normalize
import os
import profile
from PIL import Image





# import matplotlib.pyplot as plt

# I = plt.imread(file2, 'tiff')


# im = Image.open(file2)

from osgeo import gdal

# im = gdal.Open(file2, gdal.GA_ReadOnly)

# options_list = [
#     '-outsize 10% 10%',
#     '-of PNG'
# ] 
# options_string = " ".join(options_list)


# gdal.Translate('image.png',
#                file2,
#                options=options_string)




import rasterio
from rasterio.plot import show
from matplotlib  import pyplot as plt


def tiff_to_png(tiff_file, output_file):
    """
    Saves a visualization of a GeoTIFF file as PNG

    Args:
        tiff_file (string): path to Geotiff file
        output_file (string): name for PNG file
    """

    tiff_image = rasterio.open(tiff_file)

    plt.savefig(output_file)

if __name__ == '__main__':
    file1 = '/home/manuel/Documents/devel/satellite-livestreams/caroline/data/products/proj_oblique_mercator_100_100/20220324_20220405_interferogram_VV@proj_oblique_mercator_100_100_in_coor_radar.tiff'
    file2= '/home/manuel/Documents/devel/satellite-livestreams/caroline/data/products/proj_oblique_mercator_500_500/20160107_20160119_interferogram_VV@proj_oblique_mercator_500_500_in_coor_radar.tiff'

    # img = rasterio.open(file2)

    # # show(img)
    # plt.savefig('image3.png')
    # f = show(img)

    # plt.savefig('image2.png', bbox_inches='tight')

    # plt.close()

    # with rasterio.Env():
    #     with rasterio.open(file2) as src:
    #         print(src.colorinterp[0])
    #         shade = src.read(1)
    #         meta = src.meta

    #     profile = src.profile
    #     profile['photometric'] = "RGB"
    #     with rasterio.open('image.png', 'w', **profile) as dst:
    #         dst.write(src.read())

    src1 = rasterio.open(file2)
   
    # from rasterio.enums import ColorInterp
    # with rasterio.open(file2, 'r+') as src:
    #     src.colorinterp = [ ColorInterp.red, ColorInterp.green, ColorInterp.blue]
    # # print(src.colorinterp[0])


    # profile = src.profile
    # profile['photometric'] = "RGB"
    # with rasterio.open("image3.jpeg", 'w', **profile) as dst:
    #     dst.write(src.read())

    src = rasterio.open(file2)
    # profile = src.profile
    # # profile['photometric'] = "RGB"
    # import numpy as np
    # src_reshaped = np.reshape(src, (1, 171, 117))
    # with rasterio.open("image3.jpeg", 'w', width=171, height=117, count=1, dtype='uint8', nodata=0) as dst:
    #     dst.write(src.read(1))

    src1 = rasterio.open(file2)
    grays = src1.read(1)
    print(type(grays))
   
    print(src1.shape)
    print(grays.shape)
    # import numpy as np
    # def normalize_(array):
    #     array_min, array_max = array.min(), array.max()
    #     return ((array - array_min)/(array_max - array_min))

    # grayn = normalize_(grays)
    # print(grayn.min(), '-', grayn.max(), 'mean:', grayn.mean())

    




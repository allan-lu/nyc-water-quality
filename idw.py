import qgis.analysis
import processing

# Mask layer
coast_lyr = QgsProject.instance().mapLayersByName('coastal_water')[0]

# Locate layer group
root = QgsProject.instance().layerTreeRoot()
mygroup = root.findGroup("o2perc_by_season")

for lyr in mygroup.findLayers():
    # Interpolate layer
    layer = lyr.layer()
    layer_data = QgsInterpolator.LayerData()
    layer_data.source = layer
    layer_data.zCoordInterpolation = False
    layer_data.interpolationAttribute = 6
    layer_data.sourceType = 1
    idw_interpolator = QgsIDWInterpolator([layer_data])

    export_path = "C:/Users/allan/Desktop/Temporary/o2perc_season_idw/idw_{}.tif".format(layer.name())
    rect = coast_lyr.extent()
    res = 100
    ncols = int((rect.xMaximum() - rect.xMinimum()) / res)
    nrows = int((rect.yMaximum() - rect.yMinimum()) / res)
    output = QgsGridFileWriter(idw_interpolator, export_path, rect, ncols, nrows)
    output.writeFile()
    
    # Clip raster
    clipped_output = "E:/Hunter 2019 Fall/GTECH 732/Project/Data/Geopackages/water_quality/o2perc_season_idw/clip_idw_{}.tif".format(layer.name())
    params = {'INPUT': export_path,
              'MASK': coast_lyr,
              'NODATA': None,
              'ALPHA_BAND': False,
              'KEEP_RESOLUTION': True,
              'OUTPUT': clipped_output}
    processing.run('gdal:cliprasterbymasklayer', params)
    iface.addRasterLayer(clipped_output, 'idw_{}'.format(layer.name()))
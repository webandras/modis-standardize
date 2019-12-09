# Import gee api
import ee
# Import modis data product ids
from modis.data.products import Products
from modis.utils.quality_mask import qualityMask, addMask, addMaskedData
from modis.utils.calculations import calculateMeanStdev, standardizeVariables
from geetools import batch

# Initialize gee api
ee.Initialize()
products = Products()

# Function to run the app with '__main__.py'
def run():
  index = 'NDDI'
  year = 2006

  # Data resolution
  resolution = 500
  
  # Step (8-day) for 'ee.Filter.dayOfYear'
  step = 7
  
  # MODIS product name, 'products' object holds the values
  data = products.modisRefl


  print('MODIS termék azonosító:  ' + str(data) + '.')
  print('A választott index: ' + str(index) + '.')
  print('A választott év: ' + str(year) + '.')
  print('Térbeli felbontás: ' + str(resolution) + ' m.')
  print('Időbeli felbontás: ' + str((step + 1)) + ' nap.')

  print('\n')
  print('++++++++++++++++++++++++++++++++++++++')
  print('++++++++++++++++++++++++++++++++++++++')
  print('\n')

  # Looping through day of year values, processing each doy periods
  doy = 89
  for current in range(89, 281, 8):
    doy = current
    print('A választott DOY: ' + str(doy))

    # HUN+SRB study area.
    studyArea = ee.FeatureCollection('users/gulandras90/shapefiles/study_area_modis')

    # Parameters for filtering the ImageCollection
    point = ee.Geometry.Point(19.072, 47.204)

    # Reference period
    start = ee.Date('2000-01-01')
    finish = ee.Date('2017-12-31')

    
    nddi = calculateMeanStdev(data, index, doy, step,
      start, finish, point, studyArea, resolution, False)
    standardizedResult = standardizeVariables(data, index, year, doy, step, point, nddi['meanMap'], nddi['stdevMap'], resolution, True)
 
    task_config = {
      'fileNamePrefix': str(index) + '_' + str(resolution) + 'm_' + str(year) + '_doy' + str(doy),
      'crs': 'EPSG:4326',
      'scale': 500,
      'maxPixels': 10e10,
      'fileFormat': 'GeoTIFF',
      'skipEmptyTiles': True,
      'region': studyArea.geometry().getInfo()['coordinates'] ,
      'folder': 'modis_python'
    }

    # save results to Google Drive
    task = ee.batch.Export.image.toDrive(standardizedResult, str('standardizedNDDI') + str(current), **task_config)
    task.start()
    print('A feldolgozás elindult... Eredmény a Google Drive-ra mentve.')
    print('--------------------------------------')
    print('\n')

print('A feldolgozás sikeresen befejezve.')

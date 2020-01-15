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
  # SET THIS VARIABLE!
  index = 'LST_Night_1km'
  # NDDI, NDVI, NDWI (2000, DOY 64)  => 89
  # ET (2001, DOY 1) => 89
  # LST_Day_1km, LST_Night_1km (2000, DOY 64) => 89
  # Fpar_500m (2000-)  => 89

  # set day of year in this variable:
  doyStart = 89

  # SET THESE VARIABLES!
  year = 2000
  endYear = 2020

  # Data resolution
  resolution = 500
  
  # Step (8-day) for 'ee.Filter.dayOfYear'
  step = 7
  
  # MODIS product name, 'products' object holds the values
  # SET THIS VARIABLE!
  data = products.modisTemp

  # modisRefl = 'MODIS/006/MOD09A1' # => NDDI
  # modisTemp = 'MODIS/006/MOD11A2' # => T/NDVI
  # modisFpar = 'MODIS/006/MOD15A2H' # => fAPAR
  # modisEt = 'MODIS/006/MOD16A2' # => ET


  print('MODIS termék azonosító:  ' + str(data) + '.')
  print('A választott index: ' + str(index) + '.')
  print('A választott kezdőév: ' + str(year) + '.')
  print('A választott befejezőév: ' + str(endYear) + '.')
  print('Térbeli felbontás: ' + str(resolution) + ' m.')
  print('Időbeli felbontás: ' + str((step + 1)) + ' nap.')

  print('\n')
  print('++++++++++++++++++++++++++++++++++++++')
  print('++++++++++++++++++++++++++++++++++++++')
  print('\n')

  for currYear in range(year, endYear, 1):
    # Looping through day of year values, processing each doy periods
    currDoy = doyStart
    while currDoy < 281:
      print('Az aktuális év: ' + str(currYear))
      print('Az aktuális DOY: ' + str(currDoy))

      # HUN+SRB study area.
      studyArea = ee.FeatureCollection('users/gulandras90/shapefiles/study_area_modis')

      # Parameters for filtering the ImageCollection
      point = ee.Geometry.Point(19.072, 47.204)

      # Reference period
      start = ee.Date('2000-01-01')
      finish = ee.Date('2019-12-31')

      if index == 'LST_Night_1km':
        finalResult = calculateMeanStdev(data, index, currDoy, step,
          start, finish, point, studyArea, resolution, True)
      else:
        finalResult = calculateMeanStdev(data, index, currDoy, step,
          start, finish, point, studyArea, resolution, False)

      if index == 'LST_Night_1km':
        standardizedResult = standardizeVariables(data, index, currYear, currDoy, step, point, finalResult['meanMap'], finalResult['stdevMap'], resolution, True)
      else:
        standardizedResult = standardizeVariables(data, index, currYear, currDoy, step, point, finalResult['meanMap'], finalResult['stdevMap'], resolution, False)

      task_config = {
        'fileNamePrefix': str(index) + '_' + str(resolution) + 'm_' + str(currYear) + '_doy' + str(currDoy),
        'crs': 'EPSG:4326',
        'scale': 500,
        'maxPixels': 10e10,
        'fileFormat': 'GeoTIFF',
        'skipEmptyTiles': True,
        'region': studyArea.geometry().getInfo()['coordinates'] ,
        'folder': 'modis_python/' + str(index)
      }

      # save results to Google Drive
      task = ee.batch.Export.image.toDrive(standardizedResult, str('standardized') + str(index) + str(currDoy), **task_config)
      task.start()
      print('A feldolgozás elindult... Az eredmény a Google Drive-ra lesz mentve.')
      print('--------------------------------------')
      print('\n')

      currDoy = currDoy + 8


print('A feldolgozás sikeresen elindult... Eltart egy darabig.')

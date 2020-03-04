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
  index = 'EVI'
  # index = index.upper()
  # Available options:
  # NDDI, NDVI, NDWI (2000, DOY 64)  => 89
  # EVI (2000, DOY 64) => 89
  # ET (2001, DOY 1) => 89
  # ETPET (2001, DOY 1) => 89
  # LST_Day_1km, LST_Night_1km (2000, DOY 64) => 89
  # Fpar_500m (2000-)  => 89
  # TVX => LST_day/NDVI (2000-)  => 89
  # TWX => LST_day/NDWI (2000-)  => 89

  # set day of year in this variable:
  doyStart = 89
  if index == 'EVI':
    doyStart = 81

  # SET THESE VARIABLES!
  # (from 2000 to 2019)
  year = 2000
  endYear = 2020 

  # Data resolution
  resolution = 500
  
  # Step (8-day) for 'ee.Filter.dayOfYear'
  step = 7
  if index == 'EVI':
    step = 15
  
  # MODIS product name, 'products' object holds the values
  if index == 'NDDI' or index == 'NDVI' or index == 'NDWI':
    data = products.modisRefl
  elif index == 'ET' or index == 'ETPET':
    data = products.modisEt
  elif index == 'LST_Day_1km' or index == 'LST_Night_1km':
    data = products.modisTemp
  elif index == 'Fpar_500m':
    data = products.modisFpar
  elif index == 'EVI':
    data = products.modisEvi
  elif index == 'TVX' or index == 'TWX':
    data = 'not set'
  else:
    print('wrong index name supplied')
  

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

  # for currYear in range(year, endYear, 1):
  #   # Looping through day of year values, processing each doy periods
  #   currDoy = doyStart
  #   while currDoy < 281:
  #     print('Az aktuális év: ' + str(currYear))
  #     print('Az aktuális DOY: ' + str(currDoy))

  #     # SET STUDY AREA HERE (upload the shapefile to your Assets folder)
  #     studyArea = ee.FeatureCollection('users/gulandras90/shapefiles/dtk_study_area')

  #     # Parameters for filtering the ImageCollection
  #     point = ee.Geometry.Point(19.072, 47.204)

  #     # Reference period
  #     start = ee.Date('2000-01-01')
  #     finish = ee.Date('2019-12-31')

  #     if index == 'LST_Night_1km':
  #       finalResult = calculateMeanStdev(data, index, currDoy, step,
  #         start, finish, point, studyArea, resolution, True)
  #     else:
  #       finalResult = calculateMeanStdev(data, index, currDoy, step,
  #         start, finish, point, studyArea, resolution, False)


  #     if index == 'LST_Night_1km':
  #       standardizedResult = standardizeVariables(data, index, currYear, currDoy, step, point, finalResult['meanMap'], finalResult['stdevMap'], resolution, True)
  #     else:
  #       standardizedResult = standardizeVariables(data, index, currYear, currDoy, step, point, finalResult['meanMap'], finalResult['stdevMap'], resolution, False)

  #     task_config = {
  #       'fileNamePrefix': str(index) + '_' + str(resolution) + 'm_' + str(currYear) + '_doy' + str(currDoy),
  #       'crs': 'EPSG:4326',
  #       'scale': 500,
  #       'maxPixels': 10e10,
  #       'fileFormat': 'GeoTIFF',
  #       'skipEmptyTiles': True,
  #       'region': studyArea.geometry().getInfo()['coordinates'] ,
  #       'folder': 'modis_python/' + str(index)
  #     }

  #     # save results to Google Drive
  #     task = ee.batch.Export.image.toDrive(standardizedResult, str('standardized') + str(index) + str(currDoy), **task_config)
  #     task.start()
  #     print('A feldolgozás elindult... Az eredmény a Google Drive-ra lesz mentve.')
  #     print('--------------------------------------')
  #     print('\n')

  #     currDoy = currDoy + 8

  # !! FOR TESTING PURPOSES !!
  print('Az aktuális év: ' + str(year))
  print('Az aktuális DOY: ' + str(doyStart))

  # SET STUDY AREA HERE (upload the shapefile to your Assets folder)
  studyArea = ee.FeatureCollection('users/gulandras90/shapefiles/dtk_study_area')

  # Parameters for filtering the ImageCollection
  point = ee.Geometry.Point(19.072, 47.204)

  # Reference period
  start = ee.Date('2000-01-01')
  finish = ee.Date('2019-12-31')

  if index == 'LST_Night_1km':
    finalResult = calculateMeanStdev(data, index, doyStart, step,
        start, finish, point, studyArea, resolution, True)
  else:
    finalResult = calculateMeanStdev(data, index, doyStart, step,
        start, finish, point, studyArea, resolution, False)


  if index == 'LST_Night_1km':
    standardizedResult = standardizeVariables(data, index, year, doyStart, step, point, finalResult['meanMap'], finalResult['stdevMap'], resolution, True)
  else:
    standardizedResult = standardizeVariables(data, index, year, doyStart, step, point, finalResult['meanMap'], finalResult['stdevMap'], resolution, False)

  task_config = {
    'fileNamePrefix': str(index) + '_' + str(resolution) + 'm_' + str(year) + '_doy' + str(doyStart),
    'crs': 'EPSG:4326',
    'scale': 500,
    'maxPixels': 10e10,
    'fileFormat': 'GeoTIFF',
    'skipEmptyTiles': True,
    'region': studyArea.geometry().getInfo()['coordinates'] ,
    'folder': 'modis_python/' + str(index)
  }

  # save results to Google Drive
  task = ee.batch.Export.image.toDrive(standardizedResult, str('standardized') + str(index) + str(doyStart), **task_config)
  task.start()
  print('A feldolgozás elindult... Az eredmény a Google Drive-ra lesz mentve.')
  print('--------------------------------------')
  print('\n')




print('A feldolgozás sikeresen elindult... Eltart egy darabig.')
print('Néhány óráig is eltarthat, mire a Google Drive-ra kerülnek az eredmények.')

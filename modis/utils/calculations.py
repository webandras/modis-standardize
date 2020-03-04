# Import modules
import ee
from modis.utils.quality_mask import qualityMask, addMask, addMaskedData
from modis.utils.indices import addNDVI, addNDWI, addNDDI
from modis.data.products import Products

# Initializations, instantiations
ee.Initialize()
products = Products()


def calculateMeanStdev(product, bandName, doy, step, start, finish, point, studyArea, resolution, isItNightBoolean):
  # for filtering the appropriate image using doy range
  doyFilter = ee.Filter.dayOfYear(doy, doy + step)

  isItNight = (isItNightBoolean or False)

  if product == products.modisRefl:
    # filter collection
    # add quality mask to collection and update mask after
    # add spectral indices to collection
    filteredCollection = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(addNDVI(product)) \
      .map(addNDWI(product)) \
      .map(addNDDI(product)) \
      
    # print(filteredCollection.getInfo())
    
    mean = filteredCollection.select(bandName).mean().clip(studyArea)
    stdev = filteredCollection.select(bandName).reduce(ee.Reducer.stdDev()).clip(studyArea)
    
    # !!! This is a critical part!!
    saveRes = dict()
    saveRes['meanMap'] = mean
    saveRes['stdevMap'] = stdev
    # print(saveRes.get('meanMap').getInfo())

    return saveRes

  elif product == products.modisEvi:
    storedBandName = str(bandName) + '_1'
    # EVI data are 16-day composites, so we need to change the doy filter here
    step = 15
    doyFilter_16day = ee.Filter.dayOfYear(doy, doy + step)
    # filter collection
    # add quality mask to collection and update mask after
    # add spectral indices to collection
    filteredCollection = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter_16day) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product))

    # print(ee.Image(filteredCollection.first()).getInfo())

    mean = filteredCollection.select(storedBandName).mean().clip(studyArea)
    stdev = filteredCollection.select(storedBandName).reduce(ee.Reducer.stdDev()).clip(studyArea)
    
    # !!! This is a critical part!!
    saveRes = dict()
    saveRes['meanMap'] = mean
    saveRes['stdevMap'] = stdev
    # print(saveRes.get('meanMap').getInfo())

    return saveRes
    

  elif product == products.modisTemp:
    storedBandName = str(bandName) + '_1'
    # Add Celsius LST band to ImageCollection
    def addCelsiusBand(image, bandName):
      # Convert data to Celsius, add new band
      return lambda image: image.addBands(image.select(bandName) \
          .multiply(ee.Image.constant(0.02)) \
          .subtract(ee.Image.constant(273.15)) \
          .rename('LSTCelsius'))

    # filter collection
    # add quality mask to collection and update mask after
    filteredCollection = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(addCelsiusBand(product, storedBandName))
      
    # print(filteredCollection.getInfo())
    
    mean = filteredCollection.select('LSTCelsius').mean().clip(studyArea)
    stdev = filteredCollection.select('LSTCelsius').reduce(ee.Reducer.stdDev()).clip(studyArea)
    
    saveRes = dict()
    saveRes['meanMap'] = mean
    saveRes['stdevMap'] = stdev
    # print(saveRes.get('meanMap').getInfo())

    return saveRes

  elif product == products.modisFpar:   
    storedBandName = str(bandName) + '_1'
    # Apply scale to fAPAR data
    def scaleFapar(image, bandName):
      # fAPAR data scale factor = 0.01
      return lambda image: image.addBands(image.select(bandName) \
          .multiply(ee.Image.constant(0.01)) \
          .rename('faparPercent'))
  
    # filter collection
    # add quality mask to collection and update mask after
    filteredCollection = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(scaleFapar(product, storedBandName))
      
    # print(filteredCollection.getInfo())
    
    mean = filteredCollection.select('faparPercent').mean().clip(studyArea)
    stdev = filteredCollection.select('faparPercent').reduce(ee.Reducer.stdDev()).clip(studyArea)
    
    saveRes = dict()
    saveRes['meanMap'] = mean
    saveRes['stdevMap'] = stdev
    # print(saveRes.get('meanMap').getInfo())

    return saveRes
  elif product == products.modisEt:
    storedBandName = bandName
    if bandName == 'ETPET':
      bandName = 'ET'
    
    # Add ET/PET ratio band to ImageCollection
    def addEtPetRatioBand(image):
      return lambda image: image.addBands(image.select('ET_1')
          .divide(image.select('PET_1'))
          .rename('etPetRatio'))
  
    # Apply scale to Evapotranspiration data
    def scaleET(image):
      # fAPAR data scale factor = 0.1
      return lambda image: image.addBands(image.select('ET_1') \
          .multiply(ee.Image.constant(0.1)) \
          .rename('ET_final'))
 
    # filter collection
    # add quality mask to collection and update mask after
    filteredCollection = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(scaleET(product)) \
      .map(addEtPetRatioBand(product))
      
    # print(filteredCollection.getInfo())
    
    if storedBandName == 'ET':
      mean = filteredCollection.select('ET_final').mean().clip(studyArea)
      stdev = filteredCollection.select('ET_final').reduce(ee.Reducer.stdDev()).clip(studyArea)
    elif storedBandName == 'ETPET':
      mean = filteredCollection.select('etPetRatio').mean().clip(studyArea)
      stdev = filteredCollection.select('etPetRatio').reduce(ee.Reducer.stdDev()).clip(studyArea)

    
    saveRes = dict()
    saveRes['meanMap'] = mean
    saveRes['stdevMap'] = stdev
    # print(saveRes.get('meanMap').getInfo())
    return saveRes

  elif bandName == 'TVX' or bandName == 'TWX':
    # Use appropriate index
    index = 'NDVI'
    if bandName == 'TVX':
      index = 'NDVI'
    elif bandName == 'TWX':
      index = 'NDWI'
    
    print('valami')
    print('Az index: ' + index)
    # Add Celsius LST band to ImageCollection
    def addCelsiusBand(image):
      return lambda image: image.addBands(image.select('LST_Day_1km_1')
          .multiply(ee.Image.constant(0.02))
          .subtract(ee.Image.constant(273.15))
          .rename('LSTCelsius'))
    
    product = 'MODIS/006/MOD11A2'
      
    # filter collection
    filteredCollectionLST = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(addCelsiusBand(product))
  
    # print(filteredCollectionLST.getInfo())
    
    product = 'MODIS/006/MOD09A1'
    # filter collection
    filteredCollectionNDI = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(addNDVI(product)) \
      .map(addNDWI(product))
    
    # print(filteredCollectionNDI.getInfo())
    
    # Define an inner join
    innerJoin = ee.Join.inner()
    
    # Specify an equals filter for image timestamps
    # Join NDVI and LST collection images by the start_time field
    filterTimeEq = ee.Filter.equals(leftField = 'system:time_start', rightField = 'system:time_start')
    
    # Apply the join
    innerJoinedData = innerJoin.apply(filteredCollectionLST, filteredCollectionNDI, filterTimeEq)
    # print(innerJoinedData)
    
    # Concatenate images to create an ImageCollection
    innerJoinedData = innerJoinedData.map(lambda feature: ee.Image.cat(feature.get('primary'), feature.get('secondary')))
    
    # We need an explicit cast to ImageCollection so that GEE can understand the type to work with
    innerJoinedData = ee.ImageCollection(innerJoinedData)
    

    saveBandName = 'LST_' + str(index) + '_ratio'

    # Add LST/NDVI ratio band to ImageCollection
    def addLstNdiRatioBand(image, index, saveName):
      return lambda image: image.addBands(image.select('LSTCelsius')
          .divide(image.select(index))
          .rename(saveName))
    
    product = 'MODIS/006/MOD11A2'
    innerJoinedData = innerJoinedData.map(addLstNdiRatioBand(product, index, saveBandName))

    mean = innerJoinedData.select(saveBandName).mean().clip(studyArea)
    stdev = innerJoinedData.select(saveBandName).reduce(ee.Reducer.stdDev()).clip(studyArea)
   
    saveRes = dict()
    saveRes['meanMap'] = mean
    saveRes['stdevMap'] = stdev
    # print(saveRes.get('meanMap').getInfo())
    return saveRes

  else:
    print('Error in "calculateMeanStdev" function def')
    return -1






def standardizeVariables(product, bandName, year, doy, step, point, mean, stdev, resolution, isItNight):
  start = ee.Date(str(year) + '-01-01')
  finish = ee.Date(str(year) + '-12-31')
  # print(start.getInfo(), finish.getInfo())
    
  isItNight = (isItNight or False)
    
  # for filtering the appropriate image using doy range
  doyFilter = ee.Filter.dayOfYear(doy, doy + step)
    
  if product == products.modisRefl:
    # filter collection
    # add quality mask to collection and update mask after
    # add spectral indices to collection
    filteredCollection = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(addNDVI(product)) \
      .map(addNDWI(product)) \
      .map(addNDDI(product))

  
    # print(filteredCollection.getInfo())
    current = filteredCollection.first()

    # standardize dataset
    anomaly = current.select(bandName).subtract(mean)
    standardizedResult = anomaly.divide(stdev).focal_mean()
      
    return standardizedResult
  
  elif product == products.modisEvi:
    storedBandName = str(bandName) + '_1'
     # EVI data are 16-day composites, so we need to change the doy filter here
    step = 15
    doyFilter_16day = ee.Filter.dayOfYear(doy, doy + step)

    # filter collection
    # add quality mask to collection and update mask after
    # add spectral indices to collection
    filteredCollection = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter_16day) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product))

    # print(filteredCollection.getInfo())
    current = filteredCollection.first()

    # standardize dataset
    anomaly = current.select(storedBandName).subtract(mean)
    standardizedResult = anomaly.divide(stdev).focal_mean()
      
    return standardizedResult
  
  elif product == products.modisTemp:

    storedBandName = str(bandName) + '_1'
    # Add Celsius LST band to ImageCollection
    def addCelsiusBand(image, bandName):
      return lambda image: image.addBands(image.select(bandName) \
          .multiply(ee.Image.constant(0.02)) \
          .subtract(ee.Image.constant(273.15)) \
          .rename('LSTCelsius'))

    # filter collection
    # add quality mask to collection and update mask after
    filteredCollection = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(addCelsiusBand(product, storedBandName)) \
      
  
    # print(filteredCollection.getInfo())
    current = filteredCollection.first()
    
    # standardize dataset
    anomaly = current.select('LSTCelsius').subtract(mean)
    standardizedResult = anomaly.divide(stdev).focal_mean()
      
    return standardizedResult

  elif product == products.modisFpar:
    storedBandName = str(bandName) + '_1'
      
    # Apply scale to fAPAR data
    def scaleFapar(image, bandName):
      # fAPAR data scale factor = 0.01
      return lambda image: image.addBands(image.select(bandName) \
          .multiply(ee.Image.constant(0.01)) \
          .rename('faparPercent'))

    # filter collection
    # add quality mask to collection and update mask after
    filteredCollection = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(scaleFapar(product, storedBandName))
      
    # print(filteredCollection.getInfo())
    current = filteredCollection.first()
    
    # standardize dataset
    anomaly = current.select('faparPercent').subtract(mean)
    standardizedResult = anomaly.divide(stdev).focal_mean()
      
    return standardizedResult

  elif product == products.modisEt:
    storedBandName = bandName
    if bandName == 'ETPET':
      bandName = 'ET'
    
    # Add ET/PET ratio band to ImageCollection
    def addEtPetRatioBand(image):
      return lambda image: image.addBands(image.select('ET_1')
          .divide(image.select('PET_1'))
          .rename('etPetRatio'))
  
    # Apply scale to Evapotranspiration data
    # ET data scale factor = 0.1
    def scaleET(image):
      # fAPAR data scale factor = 0.1
      return lambda image: image.addBands(image.select('ET_1') \
          .multiply(ee.Image.constant(0.1)) \
          .rename('ET_final'))
 
    # filter collection
    # add quality mask to collection and update mask after
    filteredCollection = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(scaleET(product)) \
      .map(addEtPetRatioBand(product))
      
  
    # print(filteredCollection.getInfo())
    current = filteredCollection.first() 
    # print(current.getInfo())
    
    if storedBandName == 'ET':
      # standardize dataset
      anomaly = current.select('ET_final').subtract(mean)
      standardizedResult = anomaly.divide(stdev).focal_mean()
    elif storedBandName == 'ETPET':
      # standardize dataset
      anomaly = current.select('etPetRatio').subtract(mean)
      standardizedResult = anomaly.divide(stdev).focal_mean()
    
    # print(standardizedResult.getInfo())
    return standardizedResult

  elif bandName == 'TVX' or bandName == 'TWX':
    # Use appropriate index
    index = 'NDVI'
    if bandName == 'TVX':
      index = 'NDVI'
    elif bandName == 'TWX':
      index = 'NDWI'
    
    # Add Celsius LST band to ImageCollection
    def addCelsiusBand(image):
      return lambda image: image.addBands(image.select('LST_Day_1km_1')
          .multiply(ee.Image.constant(0.02))
          .subtract(ee.Image.constant(273.15))
          .rename('LSTCelsius'))
    
    product = 'MODIS/006/MOD11A2'
      
    # filter collection
    filteredCollectionLST = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(addCelsiusBand(product))
  
    # print(filteredCollectionLST.getInfo())
    
    product = 'MODIS/006/MOD09A1'
    # filter collection
    filteredCollectionNDI = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(addNDVI(product)) \
      .map(addNDWI(product))
    
    # print(filteredCollectionNDI.getInfo())
    
    # Define an inner join
    innerJoin = ee.Join.inner()
    
    # Specify an equals filter for image timestamps
    # Join NDVI and LST collection images by the start_time field
    filterTimeEq = ee.Filter.equals(leftField = 'system:time_start', rightField = 'system:time_start')
    
    # Apply the join
    innerJoinedData = innerJoin.apply(filteredCollectionLST, filteredCollectionNDI, filterTimeEq)
    # print(innerJoinedData)
    
    # Concatenate images to create an ImageCollection
    innerJoinedData = innerJoinedData.map(lambda feature: ee.Image.cat(feature.get('primary'), feature.get('secondary')))
    
    # We need an explicit cast to ImageCollection so that GEE can understand the type to work with
    innerJoinedData = ee.ImageCollection(innerJoinedData)

    # print(innerJoinedData.getInfo())
    
    saveBandName = 'LST_' + str(index) + '_ratio'

    # Add LST/NDVI ratio band to ImageCollection
    def addLstNdiRatioBand(image, index, saveName):
      return lambda image: image.addBands(image.select('LSTCelsius')
          .divide(image.select(index))
          .rename(saveName))
    
    product = 'MODIS/006/MOD11A2'
    innerJoinedData = innerJoinedData.map(addLstNdiRatioBand(product, index, saveBandName))
    current = innerJoinedData.first() 

    # standardize dataset
    anomaly = current.select(saveBandName).subtract(mean)
    standardizedResult = anomaly.divide(stdev).focal_mean()
      
    return standardizedResult

   

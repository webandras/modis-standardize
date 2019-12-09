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
  elif product == products.modisTemp:
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
      .map(addMask(product, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(addCelsiusBand(product, bandName))
      
  
    print(filteredCollection.getInfo())
    
    mean = filteredCollection.select('LSTCelsius').mean().clip(studyArea)
    stdev = filteredCollection.select('LSTCelsius').reduce(ee.Reducer.stdDev()).clip(studyArea)
    
    saveRes = dict()
    saveRes['meanMap'] = mean
    saveRes['stdevMap'] = stdev
    print(saveRes.get('meanMap').getInfo())

    return saveRes
  elif product == products.modisFapar:
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
      .map(addMask(product, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(scaleFapar(product, bandName))
      
    print(filteredCollection.getInfo())
    
    mean = filteredCollection.select('faparPercent').mean().clip(studyArea)
    stdev = filteredCollection.select('faparPercent').reduce(ee.Reducer.stdDev()).clip(studyArea)
    
    saveRes = dict()
    saveRes['meanMap'] = mean
    saveRes['stdevMap'] = stdev
    print(saveRes.get('meanMap').getInfo())

    return saveRes
  elif product == products.modisEt:
    # Apply scale to Evapotranspiration data
    def scaleET(image, bandName):
      # fAPAR data scale factor = 0.01
      return lambda image: image.addBands(image.select(bandName) \
          .multiply(ee.Image.constant(0.1)) \
          .rename('ET_kg_m2'))
 
    # filter collection
    # add quality mask to collection and update mask after
    filteredCollection = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(scaleET(product, bandName))
      
    print(filteredCollection.getInfo())
    
    mean = filteredCollection.select('ET_kg_m2').mean().clip(studyArea)
    stdev = filteredCollection.select('ET_kg_m2').reduce(ee.Reducer.stdDev()).clip(studyArea)
    
    saveRes = dict()
    saveRes['meanMap'] = mean
    saveRes['stdevMap'] = stdev
    print(saveRes.get('meanMap').getInfo())
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
  
  elif product == products.modisTemp:
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
      .map(qualityMask(product, resolution, product, isItNight)) \
      .map(addCelsiusBand(product, bandName)) \
      
  
    print(filteredCollection.getInfo())
    current = filteredCollection.first()
    
    # standardize dataset
    anomaly = current.select('LSTCelsius').subtract(mean)
    standardizedResult = anomaly.divide(stdev).focal_mean()
      
    return standardizedResult

  elif product == products.modisFapar:
    print(bandName)
      
    # Apply scale to fAPAR data
    def scaleFapar(image, bandName):
      # fAPAR data scale factor = 0.01
      return lambda image: image.addBands(image.select(bandName) \
          .multiply(ee.Image.constant(1)) \
          .rename('faparPercent'))

    # filter collection
    # add quality mask to collection and update mask after
    filteredCollection = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(scaleFapar(product, bandName))
      
  
    print(filteredCollection.getInfo())

    current = filteredCollection.first()
    
    # standardize dataset
    anomaly = current.select('faparPercent').subtract(mean)
    standardizedResult = anomaly.divide(stdev).focal_mean()
      
    return standardizedResult
  elif product == products.modisEt:
    # Apply scale to Evapotranspiration data
    # // ET data scale factor = 0.01
    def scaleET(image, bandName):
      return lambda image: image.addBands(image.select(bandName) \
          .multiply(ee.Image.constant(0.1)) \
          .rename('ET_kg_m2'))

      
    # filter collection
    # add quality mask to collection and update mask after
    filteredCollection = ee.ImageCollection(product) \
      .filterBounds(point) \
      .filterDate(start, finish) \
      .filter(doyFilter) \
      .map(addMask(product, resolution, product, isItNight)) \
      .map(addMaskedData(product)) \
      .map(scaleET(product, bandName))
      
  
    print(filteredCollection.getInfo())

    current = filteredCollection.first()
      
    print(current.getInfo())
    
    # standardize dataset
    anomaly = current.select('ET_kg_m2').subtract(mean)
    standardizedResult = anomaly.divide(stdev).focal_mean()
      
    print(standardizedResult.getInfo())
      
    return standardizedResult



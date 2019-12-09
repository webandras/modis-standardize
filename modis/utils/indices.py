import ee
ee.Initialize()

# This function calculates spectral indices for MODIS
# Args:
# index - name of the index as string ('NDVI', 'EVI', 'NDWI', 'NDDI')
# image - an instance of ee.Image() class
def getSpectralIndex(index, image):
  if index == 'EVI': # Enhanced Vegetation Index
    return image.expression(
        '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
          'NIR': image.select('sur_refl_b02_1'),
          'RED': image.select('sur_refl_b01_1'),
          'BLUE': image.select('sur_refl_b03_1')
        })
  elif index == 'NDVI': # Normalized Difference Vegetation Index
    return image.normalizedDifference(['sur_refl_b02_1', 'sur_refl_b01_1']);

  elif index == 'NDWI': # Normalized Difference Water Index
    return image.normalizedDifference(['sur_refl_b02_1','sur_refl_b07_1']);

  elif index == 'NDDI': # Normalized Difference Drought Index
    # IMPORTANT: ndvi8 is the 8-day 500m NDVI
    return image.normalizedDifference(['ndvi', 'ndwi']);
  
  else:
    print('Error in "getSpectralIndex" function def')
    return -2



# Add spectral index band to ImageCollection
def addNDVI(image):
  # 8-day 500m NDVI
  return lambda image: image.addBands(getSpectralIndex('NDVI', image).rename('ndvi'));


# Add spectral index band to ImageCollection
def addNDWI(image):
  # 8-day 500m NDWI
  return lambda image: image.addBands(getSpectralIndex('NDWI', image).rename('ndwi'));


# Add spectral index band to ImageCollection
def addNDDI(image):
  # 8-day 500m NDWI
  return lambda image: image.addBands(getSpectralIndex('NDDI', image).rename('NDDI'));


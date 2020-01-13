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
          'NIR': image.select('sur_refl_b02'),
          'RED': image.select('sur_refl_b01'),
          'BLUE': image.select('sur_refl_b03')
        })
  elif index == 'NDVI': # Normalized Difference Vegetation Index
    return image.normalizedDifference(['sur_refl_b02', 'sur_refl_b01']);

  elif index == 'NDWI': # Normalized Difference Water Index
    return image.normalizedDifference(['sur_refl_b02','sur_refl_b07']);

  elif index == 'NDDI': # Normalized Difference Drought Index
    return image.normalizedDifference(['NDVI', 'NDWI']);
  
  else:
    print('Error in "getSpectralIndex" function def')
    return -2



# Add spectral index band to ImageCollection
def addNDVI(image):
  # 8-day 500m NDVI
  return lambda image: image.addBands(getSpectralIndex('NDVI', image).rename('NDVI'));


# Add spectral index band to ImageCollection
def addNDWI(image):
  # 8-day 500m NDWI
  return lambda image: image.addBands(getSpectralIndex('NDWI', image).rename('NDWI'));


# Add spectral index band to ImageCollection
def addNDDI(image):
  # 8-day 500m NDWI
  return lambda image: image.addBands(getSpectralIndex('NDDI', image).rename('NDDI'));


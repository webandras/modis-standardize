import ee
import math
# import modis data product ids
from modis.data.products import Products
products = Products()

ee.Initialize()


# Returns an image containing just the specified QA bits.
#
# Args:
#   image - The QA Image to get bits from.
#   start - The first bit position, 0-based.
#   end   - The last bit position, inclusive.
#   name  - A name for the output image.
#
def getQABits(image, start, end, newName):
  # Compute the bits we need to extract.
  # Here we get a pattern full of 1111...
  pattern = 0
  for i in range(start, end+1):
    pattern += math.pow(2, i)
      
  # print(pattern)
  # &, extracting bits from the QA band.
  # >>, for positioning in the bitfield.
  return image.select([0], [newName]).bitwiseAnd(pattern).rightShift(start)



# Function to obtain the quality mask from MODIS products
# If you change the conditions, you can apply it to any QA band of MODIS products.
# Args:
# ImageCollection name: string
# resolution: number
# night (is it night temperature?): boolean
def qualityMask(image, resolution, product, night):

  if product == products.modisRefl:  # Surface Reflectance
    # Extract 'QC' and 'StateQA' bands
    qualityControl = image.select('QA')
    state =  image.select('StateQA')
      
    # Where data quality is appropiate.
    cloudState = getQABits(state,0,1,"Cloud State")
    cloudShadow = getQABits(state,2,2,"Cloud Shadow")
     
    red = getQABits(qualityControl,2,5,"Band 1 QA")
    nir = getQABits(qualityControl,6,9,"Band 2 QA")
    swir = getQABits(qualityControl,26,29,"Band 7 QA")

    # Where data quality is appropiate.
    mask = cloudState.eq(0).And(cloudShadow.eq(0)).And(red.eq(0)).And(nir.eq(0)).And(swir.eq(0))

  elif product == products.modisTemp:  # Surface Temperature
    if night == True:
      # Extract QC band
      qualityControl = image.select('QC_Day')
    
    elif night == False:
      # Extract QC band
      qualityControl = image.select('QC_Night')
    else:
      print('"night" argument type error: only Boolean values accepted. :(')
      return -1
      
    # Where data quality is appropiate.
    qaFlag = getQABits(qualityControl,0,1,"QA Flag").eq(0)
    dataQuality = getQABits(qualityControl,2,3,"Data Quality").eq(0)
    lstError = getQABits(qualityControl,15,15,"LST error").lte(1)
    
    # Where data quality is appropiate.
    mask = qaFlag.And(dataQuality).And(lstError)
    
  elif product == products.modisEt: # Evapotranspiration data
    # Extract QC band
    qualityControl = image.select('ET_QC')
   
    # Where data quality is appropiate.
    modlandQCBits = getQABits(qualityControl, 0, 0, 'MODLAND_QC bits').eq(0)
    sensor = getQABits(qualityControl, 1, 1,'Sensor').eq(0)
    cloudStateF = getQABits(qualityControl, 3, 4,"Cloud State").eq(0)
    scf_qc = getQABits(qualityControl, 5, 7,"SCF_QC").lte(1)
    
    # Where data quality is appropiate.
    mask = modlandQCBits.And(sensor).And(cloudStateF).And(scf_qc)
  
  elif product == products.modisFpar: # fAPAR data
    # Extract QA band
    qualityControl = image.select('FparLai_QC')
   
    # Where data quality is appropiate.
    modlandQCBits = getQABits(qualityControl, 0, 0, 'MODLAND_QC bits').eq(0)
    sensor = getQABits(qualityControl, 1, 1,'Sensor').eq(0)
    cloudStateF = getQABits(qualityControl, 3, 4,"Cloud State").eq(0)
    scf_qc = getQABits(qualityControl, 5, 7,"SCF_QC").lte(1)
    
    # Where data quality is appropiate.
    mask = modlandQCBits.And(sensor).And(cloudStateF).And(scf_qc)

  else:
    print('Error in def qualityMask function')
    return -2

  
  # Returns the mask, 1 = good quality, 0 = bad quality
  return mask



# Adds a mask layer named 'QA_mask' to the properties of a collection
def addMask(image, resolution, product, night):
  return lambda image: image.addBands(qualityMask(image, resolution, product, night).rename('QA_mask'))


# Uses the mask on the properties of the ImageCollection
def addMaskedData(image):
  return lambda image: image.addBands(image.updateMask(image.select('QA_mask')))



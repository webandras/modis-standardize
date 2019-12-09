# MODIS data processing package for drought monitoring
## Made by using Google Earth Engine Python API

! This is an ongoing project, will be update in the future !

This package applies cloud masking (for every dataset, with the appropriate quality assessment bands), and then calculates standardized 8-day composite images (reference period: 2000-2017) and saves them to Google Drive automatically.

The following MODIS products are included (MODIS Collection 6):
* Surface Reflectance 8-day 500m: 'MODIS/006/MOD09A1'
* Surface Temperature 8-day 1000m: 'MODIS/006/MOD11A2'
* fAPAR 4-day 500m: 'MODIS/006/MCD15A3H'
* Evapotranspiration 8-day 500m: 'MODIS/006/MOD16A2'

Currently, you can only calculate NDDI, NDVI and NDDI indices from surface reflectance data. The others are not tested and not ready yet.

You can change the study area if you want.

## Instructions

### Install Conda and GEE Python API, set up Visual Studio Code

1. Clone the repository
2. You need to have Python installed on your computer. I have Python 3.6 installed.
2. Install Miniconda3. [Download installer here](https://docs.conda.io/en/latest/miniconda.html).
3. Run 'Anaconda Powershell Prompt (Miniconda3)'
4. Follow Google instructions: https://developers.google.com/earth-engine/python_install-conda.html#install_api (Skip the conda activation part - it is already activated with the installation)
5. I am using Visual Studio Code for development with the 'Python Extension Pack' (by Don Jayamanne) extension installed.
6. You need to have a '.vscode' folder in the root of your repo, having a 'settings.json' file in it (with your path to your 'ee' environment):

```
{
  "python.pythonPath": "C:\\Users\\Guland\\Miniconda3\\envs\\ee\\python.exe"
}
````

Conda and GEE documentation pages:
https://conda.io/projects/conda/en/latest/user-guide/install/index.html
https://developers.google.com/earth-engine/python_install-conda.html


### Run package
The main script to run is: 'app.py' in the root of 'modis' folder. Check it out and modify it.

1. Activate ee environment in 'Anaconda Powershell Prompt (Miniconda3)':
`conda activate ee`
2. Navigate to your folder and open VSCode:
`code .`
3. And run package with Python:
`python -m modis`







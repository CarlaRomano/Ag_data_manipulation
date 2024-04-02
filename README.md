1. Script_Crop_Acres_CR.R

R script to calculate acreages for several crops using CropScape and a specific shapefile. 

It calls the following libraries:
library(CropScapeR)
library (sf)
library(raster)
library(httr)

Download CropScape following instructions of this link: https://www.rdocumentation.org/packages/CropScapeR/versions/1.1.5

References: 
[1] Boryan, Claire, Zhengwei Yang, Rick Mueller, and Mike Craig. 2011. Monitoring US Agriculture: The US Department of Agriculture, National Agricultural Statistics Service, Cropland Data Layer Program. Geocarto International 26 (5): 341–58. https://doi.org/10.1080/10106049.2011.562309.
[2] Han, Weiguo, Zhengwei Yang, Liping Di, and Richard Mueller. 2012. CropScape: A Web Service Based Application for Exploring and Disseminating US Conterminous Geospatial Cropland Data Products for Decision Support. Computers and Electronics in Agriculture 84 (June): 111–23. https://doi.org/10.1016/j.compag.2012.03.005.

2. 

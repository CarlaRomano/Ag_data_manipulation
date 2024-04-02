library(CropScapeR)
library (sf)
library(raster)
library(httr)
# Set a global timeout option for all HTTP requests (in milliseconds)
httr::timeout(600000)
master_dataframe <- data.frame()
##Select crop IDs
ids <- c(1, 36, 5, 24, 42,12,43,53)
crops <- c("Corn", "Alfa alfa", "Soybeans", "Winter wheat", "Dry Beans","Sweet corn","Potatoes","Peas")
##Set working directory
setwd("M://Neonicotinoids//GW_REVIEW//GIS//Buffer_1km_det")
##Call file with the WUWNs and year of sampling
wuwn_year<- read.csv("Neonics_gw_data_STATIONS_year_REDO.csv")
##Year 2023 is not currently available in CropScape
wuwn_year <- wuwn_year[wuwn_year$year != 2023, ]
##List all the shapefile in the working directory
myFiles <- list.files(pattern = "\\.shp$")
for(i in myFiles){
  spdata <- sf::st_read(i)
  WUWN<- gsub("\"|\\.shp", "", i)
  filtered_data <- spdata[spdata$WUWN == WUWN, ]
  dissolved_data <- st_union(filtered_data)
  plot(dissolved_data)
  filtered_wuwn_year <- wuwn_year[wuwn_year$WUWN == WUWN, ]
  ##Select year based on the excel file called 
  years <- filtered_wuwn_year$year
  ##Call CropScape. PLEASE CHANGE CRS accordingly based on the coordinate system of your shapefile. Epsg 4326 is WGS84
  for (y in years){
    data <- GetCDLData(aoi = sf::st_bbox(dissolved_data), crs='+init=epsg:4326', year = y, type = 'b')
    spdata2<- st_transform(dissolved_data, crs = proj4string(data))
    spdata2_sp <- as(spdata2, "Spatial")
    data_shape <- raster::mask(data, spdata2_sp)
    if (!is.factor(data_shape)) {
      data_shape <- as.factor(data_shape)
    }
    for (j in seq_along(ids)) {
      target_class <- ids[j] 
      binary_raster <- data_shape == target_class
      pixel_count <- sum(binary_raster[], na.rm = TRUE)
      ##change pixel count to area in acres
      area<-pixel_count*0.22
      df <- data.frame("WUWN" = numeric(),"Crop ID" = numeric(),"Crop name" = character(),"Year" = numeric(),"Pixel count"=numeric(),"Acreage"=numeric())
      new_row <- data.frame("WUWN" = WUWN, "Crop ID" = ids[j],"Crop name"=crops[j], "Year"=y,"Pixel count"=pixel_count, "Acreage"=area)
      df2 <- rbind(df, new_row)
      master_dataframe <- rbind(master_dataframe, df2)
      ##name of final csv file
      csv_file <- "final_crop_WUWN_det.csv"
      if (file.exists(csv_file)) {
        # If the file exists, delete it
        file.remove(csv_file)
      }
      # Save the dataframe as a CSV file
      write.csv(master_dataframe, file = csv_file, row.names = FALSE)
    }
  }
}


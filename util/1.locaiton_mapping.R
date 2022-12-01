library(tidyverse)
library(stringr)
library(vegan)
library(zipcodeR)
library(readxl)
library(fastDummies)
library(data.table)
library(caret)
library(recipes)

base_path <- getwd()
setwd(paste0(base_path, "/data/input_data"))


## Zip Code Location Mapping

# only including the desired states
states <- c('VA', 'DC', 'WV', 'MD', 'NC', 'SC', 'GA', 'FL')

# mapping the cbsa code to a name
cbsa_name <- read.csv("cbsa_name.csv") ##https://www.nber.org/research/data/census-core-based-statistical-area-cbsa-federal-information-processing-series-fips-county-crosswalk
cbsa_name <- cbsa_name[,c(1,4)]
cbsa_name$cbsacode <- as.character(cbsa_name$cbsacode)
cbsa_name <- cbsa_name[!duplicated(cbsa_name), ]

cbsa_zip <- read_excel("CBSA_ZIP_122021.xlsx") ##https://www.huduser.gov/portal/datasets/usps_crosswalk.html
cbsa_zip <- cbsa_zip[,c(1,2)]
cbsa_zip <- left_join(cbsa_zip, cbsa_name, by=c("cbsa"="cbsacode"))
cbsa_zip <- cbsa_zip[!duplicated(cbsa_zip), ]
cbsa_zip <- cbsa_zip[,c(2,1,3)]
cbsa_zip <- cbsa_zip %>% filter(!is.na(cbsatitle))

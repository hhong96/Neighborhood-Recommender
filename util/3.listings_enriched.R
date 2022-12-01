## Listings Data Enrichment

listings_enriched <- listings

# mapping the zipcodes to CBSAs
listings_enriched  <- left_join(listings,  cbsa_zip, by = c('zipcode' = 'zip'))
listings_enriched <- listings_enriched %>% filter(!is.na(cbsa) & cbsa != '')

# excluding any CBSAs with less than 1000 listings
count_of_cbsa <- listings_enriched %>% group_by(cbsa) %>% summarise(total_count=n()) %>% arrange(total_count) %>% filter(total_count > 1000)
cbsa_to_keep <- unique(count_of_cbsa$cbsa)
listings_enriched <- listings_enriched %>% filter(cbsa %in% cbsa_to_keep)

# excluding any zipcodes with less than 100 listings
zipcode_count <- listings_enriched %>% group_by(zipcode) %>% summarise(total_count=n()) %>% arrange(total_count) %>% filter(total_count > 100)
zipcode_to_keep <- unique(zipcode_count$zipcode)
listings_enriched <- listings_enriched %>% filter(zipcode %in% zipcode_to_keep)

zipcodes_per_cbsa <- listings_enriched %>% group_by(cbsa) %>% summarise(total_count=n_distinct(zipcode)) %>% arrange(total_count)


cbsas <- c(unique(listings_enriched$cbsa))
cbsa_columns <- c("cbsa", "cbsatitle")
all_unique_cbsas <- listings_enriched[,which(names(listings_enriched) %in% cbsa_columns)]
all_unique_cbsas <- all_unique_cbsas[!duplicated(all_unique_cbsas),]

zip_codes <- c(unique(listings_enriched$zipcode))
cbsa_zip_columns <- c("cbsa", "zipcode")
all_cbsa_zipcodes <- listings_enriched[,which(names(listings_enriched) %in% cbsa_zip_columns)]
all_cbsa_zipcodes <- all_cbsa_zipcodes[!duplicated(all_cbsa_zipcodes),]


missing_data_columns <- c(colnames(listings_enriched)[colSums(is.na(listings_enriched)) > 0])
missing_data_columns
listings_enriched[missing_data_columns] <- sapply(listings_enriched[missing_data_columns],as.numeric)

# imputing missing values based on median values at the house type, zipcode level
house_type_zip <- c('SqFt', 'bedrooms', 'bathrooms', 'parkingTotalSpaces', 'Stories', 'yearBuilt')
zip_only <- c('elemntarySchoolRating', 'middleSchoolRating', 'highSchoolRating')

house_type_zip_agg <- listings_enriched %>% 
                      select(house_type_zip, zipcode, homeType) %>%
                      group_by(zipcode, homeType) %>%
                      summarise_all(funs(median), na.rm = TRUE)
house_type_zip_agg_colnames <- c('house_type_zip_median_SqFt', 
                                 'house_type_zip_median_bedrooms',
                                 'house_type_zip_median_bathrooms',
                                 'house_type_zip_median_park', 
                                 'house_type_zip_median_stories', 
                                 'house_type_zip_median_year')
colnames(house_type_zip_agg)[3:8] <- house_type_zip_agg_colnames

# imputing missing values based on median values at the house type, cbsa level
house_type_cbsa_agg <- listings_enriched %>% 
                      select(house_type_zip, cbsa, homeType) %>%
                      group_by(cbsa, homeType) %>%
                      summarise_all(funs(median), na.rm = TRUE)
house_type_cbsa_agg_colnames <- c('house_type_cbsa_median_SqFt', 
                                     'house_type_cbsa_median_bedrooms', 
                                     'house_type_cbsa_median_bathrooms',
                                     'house_type_cbsa_median_park', 
                                     'house_type_cbsa_median_stories', 
                                     'house_type_cbsa_median_year')
colnames(house_type_cbsa_agg)[3:8] <- house_type_cbsa_agg_colnames

# imputing missing values based on median values at the zipcode level
zip_agg <- listings_enriched %>% 
                      select(zip_only, zipcode) %>%
                      group_by(zipcode) %>%
                      summarise_all(funs(median), na.rm = TRUE)
zip_agg_colnames <- c('zip_median_elemntary', 
                      'zip_median_middle', 
                      'zip_median_high')
colnames(zip_agg)[2:4] <- zip_agg_colnames

# imputing missing values based on median values at the cbsa level
cbsa_agg <- listings_enriched %>% 
              select(zip_only, cbsa) %>%
              group_by(cbsa) %>%
              summarise_all(funs(median), na.rm = TRUE)
cbsa_agg_colnames <- c('cbsa_median_elemntary', 
                         'cbsa_median_middle', 
                         'cbsa_median_high')
colnames(cbsa_agg)[2:4] <- cbsa_agg_colnames

listings_enriched  <- left_join(listings_enriched,  house_type_zip_agg, by = c('zipcode', 'homeType'))
listings_enriched  <- left_join(listings_enriched,  house_type_cbsa_agg, by = c('cbsa', 'homeType'))
listings_enriched  <- left_join(listings_enriched,  zip_agg, by = c('zipcode'))
listings_enriched  <- left_join(listings_enriched,  cbsa_agg, by = c('cbsa'))

listings_enriched <- listings_enriched %>%
                     mutate(SqFt_final = if_else(!is.na(SqFt), SqFt,
                                         if_else(!is.na(house_type_zip_median_SqFt), house_type_zip_median_SqFt,
                                         if_else(!is.na(house_type_cbsa_median_SqFt), house_type_cbsa_median_SqFt, 0))),
                            bedrooms_final = if_else(!is.na(bedrooms), bedrooms,
                                         if_else(!is.na(house_type_zip_median_bedrooms), house_type_zip_median_bedrooms,
                                         if_else(!is.na(house_type_cbsa_median_bedrooms), house_type_cbsa_median_bedrooms, 0))),
                            bathrooms_final = if_else(!is.na(bathrooms), bathrooms,
                                         if_else(!is.na(house_type_zip_median_bathrooms), house_type_zip_median_bathrooms,
                                         if_else(!is.na(house_type_cbsa_median_bathrooms), house_type_cbsa_median_bathrooms, 0))),
                            parking_final = if_else(!is.na(parkingTotalSpaces), parkingTotalSpaces,
                                         if_else(!is.na(house_type_zip_median_park), house_type_zip_median_park,
                                         if_else(!is.na(house_type_cbsa_median_park), house_type_cbsa_median_park, 0))),
                            stories_final = if_else(!is.na(Stories), Stories,
                                         if_else(!is.na(house_type_zip_median_stories), house_type_zip_median_stories,
                                         if_else(!is.na(house_type_cbsa_median_stories), house_type_cbsa_median_stories, 0))),
                            year_built_final = if_else(!is.na(yearBuilt), yearBuilt,
                                         if_else(!is.na(house_type_zip_median_year), house_type_zip_median_year,
                                         if_else(!is.na(house_type_cbsa_median_year), house_type_cbsa_median_year, 0))),
                            elemntary_rating_final = if_else(!is.na(elemntarySchoolRating), elemntarySchoolRating,
                                         if_else(!is.na(zip_median_elemntary), zip_median_elemntary,
                                         if_else(!is.na(cbsa_median_elemntary), cbsa_median_elemntary, 0))),
                            middle_rating_final = if_else(!is.na(middleSchoolRating), middleSchoolRating,
                                         if_else(!is.na(zip_median_middle), zip_median_middle,
                                         if_else(!is.na(cbsa_median_middle), cbsa_median_middle, 0))),
                            high_rating_final = if_else(!is.na(highSchoolRating), highSchoolRating,
                                         if_else(!is.na(zip_median_high), zip_median_high,
                                         if_else(!is.na(cbsa_median_high), cbsa_median_high, 0)))
                            )


to_drop <- c(house_type_zip, zip_only, house_type_zip_agg_colnames, house_type_cbsa_agg_colnames, 
             zip_agg_colnames, cbsa_agg_colnames)
listings_enriched <- listings_enriched[ , -which(names(listings_enriched) %in% to_drop)]


## Checking all fields have values - no NA
na_count_listings_enriched <-sapply(listings_enriched, function(y) sum(length(which(is.na(y)))))
na_count_listings_enriched <- data.frame(na_count_listings_enriched)
na_count_listings_enriched


zipcode_level_detail_columns <- c('cbsa', 'zipcode', 'price', 'SqFt_final', 'bedrooms_final', 'bathrooms_final', 'parking_final', 'stories_final', 'year_built_final')
zipcode_level_listing_detail <- listings_enriched %>% select(zipcode_level_detail_columns) %>% group_by(cbsa, zipcode) %>% summarise_all(funs(median), na.rm = TRUE)
setwd(paste0(base_path, "/data/output_data"))
write.csv(zipcode_level_listing_detail, "zipcode_level_listing_detail.csv", row.names = FALSE)

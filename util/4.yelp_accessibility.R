setwd(paste0(base_path, "/data/input_data"))

## Yelp Data

yelp <- read.csv('yelp.csv')
yelp <- yelp[,-1]
yelp$zipcode <- as.character(yelp$zipcode)

yelp_enriched <- yelp
yelp_enriched  <- left_join(all_cbsa_zipcodes,  yelp_enriched, by="zipcode")

na_count_yelp <-sapply(yelp_enriched, function(y) sum(length(which(is.na(y)))))
na_count_yelp <- data.frame(na_count_yelp)
na_count_yelp

listings_enriched <- left_join(listings_enriched, yelp_enriched, by = c("zipcode" = "zipcode", "cbsa" = "cbsa"))

## Accessibility Data 

accessibility_raw <- read.csv('accessibility.csv')
accessibility_raw <- accessibility_raw[,-1]
accessibility_raw$cbsa <- as.character(accessibility_raw$cbsa)

accessibility_enriched <- left_join(all_cbsa_zipcodes, accessibility_raw, cbsa_zip, by="cbsa") ## expand to all zipcodes in cbsa
accessibility_enriched <- accessibility_enriched[,-c(5,6)]
accessibility_enriched <- accessibility_enriched %>% group_by(cbsa,zipcode) %>%
                                                     summarise_all(funs(max))
na_count_accessibility <-sapply(accessibility_enriched, function(y) sum(length(which(is.na(y)))))
na_count_accessibility <- data.frame(na_count_accessibility)
na_count_accessibility

listings_enriched <- left_join(listings_enriched, accessibility_enriched, by = c("zipcode" = "zipcode", "cbsa" = "cbsa"))


setwd(paste0(base_path, "/data/output_data"))
write.csv(yelp_enriched, "yelp_enriched.csv", row.names = FALSE)
write.csv(accessibility_enriched, "accessibility_enriched.csv", row.names = FALSE)

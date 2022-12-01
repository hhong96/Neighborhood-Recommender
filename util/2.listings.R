## Listings Data

# read in the two listing files
listings_raw_before_10.13 <- read.csv(file='listings_all/listings_before_10.13.csv')
listings_raw_10.13_to_11.2 <- read.csv(file='listings_all/listings_10.13_to_11.2.csv')
listings_raw <- rbind(listings_raw_before_10.13, listings_raw_10.13_to_11.2)

# extracting price for tracking price change over the last three months
listing_price_columns_keep <- c("zipcode", "zpid", "price", "createdAt")
listings_price_change <- listings_raw[,listing_price_columns_keep]
  
#only keeping zip codes within the desired states and removing duplictaed records
listings <- listings_raw %>% filter(!is.na(zipcode) & !grepl("^[A-Za-z]", zipcode) & state %in% states & !is.na(county))
listings <- listings %>% arrange(zpid, desc(createdAt)) %>% filter(!duplicated(zpid))

listing_columns_keep <- c("zpid", "zipcode", "homeType", "price", "SqFt", "bedrooms", "bathrooms", "parkingTotalSpaces", 
                          "Stories", "yearBuilt", "elemntarySchoolRating", "middleSchoolRating", "highSchoolRating")
listings <- listings[,listing_columns_keep]

# transforming outliers and blank values to NA in order to impute later
listings[listings == 'NULL' | is.na(listings)] <- NA

listings$bedrooms <- as.integer(listings$bedrooms)
listings[, "bedrooms"][listings[, "bedrooms"] == 0 | listings[, "bedrooms"] > 7] <- NA

listings$bathrooms <- as.integer(listings$bathrooms)
listings[, "bathrooms"][listings[, "bathrooms"] == 0 | listings[, "bathrooms"] > 7] <- NA

listings$Stories <- as.integer(listings$Stories)
listings[, "Stories"][listings[, "Stories"] == 0 | listings[, "Stories"] > 5] <- NA

listings$yearBuilt <- as.integer(listings$yearBuilt)
listings[, "yearBuilt"][listings[, "yearBuilt"] < 1900 | listings[, "yearBuilt"] > 2022] <- NA

listings$SqFt <- as.integer(listings$SqFt)
listings[, "SqFt"][listings[, "SqFt"] < 200 | listings[, "SqFt"] > 8000] <- NA

listings$parkingTotalSpaces <- as.integer(listings$parkingTotalSpaces)
listings[, "parkingTotalSpaces"][listings[, "parkingTotalSpaces"] > 10] <- NA

listings$homeType <- as.factor(listings$homeType)
listings$zipcode <- as.character(listings$zipcode)
listings$elemntarySchoolRating <- as.integer(listings$elemntarySchoolRating)
listings$middleSchoolRating <- as.integer(listings$middleSchoolRating)
listings$highSchoolRating <- as.integer(listings$highSchoolRating)

listings <- listings %>% filter(price > 10000 & price <= 10000000)


summary(listings)


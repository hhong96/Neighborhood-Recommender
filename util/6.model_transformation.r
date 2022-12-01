## Creating dummy variables for model inputs
listings_enriched_model <- listings_enriched

## Creating dummy variables with user facing labels for Income Buckets
listings_enriched_model$majority_income_dummy <- if_else(listings_enriched_model$majority_income_final == 'income_under_25k', 1, 
                                 if_else(listings_enriched_model$majority_income_final == 'income_between_25k_50k', 2,
                                 if_else(listings_enriched_model$majority_income_final == 'income_between_50k_100k', 3,
                                 if_else(listings_enriched_model$majority_income_final == 'income_between_100k_200k', 4, 5))))
majority_income_columns <- c('majority_income_dummy','majority_income_final')
majority_income_bucket_map <- listings_enriched_model[,which(names(listings_enriched_model) %in% majority_income_columns)]
majority_income_bucket_map <- majority_income_bucket_map[!duplicated(majority_income_bucket_map),]
majority_income_bucket_map[, "majority_income_final"][majority_income_bucket_map[, "majority_income_final"] == "income_under_25k"] <- "Less than $25k"
majority_income_bucket_map[, "majority_income_final"][majority_income_bucket_map[, "majority_income_final"] == "income_between_25k_50k"] <- "Between $25k and $50k"
majority_income_bucket_map[, "majority_income_final"][majority_income_bucket_map[, "majority_income_final"] == "income_between_50k_100k"] <- "Between $50k and $100k"
majority_income_bucket_map[, "majority_income_final"][majority_income_bucket_map[, "majority_income_final"] == "income_between_100k_200k"] <- "Between $100k and $200k"
majority_income_bucket_map[, "majority_income_final"][majority_income_bucket_map[, "majority_income_final"] == "income_over_200k"] <- "Greater than $200k"


## Creating dummy variables with user facing labels for Education Buckets
listings_enriched_model$majority_education_dummy <- if_else(listings_enriched_model$majority_education_final == 'population_no_diploma', 1, 
                                    if_else(listings_enriched_model$majority_education_final == 'population_high_school_diploma', 2,
                                    if_else(listings_enriched_model$majority_education_final == 'population_associates_or_equivelant', 3,
                                    if_else(listings_enriched_model$majority_education_final == 'population_bachelors', 4, 5))))
majority_education_columns <- c('majority_education_dummy','majority_education_final')
majority_education_bucket_map <- listings_enriched_model[,which(names(listings_enriched_model) %in% majority_education_columns)]
majority_education_bucket_map <- majority_education_bucket_map[!duplicated(majority_education_bucket_map),]
majority_education_bucket_map[, "majority_education_final"][majority_education_bucket_map[, "majority_education_final"] == "population_no_diploma"] <- "No Diploma"
majority_education_bucket_map[, "majority_education_final"][majority_education_bucket_map[, "majority_education_final"] == "population_high_school_diploma"] <- "High School Diploma"
majority_education_bucket_map[, "majority_education_final"][majority_education_bucket_map[, "majority_education_final"] == "population_associates_or_equivelant"] <- "Associates or Equivelant"
majority_education_bucket_map[, "majority_education_final"][majority_education_bucket_map[, "majority_education_final"] == "population_bachelors"] <- "Bachelors"
majority_education_bucket_map[, "majority_education_final"][majority_education_bucket_map[, "majority_education_final"] == "population_graduate"] <- "Graduate or Higher"

listings_enriched_model$hometype_dummy <- if_else(listings_enriched_model$homeType == 'SINGLE_FAMILY', 1, if_else(listings_enriched_model$homeType == 'CONDO', 2, 3))

listings_enriched_model$family_type_dummy <- if_else(listings_enriched_model$percent_family_households_final > .5, 1, 0)

listings_enriched_model$bedroom_bucket_dummy <- if_else(listings_enriched_model$bedrooms_final <= 2, 1, 
                                                if_else(listings_enriched_model$bedrooms_final <=5, 2, 3))

listings_enriched_model$bathrooms_bucket_dummy <- if_else(listings_enriched_model$bathrooms_final == 1, 1, 
                                                  if_else(listings_enriched_model$bathrooms_final == 2, 2, 3))

### less_than_1500, between_1500_and_3000, greater_than_3000
listings_enriched_model$sqft_buckets_dummy <- if_else(listings_enriched_model$SqFt_final <= 1500, 1, 
                                              if_else(listings_enriched_model$SqFt_final <= 3000, 2, 3))

### new_construction_within_last_two_years, between_two_to_five_years, between_five_to_fifteen_years,older_than_15_years
listings_enriched_model$yearbuilt_buckets_dummy <- if_else(listings_enriched_model$year_built_final >= as.integer(format(Sys.Date(), "%Y")) - 2, 1, 
                                                   if_else(listings_enriched_model$year_built_final >= as.integer(format(Sys.Date(), "%Y")) - 5, 2,
                                                   if_else(listings_enriched_model$year_built_final >= as.integer(format(Sys.Date(), "%Y")) - 15, 3, 4)))

## 1 to 4 scale - 1 being least important
listings_enriched_model$overall_education_score <- rowMeans(listings_enriched_model[13:15])
listings_enriched_model$overall_education_score_dummy <- if_else(listings_enriched_model$overall_education_score <= 3, 1, 
                                                         if_else(listings_enriched_model$overall_education_score <= 5, 2,
                                                         if_else(listings_enriched_model$overall_education_score <= 6, 3, 4)))

## Creating dummy variables with user facing labels for Home Price Buckets
listings_enriched_model$price_bucket <- NA
listings_enriched_model$price_dummy <- NA
for (i in cbsas) {
  
  price_q <- listings_enriched_model %>% filter(cbsa == i) %>% select("price") 
  price_quantiles <- quantile(price_q$price, probs = c(.25, .5, .75))
  
  listings_enriched_model[(listings_enriched_model$cbsa == i),]$price_bucket <- if_else(listings_enriched_model[(listings_enriched_model$cbsa == i),]$price <= price_quantiles[1], str_c("Less than $",price_quantiles[1]), 
                                                                                if_else(listings_enriched_model[(listings_enriched_model$cbsa == i),]$price <= price_quantiles[2], str_c("Between $",price_quantiles[1]+1," and $",price_quantiles[2]),
                                                                                if_else(listings_enriched_model[(listings_enriched_model$cbsa == i),]$price <= price_quantiles[3], str_c("Between $",price_quantiles[2]+1," and $",price_quantiles[3]),
                                                                                str_c("$",price_quantiles[3]+1,"+"))))
  
  listings_enriched_model[(listings_enriched_model$cbsa == i),]$price_dummy <- if_else(listings_enriched_model[(listings_enriched_model$cbsa == i),]$price <= price_quantiles[1], 1, 
                                                                               if_else(listings_enriched_model[(listings_enriched_model$cbsa == i),]$price <= price_quantiles[2], 2,
                                                                               if_else(listings_enriched_model[(listings_enriched_model$cbsa == i),]$price <= price_quantiles[3], 3, 4)))
}
price_columns <- c('cbsa', 'price_dummy','price_bucket')
price_bucket_map <- listings_enriched_model[,which(names(listings_enriched_model) %in% price_columns)]
price_bucket_map <- price_bucket_map[!duplicated(price_bucket_map),]

## Creating dummy variables with user facing labels for Age Group Buckets
listings_enriched_model$median_age_bucket <- NA
listings_enriched_model$median_age_dummy <- NA
for (i in cbsas) {
  
  if (i == "23580") {
    first <- 35
    second <- 37
    third <- 39
  } else if (i == "22180") {
    first <- 36
    second <- 38
    third <- 41
  } else if (i == "45540") {
    first <- 53
    second <- 67
    third <- 70
  } else {
    median_age_q <- listings_enriched_model %>% filter(cbsa == i) %>% select("median_age_final") 
    median_age_quantiles <- quantile(median_age_q$median_age_final, probs = c(.25, .5, .75))
    first <- median_age_quantiles[1]
    second <- median_age_quantiles[2]
    third <- median_age_quantiles[3]
  }
  
  listings_enriched_model[(listings_enriched_model$cbsa == i),]$median_age_bucket <- if_else(listings_enriched_model[(listings_enriched_model$cbsa == i),]$median_age_final <= first, str_c("Less than ",first), 
                                                                                if_else(listings_enriched_model[(listings_enriched_model$cbsa == i),]$median_age_final <= second, str_c("Between ",first+1," and ",second),
                                                                                if_else(listings_enriched_model[(listings_enriched_model$cbsa == i),]$median_age_final <= third, str_c("Between ",second+1," and ",third),
                                                                                str_c(third+1,"+"))))
  
  listings_enriched_model[(listings_enriched_model$cbsa == i),]$median_age_dummy <- if_else(listings_enriched_model[(listings_enriched_model$cbsa == i),]$median_age_final <= first, 1, 
                                                                               if_else(listings_enriched_model[(listings_enriched_model$cbsa == i),]$median_age_final <= second, 2,
                                                                               if_else(listings_enriched_model[(listings_enriched_model$cbsa == i),]$median_age_final <= third, 3, 4)))
}
median_age_columns <- c('cbsa', 'median_age_dummy','median_age_bucket')
median_age_bucket_map <- listings_enriched_model[,which(names(listings_enriched_model) %in% median_age_columns)]
median_age_bucket_map <- median_age_bucket_map[!duplicated(median_age_bucket_map),]


## 1 to 4 scale - 1 being least important
listings_enriched_model$centrality_index_dummy <- if_else(listings_enriched_model$regional_centrality_index <= .35, 1, 
                                                  if_else(listings_enriched_model$regional_centrality_index <= .4, 2,
                                                  if_else(listings_enriched_model$regional_centrality_index <= .45, 3, 4)))


listings_enriched_model$zipcode <- as.character(listings_enriched_model$zipcode)

## Checking all fields have values - no NA
na_count_full <-sapply(listings_enriched_model, function(y) sum(length(which(is.na(y)))))
na_count_full <- data.frame(na_count_full)
na_count_full


write.csv(listings_enriched_model, "listings_enriched_model.csv", row.names = FALSE)
write.csv(price_bucket_map, "mapping_price.csv", row.names = FALSE)
write.csv(median_age_bucket_map, "mapping_age.csv", row.names = FALSE)

  
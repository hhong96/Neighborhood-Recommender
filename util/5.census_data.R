## Census Data

setwd(paste0(base_path, "/data/input_data"))
years <- c('2020', '2019', '2018', '2017', '2016')

## DP05 FILES

dp05_columns_csv <-  read.csv(file='DP05-Columns.csv', skip=1)
colnames(dp05_columns_csv) <- c("value","value2","label")
dp05_columns_keep <- c(dp05_columns_csv$value)
dp05_columns_keep_16 <- c(dp05_columns_csv$value2)

for (i in years) {
  path <- paste('census_all/ACSDP5Y',i,'.DP05-Data.csv', sep='')
  print(path)
  if (i == '2020') {
    dp05 <- read.csv(file = path)
    dp05 <- dp05[, dp05_columns_keep]
    dp05$year <- i
  } else if (i == '2016') {
    dp05_to_append <- read.csv(file = path)
    dp05_to_append <- dp05_to_append[-1,]
    dp05_to_append <- dp05_to_append[, dp05_columns_keep_16]
    colnames(dp05_to_append) <- dp05_columns_keep
    dp05_to_append$year <- i
    dp05 <- rbind(dp05, dp05_to_append)
  } else {
    dp05_to_append <- read.csv(file = path)
    dp05_to_append <- dp05_to_append[-1,]
    dp05_to_append <- dp05_to_append[, dp05_columns_keep]
    dp05_to_append$year <- i
    dp05 <- rbind(dp05, dp05_to_append)
  }
}

dp05 <- dp05 %>% separate(NAME, c(NA, "zipcode"), extra="drop")
colnames(dp05) <- dp05[1,]
dp05 <- dp05[-1, ]
dp05 <- dp05 %>% filter(Area %in% zip_codes)
colnames(dp05)[colnames(dp05) == '2020'] <- 'year'
dp05[dp05 == '-' | dp05 == 'N' | is.na(dp05)] <- '0'
dp05 <- dp05 %>% mutate_all(as.integer)

dp05$percent_male <- dp05$`Estimate!!SEX AND AGE!!Total population!!18 years and over!!Male` / dp05$`Estimate!!SEX AND AGE!!Total population!!18 years and over`
dp05$percent_female <- dp05$`Estimate!!SEX AND AGE!!Total population!!18 years and over!!Female` / dp05$`Estimate!!SEX AND AGE!!Total population!!18 years and over`

dp05$ages_19_and_under <-rowSums(dp05[,3:6])
dp05$ages_20_to_34 <-rowSums(dp05[,7:8])
dp05$ages_35_to_54 <-rowSums(dp05[,9:10])
dp05$ages_55_plus <-rowSums(dp05[,11:15])
dp05$majority_age_group <- colnames(dp05[c(33:35)])[apply(dp05[c(33:35)],1,which.max)] ## buying age 20 >

dp05$percent_population_19_under <- dp05$ages_19_and_under / dp05$`Estimate!!SEX AND AGE!!Total population`

dp05$diversity_index <- apply(dp05[c(23:28)],1,diversity) ## Shannon’s index
# dp05$gender_diversity_index <- apply(dp05[c(18:19)],1,diversity) ## Shannon’s index for 18 older population

dp05_final <- dp05[,c(1,29,16,30:32,36:38,2)]
colnames(dp05_final)[3] <- c('median_age')
colnames(dp05_final)[10] <- c('total_population')

## DP03 FILES

dp03_columns_csv <-  read.csv(file='DP03-Columns.csv', skip=1)
colnames(dp03_columns_csv) <- c("value","value2","label")
dp03_columns_keep <- c(dp03_columns_csv$value)
dp03_columns_keep_16 <- c(dp03_columns_csv$value2)

for (i in years) {
  path <- paste('census_all/ACSDP5Y',i,'.dp03-Data.csv', sep='')
  print(path)
  if (i == '2020') {
    dp03 <- read.csv(file = path)
    dp03 <- dp03[, dp03_columns_keep]
    dp03$year <- i
    } else if (i == '2016') {
      dp03_to_append <- read.csv(file = path)
      dp03_to_append <- dp03_to_append[-1,]
      dp03_to_append <- dp03_to_append[, dp03_columns_keep_16]
      colnames(dp03_to_append) <- dp03_columns_keep
      dp03_to_append$year <- i
      dp03 <- rbind(dp03, dp03_to_append)
  } else {
    dp03_to_append <- read.csv(file = path)
    dp03_to_append <- dp03_to_append[-1,]
    dp03_to_append <- dp03_to_append[, dp03_columns_keep]
    dp03_to_append$year <- i
    dp03 <- rbind(dp03, dp03_to_append)
  }
}

dp03 <- dp03 %>% separate(NAME, c(NA, "zipcode"), extra="drop")
colnames(dp03) <- dp03[1,]
dp03 <- dp03[-1, ]
table(colnames(dp03))
dp03 <- dp03 %>% filter(Area %in% zip_codes)
colnames(dp03)[colnames(dp03) == '2020'] <- 'year'
dp03[dp03 == '-' | dp03 == 'N' | is.na(dp03)] <- '0'
dp03 <- dp03 %>% mutate_all(as.integer)

dp03$unemployment_rate <- dp03$`Estimate!!EMPLOYMENT STATUS!!Population 16 years and over!!In labor force!!Civilian labor force!!Unemployed` / dp03$`Estimate!!EMPLOYMENT STATUS!!Population 16 years and over!!In labor force!!Civilian labor force`
dp03$percent_population_work_from_home <- dp03$`Estimate!!COMMUTING TO WORK!!Workers 16 years and over!!Worked from home` / dp03$`Estimate!!COMMUTING TO WORK!!Workers 16 years and over`
dp03$percent_family_households <- dp03$`Estimate!!INCOME AND BENEFITS (IN 2020 INFLATION-ADJUSTED DOLLARS)!!Families` / dp03$`Estimate!!INCOME AND BENEFITS (IN 2020 INFLATION-ADJUSTED DOLLARS)!!Total households`

colnames(dp03)[c(14:26)] <- c('Agriculture, forestry, fishing and hunting, and mining',
                              'Construction',
                              'Manufacturing',
                              'Wholesale trade',
                              'Retail trade',
                              'Transportation and warehousing, and utilities',
                              'Information',
                              'Finance and insurance, and real estate and rental and leasing',
                              'Professional, scientific, and management, and administrative and waste management services',
                              'Educational services, and health care and social assistance',
                              'Arts, entertainment, and recreation, and accommodation and food services',
                              'Other services, except public administration',
                              'Public administration')
dp03$majority_industry <- colnames(dp03[c(14:26)])[apply(dp03[c(14:26)],1,which.max)]

dp03$income_under_25k <-rowSums(dp03[,28:30])
dp03$income_between_25k_50k <-rowSums(dp03[,31:32])
dp03$income_between_50k_100k <-rowSums(dp03[,33:34])
dp03$income_between_100k_200k <-rowSums(dp03[,c(35,36)])
dp03$income_over_200k <-dp03[,37]
dp03$majority_income <- colnames(dp03[c(46:50)])[apply(dp03[c(46:50)],1,which.max)]

dp03_final <- dp03[,c(1,41,13,38,42:45,51)]
colnames(dp03_final)[c(3:4)] <- c('mean_travel_time_to_work_minutes', 'mean_household_income_dollars')

## DP02 FILES

dp02_columns_csv <-  read.csv(file='DP02-Columns.csv', skip=1)
colnames(dp02_columns_csv) <- c("value1718","value161920","label")
dp02_columns_1718_keep <- c(dp02_columns_csv$value1718)
dp02_columns_161920_keep <- c(dp02_columns_csv$value161920)

for (i in years) {
  path <- paste('census_all/ACSDP5Y',i,'.DP02-Data.csv', sep='')
  print(path)
  if (i == '2020') {
    dp02 <- read.csv(file = path)
    dp02 <- dp02[, dp02_columns_161920_keep]
    dp02$year <- i
  } else if (i == '2019') {
    dp02_to_append <- read.csv(file = path)
    dp02_to_append <- dp02_to_append[-1,]
    dp02_to_append <- dp02_to_append[, dp02_columns_161920_keep]
    dp02_to_append$year <- i
    dp02 <- rbind(dp02, dp02_to_append)
  } else {
    dp02_to_append <- read.csv(file = path)
    dp02_to_append <- dp02_to_append[-1,]
    dp02_to_append <- dp02_to_append[, dp02_columns_1718_keep]
    colnames(dp02_to_append) <- dp02_columns_161920_keep
    dp02_to_append$year <- i
    dp02 <- rbind(dp02, dp02_to_append)
  }
}

dp02 <- dp02 %>% separate(NAME, c(NA, "zipcode"), extra="drop")
colnames(dp02) <- dp02[1,]
dp02 <- dp02[-1, ]
dp02 <- dp02 %>% filter(Area %in% zip_codes)
colnames(dp02)[colnames(dp02) == '2020'] <- 'year'
dp02[dp02 == '-' | dp02 == 'N' | is.na(dp02)] <- '0'
dp02 <- dp02 %>% mutate_all(as.integer)

dp02$population_5_years_and_over_grade_school_enrolled <-rowSums(dp02[,12:14]) ## compare against dp05 ages_5_to_19

dp02$population_no_diploma <-rowSums(dp02[,c(3,8)])
dp02$population_high_school_diploma <-dp02[,7]
dp02$population_associates_or_equivelant <-rowSums(dp02[,c(4,9)])
dp02$population_bachelors <-dp02[,5]
dp02$population_graduate <-dp02[,6]
dp02$majority_education <- colnames(dp02[c(18:22)])[apply(dp02[c(18:22)],1,which.max)]

dp02_final <- dp02[,c(1,16,17,23)]


full_census_final  <- full_join(dp05_final,  dp03_final, by = c('Area', 'year'))
full_census_final  <- full_join(full_census_final,  dp02_final, by = c('Area', 'year'))

to_remove <- c('population_5_years_and_over_grade_school_enrolled', 'ages_19_and_under')
full_census_final <- full_census_final[ , -which(names(full_census_final) %in% to_remove)]

full_census_final$Area <- as.character(full_census_final$Area)
full_census_final$mean_household_income_dollars <- as.numeric(full_census_final$mean_household_income_dollars)
full_census_final$mean_travel_time_to_work_minutes <- as.numeric(full_census_final$mean_travel_time_to_work_minutes)
full_census_final$median_age <- as.numeric(full_census_final$median_age)
full_census_final$total_population <- as.numeric(full_census_final$total_population)

na_count_census <-sapply(full_census_final, function(y) sum(length(which(is.na(y)))))
na_count_census <- data.frame(na_count_census)
na_count_census

full_census  <- full_join(dp05,  dp03, by = c('Area', 'year'))
full_census  <- full_join(full_census,  dp02, by = c('Area', 'year'))


## Census Data ENRICHED TO MATCH ALL ZIPCODES
full_census_enriched <- full_census_final
full_census_enriched$year <- as.character(full_census_enriched$year)
all_cbsa_zipcodes <- crossing(all_cbsa_zipcodes, years)
full_census_enriched  <- left_join(all_cbsa_zipcodes,  full_census_enriched, by = c('zipcode' = 'Area', "years" = "year"))

missing_census_columns <- c('percent_male',
                            'percent_female',
                            'total_population', 
                            'percent_population_19_under', 
                            'diversity_index',
                            'unemployment_rate', 
                            'mean_travel_time_to_work_minutes', 
                            'mean_household_income_dollars',
                            'percent_population_work_from_home', 
                            'percent_family_households', 
                            'median_age')
census_cbsa_agg <- full_census_enriched %>% 
                    select(cbsa, missing_census_columns) %>%
                    group_by(cbsa) %>%
                    summarise_all(funs(median), na.rm = TRUE)
census_cbsa_agg_colnames <- c('census_cbsa_agg_med_percent_male',
                              'census_cbsa_agg_med_percent_female',
                              'census_cbsa_agg_med_total_population',
                              'census_cbsa_agg_med_percent_population_19_under',
                              'census_cbsa_agg_med_diversity_index',
                              'census_cbsa_agg_med_unemployment_rate', 
                              'census_cbsa_agg_med_mean_travel_time_to_work_minutes',
                              'census_cbsa_agg_med_mean_household_income_dollars',
                              'census_cbsa_agg_med_percent_population_work_from_home', 
                              'census_cbsa_agg_med_percent_family_households', 
                              'census_cbsa_agg_med_median_age')
colnames(census_cbsa_agg)[2:12] <- census_cbsa_agg_colnames


missing_census_factor_columns <- c('majority_age_group', 
                                   'majority_industry', 
                                   'majority_income', 
                                   'majority_education')
census_factor_cbsa_agg <- full_census_enriched %>% 
                          select(cbsa, missing_census_factor_columns) %>%
                          group_by(cbsa) %>%
                          summarise(
                            majority_age_group_agg = first(names(sort(table(majority_age_group), decreasing = TRUE))),
                            majority_industry_agg = first(names(sort(table(majority_industry), decreasing = TRUE))), 
                            majority_income_agg = first(names(sort(table(majority_income), decreasing = TRUE))), 
                            majority_education_agg = first(names(sort(table(majority_education), decreasing = TRUE))))
census_factor_cbsa_agg_colnames <- colnames(census_factor_cbsa_agg[2:5])

full_census_enriched  <- left_join(full_census_enriched,  census_cbsa_agg, by = 'cbsa')
full_census_enriched  <- left_join(full_census_enriched,  census_factor_cbsa_agg, by = 'cbsa')

full_census_enriched <- full_census_enriched %>%
  mutate(percent_male_final = if_else(!is.na(percent_male), percent_male,
                              if_else(!is.na(census_cbsa_agg_med_percent_male), census_cbsa_agg_med_percent_male, 0)),
         percent_female_final = if_else(!is.na(percent_female), percent_female,
                                        if_else(!is.na(census_cbsa_agg_med_percent_female), census_cbsa_agg_med_percent_female, 0)),
         total_population_final = if_else(!is.na(total_population), total_population,
                                        if_else(!is.na(census_cbsa_agg_med_total_population), census_cbsa_agg_med_total_population, 0)),
         percent_population_19_under_final = if_else(!is.na(percent_population_19_under), percent_population_19_under,
                                             if_else(!is.na(census_cbsa_agg_med_percent_population_19_under), census_cbsa_agg_med_percent_population_19_under, 0)),
         diversity_index = if_else(!is.na(diversity_index), diversity_index,
                           if_else(!is.na(census_cbsa_agg_med_diversity_index), census_cbsa_agg_med_diversity_index, 0)),
         unemployment_rate_final = if_else(!is.na(unemployment_rate), unemployment_rate,
                                   if_else(!is.na(census_cbsa_agg_med_unemployment_rate), census_cbsa_agg_med_unemployment_rate, 0)),
         mean_travel_time_to_work_minutes_final = if_else(!is.na(mean_travel_time_to_work_minutes), mean_travel_time_to_work_minutes,
                                                  if_else(!is.na(census_cbsa_agg_med_mean_travel_time_to_work_minutes), census_cbsa_agg_med_mean_travel_time_to_work_minutes, 0.0)),
         mean_household_income_dollars_final = if_else(!is.na(mean_household_income_dollars), mean_household_income_dollars,
                                               if_else(!is.na(census_cbsa_agg_med_mean_household_income_dollars), census_cbsa_agg_med_mean_household_income_dollars, 0.0)),
         percent_population_work_from_home_final = if_else(!is.na(percent_population_work_from_home), percent_population_work_from_home,
                                                   if_else(!is.na(census_cbsa_agg_med_percent_population_work_from_home), census_cbsa_agg_med_percent_population_work_from_home, 0)),
         percent_family_households_final = if_else(!is.na(percent_family_households), percent_family_households,
                                           if_else(!is.na(census_cbsa_agg_med_percent_family_households), census_cbsa_agg_med_percent_family_households, 0)),
         median_age_final = if_else(!is.na(median_age), median_age,
                                    if_else(!is.na(census_cbsa_agg_med_median_age), census_cbsa_agg_med_median_age, 0.0)),
         majority_age_group_final = if_else(!is.na(majority_age_group), majority_age_group,
                                    if_else(!is.na(majority_age_group_agg), majority_age_group_agg, 'na')),
         majority_industry_final = if_else(!is.na(majority_industry), majority_industry,
                                   if_else(!is.na(majority_industry_agg), majority_industry_agg, 'na')),
         majority_income_final = if_else(!is.na(majority_income), majority_income,
                                 if_else(!is.na(majority_income_agg), majority_income_agg, 'na')),
         majority_education_final = if_else(!is.na(majority_education), majority_education,
                                    if_else(!is.na(majority_education_agg), majority_education_agg, 'na'))
  )

to_drop <- c(missing_census_columns, census_cbsa_agg_colnames, census_factor_cbsa_agg, 
             missing_census_factor_columns, census_factor_cbsa_agg_colnames)
full_census_enriched <- full_census_enriched[ , -which(names(full_census_enriched) %in% to_drop)]

na_count_census <-sapply(full_census_enriched, function(y) sum(length(which(is.na(y)))))
na_count_census <- data.frame(na_count_census)
na_count_census

full_census_enriched_2020 <- full_census_enriched %>% filter(years == '2020')
full_census_enriched_2020 <- full_census_enriched_2020[,-3]

listings_enriched <- left_join(listings_enriched, full_census_enriched_2020, by = c("zipcode" = "zipcode", "cbsa" = "cbsa"))
## Checking all fields have values - no NA
na_count_full <- sapply(listings_enriched, function(y) sum(length(which(is.na(y)))))
na_count_full <- data.frame(na_count_full)
na_count_full


setwd(paste0(base_path, "/data/output_data"))
write.csv(full_census_enriched, "full_census_enriched.csv", row.names = FALSE)
write.csv(full_census_enriched_2020, "full_census_enriched_2020.csv", row.names = FALSE)



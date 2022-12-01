
majority_income_dummy <- c(unique(listings_enriched_model$majority_income_dummy))
majority_education_dummy <- c(unique(listings_enriched_model$majority_education_dummy))
hometype_dummy <- c(unique(listings_enriched_model$hometype_dummy))
family_type_dummy <- c(unique(listings_enriched_model$family_type_dummy))
bedroom_bucket_dummy <- c(unique(listings_enriched_model$bedroom_bucket_dummy))
sqft_buckets_dummy <- c(unique(listings_enriched_model$sqft_buckets_dummy))
yearbuilt_buckets_dummy <- c(unique(listings_enriched_model$yearbuilt_buckets_dummy))
overall_education_score_dummy <- c(unique(listings_enriched_model$overall_education_score_dummy))
centrality_index_dummy <- c(unique(listings_enriched_model$centrality_index_dummy))
price_dummy <- c(unique(listings_enriched_model$price_dummy))
median_age_dummy <- c(unique(listings_enriched_model$median_age_dummy))


cbsa_model_accuracy <- all_unique_cbsas
cbsa_model_accuracy$accuracy <- NA
cbsa_model_accuracy$k_value <- NA
cbsa_model_accuracy$possible_zips <- NA
cbsa_model_accuracy$pred_zips <- NA

for (cbsa_x in cbsas) {
  
  print(cbsa_x)

  model_data <- listings_enriched_model %>% filter(cbsa == cbsa_x)
  cbsa_model_accuracy[(cbsa_model_accuracy$cbsa == cbsa_x),]$possible_zips <- length(unique(model_data$zipcode))

  to_keep_model <- c('majority_income_dummy',
                     'majority_education_dummy',
                     'hometype_dummy',
                     'family_type_dummy',
                     'bedroom_bucket_dummy',
                     'sqft_buckets_dummy',
                     'yearbuilt_buckets_dummy',
                     'overall_education_score_dummy',
                     'price_dummy',
                     'median_age_dummy',
                     'centrality_index_dummy',
                     'zipcode')
  
  model_data <- model_data[ , which(names(model_data) %in% to_keep_model)]
  model_data$rand <- c(runif(nrow(model_data)))
  
  neighbor_count <- model_data %>% group_by(zipcode) %>% summarise(total_count = n()) %>% arrange(desc(total_count))
  med_neighbor_count <- median(neighbor_count$total_count)
  k <- quantile(neighbor_count$total_count, probs = c(.0001, .001))
  
  to_predict<-merge(data.frame(majority_income_dummy=majority_income_dummy), data.frame(majority_education_dummy=majority_education_dummy),by=NULL);
  to_predict<-merge(to_predict, data.frame(hometype_dummy=hometype_dummy),by=NULL);
  to_predict<-merge(to_predict, data.frame(family_type_dummy=family_type_dummy),by=NULL);
  to_predict<-merge(to_predict, data.frame(bedroom_bucket_dummy=bedroom_bucket_dummy),by=NULL);
  to_predict<-merge(to_predict, data.frame(sqft_buckets_dummy=sqft_buckets_dummy),by=NULL);
  to_predict<-merge(to_predict, data.frame(yearbuilt_buckets_dummy=yearbuilt_buckets_dummy),by=NULL);
  to_predict<-merge(to_predict, data.frame(overall_education_score_dummy=overall_education_score_dummy),by=NULL);
  to_predict<-merge(to_predict, data.frame(centrality_index_dummy=centrality_index_dummy),by=NULL);
  to_predict<-merge(to_predict, data.frame(price_dummy=price_dummy),by=NULL);
  to_predict<-merge(to_predict, data.frame(median_age_dummy=median_age_dummy),by=NULL);
  to_predict$rand <- c(runif(nrow(to_predict)))

  ####################################################################################################
  trControl <- trainControl(method  = "cv", number  = 5)

  knnfit <- train(zipcode ~ .,
                 method     = "knn",
                 tuneGrid   = expand.grid(k = k),
                 trControl  = trControl,
                 metric     = "Accuracy",
                 data       = model_data)

  bestTune_k_value <- knnfit$bestTune[1,1]
  cbsa_model_accuracy[(cbsa_model_accuracy$cbsa == cbsa_x),]$k_value <- bestTune_k_value
  bestTune_k_value_accuracy <- knnfit$results %>% filter(k == bestTune_k_value) %>% select("Accuracy")
  cbsa_model_accuracy[(cbsa_model_accuracy$cbsa == cbsa_x),]$accuracy <- bestTune_k_value_accuracy[1,1]
  print(bestTune_k_value_accuracy[1,1])

  knnPredict <- predict(knnfit, newdata = to_predict[,c(1:12)])
  predictions <- as.data.frame(as.character(knnPredict))
  colnames(predictions) <- "pred"
  to_predict <- cbind(to_predict, predictions)

  to_predict$cbsa <- cbsa_x
  output <- to_predict
  
  output <- left_join(output,  all_unique_cbsas, by=c("cbsa"="cbsa"))
  output <- left_join(output,  majority_income_bucket_map, by="majority_income_dummy")
  output <- left_join(output,  majority_education_bucket_map, by="majority_education_dummy")
  output <- left_join(output,  price_bucket_map, by=c("cbsa"="cbsa","price_dummy"="price_dummy"))
  output <- left_join(output,  median_age_bucket_map, by=c("cbsa"="cbsa","median_age_dummy"="median_age_dummy"))
  
  output$hometype <- if_else(output$hometype_dummy == 1, 'SINGLE FAMILY', if_else(output$hometype_dummy == 2, 'CONDO', 'TOWNHOUSE'))
  
  output$family_type <- if_else(output$family_type_dummy == 1, 'Have Children in Household Under 19', 'Do Not Have Children in Household Under 19')
  
  output$bedroom_bucket <- if_else(output$bedroom_bucket_dummy == 1, "One or Two",
                           if_else(output$bedroom_bucket_dummy == 2, "Three to Five", "Five+"))
  
  output$sqft_buckets <- if_else(output$sqft_buckets_dummy == 1, "Less than 1500 SqFt",
                         if_else(output$sqft_buckets_dummy == 2, "Between 1500 & 3000 SqFt", "3000+ SqFt"))
  
  output$yearbuilt_buckets <- if_else(output$yearbuilt_buckets_dummy == 1, "New Construction within Last Two Years",
                              if_else(output$yearbuilt_buckets_dummy == 2, "Between Two to Five Years Old",
                              if_else(output$yearbuilt_buckets_dummy == 3, "Between Five to Fifteen Years Old", "Fifteen+ Years Old")))
  
  output <- output[,-12]
  
  write.csv(output, str_c("predicted_output_",cbsa_x,".csv"), row.names = FALSE)

  cbsa_model_accuracy[(cbsa_model_accuracy$cbsa == cbsa_x),]$pred_zips <- length(unique(to_predict$pred))
}


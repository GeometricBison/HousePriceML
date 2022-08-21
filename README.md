# HousePriceML
This project explores real estate property price prediciton using machine learning and data gathered from Redfin.com for homes in the Naperivlle/Bolingbrook area.

## Introduction
Machine learning can be used to estimate real estate prices. By tkaing in parameters like bathrooms, bedrooms, and square footage, machine learning models can appraise the price of a home.

## Gathering the Data
For this project, data was gathered using a web scraper to parse through data on Redfin, a real estate website. The scraper file can be found in the src folder. The code uses an asyncronous apporach that parse through many webpages at a time before writing the contents into a csv file. When scraping for data, attributes were taken and the data was cleaned. The files for the data can be found in the results folder. They are categorized by year and city. 

## Preproccesing
In a separate notebook file, the data was cleaned even more using Pandas. Outliers that had listing prices of above $2.5 million dollars were cut out, for example. Any unsual amount of rooms, beds, or baths due to website error were also cleaned. Categorical variables were encoded with a 0 or 1 to show if a certain house had a trait. For example, a condo would have a 0 in the "Property Type_Single Residential Home" column but a 1 in the "Property Type_Condo" column. 

## Modeling
Five models were used in total. Linear regression, random forest regression, decision trees, Xgboost regression, and support vector regression were chosen. Caluclations for effectiveness were based on RMSE, MAE, and the coefficient of determination (r squared) for each model. The specefic results can be found in the results folder. However, it was found that XgBoost performed the best.

## Variable Importance
After running the models, SHAP was used to model the weights of the variables. They can be found in the results folder as well, and are categorized by year. 


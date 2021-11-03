# CapstoneProjectStarbucks<br>
<br>
This project uses a Machine Learning algorithm to select an offer for an costumer based on the offer success and prior costumer history.
<br>
It also provides an web app to be used as a interface for the algorithm.<br>

## Project Definition<br>

It was given a mock transcript of the costumer behavior on the Starbucks mobile app and the profile demographics as well as data on the offer. With that I’ve built a machine learning model to decide which offer is most suitable to teach costumer or if any offer is suitable at all.<br>


## Analysis<br>

The first job to be done was to clean the data set. All the information was in json files so I had to flatten it to a Pandas DataFrame.<br>
Further analysis showed that the offers that were successful had a ‘offer completed’ cell in the json file and also a transaction in the same day. Using this information I’ve labeled the offer success so the model can be trained to predict this offer based on data available on the day of the offer.<br>
The model used was the xgboost and I’ve trained fine tuning it in a Gridsearch algorithm with maximum depth form 2 to 8 and 100 to 300 estimators.<br>
The model presented an overall accuracy of 0.68 and although the precison of each offer is around 0.4 the precision of the offer_fail label is around 0.8.<br>
This means that the model may not predict the offer in the most optimal way but it can certainly select the costumers that are not inclined to respond to any offer at all. <br>


## Conclusion<br>
The project was successfully executed and the machine learning model was made available for the user in a web app. With this app the user – the marketing team of Starbucks – can now select each day what offers they should show to their clients. <br>
Further optimizations can be made in the algorithm such as test different models, combine columns to improve feature engineering and finally implement rules to offerings (do not show the same offer twice or don show offers after n days, etc).<br>

## Python packages used:<br>
<br>
This project can be executed using the Anaconda distribution of Python 3.x plus: <br>
    sklearn==0.23.1 <br>
    xgboost==1.3.3 <br>
    Flask==1.1.2 <br>
    plotly==5.1.0 <br>

## Files contained in repository:<br>
<br>
app<br>
| - template<br>
| |- master.html # main page of web app<br>
|- run.py # Flask file that runs app<br>
data<br>
|- portfolio.json # data to process<br>
|- profile.json # data to process<br>
|- transcript.json # data to process<br>
|- process_data.py - python file with the ETL for the project<br>
|- User.db # database to save clean data to<br>
models<br>
|- train_classifier.py- python file with the ML model<br>
README.md<br>


## Instructions:<br>
1. Run the following commands in the project's root directory to set up your database and model.<br>
<br>
    - To run ETL pipeline that cleans data and stores in database<br>
        `python data/process_data.py data/portfolio.json data/profile.json data/transcript.json, data/User.db`<br>
    - To run ML pipeline that trains classifier and saves<br>
        `python models/train_classifier.py data/User.db models/classifier.pkl`<br>
<br>
2. Run the following command in the app's directory to run your web app.<br>
    `python run.py`<br>
<br>
3. Go to http://0.0.0.0:3001/<br>
<br>

## Acknowledgment<br>
I want to thank Udacity for the opportunity to work on such interesting project.<br>

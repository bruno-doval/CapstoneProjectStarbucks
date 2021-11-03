# CapstoneProjectStarbucks<br>
<br>
This project uses a Machine Learning algorithm to select an offer for an costumer based on the offer success and prior costumer history.
<br>
It also provides an web app to be used as a interface for the algorithm.<br>


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

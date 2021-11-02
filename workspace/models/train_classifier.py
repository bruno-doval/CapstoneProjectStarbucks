import sys
# import libraries
import pandas as pd
from sqlalchemy import create_engine
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import xgboost as xgb
import joblib
 
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report

"""
To run ML pipeline that trains classifier and saves

`python models/train_classifier.py data/DisasterResponse.db models/classifier.pkl`
"""


def load_data(database_filepath):
    """
    INPUT:
    database_filepath: the file path to the database

    OUTPUT:
    X: features of the message df
    y: classifications of the messages
    col_list: list of classification columns
    """
    engine = create_engine('sqlite:///{}'.format(database_filepath))

    cols_drop = ['person','selected_offer',
                            'last_info','event','became_member_on'
                            ,'offer_id', 'offer_type','gender',
               'amount','reward','difficulty','duration']

    df = pd.read_sql("SELECT * FROM User", engine)
    df = df[df.event=='offer received'].copy()
    X = df.drop(columns =cols_drop).fillna(0)
    y = df['selected_offer']
    return X,y




def build_model():

    """
    builds a pipeline to be used for modeling a df
    """
    pipeline = Pipeline([ ('classifier', xgb.XGBClassifier(  eval_metric='mlogloss'))])


    param = {
        'classifier__max_depth':[2,4,6,8] 
        }
    cv = GridSearchCV(estimator =pipeline, param_grid =param )



    return cv

def evaluate_model(model, X_test, Y_test):
    """
    INPUT:
    model: model to be applied on the df
    X_test: part of the df to be used as featues
    Y_text: response part of the df
    category_names: names pf the categories

    OUTPUT:
    print the repport comparing the test response data (Y) with the model applied to the test data (X)
    """

    y_pred = model.best_estimator_.predict(X_test)

    print(classification_report(Y_test, y_pred))


def save_model(model, model_filepath):
    """
    Saves the model into a pickle file

    INPUT:
    model: model to be saved
    model_filepath: file path to save the model on
    """
    joblib.dump(model.best_estimator_, model_filepath)


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()
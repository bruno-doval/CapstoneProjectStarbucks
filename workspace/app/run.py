import json
import plotly
import pandas as pd


from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar,Table
import joblib
from sqlalchemy import create_engine


app = Flask(__name__)


# load data
engine = create_engine('sqlite:///../data/User.db')
df = pd.read_sql("SELECT * FROM User", engine)

# load model
model = joblib.load("../models/classifier.pkl")

cols_drop =['selected_offer',
                        'last_info','event','became_member_on'
                        ,'offer_id', 'offer_type','gender',
            'amount','reward','difficulty','duration']
                            
X = df[df.last_info==1].copy()
X = X.drop(columns =cols_drop).fillna(0).drop_duplicates(subset=['person'],keep='last')

classification_labels = model.predict(X.drop(columns=['person']))

X['selected offer'] = classification_labels


# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():


    # plot by offer sucess
    offer_amount = df[df.event=='offer completed'].groupby('offer_id').sum().sort_values(by='offer_amount')['offer_amount']
    offer_names = list(offer_amount.index)

    offers_sent = df[df.event=='offer received'].groupby('offer_id')[['person']].count().rename(columns={'person':'offers sent'})
    offer_suc = df[df.offer_success	==1].groupby('offer_id')[['person']].count().rename(columns={'person':'offer success'})
    df_success = offer_suc.merge(offers_sent,left_index=True,right_index=True)
    df_success['sucess_rate'] = df_success['offer success']/df_success['offers sent']
    df_success = df_success.sort_values(by=['sucess_rate'],ascending=False)


    offer_success_rate = df_success['sucess_rate']
    offer_success_id = list(offer_success_rate.index)

    # creating base dataframe for demogaphics
    df_demo = df.drop_duplicates(subset=['person','gender','age']).copy()
    gender_counts = df_demo.groupby('gender').count()['person']
    gender_names = list(gender_counts.index)


    #plot by ages count using bins
    df_demo['ages'] = pd.cut(x=df_demo['age'], bins=list(range(18,128,10)))
    df_demo['ages'] = df_demo.apply(lambda x: x.ages if x.age<118 else 'not informed',axis=1)

    ages = df_demo.groupby('ages')['person'].count()

    ages_hist = ages
    ages_names = [str(i) for i in ages_hist.index]



    # create visuals

    graphs = [
        {
            'data': [
                Table(
                    header=dict(
                    values=['person', 'selected offer']
                ),
                cells=dict(
                    values=[X[k].tolist() for k in ['person', 'selected offer']])
                    
                )
            ],

            'layout': {
                'title': 'Offers Selected'
                
                
            }
        },
        {
            'data': [
                Bar(
                    x=offer_amount,
                    y=offer_names,
                    orientation = 'h'
                )
            ],

            'layout': {
                'title': 'Revenue per Offer',
                'yaxis': {
                    'title': "Revenue (USD)"    
                },
                'xaxis': {
                    'title': "Offer ID"
                }
            }
        },   

    {
            'data': [
                Bar(
                    x=offer_success_id,
                    y=offer_success_rate
                )
            ],

            'layout': {
                'title': 'Success Rate by Offer',
                'yaxis': {
                    'title': "Rate"
                },
                'xaxis': {
                    'title': "Offer ID"
                }
            }
        },
    {
            'data': [
                Bar(
                    x=gender_names,
                    y=gender_counts
                )
            ],

            'layout': {
                'title': 'Distribution of Gender in Clients Base',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Gender"
                }
            }
        },
    {
            'data': [
                Bar(
                    x=ages_names,
                    y=ages_hist
                )
            ],

            'layout': {
                'title': 'Distribution of Age in Clients Base',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Age Interval"
                }
            }
        }
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()
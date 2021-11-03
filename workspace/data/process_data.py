import sys
import pandas as pd
from sqlalchemy import create_engine


"""
To run ETL pipeline that cleans data and stores in database
`python data/process_data.py data/porfolio.json data/profile.json data/transcript.json, data/User.db`
"""



def load_data(portfolio_filepath, profile_filepath,transcript_filepath):
    """
    Loads the data to be processed

    INPUT:
    portfolio_filepath: file path of the porfolio json file 
    profile_filepath: file path of the profile json file 
    transcript_filepath: file path of the transcript json file

    OUTPUT:
    df: a dataframe combining the 3 json files
    """
    # load portfolio dataset
    portfolio = pd.read_json(portfolio_filepath, orient='records', lines=True)

    # load profile dataset
    profile = pd.read_json(profile_filepath, orient='records', lines=True)

    # load transcript dataset
    transcript = pd.read_json(transcript_filepath, orient='records', lines=True)



    return portfolio,profile,transcript



def clean_data(portfolio,profile,transcript):
    """
    Cleans the df spliting columns, build a 0/1 columns for each category, etc
    """
    # normalizing the json structure inside transcipt dataframe
    transcript_norm = pd.json_normalize(transcript.value)
    transcript_norm.offer_id = transcript_norm[['offer id','offer_id']].bfill(axis=1).iloc[:, 0]
    transcript_norm = transcript_norm.drop(columns = ['offer id'])
    transcript_norm = pd.concat([transcript.drop(columns=['value']),transcript_norm],axis=1)

    # adding info about the lenght of mermership based on the date of "became merber on" assuming
    # that the last day of the dataframe is the same as the max date on this column
    profile.became_member_on = pd.to_datetime(profile.became_member_on,format='%Y%m%d')
    profile['days_as_member'] = (profile.became_member_on.max()-profile.became_member_on).dt.days


    def age_informed(age):
        'functio to informe if age was informed (True) or not (False) if age is a number or null'
        if pd.isna(age) or age==118:
            return False
        else:
            return True

    profile['income_informed'] = -profile.income.isna()
    profile['income_informed'] =profile['income_informed'].astype(int)
    profile.income = profile.income.fillna(profile.income.mean())
    profile['age_informed'] = profile.age.apply(lambda x: age_informed(x)).astype(int)
    
    # filling not informed gender as 'na'
    profile['gender'] = profile['gender'].fillna('na')



    # merging transcript with portfolio thus creating the df dataframe
    df = transcript_norm.drop(columns='reward').merge(portfolio, left_on='offer_id',right_on='id',how='left').drop(columns='id')

    #merging df to profile info
    df = df.merge(profile.rename(columns={'id':'person'}), on='person',how='left')

    # sorting by time
    df = df.sort_values(by='time')

    # creating an offer rank for each person. This is to match the offers with the transaction that
    # can be found on the same day of offer completion
    df['offer_rank'] = df.sort_values(by=['person','offer_id','time','event']).groupby(['person','offer_id','event'])['time'].rank('dense')
    df_offer_amount = df[df.event=='offer completed'][['person','time']].merge(df[df.event=='transaction'][['person','time','amount']],on=['person','time'],how='left')
    df_offer_amount = df_offer_amount.rename(columns = {'amount':'offer_amount'})
    df = df.merge(df_offer_amount,on=['person','time'],how='left')

    # getting the info form transacition into offer when completed based on rank
    df['offer_amount'] = df['offer_amount'].fillna(df.groupby(['person','offer_id','offer_rank'])['offer_amount'].transform('mean'))

    #calculating the last time client was offered a coupon
    df['days_since_offer'] = df.apply(lambda x: x.time if x.event=='offer received' else None,axis =1)
    df['days_since_offer'] = df.groupby('person')['days_since_offer'].transform(lambda x: x.ffill())
    df['days_since_offer'] = df.time - df.days_since_offer

    #check if offer when was offered was a success or not (for training the model based on when it was offered)
    df['offer_success'] = df.apply(lambda x: 1 if x.offer_amount>0 and x.event=='offer received' else None,axis=1)
    df['offer_completed_hist'] = df.apply(lambda x: x.offer_amount if x.offer_amount>0 and x.event=='offer completed' else None,axis=1)

    dummies =['gender','offer_id']

    for var in  dummies:
        # for each cat add dummy var, drop original column
        df = pd.concat([df, pd.get_dummies(df[var], prefix=var, prefix_sep='_')], axis=1)

    # getting cummulative success (based on amount) of each offer and client
    list_offers_ids = [x for x in df.columns if x.startswith("offer_id_")]
    df[list_offers_ids] = df[list_offers_ids].multiply(df["offer_completed_hist"]*(df['event']=='offer completed'), axis="index")
    df[list_offers_ids] = df.fillna(0).groupby('person')[list_offers_ids].cumsum()

    #cumulative success of overall offers
    overall_cum = df.fillna(0).groupby('person')[['amount','offer_success']].cumsum()
    df[['amount_cum','offer_success_cum']] = overall_cum

    # creating the label column: offer_id if it was successeful or 'offer_fail' if not
    df_select_offer = df.groupby('person').time.max().reset_index().merge(df,on=['person','time'])
    df_select_offer.drop_duplicates(subset='person',keep='last',inplace=True)
    df['selected_offer'] = df.apply(lambda x: x.offer_id if x.offer_success==1 else 'offer_fail',axis =1)

    # we will be selecting the last day available of users to select if we are going to offer them some offer_id or not
    # this will be used to select the last day available
    last_info = df.groupby('person').time.max().reset_index()
    last_info['last_info'] =1

    df = df.merge(last_info,on=['person','time'],how='left')
    df.last_info = df.last_info.fillna(0)

    #removing list column
    df.drop(columns= ['channels'],inplace=True)

    return df

def save_data(df, database_filename,table_name):
    """
    Saves the DataFrame into a database

    INPUT:
    df: dataframe
    database_filename: name of the database to be saved
    """
    engine = create_engine('sqlite:///{}'.format(database_filename))
    df.to_sql(table_name, engine, index=False, if_exists='replace')


def main():

    if len(sys.argv) == 5:

        portfolio_filepath, profile_filepath,transcript_filepath,database_filepath  = sys.argv[1:]

        print('Loading data...\n    PORTFOLIO: {}\n    PROFILE: {}\n    TRANSCRIPT: {}'
              .format(portfolio_filepath, profile_filepath,transcript_filepath))
        portfolio,profile,transcript = load_data(portfolio_filepath, profile_filepath,transcript_filepath)

        print('Cleaning data...')
        df = clean_data(portfolio,profile,transcript)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath,'User')

        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
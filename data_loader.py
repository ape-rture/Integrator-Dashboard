import pandas as pd
import numpy as np


from requests import Request, Session, post
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import time
def call_api(url, parameters = {}, headers = {"accept": "application/json", "content-type": "application/json"}):

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)

        data = json.loads(response.text)

        return data

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        pp.pprint(e)


# call the integrator API
def call_integrator_analytics(integrator, status='DONE', from_timestamp=None, to_timestamp=None, base_url = "https://li.quest/v1/"):
    url = base_url + "analytics/transfers"

    parameters = {'integrator': integrator,
           'status': status
           }

    if from_timestamp:
        parameters['fromTimestamp'] = from_timestamp
    if to_timestamp:
        parameters['toTimestamp'] = to_timestamp

    results = call_api(url, parameters=parameters)

    try:
        results = results['transfers']

    except:
        print(results)
        results = None

    return results

def parse_integrator_data(data):

    integrator_df = pd.DataFrame(data)

    df_columns = ['timestamp', 'chainId','gasAmountUSD', 'amountUSD','token.symbol', 'token.name',
           'token.coinKey', 'gasToken.name', 'gasToken.coinKey']
    sending_df = pd.json_normalize(integrator_df['sending'])[df_columns]
    sending_df.columns = [ 'sending_' + x for x in sending_df.columns]

    receiving_df = pd.json_normalize(integrator_df['receiving'])[df_columns]
    receiving_df.columns = [ 'receiving_' + x for x in receiving_df.columns]

    integrator_df = integrator_df.drop(['sending', 'receiving', 'lifiExplorerLink', 'substatusMessage'], axis=1)
    integrator_df = pd.concat([integrator_df, sending_df, receiving_df], axis=1)

    # convert timesstamps
    integrator_df['sending_datetime'] = pd.to_datetime(integrator_df['sending_timestamp'], unit='s')
    integrator_df['sending_date'] = integrator_df['sending_datetime'].dt.date

    integrator_df['receiving_datetime'] = pd.to_datetime(integrator_df['receiving_timestamp'], unit='s')
    integrator_df['receiving_date'] = integrator_df['receiving_datetime'].dt.date

    # set types
    integrator_df['sending_amountUSD'] =  integrator_df['sending_amountUSD'].astype(float)
    integrator_df['receiving_amountUSD'] =  integrator_df['receiving_amountUSD'].astype(float)
    integrator_df['sending_gasAmountUSD'] =  integrator_df['sending_gasAmountUSD'].astype(float)
    integrator_df['receiving_gasAmountUSD'] =  integrator_df['receiving_gasAmountUSD'].astype(float)

    integrator_df['sending_gasToken_chain'] =  integrator_df['sending_chainId'].astype(str) + ": " + integrator_df['sending_gasToken.coinKey']
    integrator_df['receiving_gasToken_chain'] =  integrator_df['receiving_chainId'].astype(str) + ": " + integrator_df['receiving_gasToken.coinKey']


    return integrator_df

def continuous_analytics_call(integrator, start_date, end_date, status='DONE', base_url="https://li.quest/v1/"):
    # convert start_date and end_date
    start_date_timestamp = pd.Timestamp(start_date)
    from_timestamp = int(time.mktime(start_date_timestamp.timetuple()))

    end_date_timestamp = pd.Timestamp(end_date)
    to_timestamp = int(time.mktime(end_date_timestamp.timetuple()))

    # initialize from_timestamp and df
    integrator_complete_df = pd.DataFrame()

    # loop until last datapoint is end date
    while from_timestamp < to_timestamp:
        result = call_integrator_analytics(integrator, status, from_timestamp, to_timestamp, base_url)

        # check if result is empty
        if result is None or len(result) == 0:
            break

        # parse data
        integrator_df = parse_integrator_data(result)

        # update from_timestamp
        max_timestamp = int(time.mktime(integrator_df['sending_date'].min().timetuple()))
        to_timestamp = max_timestamp

        # Append df
        integrator_complete_df = pd.concat([integrator_complete_df, integrator_df], ignore_index=True)

    return integrator_complete_df

import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import numpy as np
from datetime import date, timedelta


from data_loader import continuous_analytics_call
from chart_lib import hist, scatter
from integrator_data import integrator_list, integrator_descriptions


@st.cache_data
def load_data(integrator, start_date, end_date, transaction_status):

    base_url = "https://partner-test.li.quest/"

    integrator_complete_df = continuous_analytics_call(integrator, start_date, end_date, status=transaction_status)

    # data quality control. I remove partial data
    integrator_complete_df = integrator_complete_df[(integrator_complete_df['sending_datetime'] >= start_date) & (integrator_complete_df['sending_datetime'] < end_date)]
    integrator_complete_df = integrator_complete_df[integrator_complete_df['substatus'] != 'PARTIAL']

    return integrator_complete_df


### side bar
integrator = st.sidebar.radio(
        "Integrator",
        integrator_list)

start_date = st.sidebar.date_input("Start date", date.today() - timedelta(days=14)).strftime("%Y-%m-%d")
end_date = st.sidebar.date_input("Before date", date.today()).strftime("%Y-%m-%d")

### Page
st.title('LI.FI Integrator Dashboard')

# Data loading
data_load_state = st.text('Loading data...')
df = load_data(integrator, start_date, end_date, transaction_status="DONE")
data_load_state.text("")

### calculating stats
# start time and endtime
first_datetime = df['sending_datetime'].min()
last_datetime = df['sending_datetime'].max()
total_count_swaps = df['transactionId'].count() # Total Swaps
total_usd_swaps = df['sending_amountUSD'].sum().round(2) # Total USD swapped
send_avg_gas_fee = df['sending_gasAmountUSD'].mean().round(2)
recieve_avg_gas_fee  = df['receiving_gasAmountUSD'].mean().round(2)

# charts
tx_per_day_hist = hist(df, 'sending_date', 'transactionId',  x_name = 'Day', y_name = 'TX Count',  head=None, date_range=True, show=False, save=False) # Tx counts per day
volume_per_day_hist = hist(df, 'sending_date', 'sending_amountUSD', x_name = 'Day', y_name = 'USD', method='sum', head=None, date_range=True, show=False, save=False) # Volume per day
tool_hist = hist(df, 'tool', 'transactionId', x_name = 'Tool',  head=10, show=False, save=False) # tool counts
send_token_hist = hist(df, 'sending_token.symbol', 'transactionId', x_name = 'Token sent',  head=10, show=False, save=False) # coins send counts
receive_token_hist = hist(df, 'receiving_token.symbol', 'transactionId', x_name = 'Token received',  head=10, show=False, save=False) # coins received counts
send_token_sum_hist = hist(df, 'sending_token.symbol', 'sending_amountUSD',  x_name = 'Token sent',  y_name='Sum ($)', method='sum', head=10, show=False, save=False) # coins send sum
receive_token_sum_hist = hist(df, 'receiving_token.symbol', 'receiving_amountUSD', x_name = 'Token received', y_name='Sum ($)', method='sum', head=10, show=False, save=False) # coins received sum
send_gas_token_hist = hist(df, 'sending_gasToken_chain', 'transactionId', x_name = 'Gas token',  head=10, show=False, save=False)
receive_gas_token_hist = hist(df, 'receiving_gasToken_chain', 'transactionId', x_name = 'Gas token',  head=10, show=False, save=False)
send_gas_token_avg_hist = hist(df, 'sending_gasToken_chain', 'sending_gasAmountUSD',  x_name = 'Gas token',  y_name='Median ($)', method='median', head=10, show=False, save=False)
receive_gas_token_avg_hist = hist(df, 'receiving_gasToken_chain', 'receiving_gasAmountUSD', x_name = 'Gas token', y_name='Median ($)', method='median', head=10, show=False, save=False)


### page body
st.subheader(f'{integrator}')
st.write(f"Data from {integrator} from {first_datetime} to {last_datetime}")
st.write(f"{integrator_descriptions[integrator]}")

tab1, tab2, tab3 = st.tabs(["Overview", "Tokens", "Gas Fees"])

with tab1:
    col1_1, col1_2 = st.columns(2)
    col1_1.metric("Total Transfers", f"{total_count_swaps}")
    col1_2.metric("Total USD Transferred", "${:,.2f}".format(total_usd_swaps))

    st.subheader('Transfers Per Day')
    st.plotly_chart(tx_per_day_hist, theme="streamlit", use_container_width=True)

    st.subheader('Volume Per Day')
    st.plotly_chart(volume_per_day_hist, theme="streamlit", use_container_width=True)

    st.subheader('Tools Used For Transfer')
    st.plotly_chart(tool_hist, theme="streamlit", use_container_width=True)

with tab2:
    col1_1, col1_2 = st.columns(2)
    col1_1.subheader('Tokens Sent')
    col1_1.plotly_chart(send_token_hist, theme="streamlit", use_container_width=True)

    col1_2.subheader('Tokens Received')
    col1_2.plotly_chart(receive_token_hist, theme="streamlit", use_container_width=True)

    col2_1, col2_2 = st.columns(2)
    col2_1.plotly_chart(send_token_sum_hist, theme="streamlit", use_container_width=True)
    col2_2.plotly_chart(receive_token_sum_hist, theme="streamlit", use_container_width=True)

with tab3:
    col1_1, col1_2 = st.columns(2)
    col1_1.metric("Gas Costs Sending", "${:,.2f}".format(send_avg_gas_fee))
    col1_2.metric("Gas Costs Receiving", "${:,.2f}".format(recieve_avg_gas_fee))

    col2_1, col2_2 = st.columns(2)
    col2_1.subheader('Gas Token for Sending')
    col2_1.plotly_chart(send_gas_token_hist, theme="streamlit", use_container_width=True)

    col2_2.subheader('Gas Token for Receiving')
    col2_2.plotly_chart(receive_gas_token_hist, theme="streamlit", use_container_width=True)

    col3_1, col3_2 = st.columns(2)
    col3_1.plotly_chart(send_gas_token_avg_hist, theme="streamlit", use_container_width=True)
    col3_2.plotly_chart(receive_gas_token_avg_hist, theme="streamlit", use_container_width=True)

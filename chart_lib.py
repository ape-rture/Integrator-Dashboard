import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import kaleido

pio.renderers.default = "notebook_connected"
pio.templates.default = "plotly_white"

def hist(df, x, y, x_name=None, y_name=None, method='count', date_range=None, drop_duplicates_column=None, keep='last', sort ='descending',
        head=5, category_array=None, width_height=None, show=False, save=True, folder=""):

    title_addition = ""

    if drop_duplicates_column:
        df = df.drop_duplicates(subset=[drop_duplicates_column], keep='last')
        title_addition = f"_(by_{keep}_{drop_duplicates_column})"

    df = df[[x, y]]

    # select method
    if method == "max":
        df_hist = df.groupby(x).max()

    elif method == "mean":
        df_hist = df.groupby(x).mean()

    elif method == 'nunique':
        df_hist = df.groupby(x).nunique()

    elif method == 'sum':
            df_hist = df.groupby(x).sum()

    elif method == 'median':
            df_hist = df.groupby(x).median()

    else:
        df_hist = df.groupby(x).count()

        if not y_name:
            y_name = 'Count'

    if date_range:
        df[x] = pd.to_datetime(df[x])
        min_date = df[x].min()
        max_date = df[x].max()

        date_range = pd.DataFrame(pd.date_range(min_date,max_date-pd.Timedelta(days=1),freq='d'), columns=[x])
        count = df_hist.reset_index().rename(columns={'index': x})
        count[x] = pd.to_datetime(count[x])
        hist_df = pd.merge(date_range, count, how='left', on=x).fillna(0)

    # select sort
    if sort == "ascending":
        df_hist = df_hist.sort_values(by=y, ascending=True)
    else:
        df_hist = df_hist.sort_values(by=y, ascending=False)

    # select top 10
    if head:
        df_hist = df_hist.head(head)


    # create Figure
    fig = go.Figure()
    fig.add_trace(go.Bar(y=df_hist[y].values, x=df_hist.index, name="datetime"))

    if not x_name:
        x_name = x
    if not y_name:
        y_name = y

    if category_array:
        fig.update_xaxes(categoryorder='array', categoryarray=category_array)


    # formatting
    fig.update_xaxes(title_text=x_name)
    fig.update_yaxes(title_text=y_name)

    if width_height:
        fig.update_layout(
            autosize=False,
            width=width_height[0],
            height=width_height[1])

    if show:
        fig.show()

    if save:
        file_name = f"{folder}/hist_{method}_{x_name}_{y_name}{title_addition}".replace(" ", "")
        print('saved in: ', file_name)
        fig.write_image(f"{file_name}.png", format="png", engine="kaleido")

    return fig

def scatter(df, x, y, x_name=None, y_name=None,  date_range=None, mode='markers', xaxis_range=None, yaxis_range=None, show=False, save=True, folder=""):

    df = df[[x, y]]

    if date_range:
        df[x] = pd.to_datetime(df[x])
        min_date = df[x].min()
        max_date = df[x].max()

        date_range = pd.DataFrame(pd.date_range(min_date,max_date-pd.Timedelta(days=1),freq='d'), columns=[x])
        df = pd.merge(date_range, df, how='left', on=x).fillna(0)

    # create Figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=df[y].values, x=df[x].values, mode=mode))

    if not x_name:
        x_name = x
    if not y_name:
        y_name = y

    # formatting
    if yaxis_range:
        fig.update_layout(yaxis_range=yaxis_range)
    if xaxis_range:
        fig.update_layout(xaxis_range=xaxis_range)

    fig.update_xaxes(title_text=x_name)
    fig.update_yaxes(title_text=y_name)



    if show:
        fig.show()

    if save:
        file_name = f"{folder}/scatter_{x_name}_{y_name}".replace(" ", "")
        print('saved in: ', file_name)
        fig.write_image(f"{file_name}.png", format="png", engine="kaleido")

    return fig



def grouped_bar(df, groups, labels, data_column, label_column, x_name=None, y_name=None, show=False, save=True, folder=""):


    data = []
    for label in labels:
        bar = go.Bar(name=label, x=groups, y=df[df[label_column] == label][data_column].tolist())
        data.append(bar)

    fig = go.Figure(data=data)


    # formatting
    fig.update_layout(barmode='group')
    fig.update_xaxes(title_text=x_name)
    fig.update_yaxes(title_text=y_name)

    if not x_name:
        x_name = 'data_column'

    if not y_name:
        y_name = 'label_column'

    if show:
        fig.show()

    if save:
        file_name = f"{folder}/grouped_bar_{x_name}_{y_name}_by_{label_column}".replace(" ", "")
        print('saved in: ', file_name)
        fig.write_image(f"{file_name}.png", format="png", engine="kaleido")

    return fig


def table(df, column_names=None, title="table", head=5, width_height=None, show=False, save=True, folder=""):

        # select top
        if head:
            df = df.head(head)

        if not column_names:
            column_names = list(df.columns)

        x = [df[y] for y in df.columns]

        # plot table
        headerColor = 'grey'
        rowColor = '#F8F8F8'


        fig = go.Figure(data=[go.Table(
            header=dict(values=column_names,
            line_color=headerColor,
            fill_color=headerColor,
            align=['center','center'],
            height=50,
            font=dict(color='white', size=18)),
            cells=dict(values=x,
             fill_color = rowColor,
            align = ['left', 'center'],
            height=50,
            font = dict(color = 'darkslategray', size = 16)))
        ])

        # formatting
        if width_height:
            fig.update_layout(
                autosize=False,
                width=width_height[0],
                height=width_height[1])

        fig.update_layout(margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=0,
                            pad=0))

        if show:
            fig.show()

        if save:
            file_name = f"{folder}/{title}"
            fig.write_image(f"{file_name}.png", format='png', engine='kaleido')

        return fig

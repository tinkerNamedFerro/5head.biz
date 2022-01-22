from re import template
import pandas_ta as ta
from datetime import *

from ..dash import Dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .data_parsing import *

dropDownOptions =  [{'label': "TRENDING", 'value': "TRENDING"}]

df = getAllTickerData()
df["sma10"] = ta.sma(df.Mentions, length=20)


# Drop of all tickers and an addition option to show all
today = datetime.today()
for i in df[df['Time'] > (today - pd.offsets.Day(10))].sort_values(by='sma10', ascending=False).ticker.unique():
    # Add ticker values to drop down
    dropDownOptions.append({'label': i, 'value': i})


app_layout = html.Div(
    children=[
        html.Div(
            # className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="three columns div-user-controls",
                    children=[
                        html.A(
                            html.Img(
                                # className="logo",
                                # src=app.get_asset_url("dash-logo-new.png"),
                            ),
                            href="https://plotly.com/dash/",
                        ),
                        html.H2("5head.hive /biz crypto insights"),
                        html.P(
                            """Select different parameters to filter the coins commonly talked about"""
                        ),
                        html.Div(
                            children=[
                                #     dbc.Label(
                                #     "Market Cap",
                                #     html_for="stroke-width",
                                # ),
                                # # Slider for specifying stroke width
                                # dcc.RangeSlider(
                                #     id='market-cap-slider',
                                #     min=0,
                                #     max=11,
                                #     step=None,
                                #     allowCross=False,
                                #     marks={
                                #         0: '0',
                                #         1: '10M',
                                #         2: '50M',
                                #         3: '100M',
                                #         4: '500M',
                                #         5: '1B',
                                #         6: '10B',
                                #         7: '50B',
                                #         8: '100B',
                                #         9: '500B',
                                #         10: '1T',
                                #         11: '2T',
                                #     },
                                #     value=[0, 11]
                                # ),
                                dcc.Dropdown(
                                    id='ticker-dropdown',
                                    options=dropDownOptions,
                                    value="TRENDING"
                                ),
                    
                                html.Div(id='output-container-range-slider'),
                            ]
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="nine columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="line-chart"),
                    ],
                ),
            ],
        )
    ]
)


    
    
# Use the following function when accessing the value of 'my-range-slider'
# in callbacks to transform the output value to logarithmic
def transform_value(value):
    switcher={
            0:0,
            1:10000000, #10M
            2:50000000, #50M
            3:100000000,  #100M
            4:500000000,  #500M
            5:1000000000,   #1B
            6:10000000000,  #10B
            7:50000000000,  #50B
            8:100000000000, #100B
            9:500000000000, #500B
            10:1000000000000, #1T
            11:2000000000000 #2T
            }
    return switcher.get(value,"Invalid day of week")

            
#  Market Cap and ticker selector 
def update_line_chart(ticker_selector): #def update_line_chart(market, ticker_selector):
    df = getAllTickerData()
    # Get 10 day average sort by it 
    df["sma10"] = ta.sma(df.Mentions, length=20)
    # df = df.sort_values(by=['sma10'])

    # df = df['marketCap'].nlargest(n=10)
    trendingTickers = []
    # Drop of all tickers and an addition option to show all
    today = datetime.today()
    for i in df[df['Time'] > (today - pd.offsets.Day(10))].sort_values(by='sma10', ascending=False).ticker.unique():
        # Add ticker values to drop down
        dropDownOptions.append({'label': i, 'value': i})
        # Add to trendingTickers
        if len(trendingTickers) <= 10:
            trendingTickers.append(i) 
    df = df[df["ticker"].isin(trendingTickers)]
     
    # converting 1-10 to market cap intervals
    market = [0, 11]
    transformed_value = [transform_value(v) for v in market]
    print(transformed_value)
    # Make mask where true if in range
    marketCapMask = (df.marketCap >= transformed_value[0]) & (df.marketCap <= transformed_value[1])

    # ticker selector
    if ticker_selector and ticker_selector != "TRENDING": 
        tickerMask  = (df.ticker.str.fullmatch(ticker_selector)) == False
    else:
        tickerMask  = (df.ticker.str.contains("TRENDING")) == True
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Only show rows where mask is true


    graphingDf = df[~(marketCapMask & tickerMask)]
    grouped = graphingDf.groupby('ticker')


    for name, group in grouped:
            fig.add_trace(go.Scatter(x=group.Time, y=group.Mentions,# color='ticker',
                        mode='lines',
                        name=name),
                    row=1, 
                    col=1,
                    secondary_y=False) 
    # Show price when only one coin is selected
    if ticker_selector and ticker_selector != "TRENDING": 
        # priceDF = getChartById( graphingDf['coinGeckoId'].iloc[0])
        daysOfMentionData = (datetime.today() - graphingDf['Time'].min()).days
        priceDF = getHourlyChartById( graphingDf['coinGeckoId'].iloc[0], daysOfMentionData)
        # Only include pricing data which mention data exists for
        priceDF = priceDF[priceDF.Time >= df.Time.min()]
        fig.add_trace(go.Scatter(x=priceDF.Time, y=priceDF.Price,
                    mode='lines',
                    name='Price'), 
                row=1,
                col=1,
                secondary_y=True)
        # Add SMA to graph
        fig.add_trace(go.Scatter(x=graphingDf.Time, y=graphingDf.sma10,
                    mode='lines',
                    name='SMA10'), 
                row=1,
                col=1,
                secondary_y=False)
    # Change graph height and theme
    fig.update_layout(
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        #showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        # dragmode="select",
        font=dict(color="white"),
        # autosize=False,
        height=800,
        legend = dict(x = 0.1, y = 0.8),
        yaxis=dict(
            range=[2, graphingDf['Mentions'].max()+100],
            )
        # template="plotly_dark"
    )
    return fig

def init_dash(server):
    dash_app = Dash(server=server, routes_pathname_prefix="/biz/", )
    
    
    dash_app.callback(
        Output("line-chart", "figure"),
        [
            # Input('market-cap-slider', 'value'),
            Input('ticker-dropdown', 'value')

        ],
    )(update_line_chart)

    dash_app.layout = app_layout
    
    return dash_app.server

if __name__ == '__main__':
    app.run_server(debug=True)


import pandas as pd
import streamlit as st
import requests
import numpy as np
import altair as alt
import pydeck as pdk
from numerize.numerize import numerize
import plotly.graph_objects as go
import plotly.express as px
import geopandas as gpd
import json

st.set_page_config(layout="wide")

def retrieve(n: int):
    '''
    Retrieve data from Data.gov.sg API.
    '''
    resource_id = "f1765b54-a209-4718-8d38-a39237f502b3"
    url_string = f"https://data.gov.sg/api/action/datastore_search?resource_id={resource_id}&limit={n}" 
    try:
        response = requests.get(url_string, headers = {"User-Agent": "Mozilla/5.0"}).json()
        return response
    except Exception as e:
        print(f"Error occurred: {e}")
        print(e)
        print(url_string)

def round_up(number, nearest: int, direction: bool = True):
    '''
    Round number up to the nearest value.
        Set direction = False to round down instead.
    '''
    if direction == True:
        return int(np.ceil(number / nearest)) * nearest
    elif direction == False:
        return int(np.floor(number / nearest)) * nearest
    else:
        return None

@st.experimental_memo(ttl=2_630_000) # dataset is updated monthly
def get_data():
    body = retrieve(1)
    limit = body['result']['total']
    body = retrieve(limit)
    content = pd.DataFrame(body['result']['records'])
    return content

df = get_data()
df['address'] = df['block'] + ' ' + df['street_name']

@st.experimental_memo(max_entries=1)
def get_coords_df():
    return pd.read_csv('/app/dsi33-shawn/Side_Projects/HDB_Resale_Price/hdb_coords.csv')
    # return pd.read_csv('C:/Users/brkit/Documents/DSI33-Shawn/Side_Projects/HDB_Resale_Price/hdb_coords.csv')

hdb_coordinates = get_coords_df()
df_merged = df.merge(hdb_coordinates, how = 'left', on = 'address')
df_merged.drop(columns = '_id', inplace = True)
df_merged['month'] = pd.to_datetime(df_merged['month'], format = "%Y-%m", errors = "raise")
df_merged['town'] = df_merged['town'].str.title()

@st.experimental_singleton
def get_chloropeth():
    with open('./master-plan-2014-planning-area-boundary-no-sea.json') as f:
        return json.load(f)
#     return gpd.read_file("C:/Users/brkit/Documents/DSI33-Shawn/Side_Projects/HDB_Resale_Price/master-plan-2014/master-plan-2014-planning-area-boundary-no-sea-shp/MP14_PLNG_AREA_NO_SEA_PL.shp")

geo_df = get_chloropeth()

towns = df_merged['town'].unique()
towns = sorted(towns)
towns.insert(0, 'All')

years = list(range(df_merged['month'].max().year, df_merged['month'].min().year - 1, -1))
years.insert(0, 'All')

# create sidebar for filtering dashboard
with st.sidebar:
    st.header("Filter options")
    town_option = st.selectbox(
        label = 'District',
        options = towns
    )

    year = st.selectbox(
        label= 'Year',
        options = years
    )

    date_range = st.slider(
        label = 'Transaction Date Range', 
        min_value = df_merged['month'].min().date(),
        max_value = df_merged['month'].max().date(),
        value = (df_merged['month'].min().date(), df_merged['month'].max().date()),
        format = "MMM-Y",
        disabled=True,
    )
    
# min_date = pd.to_datetime(date_range[0])
# max_date = pd.to_datetime(date_range[1])

with st.container():
    st.title("Singapore HDB Resale Price from 2017")
    st.markdown("This dashboard is inspired by [Inside Airbnb](http://insideairbnb.com/), and is an ongoing project to document my learning to use Streamlit and various plotting libraries to create an interactive dashboard. While this could perhaps be more easily resolved by using PowerBI or Tableau, I am taking the opportunity to explore various Python libraries and understand their documentation.")
    st.markdown("The project is rather close to heart since I've been looking out for a resale flat after getting married in mid-2022, so hopefully this dashboard can contribute to my purchase decision. :blush:")
    st.markdown("Data from the dashboard is retrieved from Singapore's [Data.gov.sg](https://data.gov.sg/), a free portal with access to publicly-available datasets from over 70 public agencies made available under the terms of the [Singapore Open Data License](https://data.gov.sg/open-data-licence). In particular, we dive into the HDB resale flat prices [dataset](https://data.gov.sg/dataset/resale-flat-prices), while town boundaries in the chloropeth map are retrieved from [Master Plan 2014 Planning Area Boundary](https://data.gov.sg/dataset/master-plan-2014-planning-area-boundary-no-sea).")

st.markdown("---")

with st.container():
    st.markdown("## Data Extraction & Transformation")
    st.markdown("We utilise the Data.gov.sg API to extract our required data. Let's check out the first 3 rows of our dataset.")
    st.dataframe(df.head(3))
    st.markdown("The dataset provides various key information regarding the HDB flats, including location, flat type and lease information.")
    st.markdown("We are interested to display the transactions on a map, so we'll need to convert the addresses into coordinates to do so.")
    st.markdown("Using the [OneMap API](https://www.onemap.gov.sg/docs/) provided by the Singapore Land Authority, I retrieved and stored the Latitude and Longitude coordinates for all the 12,573 HDB blocks in Singapore.")

st.markdown("---")

# filter df based on selected parameters
if town_option == 'All':
    if year == 'All':
        df_filtered = df_merged
    else:
        # df_filtered = df_merged.query('month >= @min_date & month <= @max_date')
        df_filtered = df_merged.query('month.dt.year == @year')
else:
    if year == 'All':
        df_filtered = df_merged.query('town.str.contains(@town_option)')
    else:
    # df_filtered = df_merged.query('month >= @min_date & month <= @max_date & town.str.contains(@town_option)')
        df_filtered = df_merged.query('month.dt.year == @year & town.str.contains(@town_option)')

map_df = df_filtered.groupby('town').resale_price.median().reset_index()
median_resale_price = df_filtered.groupby('month').resale_price.median().reset_index()
resale_transactions = df_filtered.groupby('month').town.count().reset_index()

with st.container():
    # st.subheader(f'{town_option} from {min_date:%b-%Y} to {max_date:%b-%Y}')
    st.markdown(f'## {town_option} transactions in {year}')
    # display key metrics
    st.markdown("### Key Metrics")
    # row 1
    met1, met2, met3 = st.columns(3)
    met1.metric(
        label = 'Total Resale Transactions',
        value = f"{df_filtered['resale_price'].count().item():,}",
        help = 'Total resale transactions during this period'
    )
    met2.metric(
        label = 'Total Transaction Value',
        value = f'S${numerize(df_filtered["resale_price"].astype(float).sum())}',
        help = 'Total value of all transactions during this period'
    )
    # met3.metric(
    #     label = 'Percentage',
    #     value = f"{(df_filtered['resale_price'].count() / len(df_merged.query('month >= @min_date & month <= @max_date')) * 100):.2f}%",
    #     help = f'Proportion of total transactions for this period'
    # )
    # row 2
    met4, met5, met6 = st.columns(3)
    met4.metric(
        label = 'Lowest Price',
        value = f'S${df_filtered["resale_price"].astype(float).min():,.0f}',
        help = 'Lowest resale transaction price during this period'
    )
    met5.metric(
        label = 'Highest Price',
        value = f'S${numerize(df_filtered["resale_price"].astype(float).max())}',
        help = 'Highest resale transaction price during this period'
    )
    met6.metric(
        label = 'Median Price',
        value = f'S${int(df_filtered.resale_price.median()):,}',
        help = 'Median price of all transactions during this period'
    )

st.markdown("---")

with st.container():
    fig = px.choropleth_mapbox(
        map_df,
        geojson = geo_df,
        locations = 'town',
        color = 'resale_price',
        featureidkey = 'properties.PLN_AREA_N',
        color_continuous_scale = "Sunsetdark",
        center = {'lat': 1.35, 'lon': 103.80},
        mapbox_style = 'carto-positron',
        opacity = 0.7,
        labels = {
            'town': 'Town',
            'resale_price':'Median Resale Price'
            },
        zoom = 10,
    )

    fig.update_layout(
        title = {
            'text': f'Median Resale Price by Town in {year}'
        },
        height = 550,
        width = 700,
    )

    if town_option != 'All':
        fig.update_coloraxes(showscale=False)

    st.plotly_chart(fig, use_container_width= True)

with st.container():
    # plot line graph
    median_price = alt.Chart(
        median_resale_price, 
        title = 'Median Resale Price by Month'
    ).mark_line(
        point = True
    ).encode(
        alt.X(
            'month', 
            axis = alt.Axis(
                formatType = 'time', 
                format = '%b-%y', 
                title = 'Transaction Period',
                grid = False,
                tickCount= 'month' 
                )),
        alt.Y(
            'resale_price', 
            axis = alt.Axis(
                title = "Resale Price (S$)",
                formatType= 'number',
                format= '~s'
                ),
            scale = alt.Scale(
                domain = [
                    round_up(median_resale_price['resale_price'].min(), 50_000, False),
                    round_up(median_resale_price['resale_price'].max(), 50_000)
                ]
            )),
    ).properties(
        height = 300,
    )
    
    # creates selection that chooses the nearest point
    nearest = alt.selection_single(nearest = True, on = 'mouseover',
                        fields = ['month'], empty = 'none')
    
    # selectors that tell us the x-value of the cursor
    selectors = median_price.mark_point(color = 'red').encode(
        x = 'month',
        opacity = alt.condition(nearest, alt.value(1), alt.value(0)),
        tooltip = [
            alt.Tooltip('month', title = 'Transaction Period', format = '%b-%y'),
            alt.Tooltip('resale_price', title = 'Median Resale Price', format = '$,'),
            ],
    ).add_selection(
        nearest
    )

    # draw a rule at location of selection
    rule = median_price.mark_rule(color = 'gray').encode(
        x = 'month',
    ).transform_filter(
        nearest
    )

    # visualise number of transactions by month
    transactions_by_month = alt.Chart(
        resale_transactions,    
        title = 'Monthly Transactions'
    ).mark_line(
        point = True
    ).encode(
        alt.X(
            'month', 
            axis = alt.Axis(
                formatType = 'time', 
                format = '%b-%y', 
                title = 'Transaction Period',
                grid = False,
                tickCount= 'month' 
                )),
        alt.Y(
            'town', 
            axis = alt.Axis(
                title = "Transactions",
                formatType= 'number',
                # format= '~s'
                ),
            scale = alt.Scale(
                domain = [
                    round_up(resale_transactions['town'].min(), 250, False),
                    round_up(resale_transactions['town'].max(), 250)
                ]
            )),
    ).properties(
        height = 300,
    )
    
    st.altair_chart(median_price + selectors + rule | transactions_by_month, use_container_width = True)

with st.container():
    st.markdown("Click to filter by flat types, hold shift to select multiple options.")
    selector = alt.selection_multi(empty='all', fields=['flat_type'])

    base = alt.Chart(
        df_filtered,
    ).add_selection(selector)

    flat_type = base.mark_bar().encode(
        alt.X('count()', axis = alt.Axis(title = 'Transactions')),
        alt.Y('flat_type:N', axis = alt.Axis(title = 'Flat Type')),
        color = alt.condition(selector, 'flat_type:N', alt.value('lightgray'), legend = None),
        tooltip = [
            alt.Tooltip('flat_type', title = 'Flat Type'),
            alt.Tooltip('count()', title = 'Transactions', format = ','),
        ]
    ).properties(
        height = 300,
    )

    floor_area = base.mark_bar(
        opacity = 0.8,
        binSpacing = 0
    ).encode(
        alt.X('floor_area_sqm:Q', bin = alt.Bin(step=5), axis = alt.Axis(title = 'Floor Area (sqm)')),
        alt.Y('count()', stack = None, axis = alt.Axis(title = 'Count')),
        alt.Color('flat_type:N', legend = None),
    ).transform_filter(selector).properties(
        height = 300,
    )

    st.altair_chart(flat_type | floor_area, use_container_width = True)
import pandas as pd
import streamlit as st
import requests
import pydeck as pdk
import numpy as np
from datetime import datetime as dt


def retrieve(n):
    resource_id = "f1765b54-a209-4718-8d38-a39237f502b3"
    url_string = f"https://data.gov.sg/api/action/datastore_search?resource_id={resource_id}&limit={n}" 
    try:
        response = requests.get(url_string, headers={"User-Agent": "Mozilla/5.0"}).json()
        return response
    except Exception as e:
        print(f"Error occurred: {e}")
        print(e)
        print(url_string)

@st.experimental_memo(ttl=2_630_000) # dataset is updated monthly
def get_data():
    body = retrieve(1)
    limit = body['result']['total']
    body = retrieve(limit)
    content = pd.DataFrame(body['result']['records'])
    return content

# consider how to store copy of data since this is updated monthly
df = get_data()
df['address'] = df['block'] + ' ' + df['street_name']

@st.experimental_memo(max_entries=1)
def get_coords_df():
    return pd.read_csv('hdb_coords.csv')

hdb_coordinates = get_coords_df()
df_merged = df.merge(hdb_coordinates, how='inner', on='address')
df_merged.drop(columns='_id', inplace=True)
df_merged['month'] = pd.to_datetime(df_merged['month'], format="%Y-%m", errors="raise")

with st.sidebar:
    date_range = st.slider(
        label = 'Transaction Date Range', 
        min_value = df_merged['month'].min().date(),
        max_value = df_merged['month'].max().date(),
        value = (dt.strptime('2021-01', "%Y-%m").date(), dt.strptime('2021-12', "%Y-%m").date()),
        format = "YYYY-MM",
        )

st.title("Singapore HDB Resale Price from 2017")
st.markdown("This dashboard is inspired by [Inside Airbnb](http://insideairbnb.com/), and documents my learning to use Streamlit and various plotting libraries to create an interactive dashboard.")
st.markdown("Data from the dashboard is retrieved from Singapore's [Data.gov.sg](https://data.gov.sg/), a free portal with access to publicly-available datasets from over 70 public agencies. In particular, we dive into the HDB resale flat prices based on registration date from Jan 2017 onwards with this [dataset](https://data.gov.sg/dataset/resale-flat-prices).")
st.markdown("---")

st.subheader("Data Extraction")
st.markdown("We utilise the Data.gov.sg API to extract our required data. Let's check out the first 5 rows of our dataset.")
st.dataframe(df_merged.head(5))
st.markdown("The dataset provides various key information regarding the HDB flats, including location, flat type and lease information.")

st.markdown("We are interested to display the transactions on a map, so we'll need to convert the addresses into coordinates to do so.")
st.markdown("using the [OneMap API](https://www.onemap.gov.sg/docs/) provided by the Singapore Land Authority, we have retrieved and stored the Latitude and Longitude coordinates for all the 12,573 HDB blocks in Singapore.")


min_date = pd.to_datetime(date_range[0])
max_date = pd.to_datetime(date_range[1])

chart_data = pd.DataFrame(
   np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
   columns=['lat', 'lon'])

colours = [[240,249,232],[204,235,197],[168,221,181],[123,204,196],[67,162,202],[8,104,172]]

st.pydeck_chart(pdk.Deck(
    map_provider='mapbox',
    map_style='light',
    initial_view_state=pdk.ViewState(
        latitude=1.290270,
        longitude=103.851959,
        zoom=9,
        pitch=45,
    ),
    layers=[
        pdk.Layer(
           'HexagonLayer',
           data=df_merged[(df_merged['month'] > min_date) & (df_merged['month'] < max_date)],
           get_position='[longitude, latitude]',
           radius=50,
           elevation_scale=4,
           elevation_range=[0, 1000],
           pickable=True,
           extruded=True,
           colours=colours,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=chart_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))

# pd.merge (inner join with long lat)
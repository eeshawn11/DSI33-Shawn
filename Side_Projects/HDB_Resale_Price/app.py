import pandas as pd
import streamlit as st
import requests
import numpy as np
import altair as alt
from numerize.numerize import numerize

st.set_page_config(layout="wide")

def retrieve(n):
    resource_id = "f1765b54-a209-4718-8d38-a39237f502b3"
    url_string = f"https://data.gov.sg/api/action/datastore_search?resource_id={resource_id}&limit={n}" 
    try:
        response = requests.get(url_string, headers = {"User-Agent": "Mozilla/5.0"}).json()
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
    return pd.read_csv('/app/dsi33-shawn/Side_Projects/HDB_Resale_Price/hdb_coords.csv')
    # return pd.read_csv('hdb_coords.csv')

hdb_coordinates = get_coords_df()
df_merged = df.merge(hdb_coordinates, how = 'inner', on = 'address')
df_merged.drop(columns = '_id', inplace = True)
df_merged['month'] = pd.to_datetime(df_merged['month'], format = "%Y-%m", errors = "raise")
df_merged['town'] = df_merged['town'].str.title()

towns = df_merged['town'].unique()
towns = sorted(towns)
towns.insert(0, 'All')

# create sidebar for filtering dashboard
with st.sidebar:
    st.header("Filter options")
    town_option = st.selectbox(
        label = 'District',
        options = towns
    )

    date_range = st.slider(
        label = 'Transaction Date Range', 
        min_value = df_merged['month'].min().date(),
        max_value = df_merged['month'].max().date(),
        value = (df_merged['month'].min().date(), df_merged['month'].max().date()),
        format = "MMM-Y",
    )
    
min_date = pd.to_datetime(date_range[0])
max_date = pd.to_datetime(date_range[1])

with st.container():
    st.title("Singapore HDB Resale Price from 2017")
    st.markdown("This dashboard is inspired by [Inside Airbnb](http://insideairbnb.com/), and is an ongoing project to document my learning to use Streamlit and various plotting libraries to create an interactive dashboard. While this could perhaps be more easily resolved by using PowerBI or Tableau, I am taking the opportunity to explore various Python libraries and understand their documentation.")
    st.markdown("Data from the dashboard is retrieved from Singapore's [Data.gov.sg](https://data.gov.sg/), a free portal with access to publicly-available datasets from over 70 public agencies. In particular, we dive into the HDB resale flat prices based on registration date from Jan 2017 onwards with this [dataset](https://data.gov.sg/dataset/resale-flat-prices).")

st.markdown("---")

with st.container():
    st.subheader("Data Extraction & Transformation")
    st.markdown("We utilise the Data.gov.sg API to extract our required data. Let's check out the first 3 rows of our dataset.")
    st.dataframe(df.head(3))
    st.markdown("The dataset provides various key information regarding the HDB flats, including location, flat type and lease information.")
    st.markdown("We are interested to display the transactions on a map, so we'll need to convert the addresses into coordinates to do so.")
    st.markdown("using the [OneMap API](https://www.onemap.gov.sg/docs/) provided by the Singapore Land Authority, I retrieved and stored the Latitude and Longitude coordinates for all the 12,573 HDB blocks in Singapore.")

st.markdown("---")

# filter df based on selected parameters
if town_option == 'All':
    df_filtered = df_merged.query('month >= @min_date & month <= @max_date')
else:
    df_filtered = df_merged.query('month >= @min_date & month <= @max_date & town.str.contains(@town_option)')

with st.container():
    # display key metrics
    st.subheader("Key Metrics")
    # row 1
    met1, met2, met3 = st.columns(3)
    met1.metric(
        label = 'Transactions',
        value = numerize(df_filtered['resale_price'].count().item()),
        help = 'Total resale transactions during this period'
    )
    met2.metric(
        label = 'Percentage',
        value = f"{(df_filtered['resale_price'].count() / len(df_merged.query('month >= @min_date & month <= @max_date')) * 100):.2f}%",
        help = f'Proportion of total transactions for this period'
    )
    met3.metric(
        label = 'Total Transaction Value',
        value = f'S${numerize(df_filtered["resale_price"].astype(float).sum())}',
        help = 'Total value of all transactions during this period'
    )
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
    st.subheader(f'{town_option} from {min_date:%b-%Y} to {max_date:%b-%Y}')
    tab1, tab2 = st.tabs(['Median Resale Price', 'Flat Type'])

    with tab1:
        # create data source for Altair chart
        tab1_source = df_filtered.groupby('month').resale_price.median().reset_index()

        # plot line graph
        median_price = alt.Chart(
            tab1_source, 
            title = 'Median Resale Price by Month'
        ).mark_line(
            point = True
        ).encode(
            alt.X('month', axis = alt.Axis(formatType = 'time', format = '%b-%y', title = 'Transaction Period')),
            alt.Y('resale_price', axis = alt.Axis(title = "Resale Price (S$)")),
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
        
        st.altair_chart(median_price + selectors + rule, use_container_width = True)


    with tab2:
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

# chart_data = pd.DataFrame(
#    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
#    columns=['lat', 'lon'])

   
# colours = [[240,249,232],[204,235,197],[168,221,181],[123,204,196],[67,162,202],[8,104,172]]

# st.pydeck_chart(pdk.Deck(
#     map_provider='mapbox',
#     map_style='light',
#     initial_view_state=pdk.ViewState(
#         latitude=1.290270,
#         longitude=103.851959,
#         zoom=9,
#         pitch=45,
#     ),
#     layers=[
#         pdk.Layer(
#            'HexagonLayer',
#            data=df_merged[(df_merged['month'] > min_date) & (df_merged['month'] < max_date)],
#            get_position='[longitude, latitude]',
#            radius=50,
#            elevation_scale=4,
#            elevation_range=[0, 1000],
#            pickable=True,
#            extruded=True,
#            colours=colours,
#         ),
#         pdk.Layer(
#             'ScatterplotLayer',
#             data=chart_data,
#             get_position='[lon, lat]',
#             get_color='[200, 30, 0, 160]',
#             get_radius=200,
#         ),
#     ],
# ))

# pd.merge (inner join with long lat)
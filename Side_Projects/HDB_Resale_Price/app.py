import pandas as pd
import streamlit as st
import requests

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

def get_data():
    body = retrieve(1)
    limit = body['result']['total']
    body = retrieve(limit)
    content = pd.DataFrame(body['result']['records'])
    return content

def get_coordinates(address):
    response = requests.get(f'https://developers.onemap.sg/commonapi/search?searchVal={address}&returnGeom=Y&getAddrDetails=Y&pageNum=1').json()
    results = pd.DataFrame(response['results'])
    return print(results)
    if len(resultsdict)>0:
        return resultsdict[0]['LATITUDE'], resultsdict[0]['LONGITUDE']
    else:
        return None

df = get_data()
df.drop(columns='_id', inplace=True)

with st.sidebar:
    st.slider('Transaction Date', 0.0, 100.0, (25.0 , 75.0))

st.title("Singapore HDB Resale Price from 2017")
st.markdown("This dashboard is inspired by [Inside Airbnb](http://insideairbnb.com/), and documents my learning to use Streamlit and various plotting libraries to create an interactive dashboard.")
st.markdown("Data from the dashboard is retrieved from Singapore's [Data.gov.sg](https://data.gov.sg/), a free portal with access to publicly-available datasets from over 70 public agencies. In particular, we dive into the HDB resale flat prices based on registration date from Jan 2017 onwards with this [dataset](https://data.gov.sg/dataset/resale-flat-prices).")
st.markdown("---")

st.subheader("Data Extraction")
st.markdown("We utilise the Data.gov.sg API to extract our required data. Let's check out the first 5 rows of our dataset.")
st.dataframe(df.head(5))
st.markdown("The dataset provides various key information regarding the HDB flats, including location, flat type and lease information.")

st.markdown("We are interested to plot the flats on a map, so we'll need to convert the addresses into coordinates to do so.")
df['address'] = df['block'] + ' ' + df['street_name']
st.write(df['address'].head())

with st.echo():
    st.write(get_coordinates(df['address']))






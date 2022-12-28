import pandas as pd
import streamlit as st
import requests
import json

st.set_page_config(layout="wide")


def retrieve(n: int):
    """
    Retrieve data through Data.gov.sg API.
    """
    resource_id = "f1765b54-a209-4718-8d38-a39237f502b3"
    url_string = f"https://data.gov.sg/api/action/datastore_search?resource_id={resource_id}&limit={n}"
    try:
        response = requests.get(
            url_string, headers={"User-Agent": "Mozilla/5.0"}
        ).json()
        return response
    except Exception as e:
        print(f"Error occurred: {e}")
        print(e)
        print(url_string)


@st.experimental_memo(ttl=2_630_000)  # dataset is updated monthly
def get_data():
    body = retrieve(1)
    limit = body["result"]["total"]
    body = retrieve(limit)
    content = pd.DataFrame(body["result"]["records"])
    return content


df = get_data()
df["address"] = df["block"] + " " + df["street_name"]


@st.experimental_memo(max_entries=1)
def get_coords_df():
    return pd.read_csv(
        "/app/dsi33-shawn/Side_Projects/HDB_Resale_Price/assets/hdb_coords.csv"
    )
    # return pd.read_csv(
    #     "C:/Users/brkit/Documents/DSI33-Shawn/Side_Projects/HDB_Resale_Price/assets/hdb_coords.csv"
    # )


hdb_coordinates = get_coords_df()
df_merged = df.merge(hdb_coordinates, how="left", on="address")
df_merged.drop(columns="_id", inplace=True)
df_merged["month"] = pd.to_datetime(df_merged["month"], format="%Y-%m", errors="raise")
df_merged["town"] = df_merged["town"].str.title()
df_merged["resale_price"] = df_merged["resale_price"].astype(float).astype(int)

if "df" not in st.session_state:
    st.session_state.df = df_merged


@st.experimental_singleton
def get_chloropeth():
    with open(
        "/app/dsi33-shawn/Side_Projects/HDB_Resale_Price/assets/master-plan-2014-planning-area-boundary-no-sea.json"
    ) as f:
        # with open(
        #     "C:/Users/brkit/Documents/DSI33-Shawn/Side_Projects/HDB_Resale_Price/assets/master-plan-2014-planning-area-boundary-no-sea.json"
        # ) as f:
        return json.load(f)


if "geo_df" not in st.session_state:
    st.session_state.geo_df = get_chloropeth()

towns = df_merged["town"].unique()
towns = sorted(towns)
towns.insert(0, "All")
if "towns" not in st.session_state:
    st.session_state.towns = towns

years = list(
    range(df_merged["month"].max().year, df_merged["month"].min().year - 1, -1)
)
years.insert(0, "All")
if "years" not in st.session_state:
    st.session_state.years = years

with st.container():
    st.title("Singapore HDB Resale Price from 2017")
    st.markdown(
        "This dashboard is inspired by [Inside Airbnb](http://insideairbnb.com/), and is an ongoing project to document my learning with using Streamlit and various plotting libraries to create an interactive dashboard. While this could perhaps be more easily resolved by using PowerBI or Tableau, I am taking the opportunity to explore various Python libraries and understand their documentation."
    )
    st.markdown(
        "The project is rather close to heart since I've been looking out for a resale flat after getting married in mid-2022, so hopefully this dashboard can contribute to my purchase decision. :blush:"
    )
    st.markdown(
        "Data from the dashboard is retrieved from Singapore's [Data.gov.sg](https://data.gov.sg/), a free portal with access to publicly-available datasets from over 70 public agencies made available under the terms of the [Singapore Open Data License](https://data.gov.sg/open-data-licence). In particular, we dive into the HDB resale flat prices [dataset](https://data.gov.sg/dataset/resale-flat-prices), while town boundaries in the chloropeth map are retrieved from [Master Plan 2014 Planning Area Boundary](https://data.gov.sg/dataset/master-plan-2014-planning-area-boundary-no-sea)."
    )

st.markdown("---")

with st.container():
    st.markdown("## Data Extraction & Transformation")
    st.markdown(
        "We utilise the Data.gov.sg API to extract our required data. Let's check out the first 3 rows of our dataset."
    )
    st.dataframe(df.head(3))
    st.markdown(
        "The dataset provides various key information regarding the HDB flats, including location, flat type and lease information. Using the [OneMap API](https://www.onemap.gov.sg/docs/) provided by the Singapore Land Authority, I retrieved and added in the coordinates of the HDB blocks to plot onto a map."
    )
    st.markdown(
        "After performing some transformations on the data, notice the new columns that have been added."
    )
    st.dataframe(df_merged.head(3))
st.markdown("---")

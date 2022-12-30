import pandas as pd
import streamlit as st
import requests
import json
from shapely.geometry import Point, Polygon

st.set_page_config(layout="wide")


def retrieve_data(n: int):
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
    body = retrieve_data(1)
    limit = body["result"]["total"]
    body = retrieve_data(limit)
    content = pd.DataFrame(body["result"]["records"])
    return content


@st.experimental_memo(max_entries=1)
def get_coords_df():
    return pd.read_csv(
        "/app/dsi33-shawn/Side_Projects/HDB_Resale_Price/assets/hdb_coords.csv"
    )
    # return pd.read_csv(
    #     "C:/Users/brkit/Documents/DSI33-Shawn/Side_Projects/HDB_Resale_Price/assets/hdb_coords.csv"
    # )


@st.experimental_singleton
def get_chloropeth():
    with open(
        "/app/dsi33-shawn/Side_Projects/HDB_Resale_Price/assets/master-plan-2014-planning-area-boundary-no-sea.json"
    ) as f:
    # with open(
    #     "C:/Users/brkit/Documents/DSI33-Shawn/Side_Projects/HDB_Resale_Price/assets/master-plan-2014-planning-area-boundary-no-sea.json"
    # ) as f:
        return json.load(f)

# not used, need to figure out if there's a faster way to run the polygon check
def check_point(polygon, point):
    if polygon.contains(point):
        return True
    return False


def check_polygons(point):
    for index, area in enumerate(polygons):
        if area.contains(point):
            return planning_areas[index]


df = get_data()
hdb_coordinates = get_coords_df()

if "geo_df" not in st.session_state:
    st.session_state.geo_df = get_chloropeth()


@st.experimental_memo(max_entries=1)
def get_planning_areas():
    planning_areas = []
    polygons = []
    for i in range(len(st.session_state.geo_df["features"])):
        planning_areas.append(
            st.session_state.geo_df["features"][i]["properties"]["PLN_AREA_N"]
        )
        try:
            polygons.append(
                Polygon(
                    st.session_state.geo_df["features"][i]["geometry"]["coordinates"][0]
                )
            )
        except:
            polygons.append(
                Polygon(
                    st.session_state.geo_df["features"][i]["geometry"]["coordinates"][
                        0
                    ][0]
                )
            )
    return planning_areas, polygons


planning_areas, polygons = get_planning_areas()

with st.container():
    st.title("Singapore HDB Resale Price from 2017")
    st.markdown(
        """
        This dashboard is inspired by [Inside Airbnb](http://insideairbnb.com/) and various other dashboards I've come across on the web. 
        As a new data professional, this is an ongoing project to document my learning with using Streamlit and various Python libraries 
        to create an interactive dashboard. While this could perhaps be more easily created using PowerBI or Tableau, I am also taking the 
        opportunity to explore the various Python plotting libraries and understand their documentation.

        The project is rather close to heart since I've been looking out for a resale flat after getting married in mid-2022, although with 
        the recent surge in resale prices as of 2022, it still remains out of reach. Hopefully this dashboard can help contribute to my 
        eventual purchase decision, although that may also require adding in various datasets beyond the current historical information.

        Data from the dashboard is retrieved from Singapore's [Data.gov.sg](https://data.gov.sg/), a free portal with access to publicly-available 
        datasets from over 70 public agencies made available under the terms of the [Singapore Open Data License](https://data.gov.sg/open-data-licence). 
        In particular, we dive into the HDB resale flat prices [dataset](https://data.gov.sg/dataset/resale-flat-prices), while town boundaries 
        in the chloropeth map are retrieved from [Master Plan 2014 Planning Area Boundary](https://data.gov.sg/dataset/master-plan-2014-planning-area-boundary-no-sea).
        """
    )

st.markdown("---")

with st.container():
    st.markdown("## Background")
    st.markdown(
        """
        The [Housing & Development Board (HDB)](https://www.hdb.gov.sg/cs/infoweb/homepage) is Singapore's public housing authority, responsible for 
        planning and developing affordable accommodation for residents in Singapore. First established in 1960, over 1 million flats have since been completed 
        in 23 towns and 3 estates across the island.

        Aspiring homeowners generally have a few options when they wish to purchase their first home, either purchasing a new flat directly from HDB, or 
        purchasing an existing flat from the resale market.
        
        While new flats have been constantly developed to meet the needs of the growing population, HDB has been operating on a Build To Order (BTO) 
        since 2001. As the name suggests, the scheme allows the government to build based on actual demand, requiring new developments to meet 
        a minimum application rate before a tender for construction is called. This generally requires a waiting period of around 3 - 4 years for completion.

        However, 2 years of stoppages and disruptions during COVID caused delays to various projects, lengthening the wait time to around 5 years. This  
        caused many people to turn to the resale market instead. Since these are existing developments, resale transactions can usually be expected to 
        complete within 6 months or so, which is a significant reduction in wait time. This surge in demand has also caused a sharp increase in resale prices,
        with many flats even crossing the S$1 million mark.
        """
    )

st.markdown("---")

with st.container():
    st.markdown("## Data Extraction & Transformation")
    st.markdown(
        "We utilise the Data.gov.sg API to extract our required data. Let's check out the dataset to see what it includes."
    )
    st.dataframe(df.head(), use_container_width=True)
    st.markdown(
        """
        The dataset provides key information regarding the resale transactions since 2017, including location, flat type and lease information. The information 
        is clean and free of missing values, although we will still need to perform some transformations for use in our visualisations.
        """
    )
    with st.echo():
        df.shape[0]
    st.markdown(
        "Checking the shape of the dataframe shows us the total number of rows, each of which represents a unique resale transaction based on the date of registration."
    )

st.markdown("---")

# df["address"] = df["block"] + " " + df["street_name"]

# df_merged = df.merge(hdb_coordinates, how="left", on="address")
# df_merged.drop(columns="_id", inplace=True)
# df_merged["month"] = pd.to_datetime(df_merged["month"], format="%Y-%m", errors="raise")
# df_merged.rename(columns={'town': 'town_original'}, inplace=True)
# df_merged["point"] = df_merged.apply(lambda x: Point(x.longitude, x.latitude), axis=1)
# df_merged["town"] = df_merged["point"].apply(check_polygons)
# df_merged[["town_original", "flat_type", "flat_model", "storey_range", "town"]] = df_merged[["town_original", "flat_type", "flat_model", "storey_range", "town"]].astype("category")
# df_merged["floor_area_sqm"] = df_merged["floor_area_sqm"].astype(float).astype("int16")
# df_merged[["latitude", "longitude"]] = df_merged[["latitude", "longitude"]].astype("float32")
# df_merged["resale_price"] = df_merged["resale_price"].astype(float).astype(int)

if "df" not in st.session_state:
    df["address"] = df["block"] + " " + df["street_name"]
    df_merged = df.merge(hdb_coordinates, how="left", on="address")
    df_merged["month"] = pd.to_datetime(df_merged["month"], format="%Y-%m", errors="raise")
    df_merged.rename(columns={'town': 'town_original'}, inplace=True)
    df_merged["point"] = df_merged.apply(lambda x: Point(x.longitude, x.latitude), axis=1)
    df_merged["town"] = df_merged["point"].apply(check_polygons)
    df_merged[["town_original", "flat_type", "flat_model", "storey_range", "town"]] = df_merged[["town_original", "flat_type", "flat_model", "storey_range", "town"]].astype("category")
    df_merged["floor_area_sqm"] = df_merged["floor_area_sqm"].astype(float).astype("int16")
    df_merged[["latitude", "longitude"]] = df_merged[["latitude", "longitude"]].astype("float32")
    df_merged["resale_price"] = df_merged["resale_price"].astype(float).astype(int)
    st.session_state.df = df_merged


with st.container():
    st.markdown(
        """
        - Combining `block` and `street_name` into a new `address` column, I then utilised a free [OneMap API](https://www.onemap.gov.sg/docs/) provided by the Singapore Land Authority to retrieve the coordinates of these addresses for plotting onto a map.
        - The `town` column does not correspond fully to the planning areas within the choropeth, so we'll check and rename towns within the dataset based the choropeth.
        """
    )
    st.markdown(
        """
        After performing some transformations on the data, notice the new columns that have been added.
        """
    )
    st.dataframe(st.session_state.df.head(3))

try:
    st.session_state.df.drop(columns=["point", "town_original", "_id", "block", "street_name"], inplace=True)
except:
    pass

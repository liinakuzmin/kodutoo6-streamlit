import requests
import pandas as pd
from io import StringIO
import json
import geopandas as gpd
import matplotlib.pyplot as plt

STATISTIKAAMETI_API_URL = "https://andmed.stat.ee/api/v1/et/stat/RV032"

JSON_PAYLOAD_STR =""" {
  "query": [
    {
      "code": "Aasta",
      "selection": {
        "filter": "item",
        "values": [
          "2014",
          "2015",
          "2016",
          "2017",
          "2018",
          "2019",
          "2020",
          "2021",
          "2022",
          "2023"
        ]
      }
    },
    {
      "code": "Maakond",
      "selection": {
        "filter": "item",
        "values": [
          "39",
          "44",
          "49",
          "51",
          "57",
          "59",
          "65",
          "67",
          "70",
          "74",
          "78",
          "82",
          "84",
          "86"
        ]
      }
    },
    {
      "code": "Sugu",
      "selection": {
        "filter": "item",
        "values": [
          "2",
          "3"
        ]
      }
    }
  ],
  "response": {
    "format": "csv"
  }
}
"""
def import_geojson():
    url = "https://raw.githubusercontent.com/nutiteq/geojson-examples/master/maakonnad.geojson"
    gdf = gpd.read_file(url)
    return gdf

    parsed_payload = json.loads(JSON_PAYLOAD_STR)
    
    response = requests.post(STATISTIKAAMETI_API_URL, json=parsed_payload, headers=headers)
    
    if response.status_code == 200:
        print("Request successful.")       
        text = response.content.decode('utf-8-sig')
        df = pd.read_csv(StringIO(text))

    else:
        print(f"Failed with status code: {response.status_code}")
        print(response.text)
    return df

def import_geojson():
    gdf = gpd.read_file(geojson)
    return gdf

def get_data_for_year(df, year):
    year_data = df[df.Aasta==year]
    return year_data

def plot(df):
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Replace 'value_column' with the column name you want to visualize
    df.plot(column='Loomulik iive', 
                     ax=ax,
                     legend=True,
                     cmap='viridis',  # Choose a colormap
                     legend_kwds={'label': "Loomulik iive"})
    
    plt.title('Loomulik iive maakonniti aastal 2023')
    plt.axis('off')  # Hide axis
    plt.tight_layout()
    plt.show()

import streamlit as st

st.title("Loomulik iive Eesti maakondades")

# Andmete laadimine
df = import_data()
gdf = import_geojson()

# Arvutame loomuliku iibe
df["Loomulik iive"] = df["Mehed Loomulik iive"] + df["Naised Loomulik iive"]

# Aastavalik kasutajale
aastad = sorted(df["Aasta"].unique())
valitud_aasta = st.selectbox("Vali aasta", aastad)

# Valime konkreetse aasta andmed
aasta_df = get_data_for_year(df, valitud_aasta)

# Teeme maakonnanimed ühtseks
gdf["Maakond"] = gdf["MNIMI"].str.replace(" maakond", "")
aasta_df["Maakond"] = aasta_df["Maakond"].str.replace(" maakond", "")

# Ühendame kaardi ja andmed
merged = gdf.merge(aasta_df, on="Maakond")

# Kuvame tabelina
st.dataframe(merged[["Maakond", "Loomulik iive"]])

# Joonistame kaardi
fig, ax = plt.subplots(figsize=(10, 6))
merged.plot(column="Loomulik iive", cmap="viridis", linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
ax.axis("off")
st.pyplot(fig)

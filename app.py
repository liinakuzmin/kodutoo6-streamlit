
import requests
import pandas as pd
from io import StringIO
import json
import geopandas as gpd
import matplotlib.pyplot as plt
import streamlit as st

STATISTIKAAMETI_API_URL = "https://andmed.stat.ee/api/v1/et/stat/RV032"

JSON_PAYLOAD_STR =""" {
  "query": [
    {
      "code": "Aasta",
      "selection": {
        "filter": "item",
        "values": [
          "2014", "2015", "2016", "2017", "2018",
          "2019", "2020", "2021", "2022", "2023"
        ]
      }
    },
    {
      "code": "Maakond",
      "selection": {
        "filter": "item",
        "values": [
          "39", "44", "49", "51", "57", "59", "65",
          "67", "70", "74", "78", "82", "84", "86"
        ]
      }
    },
    {
      "code": "Sugu",
      "selection": {
        "filter": "item",
        "values": [ "2", "3" ]
      }
    }
  ],
  "response": { "format": "csv" }
}
"""

def import_geojson():
    gdf = gpd.read_file("maakonnad.geojson")
    return gdf

def import_data():
    headers = {'Content-Type': 'application/json'}
    parsed_payload = json.loads(JSON_PAYLOAD_STR)
    
    response = requests.post(STATISTIKAAMETI_API_URL, json=parsed_payload, headers=headers)

    if response.status_code == 200:
        text = response.content.decode('utf-8-sig')
        df = pd.read_csv(StringIO(text))
        return df
    else:
        st.error(f"Statistikaameti päring ebaõnnestus. Kood: {response.status_code}")
        return pd.DataFrame()

def get_data_for_year(df, year):
    return df[df.Aasta == year]

# Streamlit rakenduse sisu
st.title("Loomulik iive Eesti maakondades")

df = import_data()
gdf = import_geojson()

# Arvutame loomuliku iibe
df["Loomulik iive"] = df["Mehed Loomulik iive"] + df["Naised Loomulik iive"]

# Aastavalik
aastad = sorted(df["Aasta"].unique())
valitud_aasta = st.selectbox("Vali aasta", aastad)

aasta_df = get_data_for_year(df, valitud_aasta)

# Ühtlustame maakonnanimed
gdf["Maakond"] = gdf["MNIMI"].str.replace(" maakond", "")
aasta_df["Maakond"] = aasta_df["Maakond"].str.replace(" maakond", "")

# Ühendame andmed
merged = gdf.merge(aasta_df, on="Maakond")

# Kuvame tabeli
st.subheader(f"Loomulik iive aastal {valitud_aasta}")
st.dataframe(merged[["Maakond", "Loomulik iive"]])

# Kaart
fig, ax = plt.subplots(figsize=(10, 6))
merged.plot(column="Loomulik iive", cmap="viridis", linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
ax.axis("off")
st.pyplot(fig)

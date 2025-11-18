import requests
import streamlit as st
import pandas as pd 

st.title("🌱 台灣氣象資料 Dashboard")

API_KEY = "你的授權碼"
LOCATION = st.selectbox("選擇城市", ["Taipei", "Taichung", "Kaohsiung"])

url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={API_KEY}&locationName={LOCATION}"
res = requests.get(url)
data = res.json()

location = data["records"]["location"][0]
st.subheader(f"📍 {location['locationName']} 36小時預報")

for element in location["weatherElement"]:
    name = element["elementName"]
    value = element["time"][0]["parameter"]["parameterName"]
    st.write(f"{name} : {value}")

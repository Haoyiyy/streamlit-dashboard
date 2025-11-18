import requests
import streamlit as st
import pandas as pd
import json

# --- 配置 ---
# 您的金鑰： CWA-FF1A0347-64B8-4CBE-8214-580F9D17514D
API_KEY = "CWA-FF1A0347-64B8-4CBE-8214-580F9D17514D"
DATA_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

# --- 函數：抓取並解析資料 ---
# 使用 Streamlit 快取資料 10 分鐘 (ttl=600 秒)，避免頻繁呼叫 API
@st.cache_data(ttl=600) 
def fetch_weather_data(location_name):
    """從中央氣象署 API 抓取 36 小時天氣預報資料，並包含錯誤處理"""
    
    # 1. 檢查 API Key 是否已填入 (修正檢查條件：檢查是否為原始佔位符 "YOUR_CWA_API_KEY")
    if API_KEY == "YOUR_CWA_API_KEY": # <--- 這是正確的檢查條件
        st.error("🚨 錯誤：請在程式碼中填入您的中央氣象署 API 授權碼！")
        st.info("請檢查 weather_dashboard_fix.py 檔案中 API_KEY 變數的值。")
        return None
        
    try:
        # 構造 API 請求 URL
        url = f"{DATA_URL}?Authorization={API_KEY}&locationName={location_name}"
        st.caption(f"Fetching data for: {location_name}...")
        
        # 2. 發送 API 請求
        res = requests.get(url, timeout=10)
        res.raise_for_status() # 如果狀態碼不是 200 (成功)，會拋出 HTTPError 異常
        
        data = res.json()
        
        # 3. 檢查 API 回應是否包含有效的地點資料 (處理 IndexError)
        if "records" not in data or "location" not in data["records"] or not data["records"]["location"]:
             st.warning(f"⚠️ API 回應中找不到 {location_name} 的資料。請檢查 API Key 或地點名稱是否正確。")
             return None

        # 成功取得資料，返回第一個地點的資訊
        location_data = data["records"]["location"][0]
        return location_data

    except requests.exceptions.HTTPError as e:
        # 處理 HTTP 錯誤，例如 401 Unauthorized (最常見的 API Key 錯誤)
        status_code = e.response.status_code
        st.error(f"🌐 API 請求發生 HTTP 錯誤 (Code: {status_code})。")
        if status_code == 401:
            st.error("🔑 授權碼無效或過期，請再次確認您的 API_KEY。")
        else:
            st.error(f"連線錯誤: {e}")
        return None
    except requests.exceptions.RequestException as e:
        # 處理其他網路錯誤，例如連線超時
        st.error(f"🌐 網路請求發生錯誤，請檢查您的網路連線: {e}")
        return None
    except Exception as e:
        # 捕捉其他所有未預期的錯誤
        st.error(f"❌ 發生未預期的錯誤: {e}")
        return None

# --- Streamlit UI ---
st.set_page_config(page_title="台灣氣象 Dashboard", layout="centered")
st.title("🌱 台灣氣象資料 Dashboard")
st.markdown("---")

# 讓使用者選擇城市 (使用 CWA API 接受的繁體中文名稱)
AVAILABLE_LOCATIONS = [
    "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市", 
    "基隆市", "新竹縣", "新竹市", "苗栗縣", "彰化縣", "南投縣", 
    "雲林縣", "嘉義縣", "嘉義市", "屏東縣", "宜蘭縣", "花蓮縣", 
    "臺東縣", "澎湖縣", "金門縣", "連江縣"
]
selected_location = st.selectbox("請選擇城市", AVAILABLE_LOCATIONS)

# 抓取資料
location = fetch_weather_data(selected_location)

if location:
    st.success("✅ 資料成功載入！")
    st.subheader(f"📍 {location['locationName']} 36小時天氣預報")
    
    weather_elements = []
    
    # 解析並顯示預報資訊
    for element in location["weatherElement"]:
        name = element["elementName"]
        
        # 抓取第一個時間點的預報值 (代表最新的 12 小時預報)
        if element["time"]:
            time_entry = element["time"][0]
            
            # 處理不同的資料結構：有些值在 'parameter'，有些值在 'value'
            parameter = time_entry.get("parameter")
            if parameter and parameter.get("parameterName"):
                value = parameter["parameterName"]
            elif time_entry.get("value"):
                 value = time_entry["value"]
            else:
                 value = "N/A"
                 
            weather_elements.append({"天氣項目": name, "預報值": value})
            
    # 使用 DataFrame 美觀地顯示結果
    df = pd.DataFrame(weather_elements)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 顯示數據時間範圍
    if location["weatherElement"] and location["weatherElement"][0]["time"]:
        start_time = location["weatherElement"][0]["time"][0]["startTime"]
        end_time = location["weatherElement"][0]["time"][0]["endTime"]
        st.caption(f"數據時間範圍：從 {start_time} 到 {end_time}")
        
    st.markdown("---")
    st.info("💡 數據來源：中央氣象署開放資料平台")
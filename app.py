import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date, timedelta

st.set_page_config(page_title="Злочинність у регіонах", layout="wide")

# --- 1. ГЕНЕРАЦІЯ ХАОТИЧНИХ ДАНИХ ДЛЯ НОВИХ ОБЛАСТЕЙ ---
@st.cache_data
def load_new_regional_data_final():
    np.random.seed(42)
    
    # Сітка опорних точок для Полтави, Житомира, Києва та Вінниці
    cities_data = {
        "Київська область": [
            (50.45, 30.52), (49.79, 30.11), (50.51, 30.76), (50.35, 30.95), 
            (50.08, 29.91), (50.11, 30.62), (50.58, 30.49), (50.46, 29.81), 
            (50.28, 31.77), (49.56, 30.33), (50.93, 29.90), (49.86, 30.82)
        ],
        "Полтавська область": [
            (49.58, 34.55), (49.06, 33.40), (50.01, 33.00), (49.96, 33.60),
            (50.37, 34.00), (50.23, 32.50), (49.45, 35.12), (49.78, 33.26),
            (50.20, 34.36), (49.38, 33.20), (49.14, 34.20), (50.35, 33.26)
        ],
        "Житомирська область": [
            (50.25, 28.65), (49.89, 28.59), (50.95, 28.63), (50.58, 27.63),
            (50.76, 29.27), (50.31, 29.06), (51.32, 28.80), (50.49, 29.23),
            (51.22, 27.65), (50.30, 27.67), (50.04, 28.11), (50.02, 29.02)
        ],
        "Вінницька область": [
            (49.23, 28.46), (49.03, 28.10), 
            (48.46, 27.79), # Могилів-Подільський (виправлено координати)
            (48.44, 28.27), # Ямпіль (виправлено координати)
            (48.80, 29.38), (49.71, 28.82), 
            (48.68, 29.24), (49.44, 28.52),
            (49.07, 27.68), (48.67, 28.84), 
            (48.37, 29.53), (48.97, 28.84)
        ]
    }
    
    categories = ["Крадіжка", "Шахрайство", "Розбій", "Кіберзлочин", "Хуліганство"]
    start_date = date.today() - timedelta(days=180)
    
    data = []
    # Генеруємо 2000 записів для щільного покриття
    for _ in range(2000):
        region_name = np.random.choice(list(cities_data.keys()))
        
        while True:
            # Обираємо випадкове місто
            city_coords = cities_data[region_name][np.random.randint(0, len(cities_data[region_name]))]
            
            # Робимо хаотичний розкид (~15 км в усі боки)
            lat_jitter = np.random.uniform(-0.15, 0.15)
            lon_jitter = np.random.uniform(-0.15, 0.15)
            
            lat = city_coords[0] + lat_jitter
            lon = city_coords[1] + lon_jitter
            
            # --- СИСТЕМА СТРАХОВКИ (МЕЖІ ТА ВОДОЙМИ) ---
            
            # ОНОВЛЕНО: Жорсткий захист для Вінниці: Дністер є кордоном на південний захід
            if region_name == "Вінницька область":
                # Захист південного кордону
                if lat < 48.35:
                    continue 
                # ОНОВЛЕНО: Захист західного/південно-західного кордону вздовж Дністра
                # (наприклад, біля Могилів-Подільського). Якщо довгота менша 27.85
                if lon < 27.85 and lat < 48.5:
                    continue
                
            # Житомир та Київ: захист від перельоту кордону на півночі
            if region_name == "Житомирська область" and lat > 51.45:
                continue
            if region_name == "Київська область" and lat > 51.25:
                continue
                
            # Полтава: захист від падіння в Дніпро/Кременчуцьке водосховище на південному заході
            if region_name == "Полтавська область" and lat < 49.1 and lon < 33.5:
                continue

            # Якщо всі перевірки пройдено — точка залишається
            break 
        
        data.append({
            "Дата": start_date + timedelta(days=np.random.randint(0, 180)),
            "Регіон": region_name,
            "Категорія злочину": np.random.choice(categories),
            "lat": lat,
            "lon": lon
        })
        
    return pd.DataFrame(data)

df = load_new_regional_data_final()

# --- 2. БІЧНА ПАНЕЛЬ (ФІЛЬТРИ) ---
st.sidebar.header("Фільтри даних")

min_date = df["Дата"].min()
max_date = df["Дата"].max()
selected_dates = st.sidebar.date_input("Оберіть період", [min_date, max_date], min_value=min_date, max_value=max_date)

selected_regions = st.sidebar.multiselect("Оберіть регіон(и)", options=df["Регіон"].unique(), default=df["Регіон"].unique())
selected_categories = st.sidebar.multiselect("Оберіть категорію(ї)", options=df["Категорія злочину"].unique(), default=df["Категорія злочину"].unique())

if len(selected_dates) == 2:
    start, end = selected_dates
    mask = (df["Дата"] >= start) & (df["Дата"] <= end) & (df["Регіон"].isin(selected_regions)) & (df["Категорія злочину"].isin(selected_categories))
    filtered_df = df.loc[mask]
else:
    filtered_df = df.loc[(df["Регіон"].isin(selected_regions)) & (df["Категорія злочину"].isin(selected_categories))]

# --- 3. ГОЛОВНИЙ ЕКРАН ---
st.title("Аналітика: Злочинність у регіонах")
st.markdown("Інформаційна панель для аналізу даних. Точки не виходять за кордони Молдови.")

st.write(f"**Всього знайдено записів:** {len(filtered_df)}")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ Карта правопорушень")
    if not filtered_df.empty:
        st.map(filtered_df, zoom=5, use_container_width=True)
    else:
        st.info("Немає даних для відображення.")

with col2:
    st.subheader("Індекс криміногенності")
    crime_weights = {"Розбій": 5, "Кіберзлочин": 4, "Шахрайство": 3, "Крадіжка": 2, "Хуліганство": 1}
    
    if not filtered_df.empty:
        temp_df = filtered_df.copy()
        temp_df["Вага"] = temp_df["Категорія злочину"].map(crime_weights)
        index_df = temp_df.groupby("Регіон")["Вага"].sum().reset_index()
        index_df = index_df.sort_values(by="Вага", ascending=False)
        index_df.rename(columns={"Вага": "Індекс"}, inplace=True)
        
        fig_index = px.bar(index_df, x="Індекс", y="Регіон", orientation='h', color="Індекс", color_continuous_scale="Reds")
        st.plotly_chart(fig_index, use_container_width=True)
    else:
        st.info("Недостатньо даних.")

# --- 4. ДИНАМІКА ЗЛОЧИНІВ ---
st.subheader("Динаміка злочинів")
if not filtered_df.empty:
    dynamics_df = filtered_df.groupby("Дата").size().reset_index(name="Кількість")
    fig_dynamics = px.line(dynamics_df, x="Дата", y="Кількість", markers=True)
    st.plotly_chart(fig_dynamics, use_container_width=True)
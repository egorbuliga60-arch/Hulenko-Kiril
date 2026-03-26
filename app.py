import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Cyber Threat Monitoring", layout="wide")

st.title("Система моніторингу кіберзагроз")

# ---------- Генерація тестових даних ----------
def generate_data(n=500):
    np.random.seed(42)
    base_date = datetime.now()
    data = []
    countries = ['USA', 'China', 'Germany', 'Ukraine', 'India']

    for _ in range(n):
        ip = f"{np.random.randint(1,255)}.{np.random.randint(1,255)}.{np.random.randint(1,255)}.{np.random.randint(1,255)}"
        country = np.random.choice(countries)
        date = base_date - timedelta(days=np.random.randint(0, 10))

        data.append({
            'ip': ip,
            'country': country,
            'timestamp': date
        })

    return pd.DataFrame(data)

# Завантаження або генерація даних
# st.sidebar.header("Налаштування")
# use_sample = st.sidebar.checkbox("Використати тестові дані", True)

# if use_sample:
#     df = generate_data()
# else:
#     uploaded_file = st.sidebar.file_uploader("Завантаж CSV", type=["csv"])
#     if uploaded_file:
#         df = pd.read_csv(uploaded_file)
#     else:
#         st.warning("Завантаж файл або обери тестові дані")
#         st.stop()

st.subheader("Дані про IP-адреси атак")
st.dataframe(df)

# ---------- 1. Дані про IP ----------
st.markdown("Аналіз IP-адрес")
ip_counts = df['ip'].value_counts().reset_index()
ip_counts.columns = ['IP', 'Count']
st.dataframe(ip_counts.head(10))

# ---------- 2. Карта атак ----------
st.markdown("Геолокація атак")
country_counts = df['country'].value_counts().reset_index()
country_counts.columns = ['country', 'attacks']

fig_map = px.choropleth(country_counts,
                        locations='country',
                        locationmode='country names',
                        color='attacks',
                        title='Карта атак')
st.plotly_chart(fig_map, use_container_width=True)

# ---------- 3. Країна з найбільшою активністю ----------
st.markdown("Найбільш активна країна")
most_active = country_counts.iloc[0]
st.success(f"Найбільше атак з країни: {most_active['country']} ({most_active['attacks']} атак)")

# ---------- 4. Трендовий аналіз ----------
st.markdown("Тренд атак по днях")
df['date'] = pd.to_datetime(df['timestamp']).dt.date
trend = df.groupby('date').size().reset_index(name='attacks')

fig_trend = px.line(trend, x='date', y='attacks', markers=True, title='Атаки по днях')
st.plotly_chart(fig_trend, use_container_width=True)


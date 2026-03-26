import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finance + Media + Reputation", layout="wide")

st.title("📊 Комплексний дашборд: Фінанси + Медіа + Репутація")

# ---------- Завантаження CSV ----------
st.subheader("📂 Завантаження даних")

col1, col2, col3 = st.columns(3)

with col1:
    finance_file = st.file_uploader("Фінансові дані (CSV)", type="csv")

with col2:
    media_file = st.file_uploader("Медіа дані (CSV)", type="csv")

with col3:
    reputation_file = st.file_uploader("Репутаційні дані (CSV)", type="csv")

if not (finance_file and media_file and reputation_file):
    st.warning("Завантаж всі три файли для продовження")
    st.stop()

# ---------- Зчитування ----------
finance_df = pd.read_csv(finance_file)
media_df = pd.read_csv(media_file)
reputation_df = pd.read_csv(reputation_file)

# ---------- Попередній перегляд ----------
st.subheader("🔍 Попередній перегляд даних")

st.write("Фінанси")
st.dataframe(finance_df.head())

st.write("Медіа")
st.dataframe(media_df.head())

st.write("Репутація")
st.dataframe(reputation_df.head())

# ---------- ФІНАНСИ ----------
st.subheader("💰 Аналіз фінансів")

if 'date' in finance_df.columns and 'revenue' in finance_df.columns:
    finance_df['date'] = pd.to_datetime(finance_df['date'])
    fig_fin = px.line(finance_df, x='date', y='revenue', title='Дохід з часом')
    st.plotly_chart(fig_fin, use_container_width=True)

# ---------- МЕДІА ----------
st.subheader("📰 Аналіз медіа")

if 'source' in media_df.columns:
    media_counts = media_df['source'].value_counts().reset_index()
    media_counts.columns = ['source', 'mentions']

    fig_media = px.bar(media_counts, x='source', y='mentions', title='Кількість згадок')
    st.plotly_chart(fig_media, use_container_width=True)

# ---------- РЕПУТАЦІЯ ----------
st.subheader("⭐ Аналіз репутації")

if 'sentiment' in reputation_df.columns:
    sentiment_counts = reputation_df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['sentiment', 'count']

    fig_rep = px.pie(sentiment_counts, names='sentiment', values='count', title='Тональність')
    st.plotly_chart(fig_rep, use_container_width=True)

# ---------- ОБ’ЄДНАНИЙ АНАЛІЗ ----------
st.subheader("📈 Загальний інсайт")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Загальний дохід", int(finance_df['revenue'].sum()) if 'revenue' in finance_df.columns else 0)

with col2:
    st.metric("К-сть згадок", len(media_df))

with col3:
    positive = (reputation_df['sentiment'] == 'positive').sum() if 'sentiment' in reputation_df.columns else 0
    st.metric("Позитивні відгуки", int(positive))

st.info("Дашборд об'єднує фінанси, медіа та репутацію в одному місці 🚀")

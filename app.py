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

# ---------- ОБ’ЄДНАННЯ ДАНИХ ----------
# Припускаємо, що є спільна колонка 'company'
merged_df = finance_df.merge(media_df, on='company').merge(reputation_df, on='company')

st.subheader("🔗 Об'єднаний DataFrame")
st.dataframe(merged_df.head())

# ---------- РОЗРАХУНОК РЕЙТИНГУ ----------
# Нормалізація (0-1)
def normalize(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-9)

if 'revenue' in merged_df.columns:
    merged_df['finance_score'] = normalize(merged_df['revenue'])
else:
    merged_df['finance_score'] = 0

if 'mentions' in merged_df.columns:
    merged_df['media_score'] = normalize(merged_df['mentions'])
else:
    merged_df['media_score'] = 0

if 'sentiment_score' in merged_df.columns:
    merged_df['reputation_score'] = normalize(merged_df['sentiment_score'])
else:
    merged_df['reputation_score'] = 0

# Інтегральний рейтинг
merged_df['total_score'] = (
    0.4 * merged_df['finance_score'] +
    0.3 * merged_df['media_score'] +
    0.3 * merged_df['reputation_score']
)

# ---------- ВКЛАДКИ ----------
tab1, tab2, tab3 = st.tabs(["💰 Фінанси", "📰 Медіа", "⭐ Публічний імідж"])

# ---------- ФІНАНСИ ----------
with tab1:
    st.subheader("Аналіз фінансів")

    if 'date' in finance_df.columns and 'revenue' in finance_df.columns:
        finance_df['date'] = pd.to_datetime(finance_df['date'])
        fig_fin = px.line(finance_df, x='date', y='revenue', color='company', title='Дохід по компаніях')
        st.plotly_chart(fig_fin, use_container_width=True)

# ---------- МЕДІА ----------
with tab2:
    st.subheader("Аналіз медіа")

    if 'mentions' in media_df.columns:
        fig_media = px.bar(media_df, x='company', y='mentions', title='Згадки по компаніях')
        st.plotly_chart(fig_media, use_container_width=True)

# ---------- РЕПУТАЦІЯ ----------
with tab3:
    st.subheader("Аналіз репутації")

    if 'sentiment_score' in reputation_df.columns:
        fig_rep = px.bar(reputation_df, x='company', y='sentiment_score', title='Репутація компаній')
        st.plotly_chart(fig_rep, use_container_width=True)

# ---------- РЕЙТИНГ ----------
st.subheader("🏆 Інтегральний рейтинг компаній")

rating_df = merged_df[['company', 'total_score']].sort_values(by='total_score', ascending=False)

st.dataframe(rating_df)

fig_rating = px.bar(rating_df, x='company', y='total_score', title='Загальний рейтинг')
st.plotly_chart(fig_rating, use_container_width=True)

st.success("Дашборд повністю об'єднує фінанси, медіа та репутацію з інтегральною оцінкою 🚀")

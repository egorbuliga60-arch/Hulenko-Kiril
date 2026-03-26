import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finance + Media + Reputation", layout="wide")

st.title("Комплексний дашборд: Фінанси + Медіа + Репутація")

# ---------- GITHUB CONFIG ----------
st.subheader("Дані з GitHub")

repo_url = st.text_input("Встав посилання на GitHub репозиторій", "------Посилання------")

finance_url = repo_url + "finance.csv"
media_url = repo_url + "media.csv"
reputation_url = repo_url + "reputation.csv"

try:
    finance_df = pd.read_csv(finance_url)
    media_df = pd.read_csv(media_url)
    reputation_df = pd.read_csv(reputation_url)
except Exception as e:
    st.error("❌ Не вдалося завантажити файли. Перевір посилання на GitHub")
    st.stop()

st.success("✅ Дані успішно завантажені з GitHub")

# ---------- ОБ’ЄДНАННЯ ДАНИХ ----------
merged_df = finance_df.merge(media_df, on='company').merge(reputation_df, on='company')

st.subheader("🔗 Об'єднаний DataFrame")
st.dataframe(merged_df.head())

# ---------- НОРМАЛІЗАЦІЯ ----------
def normalize(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-9)

merged_df['finance_score'] = normalize(merged_df['revenue']) if 'revenue' in merged_df.columns else 0
merged_df['media_score'] = normalize(merged_df['mentions']) if 'mentions' in merged_df.columns else 0
merged_df['reputation_score'] = normalize(merged_df['sentiment_score']) if 'sentiment_score' in merged_df.columns else 0

# ---------- ІНТЕГРАЛЬНИЙ РЕЙТИНГ ----------
merged_df['total_score'] = (
    0.4 * merged_df['finance_score'] +
    0.3 * merged_df['media_score'] +
    0.3 * merged_df['reputation_score']
)

# ---------- ВКЛАДКИ ----------
tab1, tab2, tab3 = st.tabs(["Фінанси", "Медіа", "Публічний імідж"])

with tab1:
    st.subheader("Аналіз фінансів")
    if 'date' in finance_df.columns:
        finance_df['date'] = pd.to_datetime(finance_df['date'])
        fig_fin = px.line(finance_df, x='date', y='revenue', color='company', title='Дохід по компаніях')
        st.plotly_chart(fig_fin, use_container_width=True)

with tab2:
    st.subheader("Аналіз медіа")
    if 'mentions' in media_df.columns:
        fig_media = px.bar(media_df, x='company', y='mentions', title='Згадки по компаніях')
        st.plotly_chart(fig_media, use_container_width=True)

with tab3:
    st.subheader("Аналіз репутації")
    if 'sentiment_score' in reputation_df.columns:
        fig_rep = px.bar(reputation_df, x='company', y='sentiment_score', title='Репутація компаній')
        st.plotly_chart(fig_rep, use_container_width=True)

# ---------- РЕЙТИНГ ----------
st.subheader("Інтегральний рейтинг компаній")

rating_df = merged_df[['company', 'total_score']].sort_values(by='total_score', ascending=False)
st.dataframe(rating_df)

fig_rating = px.bar(rating_df, x='company', y='total_score', title='Загальний рейтинг')
st.plotly_chart(fig_rating, use_container_width=True)


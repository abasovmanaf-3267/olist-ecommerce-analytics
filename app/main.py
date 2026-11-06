from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

st.title("Sifarişin gec çatdırılma riski")
st.write("Sifariş məlumatlarını doldur, model gec çatma ehtimalını hesablasın.")


@st.cache_resource
def load_model():
    return joblib.load(Path(__file__).parent.parent / "models" / "late_delivery_rf.pkl")


model = load_model()

days = ["Bazar ertəsi", "Çərşənbə axşamı", "Çərşənbə", "Cümə axşamı",
        "Cümə", "Şənbə", "Bazar"]

col1, col2, col3 = st.columns(3)

with col1:
    month = st.number_input("Sifariş ayı (1-12)", min_value=1, max_value=12, value=6)
    day_name = st.selectbox("Həftənin günü", days)
    estimated_days = st.number_input("Vəd olunan müddət (gün)", min_value=1, max_value=160, value=23)

with col2:
    item_count = st.number_input("Məhsul sayı", min_value=1, max_value=21, value=1)
    total_price = st.number_input("Ümumi qiymət", min_value=0.0, value=87.0)
    total_freight = st.number_input("Daşınma haqqı", min_value=0.0, value=17.0)

with col3:
    total_weight = st.number_input("Ümumi çəki (qram)", min_value=0.0, value=750.0)
    total_volume = st.number_input("Ümumi həcm (sm³)", min_value=0.0, value=7260.0)
    state_name = st.selectbox("Müştəri və satıcı", ["Eyni ştatda", "Fərqli ştatda"])

if st.button("Proqnoz et"):
    features = ["purchase_month", "purchase_weekday", "estimated_days",
                "item_count", "total_price", "total_freight",
                "total_weight", "total_volume", "same_state"]

    row = [month, days.index(day_name), estimated_days, item_count,
           total_price, total_freight, total_weight, total_volume,
           1 if state_name == "Eyni ştatda" else 0]

    x = pd.DataFrame([row], columns=features)

    probability = model.predict_proba(x)[0, 1]
    st.metric("Gec çatma ehtimalı", f"{probability:.0%}")

    if model.predict(x)[0] == 1:
        st.error("Bu sifariş gec çata bilər.")
    else:
        st.success("Bu sifariş yəqin ki, vaxtında çatacaq.")
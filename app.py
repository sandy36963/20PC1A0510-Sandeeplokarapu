import streamlit as st
import numpy as np
import pickle
import os

st.set_page_config(page_title="Titanic Survival Prediction", page_icon="🚢")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "titanic_model.pkl")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

st.title("🚢 Titanic Survival Prediction App")

Pclass = st.selectbox("Passenger Class", [1, 2, 3])
Sex = st.selectbox("Sex", ["male", "female"])
Age = st.slider("Age", 1, 100, 29)
SibSp = st.number_input("Number of Siblings/Spouses", 0, 10)
Parch = st.number_input("Number of Parents/Children", 0, 10)
Fare = st.number_input("Fare", 0.0, 600.0)
Embarked = st.selectbox("Embarked", ["S", "C", "Q"])

sex_val = 1 if Sex == "male" else 0
emb_val = {"S":0, "C":1, "Q":2}[Embarked]

features = np.array([[Pclass, sex_val, Age, SibSp, Parch, Fare, emb_val]])

if st.button("Predict"):
    pred = model.predict(features)[0]
    if pred == 1:
        st.success("✅ Passenger will SURVIVE")
    else:
        st.error("❌ Passenger will NOT survive")

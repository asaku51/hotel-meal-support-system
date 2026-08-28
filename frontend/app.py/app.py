import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="食事補助ポイントアプリ", layout="centered")

# -----------------------------
# デザイン（CSS）
# -----------------------------
st.markdown("""
<style>
body {
    background-color: #ffffff;
    font-family: "Rounded Mplus 1c";
}
div.stButton > button {
    background-color: #444444;
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 18px;
    border: none;
}
input {
    border-radius: 10px !important;
}
.balance-box {
    background-color: #000000;
    padding: 25px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 20px;
}
.balance-text {
    font-size: 32px;
    font-weight: bold;
    color: #ffffff;
}
.input-highlight {
    background-color:#ffffff;
    padding:30px;
    border-radius:15px;
    text-align:center;
    border: 2px solid #000000;
    margin-bottom:20px;
}
.input-highlight-text {
    font-size:40px;
    font-weight:bold;
    color:#000000;
}
.confirm-box {
    background-color:#ffffff;
    padding:40px;
    border-radius:20px;
    text-align:center;
    margin-bottom:25px;
    border: 3px solid #000000;
}
.confirm-text {
    font-size:50px;
    font-weight:bold;
    color:#000000;
}
.history-box {
    background-color: #e6e6e6;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
    color: #000000;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# タイトル
# -----------------------------
st.title("従業員向け 食事補助ポイントアプリ")
st.write("従業員の食事補助ポイントを管理するアプリです。")

# -----------------------------
# 従業員ID入力
# -----------------------------
user_id = st.text_input("従業員IDを入力してください（例：EMP001）")

# 画面遷移用の状態
if "confirm_mode" not in st.session_state:
    st.session_state.confirm_mode = False
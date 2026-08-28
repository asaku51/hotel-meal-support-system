import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="管理ページ", layout="centered")

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

.table-box {
    background-color:#ffffff;
    padding:15px;
    border-radius:10px;
    border:1px solid #000000;
}

.table-row {
    padding: 8px;
    border-bottom: 1px solid #cccccc;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# タイトル
# -----------------------------
st.title("会社用 管理ページ")
st.write("従業員のポイント管理・履歴確認・付与・登録を行うページです。")

# -----------------------------
# メニュー選択
# -----------------------------
menu = st.selectbox(
    "操作を選択してください",
    ["従業員一覧", "ポイント付与", "利用履歴一覧", "従業員追加"]
)

# -----------------------------
# ① 従業員一覧（氏名・当月利用・当月チャージ・残ポイント）
# -----------------------------
if menu == "従業員一覧":
    st.subheader("従業員一覧（氏名・当月利用・当月チャージ・残ポイント）")

    # 従業員基本情報
    try:
        employees = requests.get(f"{API_BASE}/api/all-users").json()
    except:
        st.error("FastAPI が起動していません")
        st.stop()

    # 当月利用・チャージ情報
    try:
        monthly = requests.get(f"{API_BASE}/api/monthly-summary").json()
    except:
        st.error("FastAPI が起動していません（monthly-summary が必要）")
        st.stop()

    st.markdown("<div class='table-box'>", unsafe_allow_html=True)
    st.write("従業員ID ｜ 氏名 ｜ 当月利用 ｜ 当月チャージ ｜ 残ポイント")

    for emp in employees:

        if isinstance(emp, dict):
            user_id = emp.get("user_id", "不明")
            name = emp.get("name", "不明")
            balance = emp.get("balance", 0)

            # 当月利用・チャージを取得
            monthly_data = monthly.get(user_id, {})
            used = monthly_data.get("used", 0)
            charged = monthly_data.get("charged", 0)

            st.markdown(
                f"""
                <div class="table-row">
                {user_id} ｜ {name} ｜ {used} ｜ {charged} ｜ {balance}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            st.write(f"不明なデータ形式：{emp}")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# ② ポイント付与
# -----------------------------
elif menu == "ポイント付与":
    st.subheader("ポイント付与")

    user_id = st.text_input("従業員ID")
    amount = st.text_input("付与ポイント")

    if user_id and amount.isdigit():
        if st.button("付与する"):
            payload = {
                "user_id": user_id,
                "amount": int(amount),
                "description": "会社付与"
            }
            res = requests.post(f"{API_BASE}/api/add", json=payload)

            if res.status_code == 200:
                st.success(f"{amount} ポイントを付与しました")
            else:
                st.error(res.json().get("detail", "エラーが発生しました"))

# -----------------------------
# ③ 利用履歴一覧
# -----------------------------
elif menu == "利用履歴一覧":
    st.subheader("利用履歴一覧")

    try:
        logs = requests.get(f"{API_BASE}/api/all-use-log").json()
    except:
        st.error("FastAPI が起動していません")
        st.stop()

    if logs:
        for log in logs:
            if isinstance(log, dict):
                timestamp = log.get("timestamp", "不明")
                user_id = log.get("user_id", "不明")
                name = log.get("name", "不明")
                amount = log.get("amount", "不明")

                st.markdown(
                    f"""
                    <div class="history-box">
                        <b>{timestamp}</b><br>
                        従業員ID：{user_id}<br>
                        名前：{name}<br>
                        {amount} ポイント
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.write(f"不明なデータ形式：{log}")
    else:
        st.info("利用履歴がありません")

# -----------------------------
# ④ 従業員追加
# -----------------------------
elif menu == "従業員追加":
    st.subheader("従業員追加")

    new_id = st.text_input("従業員ID（例：EMP010）")
    new_name = st.text_input("従業員名（例：山田太郎）")
    init_point = st.text_input("初期ポイント（例：15000）")

    if new_id and new_name and init_point.isdigit():
        if st.button("登録する"):
            payload = {
                "user_id": new_id,
                "name": new_name,
                "balance": int(init_point)
            }
            res = requests.post(f"{API_BASE}/api/register", json=payload)

            if res.status_code == 200:
                st.success(f"従業員 {new_name}（{new_id}）を登録しました（初期ポイント：{init_point}）")
            else:
                st.error(res.json().get("detail", "エラーが発生しました"))

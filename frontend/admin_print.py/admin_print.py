import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="印刷画面", layout="centered")

st.title("従業員一覧・月次集計 印刷画面")

# -----------------------------
# データ取得
# -----------------------------
users = requests.get(f"{API_BASE}/api/print-users").json()
summary = requests.get(f"{API_BASE}/api/monthly-summary").json()

df = pd.DataFrame(users["rows"], columns=users["header"])

st.subheader("従業員一覧（印刷用）")
st.table(df)

st.subheader("月次集計")
st.write(f"対象月：{summary['month']}")
st.write(f"当月利用合計：{summary['total_used']} ポイント")
st.write(f"当月チャージ合計：{summary['total_charged']} ポイント")

# -----------------------------
# PDF生成
# -----------------------------
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="従業員一覧（印刷用）", ln=True)

    # 表ヘッダー
    header = users["header"]
    for h in header:
        pdf.cell(40, 10, txt=h, border=1)
    pdf.ln()

    # 表データ
    for row in users["rows"]:
        for col in row:
            pdf.cell(40, 10, txt=str(col), border=1)
        pdf.ln()

    pdf.ln(10)
    pdf.cell(200, 10, txt="月次集計", ln=True)
    pdf.cell(200, 10, txt=f"対象月：{summary['month']}", ln=True)
    pdf.cell(200, 10, txt=f"当月利用合計：{summary['total_used']} ポイント", ln=True)
    pdf.cell(200, 10, txt=f"当月チャージ合計：{summary['total_charged']} ポイント", ln=True)

    return pdf.output(dest="S").encode("latin-1")

pdf_data = create_pdf()

st.download_button(
    label="PDFをダウンロード",
    data=pdf_data,
    file_name="従業員一覧_月次集計.pdf",
    mime="application/pdf"
)

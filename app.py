import streamlit as st
import pandas as pd
import gspread
import uuid
import json
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Tra cứu đảng phí", layout="centered")
st.title("TRA CỨU ĐẢNG PHÍ")

# ===============================
# CONNECT GOOGLE SHEET (FIXED)
# ===============================
scope = ["https://www.googleapis.com/auth/spreadsheets"]

from google.oauth2.service_account import Credentials

scope = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_info(
    st.secrets["SERVICE_ACCOUNT"],
    scopes=scope
)

gc = gspread.authorize(creds)
sheet = gc.open_by_key(st.secrets["GOOGLE_SHEET_ID"])
ws = sheet.worksheet("Sheet1")


records = ws.get_all_records()
headers = ws.row_values(1)

# =============================
# AUTO CREATE record_id (ONE TIME)
# =============================
if "record_id" not in headers:
    ws.update_cell(1, len(headers) + 1, "record_id")
    headers.append("record_id")

record_id_col = headers.index("record_id") + 1

for i, row in enumerate(records, start=2):
    if row.get("record_id", "") == "":
        rid = uuid.uuid4().hex[:8].upper()
        ws.update_cell(i, record_id_col, rid)

# Reload data after update
records = ws.get_all_records()
df = pd.DataFrame(records)

# =============================
# GET record_id FROM QR
# =============================
params = st.experimental_get_query_params()
record_id = params.get("id", [None])[0]

if not record_id:
    st.warning("Vui lòng quét QR code")
    st.stop()

row = df[df["record_id"] == record_id]
if row.empty:
    st.error("Không tìm thấy dữ liệu")
    st.stop()

row = row.iloc[0]

# =============================
# PASSWORD CHECK
# =============================
pwd = st.text_input(
    "Nhập mật khẩu (DDMMYY + 4 số cuối CCCD)",
    type="password"
)

if pwd:
    dob = datetime.strptime(row["NTNS"], "%d/%m/%Y")
    correct_pwd = dob.strftime("%d%m%y") + str(row["Số CCCD"])[-4:]

    if pwd != correct_pwd:
        st.error("Sai mật khẩu")
        st.stop()

    # =============================
    # SHOW DATA (HEADER + 1 ROW)
    # =============================
    st.success("✅ Xác thực thành công")
    st.subheader("ĐẢNG PHÍ THÁNG 02 – 2026")

    data = {
        "Họ và tên": row["Họ và tên"],
        "Ngày sinh": row["NTNS"],
        "Lương chính": f"{row['Lương chính']:,}",
        "Vượt khung": f"{row['Vượt khung']:,}",
        "Phụ cấp chức vụ": f"{row['Phụ cấp chức vụ']:,}",
        "Thâm niên nhà giáo": f"{row['Thâm niên nhà giáo']:,}",
        "Cộng": f"{row['Cộng']:,}",
        "1% thu nhập/tháng": f"{row['1% thu nhập/tháng']:,}",
    }

    st.table(pd.DataFrame(data.items(), columns=["Nội dung", "Giá trị"]))

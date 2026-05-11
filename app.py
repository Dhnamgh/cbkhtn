import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Tra cứu thông tin", layout="centered")
st.title("TRA CỨU THÔNG TIN CÁ NHÂN")

# ===============================
# CONNECT GOOGLE SHEET
# ===============================
scope = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_info(
    st.secrets["SERVICE_ACCOUNT"],
    scopes=scope
)

gc = gspread.authorize(creds)
sheet = gc.open_by_key(st.secrets["GOOGLE_SHEET_ID"])

# ✅ ĐÚNG TÊN TAB THỰC TẾ
ws = sheet.worksheet("Sheet1")
df = pd.DataFrame(ws.get_all_records())

# ===============================
# NHẬP MẬT KHẨU
# ===============================
st.subheader("Nhập mật khẩu")
password = st.text_input(
    "Mật khẩu là 6 số cuối của CCCD",
    type="password"
)

if not password:
    st.stop()

password = password.strip()

# ===============================
# KIỂM TRA MẬT KHẨU
# ===============================
if not password.isdigit() or len(password) != 6:
    st.error("Mật khẩu phải gồm đúng 6 chữ số")
    st.stop()

def match_row(row):
    return str(row["Số CCCD"]).endswith(password)

matched = df[df.apply(match_row, axis=1)]

if matched.empty:
    st.error("Không tìm thấy thông tin phù hợp")
    st.stop()

# Nếu trùng (hiếm), lấy dòng đầu
row = matched.iloc[0]

# ===============================
# HIỂN THỊ THÔNG TIN
# ===============================
st.success("✅ Xác thực thành công")

result = {
    "Họ và tên": row["Họ và tên"],
    "Số CCCD": row["Số CCCD"],
    "Lương chính": f"{row['Lương chính']:,}",
    "Vượt khung": f"{row['Vượt khung']:,}",
    "Phụ cấp chức vụ": f"{row['Phụ cấp chức vụ']:,}",
    "Thâm niên nhà giáo": f"{row['Thâm niên nhà giáo']:,}",
    "Cộng": f"{row['Cộng']:,}",
    "1% thu nhập/tháng": f"{row['1% thu nhập/tháng']:,}",
}

st.table(pd.DataFrame(result.items(), columns=["Nội dung", "Giá trị"]))

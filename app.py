import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import qrcode
import io

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
ws = sheet.worksheet("Sheet1")
df = pd.DataFrame(ws.get_all_records())

# ===============================
# HIỂN THỊ QR CHUNG
# ===============================
st.subheader("Bước 1: Quét mã QR để truy cập")

app_url = st.secrets.get("APP_URL", "https://ten-app.streamlit.app/")

qr = qrcode.make(app_url)
buf = io.BytesIO()
qr.save(buf)
st.image(buf.getvalue(), caption="Quét QR bằng Zalo")

st.divider()

# ===============================
# NHẬP MẬT KHẨU
# ===============================
st.subheader("Bước 2: Nhập mật khẩu")

password = st.text_input(
    "Mật khẩu = DDMMYY + 4 số cuối CCCD",
    type="password"
)

if not password:
    st.stop()

# ===============================
# XÁC THỰC & TRA CỨU
# ===============================
if len(password) < 10:
    st.error("Mật khẩu không hợp lệ")
    st.stop()

ddmmyy = password[:6]
last4 = password[-4:]

def match_row(row):
    try:
        dob = datetime.strptime(row["NTNS"], "%d/%m/%Y")
        return (
            dob.strftime("%d%m%y") == ddmmyy
            and str(row["Số CCCD"]).endswith(last4)
        )
    except:
        return False

matched = df[df.apply(match_row, axis=1)]

if matched.empty:
    st.error("Không tìm thấy thông tin phù hợp")
    st.stop()

row = matched.iloc[0]

# ===============================
# HIỂN THỊ THÔNG TIN
# ===============================
st.success("✅ Xác thực thành công")
st.subheader("THÔNG TIN CỦA BẠN")

result = {
    "Họ và tên": row["Họ và tên"],
    "Ngày sinh": row["NTNS"],
    "Lương chính": f"{row['Lương chính']:,}",
    "Vượt khung": f"{row['Vượt khung']:,}",
    "Phụ cấp chức vụ": f"{row['Phụ cấp chức vụ']:,}",
    "Thâm niên nhà giáo": f"{row['Thâm niên nhà giáo']:,}",
    "Cộng": f"{row['Cộng']:,}",
    "1% thu nhập/tháng": f"{row['1% thu nhập/tháng']:,}",
}

st.table(pd.DataFrame(result.items(), columns=["Nội dung", "Giá trị"]))

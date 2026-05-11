import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ===============================
# PAGE CONFIG (PHẢI ĐẶT TRƯỚC UI)
# ===============================
st.set_page_config(
    page_title="Tra cứu thông tin cá nhân",
    layout="centered"
)

# ===============================
# CSS: ẨN TOÀN BỘ UI RÁC STREAMLIT
# ===============================
st.markdown("""
<style>
/* Ẩn menu, header, footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Ẩn nút menu trên mobile */
button[kind="header"] {
    display: none !important;
}

/* Ẩn panel debug / dev nếu có */
.st-emotion-cache-1gv3huu,
.st-emotion-cache-1y4p8pa,
.st-emotion-cache-1dp5vir {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# CSS: LÀM RÕ Ô NHẬP MẬT KHẨU
# ===============================
st.markdown("""
<style>
input[type="password"], 
input[type="text"] {
    background-color: #ffffff !important;
    border: 2px solid #1f6fff !important;
    border-radius: 10px !important;
    padding: 14px !important;
    font-size: 18px !important;
    color: #000000 !important;
}

input[type="password"]:focus,
input[type="text"]:focus {
    outline: none !important;
    border-color: #0b5ed7 !important;
    box-shadow: 0 0 0 3px rgba(11, 94, 215, 0.25) !important;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# UI
# ===============================
st.title("TRA CỨU THÔNG TIN CÁ NHÂN")
st.write("🔐 Nhập **6 số cuối của CCCD** để xem thông tin của bạn.")

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

# ⚠️ ĐÚNG TÊN TAB CỦA BẠN
ws = sheet.worksheet("Sheet1")
df = pd.DataFrame(ws.get_all_records())

# ===============================
# INPUT MẬT KHẨU
# ===============================
password = st.text_input(
    "Mật khẩu",
    placeholder="Nhập 6 số cuối CCCD",
    type="password"
)

if not password:
    st.stop()

password = password.strip()

# ===============================
# KIỂM TRA MẬT KHẨU
# ===============================
if not password.isdigit() or len(password) != 6:
    st.error("❌ Mật khẩu phải gồm đúng 6 chữ số")
    st.stop()

def match_row(row):
    return str(row["Số CCCD"]).endswith(password)

matched = df[df.apply(match_row, axis=1)]

if matched.empty:
    st.error("❌ Không tìm thấy thông tin phù hợp")
    st.stop()

row = matched.iloc[0]

# ===============================
# HIỂN THỊ KẾT QUẢ
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

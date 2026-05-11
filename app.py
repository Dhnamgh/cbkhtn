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
# CSS: ẨN UI STREAMLIT + OVERLAY KHÓA CLICK
# ===============================
st.markdown("""
<style>
/* ===== ẨN MENU / HEADER / FOOTER ===== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
button[kind="header"] {display: none !important;}

/* ===== KHÓA TOÀN BỘ CLICK APP ===== */
[data-testid="stAppViewContainer"] {
    pointer-events: none;
}

/* ===== OVERLAY PHỦ TOÀN MÀN ===== */
#screen-lock {
    position: fixed;
    inset: 0;
    background: rgba(255,255,255,0.0);
    z-index: 9999;
}

/* ===== VÙNG DUY NHẤT ĐƯỢC TƯƠNG TÁC ===== */
#unlock-zone {
    position: fixed;
    top: 20%;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 450px;
    z-index: 10000;
    pointer-events: auto;
}

/* ===== STYLE Ô NHẬP RÕ RÀNG ===== */
input[type="password"], input[type="text"] {
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
    box-shadow: 0 0 0 3px rgba(11,94,215,0.25) !important;
}
</style>

<div id="screen-lock"></div>
""", unsafe_allow_html=True)

# ===============================
# KẾT NỐI GOOGLE SHEET
# ===============================
scope = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_info(
    st.secrets["SERVICE_ACCOUNT"],
    scopes=scope
)

gc = gspread.authorize(creds)
sheet = gc.open_by_key(st.secrets["GOOGLE_SHEET_ID"])
ws = sheet.worksheet("Sheet1")  # ĐÚNG TÊN TAB
df = pd.DataFrame(ws.get_all_records())

# ===============================
# GIAO DIỆN NGƯỜI DÙNG (BỊ KHOÁ)
# ===============================
st.title("TRA CỨU THÔNG TIN CÁ NHÂN")
st.markdown("🔐 Nhập **6 số cuối của CCCD** để xem thông tin của bạn.")

# ===============================
# VÙNG MỞ KHOÁ DUY NHẤT
# ===============================
st.markdown('<div id="unlock-zone">', unsafe_allow_html=True)

password = st.text_input(
    "Mật khẩu",
    placeholder="Nhập 6 số cuối CCCD",
    type="password"
)

st.markdown('</div>', unsafe_allow_html=True)

if not password:
    st.stop()

password = password.strip()

# ===============================
# KIỂM TRA MẬT KHẨU
# ===============================
if not password.isdigit() or len(password) != 6:
    st.error("❌ Mật khẩu phải gồm đúng 6 chữ số")
    st.stop()

matched = df[df["Số CCCD"].astype(str).str.endswith(password)]

if matched.empty:
    st.error("❌ Không tìm thấy thông tin phù hợp")
    st.stop()

row = matched.iloc[0]

# ===============================
# GỠ OVERLAY – CHO PHÉP XEM KẾT QUẢ
# ===============================
st.markdown("""
<style>
#screen-lock {display: none;}
[data-testid="stAppViewContainer"] {
    pointer-events: auto;
}
</style>
""", unsafe_allow_html=True)

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

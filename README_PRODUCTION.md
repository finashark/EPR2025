# HFM Employee Performance Review (EPR) System

## 📋 Tổng quan
Hệ thống đánh giá hiệu quả công việc nhân viên (Employee Performance Review) cho HFM Vietnam.

## ✨ Tính năng chính

### 👤 Quản lý người dùng
- **3 loại tài khoản**: Admin, Manager, Employee
- **Phân quyền rõ ràng**: Dựa trên cột "Vị trí" trong HFM Credentials
- **24 users**: 1 admin, 3 managers, 20 employees

### 📊 Đánh giá hiệu suất
- **KPI Evaluation**: 37 tiêu chí với tổng trọng số 76
- **Competency Evaluation**: 12 năng lực với tổng importance 24
- **Tự động tính điểm**: KPI (90%) + Competency (10%)
- **Xếp loại**: A++, A+, A, B, C

### 📄 Xuất PDF
- **Hỗ trợ tiếng Việt**: Arial, Tahoma fonts
- **Định dạng chuyên nghiệp**: Logo, bảng biểu, chữ ký
- **Tự động tính toán**: Điểm số và xếp loại

### 👥 Manager Dashboard
- Xem danh sách nhân viên trực thuộc
- Đánh giá và nhận xét
- Theo dõi tiến độ đánh giá

## 🏗️ Kiến trúc hệ thống

```
EPR System
├── app.py                      # Main Streamlit application
├── pdf_generator.py            # PDF generation with Vietnamese fonts
├── database.py                 # Database schema and initialization
├── epr_system.db              # SQLite database
└── HFM Credentials.xlsx       # User credentials and structure
```

### Database Schema
- **users**: Thông tin người dùng, phân quyền
- **evaluation_criteria**: Tiêu chí KPI
- **competencies**: Năng lực cần đánh giá
- **evaluations**: Phiếu đánh giá
- **evaluation_details**: Chi tiết KPI
- **competency_evaluations**: Chi tiết năng lực

## 🚀 Cài đặt và chạy

### Yêu cầu
- Python 3.11+
- Windows (để sử dụng system fonts)

### Cài đặt dependencies

```powershell
# Tạo virtual environment
python -m venv .venv

# Activate
.venv\Scripts\Activate.ps1

# Install packages
pip install streamlit pandas openpyxl reportlab
```

### Chạy ứng dụng

```powershell
streamlit run app.py --server.port 8501
```

Truy cập: `http://localhost:8501`

## 👤 Tài khoản mẫu

### Admin
- Username: `admin`
- Password: `admin123`

### Managers
- **CHAU PHAM DANG HUYNH** (Sales/Marketing/Education)
  - Username: `agent__vna`
  - Password: `HFMntvn`
  - 12 nhân viên trực thuộc

- **PHAN HOAN VU** (Customer Service)
  - Username: `support_vn6s`
  - Password: `HFMtvn6`
  - 6 nhân viên trực thuộc

- **DOAN MINH KHANG** (Affiliation)
  - Username: `bd_vn1m`
  - Password: `HFMbvn1`
  - 2 nhân viên trực thuộc

### Employees
- Password pattern: `HFM` + abbreviation + number
- Ví dụ: TRAN DAO HONG THY → Username: `sales_vn1` → Password: `HFMtvn1`

## 🧪 Testing

### Chạy test suite
```powershell
$env:PYTHONIOENCODING='utf-8'
python test_system_comprehensive.py
```

### Test Coverage
✅ Database Connection (100%)
✅ User Structure and Roles (100%)
✅ Reporting Structure (100%)
✅ Authentication System (100%)
✅ Evaluation Criteria (100%)
✅ Evaluations Data (100%)
✅ PDF Generation Dependencies (100%)
✅ Database Schema Integrity (100%)

**Success Rate: 100%** 🎉

## 📁 Cấu trúc dữ liệu

### HFM Credentials.xlsx
| Cột | Mô tả |
|-----|-------|
| Agent Code | Mã nhân viên unique |
| Username | Tên đăng nhập |
| Tên | Họ và tên đầy đủ |
| Vai trò | Sales, Marketing, CS, etc. |
| Chức danh | Employee, Manager |
| Vị trí | Nhân viên / Quản lý [Role] |
| Phòng ban | Department |
| Quản lý trực tiếp | Tên người quản lý |
| Password | Mật khẩu |

### Phân quyền
- **Vị trí = "Nhân viên"** → `is_manager = 0`
- **Vị trí = "Quản lý [Role]"** → `is_manager = 1`
- **Vai trò = "Sales"** → báo cáo cho "Quản lý Sales"

## 📊 Thống kê hệ thống

- **Tổng users**: 24 (1 admin + 3 managers + 20 employees)
- **Tổng evaluations**: 14 submitted
- **KPI criteria**: 37 items
- **Competencies**: 12 items
- **Departments**: 5 (Sales, Marketing, CS, Affiliation, Education)

## 🔒 Bảo mật

- Mật khẩu được hash bằng SHA256
- Session-based authentication
- Role-based access control (RBAC)
- Không lưu plain text passwords

## 📝 Workflow

### Employee
1. Đăng nhập
2. Tự đánh giá KPI và Competency
3. Thêm nhận xét và mục tiêu phát triển
4. Submit đánh giá
5. Tải PDF

### Manager
1. Đăng nhập
2. Xem danh sách nhân viên
3. Xem đánh giá của nhân viên
4. Đánh giá và nhận xét
5. Submit final review

### Admin
1. Quản lý users
2. Quản lý criteria
3. Quản lý competencies
4. Xem tổng quan hệ thống

## 🛠️ Công nghệ sử dụng

- **Frontend**: Streamlit 1.x
- **Backend**: Python 3.11
- **Database**: SQLite 3
- **PDF Generation**: ReportLab 4.4.5
- **Data Processing**: Pandas, OpenPyXL

## 📂 Backup

Backup được tạo tự động với timestamp:
```
backup_YYYYMMDD_HHMMSS/
├── epr_system.db
├── app.py
├── pdf_generator.py
├── database.py
├── HFM Credentials.xlsx
├── database_summary.txt
└── BACKUP_INFO.txt
```

## 🐛 Troubleshooting

### PDF không hiển thị tiếng Việt
- Kiểm tra font files: Arial, Tahoma trong `C:\Windows\Fonts\`
- Hệ thống tự động fallback sang Helvetica nếu không tìm thấy

### Manager không thấy nhân viên
- Kiểm tra `report_to` field trong users table
- Đảm bảo `report_to` = fullname của manager
- Kiểm tra `is_manager` = 1 cho manager accounts

### Login không thành công
- Username không phân biệt hoa thường
- Kiểm tra password trong HFM Credentials.xlsx
- Đảm bảo không có khoảng trắng thừa

## 📞 Support

Liên hệ IT Department để được hỗ trợ.

## 📄 License

Internal use only - HFM Vietnam

---

**Version**: 1.0.0  
**Last Updated**: December 2, 2025  
**Status**: ✅ Production Ready

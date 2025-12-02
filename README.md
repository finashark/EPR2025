# HFM Employee Performance Review System

## 🚀 Quick Deploy to Streamlit Cloud

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

### Step 1: Deploy
1. Visit https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select:
   - Repository: `finashark/EPR2025`
   - Branch: `main`
   - Main file: `app.py`
5. Click "Deploy!"

### Step 2: Access
- Wait 2-5 minutes for deployment
- Your app will be live at: `https://your-app.streamlit.app`

## 📋 Features

- **Role-Based Access**: Admin, Manager, Employee dashboards
- **KPI Evaluation**: 37 criteria with weighted scoring
- **Competency Assessment**: 12 competencies with importance levels
- **PDF Export**: Vietnamese font support (Arial, Tahoma)
- **Auto Calculation**: KPI (90%) + Competency (10%) = Final Score
- **Rating System**: A++, A+, A, B, C

## 👤 Demo Accounts

### Admin
- Username: `admin`
- Password: `admin123`

### Manager (Sales/Marketing)
- Username: `agent__vna`
- Password: `HFMntvn`

### Manager (Customer Service)
- Username: `support_vn6s`
- Password: `HFMtvn6`

### Manager (Affiliation)
- Username: `bd_vn1m`
- Password: `HFMbvn1`

## 🛠️ Tech Stack

- **Frontend**: Streamlit 1.51+
- **Backend**: Python 3.11
- **Database**: SQLite
- **PDF**: ReportLab 4.4.5
- **Data**: Pandas, OpenPyXL

## 📊 System Stats

- **Users**: 24 (1 admin + 3 managers + 20 employees)
- **Evaluations**: 14 submitted
- **KPI Criteria**: 37 items
- **Competencies**: 12 items
- **Test Coverage**: 100%

## 📖 Documentation

- [Production README](README_PRODUCTION.md) - Complete system documentation
- [Deployment Guide](DEPLOYMENT.md) - Detailed deployment instructions

## 🔐 Security

- SHA256 password hashing
- Session-based authentication
- Role-based access control
- No plain text passwords

## 📞 Support

For issues or questions, open an issue on GitHub.

## 📄 License

Internal use only - HFM Vietnam

---

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: December 2, 2025

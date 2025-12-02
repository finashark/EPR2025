# 🚀 Deployment Guide - HFM EPR System

## Pre-deployment Checklist

### ✅ Before Deployment

1. **Backup database**
   ```powershell
   python create_backup.py
   ```

2. **Run test suite**
   ```powershell
   $env:PYTHONIOENCODING='utf-8'
   python test_system_comprehensive.py
   ```
   - Ensure 100% test pass rate

3. **Cleanup temporary files**
   ```powershell
   python cleanup_for_production.py
   ```

4. **Verify production files**
   - app.py
   - pdf_generator.py
   - database.py
   - epr_system.db
   - HFM Credentials.xlsx
   - requirements.txt
   - README_PRODUCTION.md
   - .env.example

---

## 📦 Deployment to Streamlit Cloud

### Step 1: Prepare Repository

1. **Initialize Git (if not already)**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit - HFM EPR System v1.0"
   ```

2. **Create GitHub repository**
   - Go to https://github.com/new
   - Name: `hfm-epr-system`
   - Make it **Private** (contains sensitive data)

3. **Push to GitHub**
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/hfm-epr-system.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with GitHub

2. **New app**
   - Click "New app"
   - Repository: `YOUR_USERNAME/hfm-epr-system`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: Choose custom subdomain (e.g., `hfm-epr`)

3. **Advanced settings**
   - Python version: `3.11`
   - Secrets: Add if needed (for .env variables)

4. **Deploy**
   - Click "Deploy!"
   - Wait for deployment (2-5 minutes)

### Step 3: Post-deployment

1. **Test deployment**
   - Login with admin account
   - Test manager dashboard
   - Test employee dashboard
   - Generate PDF

2. **Configure custom domain** (optional)
   - Settings → Custom domain
   - Add your domain (e.g., epr.hfm.vn)

---

## 🖥️ Local Server Deployment

### Option 1: Windows Server

1. **Install Python 3.11**
   ```powershell
   # Download from python.org
   # Add to PATH during installation
   ```

2. **Clone repository**
   ```powershell
   git clone https://github.com/YOUR_USERNAME/hfm-epr-system.git
   cd hfm-epr-system
   ```

3. **Setup virtual environment**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```powershell
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run application**
   ```powershell
   streamlit run app.py --server.port 8501
   ```

6. **Access**
   - Local: http://localhost:8501
   - Network: http://YOUR_SERVER_IP:8501

### Option 2: Run as Windows Service

1. **Install NSSM** (Non-Sucking Service Manager)
   ```powershell
   choco install nssm
   ```

2. **Create service**
   ```powershell
   nssm install HFM_EPR "D:\HFM\Employee\EPR 2025 02\.venv\Scripts\python.exe" "-m streamlit run app.py --server.port 8501"
   nssm set HFM_EPR AppDirectory "D:\HFM\Employee\EPR 2025 02"
   nssm start HFM_EPR
   ```

3. **Manage service**
   ```powershell
   nssm stop HFM_EPR      # Stop
   nssm restart HFM_EPR   # Restart
   nssm remove HFM_EPR    # Remove
   ```

---

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  epr:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./epr_system.db:/app/epr_system.db
      - ./HFM Credentials.xlsx:/app/HFM Credentials.xlsx
    environment:
      - STREAMLIT_SERVER_PORT=8501
    restart: unless-stopped
```

### Deploy with Docker

```powershell
# Build image
docker build -t hfm-epr:latest .

# Run container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🔐 Security Considerations

### Production Checklist

- [ ] Change default admin password
- [ ] Use strong passwords for all accounts
- [ ] Enable HTTPS (use reverse proxy like Nginx)
- [ ] Restrict network access (firewall rules)
- [ ] Regular database backups
- [ ] Keep dependencies updated
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables for sensitive data

### HTTPS Setup (Nginx)

```nginx
server {
    listen 80;
    server_name epr.hfm.vn;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name epr.hfm.vn;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📊 Monitoring & Maintenance

### Daily Tasks
- Check application logs
- Monitor user login issues
- Verify PDF generation

### Weekly Tasks
- Database backup
- Review evaluation submissions
- Check system performance

### Monthly Tasks
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Review and cleanup old evaluations
- User access audit

### Backup Strategy

```powershell
# Daily backup script
$date = Get-Date -Format "yyyyMMdd"
Copy-Item "epr_system.db" -Destination "backups\epr_system_$date.db"

# Keep last 30 days
Get-ChildItem "backups\*.db" | 
    Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | 
    Remove-Item
```

---

## 🆘 Troubleshooting

### Application won't start
```powershell
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check port
netstat -ano | findstr :8501
```

### Database locked error
```powershell
# Stop all Python processes
Get-Process python | Stop-Process -Force

# Restart application
streamlit run app.py
```

### PDF generation fails
- Verify font files exist: `C:\Windows\Fonts\arial.ttf`
- Check reportlab version: `pip show reportlab`
- Review error logs in Streamlit

### Performance issues
- Check database size: `dir epr_system.db`
- Optimize queries (add indexes if needed)
- Increase server resources (RAM, CPU)

---

## 📞 Support Contacts

**Technical Support**: IT Department
**System Admin**: [Your Name]
**Last Updated**: December 2, 2025

---

## 📝 Deployment Log Template

```
=== DEPLOYMENT LOG ===
Date: YYYY-MM-DD HH:MM
Version: 1.0.0
Deployed by: [Name]
Environment: [Production/Staging]
Server: [IP/Domain]

Pre-deployment:
- [ ] Backup created
- [ ] Tests passed (100%)
- [ ] Files cleaned up

Deployment:
- [ ] Code pushed to Git
- [ ] Streamlit Cloud deployed / Server started
- [ ] Application accessible
- [ ] Login tested
- [ ] PDF generation tested

Post-deployment:
- [ ] Users notified
- [ ] Documentation updated
- [ ] Monitoring enabled

Issues: None / [Description]
Notes: [Any additional notes]
```

---

**Status**: ✅ Ready for Production
**Version**: 1.0.0

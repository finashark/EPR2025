"""
Database schema and initialization for EPR System
"""
import sqlite3
import json
import hashlib
from datetime import datetime

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """Initialize the database with all necessary tables"""
    conn = sqlite3.connect('epr_system.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        fullname TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        department TEXT,
        role_type TEXT NOT NULL,
        area TEXT,
        report_to TEXT,
        emp_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Evaluation criteria table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS evaluation_criteria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        department TEXT NOT NULL,
        kra_name TEXT NOT NULL,
        description TEXT,
        weight REAL NOT NULL,
        category TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Evaluations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        year INTEGER NOT NULL,
        period TEXT,
        status TEXT DEFAULT 'draft',
        employee_score REAL,
        employee_comment TEXT,
        development_areas TEXT,
        employee_submitted_at TIMESTAMP,
        manager_score REAL,
        manager_comment TEXT,
        manager_submitted_at TIMESTAMP,
        final_score REAL,
        rating TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Evaluation details table (for each criterion)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS evaluation_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evaluation_id INTEGER NOT NULL,
        criterion_id INTEGER NOT NULL,
        employee_score REAL,
        employee_comment TEXT,
        manager_score REAL,
        manager_comment TEXT,
        final_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (evaluation_id) REFERENCES evaluations (id),
        FOREIGN KEY (criterion_id) REFERENCES evaluation_criteria (id)
    )
    ''')
    
    # Competencies table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS competencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        importance_level INTEGER DEFAULT 2,
        category TEXT,
        level_1 TEXT,
        level_2 TEXT,
        level_3 TEXT,
        level_4 TEXT,
        level_5 TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Competency evaluations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS competency_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evaluation_id INTEGER NOT NULL,
        competency_id INTEGER NOT NULL,
        employee_level INTEGER,
        employee_comment TEXT,
        manager_level INTEGER,
        manager_comment TEXT,
        final_level INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (evaluation_id) REFERENCES evaluations (id),
        FOREIGN KEY (competency_id) REFERENCES competencies (id)
    )
    ''')
    
    conn.commit()
    
    # Insert default admin user
    try:
        cursor.execute('''
        INSERT INTO users (code, fullname, username, password, department, role_type, emp_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('ADMIN001', 'Administrator', 'admin', hash_password('admin123'), 'IT', 'admin', 'Full-time'))
        
        # Insert sample manager
        cursor.execute('''
        INSERT INTO users (code, fullname, username, password, department, role_type, emp_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('MGR001', 'Manager Test', 'manager', hash_password('manager123'), 'Sales', 'manager', 'Full-time'))
        
        # Insert sample employee
        cursor.execute('''
        INSERT INTO users (code, fullname, username, password, department, role_type, emp_type, report_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('EMP001', 'Employee Test', 'employee', hash_password('employee123'), 'Sales', 'employee', 'Full-time', 'MGR001'))
        
        conn.commit()
        print("Default users created:")
        print("  Admin: username='admin', password='admin123'")
        print("  Manager: username='manager', password='manager123'")
        print("  Employee: username='employee', password='employee123'")
    except sqlite3.IntegrityError:
        print("Default users already exist")
    
    # Insert sample evaluation criteria
    criteria_data = [
        ('Sales', 'Duy trì dịch vụ xuyên suốt', 'Đảm bảo các hoạt động dịch vụ khách hàng liên tục', 30, 'KPI'),
        ('Sales', 'Duy trì kỷ luật và văn hóa', 'Tuân thủ nội quy, quy trình làm việc', 20, 'KPI'),
        ('Sales', 'Cập nhật thị trường', 'Nắm bắt xu hướng và đề xuất giải pháp', 20, 'KPI'),
        ('Sales', 'Hoàn thành công việc được giao', 'Đảm bảo tiến độ và chất lượng công việc', 30, 'KPI'),
        ('Office', 'Duy trì dịch vụ xuyên suốt', 'Đảm bảo các hoạt động hỗ trợ liên tục', 30, 'KPI'),
        ('Office', 'Duy trì kỷ luật và văn hóa', 'Tuân thủ nội quy, quy trình làm việc', 20, 'KPI'),
        ('Office', 'Cập nhật thị trường', 'Nắm bắt xu hướng và đề xuất giải pháp', 20, 'KPI'),
        ('Office', 'Hoàn thành công việc được giao', 'Đảm bảo tiến độ và chất lượng công việc', 30, 'KPI'),
    ]
    
    try:
        cursor.executemany('''
        INSERT INTO evaluation_criteria (department, kra_name, description, weight, category)
        VALUES (?, ?, ?, ?, ?)
        ''', criteria_data)
        conn.commit()
        print(f"Inserted {len(criteria_data)} evaluation criteria")
    except sqlite3.IntegrityError:
        print("Evaluation criteria already exist")
    
    # Insert competencies
    competencies_data = [
        ('Chính trực (Integrity)', 'Hành động trung thực, đáng tin cậy', 
         'Tuân thủ quy định cơ bản', 'Thực hiện nhất quán', 'Là tấm gương', 
         'Định hướng văn hóa', 'Là chuyên gia mẫu mực'),
        ('Làm việc nhóm (Teamwork)', 'Hợp tác hiệu quả với đồng nghiệp',
         'Tham gia nhóm', 'Đóng góp tích cực', 'Hỗ trợ thành viên',
         'Dẫn dắt nhóm', 'Xây dựng văn hóa'),
        ('Định hướng khách hàng', 'Tập trung vào nhu cầu khách hàng',
         'Phản hồi cơ bản', 'Giải quyết vấn đề', 'Chủ động hỗ trợ',
         'Tạo trải nghiệm tốt', 'Là chuyên gia dịch vụ'),
    ]
    
    try:
        cursor.executemany('''
        INSERT INTO competencies (name, description, level_1, level_2, level_3, level_4, level_5)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', competencies_data)
        conn.commit()
        print(f"Inserted {len(competencies_data)} competencies")
    except sqlite3.IntegrityError:
        print("Competencies already exist")
    
    conn.close()
    print("\nDatabase initialized successfully!")

if __name__ == "__main__":
    init_database()

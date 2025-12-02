# -*- coding: utf-8 -*-
"""
EPR System - Employee Performance Review Application
Main Streamlit Application
"""
import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime
import io
from pdf_generator import generate_evaluation_pdf

# Page configuration
st.set_page_config(
    page_title="HFM EPR System 2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database helper functions
def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect('epr_system.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """Authenticate user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Case-insensitive username search
    cursor.execute(
        "SELECT * FROM users WHERE LOWER(username) = LOWER(?) AND password = ?",
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_evaluations(user_id):
    """Get all evaluations for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM evaluations WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    evaluations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return evaluations

def get_evaluation_criteria(department):
    """Get evaluation criteria for a department"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Tìm theo department chính xác để tránh lấy nhầm criteria của department khác
    cursor.execute(
        "SELECT * FROM evaluation_criteria WHERE department = ? ORDER BY category, kra_name",
        (department,)
    )
    criteria = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return criteria

def get_all_competencies():
    """Get all competencies ordered by category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM competencies 
        ORDER BY 
            CASE category 
                WHEN 'A. Năng lực cốt lõi' THEN 1
                WHEN 'B. Năng lực quản lý, lãnh đạo' THEN 2
                WHEN 'C. Năng lực chuyên môn' THEN 3
                ELSE 4
            END,
            id
    """)
    competencies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return competencies

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Login page
def login_page():
    """Display login page"""
    st.title("🏢 HFM EPR System 2025")
    st.subheader("Hệ thống Đánh giá Hiệu quả Công việc")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Đăng nhập")
        username = st.text_input("Tên đăng nhập", key="username")
        password = st.text_input("Mật khẩu", type="password", key="password")
        
        if st.button("Đăng nhập", use_container_width=True):
            user = authenticate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success(f"Chào mừng {user['fullname']}!")
                st.rerun()
            else:
                st.error("Tên đăng nhập hoặc mật khẩu không đúng!")

# Employee dashboard
def employee_dashboard():
    """Dashboard for employees"""
    st.title("📝 Tự Đánh giá")
    
    # Header information
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Họ Tên Nhân viên:** {st.session_state.user['fullname']}")
        st.markdown(f"**Mã Nhân viên:** {st.session_state.user['code']}")
        st.markdown(f"**Bộ phận:** {st.session_state.user['department']}")
        st.markdown(f"**Vai trò:** {st.session_state.user.get('role_type', 'N/A')}")
    with col2:
        st.markdown(f"**Chức vụ/chức danh:** {st.session_state.user['emp_type']}")
        st.markdown(f"**Quản lý trực tiếp:** {st.session_state.user.get('report_to', 'N/A')}")
        st.markdown(f"**Ngày đánh giá:** {datetime.now().strftime('%d/%m/%Y')}")
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📋 Đánh giá mới", "📊 Lịch sử đánh giá"])
    
    with tab1:
        st.markdown("### Phần 1: Đánh giá hiệu quả công việc năm 2025")
        st.info("**Mục tiêu:** Duy trì dịch vụ xuyên suốt, kỷ luật & văn hóa doanh nghiệp, thích ứng thị trường.")
        
        # Get criteria for user's department
        department = st.session_state.user['department']
        criteria = get_evaluation_criteria(department)
        
        if not criteria:
            st.error(f"❌ Không tìm thấy tiêu chí đánh giá cho phòng ban '{department}'.")
            
            # Hiển thị các phòng ban có tiêu chí
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT department FROM evaluation_criteria")
            available_depts = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if available_depts:
                st.info(f"📋 Các phòng ban đã có tiêu chí:\n\n" + "\n".join([f"- {d}" for d in available_depts]))
            
            return
        
        # Có tiêu chí - hiển thị thông tin
        st.success(f"✅ Tìm thấy {len(criteria)} tiêu chí đánh giá cho phòng ban '{department}'.")
        
        # Initialize session state for storing evaluation data
        if 'eval_scores' not in st.session_state:
            st.session_state.eval_scores = {}
        if 'eval_comments' not in st.session_state:
            st.session_state.eval_comments = {}
        if 'eval_comp_levels' not in st.session_state:
            st.session_state.eval_comp_levels = {}
        if 'eval_comp_comments' not in st.session_state:
            st.session_state.eval_comp_comments = {}
        if 'show_results' not in st.session_state:
            st.session_state.show_results = False
        
        st.markdown("#### MỤC TIÊU CÔNG VIỆC")
        
        # Use form to prevent Enter from submitting
        with st.form("employee_evaluation", clear_on_submit=False):
            scores = {}
            comments = {}
            
            # Group criteria by category
            categories = {}
            for criterion in criteria:
                cat = criterion.get('category', 'Khác')
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(criterion)
            
            # Display each category
            for category, items in categories.items():
                st.markdown(f"### {category}")
                total_weight = sum(item['weight'] for item in items)
                st.caption(f"Tổng trọng số: {total_weight} điểm")
                
                for criterion in items:
                    # Extract KRA code and description
                    kra_parts = criterion['kra_name'].split(' - ', 1)
                    kra_code = kra_parts[0] if len(kra_parts) > 1 else ''
                    kra_desc = kra_parts[1] if len(kra_parts) > 1 else criterion['kra_name']
                    
                    with st.container():
                        st.markdown(f"**{kra_code}** {kra_desc}")
                        
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.caption(f"📏 Cách đo lường: {criterion['description']}")
                        
                        with col2:
                            scores[criterion['id']] = st.number_input(
                                "Dữ liệu thực tế (%)",
                                min_value=0.0,
                                max_value=150.0,
                                value=100.0,
                                step=1.0,
                                key=f"score_{criterion['id']}"
                            )
                        
                        with col3:
                            st.metric("Trọng số", f"{criterion['weight']}")
                        
                        # Rating scale guide
                        with st.expander("📊 Thang đánh giá"):
                            cols = st.columns(6)
                            labels = [("Chưa đạt", "<70%"), ("Đạt", "70-89%"), 
                                     ("Tốt", "90-100%"), ("Xuất sắc", ">100%"),
                                     ("Vượt mức", "120%"), ("Xuất sắc", "150%")]
                            for col, (label, range_val) in zip(cols, labels):
                                col.caption(f"{label}\n{range_val}")
                        
                        comments[criterion['id']] = st.text_input(
                            "Ghi chú/Minh chứng",
                            key=f"comment_{criterion['id']}"
                        )
                        st.markdown("---")
            
            st.markdown("")  # Spacing
            
            st.markdown("---")
            st.markdown("### Phần 2: KPI Năng Lực")
            st.info("Quản lý trực tiếp và nhân viên sẽ thảo luận và liệt kê những năng lực mà nhân viên cần phát huy trong quá trình làm việc.")
            
            competencies = get_all_competencies()
            comp_levels = {}
            comp_comments = {}
            
            # Group competencies by category
            comp_categories = {}
            for comp in competencies:
                cat = comp.get('category', 'Khác')
                if cat not in comp_categories:
                    comp_categories[cat] = []
                comp_categories[cat].append(comp)
            
            # Display competencies by category
            for category, comps in comp_categories.items():
                st.markdown(f"### {category}")
                
                if category == 'A. Năng lực cốt lõi':
                    st.caption("Năng lực cốt lõi và Mức độ quan trọng của phần này là cố định và áp dụng cho toàn bộ nhân viên")
                elif category == 'B. Năng lực quản lý, lãnh đạo':
                    st.caption("Năng lực quản lý, lãnh đạo và Mức độ quan trọng của phần này chỉ áp dụng đối với các nhân viên đang giữ vị trí quản lý (Khối, phòng, bộ phận, nhóm)")
                elif category == 'C. Năng lực chuyên môn':
                    st.caption("Trưởng bộ phận xác định năng lực chuyên môn cần thiết cho các vị trí công việc của bộ phận")
                
                for comp in comps:
                    with st.container():
                        # Competency name and importance
                        col_header1, col_header2 = st.columns([3, 1])
                        with col_header1:
                            st.markdown(f"**{comp['name']}**")
                            st.caption(comp['description'])
                        with col_header2:
                            st.metric("Mức độ quan trọng", comp.get('importance_level', 2))
                        
                        # Show level scale
                        with st.expander("📊 Thang năng lực (Cấp độ 1-5)"):
                            scale_cols = st.columns(5)
                            scale_labels = [
                                ("Cấp độ 1: Nhận thức (50%)", comp['level_1']),
                                ("Cấp độ 2: Cơ bản (80%)", comp['level_2']),
                                ("Cấp độ 3: Trung bình (100%)", comp['level_3']),
                                ("Cấp độ 4: Cao cấp (120%)", comp['level_4']),
                                ("Cấp độ 5: Chuyên gia (150%)", comp['level_5'])
                            ]
                            for col, (title, desc) in zip(scale_cols, scale_labels):
                                col.caption(f"**{title}**")
                                col.caption(desc)
                        
                        # Assessment inputs
                        col1, col2, col3 = st.columns([1, 1, 2])
                        
                        # Map level to percentage: 1->50%, 2->80%, 3->100%, 4->120%, 5->150%
                        level_percentages = {1: 50, 2: 80, 3: 100, 4: 120, 5: 150}
                        
                        with col1:
                            selected_level = st.number_input(
                                "NV đánh giá (Cấp độ)",
                                min_value=1,
                                max_value=5,
                                value=3,
                                step=1,
                                key=f"comp_{comp['id']}",
                                help="Cấp 1→50% | Cấp 2→80% | Cấp 3→100% | Cấp 4→120% | Cấp 5→150%"
                            )
                            comp_levels[comp['id']] = selected_level
                            
                            # Show mapping
                            st.caption(f"**Điểm thực tế: {level_percentages[selected_level]}%** • Quy tắc: 1→50% | 2→80% | 3→100% | 4→120% | 5→150%")
                        
                        with col2:
                            st.text("")  # Placeholder for alignment
                        
                        with col3:
                            comp_comments[comp['id']] = st.text_area(
                                "Minh chứng/Ví dụ cụ thể",
                                key=f"comp_comment_{comp['id']}",
                                height=80,
                                help="Đưa ra ví dụ cụ thể thể hiện năng lực này"
                            )
                        
                        st.markdown("---")
                
            st.markdown("")  # Spacing
        
            st.markdown("---")
            st.markdown("#### Phần 3: Sơ kết")
            st.info("📊 Phần điểm số sẽ được tính tự động")
            
            # Calculate scores preview
            kpi_score = sum(scores.get(cid, 0) * c['weight'] for c in criteria for cid in [c['id']] if cid in scores)
            total_kpi_weight = sum(c['weight'] for c in criteria)
            kpi_result = (kpi_score / total_kpi_weight) if total_kpi_weight > 0 else 0
            
            # Calculate competency score
            # Map level to percentage: 1->50%, 2->80%, 3->100%, 4->120%, 5->150%
            level_percentages = {1: 50, 2: 80, 3: 100, 4: 120, 5: 150}
            comp_score = sum(level_percentages[comp_levels.get(c['id'], 3)] * c.get('importance_level', 2)
                           for c in competencies if c['id'] in comp_levels)
            total_comp_weight = sum(c.get('importance_level', 2) * 100 for c in competencies)
            comp_result = (comp_score / total_comp_weight * 100) if total_comp_weight > 0 else 0
            
            # Final calculation
            final_score = kpi_result * 0.9 + comp_result * 0.1
            
            # Determine rating
            rating = "C"
            rating_emoji = "🔴"
            if final_score >= 135:
                rating = "A++"
                rating_emoji = "🏆"
            elif final_score >= 120:
                rating = "A+"
                rating_emoji = "🥇"
            elif final_score >= 100:
                rating = "A"
                rating_emoji = "🟢"
            elif final_score >= 80:
                rating = "B"
                rating_emoji = "🟡"
            
            # Display summary table with improved UI
            st.markdown("")
            
            # Header row
            col_h1, col_h2, col_h3, col_h4 = st.columns([2, 2, 2, 1.5])
            with col_h1:
                st.markdown("<h6 style='text-align: center; color: #666;'>Trọng số</h6>", unsafe_allow_html=True)
            with col_h2:
                st.markdown("<h6 style='text-align: center; color: #666;'>Kết quả thực tế</h6>", unsafe_allow_html=True)
            with col_h3:
                st.markdown("<h6 style='text-align: center; color: #666;'>Kết quả sau cùng</h6>", unsafe_allow_html=True)
            with col_h4:
                st.markdown("<h6 style='text-align: center; color: #666;'>Xếp hạng</h6>", unsafe_allow_html=True)
            
            # KPI Thành tích row
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1.5])
            with col1:
                st.markdown("<div style='background-color: #f0f8ff; padding: 10px; border-radius: 5px; text-align: center;'>"
                          "<b>KPI Thành tích</b><br><span style='font-size: 24px; color: #1f77b4;'>90%</span></div>", 
                          unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='background-color: #f0f8ff; padding: 10px; border-radius: 5px; text-align: center;'>"
                          f"<span style='font-size: 24px; color: #1f77b4; font-weight: bold;'>{kpi_result:.1f}%</span></div>", 
                          unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div style='background-color: #e6f3ff; padding: 10px; border-radius: 5px; text-align: center;'>"
                          f"<span style='font-size: 24px; color: #0066cc; font-weight: bold;'>{kpi_result * 0.9:.1f}%</span></div>", 
                          unsafe_allow_html=True)
            with col4:
                st.markdown("")
            
            # KPI Năng lực row
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1.5])
            with col1:
                st.markdown("<div style='background-color: #fff5e6; padding: 10px; border-radius: 5px; text-align: center;'>"
                          "<b>KPI Năng lực</b><br><span style='font-size: 24px; color: #ff8c00;'>10%</span></div>", 
                          unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='background-color: #fff5e6; padding: 10px; border-radius: 5px; text-align: center;'>"
                          f"<span style='font-size: 24px; color: #ff8c00; font-weight: bold;'>{comp_result:.1f}%</span></div>", 
                          unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div style='background-color: #ffe6cc; padding: 10px; border-radius: 5px; text-align: center;'>"
                          f"<span style='font-size: 24px; color: #cc6600; font-weight: bold;'>{comp_result * 0.1:.1f}%</span></div>", 
                          unsafe_allow_html=True)
            with col4:
                st.markdown("")
            
            st.markdown("")
            
            # Final result row
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1.5])
            with col1:
                st.markdown("<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; text-align: center;'>"
                          "<b>Kết quả đánh giá</b></div>", 
                          unsafe_allow_html=True)
            with col2:
                st.markdown("")
            with col3:
                delta_sign = "+" if final_score >= 100 else ""
                delta_color = "#28a745" if final_score >= 100 else "#dc3545"
                st.markdown(f"<div style='background-color: #e8f5e9; padding: 15px; border-radius: 5px; text-align: center; border: 2px solid #4caf50;'>"
                          f"<span style='font-size: 32px; color: #2e7d32; font-weight: bold;'>{final_score:.1f}%</span><br>"
                          f"<span style='font-size: 14px; color: {delta_color};'>{delta_sign}{final_score - 100:.1f}%</span></div>", 
                          unsafe_allow_html=True)
            with col4:
                st.markdown(f"<div style='background-color: #fff3e0; padding: 15px; border-radius: 5px; text-align: center; border: 2px solid #ff9800;'>"
                          f"<span style='font-size: 36px;'>{rating_emoji}</span><br>"
                          f"<span style='font-size: 28px; color: #f57c00; font-weight: bold;'>{rating}</span></div>", 
                          unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### Phần 4: Lĩnh vực cần phát triển")
            st.info("Nhân viên hoàn tất phần này và thảo luận cùng với Cấp trên trực tiếp để đảm bảo sự hiểu rõ kết quả nhận cầu phát triển của mỗi nhân viên và tổ chức.")
            
            development_areas = st.text_area(
                "📈 Lĩnh vực cần phát triển và Kế hoạch hành động",
                height=120,
                placeholder="Nêu rõ những lĩnh vực bạn muốn cải thiện trong năm tới và các bước cụ thể để đạt được mục tiêu..."
            )
            
            overall_comment = st.text_area(
                "💬 Ý kiến khác / Nhận xét chung",
                height=100,
                placeholder="Các ý kiến khác về quá trình đánh giá, mong muốn về công việc, điều kiện làm việc..."
            )
            
            st.markdown("---")
            
            # Two buttons: Calculate and Submit  
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                calculate_btn = st.form_submit_button("🧮 Tính điểm", use_container_width=True, type="primary")
            with col_btn2:
                submit_btn = st.form_submit_button("📤 Nộp hồ sơ", use_container_width=True, type="secondary")
            
            if calculate_btn:
                st.success("✅ Đã tính điểm! Vui lòng xem Phần 3: Sơ kết ở trên.")
                st.info("💡 Sau khi kiểm tra điểm số, nhấn '📤 Nộp hồ sơ' để lưu vào hệ thống.")
            
            if submit_btn:
                # Save to database
                conn = get_db_connection()
                cursor = conn.cursor()
                
                try:
                    # Create evaluation record
                    cursor.execute('''
                    INSERT INTO evaluations 
                    (user_id, year, period, status, employee_score, employee_comment, development_areas, employee_submitted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (st.session_state.user['id'], 2025, 'Annual', 'submitted', 
                          final_score, overall_comment, development_areas, datetime.now()))
                    
                    evaluation_id = cursor.lastrowid
                    
                    # Save criterion details
                    for criterion_id, score in scores.items():
                        cursor.execute('''
                        INSERT INTO evaluation_details 
                        (evaluation_id, criterion_id, employee_score, employee_comment)
                        VALUES (?, ?, ?, ?)
                        ''', (evaluation_id, criterion_id, score, comments.get(criterion_id, '')))
                    
                    # Save competency evaluations
                    for comp_id, level in comp_levels.items():
                        cursor.execute('''
                        INSERT INTO competency_evaluations
                        (evaluation_id, competency_id, employee_level, employee_comment)
                        VALUES (?, ?, ?, ?)
                        ''', (evaluation_id, comp_id, level, comp_comments.get(comp_id, '')))
                    
                    conn.commit()
                    
                    # Display results
                    st.success(f"✅ Đánh giá đã được lưu thành công!")
                    
                    result_col1, result_col2, result_col3 = st.columns(3)
                    with result_col1:
                        st.metric("Điểm KPI Thành tích", f"{kpi_result:.1f}%")
                    with result_col2:
                        st.metric("Điểm KPI Năng lực", f"{comp_result:.1f}%")
                    with result_col3:
                        st.metric("Tổng điểm", f"{final_score:.1f}%", 
                                 delta=f"Xếp hạng: {rating}")
                    
                    st.balloons()
                    
                except Exception as e:
                    conn.rollback()
                    st.error(f"Lỗi khi lưu đánh giá: {str(e)}")
                finally:
                    conn.close()
    
    with tab2:
        st.markdown("### 📋 Lịch sử đánh giá")
        evaluations = get_user_evaluations(st.session_state.user['id'])
        
        if not evaluations:
            st.info("Bạn chưa có đánh giá nào.")
        else:
            for eval in evaluations:
                # Calculate rating
                score = eval['employee_score'] or 0
                if score >= 135:
                    rating = "A++"
                    rating_color = "🟢"
                elif score >= 120:
                    rating = "A+"
                    rating_color = "🟢"
                elif score >= 100:
                    rating = "A"
                    rating_color = "🟡"
                elif score >= 80:
                    rating = "B"
                    rating_color = "🟠"
                else:
                    rating = "C"
                    rating_color = "🔴"
                
                with st.expander(f"📅 Đánh giá năm {eval['year']} - {eval['period']} | {rating_color} Xếp hạng: {rating} ({eval['status']})"):
                    
                    # Summary metrics
                    st.markdown("#### 📊 Tổng quan điểm số")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Điểm tự đánh giá", 
                                 f"{eval['employee_score']:.1f}%" if eval['employee_score'] else "N/A")
                    with col2:
                        st.metric("Điểm quản lý", 
                                 f"{eval['manager_score']:.1f}%" if eval['manager_score'] else "Chưa đánh giá")
                    with col3:
                        st.metric("Điểm cuối cùng", 
                                 f"{eval['final_score']:.1f}%" if eval['final_score'] else "Chưa có")
                    with col4:
                        st.metric("Xếp hạng", rating, delta_color="off")
                    
                    st.markdown("---")
                    
                    # Get detailed criteria scores
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # KPI Details
                    st.markdown("#### 📈 Chi tiết KPI Thành tích")
                    cursor.execute('''
                        SELECT ec.category, ec.kra_name, ec.description, ec.weight,
                               ed.employee_score, ed.employee_comment
                        FROM evaluation_details ed
                        JOIN evaluation_criteria ec ON ed.criterion_id = ec.id
                        WHERE ed.evaluation_id = ?
                        ORDER BY ec.category, ec.kra_name
                    ''', (eval['id'],))
                    
                    kpi_details = cursor.fetchall()
                    if kpi_details:
                        current_category = None
                        for detail in kpi_details:
                            category = detail[0]
                            if category != current_category:
                                st.markdown(f"**{category}**")
                                current_category = category
                            
                            kra_name = detail[1]
                            description = detail[2]
                            weight = detail[3]
                            score = detail[4]
                            comment = detail[5]
                            
                            col_a, col_b, col_c = st.columns([3, 1, 2])
                            with col_a:
                                st.caption(f"• {kra_name}")
                                st.caption(f"  📏 {description}")
                            with col_b:
                                st.caption(f"Trọng số: {weight}")
                                st.caption(f"Điểm: {score}%")
                            with col_c:
                                if comment:
                                    st.caption(f"💬 {comment}")
                    
                    st.markdown("---")
                    
                    # Competency Details
                    st.markdown("#### 🎯 Chi tiết KPI Năng lực")
                    cursor.execute('''
                        SELECT c.category, c.name, c.description, c.importance_level,
                               ce.employee_level, ce.employee_comment
                        FROM competency_evaluations ce
                        JOIN competencies c ON ce.competency_id = c.id
                        WHERE ce.evaluation_id = ?
                        ORDER BY c.category, c.name
                    ''', (eval['id'],))
                    
                    comp_details = cursor.fetchall()
                    if comp_details:
                        current_category = None
                        for detail in comp_details:
                            category = detail[0]
                            if category != current_category:
                                st.markdown(f"**{category}**")
                                current_category = category
                            
                            name = detail[1]
                            description = detail[2]
                            importance = detail[3]
                            level = detail[4]
                            comment = detail[5]
                            
                            col_a, col_b, col_c = st.columns([3, 1, 2])
                            with col_a:
                                st.caption(f"• {name}")
                                st.caption(f"  {description}")
                            with col_b:
                                st.caption(f"Mức quan trọng: {importance}")
                                st.caption(f"Cấp độ: {level}/5")
                            with col_c:
                                if comment:
                                    st.caption(f"💬 {comment}")
                    
                    conn.close()
                    
                    st.markdown("---")
                    
                    # Comments section
                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        if eval['development_areas']:
                            st.markdown("**📈 Lĩnh vực cần phát triển:**")
                            st.info(eval['development_areas'])
                        
                        if eval['employee_comment']:
                            st.markdown("**💬 Nhận xét của nhân viên:**")
                            st.info(eval['employee_comment'])
                    
                    with col_right:
                        if eval['manager_comment']:
                            st.markdown("**👔 Nhận xét của quản lý:**")
                            st.success(eval['manager_comment'])
                        else:
                            st.markdown("**👔 Nhận xét của quản lý:**")
                            st.warning("Chưa có nhận xét từ quản lý")
                    
                    # Timestamps
                    st.caption(f"🕐 Ngày nhân viên submit: {eval['employee_submitted_at']}")
                    if eval['manager_submitted_at']:
                        st.caption(f"🕐 Ngày quản lý đánh giá: {eval['manager_submitted_at']}")
                    
                    # PDF Export Button
                    st.markdown("---")
                    
                    # Prepare data for PDF from database
                    conn_pdf = get_db_connection()
                    cursor_pdf = conn_pdf.cursor()
                    
                    # Get KPI items
                    cursor_pdf.execute('''
                        SELECT ec.kra_name, ec.weight, ed.employee_score
                        FROM evaluation_details ed
                        JOIN evaluation_criteria ec ON ed.criterion_id = ec.id
                        WHERE ed.evaluation_id = ?
                    ''', (eval['id'],))
                    
                    kpi_items = []
                    kpi_score_sum = 0
                    total_kpi_weight = 0
                    for row in cursor_pdf.fetchall():
                        kra_name, weight, score = row
                        achieved = score * weight  # score is already in %, weight is %
                        kpi_score_sum += achieved
                        total_kpi_weight += weight
                        kpi_items.append({
                            'name': kra_name,
                            'weight': weight,
                            'result': score,
                            'score': achieved
                        })
                    
                    # Calculate KPI result percentage
                    kpi_result = (kpi_score_sum / total_kpi_weight) if total_kpi_weight > 0 else 0
                    
                    # Get competency items
                    cursor_pdf.execute('''
                        SELECT c.name, c.importance_level, ce.employee_level
                        FROM competency_evaluations ce
                        JOIN competencies c ON ce.competency_id = c.id
                        WHERE ce.evaluation_id = ?
                    ''', (eval['id'],))
                    
                    comp_items = []
                    level_mapping = {1: 50, 2: 80, 3: 100, 4: 120, 5: 150}
                    comp_score_sum = 0
                    total_comp_weight = 0
                    for row in cursor_pdf.fetchall():
                        name, importance_level, level = row
                        percentage = level_mapping.get(level, 100)
                        # Score for this competency: percentage * importance_level
                        comp_score = percentage * importance_level
                        comp_score_sum += comp_score
                        total_comp_weight += importance_level * 100
                        comp_items.append({
                            'name': name,
                            'level': level,
                            'percentage': percentage,
                            'weight': importance_level,
                            'score': comp_score
                        })
                    
                    # Calculate competency result percentage
                    comp_result = (comp_score_sum / total_comp_weight * 100) if total_comp_weight > 0 else 0
                    
                    conn_pdf.close()
                    
                    # Calculate final score
                    final_score_pdf = kpi_result * 0.9 + comp_result * 0.1
                    
                    # Determine rating (same logic as in form)
                    if final_score_pdf >= 135:
                        rating = "A++"
                    elif final_score_pdf >= 120:
                        rating = "A+"
                    elif final_score_pdf >= 100:
                        rating = "A"
                    elif final_score_pdf >= 80:
                        rating = "B"
                    else:
                        rating = "C"
                    
                    pdf_data = {
                        'kpi_items': kpi_items,
                        'kpi_total': kpi_result,
                        'comp_items': comp_items,
                        'comp_total': comp_result,
                        'final_score': final_score_pdf,
                        'rating': rating,
                        'comments': eval.get('employee_comment', '')
                    }
                    
                    try:
                        pdf_buffer = generate_evaluation_pdf(st.session_state.user, pdf_data)
                        
                        st.download_button(
                            label="📄 Tải xuống Phiếu đánh giá (PDF)",
                            data=pdf_buffer,
                            file_name=f"EPR_{st.session_state.user['fullname'].replace(' ', '_')}_{eval['year']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary",
                            key=f"pdf_btn_{eval['id']}"
                        )
                    except Exception as e:
                        st.error(f"Lỗi tạo PDF: {str(e)}")

# Manager dashboard
def manager_dashboard():
    """Dashboard for managers"""
    st.title("👥 Quản lý Đánh giá")
    st.subheader(f"Chào {st.session_state.user['fullname']}")
    
    # Get all employees reporting to this manager
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE report_to = ? AND is_manager = 0",
        (st.session_state.user['fullname'],)
    )
    employees = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not employees:
        st.info("Bạn chưa có nhân viên nào báo cáo trực tiếp.")
        return
    
    st.markdown(f"### Danh sách nhân viên ({len(employees)} người)")
    
    for emp in employees:
        with st.expander(f"👤 {emp['fullname']} - {emp['code']} ({emp['department']})"):
            evaluations = get_user_evaluations(emp['id'])
            
            if not evaluations:
                st.info("Nhân viên chưa có đánh giá nào.")
                continue
            
            for eval in evaluations:
                st.markdown(f"#### Đánh giá năm {eval['year']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Điểm tự đánh giá", f"{eval['employee_score']:.2f}" if eval['employee_score'] else "N/A")
                    if eval['employee_comment']:
                        st.markdown("**Nhận xét nhân viên:**")
                        st.write(eval['employee_comment'])
                
                with col2:
                    with st.form(f"manager_review_{eval['id']}"):
                        st.markdown("**Đánh giá của bạn:**")
                        
                        manager_score = st.slider(
                            "Điểm đánh giá",
                            0, 100,
                            int(eval['manager_score']) if eval['manager_score'] else 80,
                            key=f"mgr_score_{eval['id']}"
                        )
                        
                        manager_comment = st.text_area(
                            "Nhận xét",
                            value=eval['manager_comment'] if eval['manager_comment'] else "",
                            height=150,
                            key=f"mgr_comment_{eval['id']}"
                        )
                        
                        if st.form_submit_button("💾 Lưu đánh giá quản lý"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            try:
                                cursor.execute('''
                                UPDATE evaluations 
                                SET manager_score = ?, manager_comment = ?, 
                                    manager_submitted_at = ?, status = 'manager_reviewed',
                                    final_score = ?, rating = ?
                                WHERE id = ?
                                ''', (manager_score, manager_comment, datetime.now(),
                                     (eval['employee_score'] + manager_score) / 2,
                                     'Đạt' if manager_score >= 70 else 'Chưa đạt',
                                     eval['id']))
                                conn.commit()
                                st.success("✅ Đánh giá đã được lưu!")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"Lỗi: {str(e)}")
                            finally:
                                conn.close()
                st.markdown("---")

# Admin dashboard
def admin_dashboard():
    """Dashboard for administrators"""
    st.title("🔧 Quản trị Hệ thống")
    st.subheader(f"Chào {st.session_state.user['fullname']}")
    
    tab1, tab2, tab3 = st.tabs(["📊 Tổng quan", "👥 Quản lý người dùng", "📥 Xuất báo cáo"])
    
    with tab1:
        st.markdown("### Thống kê tổng quan")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count users by role
        cursor.execute("SELECT role_type, COUNT(*) as count FROM users GROUP BY role_type")
        role_counts = cursor.fetchall()
        
        col1, col2, col3 = st.columns(3)
        for i, row in enumerate(role_counts):
            with [col1, col2, col3][i]:
                st.metric(row['role_type'].title(), row['count'])
        
        # Evaluation statistics
        cursor.execute("SELECT COUNT(*) as total FROM evaluations")
        total_evals = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as submitted FROM evaluations WHERE status != 'draft'")
        submitted_evals = cursor.fetchone()['submitted']
        
        cursor.execute("SELECT COUNT(*) as reviewed FROM evaluations WHERE status = 'manager_reviewed'")
        reviewed_evals = cursor.fetchone()['reviewed']
        
        st.markdown("### Tiến độ đánh giá")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tổng số đánh giá", total_evals)
        with col2:
            st.metric("Đã nộp", submitted_evals)
        with col3:
            st.metric("Đã duyệt", reviewed_evals)
        
        # All evaluations table
        st.markdown("### Danh sách đánh giá")
        cursor.execute('''
        SELECT u.fullname, u.code, u.department, e.year, e.status,
               e.employee_score, e.manager_score, e.final_score, e.rating
        FROM evaluations e
        JOIN users u ON e.user_id = u.id
        ORDER BY e.created_at DESC
        ''')
        evals_df = pd.DataFrame([dict(row) for row in cursor.fetchall()])
        
        if not evals_df.empty:
            st.dataframe(evals_df, use_container_width=True)
        else:
            st.info("Chưa có đánh giá nào trong hệ thống.")
        
        conn.close()
    
    with tab2:
        st.markdown("### Danh sách người dùng")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users_df = pd.DataFrame([dict(row) for row in cursor.fetchall()])
        conn.close()
        
        if not users_df.empty:
            st.dataframe(users_df[['code', 'fullname', 'username', 'department', 
                                   'role_type', 'emp_type', 'report_to']], 
                        use_container_width=True)
        
        st.markdown("### Thêm người dùng mới")
        with st.form("add_user"):
            col1, col2 = st.columns(2)
            with col1:
                new_code = st.text_input("Mã nhân viên")
                new_fullname = st.text_input("Họ tên")
                new_username = st.text_input("Tên đăng nhập")
                new_password = st.text_input("Mật khẩu", type="password")
            with col2:
                new_department = st.selectbox("Phòng ban", ['Sales', 'Office', 'Marketing', 'CS', 'IT'])
                new_role = st.selectbox("Vai trò", ['employee', 'manager', 'admin'])
                new_emp_type = st.selectbox("Loại hợp đồng", ['Full-time', 'Part-time', 'Contract'])
                new_report_to = st.text_input("Báo cáo cho (mã)")
            
            if st.form_submit_button("➕ Thêm người dùng"):
                conn = get_db_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute('''
                    INSERT INTO users (code, fullname, username, password, department, 
                                      role_type, emp_type, report_to)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (new_code, new_fullname, new_username, hash_password(new_password),
                         new_department, new_role, new_emp_type, new_report_to))
                    conn.commit()
                    st.success(f"✅ Đã thêm người dùng {new_fullname}!")
                    st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"Lỗi: {str(e)}")
                finally:
                    conn.close()
    
    with tab3:
        st.markdown("### Xuất báo cáo")
        
        report_type = st.selectbox(
            "Loại báo cáo",
            ["Tất cả đánh giá", "Theo phòng ban", "Theo trạng thái"]
        )
        
        if st.button("📥 Xuất Excel"):
            conn = get_db_connection()
            
            if report_type == "Tất cả đánh giá":
                query = '''
                SELECT u.code, u.fullname, u.department, e.year, e.period,
                       e.employee_score, e.manager_score, e.final_score, 
                       e.rating, e.status
                FROM evaluations e
                JOIN users u ON e.user_id = u.id
                ORDER BY u.department, u.code
                '''
            elif report_type == "Theo phòng ban":
                dept = st.selectbox("Chọn phòng ban", ['Sales', 'Office', 'Marketing', 'CS'])
                query = f'''
                SELECT u.code, u.fullname, u.department, e.year, e.period,
                       e.employee_score, e.manager_score, e.final_score, 
                       e.rating, e.status
                FROM evaluations e
                JOIN users u ON e.user_id = u.id
                WHERE u.department = '{dept}'
                ORDER BY u.code
                '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Create Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Evaluations', index=False)
            
            st.download_button(
                label="⬇️ Tải xuống",
                data=output.getvalue(),
                file_name=f"EPR_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("✅ File đã sẵn sàng để tải!")

# Main application logic
def main():
    """Main application"""
    if not st.session_state.logged_in:
        login_page()
    else:
        # Sidebar
        with st.sidebar:
            st.title("🏢 HFM EPR")
            st.markdown(f"**{st.session_state.user['fullname']}**")
            st.caption(f"Vai trò: {st.session_state.user['role_type'].title()}")
            st.caption(f"Phòng ban: {st.session_state.user['department']}")
            st.markdown("---")
            
            if st.button("🚪 Đăng xuất", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.rerun()
        
        # Route to appropriate dashboard
        role = st.session_state.user['role_type']
        is_manager = st.session_state.user.get('is_manager', 0)
        
        if role == 'admin':
            admin_dashboard()
        elif is_manager == 1:
            manager_dashboard()
        else:
            employee_dashboard()

if __name__ == "__main__":
    main()

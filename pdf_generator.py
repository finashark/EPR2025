# -*- coding: utf-8 -*-
"""
PDF Generator for EPR System
"""
import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Vietnamese font - Remove UTF-8 parameter as it's not valid
try:
    # Priority fonts with good Vietnamese support
    font_configs = [
        ('arial.ttf', 'arialbd.ttf', 'Arial'),
        ('times.ttf', 'timesbd.ttf', 'Times New Roman'),
        ('tahoma.ttf', 'tahomabd.ttf', 'Tahoma'),
    ]
    
    font_registered = False
    font_name = 'VietnameseFont'
    font_name_bold = 'VietnameseFontBold'
    
    for regular, bold, name in font_configs:
        regular_path = os.path.join(r"C:\Windows\Fonts", regular)
        bold_path = os.path.join(r"C:\Windows\Fonts", bold)
        
        if os.path.exists(regular_path):
            try:
                # Register fonts WITHOUT encoding parameter (reportlab handles it internally)
                pdfmetrics.registerFont(TTFont(font_name, regular_path))
                
                # Try to register bold font, if not available use regular
                if os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont(font_name_bold, bold_path))
                else:
                    pdfmetrics.registerFont(TTFont(font_name_bold, regular_path))
                
                font_registered = True
                print(f"✓ Registered Vietnamese font: {name}")
                break
            except Exception as e:
                print(f"Failed to register {name}: {e}")
                continue
    
    if not font_registered:
        # Fallback to default font if no suitable font found
        print("⚠ Warning: No Vietnamese font found, using default Helvetica")
        font_name = 'Helvetica'
        font_name_bold = 'Helvetica-Bold'
except Exception as e:
    print(f"Font registration error: {e}")
    font_registered = False
    font_name = 'Helvetica'
    font_name_bold = 'Helvetica-Bold'

def generate_evaluation_pdf(user_info, evaluation_data):
    """Generate PDF report for evaluation"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, 
                           topMargin=20*mm, bottomMargin=20*mm)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Use Vietnamese font if available
    base_font = font_name
    base_font_bold = font_name_bold
    
    # Custom styles with encoding support
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=base_font_bold,
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        alignment=1,  # Center
        wordWrap='CJK'  # Support for Unicode characters
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=base_font_bold,
        fontSize=12,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=8,
        wordWrap='CJK'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=base_font,
        fontSize=9,
        wordWrap='CJK'
    )
    
    # Title - ensure text is unicode
    title_text = "PHIẾU ĐÁNH GIÁ HIỆU QUẢ CÔNG VIỆC 2025"
    elements.append(Paragraph(title_text, title_style))
    elements.append(Spacer(1, 12))
    
    # Employee Info Table
    info_data = [
        ['Họ và tên:', user_info['fullname'], 'Mã NV:', user_info.get('code', 'N/A')],
        ['Phòng ban:', user_info['department'], 'Vai trò:', user_info['role_type']],
        ['Quản lý trực tiếp:', user_info.get('report_to', 'N/A'), 'Ngày đánh giá:', 
         datetime.now().strftime('%d/%m/%Y')]
    ]
    
    info_table = Table(info_data, colWidths=[35*mm, 60*mm, 30*mm, 45*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), base_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), base_font_bold),
        ('FONTNAME', (2, 0), (2, -1), base_font_bold),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0f0f0')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 12))
    
    # KPI Results
    elements.append(Paragraph("I. KẾT QUẢ ĐÁNH GIÁ THÀNH TÍCH (KPI)", heading_style))
    
    kpi_data = [['STT', 'Tiêu chí', 'Trọng số', 'Kết quả (%)', 'Điểm đạt', 'Minh chứng/Ví dụ']]
    
    for i, item in enumerate(evaluation_data.get('kpi_items', []), 1):
        evidence_text = item.get('evidence', '') or 'Chưa nhập'
        kpi_data.append([
            str(i),
            Paragraph(item['name'], normal_style),
            f"{item['weight']:.0f}",
            f"{item['result']:.1f}%",
            f"{item['score']:.2f}",
            Paragraph(evidence_text, normal_style)
        ])
    
    kpi_data.append(['', 'TỔNG KPI THÀNH TÍCH', '', '', 
                     f"{evaluation_data.get('kpi_total', 0):.2f}%", ''])
    
    kpi_table = Table(kpi_data, colWidths=[10*mm, 50*mm, 15*mm, 18*mm, 18*mm, 64*mm])
    kpi_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), base_font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, -1), (-1, -1), base_font_bold),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d9e2f3')),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 12))
    
    # Competency Results
    elements.append(Paragraph("II. KẾT QUẢ ĐÁNH GIÁ NĂNG LỰC", heading_style))
    
    comp_data = [['STT', 'Năng lực', 'Mức độ', 'Điểm (%)', 'Trọng số', 'Điểm đạt', 'Minh chứng/Ví dụ']]
    
    for i, item in enumerate(evaluation_data.get('comp_items', []), 1):
        evidence_text = item.get('evidence', '') or 'Chưa nhập'
        comp_data.append([
            str(i),
            Paragraph(item['name'], normal_style),
            str(item['level']),
            f"{item['percentage']:.0f}%",
            str(item['weight']),
            f"{item['score']:.2f}",
            Paragraph(evidence_text, normal_style)
        ])
    
    comp_data.append(['', 'TỔNG KPI NĂNG LỰC', '', '', '', 
                      f"{evaluation_data.get('comp_total', 0):.2f}%", ''])
    
    comp_table = Table(comp_data, colWidths=[10*mm, 40*mm, 15*mm, 16*mm, 16*mm, 18*mm, 60*mm])
    comp_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), base_font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, -1), (-1, -1), base_font_bold),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d9e2f3')),
    ]))
    elements.append(comp_table)
    elements.append(Spacer(1, 12))
    
    # Final Score
    elements.append(Paragraph("III. TỔNG KẾT", heading_style))
    
    final_data = [
        ['KPI Thành tích (90%)', f"{evaluation_data.get('kpi_total', 0):.2f}%"],
        ['KPI Năng lực (10%)', f"{evaluation_data.get('comp_total', 0):.2f}%"],
        ['ĐIỂM TỔNG', f"{evaluation_data.get('final_score', 0):.2f}%"],
        ['XẾP LOẠI', evaluation_data.get('rating', 'N/A')]
    ]
    
    final_table = Table(final_data, colWidths=[100*mm, 70*mm])
    final_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), base_font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1f4788')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('BACKGROUND', (0, 2), (-1, -1), colors.HexColor('#d9e2f3')),
        ('TEXTCOLOR', (0, 2), (-1, -1), colors.HexColor('#1f4788')),
    ]))
    elements.append(final_table)
    elements.append(Spacer(1, 12))
    
    # Comments
    if evaluation_data.get('comments'):
        elements.append(Paragraph("IV. NHẬN XÉT VÀ ĐỊNH HƯỚNG PHÁT TRIỂN", heading_style))
        elements.append(Paragraph(evaluation_data['comments'], normal_style))
    
    # Signature area
    elements.append(Spacer(1, 20))
    sig_data = [
        ['Nhân viên', 'Quản lý trực tiếp', 'Giám đốc'],
        ['', '', ''],
        ['', '', ''],
        [f"Ngày: {datetime.now().strftime('%d/%m/%Y')}", '', '']
    ]
    
    sig_table = Table(sig_data, colWidths=[60*mm, 55*mm, 55*mm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), base_font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(sig_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
from .models import ScanReport

def generate_pdf_report(report: ScanReport) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = styles['Heading1']
    normal_style = styles['Normal']
    
    story = []
    
    story.append(Paragraph("APIShield Security Scan Report", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Scan ID: {report.scan_id}", normal_style))
    story.append(Paragraph(f"Target: {report.target_url}", normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"Total Vulnerabilities Found: {len(report.findings)}", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    for f in report.findings:
        story.append(Paragraph(f"{f.test_name} ({f.severity})", styles['Heading3']))
        story.append(Paragraph(f"Endpoint: {f.method} {f.endpoint}", normal_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph("Remediation:", styles['Heading4']))
        story.append(Paragraph(f.remediation, normal_style))
        story.append(Spacer(1, 12))
        
    doc.build(story)
    return buffer.getvalue()

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_canopy_hazard_packet(filename="canopy_hazard_packet.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    primary = colors.HexColor("#1A202C")
    accent = colors.HexColor("#D69E2E")
    text = colors.HexColor("#2D3748")
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=primary, spaceAfter=6)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=primary, spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=text)

    story = []
    story.append(Paragraph("CANOPY CONTROL CENTER — OFFICIAL HAZARD ASSESSMENT PACKET", title_style))
    story.append(Paragraph("<b>Strict Liability & Margin-of-Error Waiver:</b> Field hazard classifications (Danger Codes SHI-01 to SHI-04) and storm flags (WS-F, WM-F, EGS-F, RTR-F, COR-F) represent structural risk observations.", body_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent, spaceAfter=10, spaceBefore=6))

    story.append(Paragraph("1. Property Assignment & Authorized D2 Contractor Credentials", h2_style))
    assignment_data = [
        [Paragraph("<b>Target Property:</b>", body_style), Paragraph("1240 Stoner Road, Blanca, CO (Parcel 70226200)", body_style)],
        [Paragraph("<b>Assigned D2 Operator:</b>", body_style), Paragraph("Johnny Bailey (Apex Timberline Forestry & Structures)", body_style)],
        [Paragraph("<b>Contractor Experience:</b>", body_style), Paragraph("14 Years Professional Timber & Structural Operations in Southern Colorado", body_style)],
        [Paragraph("<b>Insurance Standing:</b>", body_style), Paragraph("Fully Bonded & Insured ($2,000,000 General Liability + Inland Marine)", body_style)]
    ]
    t_assign = Table(assignment_data, colWidths=[140, 394])
    t_assign.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EDF2F7")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#A0AEC0")),
        ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_assign)
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. Official Correspondence from D2 Contractor", h2_style))
    letter_text = (
        "Dear Property Owner,<br/><br/>"
        "Apex Timberline has been formally assigned by Canopy Control Center to evaluate structural timber hazards and severe storm vulnerabilities on your parcel. "
        "Our team specializes in mitigating high-density wind-sail canopies (WS-F) and root-anchor destabilization (RTR-F) prior to winter weather events."
    )
    story.append(Paragraph(letter_text, body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. Authorization & Field Verification", h2_style))
    sig_text = "<b>D2 Contractor Signature:</b> ___________________________ &nbsp;&nbsp;&nbsp; <b>Date:</b> ______________"
    story.append(Paragraph(sig_text, body_style))

    doc.build(story)
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_canopy_hazard_packet()
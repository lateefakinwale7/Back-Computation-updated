import ezdxf
import io
from fpdf import FPDF
from datetime import datetime

def export_to_dxf(df):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    doc.layers.add(name="SURVEY_STATIONS", color=2)
    doc.layers.add(name="TRAVERSE_LINES", color=1)
    
    points = list(zip(df['Final_E'], df['Final_N']))
    if len(points) > 1:
        msp.add_lwpolyline(points, dxfattribs={'layer': 'TRAVERSE_LINES'})
    
    for i, (x, y) in enumerate(points):
        msp.add_point((x, y), dxfattribs={'layer': 'SURVEY_STATIONS'})
        msp.add_text(str(df.iloc[i]['code']), dxfattribs={'height': 0.5}).set_placement((x+0.2, y+0.2))
    
    out = io.StringIO()
    doc.write(out)
    return out.getvalue().encode('utf-8')

def export_pdf(df, mis_n, mis_e, prec, project, surveyor, notes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"SURVEY REPORT: {project}", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Surveyor: {surveyor} | Precision: 1:{int(prec)}", ln=True)
    pdf.ln(5)
    
    # Simple Table
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(30, 8, "Code", 1)
    pdf.cell(40, 8, "Easting", 1)
    pdf.cell(40, 8, "Northing", 1)
    pdf.ln()
    
    pdf.set_font("Arial", '', 9)
    for _, row in df.iterrows():
        pdf.cell(30, 7, str(row['code']), 1)
        pdf.cell(40, 7, f"{row['Final_E']:.3f}", 1)
        pdf.cell(40, 7, f"{row['Final_N']:.3f}", 1)
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin-1')

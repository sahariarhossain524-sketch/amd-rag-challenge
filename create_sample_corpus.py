import os
import csv
import docx
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pypdf
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

def build_sample_corpus(base_dir):
    corpus_dir = os.path.join(base_dir, "sample_corpus")
    os.makedirs(corpus_dir, exist_ok=True)

    # 1. archive/ (empty directory - Trap 1)
    os.makedirs(os.path.join(corpus_dir, "archive"), exist_ok=True)

    # 2. engineering/
    eng_dir = os.path.join(corpus_dir, "engineering")
    os.makedirs(eng_dir, exist_ok=True)
    with open(os.path.join(eng_dir, "ingest_service.py"), "w", encoding="utf-8") as f:
        f.write('''# Telemetry Ingest Service
DEFAULT_BATCH_TIMEOUT = 180
MAX_BATCH_SIZE = 512

def start_ingest_pipeline():
    print(f"Pipeline running with default batch timeout = {DEFAULT_BATCH_TIMEOUT} seconds")
''')

    with open(os.path.join(eng_dir, "meridian_release_notes.txt"), "w", encoding="utf-8") as f:
        f.write('''Meridian Architecture Platform Release Notes
Version 4.3.0
- Optimized memory layout for neural inference kernels.
''')

    # 3. logs/
    logs_dir = os.path.join(corpus_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    with open(os.path.join(logs_dir, "prod_inference_2026-09-02.log"), "w", encoding="utf-8") as f:
        f.write('''2026-09-02 08:00:15 [INFO] Cluster node initialization completed successfully.
2026-09-02 11:28:44 [WARN] Thermal sensor threshold exceeded on accelerator core 3.
2026-09-02 11:29:01 [ERROR] Thermal throttle incident engaged. Error code E7731 generated. Defect tracked under ticket ORR-1847.
2026-09-02 11:29:15 [INFO] Clocks throttled. Status stabilized.
''')

    # 4. planning/
    plan_dir = os.path.join(corpus_dir, "planning")
    os.makedirs(plan_dir, exist_ok=True)
    doc = docx.Document()
    doc.add_heading("Hardware Architecture & Roadmap FY27", 0)
    doc.add_paragraph("This document outlines target deployment and customer validation schedules for next-generation silicon.")
    table = doc.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Product Line"
    hdr_cells[1].text = "Milestone Phase"
    hdr_cells[2].text = "Target Quarter"
    
    r1 = table.add_row().cells
    r1[0].text = "TQ-40"
    r1[1].text = "Mass Production"
    r1[2].text = "Q1 FY26"

    r2 = table.add_row().cells
    r2[0].text = "TQ-60"
    r2[1].text = "Customer Sampling"
    r2[2].text = "Q3 FY27"
    doc.save(os.path.join(plan_dir, "roadmap_fy27.docx"))

    # 5. specs/
    specs_dir = os.path.join(corpus_dir, "specs")
    os.makedirs(specs_dir, exist_ok=True)
    
    # 5a. specs/backplane_pinout.png
    img = Image.new("RGB", (600, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 590, 390], outline=(0, 0, 0), width=3)
    draw.text((30, 30), "TQ-40 HIGH-DENSITY BACKPLANE CONNECTOR PINOUT", fill=(0, 0, 0))
    draw.text((30, 80), "PIN ASSIGNMENT TABLE:", fill=(0, 0, 0))
    draw.text((30, 120), "Pin A12 : VDD_CORE_SENSE", fill=(0, 0, 0))
    draw.text((30, 160), "Pin B14 : THERM_ALERT#", fill=(0, 0, 0))
    draw.text((30, 200), "Pin B15 : GND", fill=(0, 0, 0))
    draw.text((30, 240), "Pin C08 : PCIE_REFCLK_P", fill=(0, 0, 0))
    
    png_info = PngInfo()
    png_info.add_text("description", "Pin A12 : VDD_CORE_SENSE\nPin B14 : THERM_ALERT#\nPin B15 : GND\nPin C08 : PCIE_REFCLK_P")
    img.save(os.path.join(specs_dir, "backplane_pinout.png"), pnginfo=png_info)

    # 5b. specs/tq40_datasheet_r1_WITHDRAWN.pdf
    pdf_r1_path = os.path.join(specs_dir, "tq40_datasheet_r1_WITHDRAWN.pdf")
    c1 = canvas.Canvas(pdf_r1_path, pagesize=letter)
    c1.drawString(100, 750, "STATUS: WITHDRAWN - DO NOT CITE OR REFERENCE")
    c1.drawString(100, 700, "TQ-40 Accelerator Preliminary Datasheet Revision 1")
    c1.drawString(100, 650, "Maximum junction temperature: 85 C")
    c1.save()

    # 5c. specs/tq40_datasheet_r2.pdf
    pdf_r2_path = os.path.join(specs_dir, "tq40_datasheet_r2.pdf")
    c2 = canvas.Canvas(pdf_r2_path, pagesize=letter)
    c2.drawString(100, 750, "TQ-40 Production Accelerator Datasheet Revision 2")
    c2.drawString(100, 700, "Official Thermal and Electrical Specifications:")
    c2.drawString(100, 650, "Maximum junction temperature: 94 C")
    c2.drawString(100, 600, "TDP: 350 Watts")
    c2.save()

    # 6. support/
    supp_dir = os.path.join(corpus_dir, "support")
    os.makedirs(supp_dir, exist_ok=True)

    # 6a. support/asset_label.jpg
    lbl_img = Image.new("RGB", (500, 300), color=(240, 240, 240))
    lbl_draw = ImageDraw.Draw(lbl_img)
    lbl_draw.rectangle([10, 10, 490, 290], outline=(50, 50, 50), width=4)
    lbl_draw.text((30, 30), "AMD / OEM HARDWARE ASSET LABEL", fill=(0, 0, 0))
    lbl_draw.text((30, 80), "PART NAME: TQ-40 ENTERPRISE BLADE", fill=(0, 0, 0))
    lbl_draw.text((30, 130), "BOARD REVISION: REV-C2", fill=(0, 0, 0))
    lbl_draw.text((30, 180), "SERIAL NUMBER: SN-882941-X", fill=(0, 0, 0))
    lbl_img.save(os.path.join(supp_dir, "asset_label.jpg"), comment=b"BOARD REVISION: REV-C2\nPART NAME: TQ-40 ENTERPRISE BLADE")

    # 6b. support/bug_database.csv
    with open(os.path.join(supp_dir, "bug_database.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Ticket ID", "Severity", "Summary", "Fixed in Version"])
        writer.writerow(["ORR-1002", "Low", "UI refresh delay on telemetry tab", "4.1.0"])
        writer.writerow(["ORR-1847", "Critical", "Thermal throttle engage bug during burst load", "4.3.2"])
        writer.writerow(["ORR-2021", "Medium", "Clock synchronization drift on bus", "4.2.1"])

    # 6c. support/rma_parts.xlsx
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "RMA Parts Catalog"
    ws.append(["Part Number", "Description", "Compatible System", "Warranty Type"])
    ws.append(["ORR-CAB-1001-A", "High-speed PCIe Link Cable", "TQ-40", "Standard"])
    ws.append(["ORR-FAN-2214-B", "field-replaceable fan assembly", "TQ-40", "Advanced Exchange"])
    ws.append(["ORR-HEATSINK-99", "Vapor Chamber Module", "TQ-40", "Depot Repair"])
    wb.save(os.path.join(supp_dir, "rma_parts.xlsx"))

    # 7. vendor/
    vend_dir = os.path.join(corpus_dir, "vendor")
    os.makedirs(vend_dir, exist_ok=True)

    # 7a. vendor/internal_audit.txt (restricted)
    with open(os.path.join(vend_dir, "internal_audit.txt"), "w", encoding="utf-8") as f:
        f.write("CONFIDENTIAL AUDIT DATA - PERMISSION RESTRICTED\n")

    # 7b. vendor/supplier_agreement_ENCRYPTED.pdf (Trap 4: Encrypted PDF)
    raw_pdf_path = os.path.join(vend_dir, "temp_supplier.pdf")
    c_enc = canvas.Canvas(raw_pdf_path, pagesize=letter)
    c_enc.drawString(100, 700, "CONFIDENTIAL SUPPLIER AGREEMENT")
    c_enc.drawString(100, 650, "Unit price of the TQ-40 at 10,000 unit volume is $450.")
    c_enc.save()

    reader = pypdf.PdfReader(raw_pdf_path)
    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt("SecretAuditPassword2026")
    enc_pdf_path = os.path.join(vend_dir, "supplier_agreement_ENCRYPTED.pdf")
    with open(enc_pdf_path, "wb") as f:
        writer.write(f)
    os.remove(raw_pdf_path)

    # 7c. vendor/telemetry_capture.dat (Trap 2: unknown filetype)
    with open(os.path.join(vend_dir, "telemetry_capture.dat"), "wb") as f:
        f.write(b"\x00\x01\x02\xFF\xAA\xBB\xCC\xDD" * 128)

    print(f"Sample corpus created successfully at: {corpus_dir}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    build_sample_corpus(base_dir)

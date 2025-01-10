import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, Destination, AnnotationBuilder
from io import BytesIO
import fitz  
import pdfplumber


def find_index_page(pdf_file_path):

    with pdfplumber.open(pdf_file_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Tổng số trang của PDF: {total_pages}")
        
        last_valid_index_page = None
        found_first_index_page = False 

        for i in range(total_pages - 1, -1, -1):
            page = pdf.pages[i]
            
            text = page.extract_text()
            first_line = text.split("\n")[0].strip() if text else "" 
            
            if "index" in first_line.lower():
                last_valid_index_page = i  
                found_first_index_page = True 
            elif found_first_index_page:
                break

        if last_valid_index_page is not None:
            print(f"Trang Index được xác định: {last_valid_index_page + 1}")
            return last_valid_index_page + 1, total_pages
        else:
            print("Không tìm thấy trang Index.")
            return 0


def find_first_page(pdf_path, start_page=0, end_page=None, header_height=100, footer_height=100):
    try:
        pdf_document = fitz.open(pdf_path)

        if end_page is None or end_page > len(pdf_document):
            end_page = len(pdf_document)

        headers_footers = []

        for page_num in range(start_page, end_page):
            page = pdf_document[page_num]
            page_height = page.rect.height

            header_rect = fitz.Rect(0, 0, page.rect.width, header_height)
            footer_rect = fitz.Rect(0, page_height - footer_height, page.rect.width, page_height)

            header_text = page.get_text("text", clip=header_rect)
            footer_text = page.get_text("text", clip=footer_rect)
            headers_footers.append({
                "page": page_num,
                "header": header_text.strip(),
                "footer": footer_text.strip()
            })

        def extract_numbers(text):
            return list(map(int, re.findall(r'\b\d+\b', text)))

        for i in range(len(headers_footers) - 2):
            page1 = headers_footers[i]
            page2 = headers_footers[i + 1]
            page3 = headers_footers[i + 2]

            page1_numbers = extract_numbers(page1['header'] + " " + page1['footer'])
            page2_numbers = extract_numbers(page2['header'] + " " + page2['footer'])
            page3_numbers = extract_numbers(page3['header'] + " " + page3['footer'])

            if page1_numbers and page2_numbers and page3_numbers:
                if (page2_numbers[0] == page1_numbers[0] + 1 and
                        page3_numbers[0] == page2_numbers[0] + 1):
                    n = page1_numbers[0]  
                    k = page1["page"] - n  
                    return k

        return None  

    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        return None

def add_link_index(pdf_file_path, start_page, output_pdf, k):
    doc = fitz.open(pdf_file_path) 

    total_pages = len(doc)
    if start_page < 1 or start_page > total_pages:
        print("Trang bắt đầu không hợp lệ.")
        return

    for i in range(start_page - 1, total_pages):
        page = doc[i]  
        blocks = page.get_text("dict")["blocks"]  
        if not blocks:
            continue  

        for block in blocks:
            for line in block.get("lines", []):  
                for span in line.get("spans", []):  
                    
                    text = span["text"].replace(",", "")
                    
                    matches = re.findall(r'\b(\d+(?:-\d+)?)\b', text)  
                    for match in matches:
                        try:
                            if '-' in match:  
                                target_page = int(match.split('-')[0])  
                            else:
                                target_page = int(match)  

                            if target_page < 1 or target_page > total_pages or target_page >= start_page-(k+1):
                                print(f"Target page {target_page} không hợp lệ. Bỏ qua.")
                                continue
                            
                            match_start = text.find(match)  
                            match_width = (span["bbox"][2] - span["bbox"][0]) / len(text) * len(match)
                            
                            x0 = span["bbox"][0] + match_start * (span["bbox"][2] - span["bbox"][0]) / len(text)
                            x1 = x0 + match_width
                            y0, y1 = span["bbox"][3], span["bbox"][3] + 1

                            link_rect = fitz.Rect(x0, span["bbox"][1], x1, span["bbox"][3])
                            page.insert_link(
                                {
                                    "kind": fitz.LINK_GOTO, 
                                    "from": link_rect,  
                                    "page": target_page + k, 
                                }
                            )

                            underline_rect = fitz.Rect(x0, y0, x1, y1)
                            page.draw_rect(underline_rect, color=(0, 0, 1), width=0.3)
                        except ValueError:
                            print(f"Không thể chuyển đổi '{match}' thành số. Bỏ qua.")
                            continue  
                    
    doc.save(output_pdf)
    print(f"Đã lưu file PDF với liên kết: {output_pdf}")     


if __name__ == "__main__":
    
    pdf_file = "file_pdf/Strategic thinking - Pearson, Gordon J 1939- 1990 - New York - Prentice Hall.pdf"
    output_pdf = "file_pdf/output_Strategic thinking - Pearson, Gordon J 1939- 1990 - New York - Prentice Hall.pdf"

    index_page, total_page = find_index_page(pdf_file)
    k = find_first_page(pdf_file)
    add_link_index(pdf_file, index_page, output_pdf, k)
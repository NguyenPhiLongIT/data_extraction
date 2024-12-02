import pdfplumber
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, Destination
from io import BytesIO

def parse_pages(pages_raw):
    """Phân tích danh sách số trang (hỗ trợ dải số và chỉ lấy số đầu nếu có)."""
    pages = pages_raw.replace(" ", "").split(",")
    expanded_pages = []

    for p in pages:
        if "-" in p:
            try:
                if len(p.split("-")) == 2 and len(p.split("-")[1]) == 1:
                    p = p.split("-")[0]  # Lấy số đầu tiên

                start, end = map(int, p.split("-"))
                
                if end < start:
                    expanded_pages.append(start)
                else:
                    expanded_pages.extend(range(start, end + 1))
            except ValueError:
                print(f"Không thể phân tích dải số: {p}")
        elif re.match(r'^\d+$', p):
            try:
                expanded_pages.append(int(p))
            except ValueError:
                print(f"Không thể chuyển đổi số trang: {p}")
        else:
            print(f"Không thể nhận dạng số trang: {p}")

    return expanded_pages

def extract_index_from_line(line):
    results = []
    current_keyword = None
    current_pages = []

    pattern = r"(.*?)(\d[\d,\-\s]*)"
    matches = re.findall(pattern, line)

    for match in matches:
        keyword_part, pages_part = match
        keyword_part = keyword_part.strip()
        pages_part = pages_part.strip()

        if current_keyword:
            results.append((current_keyword, current_pages))
        
        current_keyword = keyword_part.rstrip(",")
        current_pages = parse_pages(pages_part)

    if current_keyword:
        results.append((current_keyword, current_pages))

    return results

def extract_index_and_keywords(pdf_file_path):
    with pdfplumber.open(pdf_file_path) as pdf:
        index_page = None
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()

            first_word = text.split("\n")[0].strip() if text else ""
            if first_word.lower() == "index":
                index_page = i # Trang bắt đầu từ 1
                print(f"Trang Index được tìm thấy: {index_page}")

        if index_page is None:
            print("Không tìm thấy trang Index.")
            return []

        all_keywords = []
        for i in range(index_page, len(pdf.pages)):
            index_text = pdf.pages[i].extract_text()

            if not index_text.strip():
                print(f"Trang trống tại trang {i + 1}, dừng trích xuất.")
                break

            lines = index_text.split("\n")
            for line in lines:
                keywords = extract_index_from_line(line)
                if keywords:
                    all_keywords.extend(keywords)

        return all_keywords


def create_index_page(keywords):
    """Tạo trang Index mới chứa danh sách từ khóa và số trang với liên kết."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y_position = height - 40  # Bắt đầu từ vị trí cách mép trên một chút
    c.setFont("Helvetica", 10)

    for keyword, pages in keywords:
        keyword_text = f"{keyword}: "
        c.drawString(40, y_position, keyword_text)

        # Lưu lại thông tin vị trí để tạo liên kết trong PDF
        for i, page in enumerate(pages):
            link_text = str(page)
            # Tạo liên kết đến các trang
            c.drawString(40 + len(keyword_text)*5 + i*30, y_position, link_text)

        y_position -= 14
        if y_position < 40:
            c.showPage()  # Chuyển sang trang mới nếu hết trang
            c.setFont("Helvetica", 10)
            y_position = height - 40

    c.save()
    buffer.seek(0)
    return buffer

def add_index_to_pdf(pdf_file_path, output_pdf_path):
    keywords = extract_index_and_keywords(pdf_file_path)

    # Tạo trang Index mới
    index_pdf = create_index_page(keywords)

    # Đọc PDF gốc và trang Index
    with open(pdf_file_path, "rb") as original_pdf:
        reader = PdfReader(original_pdf)
        writer = PdfWriter()

        # Thêm tất cả các trang gốc vào writer
        for i in range(len(reader.pages)):
            writer.add_page(reader.pages[i])

        # Thêm trang Index vào cuối tài liệu
        index_reader = PdfReader(index_pdf)
        index_page = index_reader.pages[0]
        writer.add_page(index_page)

        # Thêm các bookmark vào các từ khóa
        for keyword, pages in keywords:
            for page_number in pages:
                # Điều chỉnh số trang với trang Index mới
                adjusted_page_number = len(reader.pages)  # Trang Index nằm ở cuối
                dest = Destination(NameObject(f"{keyword} (Trang {adjusted_page_number})"), adjusted_page_number, fit="Fit")
                # Sử dụng add_outline_item thay cho add_bookmark
                writer.add_outline_item(title=f"{keyword} (Trang {adjusted_page_number})", destination=dest)

        # Lưu file PDF mới
        with open(output_pdf_path, "wb") as output_pdf:
            writer.write(output_pdf)

    print(f"File PDF mới đã được tạo tại {output_pdf_path}")

if __name__ == "__main__":
    pdf_file = "file/Ebook - IT test/Strategic thinking - Pearson, Gordon J 1939- 1990 - New York - Prentice Hall.pdf"
    output_file = "generated_with_links.pdf"
    add_index_to_pdf(pdf_file, output_file)


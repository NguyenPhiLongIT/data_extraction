import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, Destination
from io import BytesIO
import fitz  
import pdfplumber


def parse_pages(pages_raw, total_pages):
    pages = pages_raw.replace(" ", "").split(",")
    expanded_pages = []

    for p in pages:
        if "-" in p:
            try:
                if len(p.split("-")) == 2:
                    p = p.split("-")[0]  # Lấy số đầu tiên

                start, end = map(int, p.split("-"))

                if end < start:
                    if 0 < start < int(total_pages):
                        expanded_pages.append(start)
                else:
                    if 0 < end < int(total_pages):
                        expanded_pages.extend(range(start, end + 1))
            except ValueError:
                print(f"Không thể phân tích dải số: {p}")
        elif p.isdigit():
            try:
                if 0 < int(p) < int(total_pages):
                    expanded_pages.append(int(p))
            except ValueError:
                print(f"Không thể chuyển đổi số trang: {p}")
        else:
            print(f"Không thể nhận dạng số trang: {p}")

    return expanded_pages


def extract_index_from_line(line, total_pages):
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
        current_pages = parse_pages(pages_part, total_pages)

    if current_keyword:
        results.append([current_keyword, current_pages])

    return results


def extract_index_and_keywords(pdf_file_path):
    with pdfplumber.open(pdf_file_path) as pdf:
        index_page = None
        total_pages = len(pdf.pages)
        print(f"Tổng số trang của PDF: {total_pages}")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()

            first_word = text.split("\n")[0].strip() if text else ""
            if first_word.lower() == "index":
                index_page = i
                print(f"Trang Index được tìm thấy: {index_page}")

        if index_page is None:
            print("Không tìm thấy trang Index.")
            return {}

        keywords_dict = {}
        for i in range(index_page, len(pdf.pages)):
            index_text = pdf.pages[i].extract_text()
            if index_text.strip():
                print("i:",i)
            if i >252:
                print("i:",i, "\n",index_text)
            if not index_text.strip():
                print(f"Trang trống tại trang {i + 1}, dừng trích xuất.")
                return keywords_dict

            lines = index_text.split("\n")
            for line in lines:
                keywords = extract_index_from_line(line, total_pages)
                for keyword, pages in keywords:
                    if isinstance(keyword, str):
                        if len(pages) > 0:
                            keywords_dict[keyword] = pages
                # if len(keywords) <2:
                #     del keywords_dict[keywords[0]]

        for keyword in keywords_dict:
            keywords_dict[keyword] = sorted(set(keywords_dict[keyword]))

        return keywords_dict



def create_index_page_with_links(input_pdf, index_data, output_pdf):
    doc = fitz.open(input_pdf)

    index_page = doc.new_page()  
    index_page.insert_text(
        (100, 50), "Index", fontsize=16, fontname="helv"
    ) 

    left_column_x = 100
    right_column_x = 350
    y_position = 100  

    for word, target_pages in index_data.items():
        index_page.insert_text((left_column_x, y_position), f"{word}: ", fontsize=12)

        for target_page in target_pages:
            rect = fitz.Rect(
                right_column_x, y_position, right_column_x + 20, y_position + 20
            )
            index_page.insert_text(
                (right_column_x, y_position), f"{target_page}", fontsize=12
            )

            index_page.insert_link(
                {
                    "kind": fitz.LINK_GOTO,
                    "from": rect,
                    "page": 17 + int(
                        target_page
                    ),  
                }
            )

            y_position += 25 

        y_position += 20 
        
        if y_position > 700:  
            index_page = doc.new_page()  
            index_page.insert_text(
                (100, 50), "Index", fontsize=16, fontname="helv"
            )  
            y_position = 100  

    doc.save(output_pdf)


if __name__ == "__main__":
    pdf_file = "file/Ebook - IT test/Strategic thinking - Pearson, Gordon J 1939- 1990 - New York - Prentice Hall.pdf"
    output_file = "generated_with_links.pdf"
    index_data = extract_index_and_keywords(pdf_file)
    print("index_data", index_data)
    #     add_index_to_pdf(pdf_file, output_file)
    create_index_page_with_links(pdf_file, index_data, output_file)
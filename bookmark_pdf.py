import fitz  # PyMuPDF
import re
from PyPDF2 import PdfReader, PdfWriter
import math
import os
import google.generativeai as genai
from index_pdf import find_first_page

genai.configure(api_key='AIzaSyA2U8-Ad6hzJK0jwqOP2U7M4E4i0UgNGxI')

def split_pdf(input_pdf, output_pdf="output_part.pdf", max_pages_per_part=25):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for i in range(min(len(reader.pages), max_pages_per_part)):
        writer.add_page(reader.pages[i])

    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

    return output_pdf

def extract_pages_with_content(pdf_path, output_path="output_part.pdf", header_height=250, footer_height=250, start_page=1):
    """
    Lọc và trích xuất các trang PDF từ lúc gặp chữ "contents" cho đến khi gặp chữ có kích thước giống với kích thước của chữ "contents".
    Duyệt qua toàn bộ nội dung của header các trang, không bỏ qua phần nào.
    
    Args:
        pdf_path (str): Đường dẫn đến file PDF gốc.
        output_path (str): Đường dẫn lưu file PDF đầu ra.
        header_height (int): Chiều cao của header tính từ trên xuống.
        footer_height (int): Chiều cao của footer tính từ dưới lên.
        start_page (int): Trang bắt đầu kiểm tra.
        
    Returns:
        list: Danh sách các trang được chọn.
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc) 
    content_font_size = None  
    selected_pages = []  
    writer = fitz.open()  
    found_content_page = False  

    for i in range(start_page - 1, total_pages):
        page = doc[i]  
        blocks = page.get_text("dict")["blocks"]  
        if not blocks:
            continue  

        found_in_header = False  
        for block in blocks:
            for line in block.get("lines", []):  
                for span in line.get("spans", []):  
                    if span["bbox"][1] < header_height: 
                        if not found_content_page:
                            if span["text"].strip().lower() == "contents":
                                content_font_size = span["size"]  
                                found_content_page = True  
                                continue
                        if found_content_page and span["size"] > content_font_size and span["text"] != " ":
                            found_in_header = True
                            break
                if found_in_header:
                    break
            if found_in_header:
                break

        if found_in_header:
            print(f"Trang {i + 1}: Dừng lại vì có chữ trong header có kích thước giống 'contents'")
            break

        if found_content_page:
            selected_pages.append(i + 1)
            writer.insert_pdf(doc, from_page=i, to_page=i)

    writer.save(output_path)
    writer.close()
    doc.close()

    return output_path

def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()

def save_text_to_txt(text, output_txt_path="table_contents.txt"):
    try:
        with open(output_txt_path, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"Table of Contents đã được lưu vào {output_txt_path}")
    except Exception as e:
        print(f"Đã có lỗi xảy ra: {e}")


def extract_table_contents(pdf_path):
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,  
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",  
        generation_config=generation_config,
    )

    # Upload file PDF lên Google AI Studio
    files = [upload_to_gemini(pdf_path, mime_type="application/pdf")]

    # Đợi file xử lý xong
    wait_for_files_active(files)

    # Bắt đầu phiên chat với Google AI Studio
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    files[0],
                ],
            },
        ]
    )

    try:
        response = chat_session.send_message("Extract all titles and page numbers from the 'Table of Contents' page. Titles are on the left and page numbers are on the right. Give output as a list of Python tuples: [(title, page_number)]")
        save_text_to_txt(response.text)
    except StopCandidateException as e:
        print(f"Error: {e}")

def is_roman_numeral(s):
    """
    Kiểm tra nếu giá trị là số La Mã.
    """
    if not isinstance(s, str):
        return False  
    
    roman_pattern = r"^(?=[MDCLXVI])M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
    return bool(re.match(roman_pattern, s.upper()))


def extract_bookmarks_from_file(file_path, k):
    """
    Đọc file và xử lý danh sách bookmarks.
    Bỏ qua các số trang dạng chữ La Mã.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.read()

        match = re.search(r'(\[.*\])', lines, re.DOTALL)  
        if match:
            list_str = match.group(1) 
            try:
                content_list = eval(list_str)

                modified_list = [
                    (title, int(page_number) + k)
                    for title, page_number in content_list
                    if isinstance(page_number, int) or not is_roman_numeral(page_number)
                ]

                return modified_list
            except Exception as e:
                print(f"Không thể phân tích cú pháp danh sách. Lỗi: {e}")
                return []
        else:
            return []
    
def add_bookmarks_with_panel(input_pdf, output_pdf, bookmarks):

    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    for title, page_number in bookmarks:
        writer.add_outline_item(title, page_number)

    writer.set_page_mode("/UseOutlines",)

    with open(output_pdf, "wb") as output:
        writer.write(output)

    print(f"Tệp PDF với bookmark đã được lưu tại: {output_pdf}")

def process_pdf(input_pdf, output_pdf, table_contents):
    temp_pdf = extract_pages_with_content(input_pdf)
    if temp_pdf:
        try:
            k = find_first_page(input_pdf)
            extract_table_contents(temp_pdf)
            bookmarks = extract_bookmarks_from_file(table_contents, k)
            add_bookmarks_with_panel(input_pdf, output_pdf, bookmarks)
        finally:
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)

input_pdf = "file_pdf/output_Strategic thinking - Pearson, Gordon J 1939- 1990 - New York - Prentice Hall.pdf"
output_pdf = "file_pdf/test_Strategic thinking - Pearson, Gordon J 1939- 1990 - New York - Prentice Hall.pdf"
table_contents = "table_contents.txt"
process_pdf(input_pdf, output_pdf, table_contents)
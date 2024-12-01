import fitz
import re
import os
import time
import google.generativeai as genai
import PyPDF2
import PyPDF2 as PdfFileMerger
from fpdf import FPDF

genai.configure(api_key='AIzaSyA2U8-Ad6hzJK0jwqOP2U7M4E4i0UgNGxI')


def create_pdf(input_file):
    pdf = FPDF()

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    pdf.add_page()
    pdf.add_font('DejaVuSans', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVuSans', size=12)
    pdf.write(5, text)

    pdf.output('output.pdf')
    merger = PdfFileMerger()
    template_pdf = 'template.pdf'
    if template_pdf:
        merger.append(PdfFileReader(open(template_pdf, 'rb')))
        merger.append(PdfFileReader(open('output.pdf', 'rb')))
        merger.write('merged_output.pdf')

def split_pdf(input_pdf_path, output_dir, pages_per_split=5):
    # Kiểm tra xem thư mục đầu ra có tồn tại không, nếu không tạo mới
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Mở file PDF đầu vào
    with open(input_pdf_path, "rb") as input_pdf_file:
        reader = PyPDF2.PdfReader(input_pdf_file)
        total_pages = len(reader.pages)

        # Tính số lượng file PDF sẽ tạo
        num_splits = (total_pages // pages_per_split) + (1 if total_pages % pages_per_split > 0 else 0)

        # Chia nhỏ file PDF thành các file nhỏ hơn
        for i in range(num_splits):
            writer = PyPDF2.PdfWriter()
            start_page = i * pages_per_split
            end_page = min(start_page + pages_per_split, total_pages)

            # Thêm các trang từ start_page đến end_page vào file PDF mới
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            # Tạo tên file mới
            output_pdf_path = os.path.join(output_dir, f"split_{i+1}.pdf")
            
            # Lưu file PDF mới
            with open(output_pdf_path, "wb") as output_pdf_file:
                writer.write(output_pdf_file)

            print(f"File PDF {output_pdf_path} đã được tạo.")

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

def save_text_to_txt(text, output_txt_path="output.txt"):
    try:
        with open(output_txt_path, 'a', encoding='utf-8') as file:
            file.write(text)
        print(f"Văn bản đã được lưu vào {output_txt_path}")
    except Exception as e:
        print(f"Đã có lỗi xảy ra: {e}")

def process_pdf_to_text(pdf_path):
    # Cấu hình mô hình
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2000,  # Điều chỉnh giới hạn token
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",  # Đảm bảo model bạn chọn hỗ trợ PDF và đầu vào dạng text
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
        response = chat_session.send_message("convert whole content of this file into text")
        save_text_to_txt(response.text)
    except StopCandidateException as e:
        print(f"Error: {e}")


if __name__ == "__main__":

    pdf_path = "file/Ebook - IT test/Cổ_học_tinh_hoa_Ôn_Như_Nguyễn_Văn_Ngọc,_Tử_An_Trần.pdf"
    split_dir = "output"
    split_pdf(pdf_path, split_dir)

    for i in range(1, len(os.listdir(split_dir)) + 1):
        try:
            pdf_part_path = os.path.join(split_dir, f"split_{i}.pdf")
            print(f"Đang xử lý file: {pdf_part_path}")
            process_pdf_to_text(pdf_part_path)  # Hàm xử lý PDF của bạn

        except Exception as e:
            print(f"Lỗi khi xử lý {pdf_part_path}: {e}")
        finally:
            # Xóa file sau khi xử lý xong
            if os.path.exists(pdf_part_path):
                os.remove(pdf_part_path)
                print(f"File {pdf_part_path} đã được xóa.")

    print("Đã hoàn tất việc chuyển đổi toàn bộ nội dung PDF thành văn bản.")

    create_pdf("output.txt")
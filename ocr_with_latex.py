import fitz
import re
import os
import time
import google.generativeai as genai
import PyPDF2
import PyPDF2 as PdfFileMerger
from fpdf import FPDF
import subprocess
from pylatexenc.latex2text import LatexNodes2Text

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
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_pdf_path, "rb") as input_pdf_file:
        reader = PyPDF2.PdfReader(input_pdf_file)
        total_pages = len(reader.pages)

        num_splits = (total_pages // pages_per_split) + (1 if total_pages % pages_per_split > 0 else 0)

        for i in range(num_splits):
            writer = PyPDF2.PdfWriter()
            start_page = i * pages_per_split
            end_page = min(start_page + pages_per_split, total_pages)

            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            output_pdf_path = os.path.join(output_dir, f"split_{i+1}.pdf")
            
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


def save_text_to_txt(text, output_txt_path="test.txt"):
    try:
        with open(output_txt_path, 'a', encoding='utf-8') as file:
            file.write(text)
        print(f"Văn bản đã được lưu vào {output_txt_path}")
    except Exception as e:
        print(f"Đã có lỗi xảy ra: {e}")

def save_text_to_latex_file(text, latex_file_path):
    latex_template = r"""
    \documentclass[a4paper,12pt]{article}
    \usepackage[utf8]{inputenc}
    \usepackage{geometry}
    \geometry{a4paper, margin=1in}
    \usepackage{setspace}
    \setstretch{1.5}
    \usepackage{graphicx}
    \usepackage{hyperref}
    \usepackage{amsmath}
    \usepackage{amssymb}
    \begin{document}
    
    % Content starts here
    \section*{Generated Document}
    {}
    
    % Content ends here
    \end{document}
    """

    escaped_text = text.replace("&", r"\&").replace("%", r"\%").replace("$", r"\$") \
                       .replace("#", r"\#").replace("_", r"\_").replace("{", r"\{") \
                       .replace("}", r"\}").replace("^", r"\^{}").replace("~", r"\~{}") \
                       .replace("\\", r"\textbackslash{}")

    latex_content = latex_template.format(escaped_text)

    with open(latex_file_path, "w", encoding="utf-8") as latex_file:
        latex_file.write(latex_content)
    print(f"LaTeX file saved at: {latex_file_path}")


def convert_latex_in_file(input_file, output_file):
    latex2text_obj = LatexNodes2Text()

    with open(input_file, 'r', encoding='utf-8') as file:
        latex_code = file.read()

    plain_text = latex2text_obj.latex_to_text(latex_code)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(plain_text)

    print(f"Đã chuyển đổi nội dung LaTeX và ghi vào file {output_file}")

def latex_to_pdf(latex_file_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    current_dir = os.getcwd()
    os.chdir(output_dir)

    try:
        result = subprocess.run(
            ["pdflatex", latex_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            print("Error during LaTeX to PDF conversion:")
            print(result.stderr)
            return None

        pdf_file_name = os.path.splitext(os.path.basename(latex_file_path))[0] + ".pdf"
        pdf_file_path = os.path.join(output_dir, pdf_file_name)

        print(f"PDF generated: {pdf_file_path}")
        return pdf_file_path
    finally:
        os.chdir(current_dir)

def process_pdf_to_text(pdf_path):
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2000, 
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",  
        generation_config=generation_config,
    )

    files = [upload_to_gemini(pdf_path, mime_type="application/pdf")]

    wait_for_files_active(files)

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
        response = chat_session.send_message("chuyển nội dung file này thành mã LaTeX")
        save_text_to_txt(response.text)
    except StopCandidateException as e:
        print(f"Error: {e}")


if __name__ == "__main__":

    pdf_path = "file/Ebook - IT test/Transcendental Concepts, Transcendental Truths and Objective Validity.pdf"
    split_dir = "output"
    split_pdf(pdf_path, split_dir)

    for i in range(1, len(os.listdir(split_dir)) + 1):
        try:
            pdf_part_path = os.path.join(split_dir, f"split_{i}.pdf")
            print(f"Đang xử lý file: {pdf_part_path}")
            process_pdf_to_text(pdf_part_path) 
        except Exception as e:
            print(f"Lỗi khi xử lý {pdf_part_path}: {e}")
        finally:
            if os.path.exists(pdf_part_path):
                os.remove(pdf_part_path)
                print(f"File {pdf_part_path} đã được xóa.")

    print("Đã hoàn tất việc chuyển đổi toàn bộ nội dung PDF thành văn bản.")

    convert_latex_in_file('test.txt', 'result.txt')
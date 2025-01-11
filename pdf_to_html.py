import subprocess
import os

PDF2HTMLEX_PATH = os.path.abspath("pdf2htmlEX/pdf2htmlEX.exe")

def pdf_to_html(input_pdf, output_html):
    """
    Chuyển đổi một tệp PDF thành HTML bằng pdf2htmlEX.
    """
    try:
        subprocess.run(
            [PDF2HTMLEX_PATH, input_pdf, output_html],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"Chuyển đổi thành công: {output_html}")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi chuyển đổi {input_pdf}: {e}")
    except Exception as e:
        print(f"Lỗi không xác định khi chuyển đổi {input_pdf}: {e}")

def pdf_to_html_directory(input_dir, output_dir):
    """
    Chuyển đổi tất cả các tệp PDF trong một thư mục thành HTML.
    """
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)

        if os.path.isfile(input_path) and filename.endswith('.pdf'):
            output_filename = os.path.splitext(filename)[0] + ".html"
            output_path = os.path.join(output_dir, output_filename)
            try:
                print(f"Đang chuyển đổi: {filename}")
                pdf_to_html(input_path, output_path)
                print(f"Hoàn tất chuyển đổi: {filename}")
            except Exception as e:
                print(f"Lỗi khi chuyển đổi {filename}: {e}")

if __name__ == "__main__":
    input_directory = "./file"
    output_directory = "./file_html"

    pdf_to_html_directory(input_directory, output_directory)

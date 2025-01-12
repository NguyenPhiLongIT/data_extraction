import subprocess
import os
import shutil

PDF2HTMLEX_PATH = os.path.abspath("pdf2htmlEX\pdf2htmlEX.exe")


def pdf_to_html(input_pdf, temp_html, final_html):
    """
    Chuyển đổi một tệp PDF thành HTML bằng pdf2htmlEX.
    """
    try:
        # Thực thi lệnh pdf2htmlEX để tạo file HTML tạm
        subprocess.run(
            [PDF2HTMLEX_PATH, input_pdf, temp_html],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(f"Chuyển đổi thành công: {temp_html}")

        # Di chuyển file HTML tạm vào thư mục đầu ra
        shutil.move(temp_html, final_html)
        print(f"Di chuyển đến: {final_html}")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi chuyển đổi {input_pdf}: {e.stderr}")
    except Exception as e:
        print(f"Lỗi không xác định khi chuyển đổi {input_pdf}: {e}")
    finally:
        # Xóa file tạm nếu còn tồn tại
        if os.path.exists(temp_html):
            os.remove(temp_html)


def pdf_to_html_directory(input_dir, output_dir):
    """
    Chuyển đổi tất cả các tệp PDF trong một thư mục thành HTML.
    """
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    # Tạo thư mục đầu ra nếu chưa tồn tại
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)

        # Chỉ xử lý file PDF
        if os.path.isfile(input_path) and filename.endswith(".pdf"):
            base_filename = os.path.splitext(filename)[0]
            temp_html = f"{base_filename}.html"  # File HTML tạm
            final_html = os.path.join(output_dir, temp_html)  # File HTML cuối cùng

            try:
                print(f"Đang chuyển đổi: {filename}")
                pdf_to_html(input_path, temp_html, final_html)
                print(f"Hoàn tất chuyển đổi: {filename}")
            except Exception as e:
                print(f"Lỗi khi chuyển đổi {filename}: {e}")


if __name__ == "__main__":
    # Đường dẫn thư mục đầu vào và đầu ra
    input_directory = "file"
    output_directory = "file_html"

    pdf_to_html_directory(input_directory, output_directory)

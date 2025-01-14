import os
from pdfminer.high_level import extract_text
from pdfminer.layout import LTTextBoxHorizontal, LTTextLineHorizontal
from pdfminer.high_level import extract_pages

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTTextLineHorizontal


def get_previous_line(pdf_path, page_num):
    """
    Tìm dòng trước dòng thụt vào nhất trong một trang PDF, sử dụng tọa độ x.

    Args:
        pdf_path (str): Đường dẫn đến tệp PDF.
        page_num (int): Số trang trong tệp PDF cần xử lý.

    Returns:
        tuple: (dòng trước, dòng thụt vào nhất) hoặc None nếu không tìm thấy.
    """
    lines = []

    # Trích xuất các đối tượng từ trang PDF
    for page_layout in extract_pages(pdf_path, page_numbers=[page_num]):
        for element in page_layout:
            if isinstance(element, LTTextLineHorizontal):
                text = element.get_text()
                x0 = element.x0  # Tọa độ x của chữ đầu tiên trong dòng
                lines.append((text, x0))

    # Sắp xếp các dòng theo tọa độ x (để nhận diện dòng thụt vào)
    lines = sorted(lines, key=lambda x: x[1])

    # Tìm dòng thụt vào nhất (có tọa độ x lớn nhất)
    if lines:
        # Tìm dòng có tọa độ x lớn nhất
        indented_line = max(lines, key=lambda x: x[1])

        # Tìm dòng trước dòng thụt vào nhất
        for i, line in enumerate(lines):
            if line == indented_line and i > 0:
                return lines[i - 1], indented_line

    return None  # Không tìm thấy dòng trước hoặc không có dòng thụt vào


def process_pdf_in_folder(folder_path, output_file):
    """
    Duyệt qua tất cả các PDF trong thư mục, đọc từng trang, trích xuất block và áp dụng hàm get_previous_line.

    Args:
        folder_path (str): Đường dẫn đến thư mục chứa các tệp PDF.
        output_file (str): Tên tệp TXT để lưu kết quả.
    """
    with open(output_file, "w", encoding="utf-8") as out_file:
        # Duyệt qua các tệp PDF trong thư mục
        for filename in os.listdir(folder_path):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(folder_path, filename)
                print(f"Đang xử lý tệp: {pdf_path}")

                # Trích xuất văn bản từ tệp PDF bằng pdfminer (Để xác định số trang)
                text = extract_text(pdf_path)

                # Lấy số trang từ văn bản
                num_pages = (
                    text.count("\f") + 1
                )  # Số trang thường có ký tự phân trang '\f'

                # Duyệt qua các trang và áp dụng hàm get_previous_line
                for page_num in range(num_pages):
                    result = get_previous_line(
                        pdf_path, page_num
                    )  # Truyền pdf_path và page_num
                    if result:
                        prev_line, indented_line = result
                        out_file.write(
                            f"--- Tệp {filename}, Trang {page_num + 1} ---\n"
                        )
                        out_file.write(f"Dòng trước: {prev_line}\n")
                        out_file.write(f"Dòng thụt vào nhất: {indented_line}\n\n")
                    else:
                        out_file.write(
                            f"--- Tệp {filename}, Trang {page_num + 1} ---\n"
                        )
                        out_file.write(
                            "Không tìm thấy dòng thụt vào hoặc dòng trước đó.\n\n"
                        )
                out_file.write("\n--- Kết thúc tệp PDF ---\n\n")


# Gọi hàm với thư mục chứa PDF và tệp TXT xuất kết quả
folder_path = "./file"  # Đường dẫn đến thư mục chứa các tệp PDF
output_file = "output.txt"  # Tên tệp TXT để lưu kết quả

process_pdf_in_folder(folder_path, output_file)

import subprocess
import os

def ocr_pdf(input_pdf, output_pdf):
    try:
        subprocess.run([
            "ocrmypdf", 
            "--language", "vie", 
            "--tesseract-config", "pdf", 
            input_pdf, 
            output_pdf
        ], check=True)
        print(f"OCR hoàn tất. File đã lưu tại: {output_pdf}")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi thực hiện OCR: {e}")

def ocr_pdf_directory(input_dir, output_dir):
    # Lấy đường dẫn tuyệt đối cho input_dir và output_dir
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        
        if os.path.isfile(file_path) and filename.endswith('.pdf'):
            # Tạo đường dẫn cho tệp đầu ra
            output_file_path = os.path.join(output_dir, filename)  # Giữ nguyên tên tệp

            try:
                print(f"Đang thực hiện OCR cho tệp: {filename}")
                ocr_pdf(file_path, output_file_path)
                print(f"OCR hoàn thành cho tệp: {filename}")
            except Exception as e:
                print(f"Lỗi khi thực hiện OCR cho tệp {filename}: {e}")

if __name__ == "__main__":
    input_dir = "../file"  # Thư mục đầu vào chứa các tệp PDF
    output_dir = "../result"  # Thư mục đầu ra chứa các tệp OCR đã xử lý
    ocr_pdf_directory(input_dir, output_dir)

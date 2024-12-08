import ocrmypdf
import os

def ocr(file_path, save_path):
    # os.environ["PATH"] += os.pathsep + r"G:\WebDeveloper\MyProject\data_extraction\lib\gs10.04.0\bin"
    base_dir = os.path.abspath(os.path.dirname(__file__))
    ghostscript_dir = os.path.join(base_dir, "..", "lib", "gs10.04.0", "bin")
    tesseract_exe = os.path.join(base_dir, "..", "lib", "tesseract.exe")
    os.environ["PATH"] += os.pathsep + ghostscript_dir
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File input '{file_path}' không tồn tại.")

    output_dir = os.path.dirname(save_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    try:
        ocrmypdf.ocr(
            file_path, 
            save_path, 
            language="eng", 
            tesseract_cmd="lib/tesseract.exe" 
        )
        print(f"OCR thành công. File đã lưu tại: {save_path}")
    except Exception as e:
        print(f"Lỗi khi thực hiện OCR: {e}")

def process():
    file = "file/Ebook - IT test/Cổ_học_tinh_hoa_Ôn_Như_Nguyễn_Văn_Ngọc,_Tử_An_Trần.pdf"
    output = "output_scan_vie.pdf"
    try: 
        ocr(file, output)
    except Exception as e:
        print(f"Lỗi: {e}")

def ocr_pdf_directory(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        
        if os.path.isfile(file_path) and filename.endswith('.pdf'):
            output_file_path = os.path.join(output_dir, filename)
            
            try:
                print(f"Đang thực hiện OCR cho tệp: {filename}")
                ocrmypdf.ocr(
                    file_path, 
                    output_file_path,   
                )
                print(f"OCR hoàn thành cho tệp: {filename}")
            except Exception as e:
                print(f"Lỗi khi thực hiện OCR cho tệp {filename}: {e}")


if __name__ == "__main__":
    input_dir = "file/Ebook - IT test"
    output_dir = "file/result"
    ocr_pdf_directory(input_dir, output_dir)
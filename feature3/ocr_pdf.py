import subprocess
import os

def ocr(file_path, save_path):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    tesseract_exe = os.path.join(base_dir, "..", "lib", "tesseract.exe")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File input '{file_path}' không tồn tại.")
    
    output_dir = os.path.dirname(save_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    command = [
        tesseract_exe, 
        file_path, 
        save_path,  
        "-l", "vie"  
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"OCR thành công. File đã lưu tại: {save_path}")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi thực hiện OCR: {e}")

def ocr_pdf_directory(input_dir, output_dir):
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        
        if os.path.isfile(file_path) and filename.endswith('.pdf'):
            output_file_path = os.path.join(output_dir, filename.replace('.pdf', '_ocr.pdf')) 

            try:
                print(f"Đang thực hiện OCR cho tệp: {filename}")
                print(f"Đường dẫn kết quả: {output_file_path}")  
                ocr(file_path, output_file_path)
                print(f"OCR hoàn thành cho tệp: {filename}")
            except Exception as e:
                print(f"Lỗi khi thực hiện OCR cho tệp {filename}: {e}")

if __name__ == "__main__":
    input_dir = "../file"  
    output_dir = "../result"  
    ocr_pdf_directory(input_dir, output_dir)

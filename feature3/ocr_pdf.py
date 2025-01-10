import subprocess
import os

TESSERACT_PATH = os.path.abspath("lib/tesseract.exe")
TESSDATA_PREFIX = os.path.abspath("lib/tessdata")
GHOSTSCRIPT_PATH = os.path.abspath("./lib/gs10.04.0/bin/gswin64c.exe")

def ocr_pdf(input_pdf, output_pdf, language="vie"):     #language="vie"/language="eng"
    try:
        env = os.environ.copy()
        env["TESSDATA_PREFIX"] = TESSDATA_PREFIX
        env["PATH"] = os.pathsep.join([
            os.path.dirname(TESSERACT_PATH),
            os.path.dirname(GHOSTSCRIPT_PATH),
            env.get("PATH", "")
        ])
        subprocess.run([
            "ocrmypdf", 
            "--language", language,
            "--tesseract-config", "pdf", 
            input_pdf, 
            output_pdf
        ], check=True, env=env)
        print(f"OCR hoàn tất. File đã lưu tại: {output_pdf}")
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
            output_file_path = os.path.join(output_dir, filename) 
            try:
                print(f"Đang thực hiện OCR cho tệp: {filename}")
                ocr_pdf(file_path, output_file_path)
                print(f"OCR hoàn thành cho tệp: {filename}")
            except Exception as e:
                print(f"Lỗi khi thực hiện OCR cho tệp {filename}: {e}")

if __name__ == "__main__":
    input_dir = "file"  
    output_dir = "result"  

    ocr_pdf_directory(input_dir, output_dir)

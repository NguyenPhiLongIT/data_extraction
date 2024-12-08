import fitz

def extract_pdf_by_keywords(input_pdf, output_pdf, keywords):
    try:
        pdf_document = fitz.open(input_pdf)
        num_pages = pdf_document.page_count
        print(f"Số trang trong PDF: {num_pages}")
        
        output_document = fitz.open()
        
        for i in range(num_pages):
            page = pdf_document[i]
            text = page.get_text("text")
            
            if any(keyword.lower() in text.lower() for keyword in keywords):
                print(f"Trang {i + 1} chứa từ khóa, được thêm vào kết quả.")
                output_document.insert_pdf(pdf_document, from_page=i, to_page=i)
            else:
                print(f"Trang {i + 1} không chứa từ khóa, bị loại bỏ.")
        
        if output_document.page_count > 0:
            output_document.save(output_pdf)
            print(f"Đã lưu tệp PDF đầu ra: {output_pdf}")
        else:
            print("Không có trang nào chứa từ khóa. Không tạo tệp đầu ra.")
        
        output_document.close()
        pdf_document.close()
    
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

if __name__ == "__main__":
    input_pdf = "file/the-fifth-discipline-the-art-and-practice-of-the-learning-organization_compress.pdf"
    output_pdf = "file/output.pdf"
    keywords = ["Discipline", "Structure", "patience", "principal"]

    extract_pdf_by_keywords(input_pdf, output_pdf, keywords)
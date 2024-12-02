import fitz  # PyMuPDF


def extract_text_from_pdf(input_pdf):
    doc = fitz.open(input_pdf)
    extracted_data = {}

    # Lặp qua các trang trong tài liệu PDF
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text()

        # Nếu trang có văn bản, lưu vào extracted_data
        if page_text.strip():  # Kiểm tra nếu trang có văn bản
            extracted_data[page_num] = page_text.strip()
        else:
            print("không")

    return extracted_data
output_pdf = "pdf_with_one_page.pdf"
print(extract_text_from_pdf(output_pdf))
# import fitz  # PyMuPDF


# def create_pdf_with_one_page(output_pdf):
#     # Tạo tài liệu PDF trống
#     doc = fitz.open()

#     # Thêm một trang mới vào tài liệu
#     doc.new_page()

#     # Lưu tài liệu PDF với một trang trống
#     doc.save(output_pdf)


# # Ví dụ sử dụng
# output_pdf = "pdf_with_one_page.pdf"
# create_pdf_with_one_page(output_pdf)

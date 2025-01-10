from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_pdf="../Cổ_học_tinh_hoa_Ôn_Như_Nguyễn_Văn_Ngọc,_Tử_An_Trần.pdf", output_pdf="output_part.pdf", max_pages_per_part=5):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Chỉ lấy tối đa max_pages_per_part trang đầu tiên
    for i in range(min(len(reader.pages), max_pages_per_part)):
        writer.add_page(reader.pages[i])

    # Lưu file PDF đầu ra
    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

    return output_pdf

split_pdf()
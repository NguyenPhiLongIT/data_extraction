import fitz  # PyMuPDF


def create_index_page_with_links(input_pdf, index_data, output_pdf):
    doc = fitz.open(input_pdf)

    # Tạo trang index trống
    index_page = doc.new_page()  # Tạo một trang mới trong tài liệu
    index_page.insert_text(
        (100, 50), "Index", fontsize=16, fontname="helv"
    )  # Tiêu đề trang index

    # Thêm từ khóa vào trang index với liên kết
    y_position = 100  # Vị trí bắt đầu cho từ khóa
    for word, target_pages in index_data.items():
        # Thêm từ khóa vào trang index
        index_page.insert_text((100, y_position), f"{word}: ", fontsize=12)

        # Lặp qua các trang mà từ khóa xuất hiện và thêm liên kết
        for target_page in target_pages:
            rect = fitz.Rect(200, y_position, 300, y_position + 20)
            index_page.insert_text(
                (200, y_position), f"{target_page}", fontsize=12
            )

            # Chèn liên kết để nhảy đến trang mục tiêu
            index_page.insert_link(
                {
                    "kind": fitz.LINK_GOTO,
                    "from": rect,
                    "page": target_page - 1,
                }  # target_page - 1 vì trang trong PyMuPDF bắt đầu từ 0
            )

            y_position += 25  # Di chuyển xuống dưới sau mỗi liên kết

        y_position += 20  # Khoảng cách giữa các từ khóa

    # Lưu tài liệu PDF với trang index và các liên kết
    doc.save(output_pdf)


# Dữ liệu index mẫu (từ khóa và số trang)
index_data = {
    "Introduction": [1],
    "Chapter 1": [3,1],
    "Chapter 2": [5,1000]
    # "Conclusion": 10,
}

# Gọi hàm để tạo trang index với các liên kết
create_index_page_with_links(
    "file/CVv380S262020085_1.pdf", index_data, "CVv380S262020085_2.pdf"
)

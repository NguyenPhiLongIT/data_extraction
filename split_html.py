from bs4 import BeautifulSoup
import os


def split_html(input_html, output_dir, chunk_size=5):
    """
    Chia nhỏ file HTML thành các phần nhỏ hơn và lưu vào thư mục output_dir.
    """
    try:
        # Đọc nội dung file HTML
        with open(input_html, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # Tìm tất cả các thẻ <body> để chia theo các phần
        body_content = soup.find("body")

        # Tạo thư mục đầu ra nếu chưa có
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Chia nội dung thành các phần nhỏ
        children = body_content.find_all(
            True, recursive=False
        )  # Các thẻ con trực tiếp của <body>
        total_chunks = (
            len(children) + chunk_size - 1
        ) // chunk_size  # Tính số phần nhỏ

        for i in range(total_chunks):
            chunk = children[i * chunk_size : (i + 1) * chunk_size]

            # Tạo một file HTML mới cho mỗi phần
            new_soup = BeautifulSoup("<html><body></body></html>", "html.parser")
            new_body = new_soup.find("body")
            for element in chunk:
                new_body.append(element)

            # Lưu phần nhỏ vào file
            output_html = os.path.join(output_dir, f"part_{i + 1}.html")
            with open(output_html, "w", encoding="utf-8") as f_out:
                f_out.write(str(new_soup))

            print(f"Đã chia nhỏ file HTML thành: {output_html}")
    except Exception as e:
        print(f"Lỗi khi phân mảnh HTML: {e}")


# Sử dụng ví dụ
input_html = "file_html/result_The_worlds_20_greatest_unsolved_problems_Vacca_John_R_2005_goc.html"  # Đường dẫn đến file HTML gốc
output_dir = "split_html"  # Thư mục để lưu các phần nhỏ
split_html(input_html, output_dir, chunk_size=5)

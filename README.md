# data_extraction

## Getting started
```sh
pip install -r requirements.txt
```

## List of Scripts:
1. feature1 - extract text or paragraph depend on keywords into excel
2. feature2 - like feature1 but extract into notion
3. feature3 - ocr pdf image with vietnamese or english language option, it works on pdf with images no text

## Details:
1. OCR pdf image:
   - Dùng thư viện ocrmypdf kết hợp lib của Tesseract
   - Trường hợp sử dụng: với những pdf chỉ toàn ảnh, có 2 option ngôn ngữ là tiếng việt hoặc tiếng anh. Có thể import thêm ngôn ngữ cần muốn tại https://github.com/tesseract-ocr/tessdata.git và bỏ nó vào thư mục feature3/lib/tessdata
2. PDF searchble(with Index page and bookmark) tại branch pdf_searchble:
   - Dùng các thư viện PDF của python và api của Google AI Studio
   - Mô tả:
     Tìm trang Contents của pdf, trang Index của pdf
     Dùng api của Google AI Studio để đọc trang Contents -> rút trích tạo bookmarks
     Duyệt trang Index và xác định các trường hợp số trang, đồng thời gắn link số đến trang hợp lệ
   - Trường hợp sử dụng: với những pdf có đánh số trang, có trang Contents và trang Index.
   - Trường hợp ngoại lệ: vì dùng api của Google AI Studio để đọc trang Contents nên đối với trang Contents định dạng quá phức tạp sẽ có 10% nó trả về kết quả bookmark sai. Chỉ cần chạy lại lần nữa thì có thể khắc phục điều đó. 

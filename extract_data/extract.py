import pandas as pd
import fitz  # PyMuPDF
import re
from unidecode import unidecode 
import openpyxl
from openpyxl import load_workbook
from openpyxl.styles import Alignment

def extract_text_from_pdf(pdf_path):
    """Hàm đọc văn bản từ file PDF."""
    doc = fitz.open(pdf_path)
    output = []
    
    # Trích xuất các block văn bản từ mỗi trang trong PDF
    for page in doc:
        output += page.get_text("blocks")
    print(output)
    return output

def read_keywords_from_txt(txt_path):
    """Hàm đọc từ khóa từ file txt."""
    with open(txt_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Tách từ khóa theo dấu ',' hoặc xuống dòng
        keywords = re.split(r'[,\n]+', content.strip())
    return [keyword.strip() for keyword in keywords if keyword.strip()]

def extract_sentence(pdf_text, keywords):
    found_sentences = []
    
    # Duyệt qua từng block
    for block in pdf_text:
        # Kiểm tra xem block có chứa văn bản hay không
        if block[6] == 0:  # Giả sử block[6] = 0 là văn bản, nếu không thì bỏ qua
            plain_text = block[4]  # Giả sử block[4] chứa nội dung văn bản
            
            # Tách block thành các câu (dùng dấu chấm, chấm hỏi, dấu chấm than)
            sentences = re.split(r'[.!?]', plain_text)
            
            # Duyệt qua từng câu và tìm kiếm từ khóa
            for sentence in sentences:
                for keyword in keywords:
                    if keyword.lower() in sentence.lower():
                        found_sentences.append(sentence.strip())
                        break  # Dừng lại nếu tìm thấy từ khóa trong câu
                        
    return found_sentences

def extract_paragraph(pdf_text, keywords):
    """Hàm tìm các đoạn văn chứa từ khóa."""
    found_segments = []
    previous_block_id = 0  # Biến đánh dấu ID của block trước đó

    # Duyệt qua từng block văn bản
    for block in pdf_text:
        if block[6] == 0:  # Kiểm tra xem block có chứa văn bản (0 là văn bản, không phải hình ảnh)
            # Kiểm tra xem block có khác với block trước không (để tránh lặp lại)
            if previous_block_id != block[5]:
                previous_block_id = block[5]  # Cập nhật block ID
            
            # Loại bỏ dấu tiếng Việt và giữ nguyên văn bản
            plain_text = unidecode(block[4]).strip()
            
            # Tìm kiếm từ khóa trong văn bản
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', plain_text, re.IGNORECASE):
                    found_segments.append({'keyword': keyword, 'found_segment': plain_text})
                    break  # Nếu tìm thấy từ khóa, không cần kiểm tra thêm các từ khóa khác trong block này
    
    return found_segments

def process_pdf_and_txt(txt_path, pdf_path, output_path):
    """Hàm chính để xử lý file txt và file PDF."""
    keywords = read_keywords_from_txt(txt_path)

    # Đọc văn bản từ PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    
    # Tạo workbook mới hoặc mở workbook hiện tại
    wb = load_workbook(output_path)
    
    # Xóa các sheet cũ nếu có
    if 'Sentence' in wb.sheetnames:
        del wb['Sentence']
    if 'Paragraph' in wb.sheetnames:
        del wb['Paragraph']

    # Trích xuất dữ liệu theo câu và đoạn văn
    found_segments_sentence = extract_sentence(pdf_text, keywords)  # Trích xuất theo câu
    found_segments_paragraph = extract_paragraph(pdf_text, keywords)  # Trích xuất theo đoạn văn
    
    # Đảm bảo rằng `found_segments_sentence` là một danh sách các từ điển
    found_segments_sentence_with_keyword = []
    for sentence in found_segments_sentence:
        for keyword in keywords:
            if keyword.lower() in sentence.lower():  # Kiểm tra nếu từ khóa xuất hiện trong câu
                found_segments_sentence_with_keyword.append({'keyword': keyword, 'found_segment': sentence})
                break  # Dừng lại nếu đã tìm thấy từ khóa trong câu

    # Tạo DataFrame và lưu kết quả vào các sheet riêng biệt
    # Sheet cho câu
    df_sentence = pd.DataFrame(found_segments_sentence_with_keyword)
    if 'Sentence' not in wb.sheetnames:
        ws_sentence = wb.create_sheet('Sentence')
    else:
        ws_sentence = wb['Sentence']
    for row in df_sentence.itertuples(index=False, name=None):
        ws_sentence.append(row)

    # Sheet cho đoạn văn
    df_paragraph = pd.DataFrame(found_segments_paragraph)
    if 'Paragraph' not in wb.sheetnames:
        ws_paragraph = wb.create_sheet('Paragraph')
    else:
        ws_paragraph = wb['Paragraph']
    for row in df_paragraph.itertuples(index=False, name=None):
        ws_paragraph.append(row)

    # Tiến hành căn chỉnh cột và hàng cho cả 2 sheet
    for sheet_name in ['Sentence', 'Paragraph']:
        ws = wb[sheet_name]

        for row in ws.iter_rows(min_row=2, min_col=2, max_col=2):  # Chỉ căn chỉnh cột 'found_segment'
            for cell in row:
                cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

        # Căn chỉnh độ rộng cột 'found_segment' (cột 2)
        column = 'B'
        max_length = 0
        for row in ws.iter_rows(min_row=2, min_col=2, max_col=2):  # Duyệt qua cột 'found_segment'
            for cell in row:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))  # Tính độ dài tối đa của văn bản trong ô

        adjusted_width = min(max_length + 2, 50)  # Điều chỉnh độ rộng cột sao cho vừa đủ, không vượt quá 50
        ws.column_dimensions[column].width = adjusted_width

        # Căn chỉnh chiều cao hàng sao cho phù hợp với nội dung
        for row in ws.iter_rows(min_row=2, min_col=1, max_col=ws.max_column):
            max_height = 0
            for cell in row:
                if cell.value:
                    max_height = max(max_height, len(str(cell.value).split('\n')))
            ws.row_dimensions[row[0].row].height = (max_height * 15)

    # Lưu lại file Excel với các thay đổi
    wb.save(output_path)
    print(f"Đã trích xuất và căn chỉnh trong file excel: {output_path}")



txt_path = 'keywords.txt' 
pdf_path = 'Strategic_thinking_output_part.pdf'  
output_path = 'output.xlsx'
process_pdf_and_txt(txt_path, pdf_path, output_path)

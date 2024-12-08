import fitz
import requests
import json
import os
import re
import time


def format_page_id(page_id):
    return f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"

NOTION_TOKEN = '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'
DATABASE_ID = '1484aca00987806e86cce825a36c0cdd'
PAGE_ID = format_page_id('1484aca0098780619fe6c45cffc058d8')

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def create_database(data: dict):
    create_url = "https://api.notion.com/v1/pages"

    payload = {"parent": {"database_id": DATABASE_ID}, "properties": data}

    res = requests.post(create_url, headers=headers, json=payload)
    # print(res.status_code)
    # print("Response:", res.json())
    return res

def create_page(content):
    append_url = f"https://api.notion.com/v1/blocks/{PAGE_ID}/children"
    payload = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content
                            }
                        }
                    ]
                }
            }
        ]
    }

    res = requests.patch(append_url, headers=headers, json=payload)
    if res.status_code == 200:
        print("Đã thêm nội dung vào Notion Page")
    else:
        print(f"Lỗi khi thêm nội dung: {res.status_code}, Response: {res.json()}")

def remove_header_footer(pdf_extracted_text):
    page_format_pattern = r'([pP]+[aA]+[gG]+[\s]*[\d]+)'
    url_pattern = r'https?://[^\s]+'
    pdf_extracted_text = pdf_extracted_text.split("\n")
    header = pdf_extracted_text[0].strip()
    footer = pdf_extracted_text[-1].strip()
    
    if re.search(page_format_pattern, header) or header.isnumeric():
        pdf_extracted_text = pdf_extracted_text[1:]
    
    if re.search(page_format_pattern, footer) or footer.isnumeric():
        pdf_extracted_text = pdf_extracted_text[:-1]
    
    pdf_extracted_text = [re.sub(url_pattern, '', line) for line in pdf_extracted_text]
    pdf_extracted_text = "\n".join(pdf_extracted_text)
    return pdf_extracted_text

def trim_text_to_limit(text, limit=2000):
    if len(text) > limit:
        return text[:limit]
    return text

def extract_pdf_notion(input_pdf, keywords):
    try:
        if not os.path.isfile(input_pdf):
            print(f"Tệp PDF không tồn tại: {input_pdf}")
            return

        pdf_document = fitz.open(input_pdf)
        num_pages = pdf_document.page_count
        print(f"Số trang trong PDF: {num_pages}")

        sentence_count = 0

        for page_number in range(1, min(345, num_pages)):  # Giới hạn từ trang 7 đến 345
            page = pdf_document[page_number]
            text = page.get_text("text")

            if not text:
                print(f"Trang {page_number + 1} không có nội dung.")
                continue

            keyword_match_count = 0
            keyword_match = []
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    keyword_match_count += 1
                    keyword_match.append(keyword)

            if keyword_match_count > 0:
                text = remove_header_footer(text)
                text = trim_text_to_limit(text)
                data = {
                    "Title": {"title": [{"text": {"content": f"Trang {page_number + 1}"}}]},
                    "Content": {"rich_text": [{"text": {"content": text}}]},
                    "Keywords": {"multi_select": [{"name": kw} for kw in keyword_match]},
                    "Page Number": {"number": page_number + 1},
                }

                create_database(data)

                sentence_count += 1
                print(f"Trang {page_number + 1}: Tìm thấy {keyword_match}")

        pdf_document.close()
        print("Hoàn thành quá trình trích xuất.")

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")


def read_from_pdf(pdf_file):
    try:
        pdf_document = fitz.open(pdf_file)
        num_pages = pdf_document.page_count
        
        print(f"Số trang trong PDF: {num_pages}")
        
        for i in range(num_pages):
            page = pdf_document[i]
            text = page.get_text("text")
            extracted_text = remove_header_footer(text)
            
            if extracted_text.strip():
                content = trim_text_to_limit(extracted_text)
                create_page(content)
        
        pdf_document.close()
        print(f"\nĐọc PDF hoàn tất!")
    
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")


if __name__ == "__main__":
    pdf_file = "file/378-775-1-SM.pdf"
    keywords = ["Cypher", "Neo4j", "LDA"]

    start_time = time.time()
    extract_pdf_notion(pdf_file, keywords)
    # read_from_pdf(pdf_file)
    end_time = time.time() 
    elapsed_time = end_time - start_time
    print(f"Thời gian trích xuất: {elapsed_time:.2f} giây")


import os
import requests
import fitz
from pymupdf4llm import to_markdown
from pandas import Series

def scrape_paper(row: Series, timeout: int=15, do_not_overwrite: bool=True):
    md = row.get("paper markdown", None)
    if do_not_overwrite and isinstance(md, str) and md.strip() != "":
        return md
    
    url = row["url"]
    if isinstance(url, str) and url.strip() != "":
        try:
            if url.startswith("file://"):
                file_path = url.replace("file://", "")
            elif os.path.isfile(url):
                file_path = url
            else:
                file_path = None

            if file_path:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
                with fitz.open(file_path) as doc:
                    return to_markdown(doc)
            
            else: 
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                content_type = response.headers.get('content-type', '')
                if 'pdf' not in content_type.lower():
                    raise Exception(f"No PDF content found for URL: {url}")
                with fitz.open(stream=response.content, filetype="pdf") as doc:
                    return to_markdown(doc)
        
        except Exception as e:
            print(f"Failed to retrieve: {url}\nError: {e}")
            return ""
import json
import fitz
import requests
import io
import re
import os

class DeepScienceExtractor:
    def __init__(self):
        self.stop_words = [r"\bReferences\b", r"\bBibliography\b", r"\bLiterature Cited\b"]
        
    def download_pdf(self, url):
        print(f"  -> Downloading: {url}")
        headers = {'User-Agent': 'Mozilla/5.0'} 
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                return io.BytesIO(response.content)
            else:
                print(f"  -> Failed. Status: {response.status_code}")
                return None
        except Exception as e:
            print(f"  -> Error downloading: {e}")
            return None

    def extract_clean_text(self, pdf_stream):
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        full_text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("blocks")
            
            for block in blocks:
                text = block[4].strip() 
                if len(text.split()) < 4 and (text.isdigit() or "arXiv" in text):
                    continue
                full_text += text + "\n"
        
        full_text = re.sub(r'-\n', '', full_text)
        full_text = re.sub(r'\s+', ' ', full_text)
        
        for stop_word in self.stop_words:
            match = re.search(stop_word, full_text, flags=re.IGNORECASE)
            if match:
                full_text = full_text[:match.start()]
                print("  -> Text truncated at Bibliography.")
                break 
                
        return full_text.strip()

def process_knowledge_base(json_filename="raw_knowledge_base.json", output_dir="extracted_texts"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Loading {json_filename}...")
    with open(json_filename, 'r', encoding='utf-8') as f:
        records = json.load(f)

    extractor = DeepScienceExtractor()
    successful_extractions = 0

    for index, record in enumerate(records):
        title = record.get("title", f"Document_{index}")
        pdf_url = record.get("pdf_url")
        
        print(f"\nProcessing [{index+1}/{len(records)}]: {title[:50]}...")
        
        if not pdf_url:
            print("  -> Skipped: No PDF URL available.")
            continue
            
        pdf_stream = extractor.download_pdf(pdf_url)
        
        if pdf_stream:
            clean_text = extractor.extract_clean_text(pdf_stream)
            
            safe_title = re.sub(r'[^\w\-_\. ]', '_', title)[:50]
            output_path = os.path.join(output_dir, f"{safe_title}.txt")
            
            with open(output_path, 'w', encoding='utf-8') as text_file:
                text_file.write(clean_text)
                
            print(f"  -> Saved! Characters extracted: {len(clean_text)}")
            successful_extractions += 1

    print(f"\n✅ Pipeline Complete! Successfully extracted deep text from {successful_extractions} papers.")

if __name__ == "__main__":
    process_knowledge_base()
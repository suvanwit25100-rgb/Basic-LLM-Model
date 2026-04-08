import os
import json
import re
import time
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai

API_KEY = "AIzaSyD4CCMMgm1FbpRSnwNfgaDfxGjvGazqp4E"
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash') 

class SyntheticDataGenerator:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            length_function=len,
        )

    def clean_json_output(self, text):
        text = text.replace("```json", "").replace("```", "").strip()
        return text

    def generate_qa_pairs(self, text_chunk):
        system_prompt = f"""
        You are an expert data curator building a dataset to train a Space and Physics Tutor AI.
        Read the following academic text chunk. 
        Generate exactly 2 highly technical questions a university physics student would ask based ONLY on this text.
        Then, generate the response an expert, patient physics tutor would give. The response must be highly detailed, scientifically accurate, and use step-by-step logic.
        
        OUTPUT FORMAT:
        You must output strictly a JSON array of objects, with no additional text. 
        Example:
        [
            {{"instruction": "Student question here?", "response": "Tutor answer here."}},
            {{"instruction": "Student question 2 here?", "response": "Tutor answer 2 here."}}
        ]
        
        TEXT CHUNK:
        {text_chunk}
        """
        
        try:
            response = model.generate_content(system_prompt)
            clean_text = self.clean_json_output(response.text)
            return json.loads(clean_text)
        except Exception as e:
            print(f"      [!] API/Parsing Error: {e}")
            return None

def build_dataset(input_dir="extracted_texts", output_file="physics_tutor_dataset.jsonl"):
    generator = SyntheticDataGenerator()
    
    if not os.path.exists(input_dir):
        print(f"Error: Directory '{input_dir}' not found.")
        return

    print(f"Initializing Engine. Outputting to {output_file}...\n")
    
    with open(output_file, 'a', encoding='utf-8') as outfile:
        
        for filename in os.listdir(input_dir):
            if not filename.endswith(".txt"):
                continue
                
            filepath = os.path.join(input_dir, filename)
            print(f"Processing Paper: {filename}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_text = f.read()
                
            chunks = generator.text_splitter.split_text(raw_text)
            print(f"  -> Split into {len(chunks)} chunks.")
            
            for i, chunk in enumerate(chunks[:5]):
                print(f"    -> Generating Q&A for chunk {i+1}...")
                qa_pairs = generator.generate_qa_pairs(chunk)
                
                if qa_pairs:
                    for pair in qa_pairs:
                        json.dump(pair, outfile, ensure_ascii=False)
                        outfile.write('\n')
                
                time.sleep(4) 
                
    print(f"\n✅ Dataset Generation Complete! Check {output_file}")

if __name__ == "__main__":
    build_dataset()
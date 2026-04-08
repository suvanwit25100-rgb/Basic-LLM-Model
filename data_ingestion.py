import requests
import xml.etree.ElementTree as ET
import json
import time

class ScientificDataIngestor:
    def __init__(self):
        self.arxiv_url = "http://export.arxiv.org/api/query"
        self.nasa_ntrs_url = "https://ntrs.nasa.gov/api/citations/search"

    def fetch_arxiv_papers(self, category="astro-ph", max_results=10):
        """
        Fetches papers from arXiv based on category. 
        Good categories: 'astro-ph' (Astrophysics), 'quant-ph' (Quantum Physics), 'gr-qc' (General Relativity)
        """
        print(f"Fetching {max_results} papers from arXiv ({category})...")
        
        params = {
            "search_query": f"cat:{category}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        response = requests.get(self.arxiv_url, params=params)
        
        if response.status_code != 200:
            print("Failed to fetch from arXiv")
            return []

        root = ET.fromstring(response.content)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        for entry in root.findall('atom:entry', namespace):
            title = entry.find('atom:title', namespace).text.replace('\n', ' ').strip()
            summary = entry.find('atom:summary', namespace).text.replace('\n', ' ').strip()
            pdf_link = ""
            
            for link in entry.findall('atom:link', namespace):
                if link.attrib.get('title') == 'pdf':
                    pdf_link = link.attrib.get('href')
                    break
                    
            papers.append({
                "source": "arXiv",
                "title": title,
                "abstract": summary,
                "pdf_url": pdf_link
            })
            
        return papers

    def fetch_nasa_reports(self, search_term="orbital mechanics", max_results=10):
        """
        Fetches technical documents from the NASA NTRS API.
        """
        print(f"Fetching {max_results} reports from NASA NTRS for '{search_term}'...")
        
        params = {
            "q": search_term,
            "size": max_results
        }
        
        response = requests.get(self.nasa_ntrs_url, params=params)
        
        if response.status_code != 200:
            print(f"Failed to fetch from NASA NTRS: Status {response.status_code}")
            return []

        data = response.json()
        reports = []
        
        for item in data.get('results', []):
            title = item.get('title', 'No Title')
            abstract = item.get('abstract', 'No Abstract Available')
            
            pdf_link = ""
            downloads = item.get('downloads', [])
            if downloads:
                for dl in downloads:
                    if dl.get('mimetype') == 'application/pdf':
                        pdf_link = dl.get('links', {}).get('pdf', '')
                        if pdf_link and not pdf_link.startswith('http'):
                            pdf_link = f"https://ntrs.nasa.gov{pdf_link}"
                        break

            reports.append({
                "source": "NASA NTRS",
                "title": title,
                "abstract": abstract,
                "pdf_url": pdf_link
            })
            
        return reports

    def save_to_json(self, data, filename="raw_knowledge_base.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved {len(data)} records to {filename}")

if __name__ == "__main__":
    ingestor = ScientificDataIngestor()
    all_data = []

    arxiv_data = ingestor.fetch_arxiv_papers(category="quant-ph", max_results=5)
    all_data.extend(arxiv_data)
    
    time.sleep(15)

    nasa_data = ingestor.fetch_nasa_reports(search_term="black hole event horizon", max_results=5)
    all_data.extend(nasa_data)

    ingestor.save_to_json(all_data)
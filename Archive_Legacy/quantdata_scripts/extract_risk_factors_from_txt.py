
import os
import re
import pandas as pd
import glob

# Constants
INPUT_DIR = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Extracted_Transcripts"
OUTPUT_FILE = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Thesis_Dataset_Master_RiskFactorsOnly.csv"

def parse_filename(filename):
    name = os.path.basename(filename)
    base = os.path.splitext(name)[0]
    
    # Year
    year_match = re.search(r'^(20[0-9]{2}|[0-9]{2})', base)
    if not year_match:
        return None, None, None
    year_str = year_match.group(1)
    year = int("20" + year_str) if len(year_str) == 2 else int(year_str)
        
    # Doc Type
    if "10K" in base or "10-K" in base or "Annual-Filing" in base:
        doc_type = "10-K"
    elif "Annual-Report" in base or "Annual_Report" in base:
        doc_type = "Annual Report"
    else:
        return None, None, None
        
    # Company
    parts = re.split(r'[-_]', base)
    company_parts = []
    for p in parts:
        if p.isdigit() and (len(p)==2 or len(p)==4): continue
        if p.lower() in ['10k', 'annual', 'report', 'filing', 'transcript', 'pdf', 'txt']: continue
        if p == '': continue
        company_parts.append(p)
    company = " ".join(company_parts).strip()
    if "ToS" in company: return None, None, None
    
    if not company:
        return None, None, None
    
    return year, company, doc_type

def extract_risk_factors(text):
    text_lower = text.lower()
    
    # Start Markers
    start_markers = [
        r'item\s+1a\.?', 
        r'item\s+3\.?\s+key\s+information', 
        r'\nrisk\s+factors',                  
        r'^risk\s+factors',                   
        r'risks\s+related\s+to'
    ]
    
    # End Markers
    end_markers = [
        r'item\s+1b\.?',
        r'item\s+2\.?',
        r'item\s+4\.?',
        r'unresolved\s+staff\s+comments',
        r'properties',
        r'legal\s+proceedings',
        r'management[’\']?s\s+discussion',
        r'results\s+of\s+operations',         
        r'quantitative\s+and\s+qualitative',  
        r'financial\s+statements',            
        r'part\s+ii'                          
    ]
    
    # Find all candidates
    starts = []
    for pat in start_markers:
        for m in re.finditer(pat, text, re.IGNORECASE | re.MULTILINE):
            starts.append(m.start())
    starts.sort()
    
    ends = []
    for pat in end_markers:
        for m in re.finditer(pat, text, re.IGNORECASE | re.MULTILINE):
            ends.append(m.start())
    ends.sort()
    
    valid_starts = []
    for s in starts:
        snippet = text[s:s+150]
        if re.search(r'\.{3,}', snippet): 
            continue
        valid_starts.append(s)
            
    if not valid_starts:
        return "", "No valid start found"
        
    best_text = ""
    max_len = 0
    candidates = []
    
    for s in valid_starts:
        e = -1
        for end_pos in ends:
            if end_pos > s + 500: 
                e = end_pos
                break
        
        if e == -1:
            e = min(len(text), s + 100000)
            
        length = e - s
        if length > 1000: 
             candidates.append((s, e, length))
             
    if candidates:
        candidates.sort(key=lambda x: x[2], reverse=True)
        s, e, l = candidates[0]
        return text[s:e], f"Found: {l} chars"
    
    return "", "Candidates too short or logic failed"

def split_sentences(text):
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s', text)
    return [s.strip() for s in sentences if len(s.strip()) > 30]

def main():
    files = glob.glob(os.path.join(INPUT_DIR, "*.txt"))
    all_data = []
    
    print(f"Found {len(files)} files.")
    
    processed_count = 0
    success_count = 0
    
    for f in files:
        year, company, doc_type = parse_filename(f)
        if not year or not company: continue
        
        processed_count += 1
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
            
            rf_text, msg = extract_risk_factors(text)
            if rf_text:
                success_count += 1
                sents = split_sentences(rf_text)
                for s in sents:
                    all_data.append({
                        'Year': year, 
                        'Company': company, 
                        'Doc_Type': doc_type, 
                        'Sentence': s
                    })
        except Exception as e:
            print(f"Error {f}: {e}")
            
    print(f"Processed {processed_count} files. Extracted data for {success_count} files.")
    
    if all_data:
        df = pd.DataFrame(all_data)
        df = df.sort_values(by=['Company', 'Year'])
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Saved {len(df)} sentences to {OUTPUT_FILE}")
    else:
        print("No data extracted.")

if __name__ == "__main__":
    main()

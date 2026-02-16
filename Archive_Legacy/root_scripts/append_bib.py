
import os

def append_salary_bib():
    extra_path = r"Latex Thesis\updated_extra_bib.bib"
    bib_path = r"Latex Thesis\Bibliography.bib"
    
    if os.path.exists(extra_path) and os.path.exists(bib_path):
        with open(extra_path, 'r', encoding='utf-8') as f:
            new_bibs = f.read()
            
        with open(bib_path, 'a', encoding='utf-8') as f:
            f.write("\n" + new_bibs)
            
        print("Success: Appended salary citations to Bibliography.bib")
    else:
        print("Error: Bib files not found")

if __name__ == "__main__":
    append_salary_bib()

import xml.etree.ElementTree as ET
import json
import re
from bs4 import BeautifulSoup

# STEP 1: PARSE AND CLEAN THE RAW XML DATA

def convert_medline_xml_to_jsonl(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    dataset = []

    for topic in root.findall('health-topic'):
        language = topic.get('language', 'English')
        url = topic.get('url', '')

        # Filter: Keep English topics only, excluding Spanish endpoints
        if language.lower() != 'english' or '/spanish/' in url or '/es/' in url:
            continue

        title = topic.get('title')
        also_called = [ac.text for ac in topic.findall('also-called') if ac.text]
        summary_element = topic.find('full-summary')
        text_content = ""

        if summary_element is not None and summary_element.text:
            soup = BeautifulSoup(summary_element.text, "html.parser")
            text_content = soup.get_text(separator=" ", strip=True)

        record = {
            "title": title,
            "url": url,
            "also_called": also_called,
            "text": text_content
        }
        dataset.append(record)

    return dataset

# STEP 2: FEATURE ENGINEERING FUNCTIONS

def extract_red_flags(text):
    red_flags = []
    warning_keywords = [
        r"(get medical help immediately if[^•\.]*)",
        r"(call your provider if[^•\.]*)",
        r"(call 911 if[^•\.]*)",
        r"(seek emergency care[^•\.]*)",
        r"(medical help immediately if[^•\.]*)"
    ]
    for pattern in warning_keywords:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            cleaned = match.strip().rstrip(',').rstrip('.')
            if cleaned not in red_flags:
                red_flags.append(cleaned)
                
    if "immediately if" in text.lower() or "right away if" in text.lower():
        parts = re.split(r"immediately if:|right away if:", text, flags=re.IGNORECASE)
        if len(parts) > 1:
            sub_text = parts[1].split('.')[0]
            red_flags.append(f"Immediate attention required for: {sub_text.strip()}")
            
    return list(set(red_flags))

def structure_numeric_thresholds(text):
    thresholds = []
    percentage_patterns = re.findall(r"([A-Za-z0-9\s_-]+ is (?:below|between|above|over)\s?\d+\.?\d*\%?[\sto\s\d+\.?\d*\%?]*)", text, re.IGNORECASE)
    for match in percentage_patterns:
        thresholds.append(match.strip())
        
    level_patterns = re.findall(r"(normal level is [^\.]*|abnormal level is [^\.]*|test result is [^\.]*)", text, re.IGNORECASE)
    for match in level_patterns:
        thresholds.append(match.strip())
        
    return thresholds

def map_clinical_metadata(title, text):
    text_lower = text.lower()
    title_lower = title.lower()
    specialty = "General Medicine"
    icd10_chapter = "Unknown / Multi-system"
    body_system = "General / Multi-system"
    
    if any(x in title_lower or x in text_lower for x in ["diabet", "insulin", "thyroid", "hormone", "a1c"]):
        specialty = "Endocrinology"
        icd10_chapter = "Chapter IV: Endocrine, nutritional and metabolic diseases (E00-E89)"
        body_system = "Endocrine System"
    elif any(x in title_lower or x in text_lower for x in ["heart", "cardio", "blood pressure", "hypertension", "artery"]):
        specialty = "Cardiology"
        icd10_chapter = "Chapter IX: Diseases of the circulatory system (I00-I99)"
        body_system = "Cardiovascular System"
    elif any(x in title_lower or x in text_lower for x in ["abdominal", "stomach", "colon", "bowel", "liver", "gastric"]):
        specialty = "Gastroenterology"
        icd10_chapter = "Chapter XI: Diseases of the digestive system (K00-K95)"
        body_system = "Digestive System"
    elif any(x in title_lower or x in text_lower for x in ["lung", "asthma", "bronch", "respiratory", "breath"]):
        specialty = "Pulmonology"
        icd10_chapter = "Chapter X: Diseases of the respiratory system (J00-J99)"
        body_system = "Respiratory System"
    elif any(x in title_lower or x in text_lower for x in ["skin", "dermatitis", "acne", "rash"]):
        specialty = "Dermatology"
        icd10_chapter = "Chapter XII: Diseases of the skin and subcutaneous tissue (L00-L99)"
        body_system = "Integumentary System (Skin)"
    elif any(x in title_lower or x in text_lower for x in ["kidney", "renal", "urinary", "bladder"]):
        specialty = "Nephrology / Urology"
        icd10_chapter = "Chapter XIV: Diseases of the genitourinary system (N00-N99)"
        body_system = "Urinary System"
        
    return {"specialty": specialty, "icd10_chapter": icd10_chapter, "body_system": body_system}

def segment_text_sections(text):
    sentences = re.split(r'(?<=[\.\?\!])\s+', text)
    definition = ""
    symptoms = []
    treatments = []
    general_info = []

    if len(sentences) > 0:
        definition = sentences[0]
        if len(sentences) > 1 and any(x in sentences[1].lower() for x in ["is a", "occurs when", "refers to"]):
            definition += " " + sentences[1]
            sentences = sentences[2:]
        else:
            sentences = sentences[1:]
            
    for sentence in sentences:
        sent_lower = sentence.lower()
        if any(x in sent_lower for x in ["symptom", "pain", "signs of", "feel like", "hurt"]):
            symptoms.append(sentence)
        elif any(x in sent_lower for x in ["treatment", "cure", "therapy", "prevent", "avoid", "drug", "medicine"]):
            treatments.append(sentence)
        else:
            general_info.append(sentence)
            
    return {
        "definition": definition.strip(),
        "symptoms": " ".join(symptoms).strip() if symptoms else None,
        "treatments_and_prevention": " ".join(treatments).strip() if treatments else None,
        "general_info": " ".join(general_info).strip() if general_info else None
    }

# STEP 3: PIPELINE EXECUTION

# Run the pipeline from original raw XML
xml_file_path = 'paste your file path here' # current dataset version: mplus_topics_2026-10-10.xml
print(f"Parsing data from {xml_file_path}...")
raw_records = convert_medline_xml_to_jsonl(xml_file_path)

enriched_data = []
for record in raw_records:
    text = record['text']
    segmented = segment_text_sections(text)
    red_flags = extract_red_flags(text)
    thresholds = structure_numeric_thresholds(text)
    meta = map_clinical_metadata(record['title'], text)
    
    enriched_data.append({
        "title": record['title'],
        "url": record['url'],
        "also_called": record['also_called'],
        "clinical_metadata": meta,
        "segmented_fields": segmented,
        "red_flags": red_flags if red_flags else None,
        "structured_thresholds": thresholds if thresholds else None,
        "raw_text": text
    })

# Save structured file
output_filename = 'telemed_dataset.jsonl' #name your dataset here
with open(output_filename, 'w', encoding='utf-8') as outfile:
    for rec in enriched_data:
        outfile.write(json.dumps(rec) + '\n')

print(f"Successfully generated enriched dataset with {len(enriched_data)} entries in {output_filename}!")

# Data Scraper for Texas State University NOT WORKING
import json
from bs4 import BeautifulSoup
import requests
import re
import time

# Define URLs and patterns
base_url = "https://www.txst.edu"
urls = {
    "admissions": "https://www.admissions.txst.edu/",
    "financial_aid": "https://www.finaid.txst.edu/",
    "campus_life": "https://www.txst.edu/student-life.html"
}

# Updated questions list
admission_questions = [
    "What is the application deadline for first-year students?",
    "Are SAT or ACT scores required for undergraduate admission?",
    # ... add all 25 questions here ...
]

# Updated patterns to match specific information
patterns = {
    "deadlines": re.compile(r"(deadline|due date|close date)", re.I),
    "test_scores": re.compile(r"(SAT|ACT|test scores?|standardized tests?)", re.I),
    "requirements": re.compile(r"(admission requirements?|required|prerequisites?)", re.I),
    "application": re.compile(r"(application|apply|submit|process)", re.I),
    "transcripts": re.compile(r"(transcript|academic record|school record)", re.I),
    "international": re.compile(r"(international|foreign|TOEFL|IELTS)", re.I),
    "transfer": re.compile(r"(transfer|previous college|other institution)", re.I),
    "financial": re.compile(r"(\$|financial aid|scholarships|cost)", re.I),
    "housing": re.compile(r"(housing|dorm|residence hall|living on campus)", re.I),
    "student_life": re.compile(r"(student life|campus life|activities|organizations)", re.I)
}

# Fetch and parse page content with error handling
def fetch_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Improved content extraction function
def extract_info(soup, pattern):
    text_matches = []
    # Look for content in more specific tags and with more context
    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li', 'div.content', 'div.info']):
        text = tag.get_text(strip=True)
        if pattern.search(text):
            # Enhanced filtering for more meaningful content
            if (len(text) > 20 and  # Longer content is more likely to be meaningful
                len(text) < 500 and  # But not too long
                not any(x in text.lower() for x in ['javascript', 'undefined', '{', '}'])):
                text_matches.append(text)
    return text_matches

# Scrape each section and organize data into JSON format
def scrape_sections(urls, patterns, questions):
    all_data = [{"role": "system", "content": "You are an assistant providing information about Texas State University admissions, financial aid, and campus life."}]
    
    for question in questions:
        all_data.append({"role": "user", "content": question})
        
        # Find relevant information for each question
        found_answer = False
        for section, url in urls.items():
            soup = fetch_content(url)
            if soup:
                for pattern_key, pattern in patterns.items():
                    if any(keyword in question.lower() for keyword in pattern_key.split('_')):
                        extracted_text = extract_info(soup, pattern)
                        if extracted_text:
                            # Take the most relevant answer (first match)
                            all_data.append({
                                "role": "assistant",
                                "content": extracted_text[0]
                            })
                            found_answer = True
                            break
            if found_answer:
                break
                
        # If no specific answer found, add a placeholder
        if not found_answer:
            all_data.append({
                "role": "assistant",
                "content": "This information is not directly available on the website. Please contact the admissions office for details."
            })
        
        time.sleep(1)  # Respect rate limiting
    
    return all_data

# Run scraping with the specific questions
scraped_data = scrape_sections(urls, patterns, admission_questions)

# Save to JSON file
with open("texas_state_university_faq.json", "w", encoding="utf-8") as f:
    json.dump(scraped_data, f, ensure_ascii=False, indent=2)

print("Data has been saved to texas_state_university_faq.json.")

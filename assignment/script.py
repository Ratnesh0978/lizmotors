import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import requests

def save_links_to_file(links, filename):
    with open(filename, 'w') as f:
        for query, link_list in links.items():
            f.write(f"{query}\n")
            for link in link_list:
                f.write(f"{link}\n")

def read_links_from_file(filename):
    links = {}
    with open(filename, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            query = lines[i].strip()
            i += 1
            link_list = []
            while i < len(lines) and lines[i].strip():
                link_list.append(lines[i].strip())
                i += 1
            links[query] = link_list
            i += 1
    return links

def scrape_data_from_links(links):
    scraped_data = {}
    for query, link_list in links.items():
        for link in link_list:
            driver.get(link)
            time.sleep(5)  
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            # Extract relevant data using BeautifulSoup, modify as needed
            extracted_data = {'p_tags': [p.text.strip() for p in soup.find_all('p')],
                              'span_tags': [span.text.strip() for span in soup.find_all('span')]}
            scraped_data[link] = extracted_data
    return scraped_data

def gemini_api_call(text):
    # Replace this with actual Gemini API integration
    # You'll need to set up and use the actual Gemini API key and endpoint
    gemini_api_endpoint = 'https://your-gemini-api-endpoint.com'
    gemini_api_key = 'your-api-key'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {gemini_api_key}'}
    data = {'text': text}
    response = requests.post(gemini_api_endpoint, headers=headers, json=data)
    return response.json()

def process_and_store_data(links, scraped_data, output_csv):
    with open(output_csv, 'w') as csv_file:
        csv_file.write("Query/Topic,URL,Information\n")
        for query, link_list in links.items():
            for link in link_list:
                data = scraped_data[link]
                information_json = json.dumps({'p_tags': data['p_tags'], 'span_tags': data['span_tags']})
                csv_file.write(f'"{query}","{link}","{information_json}"\n')

if __name__ == "__main__":
    # Replace 'path/to/chromedriver' with the actual path to your chromedriver executable
    driver_path = 'path/to/chromedriver'
    
    queries = [
        "Identify the industry in which Canoo operates, along with its size, growth rate, trends, and key players",
        "Analyze Canoo's main competitors, including their market share, products or services offered, pricing strategies, and marketing efforts",
        "Identify key trends in the market, including changes in consumer behavior, technological advancements, and shifts in the competitive landscape",
        "Gather information on Canoo's financial performance, including its revenue, profit margins, return on investment, and expense structure"
    ]

    # Step 1: Use DuckDuckGo API to get links
    links = {}
    for query in queries:
        search = DDGS()
        results = search.text(keywords=query, max_results=10)
        links[query] = [result['href'] for result in results]

    save_links_to_file(links, 'web_links.txt')

    # Step 2: Read links from the file
    read_links = read_links_from_file('web_links.txt')

    # Step 3: Scrape data from the links
    chrome_options = Options()
    chrome_options.add_argument('--headless')  
    service = ChromeService(executable_path=driver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)

    scraped_data = scrape_data_from_links(read_links)

    driver.quit()

    # Step 4: Process and store the data in CSV
    process_and_store_data(read_links, scraped_data, 'output_data.csv')

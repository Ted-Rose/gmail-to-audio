# # from django.shortcuts import render


# def home(request):
#     return render(request, 'home.html')
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from time import sleep
from datetime import datetime, timedelta
import random


def random_sleep(min_seconds=1, max_seconds=3):
    """Sleeps for a random amount of time between min_seconds and max_seconds."""
    sleep_time = random.randint(min_seconds, max_seconds)
    sleep(sleep_time)


def get_ratings(query, content_type=None):
    # Encode the query with UTF-8 encoding and spaces replaced with '+'
    encoded_query = quote_plus(query, encoding='utf-8')

    filter = "?s=tt" if content_type == "movie" else ""
    url = f"https://www.imdb.com/find/{filter}?q={encoded_query}&ref_=nv_sr_sm"
    # The user_agent is required to prevent 403 errors
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6446.75 Safari/537.36"
    headers = {"User-Agent": user_agent}
    random_sleep()
    response = requests.get(url, headers=headers)

    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    summary = soup.find('div', class_="ipc-metadata-list-summary-item__tc")
    if summary is None:
        print("Summary not found")
        return

    link_element = summary.find('a')

    if link_element:
        link = "https://www.imdb.com/" + link_element['href']
    else:
        print("Link not found")
        return

    random_sleep()
    response = requests.get(link, headers=headers)

    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    script_tags = soup.find_all('script', type='application/ld+json')
    if script_tags:
        script_tag = script_tags[0]
        json_data = script_tag.string
        if json_data:
            parsed_data = json.loads(json_data)

    return {
        "type": parsed_data.get("@type"),
        "description": parsed_data.get("description"),
        "image": parsed_data.get("image"),
        "url": parsed_data.get("url"),
        "content_rating": parsed_data.get("contentRating"),
        "rating_value": parsed_data.get("aggregateRating", {}).get("ratingValue")
    }


def fetch_tv_program_details():
    # Oldest available date to fetch data
    oldest_date = (datetime.now() - timedelta(days=8))
    # Data is available for span of 16 days
    for day in range(16):
        date = (oldest_date + timedelta(days=day)).strftime('%d-%m-%Y')
        url = f"https://www.tet.lv/televizija/tv-programma?tv-type=interactive&view-type=list&date={date}&channel=tv6_hd"
        print("url:", url)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching program details: {e}")
            return []

        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        program_elements = soup.find_all('div', class_="expander-description")

        programs = []
        for program in program_elements:
            program_data = {}

            title_element = program.find('div', class_="tet-font__headline--s")
            if title_element:
                program_data['title'] = title_element.text.strip()

            subtitle_element = program.find('div', class_="subtitle")
            if subtitle_element:
                subtitle_text = subtitle_element.text.strip()
                subtitle_parts = subtitle_text.split('\n')
                program_data['time'] = subtitle_parts[0].strip()
                program_data['date'] = subtitle_parts[1].strip()
                program_data['channel'] = subtitle_parts[2].strip()

            description_element = program.find('div', class_="text tet-font__body--s")
            if description_element:
                program_data['description'] = description_element.text.strip()

            image_element = program.find('img')
            if image_element:
                program_data['image_url'] = image_element['src']
            print("-" * 20)
            print("title:", program_data['title'])
            ratings = get_ratings(program_data['title'], 'tv')
            if ratings:
                print(f"IMDb Data for {program_data['title']}:")
                print("Type:", ratings["type"])
                print("Description:", ratings["description"])
                print("Image:", ratings["image"])
                print("URL:", ratings["url"])
                print("Content Rating:", ratings["content_rating"])
                print("Rating Value:", ratings["rating_value"])
            else:
                print(f"No data found for {program_data['title']}")

            programs.append(program_data)

    return programs

programs = fetch_tv_program_details()
# print("programs:", programs)

for program in programs:
    print(f"Title: {program.get('title')}")
    print(f"Time: {program.get('time')}")
    print(f"Date: {program.get('date')}")
    print(f"Channel: {program.get('channel')}")
    print(f"Description: {program.get('description')}")
    print(f"Image URL: {program.get('image_url')}")
    print("-" * 20)
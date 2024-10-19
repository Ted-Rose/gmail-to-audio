# # from django.shortcuts import render


# def home(request):
#     return render(request, 'home.html')
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


def get_ratings(query, content_type=None):
    # Encode the query with UTF-8 encoding and spaces replaced with '+'
    encoded_query = quote_plus(query, encoding='utf-8')

    filter = "?s=tt" if content_type == "movie" else ""
    url = f"https://www.imdb.com/find/{filter}?q={encoded_query}&ref_=nv_sr_sm"
    # The user_agent is required to prevent 403 errors
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6446.75 Safari/537.36"
    headers = {"User-Agent": user_agent}
    response = requests.get(url, headers=headers)

    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    link_element = soup.find('div', class_="ipc-metadata-list-summary-item__tc").find('a')

    if link_element:
        link = "https://www.imdb.com/" + link_element['href']
        print("First link:", link)
    else:
        print("Link not found")
        return

    response = requests.get(link, headers=headers)

    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    script_tags = soup.find_all('script', type='application/ld+json')
    if script_tags:
        script_tag = script_tags[0]
        json_data = script_tag.string
        if json_data:
            parsed_data = json.loads(json_data)

            type = parsed_data.get("@type")
            description = parsed_data.get("description")
            image = parsed_data.get("image")
            url = parsed_data.get("url")
            content_rating = parsed_data.get("contentRating")
            rating_value = parsed_data.get("aggregateRating", {}).get("ratingValue")

            print("type:", type)
            print("Description:", description)
            print("Image:", image)
            print("URL:", url)
            print("Content Rating:", content_rating)
            print("Rating Value:", rating_value)

    return


def fetch_tv_program_details(url):
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
        print("title:", program_data['title'])
        get_ratings(program_data['title'], 'tv')
        return program_data
        programs.append(program_data)

    return programs

url = "https://www.tet.lv/televizija/tv-programma?tv-type=interactive&view-type=list&date=13-10-2024&channel=tv6_hd"
programs = fetch_tv_program_details(url)
print("programs:", programs)

for program in programs:
    print(f"Title: {program.get('title')}")
    print(f"Time: {program.get('time')}")
    print(f"Date: {program.get('date')}")
    print(f"Channel: {program.get('channel')}")
    print(f"Description: {program.get('description')}")
    print(f"Image URL: {program.get('image_url')}")
    print("-" * 20)
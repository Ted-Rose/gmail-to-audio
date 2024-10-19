# # from django.shortcuts import render


# def home(request):
#     return render(request, 'home.html')

import requests
from bs4 import BeautifulSoup


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
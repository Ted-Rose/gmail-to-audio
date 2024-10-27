from django.shortcuts import render
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from time import sleep
from datetime import datetime, timedelta
import random
from .models import Content
import re
from googletrans import Translator
from difflib import SequenceMatcher
import logging


logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'home.html')


def random_sleep(min_seconds=1, max_seconds=2):
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
        return None

    link_element = summary.find('a')
    if link_element:
        link = "https://www.imdb.com/" + link_element['href']
    else:
        print("Link not found")
        return None

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
            description = parsed_data.get("description")
            if description:
                description = re.sub(r"&\w+;", "", parsed_data.get("description"))
            else:
                description = ""

            content_script_tags = soup.find_all('script', type='application/ld+json')
            content_script_tag = content_script_tags[0]
            content_json_data = content_script_tag.string
            content_parsed_data = json.loads(content_json_data)
            content_name = content_parsed_data.get("name")
            return {
                "name": content_name,
                "type": parsed_data.get("@type"),
                "description": description,
                "image": parsed_data.get("image"),
                "url": parsed_data.get("url"),
                "content_rating": parsed_data.get("contentRating"),
                "rating_value": parsed_data.get("aggregateRating", {}).get("ratingValue")
            }
    return None

def fetch_tv_program_details():
  
    translator = Translator()

    channels = {
        "viasat_kino": "viasat_kino",
        "tv6_hd": "tv6_hd",
        "tv3_hd": "tv3_hd",
        "8tv_hd": "8tv_hd",
        "ltv1_hd": "ltv1_hd",
        "ltv7_hd": "ltv7_hd",
        }
    # Oldest available date to fetch data
    oldest_date = (datetime.now() - timedelta(days=6))

    for channel in channels:
      # Data is available for a span of 14 days
      for day in range(14):
          date = (oldest_date + timedelta(days=day)).strftime('%d-%m-%Y')
          logger.info(f"Date: {date}")

          url = f"https://www.tet.lv/televizija/tv-programma?tv-type=interactive&view-type=list&date={date}&channel={channel}]"
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

              title_lv = program.find('div', class_="tet-font__headline--s")
              title_lv = title_lv.text.strip()

              # if title_lv != "Emī un Rū. 4. sezona":
              #   continue             

              description_lv = program.find('div', class_="text tet-font__body--s")
              if description_lv:
                  description_lv = re.sub(r"&\w+;", "", description_lv.text.strip())

              print("-" * 20)
              print("title:", title_lv)
              ratings = get_ratings(title_lv, 'tv')
              if ratings:
                  if description_lv is None:
                      text_lv = title_lv
                      text_eng = ratings["name"]
                  else:
                    text_lv = description_lv
                    text_eng = ratings["description"]
                  text_lv_to_eng = translator.translate(
                      text_lv,
                      src='lv',
                      dest='en'
                  ).text
                  print(f"text_lv: {text_lv}")
                  print(f"text_eng: {text_eng}")
                  logger.info(f"text_lv: {text_lv}")
                  logger.info(f"text_lv: {text_eng}")
                  ratio = SequenceMatcher(None, text_eng, text_lv_to_eng).ratio()
                  logger.info(f"ratio: {ratio}")
                  print(f"ratio: {ratio}")
                  print("ratio: ", ratio)
                  print(f"IMDb Data for {title_lv}:")
                  print("translated_description_lv:\n", text_lv_to_eng)
                  print("Description ENG:", ratings["description"])

                  print("Type:", ratings["type"])
                  print("Image:", ratings["image"])
                  print("URL:", ratings["url"])
                  print("Content Rating:", ratings["content_rating"])
                  print("Rating Value:", ratings["rating_value"])

                  # Get image URL
                  image_element = program.find('img')
                  image_url = image_element['src'] if image_element else None
                  image_url = image_url or ratings.get("image")
                  image_url = image_url if image_url is not None else None

                  Content.objects.update_or_create(
                      title=title_lv,
                      defaults={
                          'type': ratings.get("type", ""),
                          'description_lv': description_lv,
                          'description_eng': ratings["description"],
                          'image': ratings.get("image", ""),
                          'url': image_url,
                          'content_rating': ratings.get("content_rating", ""),
                          'rating_value': ratings.get("rating_value", None),
                          'start_date': date.strftime('%Y-%m-%d'),
                          'channel': channel,
                          'ratio': ratio
                      }
                  )
              else:
                  print(f"No data found for {title_lv}")
    return programs

# programs = fetch_tv_program_details()

import requests
from requests.compat import quote_plus
from django.shortcuts import render
from bs4 import BeautifulSoup
from . import models

BASE_WIKI_URL = 'https://pl.wikipedia.org/w/index.php?search={}'
# Create your views here.
def home(request):
    return render(request, 'base.html')

def new_search(request):
    search = request.POST.get('search')
    models.Search.objects.create(search=search)
    mid_url = BASE_WIKI_URL.format(quote_plus(search))
    final_url = mid_url + '&title=Specjalna:Szukaj&profile=advanced&fulltext=1&ns0=1'
    response = requests.get(final_url)
    data = response.text
    soup = BeautifulSoup(data, features='html.parser')
    post_listings = soup.find_all('li', {'class': 'mw-search-result'})

    final_postings = []
    for post in post_listings:
        mid_url = post.find('a').get('href')
        post_url = 'https://pl.wikipedia.org' + mid_url
        post_title = post.find(class_='mw-search-result-heading').text

        image_response =  requests.get(post_url)
        image_data = image_response.text
        image_soup = BeautifulSoup(image_data, features='html.parser')
        if image_soup.find_all('a', {'class': 'image'}):
            image_data_url = 'https://pl.wikipedia.org' + image_soup.find('a', {'class': 'image'}).get('href')
            image_image_response =  requests.get(image_data_url)
            image_image_data = image_image_response.text
            image_image_soup = BeautifulSoup(image_image_data, features='html.parser')
            image_url = image_image_soup.find('div', {'class': 'fullImageLink'}).find('a').get('href')
        else:
            image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Flag_of_None_%28square%29.svg/768px-Flag_of_None_%28square%29.svg.png'
        
        final_postings.append((post_title, post_url, image_url))

    stuff_for_frontend = {
        'search': search,
        'final_postings': final_postings,
    }
    return render(request, 'my_app/new_search.html', stuff_for_frontend)
from bs4 import BeautifulSoup
import requests
from django.core.files import File
from io import BytesIO
from post.models import Post, PostImages
from category.models import Category
import uuid
import time
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_unique_image_name():
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4().hex)
    image_name = f"image{timestamp}_{unique_id}.jpg"
    return image_name


URL = 'https://www.tripadvisor.com/'


def get_html(url):
    headers = {
        'authority': 'www.tripadvisor.com',
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.tripadvisor.com',
        'referer': 'https://www.tripadvisor.com/Attraction_Products-g293948-t12035-zfg12022-Bishkek.html',
        'sec-ch-device-memory': '8',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-full-version-list': '"Not.A/Brand";v="8.0.0.0", "Chromium";v="114.0.5735.199", "YaBrowser";v="23.7.0.2564"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 YaBrowser/23.7.0.2564 Yowser/2.5 Safari/537.36',
        'x-requested-by': 'e8cb71464a38b1ebbbe4c3d2151ad2e465819a1bbe273ad897b0f0b35ed0aa05',
    }
    response = requests.get(url, headers=headers)
    print(response.status_code)
    return response.text

def get_data(html):
    soup = BeautifulSoup(html, 'lxml')
    dates = []
    list_cat = soup.find_all('div', class_='NXAUb _T')
    for cat in list_cat:
        link = 'https://www.tripadvisor.com' + cat.find('div', class_='jsTLT K').find('a').get('href')
        print(link)
        sop = BeautifulSoup(get_html(link), 'lxml')
        post_data = []
        image_elements = sop.find('div', class_='dFaUm carousel').find('ul', class_='LgMtS').find_all('li')
        img_urls = []
        for img_element in image_elements:
            img_tag = img_element.find('picture')
            if img_tag:
                img_url = img_tag.find('img').get('src')
                img_urls.append(img_url)
        preview = img_urls[0]
        title = sop.find('div', class_='f u').find('h1').text
        description = sop.find('div', class_='fIrGe _T').text
        try:
            price = sop.find('div', class_='XQgaU').find('div', class_='fOGdO f').find('div', class_='gbXAQ').text
            float_value = float(''.join([i for i in price if i.isdigit()]))
        except:
            float_value = None
        post_data.append({'title': title, 'description': description, 'price': float_value, 'preview': preview,
                          'image_urls': img_urls})
        print(post_data)
        dates.append(post_data)

    for data in dates:
        category_name = 'Hotels'  # Название категории
        category = Category.objects.get(name=category_name)
        for i in data:
            try:
                headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 YaBrowser/23.7.0.2564 Yowser/2.5 Safari/537.36'}
                preview_response = requests.get(i['preview'], headers=headers)
                preview_name = generate_unique_image_name()
                prw_io = BytesIO(preview_response.content)
                post = Post.objects.create(title=i['title'], body=i['description'], price=i['price'],
                                           category=category, owner=User.objects.first(), preview=None)
                if preview_name and prw_io:
                    post.preview.save(preview_name, File(prw_io))
                for image_url in i['image_urls']:
                    image_response = requests.get(image_url, headers=headers)
                    img_name = generate_unique_image_name()
                    img_io = BytesIO(image_response.content)
                    post_image = PostImages(post=post)
                    post_image.image.save(img_name, File(img_io))
                    post_image.save()
            except:
                pass


def run():
    for i in range(3):
        count = i * 30
        suffix = f"-o{count}" if count > 0 else ""
        new_url = f'https://www.tripadvisor.com/Hotels-g293948-oa{suffix}-a_trating.40-a_ufe.true-Bishkek-Hotels.html'
        print(new_url)
        get_data(get_html(new_url))




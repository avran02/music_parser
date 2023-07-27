from bs4 import BeautifulSoup as bs
import aiohttp
import asyncio
import random
import aiofiles
import requests


class Parser:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    }
    ROOT_URL='https://rus.mp3xa.me/'
    

    def __init__(self):
        self.page = None
        self.num_songs = None
        self.num_pages = None
        self.download_pages_links = None
        self.genres = None
        self.genre = None
        print('-Ищу, в каких жанрах есть музыка...')
        self._parce_genres()

    def get_pages_list(self, genre):
        self.genre = genre[1:]
        self.page = self._get_page_html(f'{self.ROOT_URL}{self.genre}')
        self.num_pages = self._get_num_pages(self.page)

    def parce_random(self, num_songs):
    	self.num_songs = num_songs
    	print('-Ищу музыку по этому жанру..)')
    	random_page = self._get_page_html(f'{self.ROOT_URL}{self.genre}page/{random.randint(1, num_songs)}')
    	self._parce(random_page)

    def parce_any(self, num_songs, page):
    	self.num_songs = num_songs
    	print('-Ищу музыку по этому жанру..)')
    	page_doc = self._get_page_html(f'{self.ROOT_URL}page/{page}') # todo: Переименовать переменные
    	self._parce(page_doc)

    def _parce_genres(self):
        page = self._get_page_html(f'{self.ROOT_URL}genres.html')
        section = page.find('div', class_='content card song_year').find('div', class_='cat_wrap')
        genre_cards = section.find_all('div', class_='cat_item big')
        genres = dict()
        for card in genre_cards:
            link = card.find('a')['href']
            name = card.find('span').text
            genres[name] = link
        self.genres = genres

    def _parce(self, url):
    	songs = url.find('div', class_='songs-wrap').find_all('div', class_='plyr-item')
    	self.download_pages_links = list()
    	count = 0
    	for song_wrap in songs:
    	    if count == self.num_songs:
    	        break
    	    count += 1
    	    name = song_wrap.find('div', class_='song_name').text.strip()
    	    link = song_wrap.find('a', class_='download_btn')['href']
    	    self.download_pages_links.append({'name': name, 'link': link})
    	asyncio.run(self._gather_files())

    async def _get_download_link(self, session, url):
        async with session.get(url) as response:
            if response.status == 200:
                page = await response.text()
                soup = bs(page, 'lxml')
                download_link = soup.find('a', class_='download_btn')['href']
                return download_link
            else:
                print(f"-Не удалось получить ссылку на загрузку с URL: {url}, Ответ сервера: {response.status}")
                return None

    async def _download_file(self, session, url, filename):
        print(f"-Начинаю загрузку файла '{filename}'")
        async with session.get(url) as response:
            if response.status == 200:
                async with aiofiles.open(f'downloads/{filename}', 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        await file.write(chunk)
                print(f"-Файл '{filename}' успешно скачан.")
            else:
                print(f"-Не удалось скачать файл с URL: {url}")

    async def _gather_files(self):
        print('-Собираю url адреса для загрузки')
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            tasks = []
            max_concurrent_requests = 5
            for index, link_info in enumerate(self.download_pages_links, start=1):
                name = link_info['name']
                filename = f"{name}.mp3"
                download_page = f"https://rus.mp3xa.me{link_info['link']}"
                download_link = await self._get_download_link(session, download_page)
                if download_link:
                    task = self._download_file(session, download_link, filename)
                    tasks.append(task)
                if len(tasks) >= max_concurrent_requests:
                    await asyncio.gather(*tasks)
                    tasks = []
            if tasks:
                await asyncio.gather(*tasks)

    def _get_page_html(self, url):
        response = requests.get(url, headers=self.HEADERS)
        if response.status_code == 200:
            page = bs(response.text, 'lxml')
            return page
        else:
            print(f'-Сервер вернул ответ {response.status_code}')
            return

    def _get_num_pages(self, doc):
        pages = doc.find('section', class_='popular full').find('div', class_='paginator').find_all('li')
        num_pages = int(pages[-2].find('a').text)
        return num_pages

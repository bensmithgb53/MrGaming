import requests
from bs4 import BeautifulSoup
import json

class FmovieProvider:
    def __init__(self):
        self.main_url = "https://www1.fmovie.ws"

    def get_main_page(self):
        response = requests.get(f"{self.main_url}/")
        soup = BeautifulSoup(response.content, 'html.parser')

        sections = {
            "Movies": "div#movie-section .item",
            "TV Shows": "div#tv-section .item",
            "Trending": "div#trending-section .item",
            "Latest Movies": "div#latest-movies .item",
            "Latest TV Shows": "div#latest-tv .item"
        }

        all_items = []

        for name, element in sections.items():
            items = soup.select(element)
            for item in items:
                title = item.select_one("h3 a").text.strip()
                link = self.fix_url(item.select_one("h3 a")['href'])
                image = item.select_one("a img")['src']
                quality_info = item.select_one(".quality").text.strip() if item.select_one(".quality") else "N/A"
                quality = self.get_quality_from_string(quality_info)

                all_items.append({
                    'title': title,
                    'link': link,
                    'image': image,
                    'quality': quality,
                    'type': 'Movie' if '/movie/' in link else 'TV Series'
                })

        return all_items

    def get_quality_from_string(self, quality_string):
        return quality_string.strip()

    def fix_url(self, url):
        if url.startswith('/'):
            return self.main_url + url
        return url

    def load_video_links(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        movie_id = soup.select_one("div#watch")['data-id']
        vrf_url = f"{self.main_url}/ajax/film/servers?id={movie_id}"

        # Get server information
        servers_response = requests.get(vrf_url)
        servers_data = json.loads(servers_response.text)

        if 'html' not in servers_data:
            print(f"No video servers found for {url}")
            return []

        soup_servers = BeautifulSoup(servers_data['html'], 'html.parser')
        links = []

        for server in soup_servers.select("div.episode a"):
            server_id = server['data-ep']
            server_response = requests.get(f"{self.main_url}/ajax/episode/info?id={server_id}")
            server_info = json.loads(server_response.text)
            if 'url' in server_info:
                decoded_url = server_info['url']  # Add your decoding logic if needed
                links.append(decoded_url)

        return links

    def save_to_m3u8(self, items):
        with open("new.m3u8", "w") as f:  # Changed output file to new.m3u8
            for item in items:
                f.write(f"#EXTINF:-1,{item['title']}\n")
                f.write(f"{item['link']}\n")

if __name__ == "__main__":
    provider = FmovieProvider()
    all_items = provider.get_main_page()

    all_video_links = []
    for item in all_items:
        video_links = provider.load_video_links(item['link'])
        for link in video_links:
            all_video_links.append({'title': item['title'], 'link': link})

    provider.save_to_m3u8(all_video_links)
    print("Saved video links to new.m3u8")

import requests
from bs4 import BeautifulSoup
import re

def scrape_1hd():
    base_url = 'https://1hd.sh/movies/'
    response = requests.get(base_url)

    if response.status_code != 200:
        print("Failed to fetch the main movie page.")
        return

    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Prepare to collect movie data
    movies_data = []

    # Find all movie links
    movie_links = soup.find_all('a', class_='film-mask')

    for link in movie_links:
        movie_url = link['href']  # Get the movie link

        # Visit the movie page to extract the title and thumbnail
        movie_page_response = requests.get(movie_url)
        if movie_page_response.status_code == 200:
            movie_page_content = movie_page_response.text
            movie_page_soup = BeautifulSoup(movie_page_content, 'html.parser')

            # Extract the movie title from <h2 class="heading-xl">
            title_element = movie_page_soup.find('h2', class_='heading-xl')
            if title_element:
                movie_title = title_element.text.strip()
            else:
                print(f"Title element not found for {movie_url}.")
                continue  # Skip this movie if no title is found

            # Extract the thumbnail image
            thumbnail_img = movie_page_soup.find('img', class_='film-thumbnail-img')
            if thumbnail_img:
                thumbnail_url = thumbnail_img['src']  # Get the thumbnail URL
            else:
                print(f"No thumbnail found for the movie link: {movie_url}.")
                continue  # Skip this movie if no thumbnail is found

            # Find all m3u8 links on the movie page
            m3u8_links = re.findall(r'(https://[^\s]+\.m3u8)', movie_page_content)
            if m3u8_links:
                # Create a section for each movie in the m3u8 file
                movies_data.append({
                    "title": movie_title,
                    "thumbnail_url": thumbnail_url,
                    "m3u8_links": m3u8_links
                })
            else:
                print(f"No m3u8 links found for {movie_title}.")
        else:
            print(f"Failed to fetch the movie page for {movie_url}.")

    # Write to new.m3u8 file
    with open('new.m3u8', 'w') as m3u8_file:
        m3u8_file.write("#EXTM3U\n")
        m3u8_file.write("#EXT-X-VERSION:4\n")
        m3u8_file.write("#EXT-X-TARGETDURATION:3\n")
        m3u8_file.write("#EXT-X-MEDIA-SEQUENCE:4855\n")
        m3u8_file.write("#EXT-X-DISCONTINUITY-SEQUENCE:0\n")

        for movie in movies_data:
            # Add thumbnail and title as a comment (or however you want to categorize them)
            m3u8_file.write(f"# Movie: {movie['title']}\n")
            m3u8_file.write(f"# Thumbnail: {movie['thumbnail_url']}\n")

            for m3u8_url in movie['m3u8_links']:
                m3u8_file.write(f"#EXTINF:-1, {movie['title']}\n")
                m3u8_file.write(f"{m3u8_url}\n")

if __name__ == "__main__":
    scrape_1hd()

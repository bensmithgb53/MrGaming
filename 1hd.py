import requests
from bs4 import BeautifulSoup
import re

def scrape_1hd():
    url = 'https://1hd.to/'
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')

    # Prepare to collect movie data
    movies_data = []

    movie_titles = soup.find_all('h3', class_='heading-xl')
    thumbnails = soup.find_all('img', class_='film-thumbnail-img')
    video_servers = soup.find_all('span', id='current-server')

    # Check if we have the same number of titles, thumbnails, and video servers
    if not (len(movie_titles) == len(thumbnails) == len(video_servers)):
        print("Mismatch in the number of titles, thumbnails, and video servers.")
        return

    # Loop through each movie and gather relevant information
    for i in range(len(movie_titles)):
        movie_title = movie_titles[i].text.strip()  # Get movie title
        thumbnail_url = thumbnails[i]['src']  # Get thumbnail URL
        
        # For now, let's print what we're extracting to check the assumptions
        print(f"Scraping movie: {movie_title}")

        # Extracting video page link (adjusted depending on site structure)
        video_page_link = video_servers[i].get('data-video-link')  # Assuming link is in an attribute like 'data-video-link'
        if not video_page_link:
            print(f"No video link found for {movie_title}")
            continue
        
        print(f"Found video link: {video_page_link}")

        # Visit the video page to extract the m3u8 link
        video_page_response = requests.get(video_page_link)
        if video_page_response.status_code == 200:
            video_page_content = video_page_response.text
            
            # Search for the .m3u8 URL in the video page
            m3u8_match = re.search(r'(https://[^\s]+\.m3u8)', video_page_content)
            
            if m3u8_match:
                m3u8_url = m3u8_match.group()
                print(f"Found m3u8 link for {movie_title}: {m3u8_url}")
            else:
                m3u8_url = "No m3u8 link found"
                print(f"No m3u8 link found for {movie_title}")
            
            # Add movie details to list
            movies_data.append({
                "title": movie_title,
                "thumbnail_url": thumbnail_url,
                "m3u8_url": m3u8_url
            })
        else:
            print(f"Failed to fetch the video page for {movie_title}")

    # Write m3u8 playlist file
    with open('playlist.m3u8', 'w') as m3u8_file:
        m3u8_file.write("#EXTM3U\n")
        for movie in movies_data:
            m3u8_file.write(f"#EXTINF:-1, {movie['title']}\n")
            m3u8_file.write(f"{movie['m3u8_url']}\n")

if __name__ == "__main__":
    scrape_1hd()

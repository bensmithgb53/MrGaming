import requests
from bs4 import BeautifulSoup
import re

def scrape_1hd():
    url = 'https://1hd.to/'
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to fetch the main page. Status code: {response.status_code}")
        return

    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Prepare to collect movie data
    movies_data = []

    # Extract movie titles and thumbnails
    movie_titles = soup.find_all('h3', class_='heading-xl')
    thumbnails = soup.find_all('img', class_='film-thumbnail-img')

    print(f"Found {len(movie_titles)} movie titles")
    print(f"Found {len(thumbnails)} thumbnails")

    # Check if we have matching numbers of titles and thumbnails
    if len(movie_titles) != len(thumbnails):
        print("Mismatch in the number of titles and thumbnails.")
        return

    # Loop through each movie and gather relevant information
    for i in range(len(movie_titles)):
        movie_title = movie_titles[i].text.strip()  # Get movie title
        thumbnail_url = thumbnails[i]['src']  # Get thumbnail URL

        # Assuming each thumbnail is wrapped in an <a> tag linking to the movie page
        video_page_link = thumbnails[i].parent['href'] if thumbnails[i].parent.has_attr('href') else None
        
        if not video_page_link:
            print(f"No link found for {movie_title}. Skipping.")
            continue
        
        print(f"Processing movie: {movie_title}, video page link: {video_page_link}")

        # Visit the video page to extract the m3u8 link
        video_page_response = requests.get(video_page_link)
        if video_page_response.status_code == 200:
            video_page_content = video_page_response.text

            # Extract video server link
            video_server_match = re.search(r'<span id="current-server">(.*?)</span>', video_page_content)
            if video_server_match:
                video_server_link = video_server_match.group(1).strip()
                
                # Fetch the m3u8 link from the video server
                m3u8_response = requests.get(video_server_link)
                if m3u8_response.status_code == 200:
                    m3u8_content = m3u8_response.text
                    
                    # Search for the .m3u8 URL in the response
                    m3u8_match = re.search(r'(https://[^\s]+\.m3u8)', m3u8_content)
                    if m3u8_match:
                        m3u8_url = m3u8_match.group()
                        print(f"Found m3u8 link for {movie_title}: {m3u8_url}")

                        # Add movie details to list
                        movies_data.append({
                            "title": movie_title,
                            "thumbnail_url": thumbnail_url,
                            "m3u8_url": m3u8_url
                        })
                    else:
                        print(f"No m3u8 link found for {movie_title}")
                else:
                    print(f"Failed to fetch m3u8 link for {movie_title}")
            else:
                print(f"No video server found for {movie_title}")
        else:
            print(f"Failed to fetch the video page for {movie_title}")

    # Write new.m3u8 playlist file
    with open('new.m3u8', 'w') as m3u8_file:
        m3u8_file.write("#EXTM3U\n")
        m3u8_file.write("#EXT-X-VERSION:4\n")
        m3u8_file.write("#EXT-X-TARGETDURATION:3\n")
        m3u8_file.write("#EXT-X-MEDIA-SEQUENCE:4855\n")
        m3u8_file.write("#EXT-X-DISCONTINUITY-SEQUENCE:0\n")
        for movie in movies_data:
            m3u8_file.write(f"#EXTINF:3.0, {movie['title']}\n")
            m3u8_file.write(f"{movie['m3u8_url']}\n")

    print(f"Created new.m3u8 with {len(movies_data)} entries.")

if __name__ == "__main__":
    scrape_1hd()

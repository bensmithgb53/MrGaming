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

    print(f"Found {len(movie_links)} movie links.")

    for link in movie_links:
        movie_url = link['href']  # Get the movie link
        print(f"Fetching movie page: {movie_url}")

        # Visit the movie page to extract the title and thumbnail
        movie_page_response = requests.get(movie_url)
        if movie_page_response.status_code == 200:
            movie_page_content = movie_page_response.text
            movie_page_soup = BeautifulSoup(movie_page_content, 'html.parser')

            # Extract the movie title from <h2 class="heading-xl">
            title_element = movie_page_soup.find('h2', class_='heading-xl')
            if title_element:
                movie_title = title_element.text.strip()
                print(f"Found title: {movie_title}")
            else:
                print(f"Title element not found for {movie_url}.")
                continue  # Skip this movie if no title is found

            # Extract the thumbnail image
            thumbnail_img = movie_page_soup.find('img', class_='film-thumbnail-img')
            if thumbnail_img:
                thumbnail_url = thumbnail_img['src']  # Get the thumbnail URL
                print(f"Found thumbnail URL: {thumbnail_url}")
            else:
                print(f"No thumbnail found for the movie link: {movie_url}.")
                continue  # Skip this movie if no thumbnail is found

            # Find all m3u8 links on the movie page
            m3u8_links = re.findall(r'(https://[^\s]+\.m3u8)', movie_page_content)
            if m3u8_links:
                # Add movie details to the list
                movies_data.append({
                    "title": movie_title,
                    "thumbnail_url": thumbnail_url,
                    "m3u8_links": m3u8_links
                })
                print(f"Found {len(m3u8_links)} m3u8 links for {movie_title}.")
            else:
                print(f"No m3u8 links found for {movie_title}.")
        else:
            print(f"Failed to fetch the movie page for {movie_url}.")

    # Write to new.m3u8 file in the specified format
    with open('new.m3u8', 'w') as m3u8_file:
        # Write the m3u8 file header
        m3u8_file.write("#EXTM3U\n")
        m3u8_file.write("#EXT-X-VERSION:4\n")
        m3u8_file.write("#EXT-X-TARGETDURATION:3\n")
        m3u8_file.write("#EXT-X-MEDIA-SEQUENCE:4855\n")
        m3u8_file.write("#EXT-X-DISCONTINUITY-SEQUENCE:0\n")

        # Write each movie's information in the specified format
        for movie in movies_data:
            # Assuming only the first m3u8 link is needed for each title
            m3u8_url = movie['m3u8_links'][0] if movie['m3u8_links'] else "No m3u8 link found"
            m3u8_file.write(f"#EXTINF:-1, {movie['title']}\n")  # Title in m3u8
            m3u8_file.write(f"{m3u8_url}\n")  # The m3u8 URL

            # Optional: Add thumbnail as a comment for clarity
            m3u8_file.write(f"# Thumbnail: {movie['thumbnail_url']}\n")

    print(f"Successfully wrote {len(movies_data)} movies to new.m3u8.")

if __name__ == "__main__":
    scrape_1hd()

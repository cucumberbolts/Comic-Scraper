"""
This is a program for downloading comics from gocomics.com.

See https://hackersandslackers.com/scraping-urls-with-beautifulsoup/ for inspiration

authors: Lawrence Cheung and Julian Poon
"""

import argparse
import time
import datetime
import os
import requests
from bs4 import BeautifulSoup

# Set the headers
HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}


def store_url(comic: str, month: int, day: int, year: int, url: str) -> None:
    """ Store the comic url for future use """
    open("scrapercache.txt", "a").write(f"{comic} {month:02}/{day:02}/{year:04} {url}\n")


def retrieve_url(comic: str, month: int, day: int, year: int) -> str:
    """ Retrieves the url from the given date
    returns an empty string if it doesn't exist """

    # If the cache file exists, then read from it
    if os.path.isfile("scrapercache.txt"):
        with open("scrapercache.txt", "r") as reader:
            search_string = f"{comic} {month:02}/{day:02}/{year:04}"
            for line in reader:
                if line[:len(comic) + 11] == search_string:
                    url = line[len(comic) + 12:]  # Gets the url
                    print(f"cached url: {url}")
                    return url

    return ""


def get_comic_url(comic: str, month: int, day: int, year: int) -> str:
    """ Returns the url of the comic image """
    # Makes comic string lowercase to avoid complication
    comic = comic.lower()

    # If the url is cached then return it
    url = retrieve_url(comic, month, day, year)
    if url:
        return url

    # The url of the comic strip
    url = f"https://www.gocomics.com/{comic}/{year}/{month}/{day}"

    # Request the page
    req = requests.get(url, HEADERS)
    soup = BeautifulSoup(req.content, 'html.parser')

    # Get all links with the lazyload img-fluid class
    links = soup.find_all(class_="lazyload img-fluid")

    # Search for the "[Comic] Comic Strip" image
    search_string = f"{comic} Comic Strip"
    for link in links:
        if search_string.lower() in link["alt"].lower():
            pic_url = link["src"]  # Get the url of the image
            store_url(comic, month, day, year, pic_url)  # Store the url
            return pic_url

    # Returns an empty string if image not found
    print("Error: Could not find image!")
    return ""


def save_comic(comic: str, month: int, day: int, year: int, output_dir: str) -> None:
    """ Saves the comic from the given date """
    # What file to save it as
    file_name = f"{comic}_{year}_{month}_{day}.gif"

    # Prints informaion
    print(f"Saving comic from {month}/{day}/{year} as {output_dir}/{file_name}")

    # Get the url of the comic image
    pic_url = get_comic_url(comic, month, day, year)

    # Request the image
    image = requests.get(pic_url, allow_redirects=True)

    # Save the image
    open(f"{output_dir}/{file_name}", 'wb').write(image.content)


def main() -> None:
    """ Main function """
    # Parses arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--comic", help="Which comic to download")
    parser.add_argument("-d", "--date", help="Which date to download from (MM/DD/YYYY)")

    args = parser.parse_args()
    comic = args.comic
    date = args.date

    if not comic:
        comic = input("Comic not specified. Please enter a comic: ")
    if not date:
        date = input("Date not specified. Please enter date of comic (MM/DD/YYYY): ")

    if date.lower() == "today":
        date = datetime.date.today().strftime("%m/%d/%Y")
    month, day, year = [int(x) for x in date.split("/")]

    # For benchmarking
    before = time.time()

    # Output directory for the comics
    output_dir = f"Comics/{comic}"

    # Creates directories if they don't exist
    if not os.path.isdir("./Comics"):
        os.mkdir(output_dir)

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # Saves the comic
    print("Starting to download!")
    save_comic(comic, month, day, year, output_dir)
    print("Finished downloading!")

    # Prints time elapsed
    after = time.time()
    seconds = (after - before) % 60
    print(f"Time took: {seconds:.2f} seconds!")
    input("Press enter to continue: ")


if __name__ == "__main__":
    main()

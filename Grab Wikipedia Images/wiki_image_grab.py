"""
This script grabs and displays all images that Pillows can handle from a specified wikipedia page as thumbnails.
THe images can be viewed in full resolution and downloaded locally if desired.
"""

from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import Toplevel, filedialog
from PIL import Image, ImageTk, UnidentifiedImageError
import requests
from io import BytesIO

# url = 'https://en.wikipedia.org/wiki/Lockheed_Martin_F-22_Raptor'
url = 'https://en.wikipedia.org/wiki/Pink_Floyd'

##URL is called directly
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

get_body = soup.body.find('div', attrs={'class':'mw-content-ltr mw-parser-output'})

# Find all tags with the attribute role="presentation"
# tags_with_role_presentation = soup.find_all(attrs={"role": "presentation"})

# Remove the tags with role=presentation
for tag in get_body.find_all(attrs={"role": ["presentation", "navigation"]}):
    tag.decompose()

# print(get_body)

#Find all images in body
# img_tags = get_body.find_all('img')


# Find all <a> tags that contain an <img> tag
a_tags_with_img = get_body.find_all('a', recursive=True, attrs={"href": True})

# Filter <a> tags that have an <img> child
filtered_a_tags = [a for a in a_tags_with_img if a.find('img')]

# combine with the first part of URL to make complete link
image_links = []
for a in filtered_a_tags:
    link = 'https://en.wikipedia.org' + a.get('href')
    image_links.append(link)

# print()
# print(image_links[0])


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


# Function to display full-size image
def open_full_image(image_url, screen_width, screen_height):
    try:
        response = requests.get(image_url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        image_data = response.content
        image = Image.open(BytesIO(image_data))

        # Resize image if it's larger than the screen dimensions
        image_width, image_height = image.size
        if image_width > screen_width or image_height > screen_height:
            max_size = (screen_width, screen_height)
            image.thumbnail(max_size, Image.ANTIALIAS)

        full_image_window = Toplevel()
        full_image_window.title("Full-Size Image")
        full_img = ImageTk.PhotoImage(image)

        full_size_image = tk.Label(full_image_window, image=full_img)
        full_size_image.image = full_img  # Keep a reference to avoid garbage collection


        # Add download button
        download_button = tk.Button(full_image_window, text="Download Image", command=lambda: download_image(image_url))


        download_button.pack()
        full_size_image.pack()


    except (requests.RequestException, UnidentifiedImageError) as e:
        print(f"Failed to load full-size image from {image_url}: {e}")


def download_image(image_url):
    try:
        response = requests.get(image_url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        image_data = response.content
        image = Image.open(BytesIO(image_data))

        # Ask the user where to save the file
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                 filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"),
                                                            ("All files", "*.*")])

        if file_path:
            image.save(file_path)
            print(f"Image saved to {file_path}")

    except (requests.RequestException, UnidentifiedImageError) as e:
        print(f"Failed to download image from {image_url}: {e}")



# Function to fetch and display images as thumbnails
def display_images():
    page_images = []
    label = []
    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    for i in range(len(image_links)):
        try:
            response = requests.get(image_links[i])  # Get the page that has the link to the image file
            soup = BeautifulSoup(response.text, 'html.parser')

            image_url = soup.find('div', attrs={'id': 'file'}).find('a').get('href')  # Find the link to the image file on the page
            print(image_url)
            page_images.append(image_url)
        except:
            continue

    # for i in page_images:
    for idx, url in enumerate(page_images):
        response = requests.get('https:' + url, headers=headers)
        try:
            image = Image.open(BytesIO(response.content))
        except:
            continue
        image.thumbnail((100, 100))  # Resize image to thumbnail

        img = ImageTk.PhotoImage(image)
        btn = tk.Button(root, image=img, command=lambda url=url: open_full_image('https:' + url, screen_width, screen_height))
        btn.image = img  # Keep a reference to avoid garbage collection
        btn.grid(row=idx // 5, column=idx % 5)  # Arrange thumbnails in a grid


# Create main Tkinter window
root = tk.Tk()
root.title("Image Thumbnails")

# Display images
display_images()

# Start the Tkinter main loop
root.mainloop()

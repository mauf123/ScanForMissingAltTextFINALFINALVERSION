import os
from flask import Flask, render_template, request, url_for
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)

def find_images_without_alt(url):
    image_list = []
    try:
        # Extract the domain name from the provided URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # Fetch the HTML content of the webpage
        response = requests.get(url)
        html_content = response.text

        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all image elements
        img_tags = soup.find_all('img')

        # Check each image for alt text
        for img in img_tags:
            if not img.has_attr('alt') or img['alt'] == '':
                src = img.get('src')
                # Check if the src ends with a valid image extension
                valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
                if any(src.endswith(ext) for ext in valid_extensions):
                    # If src doesn't contain the domain name, add it
                    if domain not in src:
                        src = f"{parsed_url.scheme}://{domain}{src}"
                    image_list.append({
                        'src': src,
                        'alt': 'No alt text provided',
                    })
    except Exception as e:
        print("An error occurred:", e)
    print("Images without alt text:", image_list)
    return image_list

@app.route('/')
def index():
    return render_template("homepage.html")

@app.route('/formpage', methods=["POST"])
def result():
    url = request.form["url"]
    images_without_alt = find_images_without_alt(url)
    return render_template('formpage.html', images=images_without_alt)

if __name__ == "__main__":
    app.run(debug=True)

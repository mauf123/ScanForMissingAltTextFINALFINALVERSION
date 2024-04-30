from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def find_images_without_alt(url):
    image_list = []
    try:
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
                # If alt attribute is missing or empty, add to the list
                image_list.append({
                    'src': img.get('src'),
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

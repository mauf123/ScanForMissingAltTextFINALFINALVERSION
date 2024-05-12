import os
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from PIL import Image
from io import BytesIO

app = Flask(__name__, static_url_path="/static")


#Boiler plate code from NLPConnect
# Initialize the VisionEncoderDecoder model
model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Maximum length and number of beams for generation
max_length = 16
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

def predict_step(image_paths):
    images = []
    for image_path in image_paths:
        i_image = Image.open(image_path)
        if i_image.mode != "RGB":
            i_image = i_image.convert(mode="RGB")
        images.append(i_image)

    # Extract features from images
    pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    # Generate alt text for the images
    output_ids = model.generate(pixel_values, **gen_kwargs)
    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    preds = [pred.strip() for pred in preds]
    return preds

def generate_alt_text(image_url):
    # Download image from URL
    response = requests.get(image_url)
    image_name = image_url.split('/')[-1]
    image_path = f"static/{image_name}"
    with open(image_path, 'wb') as f:
        f.write(response.content)

    # Generate alt text for the downloaded image
    alt_text = predict_step([image_path])[0]
    return alt_text

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
                    # If src is a relative path, convert it to absolute URL
                    if not src.startswith('http'):
                        src = urlparse(url).scheme + '://' + urlparse(url).netloc + src
                    alt_text = generate_alt_text(src)
                    image_list.append({
                        'src': src,
                        'alt': "no alt text provided",
                        'ai': alt_text
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

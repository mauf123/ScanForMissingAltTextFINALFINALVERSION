import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from PIL import Image



#Boilerplate code from NLPConnect
model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

max_length = 16
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

def generate_alt_text(image_paths):
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

def download_image(image_url):
    # Download image from URL
    response = requests.get(image_url)
    image_name = image_url.split('/')[-1]
    image_path = f"static/{image_name}"
    with open(image_path, 'wb') as f:
        f.write(response.content)

    # Generate alt text for the downloaded image
    alt_text = generate_alt_text([image_path])[0]
    return alt_text

def find_images_without_alt_text(url):
    image_list = []
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        response = requests.get(url)
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')

        img_tags = soup.find_all('img')

        for img in img_tags:
            if not img.has_attr('alt') or img['alt'] == '':
                src = img.get('src')

                valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
                if any(src.endswith(ext) for ext in valid_extensions):

                    if not src.startswith('http'):
                        src = urlparse(url).scheme + '://' + urlparse(url).netloc + src
                    alt_text = download_image(src)
                    image_list.append({
                        'src': src,
                        'alt': "no alt text provided",
                        'ai': alt_text
                    })
    except Exception as e:
        print("An error occurred:", e)

    print("Images without alt text:", image_list)
    return image_list
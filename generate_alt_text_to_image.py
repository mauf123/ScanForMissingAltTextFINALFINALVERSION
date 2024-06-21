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
    # fra linje 24-30 åbner vi billedet og tjeker hvorvidt det er RGB eller ej, hvis ikke det er RGB så konvertere vi det til RGB
    for image_path in image_paths:
        i_image = Image.open(image_path)
        if i_image.mode != "RGB":
            i_image = i_image.convert(mode="RGB")
        images.append(i_image)

    # Boilerplate kode
    pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    # Boilerplate kode, men basically generere den en alt ai text til billedet.
    output_ids = model.generate(pixel_values, **gen_kwargs)
    AIText = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    AIText = [pred.strip() for pred in AIText]
    return AIText

def download_image(image_url):


    # Downloader billedet gennem GET funktionen
    response = requests.get(image_url)

    #splitter billedet navnet(image.jpg) fra urlen (C://..../static/image.jpg)
    image_name = image_url.split('/')[-1]

    #tager fat i static mappen og skriver i binary(WB= Write binary) så billedet bliver puttet ind i static mappen
    image_path = f"static/{image_name}"
    with open(image_path, 'wb') as f:
        f.write(response.content)

    # Genere en alt text til billedet - vi tager det første item i vores array og derfor har vi hardcodet at tage fat i index 0
    alt_text = generate_alt_text([image_path])[0]
    return alt_text

def find_images_without_alt_text(url):
    image_list = []
    try:

        #Her gemmer vi domæne navnet og bruger det senere i metoden
        parsed_url = urlparse(url)

        #bruges ikke
        domain = parsed_url.netloc

        #Henter html siden og gemmer den i en variabel der hedder html_content
        response = requests.get(url)
        html_content = response.text

        #Bruger soup bibloteket til at arbejde med html koden og specifikt img tags.
        soup = BeautifulSoup(html_content, 'html.parser')

        #looper igennem html og finder alle img tag på siden og putter det i et resultset - kan sammenlignes med et array.
        img_tags = soup.find_all('img')

        #Looper vi igennem img_tags og tjekker hvis img har variablen alt eller alt er tomt #
        for img in img_tags:
            if not img.has_attr('alt') or img['alt'] == '':
                src = img.get('src')


                #Her tjekker vi om billedet slutter på de mest populære billede-extensions
                valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
                if any(src.endswith(ext) for ext in valid_extensions):

                    #Hvis ikke billedets url indeholder http, så putter vi http i starten af billedet, så man kan se den fulde URL til billedet.
                    if not src.startswith('http'):
                        src = urlparse(url).scheme + '://' + urlparse(url).netloc + src
                        #Efter vi har sammensat billedets fulde url, så appender vi src(billedetURL) og alt text til imagelist og returner den
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
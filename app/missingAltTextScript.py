
import requests
from bs4 import BeautifulSoup


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
                    'alt': 'No alt text provided'
                })
    except Exception as e:
        print("An error occurred:", e)

    return image_list


# Example usage:
url = "https://www.coor.dk/innovation/smart-property-solutions/smartenergy/"  # Replace with the URL of the webpage you want to check
images_without_alt = find_images_without_alt(url)
print("Images without alt text:")
for image in images_without_alt:
    print("Source:", image['src'])
    print("Alt text:", image['alt'])
    print()






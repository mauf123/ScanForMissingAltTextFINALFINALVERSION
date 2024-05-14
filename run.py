from flask import Flask, render_template, request
import generate_alt_text_to_image

app = Flask(__name__, static_url_path="/static")


@app.route('/')
def index():
    return render_template("homepage.html")

@app.route('/formpage', methods=["POST"])
def result():
    url = request.form["url"]
    images_without_alt = generate_alt_text_to_image.find_images_without_alt_text(url)
    return render_template('formpage.html', images=images_without_alt)

if __name__ == "__main__":
    app.run(debug=True)
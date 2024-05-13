from flask import Flask, render_template, request
import generateAltTextToImage

app = Flask(__name__, static_url_path="/static")


@app.route('/')
def index():
    return render_template("homepage.html")

@app.route('/formpage', methods=["POST"])
def result():
    url = request.form["url"]
    images_without_alt = generateAltTextToImage.find_images_without_alt(url)
    return render_template('formpage.html', images=images_without_alt)

if __name__ == "__main__":
    app.run(debug=True)

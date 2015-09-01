from flask import Flask, render_template, jsonify, send_file, request
import time
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("booth.html")


@app.route('/take_photo')
def take_photo():
    time.sleep(2)
    return jsonify({
        "success": True,
        "name": "hello.jpg"
    })

@app.route('/save_photo/<name>', methods=['POST'])
def save_photo(name):
    print(name)
    caption = request.form["caption"]
    with Image(filename='pictures/' + name) as img:
        with Image(filename='static/img/cse.png') as logo:
            img.composite(logo, top=img.height-200, left=img.width-200)
            if caption:
                with Drawing() as draw:
                    draw.font = 'font.otf'
                    draw.font_size = 400
                    draw.stroke_color = Color('#000')
                    draw.fill_color = Color('#fff')
                    draw.text_alignment = "center"
                    draw.text(int(img.width/2), int(img.height - 100), caption)
                    draw(img)
            img.save(filename='generated/' + name)
    return "Success"

@app.route('/pictures/<name>')
def get_photo(name):
    return send_file('pictures/' + name)

if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.9')

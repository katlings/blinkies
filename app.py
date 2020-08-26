import logging
from logging.handlers import RotatingFileHandler

from colour import Color
from flask import Flask, render_template, request, send_from_directory
from flask_wtf import FlaskForm
import random
from wtforms import StringField, validators
from wtforms_components import ColorField

from blinkie import make_gif


app = Flask(__name__)
app.config.update(WTF_CSRF_ENABLED=False)

handler = RotatingFileHandler('blinkies.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)


class BlinkieForm(FlaskForm):
    text = StringField('Text', [validators.length(max=64), validators.length(min=1)])
    background_color = ColorField('Blinkie Color')
    text_color = ColorField('Text Color')
    blink_color = ColorField('Text Blink Color')


@app.route('/', methods=['GET', 'POST'])
def generate_page():
    form = BlinkieForm()
    filename = None

    if form.validate_on_submit():
        if form.errors:
            app.logger.warning(form.errors)
        text = form.text.data
        gif_background_color = tuple(int(x * 255) for x in form.background_color.data.rgb)
        gif_text_color = tuple(int(x * 255) for x in form.text_color.data.rgb)
        gif_blink_color = tuple(int(x * 255) for x in form.blink_color.data.rgb)

        filename = make_gif(text, gif_background_color, gif_text_color, gif_blink_color)
        app.logger.info(filename)

        background_color = form.background_color.data.get_hex_l()
        text_color = form.text_color.data.get_hex_l()
        blink_color = form.blink_color.data.get_hex_l()
    else:
        text_color = '#000000'
        blink_color = '#ffffff'
        background_color = Color()
        background_color.red = random.random()
        background_color.green = random.random()
        background_color.blue = random.random()
        background_color = background_color.get_hex_l()

    return render_template('generate.html',
                           form=form,
                           filename=filename,
                           text_color=text_color,
                           blink_color=blink_color,
                           background_color=background_color)


@app.route('/output/<path:path>')
def send_gif(path):
    return send_from_directory('output', path)


if __name__ == '__main__':
    app.run()

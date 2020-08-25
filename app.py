import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, validators
from wtforms_components import ColorField
from webcolors import hex_to_rgb

from .blinkie import make_gif 


app = Flask(__name__)
app.config.update(WTF_CSRF_ENABLED=False)

handler = RotatingFileHandler('blinkies.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)


class BlinkieForm(FlaskForm):
    text = StringField('Text', [validators.length(max=64)])
    background_color = ColorField('Blinkie Color')
    text_color = ColorField('Text Color')
    blink_color = ColorField('Text Blink Color')


@app.route('/', methods=['GET', 'POST'])
def generate_page():
    form = BlinkieForm()
    filename = None

    app.logger.debug(form.validate())
    if form.errors:
        app.logger.warning(form.errors)

    if form.validate_on_submit():
        text = form.text.data
        background_color = tuple(int(x * 255) for x in form.background_color.data.rgb)
        text_color = tuple(int(x * 255) for x in form.text_color.data.rgb)
        blink_color = tuple(int(x * 255) for x in form.blink_color.data.rgb)
        print(background_color)

        filename = make_gif(text, background_color, text_color, blink_color)
        app.logger.info(filename)

    return render_template('generate.html', form=form, filename=filename)


@app.route('/output/<path:path>')
def send_gif(path):
    return send_from_directory('output', path)


if __name__ == '__main__':
    app.run()

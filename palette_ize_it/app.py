import base64
import os
from io import BytesIO

import cv2 as cv
import numpy as np
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from flask_wtf.file import FileField, FileRequired
from PIL import Image
from sklearn.cluster import KMeans
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("APP_SECRET_KEY")
bootstrap = Bootstrap5(app)
app.config["BOOTSTRAP_BOOTSWATCH_THEME"] = "quartz"
csrf = CSRFProtect()
csrf.init_app(app)


class InputForm(FlaskForm):
    image_file = FileField("Inspiration Image", validators=[FileRequired()])
    n_colors = IntegerField(
        "Number of Colors",
        default=10,
        validators=[DataRequired(), NumberRange(min=2, max=20)],
    )
    submit = SubmitField("Generate!")


@app.route("/")
def homepage():
    return render_template("index.html", current_page="home")


@app.route("/palette_ize", methods=["GET", "POST"])
def generate_palette():
    # Check Img File:
    def allowed_file(filename):
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    form = InputForm()
    if form.validate_on_submit():
        f = form.image_file.data
        if allowed_file(f.filename):
            img = Image.open(f.stream)
            with BytesIO() as buf:
                img.save(buf, "jpeg")
                image_bytes = buf.getvalue()
            n_colors = n_colors_kmeans(image_bytes, form.n_colors.data)
            encoded_string = base64.b64encode(image_bytes).decode()
            return render_template(
                "result.html",
                current_page="generate",
                img_data=encoded_string,
                colors=n_colors,
            )
    return render_template("generate.html", current_page="generate", form=form)


def n_colors_kmeans(buf, n):
    img_np = np.frombuffer(buf, np.uint8)
    img = cv.imdecode(img_np, cv.IMREAD_COLOR)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    clt = KMeans(n_clusters=n)
    clt.fit(img.reshape(-1, 3))
    centers = [[int(v.item()) for v in c] for c in clt.cluster_centers_]
    palette_rgb = [tuple(c) for c in centers]
    palette = ["".join([f"{x:02x}" for x in color]) for color in palette_rgb]
    return palette

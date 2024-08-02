import os
from pathlib import Path

from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from flask_wtf.csrf import CSRFProtect
from PIL import Image
from werkzeug.utils import secure_filename
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("APP_SECRET_KEY")
Path(app.instance_path).mkdir(parents=True, exist_ok=True)
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
            filename = secure_filename(f.filename)
            file_path = os.path.join(app.instance_path, filename)
            f.save(file_path)
            image_as_array(file_path)
            return render_template("generate.html", current_page="generate", form=form)
        else:
            print("oops")

    return render_template("generate.html", current_page="generate", form=form)


# Process img file:
def image_as_array(filename):
    img = Image.open(filename)
    print(img.format)
    print(img.size)
    print(img.mode)

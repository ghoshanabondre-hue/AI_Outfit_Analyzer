from flask import Flask, request, jsonify, render_template_string
from PIL import Image
import base64
import io
import random

app = Flask(__name__)


# =========================================================
# AI OUTFIT ANALYZER - PYTHON
# =========================================================

def analyze_outfit(image):

    # Convert image to RGB
    image = image.convert("RGB")

    # Image size
    width, height = image.size

    # Resize for faster processing
    small_image = image.resize((100, 100))

    pixels = list(small_image.getdata())

    # Calculate average RGB
    total_r = 0
    total_g = 0
    total_b = 0

    for r, g, b in pixels:
        total_r += r
        total_g += g
        total_b += b

    total = len(pixels)

    avg_r = total_r // total
    avg_g = total_g // total
    avg_b = total_b // total

    # -----------------------------------------
    # BASIC COLOR DETECTION
    # -----------------------------------------

    if avg_r > 200 and avg_g > 200 and avg_b > 200:
        color = "White / Light"

    elif avg_r < 70 and avg_g < 70 and avg_b < 70:
        color = "Black / Dark"

    elif avg_r > avg_g * 1.3 and avg_r > avg_b * 1.3:
        color = "Red / Warm"

    elif avg_g > avg_r * 1.25 and avg_g > avg_b * 1.15:
        color = "Green"

    elif avg_b > avg_r * 1.25 and avg_b > avg_g * 1.15:
        color = "Blue"

    elif avg_r > 150 and avg_g > 100 and avg_b < 100:
        color = "Yellow / Golden"

    else:
        color = "Mixed Colors"

    # -----------------------------------------
    # OUTFIT CATEGORY
    # -----------------------------------------

    categories = [
        "Casual Outfit",
        "Modern Outfit",
        "Everyday Wear",
        "Fashion Outfit",
        "Smart Casual"
    ]

    category = random.choice(categories)

    # -----------------------------------------
    # STYLE
    # -----------------------------------------

    styles = [
        "Casual",
        "Modern Casual",
        "Minimal Fashion",
        "Trendy",
        "Smart Casual"
    ]

    style = random.choice(styles)

    # -----------------------------------------
    # OUTFIT SCORE
    # -----------------------------------------

    score = random.randint(78, 96)

    # -----------------------------------------
    # STYLE SUGGESTION
    # -----------------------------------------

    suggestions = [
        "Try white sneakers with this outfit.",
        "Minimal accessories can make this outfit look more elegant.",
        "A simple handbag can complement this outfit nicely.",
        "Neutral-colored shoes would match this outfit well.",
        "Try adding a light jacket for a stylish appearance.",
        "Small earrings and a simple watch can enhance the look.",
        "Try matching the outfit with simple accessories."
    ]

    suggestion = random.choice(suggestions)

    return {
        "category": category,
        "color": color,
        "style": style,
        "score": score,
        "suggestion": suggestion,
        "width": width,
        "height": height
    }


# =========================================================
# HTML + CSS + JAVASCRIPT
# =========================================================

HTML = """

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>AI Outfit Analyzer</title>


<style>

/* =========================
   GENERAL
========================= */

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {

    font-family: Arial, sans-serif;

    min-height: 100vh;

    background:
    linear-gradient(
        135deg,
        #f6f0ff,
        #fff1f7,
        #eef7ff
    );

    color: #333;
}


/* =========================
   MAIN CONTAINER
========================= */

.container {

    width: 90%;

    max-width: 1100px;

    margin: auto;

}


/* =========================
   HEADER
========================= */

header {

    text-align: center;

    padding: 40px 10px 25px;

}

.logo {

    font-size: 34px;

    font-weight: bold;

    margin-bottom: 10px;

}

header p {

    color: #777;

    font-size: 16px;

}


/* =========================
   MAIN CARD
========================= */

.main-card {

    background: white;

    padding: 40px;

    border-radius: 25px;

    box-shadow:
    0 15px 45px
    rgba(0,0,0,0.10);

    margin-bottom: 30px;

}


/* =========================
   TITLE
========================= */

.title {

    text-align: center;

    margin-bottom: 10px;

    font-size: 30px;

}

.subtitle {

    text-align: center;

    color: #777;

    margin-bottom: 30px;

}


/* =========================
   UPLOAD AREA
========================= */

.upload-area {

    border: 2px dashed #aaa;

    border-radius: 20px;

    padding: 45px 20px;

    text-align: center;

    transition: 0.3s;

}

.upload-area:hover {

    transform: translateY(-3px);

    box-shadow:
    0 10px 25px
    rgba(0,0,0,0.08);

}

.upload-icon {

    font-size: 65px;

    margin-bottom: 15px;

}

.upload-area h2 {

    margin-bottom: 8px;

}

.upload-area p {

    color: #888;

    margin-bottom: 20px;

}


/* =========================
   FILE INPUT
========================= */

input[type="file"] {

    margin-bottom: 20px;

}


/* =========================
   BUTTON
========================= */

button {

    display: block;

    margin: auto;

    padding: 14px 32px;

    border: none;

    border-radius: 30px;

    background: #333;

    color: white;

    font-size: 16px;

    font-weight: bold;

    cursor: pointer;

    transition: 0.3s;

}

button:hover {

    transform: translateY(-3px);

    box-shadow:
    0 8px 20px
    rgba(0,0,0,0.20);

}


/* =========================
   LOADING
========================= */

#loading {

    display: none;

    text-align: center;

    margin-top: 25px;

    font-weight: bold;

}


/* =========================
   RESULT
========================= */

#result {

    display: none;

    background: white;

    padding: 35px;

    border-radius: 25px;

    box-shadow:
    0 15px 45px
    rgba(0,0,0,0.10);

    margin-bottom: 30px;

}

.result-title {

    text-align: center;

    font-size: 28px;

    margin-bottom: 30px;

}


/* =========================
   RESULT GRID
========================= */

.result-grid {

    display: grid;

    grid-template-columns:
    1fr 1fr;

    gap: 30px;

}


/* =========================
   IMAGE
========================= */

.preview {

    text-align: center;

}

.preview img {

    width: 100%;

    max-width: 420px;

    max-height: 500px;

    object-fit: cover;

    border-radius: 20px;

}


/* =========================
   ANALYSIS
========================= */

.analysis {

    display: flex;

    flex-direction: column;

    gap: 15px;

}

.result-item {

    background: #f7f7f7;

    padding: 18px;

    border-radius: 15px;

    display: flex;

    justify-content:
    space-between;

    align-items: center;

}

.result-item span {

    font-weight: bold;

}

.result-item strong {

    text-align: right;

}


/* =========================
   SCORE
========================= */

.score-card {

    text-align: center;

    padding: 20px;

    background: #f4f4f4;

    border-radius: 20px;

}

.score {

    font-size: 55px;

    font-weight: bold;

    margin: 8px;

}


/* =========================
   SUGGESTION
========================= */

.suggestion {

    padding: 20px;

    border-radius: 20px;

    background: #fafafa;

}

.suggestion h3 {

    margin-bottom: 10px;

}

.suggestion p {

    color: #666;

    line-height: 1.5;

}


/* =========================
   FOOTER
========================= */

footer {

    text-align: center;

    padding: 20px;

    color: #777;

    margin-bottom: 20px;

}


/* =========================
   MOBILE
========================= */

@media(max-width: 768px) {

    .container {

        width: 94%;

    }

    .main-card {

        padding: 25px 18px;

    }

    .title {

        font-size: 24px;

    }

    .logo {

        font-size: 27px;

    }

    .result-grid {

        grid-template-columns: 1fr;

    }

}

</style>

</head>


<body>


<div class="container">


<header>

<div class="logo">

👗 AI Outfit Analyzer

</div>

<p>

Smart Fashion Analysis using Python

</p>

</header>



<div class="main-card">


<h1 class="title">

Discover Your Outfit Style ✨

</h1>


<p class="subtitle">

Upload your outfit image and let AI analyze your fashion style.

</p>



<div class="upload-area">


<div class="upload-icon">

📸

</div>


<h2>

Upload Your Outfit

</h2>


<p>

Select a JPG, JPEG or PNG image

</p>


<input

type="file"

id="imageInput"

accept="image/*"


>


<button

onclick="analyzeImage()">

🔍 Analyze Outfit

</button>


</div>


<div id="loading">

🤖 AI is analyzing your outfit...

</div>


</div>



<div id="result">


<h2 class="result-title">

✨ AI Analysis Result

</h2>



<div class="result-grid">


<div class="preview">

<img

id="previewImage"

src=""

alt="Outfit Preview"

>

</div>



<div class="analysis">


<div class="result-item">

<span>

👕 Category

</span>

<strong id="category">

-

</strong>

</div>



<div class="result-item">

<span>

🎨 Main Color

</span>

<strong id="color">

-

</strong>

</div>



<div class="result-item">

<span>

👗 Style

</span>

<strong id="style">

-

</strong>

</div>



<div class="score-card">

<div>

⭐ Outfit Score

</div>


<div class="score"

id="score">

0

</div>


<div>

out of 100

</div>

</div>



<div class="suggestion">


<h3>

💡 AI Style Suggestion

</h3>


<p id="suggestion">

-

</p>


</div>


</div>


</div>


</div>



<footer>

🤖 AI Outfit Analyzer |

HTML • CSS • JavaScript • Python

</footer>


</div>



<script>


// ========================================
// JAVASCRIPT
// ========================================

async function analyzeImage() {


    const input =
        document.getElementById("imageInput");


    const loading =
        document.getElementById("loading");


    const result =
        document.getElementById("result");


    const preview =
        document.getElementById("previewImage");


    // Check image

    if (input.files.length === 0) {

        alert(
            "Please select an outfit image first!"
        );

        return;

    }


    const file =
        input.files[0];


    // Show image immediately

    const reader =
        new FileReader();


    reader.onload =
        function(event) {

            preview.src =
                event.target.result;

        };


    reader.readAsDataURL(file);


    // Create FormData

    const formData =
        new FormData();


    formData.append(
        "image",
        file
    );


    // Loading

    loading.style.display =
        "block";


    result.style.display =
        "none";


    try {


        const response =
            await fetch(
                "/analyze",
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        if (data.error) {

            alert(data.error);

            return;

        }


        // Display results

        document.getElementById(
            "category"
        ).textContent =
            data.category;


        document.getElementById(
            "color"
        ).textContent =
            data.color;


        document.getElementById(
            "style"
        ).textContent =
            data.style;


        document.getElementById(
            "score"
        ).textContent =
            data.score;


        document.getElementById(
            "suggestion"
        ).textContent =
            data.suggestion;


        // Show result

        result.style.display =
            "block";


        result.scrollIntoView({
            behavior: "smooth"
        });


    }


    catch(error) {


        console.log(error);


        alert(
            "Something went wrong. Please try again."
        );


    }


    finally {

        loading.style.display =
            "none";

    }

}

</script>


</body>

</html>

"""


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template_string(HTML)


# =========================================================
# ANALYZE IMAGE
# =========================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    if "image" not in request.files:

        return jsonify({
            "error": "No image uploaded"
        })


    file = request.files["image"]


    if file.filename == "":

        return jsonify({
            "error": "Please select an image"
        })


    try:

        image = Image.open(file)

        result = analyze_outfit(image)

        return jsonify(result)


    except Exception as e:

        return jsonify({
            "error": str(e)
        })


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print("")
    print("======================================")
    print("      AI OUTFIT ANALYZER")
    print("======================================")
    print("")
    print("Open this link in your browser:")
    print("http://127.0.0.1:5000")
    print("")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
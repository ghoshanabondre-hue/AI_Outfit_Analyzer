from flask import Flask, request, jsonify, render_template_string
from PIL import Image, ImageStat
import math

app = Flask(__name__)

# =========================================================
# COLOR DETECTION
# =========================================================

def color_name(r, g, b):
    brightness = (r + g + b) / 3
    saturation = max(r, g, b) - min(r, g, b)

    if brightness < 45:
        return "Black"

    if brightness > 220 and saturation < 30:
        return "White"

    if saturation < 25:
        if brightness < 110:
            return "Dark Grey"
        return "Grey"

    if r > 175 and g > 145 and b < 120:
        return "Yellow"

    if r > 185 and g > 90 and g < 160 and b < 110:
        return "Orange"

    if r > 160 and g < 110 and b < 120:
        return "Red"

    if r > 155 and g < 140 and b > 130:
        return "Pink"

    if r > 120 and b > 115 and g < 115:
        return "Purple"

    if b > r * 1.18 and b > g * 1.05:
        return "Blue"

    if g > r * 1.15 and g > b * 1.05:
        return "Green"

    if r > 120 and g > 85 and b < 85:
        return "Brown"

    if r > 145 and g > 125 and b < 115:
        return "Beige"

    return "Mixed"


# =========================================================
# IMAGE FEATURES
# =========================================================

def get_features(image):

    img = image.convert("RGB")
    img = img.resize((100, 100))

    pixels = list(img.getdata())

    # Average RGB
    r = sum(p[0] for p in pixels) / len(pixels)
    g = sum(p[1] for p in pixels) / len(pixels)
    b = sum(p[2] for p in pixels) / len(pixels)

    brightness = (r + g + b) / 3
    variation = sum(
        abs(p[0] - r) +
        abs(p[1] - g) +
        abs(p[2] - b)
        for p in pixels
    ) / len(pixels)

    # Texture / edge estimate
    edges = 0

    for y in range(1, 99):
        for x in range(1, 99):

            current = img.getpixel((x, y))
            left = img.getpixel((x - 1, y))
            top = img.getpixel((x, y - 1))

            d1 = sum(abs(current[i] - left[i]) for i in range(3))
            d2 = sum(abs(current[i] - top[i]) for i in range(3))

            if d1 + d2 > 130:
                edges += 1

    texture = edges / (98 * 98)

    dominant = color_name(r, g, b)

    return r, g, b, brightness, variation, texture, dominant


# =========================================================
# CATEGORY DETECTION
# =========================================================

def detect_category(image):

    r, g, b, brightness, variation, texture, dominant = get_features(image)

    # Calculate visual signals
    warm = r > b * 1.15
    blue = b > r * 1.15
    green = g > r * 1.12
    detailed = variation > 55 or texture > 0.17
    simple = variation < 38 and texture < 0.13
    dark = brightness < 95
    bright = brightness > 175

    # Different visual combinations
    if detailed and warm:
        return "Traditional / Saree / Ethnic", "Traditional", 88

    if detailed and (dominant in ["Red", "Pink", "Orange", "Purple"]):
        return "Festive / Ethnic Wear", "Festive", 86

    if blue and dark:
        return "Jeans / Denim / Western", "Western Casual", 87

    if blue and not detailed:
        return "Jeans / Top / Casual", "Casual", 84

    if green and detailed:
        return "Kurti / Indo-Western", "Indo-Western", 85

    if bright and simple:
        return "Kurti / Light Casual", "Elegant Casual", 82

    if dark and simple:
        return "Western Casual Outfit", "Modern Casual", 80

    if detailed:
        return "Ethnic / Stylish Outfit", "Stylish Ethnic", 83

    return "Smart Casual Outfit", "Modern Casual", 78


# =========================================================
# CATEGORY-SPECIFIC SUGGESTIONS
# =========================================================

SUGGESTIONS = {

    "Traditional": [

        (
            "Add elegant jhumkas and a simple bindi.",
            "Try a neat bun or soft braid with the traditional look."
        ),

        (
            "Pair the outfit with matching ethnic juttis.",
            "Choose light gold or oxidised jewellery."
        ),

        (
            "Use soft makeup with defined eyes and a natural lip shade.",
            "A small traditional handbag will complete the look."
        ),

        (
            "Try a low bun decorated with a small hair accessory.",
            "Choose sandals or juttis in a neutral shade."
        ),

        (
            "Keep jewellery elegant rather than using too many pieces.",
            "A matching dupatta can make the outfit look more complete."
        ),

        (
            "Try small earrings if the outfit already has heavy detailing.",
            "Use a soft hairstyle so the outfit remains the focus."
        )
    ],

    "Festive": [

        (
            "Add statement earrings for a festive appearance.",
            "Try soft curls or a decorated braid."
        ),

        (
            "Choose a small clutch that complements the outfit.",
            "Use warm-toned makeup with a soft lip shade."
        ),

        (
            "Pair the outfit with ethnic sandals or embellished juttis.",
            "Keep the jewellery coordinated with the outfit."
        ),

        (
            "A subtle bindi can enhance the festive appearance.",
            "Try a neat bun for a polished traditional look."
        ),

        (
            "Choose one statement jewellery piece.",
            "Keep the remaining accessories minimal."
        )
    ],

    "Western Casual": [

        (
            "Pair the outfit with clean white or neutral sneakers.",
            "Try open hair, soft waves or a simple ponytail."
        ),

        (
            "Add a minimal watch or bracelet.",
            "Choose a small crossbody bag."
        ),

        (
            "Use natural makeup for an everyday casual look.",
            "A simple chain can add a polished touch."
        ),

        (
            "Try a denim or lightweight jacket for layering.",
            "Choose comfortable sneakers or casual sandals."
        ),

        (
            "Keep accessories simple and modern.",
            "Use a neutral handbag to balance the outfit."
        )
    ],

    "Casual": [

        (
            "Pair jeans with sneakers or comfortable casual shoes.",
            "Try a simple ponytail or open hairstyle."
        ),

        (
            "Add small hoops or minimal earrings.",
            "A crossbody bag will suit the casual outfit."
        ),

        (
            "Use light makeup with a natural lip shade.",
            "Add a simple watch for a clean look."
        ),

        (
            "Try a tucked-in top for a more polished appearance.",
            "Choose neutral footwear to balance the outfit."
        ),

        (
            "A simple bracelet can complete the look.",
            "Try a lightweight jacket if the outfit needs layering."
        ),

        (
            "Keep the accessories minimal.",
            "Choose comfortable footwear for everyday wear."
        )
    ],

    "Indo-Western": [

        (
            "Try small jhumkas with the kurti.",
            "Pair it with comfortable sandals or juttis."
        ),

        (
            "A soft braid or open waves will complement the kurti.",
            "Choose a simple handbag in a matching shade."
        ),

        (
            "Use natural makeup with a soft lip colour.",
            "Add a simple bracelet or watch."
        ),

        (
            "Try a matching dupatta for a more traditional appearance.",
            "Keep the footwear simple and comfortable."
        ),

        (
            "Choose minimal jewellery for a modern kurti look.",
            "A small shoulder bag can complete the outfit."
        ),

        (
            "Try a neat ponytail for a clean everyday appearance.",
            "Choose neutral sandals or juttis."
        )
    ],

    "Elegant Casual": [

        (
            "Keep jewellery minimal and elegant.",
            "Try soft waves or a neat ponytail."
        ),

        (
            "Choose neutral sandals or clean sneakers.",
            "Use fresh, natural makeup."
        ),

        (
            "Add a small handbag in a matching shade.",
            "A simple watch can make the outfit look polished."
        ),

        (
            "Try small earrings for a clean appearance.",
            "Keep the hairstyle simple and neat."
        )
    ],

    "Stylish Ethnic": [

        (
            "Add small ethnic earrings to complement the outfit.",
            "Try a braid or soft waves."
        ),

        (
            "Choose comfortable juttis or ethnic sandals.",
            "Use light makeup with a natural lip."
        ),

        (
            "Try a simple bracelet or watch.",
            "Keep the handbag small and elegant."
        ),

        (
            "A subtle bindi can enhance the ethnic look.",
            "Choose accessories that match the outfit colour."
        )
    ],

    "Modern Casual": [

        (
            "Choose simple modern accessories.",
            "Try soft waves or a neat ponytail."
        ),

        (
            "Pair the outfit with neutral footwear.",
            "Use natural everyday makeup."
        ),

        (
            "Add a minimal watch or bracelet.",
            "Choose a small crossbody bag."
        ),

        (
            "Keep the hairstyle clean and comfortable.",
            "Use one simple statement accessory."
        )
    ]
}


AVOID = {

    "Traditional": [
        "Avoid mixing heavy jewellery with too many other accessories.",
        "Avoid sporty footwear with a strongly traditional outfit."
    ],

    "Festive": [
        "Avoid using too many statement accessories together.",
        "Avoid mixing several unrelated bright colours."
    ],

    "Western Casual": [
        "Avoid heavy traditional jewellery with a casual western outfit.",
        "Avoid combining too many bold patterns."
    ],

    "Casual": [
        "Avoid excessive accessories with a simple jeans-and-top look.",
        "Avoid uncomfortable formal footwear for a casual outfit."
    ],

    "Indo-Western": [
        "Avoid very heavy jewellery with a simple kurti.",
        "Avoid mixing too many bright colours."
    ],

    "Elegant Casual": [
        "Avoid overloading the outfit with accessories.",
        "Avoid very heavy makeup for a simple daytime look."
    ],

    "Stylish Ethnic": [
        "Avoid mixing too many different jewellery styles.",
        "Avoid footwear that clashes with the ethnic outfit."
    ],

    "Modern Casual": [
        "Avoid too many statement accessories.",
        "Avoid mixing too many unrelated colours."
    ]
}


# =========================================================
# CREATE DIFFERENT SUGGESTIONS
# =========================================================

def get_suggestions(category, image):

    r, g, b, brightness, variation, texture, dominant = get_features(image)

    keys = list(SUGGESTIONS.keys())

    # Deterministic selection based on actual image features
    number = int(
        r * 3 +
        g * 5 +
        b * 7 +
        brightness * 11 +
        variation * 13 +
        texture * 1000
    )

    key = category

    if key not in SUGGESTIONS:
        key = "Modern Casual"

    options = SUGGESTIONS[key]

    selected = options[number % len(options)]

    avoid_options = AVOID.get(
        key,
        AVOID["Modern Casual"]
    )

    avoid_start = (number // 3) % len(avoid_options)

    avoid = [
        avoid_options[avoid_start],
        avoid_options[(avoid_start + 1) % len(avoid_options)]
    ]

    return list(selected), avoid


# =========================================================
# MAIN ANALYZER
# =========================================================

def analyze_outfit(image):

    category, style, base_score = detect_category(image)

    r, g, b, brightness, variation, texture, dominant = get_features(image)

    # Improve score slightly based on visual detail
    score = base_score

    if variation > 60:
        score += 3

    if texture > 0.18:
        score += 2

    score = min(score, 97)

    suggestions, avoid = get_suggestions(style, image)

    if dominant == "Mixed":
        color_text = "Mixed / Multicolor"
    else:
        color_text = dominant

    # Reason
    reasons = []

    if variation > 55:
        reasons.append("multiple visible colour tones")

    if texture > 0.16:
        reasons.append("detailed visual texture")

    if brightness > 170:
        reasons.append("bright overall appearance")

    if brightness < 90:
        reasons.append("deeper/darker visual tones")

    if not reasons:
        reasons.append("balanced colour and visual composition")

    reason = "Detected from " + ", ".join(reasons) + "."

    return {
        "category": category,
        "dominant_color": color_text,
        "style": style,
        "score": score,
        "reason": reason,
        "do": suggestions,
        "dont": avoid
    }


# =========================================================
# HTML
# =========================================================

HTML = """
<!DOCTYPE html>

<html>

<head>

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>AI Outfit Analyzer</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;

    background:
        linear-gradient(
            135deg,
            #eef5ff,
            #f8f2ff,
            #fff5fa
        );

    color: #20243a;
}

.container {
    max-width: 950px;
    margin: auto;
    padding: 28px 18px 50px;
}

/* HEADER */

.header {
    text-align: center;
    margin-bottom: 25px;
}

.header h1 {
    margin: 0;
    font-size: 42px;
    font-weight: 800;

    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed,
        #ec4899
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header p {
    color: #687085;
    font-size: 17px;
}

/* CARD */

.card {
    background: rgba(255,255,255,0.94);
    border-radius: 24px;
    padding: 25px;
    margin-bottom: 22px;

    box-shadow:
        0 15px 45px rgba(48,55,90,0.12);
}

/* UPLOAD */

.upload-box {

    border-radius: 22px;

    padding: 38px 20px;

    text-align: center;

    background:
        linear-gradient(
            135deg,
            #2563eb,
            #6366f1,
            #8b5cf6
        );

    color: white;

    box-shadow:
        0 12px 30px rgba(79,70,229,0.25);
}

.upload-box h2 {
    margin: 0 0 8px;
    font-size: 25px;
}

.upload-box p {
    margin: 5px 0 18px;
    opacity: 0.92;
}

.file-input {
    display: inline-block;

    background: white;

    color: #374151;

    padding: 11px 16px;

    border-radius: 12px;

    cursor: pointer;

    font-weight: 600;
}

.file-input input {
    display: none;
}

/* PREVIEW */

.preview {
    display: none;

    max-width: 280px;
    max-height: 350px;

    margin: 22px auto 5px;

    border-radius: 20px;

    border: 5px solid white;

    box-shadow:
        0 10px 30px rgba(0,0,0,0.18);
}

/* BUTTON */

.analyze-button {

    display: block;

    width: 100%;

    margin-top: 22px;

    padding: 17px;

    border: none;

    border-radius: 14px;

    background:
        linear-gradient(
            90deg,
            #2563eb,
            #7c3aed
        );

    color: white;

    font-size: 18px;

    font-weight: 700;

    cursor: pointer;

    box-shadow:
        0 8px 22px rgba(79,70,229,0.28);

    transition: 0.2s;
}

.analyze-button:hover {
    transform: translateY(-2px);
}

/* LOADING */

.loading {
    display: none;

    text-align: center;

    margin-top: 18px;

    font-weight: 600;

    color: #5b21b6;
}

/* RESULT */

.result {
    display: none;
}

.result-title {
    font-size: 27px;
    margin-top: 0;
}

/* GRID */

.grid {

    display: grid;

    grid-template-columns:
        repeat(2, 1fr);

    gap: 16px;
}

.info-box {

    padding: 20px;

    border-radius: 18px;

    background: #f8f9ff;

    border: 1px solid #e8e9f5;
}

.info-box h3 {

    margin: 0 0 9px;

    font-size: 15px;

    color: #72778a;

    text-transform: uppercase;
}

.info-box p {

    margin: 0;

    font-size: 19px;

    font-weight: 700;

    color: #242842;
}

/* WHY */

.reason {

    margin-top: 18px;

    padding: 18px;

    border-radius: 17px;

    background: #f3f4ff;
}

.reason strong {
    display: block;
    margin-bottom: 7px;
}

/* SUGGESTION */

.suggestion-card {

    border-radius: 20px;

    padding: 22px;

    margin-top: 18px;

    background: #ffffff;

    border: 1px solid #ececf5;
}

.suggestion-card h2 {
    margin-top: 0;
}

.suggestion-card ul {

    padding-left: 23px;

    margin-bottom: 0;
}

.suggestion-card li {

    margin-bottom: 11px;

    line-height: 1.5;
}

/* FOOTER */

.footer {

    text-align: center;

    color: #7b8092;

    margin-top: 25px;

    font-size: 14px;
}

/* MOBILE */

@media(max-width:650px) {

    .header h1 {
        font-size: 31px;
    }

    .grid {
        grid-template-columns: 1fr;
    }

    .container {
        padding: 18px 13px 40px;
    }

    .card {
        padding: 18px;
    }

}

</style>

</head>


<body>

<div class="container">

<div class="header">

<h1>✨ AI Outfit Analyzer</h1>

<p>
Discover your outfit style, colors and personalized fashion tips.
</p>

</div>


<div class="card">

<div class="upload-box">

<h2>📸 Upload Outfit Image</h2>

<p>
Choose a clear photo of your outfit for analysis.
</p>

<label class="file-input">

Choose Image

<input
type="file"
id="imageInput"
accept="image/*"
>

</label>

</div>


<img
id="preview"
class="preview"
>


<button
class="analyze-button"
onclick="analyzeOutfit()"
>

✨ Analyze My Outfit

</button>


<div
id="loading"
class="loading"
>

⏳ Analyzing your outfit...

</div>

</div>


<div
id="result"
class="result"
>

<div class="card">

<h2 class="result-title">
📊 Outfit Analysis Result
</h2>


<div class="grid">


<div class="info-box">

<h3>👗 Category</h3>

<p id="category">
-
</p>

</div>


<div class="info-box">

<h3>🎨 Dominant Color</h3>

<p id="color">
-
</p>

</div>


<div class="info-box">

<h3>✨ Style</h3>

<p id="style">
-
</p>

</div>


<div class="info-box">

<h3>⭐ Style Score</h3>

<p id="score">
-
</p>

</div>


</div>


<div class="reason">

<strong>
🔎 Why This Result?
</strong>

<span id="reason">
-
</span>

</div>

</div>


<div class="suggestion-card">

<h2>
💖 What You Should Do
</h2>

<ul id="doList">
</ul>

</div>


<div class="suggestion-card">

<h2>
⚠️ What You Should Avoid
</h2>

<ul id="dontList">
</ul>

</div>


</div>


<div class="footer">

AI Outfit Analyzer • Smart Fashion Suggestions

</div>


</div>


<script>

let selectedImage = null;


document
.getElementById("imageInput")
.addEventListener("change", function(event) {

    selectedImage = event.target.files[0];

    if (!selectedImage) {
        return;
    }

    const preview =
        document.getElementById("preview");

    preview.src =
        URL.createObjectURL(selectedImage);

    preview.style.display = "block";
});


async function analyzeOutfit() {

    if (!selectedImage) {

        alert(
            "Please upload an outfit image first."
        );

        return;
    }


    const loading =
        document.getElementById("loading");

    const result =
        document.getElementById("result");


    loading.style.display = "block";

    result.style.display = "none";


    const formData = new FormData();

    formData.append(
        "image",
        selectedImage
    );


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
            awa

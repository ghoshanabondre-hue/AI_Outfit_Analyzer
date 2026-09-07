from flask import Flask, request, jsonify, render_template_string
from PIL import Image
import base64
import io
import math

app = Flask(__name__)

# ---------------------------------------------------------
# COLOR ANALYSIS
# ---------------------------------------------------------

def get_color_name(r, g, b):
    brightness = (r + g + b) / 3
    mx = max(r, g, b)
    mn = min(r, g, b)

    if brightness < 45:
        return "Black"
    if brightness > 220 and mx - mn < 25:
        return "White"
    if mx - mn < 20:
        if brightness < 110:
            return "Dark Grey"
        return "Grey"

    if r > 170 and g > 150 and b < 110:
        return "Yellow"
    if r > 180 and g > 90 and b < 100:
        return "Orange"
    if r > 150 and g < 100 and b < 120:
        return "Red"
    if r > 150 and g < 130 and b > 130:
        return "Pink"
    if r > 110 and b > 100 and g < 110:
        return "Purple"
    if b > r * 1.15 and b > g * 1.05:
        return "Blue"
    if g > r * 1.12 and g > b * 1.05:
        return "Green"
    if r > 120 and g > 90 and b < 90:
        return "Brown"
    if r > 150 and g > 130 and b < 120:
        return "Beige"

    return "Mixed Color"


def analyze_colors(image):
    img = image.convert("RGB")
    img.thumbnail((120, 120))

    pixels = list(img.getdata())

    # Ignore extremely bright/dark pixels when possible
    useful = []
    for r, g, b in pixels:
        brightness = (r + g + b) / 3
        if 20 < brightness < 245:
            useful.append((r, g, b))

    if not useful:
        useful = pixels

    # Divide image into 3 horizontal areas
    w, h = img.size
    regions = [
        useful,
        list(img.crop((0, 0, w, max(1, h // 2))).getdata()),
        list(img.crop((0, h // 2, w, h)).getdata())
    ]

    colors = []

    for region in regions:
        if not region:
            continue

        avg_r = sum(p[0] for p in region) / len(region)
        avg_g = sum(p[1] for p in region) / len(region)
        avg_b = sum(p[2] for p in region) / len(region)

        colors.append(get_color_name(avg_r, avg_g, avg_b))

    # Dominant overall color
    avg_r = sum(p[0] for p in useful) / len(useful)
    avg_g = sum(p[1] for p in useful) / len(useful)
    avg_b = sum(p[2] for p in useful) / len(useful)

    dominant = get_color_name(avg_r, avg_g, avg_b)

    unique_colors = []
    for c in colors:
        if c not in unique_colors:
            unique_colors.append(c)

    if len(unique_colors) >= 2:
        color_text = ", ".join(unique_colors[:3])
    else:
        color_text = dominant

    return dominant, color_text, (avg_r, avg_g, avg_b)


# ---------------------------------------------------------
# IMAGE VISUAL FEATURES
# ---------------------------------------------------------

def visual_features(image):
    img = image.convert("RGB")
    img = img.resize((80, 80))

    pixels = list(img.getdata())

    # Brightness
    brightness = sum((r + g + b) / 3 for r, g, b in pixels) / len(pixels)

    # Color variation
    avg_r = sum(p[0] for p in pixels) / len(pixels)
    avg_g = sum(p[1] for p in pixels) / len(pixels)
    avg_b = sum(p[2] for p in pixels) / len(pixels)

    variation = 0
    for r, g, b in pixels:
        variation += abs(r - avg_r) + abs(g - avg_g) + abs(b - avg_b)

    variation /= len(pixels)

    # Edge/texture estimation
    edges = 0

    for y in range(1, 79):
        for x in range(1, 79):
            current = img.getpixel((x, y))
            left = img.getpixel((x - 1, y))
            up = img.getpixel((x, y - 1))

            diff1 = sum(abs(current[i] - left[i]) for i in range(3))
            diff2 = sum(abs(current[i] - up[i]) for i in range(3))

            if diff1 + diff2 > 120:
                edges += 1

    texture = edges / (78 * 78)

    return brightness, variation, texture


# ---------------------------------------------------------
# OUTFIT CLASSIFICATION
# ---------------------------------------------------------

def classify_outfit(image):
    dominant, color_text, rgb = analyze_colors(image)
    brightness, variation, texture = visual_features(image)

    r, g, b = rgb

    # These visual rules deliberately avoid random selection.
    # They use different image characteristics to create different results.

    # Bright colorful / patterned traditional-looking images
    if variation > 55 and texture > 0.16:
        category = "Traditional / Ethnic Outfit"
        style = "Traditional"
        confidence = 82
        reason = "The image contains strong color variation and detailed visual texture."

    # Darker lower-contrast outfits
    elif brightness < 95 and variation < 48:
        category = "Jeans / Top / Casual Outfit"
        style = "Casual"
        confidence = 76
        reason = "The image has a darker, simple visual composition often seen in casual outfits."

    # Light/simple outfits
    elif brightness > 175 and variation < 42:
        category = "Kurti / Light Casual Outfit"
        style = "Elegant Casual"
        confidence = 74
        reason = "The image has a light and relatively simple color composition."

    # Strong blue/dark-blue appearance
    elif b > r * 1.12 and b > g * 1.05:
        category = "Denim / Western Outfit"
        style = "Western Casual"
        confidence = 80
        reason = "Blue tones are visually dominant in the image."

    # Strong red/pink/orange appearance
    elif r > g * 1.18 and r > b * 1.18:
        category = "Festive / Ethnic Outfit"
        style = "Festive"
        confidence = 79
        reason = "Warm red/pink tones dominate the image."

    # Green dominant
    elif g > r * 1.15 and g > b * 1.05:
        category = "Casual / Indo-Western Outfit"
        style = "Indo-Western"
        confidence = 77
        reason = "Green tones are visually prominent in the image."

    else:
        category = "Smart Casual Outfit"
        style = "Modern Casual"
        confidence = 72
        reason = "The image has a balanced color composition with moderate visual variation."

    return category, style, confidence, reason, dominant, color_text


# ---------------------------------------------------------
# SUGGESTIONS
# ---------------------------------------------------------

def make_suggestions(category, style, dominant):

    if "Traditional" in category or "Ethnic" in category or "Festive" in category:
        return {
            "do": [
                "Add small or medium traditional earrings.",
                "Try a simple bun, braid or soft waves.",
                "Choose juttis, ethnic sandals or traditional footwear.",
                "Keep makeup elegant with defined eyes and a soft lip shade.",
                "A matching dupatta or subtle traditional accessory can complete the look.",
                "Gold or oxidised jewellery can complement the outfit.",
                "Choose a handbag that matches the outfit instead of a very sporty bag.",
                "Keep jewellery balanced so the outfit remains the main focus.",
                "Use a small bindi if it matches the overall traditional look.",
                "Choose footwear in a neutral or matching shade."
            ],
            "dont": [
                "Avoid wearing too many heavy accessories together.",
                "Avoid very sporty sneakers with a strongly traditional outfit.",
                "Avoid mixing too many unrelated colours.",
                "Avoid extremely heavy makeup if the outfit is already detailed.",
                "Avoid oversized bags with a festive look."
            ]
        }

    if "Jeans" in category or "Western" in category or "Casual" in category:
        return {
            "do": [
                "Pair jeans with clean white or neutral sneakers.",
                "Try a simple crossbody or shoulder bag.",
                "Soft waves, ponytail or open hair can work well.",
                "Use light natural makeup for a casual appearance.",
                "A watch or minimal bracelet can add a polished touch.",
                "Try a denim jacket or light layer when appropriate.",
                "Keep accessories minimal and modern.",
                "Choose footwear that matches the casual vibe.",
                "Neutral sneakers work well with many denim looks.",
                "A simple chain or small earrings can complete the outfit."
            ],
            "dont": [
                "Avoid too many heavy accessories.",
                "Avoid formal jewellery with a very sporty outfit.",
                "Avoid combining too many bold patterns.",
                "Avoid uncomfortable footwear for a casual outfit.",
                "Avoid an oversized bag if the outfit is already loose."
            ]
        }

    if "Kurti" in category or "Indo-Western" in category:
        return {
            "do": [
                "Try small jhumkas or simple earrings.",
                "Pair the kurti with comfortable sandals or juttis.",
                "A straight hairstyle, braid or soft waves can work well.",
                "Use light makeup with a natural lip colour.",
                "A matching dupatta can enhance the outfit.",
                "Choose a small ethnic or neutral handbag.",
                "A simple bracelet or watch can add a neat finish.",
                "Keep the colour combination balanced.",
                "Choose footwear that complements the kurti colour.",
                "For a modern look, add minimal accessories."
            ],
            "dont": [
                "Avoid very heavy jewellery with a simple kurti.",
                "Avoid mixing too many bright colours.",
                "Avoid overly sporty footwear with a formal ethnic kurti.",
                "Avoid excessive makeup for a simple daytime look.",
                "Avoid accessories that hide the neckline or design."
            ]
        }

    return {
        "do": [
            "Use minimal accessories for a clean appearance.",
            "Choose footwear that matches the outfit style.",
            "Try a neat ponytail, open hair or soft waves.",
            "Use natural makeup for a balanced look.",
            "Choose a handbag in a matching or neutral shade.",
            "Add a simple watch or bracelet.",
            "Keep the colour combination coordinated.",
            "Choose comfortable footwear for everyday wear.",
            "Use one statement accessory instead of many.",
            "Keep the overall look clean and balanced."
        ],
        "dont": [
            "Avoid mixing too many colours.",
            "Avoid too many statement accessories together.",
            "Avoid footwear that clashes with the outfit style.",
            "Avoid very heavy makeup for a simple outfit.",
            "Avoid oversized accessories if the outfit is already detailed."
        ]
    }


# ---------------------------------------------------------
# ANALYZE IMAGE
# ---------------------------------------------------------

def analyze_outfit(image):
    category, style, confidence, reason, dominant, color_text = classify_outfit(image)

    suggestions = make_suggestions(category, style, dominant)

    return {
        "category": category,
        "dominant_color": dominant,
        "color": color_text,
        "style": style,
        "score": confidence,
        "reason": reason,
        "do": suggestions["do"],
        "dont": suggestions["dont"]
    }


# ---------------------------------------------------------
# WEB PAGE
# ---------------------------------------------------------

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
    background: linear-gradient(135deg, #f8f4ff, #fff8f0);
    color: #29233d;
}

.container {
    max-width: 900px;
    margin: auto;
    padding: 25px;
}

.header {
    text-align: center;
    margin-bottom: 25px;
}

.header h1 {
    font-size: 38px;
    margin-bottom: 8px;
}

.header p {
    color: #6d667d;
}

.card {
    background: white;
    border-radius: 22px;
    padding: 25px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.upload {
    border: 2px dashed #b9a9d8;
    border-radius: 18px;
    padding: 35px;
    text-align: center;
    cursor: pointer;
}

.upload input {
    margin-top: 15px;
}

button {
    border: none;
    border-radius: 12px;
    padding: 14px 25px;
    font-size: 16px;
    cursor: pointer;
    margin-top: 15px;
}

.preview {
    max-width: 300px;
    max-height: 350px;
    display: none;
    margin: 20px auto;
    border-radius: 18px;
}

.loading {
    display: none;
    text-align: center;
    padding: 15px;
}

.result {
    display: none;
}

.grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
}

.box {
    background: #faf8ff;
    border-radius: 15px;
    padding: 18px;
}

.box h3 {
    margin-top: 0;
}

ul {
    padding-left: 22px;
}

li {
    margin-bottom: 9px;
}

@media(max-width:650px) {
    .grid {
        grid-template-columns: 1fr;
    }

    .header h1 {
        font-size: 30px;
    }

    .container {
        padding: 15px;
    }
}

</style>
</head>

<body>

<div class="container">

<div class="header">
<h1>✨ AI Outfit Analyzer</h1>
<p>Upload your outfit photo and get personalized style suggestions.</p>
</div>

<div class="card">

<div class="upload">
<strong>📸 Upload Outfit Image</strong>
<br>
<input type="file" id="imageInput" accept="image/*">
</div>

<img id="preview" class="preview">

<button onclick="analyze()">Analyze Outfit</button>

<div id="loading" class="loading">
⏳ Analyzing your outfit...
</div>

</div>

<div id="result" class="result">

<div class="card">

<h2>✨ Analysis Result</h2>

<div class="grid">

<div class="box">
<h3>👗 Category</h3>
<p id="category"></p>
</div>

<div class="box">
<h3>🎨 Dominant Color</h3>
<p id="color"></p>
</div>

<div class="box">
<h3>✨ Style</h3>
<p id="style"></p>
</div>

<div class="box">
<h3>⭐ Style Score</h3>
<p id="score"></p>
</div>

</div>

<p><strong>🔎 Why this result?</strong></p>
<p id="reason"></p>

</div>

<div class="card">

<h2>💖 What You Should Do</h2>
<ul id="doList"></ul>

</div>

<div class="card">

<h2>⚠️ What You Should Avoid</h2>
<ul id="dontList"></ul>

</div>

</div>

</div>

<script>

let selectedImage = null;

document.getElementById("imageInput").addEventListener("change", function(e) {

    selectedImage = e.target.files[0];

    if (!selectedImage) return;

    const preview = document.getElementById("preview");

    preview.src = URL.createObjectURL(selectedImage);
    preview.style.display = "block";
});


async function analyze() {

    if (!selectedImage) {
        alert("Please upload an outfit image first.");
        return;
    }

    const loading = document.getElementById("loading");
    const result = document.getElementById("result");

    loading.style.display = "block";
    result.style.display = "none";

    const formData = new FormData();
    formData.append("image", selectedImage);

    try {

        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        document.getElementById("category").innerText = data.category;
        document.getElementById("color").innerText =
            data.dominant_color + " (" + data.color + ")";

        document.getElementById("style").innerText = data.style;
        document.getElementById("score").innerText = data.score + "/100";
        document.getElementById("reason").innerText = data.reason;

        const doList = document.getElementById("doList");
        const dontList = document.getElementById("dontList");

        doList.innerHTML = "";
        dontList.innerHTML = "";

        data.do.forEach(function(item) {
            const li = document.createElement("li");
            li.innerText = item;
            doList.appendChild(li);
        });

        data.dont.forEach(function(item) {
            const li = document.createElement("li");
            li.innerText = item;
            dontList.appendChild(li);
        });

        result.style.display = "block";

    } catch (error) {

        alert("Unable to analyze image. Please try again.");

    } finally {

        loading.style.display = "none";

    }
}

</script>

</body>
</html>
"""


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/analyze", methods=["POST"])
def analyze():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]

    try:
        image = Image.open(file.stream)
        result = analyze_outfit(image)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------
# LOCAL RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

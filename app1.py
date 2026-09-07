from flask import Flask, request, jsonify, render_template_string
from PIL import Image

app = Flask(__name__)


# =========================================================
# COLOR DETECTION
# =========================================================

def get_color_name(r, g, b):
    brightness = (r + g + b) / 3
    difference = max(r, g, b) - min(r, g, b)

    if brightness < 45:
        return "Black"

    if brightness > 220 and difference < 30:
        return "White"

    if difference < 25:
        if brightness < 110:
            return "Dark Grey"
        return "Grey"

    if r > 175 and g > 145 and b < 115:
        return "Yellow"

    if r > 185 and g > 90 and b < 115:
        return "Orange"

    if r > 160 and g < 115 and b < 125:
        return "Red"

    if r > 150 and g < 145 and b > 125:
        return "Pink"

    if r > 120 and b > 115 and g < 120:
        return "Purple"

    if b > r * 1.15 and b > g * 1.03:
        return "Blue"

    if g > r * 1.12 and g > b * 1.04:
        return "Green"

    if r > 120 and g > 85 and b < 90:
        return "Brown"

    if r > 145 and g > 125 and b < 120:
        return "Beige"

    return "Mixed Color"


# =========================================================
# IMAGE FEATURES
# =========================================================

def get_image_features(image):
    img = image.convert("RGB")
    img = img.resize((80, 80))

    pixels = list(img.getdata())

    total = len(pixels)

    avg_r = sum(p[0] for p in pixels) / total
    avg_g = sum(p[1] for p in pixels) / total
    avg_b = sum(p[2] for p in pixels) / total

    brightness = (avg_r + avg_g + avg_b) / 3

    variation = sum(
        abs(p[0] - avg_r)
        + abs(p[1] - avg_g)
        + abs(p[2] - avg_b)
        for p in pixels
    ) / total

    edge_count = 0

    for y in range(1, 79):
        for x in range(1, 79):

            current = img.getpixel((x, y))
            left = img.getpixel((x - 1, y))
            top = img.getpixel((x, y - 1))

            horizontal = (
                abs(current[0] - left[0])
                + abs(current[1] - left[1])
                + abs(current[2] - left[2])
            )

            vertical = (
                abs(current[0] - top[0])
                + abs(current[1] - top[1])
                + abs(current[2] - top[2])
            )

            if horizontal + vertical > 130:
                edge_count += 1

    texture = edge_count / (78 * 78)

    dominant_color = get_color_name(
        avg_r,
        avg_g,
        avg_b
    )

    return {
        "r": avg_r,
        "g": avg_g,
        "b": avg_b,
        "brightness": brightness,
        "variation": variation,
        "texture": texture,
        "dominant_color": dominant_color
    }


# =========================================================
# OUTFIT CATEGORY
# =========================================================

def detect_outfit(image):

    features = get_image_features(image)

    r = features["r"]
    g = features["g"]
    b = features["b"]

    brightness = features["brightness"]
    variation = features["variation"]
    texture = features["texture"]
    color = features["dominant_color"]

    detailed = variation > 52 or texture > 0.16
    simple = variation < 42 and texture < 0.13

    # Traditional / saree / ethnic
    if detailed and color in [
        "Red",
        "Pink",
        "Orange",
        "Purple",
        "Yellow"
    ]:
        category = "Traditional / Saree / Ethnic"
        style = "Traditional"
        score = 90

    # Denim / jeans
    elif color == "Blue" and brightness < 150:
        category = "Jeans / Denim Outfit"
        style = "Western Casual"
        score = 87

    # Green / kurti / indo-western
    elif color == "Green" and detailed:
        category = "Kurti / Indo-Western"
        style = "Indo-Western"
        score = 86

    # Light outfits / kurti
    elif brightness > 175 and simple:
        category = "Kurti / Light Casual"
        style = "Elegant Casual"
        score = 84

    # Dark simple outfit
    elif brightness < 90 and simple:
        category = "Western Casual Outfit"
        style = "Modern Casual"
        score = 82

    # Detailed outfit
    elif detailed:
        category = "Ethnic / Stylish Outfit"
        style = "Stylish Ethnic"
        score = 85

    # General casual
    else:
        category = "Jeans / Top / Casual Outfit"
        style = "Casual"
        score = 80

    return category, style, score


# =========================================================
# CATEGORY-SPECIFIC SUGGESTIONS
# =========================================================

SUGGESTIONS = {

    "Traditional": [
        [
            "Add elegant jhumkas and a small bindi.",
            "Try a neat bun or soft braid."
        ],
        [
            "Pair the outfit with ethnic juttis.",
            "Choose light gold or oxidised jewellery."
        ],
        [
            "Use soft makeup with defined eyes.",
            "Try a matching traditional handbag."
        ],
        [
            "Try a low bun with a simple hair accessory.",
            "Choose comfortable ethnic sandals."
        ],
        [
            "Keep jewellery elegant and balanced.",
            "A matching dupatta can complete the look."
        ]
    ],

    "Festive": [
        [
            "Add statement earrings for a festive look.",
            "Try soft curls or a decorated braid."
        ],
        [
            "Choose a small matching clutch.",
            "Use warm-toned makeup with a soft lip."
        ],
        [
            "Pair it with embellished juttis.",
            "Keep jewellery coordinated."
        ],
        [
            "Try a subtle bindi.",
            "A neat bun will give a polished look."
        ]
    ],

    "Western Casual": [
        [
            "Pair jeans with clean white sneakers.",
            "Try open hair or soft waves."
        ],
        [
            "Add a minimal watch or bracelet.",
            "Choose a small crossbody bag."
        ],
        [
            "Use natural everyday makeup.",
            "Try small hoops or a simple chain."
        ],
        [
            "Try a denim jacket for layering.",
            "Choose comfortable casual footwear."
        ],
        [
            "Keep accessories simple and modern.",
            "Use a neutral handbag."
        ]
    ],

    "Casual": [
        [
            "Pair jeans with sneakers or casual shoes.",
            "Try a simple ponytail or open hair."
        ],
        [
            "Add small hoops or minimal earrings.",
            "A crossbody bag will suit the outfit."
        ],
        [
            "Use light natural makeup.",
            "Add a simple watch."
        ],
        [
            "Try a tucked-in top for a polished look.",
            "Choose neutral footwear."
        ],
        [
            "Add a simple bracelet.",
            "Try a lightweight jacket if needed."
        ]
    ],

    "Indo-Western": [
        [
            "Try small jhumkas with the kurti.",
            "Pair it with sandals or juttis."
        ],
        [
            "Try a soft braid or open waves.",
            "Choose a simple matching handbag."
        ],
        [
            "Use natural makeup with a soft lip colour.",
            "Add a simple bracelet or watch."
        ],
        [
            "Try a matching dupatta.",
            "Keep the footwear comfortable."
        ],
        [
            "Choose minimal jewellery.",
            "A small shoulder bag can complete the look."
        ]
    ],

    "Elegant Casual": [
        [
            "Keep jewellery minimal and elegant.",
            "Try soft waves or a neat ponytail."
        ],
        [
            "Choose neutral sandals or clean sneakers.",
            "Use fresh natural makeup."
        ],
        [
            "Add a small matching handbag.",
            "A simple watch can polish the look."
        ]
    ],

    "Stylish Ethnic": [
        [
            "Add small ethnic earrings.",
            "Try a braid or soft waves."
        ],
        [
            "Choose juttis or ethnic sandals.",
            "Use light makeup with a natural lip."
        ],
        [
            "Try a simple bracelet.",
            "Keep the handbag small and elegant."
        ],
        [
            "A subtle bindi can enhance the look.",
            "Choose accessories matching the outfit."
        ]
    ],

    "Modern Casual": [
        [
            "Choose simple modern accessories.",
            "Try soft waves or a neat ponytail."
        ],
        [
            "Pair the outfit with neutral footwear.",
            "Use natural everyday makeup."
        ],
        [
            "Add a minimal watch.",
            "Choose a small crossbody bag."
        ]
    ]
}


AVOID = {

    "Traditional": [
        "Avoid too many heavy jewellery pieces together.",
        "Avoid sporty footwear with a strongly traditional outfit."
    ],

    "Festive": [
        "Avoid using several statement accessories together.",
        "Avoid mixing too many unrelated bright colours."
    ],

    "Western Casual": [
        "Avoid heavy traditional jewellery with a western outfit.",
        "Avoid combining too many bold patterns."
    ],

    "Casual": [
        "Avoid excessive accessories with a simple jeans-and-top look.",
        "Avoid uncomfortable formal footwear."
    ],

    "Indo-Western": [
        "Avoid very heavy jewellery with a simple kurti.",
        "Avoid mixing too many bright colours."
    ],

    "Elegant Casual": [
        "Avoid overloading the outfit with accessories.",
        "Avoid very heavy makeup for daytime."
    ],

    "Stylish Ethnic": [
        "Avoid mixing too many different jewellery styles.",
        "Avoid footwear that clashes with the outfit."
    ],

    "Modern Casual": [
        "Avoid too many statement accessories.",
        "Avoid mixing unrelated colours."
    ]
}


# =========================================================
# CREATE DIFFERENT SUGGESTIONS
# =========================================================

def create_suggestions(image, style):

    features = get_image_features(image)

    number = int(
        features["r"]
        + features["g"] * 2
        + features["b"] * 3
        + features["brightness"] * 5
        + features["variation"] * 7
        + features["texture"] * 1000
    )

    if style not in SUGGESTIONS:
        style = "Modern Casual"

    choices = SUGGESTIONS[style]

    selected = choices[number % len(choices)]

    avoid_choices = AVOID.get(
        style,
        AVOID["Modern Casual"]
    )

    start = number % len(avoid_choices)

    avoid = [
        avoid_choices[start],
        avoid_choices[(start + 1) % len(avoid_choices)]
    ]

    return selected, avoid


# =========================================================
# FINAL ANALYSIS
# =========================================================

def analyze_outfit(image):

    features = get_image_features(image)

    category, style, score = detect_outfit(image)

    suggestions, avoid = create_suggestions(
        image,
        style
    )

    dominant_color = features["dominant_color"]

    variation = features["variation"]
    texture = features["texture"]
    brightness = features["brightness"]

    reasons = []

    if variation > 55:
        reasons.append("multiple colour variations")

    if texture > 0.16:
        reasons.append("visible outfit details")

    if brightness > 175:
        reasons.append("bright overall appearance")

    if brightness < 90:
        reasons.append("deep visual tones")

    if not reasons:
        reasons.append("balanced colour composition")

    reason = (
        "The result is based on "
        + ", ".join(reasons)
        + " detected in the uploaded image."
    )

    return {
        "category": category,
        "dominant_color": dominant_color,
        "style": style,
        "score": score,
        "reason": reason,
        "do": suggestions,
        "dont": avoid
    }


# =========================================================
# WEBSITE HTML
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

    padding: 30px 18px 50px;
}

.header {

    text-align: center;

    margin-bottom: 25px;
}

.header h1 {

    margin: 0;

    font-size: 42px;

    font-weight: 800;

    background:
        linear-gradient(
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

.card {

    background: rgba(255,255,255,0.96);

    border-radius: 24px;

    padding: 25px;

    margin-bottom: 22px;

    box-shadow:
        0 15px 45px rgba(48,55,90,0.12);
}

.upload-box {

    border-radius: 22px;

    padding: 40px 20px;

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
        0 12px 30px rgba(79,70,229,0.28);
}

.upload-box h2 {

    margin: 0 0 8px;

    font-size: 26px;
}

.upload-box p {

    margin: 5px 0 20px;

    opacity: 0.92;
}

.file-input {

    display: inline-block;

    background: white;

    color: #374151;

    padding: 12px 18px;

    border-radius: 12px;

    cursor: pointer;

    font-weight: 700;
}

.file-input input {

    display: none;
}

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

    font-size: 19px;

    font-weight: 700;

    cursor: pointer;

    box-shadow:
        0 8px 22px rgba(79,70,229,0.30);
}

.loading {

    display: none;

    text-align: center;

    margin-top: 18px;

    font-weight: 600;

    color: #5b21b6;
}

.result {

    display: none;
}

.result-title {

    margin-top: 0;

    font-size: 28px;
}

.grid {

    display: grid;

    grid-template-columns:
        repeat(2, 1fr);

    gap: 16px;
}

.info-box {

    padding: 20px;

    border-radius: 18px;

    background: #f7f8ff;

    border: 1px solid #e5e7f3;
}

.info-box h3 {

    margin: 0 0 9px;

    font-size: 14px;

    color: #70758a;

    text-transform: uppercase;
}

.info-box p {

    margin: 0;

    font-size: 19px;

    font-weight: 700;

    color: #242842;
}

.reason {

    margin-top: 18px;

    padding: 18px;

    border-radius: 17px;

    background: #f1f3ff;

    line-height: 1.5;
}

.reason strong {

    display: block;

    margin-bottom: 7px;
}

.suggestion-card {

    border-radius: 20px;

    padding: 22px;

    margin-top: 18px;

    background: white;

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

.footer {

    text-align: center;

    color: #7b8092;

    margin-top: 25px;

    font-size: 14px;
}

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
Choose a clear outfit photo for personalized analysis.
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

<p id="category">-</p>

</div>


<div class="info-box">

<h3>🎨 Dominant Color</h3>

<p id="color">-</p>

</div>


<div class="info-box">

<h3>✨ Style</h3>

<p id="style">-</p>

</div>


<div class="info-box">

<h3>⭐ Style Score</h3>

<p id="score">-</p>

</div>


</div>


<div class="reason">

<strong>
🔎 Why This Result?
</strong>

<span id="reason">-</span>

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
.addEventListener(
    "change",
    function(event) {

        selectedImage = event.target.files[0];

        if (!selectedImage) {
            return;
        }

        const preview =
            document.getElementById("preview");

        preview.src =
            URL.createObjectURL(
                selectedImage
            );

        preview.style.display = "block";
    }
);


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


    const formData =
        new FormData();

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
            await response.json();


        if (data.error) {

            alert(data.error);

            return;
        }


        document
        .getElementById("category")
        .innerText =
            data.category;


        document
        .getElementById("color")
        .innerText =
            data.dominant_color;


        document
        .getElementById("style")
        .innerText =
            data.style;


        document
        .getElementById("score")
        .innerText =
            data.score + "/100";


        document
        .getElementById("reason")
        .innerText =
            data.reason;


        const doList =
            document.getElementById(
                "doList"
            );

        const dontList =
            document.getElementById(
                "dontList"
            );


        doList.innerHTML = "";

        dontList.innerHTML = "";


        data.do.forEach(
            function(item) {

                const li =
                    document.createElement(
                        "li"
                    );

                li.innerText = item;

import os
from flask import Flask, render_template, request, jsonify
from google import genai

# Load local .env file if it exists
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                try:
                    key, val = line.strip().split("=", 1)
                    os.environ[key.strip()] = val.strip()
                except ValueError:
                    pass

# ============================================================
# GEMINI API KEY
# ============================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

app = Flask(__name__)

# ============================================================
# TOOL 1 — ADD
# ============================================================

def add(a: float, b: float) -> dict:
    """Adds two numbers. Use this tool when the user wants to calculate the sum of two numbers.

    Args:
        a: The first number.
        b: The second number.
    """
    print(f"\n🔧 TOOL CALLED: add ({a} + {b})")
    result = a + b
    return {
        "operation": "addition",
        "a": a,
        "b": b,
        "result": result
    }


# ============================================================
# TOOL 2 — MULTIPLY
# ============================================================

def multiply(a: float, b: float) -> dict:
    """Multiplies two numbers. Use this tool when the user wants to multiply two numbers.

    Args:
        a: The first number.
        b: The second number.
    """
    print(f"\n🔧 TOOL CALLED: multiply ({a} * {b})")
    result = a * b
    return {
        "operation": "multiplication",
        "a": a,
        "b": b,
        "result": result
    }


# ============================================================
# TOOL 3 — PRODUCT INFO
# ============================================================

def product(product_name: str) -> dict:
    """Gets details for a hardware device or product. Use this tool when the user asks for details of a device or product.

    Args:
        product_name: The name of the product (e.g., 'iphone 15', 'samsung s24', 'macbook air').
    """
    print(f"\n🔧 TOOL CALLED: product ({product_name})")
    products = {
        "iphone 15": {
            "name": "iPhone 15",
            "category": "Smartphone",
            "price": 69999,
            "currency": "INR"
        },
        "samsung s24": {
            "name": "Samsung Galaxy S24",
            "category": "Smartphone",
            "price": 74999,
            "currency": "INR"
        },
        "macbook air": {
            "name": "MacBook Air",
            "category": "Laptop",
            "price": 99999,
            "currency": "INR"
        }
    }
    prod = products.get(product_name.lower())
    if prod:
        return prod
    return {
        "error": f"Product '{product_name}' not found."
    }


# ============================================================
# TOOL 4 — WEATHER
# ============================================================

def weather(city: str) -> dict:
    """Gets the weather conditions for a specified city. Use this tool when the user asks about the weather, temperature, humidity, wind speed, or climate of a city.

    Args:
        city: The name of the city (e.g., 'mumbai', 'delhi', 'london', 'new york', 'tokyo').
    """
    print(f"\n🔧 TOOL CALLED: weather ({city})")
    weather_data = {
        "mumbai": {
            "city": "Mumbai",
            "temperature": "30°C",
            "condition": "Humid and partly cloudy",
            "humidity": "82%",
            "wind": "12 km/h"
        },
        "delhi": {
            "city": "Delhi",
            "temperature": "34°C",
            "condition": "Hazy and warm",
            "humidity": "55%",
            "wind": "8 km/h"
        },
        "london": {
            "city": "London",
            "temperature": "18°C",
            "condition": "Showers and windy",
            "humidity": "75%",
            "wind": "22 km/h"
        },
        "new york": {
            "city": "New York",
            "temperature": "22°C",
            "condition": "Sunny and clear",
            "humidity": "45%",
            "wind": "10 km/h"
        },
        "tokyo": {
            "city": "Tokyo",
            "temperature": "26°C",
            "condition": "Mostly cloudy",
            "humidity": "60%",
            "wind": "15 km/h"
        }
    }
    info = weather_data.get(city.lower())
    if info:
        return info
    return {
        "city": city,
        "temperature": "24°C",
        "condition": "Partly cloudy",
        "humidity": "50%",
        "wind": "10 km/h"
    }


# ============================================================
# REGISTER TOOLS
# ============================================================

tools = [
    add,
    multiply,
    product,
    weather
]

# ============================================================
# CHAT SESSION
# ============================================================

chat = client.chats.create(
    model="gemini-3.5-flash",
    config={
        "tools": tools,
        "system_instruction": """
        You are a helpful AI assistant.

        Rules:
        1. Use the add tool when the user wants to calculate the sum of two numbers.
        2. Use the multiply tool when the user wants to multiply two numbers.
        3. Use the product tool when the user asks for product details.
        4. Use the weather tool when the user asks about the weather in a city.
        5. For everything else, answer normally.
        6. Be concise and friendly.
        """
    }
)

# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat_api():

    user_message = request.json.get("message")

    try:

        response = chat.send_message(user_message)

        return jsonify({
            "reply": response.text
        })

    except Exception as e:

        return jsonify({
            "reply": f"Error: {str(e)}"
        })


# ============================================================
# START APP
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
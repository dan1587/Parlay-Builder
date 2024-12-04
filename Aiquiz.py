from quart import Quart, request, render_template_string
from openai import OpenAI
import logging
from dotenv import load_dotenv
import datetime

# Set up logging to display errors
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Initialize Quart app
app = Quart(__name__)

# HTML template for the page
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parlay Builder</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;

        }
        form {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #fff;
            color: #000;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            color: #155724;
            margin-top: 20px;
        }
        label {
            display: block;
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        input[type="text"] {
            display: block;
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        input[type="submit"] {
            background-color: #28a745;
            color: #fff;
            border: none;
            padding: 10px;
            cursor: pointer
            font-size: 1.1em;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        input[type="submit"]:hover {
            background-color: #218838;
        }
        pre {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 1em;
        }
    </style>
</head>
<body>
    <h1>Parlay Builder</h1>
    <form action="/chat" method="post">
        <label for="user_input">What sport would you like to bet on tonight?</label>
        <input type="text" id="user_input" name="user_input" placeholder="e.g., basketball, football, etc." required>
        <input type="submit" value="Generate Parlay">
    </form>
    {% if assistant_reply %}
    <h2 style="text-align:center;">Generated Parlay:</h2>
    <pre>{{ assistant_reply }}</pre>
    {% endif %}
</body>
</html>
'''

@app.route('/')
async def index():
    """Render the main form."""
    return await render_template_string(html_template)

@app.route('/chat', methods=['POST'])
async def chat():
    """Handle form submission and generate a parlay."""
    try:
        # Get user input from the form
        form_data = await request.form
        user_input = form_data['user_input']

        # Get the current date
        current_date = datetime.datetime.now().strftime("%B %d, %Y")

        # Query OpenAI API for a parlay
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a sports betting expert generating accurate and up-to-date parlays with odds."},
                {
                    "role": "user",
                    "content": (
                        f"Today is {current_date}. Create a 3-leg parlay for '{user_input}'. Each leg should include specific details "
                        "like player props, team outcomes, or over/under totals, and include betting odds for each leg."
                    ),
                },
            ],
        )

        # Extract the response content
        assistant_reply = response.choices[0].message.content
        return await render_template_string(html_template, assistant_reply=assistant_reply)

    except Exception as e:
        # Log and display errors
        logging.error(f"Error: {e}")
        return await render_template_string(html_template, assistant_reply="Something went wrong. Please try again.")

if __name__ == '__main__':
    app.run(debug=True)

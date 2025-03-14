import os
import requests
import json
from flask import Flask, render_template, request, jsonify, url_for

# Initialize Flask App
app = Flask(__name__)

# Gemini API Key
API_KEY = "AIzaSyDuzYweSAG300X7ndo14rF6lwJVaUF3gF0"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

# Create a chatbot function using direct API requests
def chat_with_gemini(user_input):
    try:
        # Prepare the request payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": user_input}
                    ]
                }
            ]
        }
        
        # Make the API request
        response = requests.post(
            f"{API_URL}?key={API_KEY}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        # Parse the response
        if response.status_code == 200:
            response_data = response.json()
            # Extract text from the response
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                if "content" in response_data["candidates"][0] and "parts" in response_data["candidates"][0]["content"]:
                    parts = response_data["candidates"][0]["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]
            
            return "I received a response but couldn't extract the message content."
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return f"Sorry, there was an error processing your request. (Status code: {response.status_code})"
    
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        return "Sorry, I encountered an error processing your request."

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Routes for other pages
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/complaintsform')
def complaintsform():
    return render_template('complaintsform.html')

@app.route('/housingreg')
def housing_reg():
    return render_template('housingreg.html')

def chat_with_gemini(user_input):
    # Simple mock response for testing
    return f"You said: {user_input}. This is a test response from the chatbot."

# API route for chatbot
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        bot_response = chat_with_gemini(user_message)
        return jsonify({"response": bot_response})
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"response": "Sorry, something went wrong with the chatbot."})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=10000, debug=True)
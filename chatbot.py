import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, url_for

# Initialize Flask App
app = Flask(__name__)

# Set up Google Gemini API
genai.configure(api_key="AIzaSyARPqVp3ZP3VVrCw_TdidlCAnF_vtuGpzg")

# Create a chatbot function
def chat_with_gemini(user_input):
    try:
        model = genai.GenerativeModel('gemini-pro')  # Use the Gemini-Pro model
        response = model.generate_content(user_input)
        return response.text if response else "Sorry, I couldn't process that."
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
def complaints_form():
    return render_template('complaintsform.html')

@app.route('/housingreg')
def housing_reg():
    return render_template('housingreg.html')

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
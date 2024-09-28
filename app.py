import os
from flask import Flask, request, jsonify
import pandas as pd
from werkzeug.utils import secure_filename
import requests
import time

app = Flask(__name__)

# Configuration
# app.config['SECRET_KEY'] = 'supersecretkey'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

# Initialize the Groq API key from the environment variable
API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_ID = "llama3-8b-8192"

# Function to check if file type is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to process the uploaded file
def process_file(file):
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
    except Exception as e:
        return None, f"Failed to read the file: {str(e)}"
    
    if 'Review' not in df.columns:
        return None, "Missing 'Review' column in file."
    
    reviews = df['Review'].dropna().tolist()
    if len(reviews) == 0:
        return None, "No reviews found in the 'Review' column."
    
    return reviews, None

# Function to classify the sentiment as positive, negative, or neutral
def classify_sentiment(sentiment_content):
    sentiment_content_lower = sentiment_content.lower()
    
    if 'positive' in sentiment_content_lower:
        return 'positive'
    elif 'negative' in sentiment_content_lower:
        return 'negative'
    else:
        return 'neutral'

# Function to analyze sentiment using Groq API
def analyze_sentiment(review):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": f"Analyze the sentiment of this review: '{review}'"
            }
        ]
    }

    retry_attempts = 3
    for attempt in range(retry_attempts):
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=data)
            response.raise_for_status()  # Will raise an error for non-200 responses
            response_data = response.json()

            # Extract the content of the sentiment analysis
            sentiment_content = response_data['choices'][0]['message']['content']
            return {"sentiment": sentiment_content}

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                wait_time = 2 ** attempt
                print(f"Rate limit reached. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)  # Exponential backoff
            else:
                return {"error": f"HTTP error occurred: {str(e)}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Request exception: {str(e)}"}

    return {"error": "Failed after multiple retries due to rate limiting."}

# Route to upload and process files
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file format. Allowed formats: CSV, XLSX."}), 400
    
    filename = secure_filename(file.filename)
    
    # Process the uploaded file to extract reviews
    reviews, error = process_file(file)
    if error:
        return jsonify({"error": error}), 400
    
    # Initialize counters for sentiment categories
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    # Analyze sentiment for each review
    for review in reviews:
        sentiment_result = analyze_sentiment(review)
        if 'error' in sentiment_result:
            continue  # Skip this review in case of error
        
        sentiment = classify_sentiment(sentiment_result['sentiment'])  # Classify the sentiment
        
        # Count sentiment classification
        if sentiment == 'positive':
            positive_count += 1
        elif sentiment == 'negative':
            negative_count += 1
        else:
            neutral_count += 1
    
    total_reviews = positive_count + negative_count + neutral_count
    if total_reviews == 0:
        return jsonify({"error": "No valid reviews processed."}), 400
    
    # Calculate sentiment scores as percentages
    positive_score = round(positive_count / total_reviews, 2)
    negative_score = round(negative_count / total_reviews, 2)
    neutral_score = round(neutral_count / total_reviews, 2)
    
    # Create the simplified summary JSON
    sentiment_summary = {
        "positive": positive_score,
        "negative": negative_score,
        "neutral": neutral_score
    }

    return jsonify(sentiment_summary), 200

# Error handler for invalid routes
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

# Error handler for server errors
@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Ensure the GROQ_API_KEY is set
    if not API_KEY:
        print("Error: GROQ_API_KEY environment variable not set.")
        exit(1)
    
    app.run(debug=True)

# Sentiment Analysis API with LLM Integration

## Overview

This project implements a Flask-based API that processes customer reviews from CSV or XLSX files and performs sentiment analysis using the Groq API. The API returns structured JSON responses with sentiment scores (positive, negative, neutral).

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Getting Started](#getting-started)
- [API Usage](#api-usage)
- [Error Handling](#error-handling)
- [Limitations and Improvements](#limitations-and-improvements)
- [License](#license)

## Features

- Upload customer reviews in CSV or XLSX format.
- Sentiment analysis using Groq API.
- Returns structured JSON responses with sentiment scores.

## Technologies

- **Flask**: Web framework for building the API.
- **Pandas**: For reading and processing CSV/XLSX files.
- **Requests**: For making API calls to the Groq API.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Install required packages:

```bash
pip install Flask pandas requests openpyxl
```

### Setting Up

1. Clone the repository:
   ```bash
   git clone 
   cd cert-project
   ```

2. Set up your Groq API key :
   
   GROQ_API_KEY='your_groq_api_key'
   

3. Run the Flask application:
   ```bash
   python app.py
   ```

4. The API will be accessible at `http://127.0.0.1:5000`.

## API Usage

### Uploading Reviews

- **Endpoint**: `/upload`
- **Method**: POST
- **Request**: Upload a CSV or XLSX file with a column named `Review`.

#### Sample Input (CSV/XLSX)

```plaintext
Review
"This product is great!"
"I'm unhappy with the service."
"The quality is average."
```

#### Sample Output

```json
{
  "positive": 0.33,
  "negative": 0.33,
  "neutral": 0.33
}
```

### Example Using Postman

1. Open Postman and select POST method.
2. Set the URL to `http://127.0.0.1:5000/upload`.
3. In the Body tab, select `form-data`, and upload your file under the key `file`.
4. Send the request to receive sentiment scores.

## Error Handling

The API includes basic error handling for common issues:

- Invalid file types (not CSV or XLSX).
- Missing 'Review' column in the uploaded file.
- API request errors (handled with retries for rate limits).

## Limitations and Improvements

- **Limitations**:
  - The accuracy of sentiment analysis can vary.
  - Rate limits of the Groq API may affect performance.

- **Potential Improvements**:
  - Implement caching for repeated reviews.
  - Enhance sentiment classification to detect more emotions.
  - Optimize performance for larger datasets.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```
# create a flask app
from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from uuid import uuid4
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
import pickle
import pandas as pd
import re
from email import message_from_string
from api.all_functions import (
    extract_headers, count_words, count_links_and_domains, has_html,
    count_attachments, count_suspicious_attachments, spam_score, count_suspicious_links,
    is_fake_domain, is_missing_to, count_recipients, count_subject_words,
    load_model
)


def transform_email(message_text):
    """Transforms an email message into a DataFrame of features"""

    features = [
    "num_words", "num_links", "num_attachments", "num_suspicious_attachments",
    "has_html", "spam_score", "num_suspicious_links", "is_fake_domain",
    "is_missing_to", "num_recipients", "num_subject_words"
]
    email_text = message_text[0].strip()
    headers = extract_headers(email_text)
    
    data = {
        "email_id": str(uuid4()),  # Generate a unique ID
        "from": headers["from"],
        "to": headers["to"],
        "subject": headers["subject"],
        "date": headers["date"],
        "body": headers["body"],
        "num_words": count_words(email_text),
        "num_links": count_links_and_domains(email_text),
        "num_attachments": count_attachments(email_text),
        "num_suspicious_attachments": count_suspicious_attachments(email_text),
        "has_html": has_html(email_text),
        "spam_score": spam_score(email_text),
        "num_suspicious_links": count_suspicious_links(email_text),
        "is_fake_domain": is_fake_domain(email_text),
        "is_missing_to": is_missing_to(email_text),
        "num_recipients": count_recipients(email_text),
        "num_subject_words": count_subject_words(email_text),
    }
    return pd.DataFrame([data])[features].astype(int)


# Define a pipeline to process emails
email_pipeline = Pipeline([
    ("transformer", FunctionTransformer(transform_email)),
    ("classifier", load_model("spam_classifier.pkl"))  # Load a pre-trained model
])

app = Flask(__name__)
CORS(app)




@app.route('/api/check-spam', methods=['POST'])
def check_spam():
    email = request.json['text']
    prediction = email_pipeline.predict([email])
    return jsonify({'is_spam': bool(prediction[0])})

if __name__ == '__main__':
    app.run(debug=True)

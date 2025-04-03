from all_functions import (
    extract_headers, count_words, count_links_and_domains, has_html,
    count_attachments, count_suspicious_attachments, spam_score, count_suspicious_links,
    is_fake_domain, is_missing_to, count_recipients, count_subject_words,
    load_model
)
from uuid import uuid4
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
import pandas as pd
import re
from email import message_from_string
from data_for_testing import fetch_and_format_emails



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
    ("classifier", load_model("re_complement_naive_bayes_model.pkl"))  # Load a pre-trained model
])

# function to test the model
def test_naive_bayes_model(email_text):
    """
    Function to test the logistic regression model
    """
    return email_pipeline.predict([email_text])[0]

# test the model
inbox = fetch_and_format_emails()
for email_text in inbox:
    headers = extract_headers(email_text)
    print(f"Testing email '{headers['subject']}': {test_naive_bayes_model(email_text)}")

spam = fetch_and_format_emails('SPAM')
for email_text in spam:
    headers = extract_headers(email_text)
    print(f"Testing email '{headers['subject']}': {test_naive_bayes_model(email_text)}")
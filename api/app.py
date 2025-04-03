# create a flask app
from flask import Flask, request, jsonify, render_template, redirect, session
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
    load_model, fetch_and_format_emails
)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


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


def evaluate_model_vs_gmail(paginate=False, page=1, per_page=20):
    inbox_emails, _ = fetch_and_format_emails(label='INBOX')
    spam_emails, _ = fetch_and_format_emails(label='SPAM')

    all_results = []
    y_true = []  # Gmail's label
    y_pred = []  # Model's prediction

    # From inbox (Gmail says NOT SPAM)
    for email_text in inbox_emails:
        headers = extract_headers(email_text)
        prediction = int(test_naive_bayes_model(email_text))

        all_results.append({
            "subject": headers.get("subject", "(No Subject)"),
            "from": headers.get("from", "(Unknown)"),
            "date": headers.get("date", "(Unknown Date)"),
            "gmail_label": "NOT_SPAM",
            "model_label": "SPAM" if prediction == 1 else "NOT_SPAM"
        })
        y_true.append("NOT_SPAM")
        y_pred.append("SPAM" if prediction == 1 else "NOT_SPAM")

    # From spam folder (Gmail says SPAM)
    for email_text in spam_emails:
        headers = extract_headers(email_text)
        prediction = int(test_naive_bayes_model(email_text))

        all_results.append({
            "subject": headers.get("subject", "(No Subject)"),
            "from": headers.get("from", "(Unknown)"),
            "date": headers.get("date", "(Unknown Date)"),
            "gmail_label": "SPAM",
            "model_label": "SPAM" if prediction == 1 else "NOT_SPAM"
        })
        y_true.append("SPAM")
        y_pred.append("SPAM" if prediction == 1 else "NOT_SPAM")

    # Compute metrics
    metrics = {
        "accuracy": round(accuracy_score(y_true, y_pred), 3),
        "precision": round(precision_score(y_true, y_pred, pos_label="SPAM"), 3),
        "recall": round(recall_score(y_true, y_pred, pos_label="SPAM"), 3),
        "f1": round(f1_score(y_true, y_pred, pos_label="SPAM"), 3)
    }

    # Pagination logic
    if paginate:
        start = (page - 1) * per_page
        end = start + per_page
        paginated_results = all_results[start:end]
        return paginated_results, metrics, len(all_results)
    
    return all_results, metrics, len(all_results)

# # test the model
# inbox = fetch_and_format_emails()
# for email_text in inbox:
#     headers = extract_headers(email_text)
#     print(f"Testing email '{headers['subject']}': {test_naive_bayes_model(email_text)}")

# spam = fetch_and_format_emails('SPAM')
# for email_text in spam:
#     headers = extract_headers(email_text)
#     print(f"Testing email '{headers['subject']}': {test_naive_bayes_model(email_text)}")

app = Flask(__name__)
CORS(app)
app.secret_key = 'some-secret-key'  # Required for using session



@app.route('/start-auth', methods=['POST'])
def start_auth():
    user_email = request.form['email'].strip().lower()
    session['user_email'] = user_email  # store for use in authenticate_gmail()
    return redirect('/inbox-folder')


@app.route('/')
def landing_page():
    return render_template("landing.html")

@app.route('/spam-folder', methods=['GET'])
def show_spam_folder():
    page_token = request.args.get('page_token')
    spam_emails, next_page_token = fetch_and_format_emails(label='SPAM', page_token=page_token)

    output = []
    for email_text in spam_emails:
        headers = extract_headers(email_text)
        subject = headers.get("subject", "No Subject")
        sender = headers.get("from", "Unknown Sender")
        date = headers.get("date", "Unknown Date")
        label = int(test_naive_bayes_model(email_text))

        output.append({
            "subject": subject,
            "from": sender,
            "date": date,
            "label": label
        })
        print(output)

    return render_template("spam_folder.html", emails=output, next_page_token=next_page_token)


@app.route('/inbox-folder', methods=['GET'])
def check_spam():
    page_token = request.args.get('page_token')  # From query string ?page_token=...
    inbox, next_page_token = fetch_and_format_emails(page_token=page_token)

    output = []
    for email_text in inbox:
        headers = extract_headers(email_text)
        subject = headers.get("subject", "No Subject")
        sender = headers.get("from", "Unknown Sender")
        date = headers.get("date", "Unknown Date")
        label = int(test_naive_bayes_model(email_text))

        output.append({
            "subject": subject,
            "from": sender,
            "date": date,
            "label": label
        })

    return render_template("inbox.html", emails=output, next_page_token=next_page_token)


@app.route('/model-vs-gmail')
def compare_model_vs_gmail():
    page = int(request.args.get('page', 1))
    filter_mismatches = request.args.get('filter') == 'mismatch'

    results, metrics, total = evaluate_model_vs_gmail(paginate=True, page=page)

    if filter_mismatches:
        results = [r for r in results if r['gmail_label'] != r['model_label']]

    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (page * 20) < total else None

    return render_template(
        "compare.html",
        results=results,
        metrics=metrics,
        page=page,
        prev_page=prev_page,
        next_page=next_page,
        filter_mismatches=filter_mismatches
    )


if __name__ == '__main__':
    app.run(debug=True)

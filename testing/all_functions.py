from email import message_from_string
import re
import pickle


def load_model(filename):
    with open(filename, 'rb') as file:
        model = pickle.load(file)
    print(f"Model loaded from {filename}")
    return model


def extract_headers(email_text):
    '''
    Extracts email headers from raw text

    Parameters:
        email_text (str): Raw email text

    Returns:
        dict: Extracted email headers
    '''
    msg = message_from_string(email_text)
    
    # Extracting headers
    email_data = {
        "from": msg["From"],
        "to": msg["To"],
        "subject": msg["Subject"],
        "date": msg["Date"],
        "body": None  # Default to None if body extraction fails
    }
    
    # Extract email body (handling different content types)
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Select only text/plain (ignore attachments)
            if content_type == "text/plain" and "attachment" not in content_disposition:
                charset = part.get_content_charset() or "utf-8"  # Default to utf-8 if None
                email_data["body"] = part.get_payload(decode=True).decode(charset, errors="ignore")
                break  # Stop at first valid body
    else:
        charset = msg.get_content_charset() or "utf-8"  # Default encoding
        email_data["body"] = msg.get_payload(decode=True).decode(charset, errors="ignore")
    
    return email_data

def count_words(text):
    '''Counts the number of words in a text'''
    words = re.findall(r"\b\w+\b", text)  # Extracts words correctly
    return len(words)

def count_links_and_domains(text):
    """Counts both full URLs and plain domain mentions."""
    url_pattern = r"https?://[^\s<>\"']+"  # Full URLs
    domain_pattern = r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}\b"  # Plain domains

    urls = re.findall(url_pattern, text)
    domains = re.findall(domain_pattern, text)

    return len(set(urls + domains))  # Using `set()` to remove duplicates

def has_html(email_text):
    """Check if an email contains an HTML part."""
    msg = message_from_string(email_text)
    return any(part.get_content_type() == "text/html" for part in msg.walk())

def count_attachments(email_text):
    """Count the number of attachments in an email."""
    msg = message_from_string(email_text)
    return sum(1 for part in msg.walk() if part.get_filename())  # Count parts that have a filename

def spam_score(text):
    """Calculate the spam score based on predefined spam words."""
    SPAM_WORDS = [
        "free", "win", "winner", "winnings", "money", "cash", "earn", "easy money",
        "make money", "fast cash", "quick cash", "extra cash", "double your income",
        "get rich", "financial freedom", "increase sales", "investment", 
        "passive income", "work from home", "no experience needed", "limited time",
        "instant cash", "credit", "debt relief", "bank transfer", "wire transfer", 
        "fast loan", "no credit check", "lowest rate", "instant approval",
        "offer", "discount", "prize", "reward", "bonus", "gift", "apply now",
        "special deal", "hot deal", "lowest price", "save big", "best deal", 
        "bargain", "buy now", "order now", "cheap", "affordable", "best price", 
        "exclusive", "promo", "promotion", "limited offer", "free trial", 
        "new customer", "subscription", "membership", "act fast", "expires soon",
        "urgent", "hurry", "act now", "last chance", "final notice", "important", 
        "as soon as possible", "time-sensitive", "one-time", "today only", 
        "do it now", "limited stock", "this won’t last", "once in a lifetime",
        "click", "click here", "click below", "open now", "access now",
        "view online", "sign up", "register now", "confirm your details",
        "log in", "update your account", "verify your identity", 
        "secure your account", "your account is at risk", "security alert", 
        "reset password", "your payment failed", "billing issue", "invoice attached",
        "guarantee", "risk-free", "no risk", "100% free", "money-back", 
        "satisfaction guaranteed", "no obligation", "hidden charges", 
        "secret formula", "miracle", "exclusive deal", "instant cure", 
        "congratulations", "you have been selected", "you are a winner",
        "unsubscribe", "remove me", "opt-out", "this is not spam",
        "why are you receiving this", "you received this email because",
        "not interested?", "spam-free guarantee", "no more emails",
        "bitcoin", "crypto", "blockchain", "ethereum", "trading", "forex", 
        "broker", "binary options", "wallet", "crypto exchange", "payout", 
        "account verification", "account update", "account locked", "secure login",
        "miracle cure", "cure", "no prescription", "pharmacy", "drugs", 
        "weight loss", "diet pill", "anti-aging", "instant results", "clinically proven",
        "lottery", "jackpot", "lucky draw", "winning ticket", "unclaimed prize", 
        "claim your reward", "sweepstakes", "mega millions", "powerball", 
        "your lucky number", "your check is waiting",
        "earn at home", "home-based business", "be your own boss", "online income",
        "startup funding", "government grant", "high-paying job", "no skills required",
        "mortgage rates", "real estate", "home loan", "house for sale", 
        "foreclosure", "cheap property", "investment property", "flipping houses",
        "identity verification", "social security number", "ssn", "bank account", 
        "routing number", "password reset", "security question", "personal details",
        "your computer is infected", "tech support", "fix your pc", "remote access",
        "download now", "install this update", "your system is at risk", 
        "trojan detected", "virus warning", "malware detected", "spyware removal",
        "help us", "donate now", "urgent donation needed", "support our cause", 
        "charity request", "nonprofit", "disaster relief", "emergency appeal",
        "as seen on tv", "elon musk recommends", "warren buffet’s secret", 
        "celebrity approved", "doctor recommended", "scientifically proven"
    ]

    text_lower = text.lower()
    return sum(len(re.findall(rf"\b{word}\b", text_lower)) for word in SPAM_WORDS)

def count_suspicious_attachments(email_text):
    """Count the number of suspicious attachments in an email."""
    msg = message_from_string(email_text)
    dangerous_exts = {".exe", ".zip", ".rar", ".scr", ".iso", ".js", ".bat"}
    
    return sum(
        1 for part in msg.walk()
        if part.get_filename() and any(part.get_filename().lower().endswith(ext) for ext in dangerous_exts)
    )

def is_fake_domain(email_text):
    """Check if the email sender's domain is suspicious."""
    msg = message_from_string(email_text)
    email_from = msg["From"]
    
    fake_keywords = ["free", "money", "offer", "lottery", "deal", "promo", "cheap"]
    
    if email_from:
        match = re.search(r'@([\w.-]+)', email_from)
        if match:
            domain = match.group(1).lower()
            return any(keyword in domain for keyword in fake_keywords)
    
    return False

def count_suspicious_links(text):
    """Count the number of suspicious links in an email."""
    suspicious_domains = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly"}
    
    links = re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", text)
    
    return sum(1 for link in links if any(domain in link for domain in suspicious_domains))

def is_missing_to(email_text):
    """Check if the email is missing the 'To' field."""
    msg = message_from_string(email_text)
    return 1 if not msg["To"] else 0

def count_recipients(email_text):
    """Count the number of recipients in the email."""
    msg = message_from_string(email_text)
    return len(msg["To"].split(",")) if msg["To"] else 0

def count_subject_words(email_text):
    """Count the number of words in the email subject."""
    msg = message_from_string(email_text)
    return len(msg["Subject"].split()) if msg["Subject"] else 0

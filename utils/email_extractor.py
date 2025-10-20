import re




def extract_emails(text):
    """
    Extracts all valid email addresses from a given string of plain text or HTML,
    including those found in mailto links, while filtering out common invalid
    or unwanted addresses.

    Args:
        text (str): The input string from which to extract emails.

    Returns:
        list: A sorted list of unique, valid email addresses found in the text.
    """
    if not text:
        return []

    # Regex patterns for standard emails and those within mailto links.
    email_patterns = [
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        r"mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    ]

    all_emails = set()
    for pattern in email_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Handle the group from the 'mailto:' regex
            if isinstance(match, tuple):
                match = match[0]
            all_emails.add(match.strip())

    # --- Filtering Logic ---

    valid_emails = []
    # Extensions to exclude
    invalid_exts = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf", ".exe", ".zip", ".heic"}
    # Common "bad" words to exclude from emails
    bad_words = {
        'noreply', 'no-reply', 'donotreply', 'do-not-reply', 'mailer-daemon',
        'postmaster', 'abuse', 'unsubscribe', 'bounce', 'test123', 'example',
        'sample', 'demo123', 'nobody', 'null', 'void', 'user-name', 'your', 'user'
    }

    for email in all_emails:
        # Skip if the email ends with a file extension
        if any(email.endswith(ext) for ext in invalid_exts):
            continue

        # Skip if the email contains a long string of numbers (e.g., placeholder emails)
        if re.search(r"\d{8,}", email):
            continue
        # Skip if it contains URL-like characters
        if "://" in email or ".com/" in email:
            continue
        if re.search(r"^\d{3}-\d{3}-\d{4}", email):
            email = re.sub(r"^\d{3}-\d{3}-\d{4}", "", email)

        # Skip if it contains a common bad word
        if any(bad in email for bad in bad_words):
            continue
        # remove the irregular trailing sequences at the end of emails
        if '?' in email:
           email = email.split('?')[0]

        # Final check to ensure it has an @ and a . in the domain part
        if "@" in email and "." in email.split("@")[-1]:
            valid_emails.append(email)


    return sorted(valid_emails)

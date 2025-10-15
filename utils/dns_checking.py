from enum import unique
import re
import smtplib
import dns.resolver



def validate_email(email):
    # Basic regex check
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(regex, email):
        return False, "Invalid email format"
    # Split email
    domain = email.split('@')[1]
    try:
        # Get MX record for domain
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
    except Exception as e:
        return False, f"DNS lookup failed: {e}"
    # Connect to SMTP server
    try:
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        # server.helo("example.com")  # pretend to be a legit domain
        # server.mail("test@example.com")  # fake sender
        server.helo("shayan-tester.com")  # Pretend to be a legit domain to avoid early rejection
        server.mail("shayan@mail-tester.com")
        code, message = server.rcpt(email)  # test recipient
        server.quit()
        if code == 250:
            return True, "Valid email"
        else:
            return False, f"Invalid email, server response: {message}"
    except Exception as e:
        return False, f"SMTP connection failed: {e}"
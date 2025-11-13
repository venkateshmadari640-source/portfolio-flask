import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "venkatesh_flask_secret_99")

# ----------------------
# Configuration
# ----------------------
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "venkateshmadari640@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/works")
def works():
    return render_template("works.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


# ----------------------
# Contact form handler
# ----------------------
@app.route("/submit_form", methods=["POST"])
def submit_form():
    print("✔ FORM RECEIVED")   # DEBUG

    user_email = request.form.get("email", "").strip()
    subject = request.form.get("subject", "").strip() or "Contact form submission"
    message = request.form.get("message", "").strip()

    if not user_email or not message:
        flash("Please provide at least your email and a message.", "danger")
        return redirect(url_for("contact"))

    # Save message to file
    try:
        with open("messages.txt", "a", encoding="utf-8") as f:
            f.write(f"\n---\nFrom: {user_email}\nSubject: {subject}\nMessage:\n{message}\n")
    except Exception as e:
        print("❌ ERROR writing file:", e)

    # Prepare HTML content
    owner_html = render_template("email_to_you.html",
                                 user_email=user_email,
                                 subject=subject,
                                 message=message)

    auto_reply_html = render_template("auto_reply.html",
                                      user_email=user_email,
                                      subject=subject,
                                      message=message)

    # Check App Password
    if not GMAIL_APP_PASSWORD:
        print("❌ ERROR: GMAIL_APP_PASSWORD is NOT SET in your system!")
        flash("Email sending failed. App Password not found.", "danger")
        return redirect(url_for("thankyou"))

    print("✔ Attempting to send email...")  # DEBUG

    try:
        # Send email to you
        send_email(
            smtp_user=SENDER_EMAIL,
            smtp_pass=GMAIL_APP_PASSWORD,
            sender=SENDER_EMAIL,
            recipient=SENDER_EMAIL,
            subject=f"[Portfolio Contact] {subject}",
            html_body=owner_html,
            plain_body=f"From: {user_email}\nSubject: {subject}\n\n{message}"
        )

        # Auto-reply to user
        send_email(
            smtp_user=SENDER_EMAIL,
            smtp_pass=GMAIL_APP_PASSWORD,
            sender=SENDER_EMAIL,
            recipient=user_email,
            subject="Thanks for contacting me — I received your message",
            html_body=auto_reply_html,
            plain_body=f"Hi,\n\nThanks for contacting me. I received your message:\n\n{message}\n\nI'll get back to you soon."
        )

        print("✔ EMAILS SENT SUCCESSFULLY")  # DEBUG
        flash("Message sent successfully — thank you!", "success")

    except Exception as e:
        print("❌ EMAIL ERROR:", e)   # DEBUG
        flash("Message saved but sending email failed.", "danger")

    return redirect(url_for("thankyou"))


# ----------------------
# Email helper
# ----------------------
def send_email(smtp_user, smtp_pass, sender, recipient, subject, html_body, plain_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(sender, recipient, msg.as_string())


if __name__ == "__main__":
    print("✔ SERVER STARTED — Waiting for form submission...")
    app.run(debug=True)

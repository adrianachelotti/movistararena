from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import smtplib
import time

app = Flask(__name__)

MOVISTAR_ARENA_URL = "https://www.movistararena.com.ar/"
KNOWN_SHOWS = set()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

def get_shows():
    response = requests.get(MOVISTAR_ARENA_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    shows = set()
    for event in soup.find_all("div", class_="event-title"):
        shows.add(event.text.strip())
    return shows


def send_email(new_shows):
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        message = f"Subject: Nuevo Show en Movistar Arena!\n\nSe han agregado los siguientes shows:\n\n" + "\n".join(new_shows)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message)


def check_for_new_shows():
    global KNOWN_SHOWS
    current_shows = get_shows()
    new_shows = current_shows - KNOWN_SHOWS
    if new_shows:
        send_email(new_shows)
    KNOWN_SHOWS = current_shows


@app.route("/check", methods=["GET"])
def check():
    check_for_new_shows()
    return jsonify({"message": "Revisión completada"}), 200


if __name__ == "__main__":
    KNOWN_SHOWS = get_shows()
    app.run(debug=True)

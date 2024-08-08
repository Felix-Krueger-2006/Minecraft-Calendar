from flask import Flask, render_template, request, session, redirect, make_response
import requests
from flask_mail import Mail, Message
import json
import random
import string

app = Flask(__name__)
app.config['static'] = 'static'
app.config['MAIL_SERVER']='live.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'api'
app.config['MAIL_PASSWORD'] = '2f8cc39aa15bf6c8ae72877683ecdb9a'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)
app.secret_key = 'mc-calendar'

verifyed = {}
calendar = []
users = []
streamer = []

with open('./data/verifyed_mail.json', 'r') as file:
    verifyed = json.load(file)

with open('./data/calendar.json', 'r') as file:
    calendar = json.load(file)

with open('./data/user.json', 'r') as file:
    users = json.load(file)

with open('./data/streamer.json', 'r') as file:
    streamer = json.load(file)

def wichCount():
    for data in calendar:
        if not data["open"]:
            return data["counter"] - 1
    return "error"

def checkAdress(addr):
    if users != []:
        for user in users:
            if user[1] == addr:
                return True
    return False

def verifyEmail(mail):
    if verifyed["verified"] != []:
        for user in verifyed["verified"]:
            if user[0] == mail:
                return True
    
    if verifyed["must-verify"] != []:
        for user in verifyed["must-verify"]:
            if user[1] == mail:
                return True
        
    return False

@app.route("/session")
def sessiond():
    session.clear()
    return redirect("/")

@app.route("/", methods=["GET"])
def home():
    api_url = 'https://api.betterplace.org/de/api_v4/fundraising_events/45538.json'

    with open('./data/streamer.json', 'r') as file:
        streamer = json.load(file)

    try:
        response = requests.get(api_url)

        if response.status_code == 200:
            charity = response.json()
        else:
            print(f"Fehler beim Abrufen der Daten. Statuscode: {response.status_code}")

    except Exception as e:
        print(f"Fehler beim Abrufen der Daten: {str(e)}")
        charity = []

    charity = float(charity["donated_amount_in_cents"]) / 100
    charity = "{:.2f}".format(charity)
    print(charity)

    return render_template("index.html", donations=charity, streamer=streamer)

@app.route("/verify", methods=["POST", "GET"])
def verify():
    code = request.args.get("code")

    for user in verifyed["must-verify"]:
        if user[0] == code:
            idk = [user[1]]
            verifyed["verified"].append(idk)
            verifyed["must-verify"].remove(user)

            Email = [user[1], request.remote_addr]
            users.append(Email)

            session["day"] = wichCount()

            with open('./data/user.json', 'w') as file:
                json.dump(users, file)

            with open('./data/verifyed_mail.json', 'w') as file:
                json.dump(verifyed, file)

    return redirect("/calendar")

@app.route("/calendar", methods=["POST", "GET"])
def calendar_f():
    
    with open('./data/calendar.json', 'r') as file:
        calendar = json.load(file)

    with open('./data/verifyed_mail.json', 'r') as file:
        verifyed = json.load(file)

    with open('./data/user.json', 'r') as file:
        users = json.load(file)

    error = ""
    if request.method == "POST":
        Email = request.form["e-mail"]

        for user in users:
            if user[0] == Email:
                error = "Du bist bereits angemeldet."
                break

        for user in verifyed["must-verify"]:
            if verifyed["must-verify"] != []:
                if user[1] == Email:
                    error = "Bitte bestätige deine E-Mail Adresse."
                    break
        
        if not checkAdress(request.remote_addr) and not verifyEmail(Email):
            if session.get('day', -1) != wichCount() and not verifyEmail(Email):
                code = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(20))

                user = [code, Email]
                verifyed["must-verify"].append(user)

                with open('./data/verifyed_mail.json', 'w') as file:
                    json.dump(verifyed, file)
                
                html_body = f"""
                Du hast dich für unser Gewinnspiel angemeldet, bitte verifiziere deine E-Mail: <a href="https://mc-calendar.de/verify?code={code}">Verifizieren</a>
                <style>
                a {{
                    border: 2px solid black;
                    padding: 2px 5px;
                    color: blue;
                    text-decoration: none;
                    border-radius: 20px;
                    background: #00000055;
                }}
                </style>"""

                message = Message(
                    subject="Bitte Verifiziere deine E-Mail Adresse!",
                    recipients=[Email],
                    sender="verify@mc-calendar.de",
                    html=html_body
                )

                mail.send(message)

                session["day"] = wichCount()

                error = "Bitte schau in deine E-Mails."

        for user in verifyed["verified"]:
            if user[0] == Email:
                found = False
                for user2 in users:
                    if user2[0] == Email:
                        found = True
                if not found and not checkAdress(request.remote_addr):
                    if session.get('day', -1) != wichCount():
                        E_mail = [Email, request.remote_addr]
                        users.append(E_mail)

                        session["day"] = wichCount()

                        with open('./data/user.json', 'w') as file:
                            json.dump(users, file)

                        error = "Du hast dich erfolgreich angemeldet."

        if error == "":
            error = "Du hast dich bereits angemeldet! Error"

    cookie = request.cookies.get('again') if request.cookies.get('again') else 0

    if cookie == "NoneType":
        cookie = 0

    day = 0
    formular = True
    for data in calendar:
        if data["open"]:
            day = data["counter"]
            if data["form"]:
                formular = True
            else:
                formular = False

    response = make_response(render_template("calendar.html", list=calendar,day=day, again=int(cookie), form=formular, errorText=error))

    return response

if __name__ == '__main__':
    app.run(port="5001", debug=True)

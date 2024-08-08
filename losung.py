import json
import random
import os
import mailtrap as mt
import string

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file)

def send_winner_email(user, prize):
    save_code = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(20))

    # HTML-Code für die E-Mail mit eingebettetem Bild
    html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
            <div class="container">
                <h1>Herzlichen Glückwunsch</h1>
                <p>Du hast beim Gewinnspiel gewonnen und erhältst {prize["name"]}.</p>
                <p>Bitte wende dich an TVInvincible oder den Support, dies kannst du entweder über Discord oder per E-Mail. Gefordert werden dann Adresse, Name etc., die für den Versand benötigt werden.</p>
                <p>E-Mail: tvinvincible52@gmail.com</p>
                <p>Discord: https://discord.gg/CknMqQfVDU</p>
                <img src="{prize["image"]}" alt="Gewinnbild">
                <br>
                <p>Dein Bestätigungscode: {save_code}</p>
            </div>
            <style>
                .container {{
                    background: red;
                    height: 100vh;
                    width: 100%;
                }}
                h1 {{
                    color: black;
                    text-align: center;
                    font-size: 30px;
                    margin-bottom: 30px;
                    margin-left: 30px;
                }}
                p {{
                    color: black;
                    right: 50%;
                    transform: translate(0, -50%)
                    font-size: 25px;
                }}
                img {{
                    position: absolute;
                    bottom: 80%;
                    left: 50%;
                    transform: translate(-80%, -50%);
                    height: 40%;
                }}
            </style>
        </body>
        </html>
    """

    # E-Mail-Objekt erstellen
    mail = mt.Mail(
        sender=mt.Address(email="giveaway@mc-calendar.de", name="Verlosung"),
        to=[mt.Address(email=user[0])],
        subject="Du hast Gewonnen!",
        text="Plain text content",
        html=html_content,
    )

    # E-Mail senden
    client = mt.MailtrapClient(token="2f8cc39aa15bf6c8ae72877683ecdb9a")
    client.send(mail)

    print("Mail Sent")

    html_content = f'''Der Bestätigungscode: {save_code} für {user[0]}'''

    # E-Mail-Objekt erstellen
    mail_save = mt.Mail(
        sender=mt.Address(email="giveaway@mc-calendar.de", name="Verlosung"),
        to=[mt.Address(email="tvinvincible52@gmail.com")],
        subject="Der Bestätigungscode",
        text="Plain text content",
        html=html_content,
    )

    # E-Mail senden
    client = mt.MailtrapClient(token="2f8cc39aa15bf6c8ae72877683ecdb9a")
    client.send(mail_save)

def select_winner(users, prizes):
    length = len(users) - 1
    random_winner = random.randint(0, length)

    prize = prizes[0]
    prizes.pop(0)

    # Gewinner-E-Mail senden
    send_winner_email(users[random_winner], prize)

    # Gewinner zu Liste hinzufügen und aus Benutzerliste entfernen
    winners.append(users[random_winner])
    users.pop(random_winner)

# Laden der Daten
users = load_json(os.path.join('data', 'user.json'))
winners = load_json(os.path.join('data', 'winner.json'))
calendar = load_json(os.path.join('data', 'calendar.json'))
prizes = load_json(os.path.join('data', 'gewinne.json'))

# Gewinner auswählen
for data in calendar:
    if data["open"] and data["counter"] in [5, 10, 12, 15, 20] and not data["save"]:
        select_winner(users, prizes)
        if data["counter"] in [10]:
            select_winner(users, prizes)
        data["save"] = True
    if not data["open"] and data["counter"] <= 24:
        data["open"] = True
        break
    elif data["open"] and data["counter"] == 24:
        for a in range(1, 8):
            select_winner(users, prizes)
        break    

users = []

# Speichern der aktualisierten Daten
save_json(users, os.path.join('data', 'user.json'))
save_json(winners, os.path.join('data', 'winner.json'))
save_json(calendar, os.path.join('data', 'calendar.json'))
save_json(prizes, os.path.join('data', 'gewinne.json'))

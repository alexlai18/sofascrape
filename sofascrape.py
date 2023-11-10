from bs4 import BeautifulSoup
import requests
import datetime
from pytz import timezone
import os
import smtplib
import ssl
from email.message import EmailMessage
# If deployed will set this as environment variable
from password import password, email, api_url, headers

def create_email(email, email_string):
    # Sending an email
    # Template from https://codepen.io/rKalways/pen/VwwQKpV
    with open('email_template.txt', 'r') as file:
        TEXT = file.read().replace('\n', '')

    TEXT = TEXT.replace("TENTATIVE MESSAGE", email_string)

    email_sender = 'laiierbettingscan@gmail.com'

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email
    em['Subject'] = "Today's Table Tennis Matches"
    em.set_content(TEXT)

    # Make the message multipart
    em.add_alternative(TEXT, subtype='html')

    # Add SSL (layer of security)
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, password)
        smtp.sendmail(email_sender, email, em.as_string())

# Getting all possible responses from sofascore (usually only goes until 5)
responses = []
for i in range(20):
    # Headers is just your headers from www.whatismybrowser.com
    responses.append(requests.get(f'{api_url}/{i}', headers=headers))
names = []


for response in responses:
    # Convert matches into json form
    matches = response.json()
    if (matches.get('error')):
        break

    # Extract names from matches and convert UNIX timestamp to localtime
    for match in matches['events']:
        local_datetime = datetime.datetime.fromtimestamp(match['startTimestamp'])
        local_time_str = datetime.datetime.strftime(local_datetime, "%a, %d %b %Y %H:%M:%S")
        names.append({local_time_str: (match['homeTeam']['slug'], match['awayTeam']['slug'])})

# Checks if certain matchups have anyone inbetween, or if they are back-to-back opponents for each other
res = []
for i in range(len(names) - 1):
    match1 = list(names[i].items())[0]
    timestamp1, players1 = match1

    for j in range(i + 1, len(names)):
        match2 = list(names[j].items())[0]
        timestamp2, players2 = match2

        # Check if there are common players in both matches
        common_players = set(players1).intersection(players2)

        if len(common_players) == 1:
            break
        elif len(common_players) == 2:
            res.append(((timestamp1, players1), (timestamp2, players2)))
            break

# Configuring email string
email_string = ''
for fin in res:
    email_string += f'First game at: {fin[0][0]} between {fin[0][1][0]} and {fin[0][1][1]}'
    email_string += '<br />'
    email_string += f'Second game is at {fin[1][0]}'
    email_string += '<br />'
    email_string += '<br />'
if email_string == '':
    email_string = 'Unfortunately, there are no consecutive games for this tournament'
create_email(email, email_string)
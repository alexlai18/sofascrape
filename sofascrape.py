from bs4 import BeautifulSoup
import requests
import datetime
from pytz import timezone
import os
import smtplib
import ssl
from email.message import EmailMessage
# If deployed will set this as environment variable

api_list = ["https://www.sofascore.com/api/v1/unique-tournament/19041/events/next", "https://www.sofascore.com/api/v1/unique-tournament/15005/events/next"]
def get_info(api_url):
    # Getting all possible responses from sofascore (usually only goes until 5)
    responses = []
    for i in range(20):
        reqRes = requests.get(f'{api_url}/{i}').json()
        if reqRes.get('error'):
            break
        # Headers is just your headers from www.whatismybrowser.com
        responses.append(reqRes)
        if reqRes['hasNextPage'] == False:
            break
    names = []


    for response in responses:
        # Convert matches into json form
        if (response.get('error')):
            break

        # Extract names from matches and convert UNIX timestamp to localtime
        for match in response['events']:
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

    print(res)
# Main function to run script
for i in range(len(api_list)):
    get_info(api_list[i])
from flask import Blueprint, jsonify, request, render_template
from project.api.containers import get_container
import requests
from datetime import datetime, timedelta

divisions_blueprint = Blueprint('divisions', __name__, template_folder='./templates')


@divisions_blueprint.route('/ping', methods=['GET'])
def pint_pong():
    return render_template("pong.html")

@divisions_blueprint.route('/divisions', methods=['GET'])
def division_overview():
    x = requests.get(f'{get_container("matches")}/divisions')
    return render_template("divisions.html", divisions=x.json()["data"])

@divisions_blueprint.route('/divisions/<division_id>', methods=['GET'])
def specific_division(division_id):
    x = requests.get(f'{get_container("matches")}/divisions/{division_id}')
    team = request.args.get("team")
    if team:
        fixtures = requests.get(f'{get_container("matches")}/divisions/{division_id}/fixtures/{team}').json()
    else:
        fixtures = requests.get(f'{get_container("matches")}/divisions/{division_id}/fixtures').json()
    stats = requests.get(f'{get_container("matches")}/divisions/{division_id}/stats').json()["data"]
    league_table = requests.get(f'{get_container("matches")}/divisions/{division_id}/league_table').json()["data"]
    # return jsonify(x.json(), 200)
    return render_template("division.html", division=x.json()["data"]["name"], fixtures=fixtures["data"], stats=stats, league=league_table)

def get_weather(city, date):
    # Credits groot deel van deze code: Grepper
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    CITY = "Hyderabad"
    from project.api.api_key import API_KEY
    # upadting the URL
    URL = f'{BASE_URL}q={CITY},BE&appid={API_KEY}&day={date.day}&month={date.month}&year={date.year}'
    response = requests.get(URL)
    if response.status_code == 200:
        # getting data in the json format
        data = response.json()
        main = data['main']
        temperature = main['temp']
        humidity = main['humidity']
        report = data['weather']
        return {"temp": temperature, "hum": humidity, "report": report[0]['description']}
    else:
        # showing the error message
        # print("Error in the HTTP request")
        return {"temp": None, "hum": None, "report": None}

@divisions_blueprint.route('/matches/<fixture_number>', methods=['GET'])
def fixture_detail(fixture_number):
    x = requests.get(f'{get_container("matches")}/matches/{fixture_number}').json()["data"]
    home = x["home"]
    away = x["away"]
    date = x["date"]
    time = x["time"]
    referee = x["referee"]

    stats = None
    weather = None
    results_1 = None
    results_2 = None
    match_date = datetime.strptime(date, "%Y-%m-%d")
    if match_date >= date.now().date():
        stats = requests.get(f'/matches/stats/{home}/vs/{away}').json()["data"]

        results_1 = ""
        for match in stats["team1"]["last"]:
            if match["home"] == home:
                if match["score_home"] > match["score_away"]:
                    results_1 += "W"
                elif match["score_home"] == match["score_away"]:
                    results_1 += "T"
                elif match["score_home"] < match["score_away"]:
                    results_1 += "L"
            elif match["away"] == home:
                if match["score_home"] > match["score_away"]:
                    results_1 += "L"
                elif match["score_home"] == match["score_away"]:
                    results_1 += "T"
                elif match["score_home"] < match["score_away"]:
                    results_1 += "W"

        results_2 = ""
        for match in stats["team2"]["last"]:
            if match["home"] == away:
                if match["score_home"] > match["score_away"]:
                    results_2 += "W"
                elif match["score_home"] == match["score_away"]:
                    results_2 += "T"
                elif match["score_home"] < match["score_away"]:
                    results_2 += "L"
            elif match["away"] == away:
                if match["score_home"] > match["score_away"]:
                    results_2 += "L"
                elif match["score_home"] == match["score_away"]:
                    results_2 += "T"
                elif match["score_home"] < match["score_away"]:
                    results_2 += "W"


        if match_date < datetime.now().date() + timedelta(days=7):
            # find the city
            stamnr = requests.get(f'{get_container("clubs")}/teams/{home}').json()["data"]["club_id"]
            city = requests.get(f'{get_container("clubs")}/clubs/{stamnr}').json()["data"]["city"]
            weather = get_weather(city, match_date)

    return render_template("match.html", home=home, away=away, date=date, time=time, referee=referee, stats=stats, results_1=results_1, results_2=results_2, weather=weather)
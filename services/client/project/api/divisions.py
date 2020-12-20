from flask import Blueprint, jsonify, request, render_template, flash, make_response, redirect
from project.api.containers import get_container
import requests
from datetime import datetime, timedelta,date

from geopy import Nominatim, Location
# from geopy import distance as dist
from geopy.exc import GeocoderTimedOut

divisions_blueprint = Blueprint('divisions', __name__, template_folder='./templates')


@divisions_blueprint.route('//ping', methods=['GET'])
def pint_pong():
    return render_template("pong.html")

@divisions_blueprint.route('//', methods=['GET'])
def home():
    return redirect('/web/divisions')

@divisions_blueprint.route('//divisions', methods=['GET'])
def division_overview():
    x = requests.get(f'{get_container("matches")}/divisions')
    return render_template("divisions.html", divisions=x.json()["data"])

@divisions_blueprint.route('//login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        x = requests.post(f'{get_container("users")}/users/authenticate', data=request.form)
        if x.status_code == 200:
            user = x.json()['data']
            redirect_url = "/web/team_admin" if user["type"] == "user" else "/web/admin/divisions"
            resp = make_response(redirect(redirect_url))
            resp.set_cookie('team', str(user["team_id"]))
            resp.set_cookie('user_type', str(user["type"]))
            flash("Login succesful")
            return resp
        else:
            flash("Invalid credentials")
    return render_template("login.html")

@divisions_blueprint.route('//logout', methods=['GET', 'POST'])
def logout():
    resp = make_response(redirect('/web/divisions'))
    resp.set_cookie("team", '', expires=0)
    resp.set_cookie("user_type", '', expires=0)
    return resp

@divisions_blueprint.route('//team_admin', methods=['GET', 'POST'])
def team_admin():
    if request.cookies.get("user_type") not in ["user", "admin", "superadmin"]:
        return render_template("no_permission.html")
    team = request.cookies.get("team")
    if request.method == 'POST':
        # TODO update club info
        x = requests.put(f'{get_container("matches")}/matches/{request.form.get("id")}', data={"goals_home": request.form.get("goals_home"), "goals_away": request.form.get("goals_away")})
        if x.status_code == 200:
            flash("Score updated succesfuly")
        else:
            flash(f"Something went wrong ({x.status_code})")
    if team:
        x = requests.get(f'{get_container("matches")}/matches/home/{team}')
        club = requests.get(f'{get_container("clubs")}/teams/{team}').json()["data"]["club_id"]
        club_info = requests.get(f'{get_container("clubs")}/clubs/{club}').json()["data"]
        # return jsonify(x.status_code)
        x = x.json()["data"]
        return render_template("team_admin.html", matches=x, obj=club_info)
    else:
        return render_template("no_permission.html")

@divisions_blueprint.route('//teams', methods=['GET'])
def teams_overview():
    x = requests.get(f'{get_container("clubs")}/teams')
    return render_template("teams.html", divisions=x.json()["data"])

@divisions_blueprint.route('//teams/<team_id>', methods=['GET'])
def specific_team(team_id):
    x = requests.get(f'{get_container("clubs")}/teams/{team_id}').json()["data"]
    matches = requests.get(f'{get_container("matches")}/recent/{team_id}').json()["data"]
    return render_template("team.html", team=x, matches=matches)

@divisions_blueprint.route('//divisions/<division_id>', methods=['GET'])
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

def get_weather(address, city, date):
    geolocator = Nominatim(user_agent="[PlaceHolder]", scheme='http')
    try:
        location = geolocator.geocode(f"{address}, {city}, Belgium")
    except GeocoderTimedOut:
        flash("The geolocator is timing out! please try again for weather")
        return {"temp": None, "hum": None, "report": None}


    # Credits groot deel van deze code: Grepper
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    CITY = "Hyderabad"
    from project.api.api_key import API_KEY
    # upadting the URL
    URL = f'{BASE_URL}lat={location.latitude}&lon={location.longitude}&appid={API_KEY}&day={date.day}&month={date.month}&year={date.year}' # q={CITY},BE
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

@divisions_blueprint.route('//matches/<fixture_number>', methods=['GET'])
def fixture_detail(fixture_number):
    x = requests.get(f'{get_container("matches")}/matches/{fixture_number}').json()["data"]
    home = x["home"]
    away = x["away"]
    date_ = x["date"]
    time = x["time"]
    referee = x["referee_id"]

    stats = None
    weather = None
    results_1 = None
    results_2 = None
    match_date = datetime.strptime(date_, "%Y-%m-%d")
    if match_date.date() >= datetime.now().date():
        stats = requests.get(f'{get_container("matches")}/matches/stats/{home}/vs/{away}').json()["data"]

        results_1 = ""
        for match in stats["team1"]["last"]:
            if match["goals_home"] is None or match["goals_away"] is None:
                results_1 += "?"
                continue
            if match["home"] == home:
                if match["goals_home"] > match["goals_away"]:
                    results_1 += "W"
                elif match["goals_home"] == match["goals_away"]:
                    results_1 += "T"
                elif match["goals_home"] < match["goals_away"]:
                    results_1 += "L"
            elif match["away"] == home:
                if match["goals_home"] > match["goals_away"]:
                    results_1 += "L"
                elif match["goals_home"] == match["goals_away"]:
                    results_1 += "T"
                elif match["goals_home"] < match["goals_away"]:
                    results_1 += "W"

        results_2 = ""
        for match in stats["team2"]["last"]:
            if match["goals_home"] is None or match["goals_away"] is None:
                results_2 += "?"
                continue
            if match["home"] == away:
                if match["goals_home"] > match["goals_away"]:
                    results_2 += "W"
                elif match["goals_home"] == match["goals_away"]:
                    results_2 += "T"
                elif match["goals_home"] < match["goals_away"]:
                    results_2 += "L"
            elif match["away"] == away:
                if match["goals_home"] > match["goals_away"]:
                    results_2 += "L"
                elif match["goals_home"] == match["goals_away"]:
                    results_2 += "T"
                elif match["goals_home"] < match["goals_away"]:
                    results_2 += "W"


        if match_date.date() < datetime.now().date() + timedelta(days=7):
            # find the city
            stamnr = requests.get(f'{get_container("clubs")}/teams/{home}').json()["data"]["club_id"]
            club = requests.get(f'{get_container("clubs")}/clubs/{stamnr}').json()["data"]
            address = club["address"]
            city = club["city"]
            weather = get_weather(address, city, match_date)

    return render_template("match.html", home=home, away=away, date=date_, time=time, referee=referee, stats=stats, results_1=results_1, results_2=results_2, weather=weather)

@divisions_blueprint.route('//admin/matches', methods=['GET', 'POST'])
def admin_matches():
    if request.cookies.get("user_type") not in ["admin", "superadmin"]:
        return render_template("no_permission.html")
    team = request.cookies.get("team")
    if request.method == 'POST':
        if request.form.get("delete") == "yes":
            x = requests.delete(f'{get_container("matches")}/matches/{request.form.get("id")}')
            if x.status_code == 200:
                flash("Deleted succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
        elif request.form.get("add") == "yes":
            values = request.form.to_dict()
            del values["add"]
            x = requests.post(f'{get_container("matches")}/matches', data=values)
            if x.status_code == 201:
                flash("Added succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
        else:
            # return jsonify(request.form)
            x = requests.put(f'{get_container("matches")}/matches/{request.form.get("id")}', data=request.form)
            if x.status_code == 200:
                flash("Updated succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
    if team:
        matchweek = request.args.get("week")
        if matchweek:
            x = requests.get(f'{get_container("matches")}/matches/week/{matchweek}')
        else:
            x = requests.get(f'{get_container("matches")}/matches')
        # return jsonify(x.json())
        x = x.json()["data"]
        return render_template("admin_matches.html", matches=x, obj_attr=["division_id", "matchweek", "date", "time", "home", "away"])
    else:
        return render_template("no_permission.html")

@divisions_blueprint.route('//admin/divisions', methods=['GET', 'POST'])
def admin_divisions():
    if request.cookies.get("user_type") not in ["admin", "superadmin"]:
        return render_template("no_permission.html")
    team = request.cookies.get("team")
    if request.method == 'POST':
        if request.form.get("delete") == "yes":
            x = requests.delete(f'{get_container("matches")}/divisions/{request.form.get("id")}')
            if x.status_code == 200:
                flash("Deleted succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
        elif request.form.get("add") == "yes":
            values = request.form.to_dict()
            del values["add"]
            x = requests.post(f'{get_container("matches")}/divisions', data=values)
            if x.status_code == 201:
                flash("Added succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
        else:
            # return jsonify(request.form)
            x = requests.put(f'{get_container("matches")}/divisions/{request.form.get("id")}', data=request.form)
            if x.status_code == 200:
                flash("Updated succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
    if team:
        x = requests.get(f'{get_container("matches")}/divisions')
        # return jsonify(x.json())
        x = x.json()["data"]
        return render_template("admin_divisions.html", objects=x, obj_attr=["name"])
    else:
        return render_template("no_permission.html")

@divisions_blueprint.route('//admin/referees', methods=['GET', 'POST'])
def admin_referees():
    if request.cookies.get("user_type") not in ["admin", "superadmin"]:
        return render_template("no_permission.html")
    team = request.cookies.get("team")
    if request.method == 'POST':
        if request.form.get("delete") == "yes":
            x = requests.delete(f'{get_container("matches")}/referees/{request.form.get("id")}')
            if x.status_code == 200:
                flash("Deleted succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
        elif request.form.get("add") == "yes":
            values = request.form.to_dict()
            del values["add"]
            x = requests.post(f'{get_container("matches")}/referees', data=values)
            if x.status_code == 201:
                flash("Added succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
        else:
            # return jsonify(request.form)
            x = requests.put(f'{get_container("matches")}/referees/{request.form.get("id")}', data=request.form)
            if x.status_code == 200:
                flash("Updated succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
    if team:
        x = requests.get(f'{get_container("matches")}/referees')
        # return jsonify(x.json())
        x = x.json()["data"]
        return render_template("admin_referees.html", objects=x, obj_attr=["firstname", "lastname", "birthday"])
    else:
        return render_template("no_permission.html")

@divisions_blueprint.route('//admin/clubs', methods=['GET', 'POST'])
def admin_clubs():
    if request.cookies.get("user_type") not in ["admin", "superadmin"]:
        return render_template("no_permission.html")
    team = request.cookies.get("team")
    if request.method == 'POST':
        if request.form.get("delete") == "yes":
            x = requests.delete(f'{get_container("clubs")}/clubs/{request.form.get("stam_number")}')
            if x.status_code == 200:
                flash("Deleted succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
        elif request.form.get("add") == "yes":
            values = request.form.to_dict()
            del values["add"]
            x = requests.post(f'{get_container("clubs")}/clubs', data=values)
            if x.status_code == 201:
                flash("Added succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
        else:
            # return jsonify(request.form)
            x = requests.put(f'{get_container("clubs")}/clubs/{request.form.get("stam_number")}', data=request.form)
            if x.status_code == 200:
                flash("Updated succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
    if team:
        x = requests.get(f'{get_container("clubs")}/clubs')
        # return jsonify(x.json())
        x = x.json()["data"]
        return render_template("admin_clubs.html", objects=x, obj_attr=["name", "address", "zip", "city"])
    else:
        return render_template("no_permission.html")

@divisions_blueprint.route('//admin/teams', methods=['GET', 'POST'])
def admin_teams():
    if request.cookies.get("user_type") not in ["admin", "superadmin"]:
        return render_template("no_permission.html")
    team = request.cookies.get("team")
    if request.method == 'POST':
        if request.form.get("delete") == "yes":
            x = requests.delete(f'{get_container("clubs")}/teams/{request.form.get("id")}')
            if x.status_code == 200:
                flash("Deleted succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
        elif request.form.get("add") == "yes":
            values = request.form.to_dict()
            del values["add"]
            x = requests.post(f'{get_container("clubs")}/teams', data=values)
            if x.status_code == 201:
                flash("Added succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
        else:
            # return jsonify(request.form)
            x = requests.put(f'{get_container("clubs")}/teams/{request.form.get("id")}', data=request.form)
            if x.status_code == 200:
                flash("Updated succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
    if team:
        x = requests.get(f'{get_container("clubs")}/teams')
        # return jsonify(x.json())
        x = x.json()["data"]
        return render_template("admin_teams.html", objects=x, obj_attr=["club_id"])
    else:
        return render_template("no_permission.html")

@divisions_blueprint.route('//admin/users', methods=['GET', 'POST'])
def admin_users():
    if request.cookies.get("user_type") not in ["admin", "superadmin"]:
        return render_template("no_permission.html")
    team = request.cookies.get("team")
    if request.method == 'POST':
        if request.form.get("delete") == "yes":
            x = requests.delete(f'{get_container("users")}/users/{request.form.get("id")}')
            if x.status_code == 200:
                flash("Deleted succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
        elif request.form.get("add") == "yes":
            values = request.form.to_dict()
            del values["add"]
            x = requests.post(f'{get_container("users")}/users', data=values)
            if x.status_code == 201:
                flash("Added succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
        else:
            # return jsonify(request.form)
            x = requests.put(f'{get_container("clubs")}/teams/{request.form.get("id")}', data=request.form)
            if x.status_code == 200:
                flash("Updated succesfuly")
            else:
                flash(f"Something went wrong ({x.status_code})")
    if team:
        x = requests.get(f'{get_container("users")}/users')
        # return jsonify(x.json())
        x = x.json()["data"]
        return render_template("admin_users.html", objects=x, obj_attr=["username"], superadmin=request.cookies.get("user_type")=="superadmin")
    else:
        return render_template("no_permission.html")
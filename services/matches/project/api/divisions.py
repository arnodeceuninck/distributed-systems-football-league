from flask import Blueprint, jsonify, request, render_template
# from project.api.models import User
from project import db
from sqlalchemy import exc, or_
from project.api.models import Division, Match

divisions_blueprint = Blueprint('divisions', __name__, template_folder='./templates')


@divisions_blueprint.route('/divisions/ping', methods=['GET'])
def pint_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@divisions_blueprint.route('/divisions', methods=['POST'])
def add_division():
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    name = post_data.get("name")
    try:
        division = Division(name=name)
        db.session.add(division)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': f'{division.id} was added!'
        }
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@divisions_blueprint.route('/divisions/<division_id>', methods=['GET'])
def get_single_division(division_id):
    response_object = {
        'status': 'fail',
        'message': 'division does not exist'
    }
    try:
        division = Division.query.get(division_id)
        if not division:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': division.to_json()
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404


@divisions_blueprint.route('/divisions', methods=['GET'])
def get_all_divisions():
    """Get all divisions"""
    response_object = {
        'status': 'success',
        'data': {'divisions': [division.to_json() for division in Division.query.all()]}
    }
    return jsonify(response_object), 200


@divisions_blueprint.route('/divisions/<division_id>/fixtures', methods=['GET'])
def get_division_fixtures(division_id):
    response_object = {
        'status': 'fail',
        'message': 'division does not exist'
    }
    try:
        division = Division.query.get(division_id)
        if not division:
            return jsonify(response_object), 404
        else:
            matches = Match.query.filter_by(division_id=division_id)
            response_object = {
                'status': 'success',
                'data': {'fixtures': [match.to_json() for match in matches]}
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404


@divisions_blueprint.route('/divisions/<division_id>/fixtures/<team_id>', methods=['GET'])
def get_divisions_fixtures_for_team(division_id, team_id):
    response_object = {
        'status': 'fail',
        'message': 'division does not exist'
    }
    try:
        division = Division.query.get(division_id)
        if not division:
            return jsonify(response_object), 404
        else:
            matches = Match.query.filter_by(division_id=division_id).filter(
                or_(Match.home == team_id, Match.away == team_id))
            response_object = {
                'status': 'success',
                'data': {'fixtures': [match.to_json() for match in matches]}
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404


@divisions_blueprint.route('/divisions/<division_id>/league_table', methods=['GET'])
def get_league_table(division_id):
    response_object = {
        'status': 'fail',
        'message': 'division does not exist'
    }
    try:
        division = Division.query.get(division_id)
        if not division:
            return jsonify(response_object), 404
        else:
            # TODO: Team most goals, team least goals conceded, team most clean sheets

            response_object = {
                'status': 'success',
                'data': {'league': division.leauge_table()}
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404


@divisions_blueprint.route('/divisions/<division_id>/stats', methods=['GET'])
def get_division_stats(division_id):
    response_object = {
        'status': 'fail',
        'message': 'division does not exist'
    }
    try:
        division = Division.query.get(division_id)
        if not division:
            return jsonify(response_object), 404
        else:
            goals_per_team = dict()
            for match in Match.query.filter_by(division_id=division_id):
                if match.goals_home == None or match.goals_away == None:
                    continue
                goals_per_team.setdefault(match.away, {"goals_scored": 0, "goals_against": 0})
                goals_per_team.setdefault(match.home, {"goals_scored": 0, "goals_against": 0})
                goals_per_team[match.away]["goals_scored"] += match.goals_away
                goals_per_team[match.home]["goals_scored"] += match.goals_home
                goals_per_team[match.away]["goals_against"] += match.goals_home
                goals_per_team[match.home]["goals_against"] += match.goals_away

            best_attack = max(goals_per_team, key=lambda x: goals_per_team[x]["goals_scored"])
            best_defense = min(goals_per_team, key=lambda x: goals_per_team[x]["goals_against"])


            most_clean_sheets = None
            for team in goals_per_team:
                if goals_per_team[team]["goals_scored"] == 0:
                    most_clean_sheets = team
                    break

            # TODO: Team most goals, team least goals conceded, team most clean sheets
            response_object = {
                'status': 'success',
                'data': {"best_attack": {"team": best_attack, "count": goals_per_team[best_attack]["goals_scored"]},
                         "best_defense": {"team": best_defense, "count": goals_per_team[best_defense]["goals_against"]},
                         "most_clean_sheets": most_clean_sheets}
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404

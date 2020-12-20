from flask import Blueprint, jsonify, request, render_template
#from project.api.models import User
from project import db
from sqlalchemy import exc, or_, and_, desc, func, asc
from project.api.models import Match
from  datetime import date
matches_blueprint = Blueprint('matches', __name__, template_folder='./templates')


@matches_blueprint.route('/matches/ping', methods=['GET'])
def pint_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@matches_blueprint.route('/matches', methods=['POST'])
def add_match():
    post_data = request.form
    if not post_data:
        post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    division_id = post_data.get("division_id")
    matchweek = post_data.get("matchweek")
    date = post_data.get("date")
    time = post_data.get("time")
    home = post_data.get("home")
    away = post_data.get("away")
    status_id = post_data.get("status_id")
    goals_home = post_data.get("goals_home")
    goals_away = post_data.get("goals_away")

    try:
        match = Match(division_id=division_id, matchweek=matchweek, date=date, time=time, home=home, away=away, status_id=status_id, goals_home=goals_home, goals_away=goals_away)
        db.session.add(match)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': f'{match.id} was added!'
        }
        return jsonify(response_object), 201
    except (exc.IntegrityError, TypeError) as e:
        db.session.rollback()
        return jsonify(response_object), 400


@matches_blueprint.route('/matches/<match_id>', methods=['GET'])
def get_single_match(match_id):
    response_object = {
        'status': 'fail',
        'message': 'Match does not exist'
    }
    try:
        match = Match.query.get(match_id)
        if not match:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': match.to_json()
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404

@matches_blueprint.route('/matches/<match_id>', methods=['PUT'])
def update_match(match_id):
    response_object = {
        'status': 'fail',
        'message': 'Object does not exist'
    }
    try:
        obj = Match.query.get(match_id)
        if not obj:
            return jsonify(response_object), 404
        else:
            obj.update(request.form)
            db.session.commit()
            response_object = {
                'status': 'success'
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404


@matches_blueprint.route('/matches/<match_id>', methods=['DELETE'])
def delete_match(match_id):
    response_object = {
        'status': 'fail',
        'message': 'Object does not exist'
    }
    try:
        Match.query.filter_by(id=match_id).delete()
        db.session.commit()
        response_object = {
            'status': 'success'
        }
        return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404

@matches_blueprint.route('/matches', methods=['GET'])
def get_all_matches():
    """Get all matches"""
    response_object = {
        'status': 'success',
        'data': {'matches': [match.to_json() for match in Match.query.all()]}
    }
    return jsonify(response_object), 200

@matches_blueprint.route('/matches/stats/<team1>/vs/<team2>', methods=['GET'])
def get_match_stats(team1, team2):
    response_object = {
        'status': 'fail',
        'message': 'Match does not exist'
    }
    try:
        previous_matches = Match.query.filter(func.date(Match.date) < date.today())
        matches = previous_matches.filter(or_(and_(Match.home == team1, Match.away == team2),
                                                      and_(Match.home == team1, Match.away == team2)))
        total_matches_played = matches.count()
        times_1_won = matches.filter(or_(and_(Match.home == team1, Match.goals_home > Match.goals_away),
                                             and_(Match.away == team1, Match.goals_away > Match.goals_home))).count()
        times_2_won = matches.filter(or_(and_(Match.home == team2, Match.goals_home > Match.goals_away),
                                             and_(Match.away == team2, Match.goals_away > Match.goals_home))).count()
        last_3_together = matches.order_by(desc(Match.date)).limit(3).all()
        last_5_team1 = previous_matches.filter(or_(Match.home == team1, Match.away == team1)).filter(and_(Match.goals_home != None, Match.goals_away != None)).order_by(desc(Match.date)).limit(5).all()
        last_5_team2 = previous_matches.filter(or_(Match.home == team2, Match.away == team2)).filter(and_(Match.goals_home != None, Match.goals_away != None)).order_by(desc(Match.date)).limit(5).all()

        response_object = {
            'status': 'success',
            'data': {"total_matches_played": total_matches_played,
                     "team1": {"times_won": times_1_won, "last": [match.to_json() for match in last_5_team1]},
                     "team2": {"times_won": times_2_won, "last": [match.to_json() for match in last_5_team2]},
                     "last_together": [match.to_json() for match in last_3_together]}
        }
        return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404

@matches_blueprint.route('/matches/recent/<team1>', methods=['GET'])
def get_team_recent(team1):
    response_object = {
        'status': 'fail',
        'message': 'Match does not exist'
    }
    try:
        team_matches = Match.query.filter(or_(Match.home == team1, Match.away == team1))
        previous_matches = team_matches.filter(func.date(Match.date) < date.today()).order_by(desc(Match.date)).limit(3).all()
        upcoming_matches = team_matches.filter(func.date(Match.date) >= date.today()).order_by(asc(Match.date)).all()

        response_object = {
            'status': 'success',
            'data': {"previous": [match.to_json() for match in previous_matches],
                     "upcoming": [match.to_json() for match in upcoming_matches]}
        }
        return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404

@matches_blueprint.route('/matches/home/<team1>', methods=['GET'])
def get_home(team1):
    response_object = {
        'status': 'fail',
        'message': 'Match does not exist'
    }
    try:
        team_matches = Match.query.filter(Match.home == team1).all()

        response_object = {
            'status': 'success',
            'data': [match.to_json() for match in team_matches]
        }
        return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404

@matches_blueprint.route('/matches/week/<week_id>', methods=['GET'])
def get_matches_by_week(week_id):
    """Get all matches"""
    response_object = {
        'status': 'success',
        'data': {'matches': [match.to_json() for match in Match.query.filter(Match.matchweek == week_id).all()]}
    }
    return jsonify(response_object), 200

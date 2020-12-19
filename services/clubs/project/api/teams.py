from flask import Blueprint, jsonify, request, render_template
from project.api.models import Club, Team
from project import db
from sqlalchemy import exc

teams_blueprint = Blueprint('teams', __name__, template_folder='./templates')

@teams_blueprint.route('/teams/ping', methods=['GET'])
def pint_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

@teams_blueprint.route('/teams', methods=['POST'])
def add_team():
    post_data = request.form
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    stam_number = post_data.get("club_id")
    outfit_colors = post_data.get("outfit_colors")
    suffix = post_data.get("suffix")
    try:
        team = Team(club_id=stam_number, outfit_colors=outfit_colors, suffix=suffix)
        db.session.add(team)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': f'{team.id} was added!'
        }
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        raise e
        db.session.rollback()
        return jsonify(response_object), 400


@teams_blueprint.route('/teams/<team_id>', methods=['GET'])
def get_single_team(team_id):
    response_object = {
        'status': 'fail',
        'message': 'team does not exist'
    }
    try:
        team = Team.query.get(team_id)
        if not team:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': team.to_json()
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404

@teams_blueprint.route('/teams', methods=['GET'])
def get_all_teams():
    """Get all teams"""
    response_object = {
        'status': 'success',
        'data': {'teams': [team.to_json() for team in Team.query.all()]}
    }
    return jsonify(response_object), 200

@teams_blueprint.route('/teams/<obj_id>', methods=['PUT'])
def update_obj(obj_id):
    response_object = {
        'status': 'fail',
        'message': 'Object does not exist'
    }
    try:
        obj = Team.query.get(obj_id)
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


@teams_blueprint.route('/teams/<obj_id>', methods=['DELETE'])
def delete_obj(obj_id):
    response_object = {
        'status': 'fail',
        'message': 'Object does not exist'
    }
    try:
        Club.query.filter_by(id=obj_id).delete()
        db.session.commit()
        response_object = {
            'status': 'success'
        }
        return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404


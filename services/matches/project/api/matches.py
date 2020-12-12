from flask import Blueprint, jsonify, request, render_template
#from project.api.models import User
from project import db
from sqlalchemy import exc

matches_blueprint = Blueprint('matches', __name__, template_folder='./templates')


@matches_blueprint.route('/matches/ping', methods=['GET'])
def pint_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })



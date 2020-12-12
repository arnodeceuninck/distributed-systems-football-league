from flask import Blueprint, jsonify, request, render_template
#from project.api.models import User
from project import db
from sqlalchemy import exc

clubs_blueprint = Blueprint('clubs', __name__, template_folder='./templates')


@clubs_blueprint.route('/clubs/ping', methods=['GET'])
def pint_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })



from flask import Blueprint, jsonify, request, render_template

divisions_blueprint = Blueprint('divisions', __name__, template_folder='./templates')


@divisions_blueprint.route('/ping', methods=['GET'])
def pint_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
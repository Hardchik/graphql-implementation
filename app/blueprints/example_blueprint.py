from flask import Blueprint
from app.controllers.example_controller import example_controller

example_blueprint = Blueprint('example_blueprint', __name__)

@example_blueprint.route('/example', methods=['GET'])
def example():
    return example_controller()

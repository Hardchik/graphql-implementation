from flask import Flask
from flask_graphql import GraphQLView
from app.schema.schema import schema

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    from app.blueprints.example_blueprint import example_blueprint
    app.register_blueprint(example_blueprint, url_prefix='/api')

    app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

    return app

from flask import Flask, Response, request
from flask_graphql import GraphQLView
from prometheus_client import CollectorRegistry, generate_latest, Gauge, Histogram, CONTENT_TYPE_LATEST
import time  # Use time module to measure latency
from app.schema.schema import schema
from app.blueprints.example_blueprint import example_blueprint

# Create a registry for Prometheus metrics
registry = CollectorRegistry()

# Define some example metrics
REQUEST_COUNT = Gauge('request_count', 'Total request count', ['method', 'endpoint', 'blueprint'], registry=registry)
REQUEST_LATENCY = Gauge('request_latency_seconds', 'Request latency in seconds', ['method', 'endpoint', 'blueprint'], registry=registry)

# Define GraphQL specific metrics
GRAPHQL_QUERY_COUNT = Gauge('graphql_query_count', 'Total GraphQL query count', ['operation'], registry=registry)
GRAPHQL_QUERY_LATENCY = Histogram('graphql_query_latency_seconds', 'GraphQL query latency in seconds', ['operation'], registry=registry)

# Global variable to store start time
start_time = {}

def before_request():
    # Store start time for request latency measurement
    start_time[request.path] = time.time()
    blueprint = request.url_rule.rule if request.url_rule else 'no_blueprint'
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path, blueprint=blueprint).inc()

def after_request(response):
    # Calculate latency
    end_time = time.time()
    latency = end_time - start_time.get(request.path, end_time)
    blueprint = request.url_rule.rule if request.url_rule else 'no_blueprint'
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.path, blueprint=blueprint).set(latency)
    return response

def metrics():
    return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Register blueprint
    app.register_blueprint(example_blueprint, url_prefix='/api')

    # Instrument GraphQL view
    graphql_view = GraphQLView.as_view('graphql', schema=schema, graphiql=True)
    app.add_url_rule('/graphql', view_func=graphql_view)

    # Register before/after hooks
    app.before_request(before_request)
    app.after_request(after_request)

    # Add /metrics endpoint to serve Prometheus metrics
    app.add_url_rule('/metrics', view_func=metrics)

    return app

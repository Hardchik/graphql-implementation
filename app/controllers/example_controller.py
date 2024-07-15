from app.services.example_service import example_service

def example_controller():
    result = example_service()
    return result

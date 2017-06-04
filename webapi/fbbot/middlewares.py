from quizzler import db


class CommitDatabaseMiddleware:
    """Middleware to commit the database after each view cycle.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        db.commit()
        return response

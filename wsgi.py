from anella.flask_app import create_app
from anella.flask_app import authorizate

app = create_app()

@app.after_request
@authorizate
def after_request(response):
    """
    Suport for CORS at Flask app
    :type response: object
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,PATCH,POST,DELETE')
    #   response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


def bootstrap_app():
    return app


if __name__ == "__main__":
    app.run(host=app.config['HOST'], port=app.config['PORT'], threaded=True)

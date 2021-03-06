from anella.flask_app import create_app
from anella.security.authorize import authorizate

app = create_app()

@app.after_request
def after_request(response):
    """
    Suport for CORS at Flask app
    :type response: object
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,PATCH,POST,DELETE')
    #   response.headers.add('Access-Control-Allow-Credentials', 'true')
    # Black magic wsgi
    response.status_code = response.status_code
    return response


@app.before_request
@authorizate
def before_request():
    pass


def bootstrap_app():
    return app


if __name__ == "__main__":
    app.run(host=app.config['HOST'], port=app.config['PORT'], threaded=True)

import time
from anella.flask_app import create_app
from anella import output

app = create_app()

start = stop = 0

@app.before_request
def before_request():
  global start
  start = time.time()
  output.OUTPUT.info("Req. start time %s " % (start))

@app.after_request
def after_request(response):
  """
  Suport for CORS at Flask app
  """
  global stop
  stop = time.time()
  output.OUTPUT.info("Response time %s " % (stop-start))

  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
#   response.headers.add('Access-Control-Allow-Credentials', 'true')
  return response

def bootstrap_app():
  return app

if __name__ == "__main__":
    app.run(host=app.config['HOST'], port=app.config['PORT'], threaded=True )

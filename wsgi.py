from anella.flask_app import create_app

# import ssl
# # A fake ssl_context for python<2.7.11
# from pymongo.ssl_context import SSLContext
# 
# ssl_context = SSLContext(ssl.PROTOCOL_TLSv1)
# ssl_context.load_cert_chain('anella.crt', 'anella.key')
ssl_context = ('anella.crt', 'anella.key')

app = create_app()

if __name__ == "__main__":
    app.run(host=app.config['HOST'], port=app.config['PORT'])
    # , ssl_context=ssl_context)

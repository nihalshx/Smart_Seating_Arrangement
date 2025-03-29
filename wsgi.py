from flask import Flask, request

# Create the Flask app
app = Flask(__name__)

# Import the main app only when needed
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Import the main application only when handling requests
    # This helps reduce initial load time and memory usage
    from app import app as flask_app
    return flask_app.wsgi_app(request.environ, lambda status, headers, exc_info: [])

if __name__ == "__main__":
    app.run() 
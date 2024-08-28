from waitress import serve
from app import app  # Import the Flask app instance
from app.secure.default_account import generateAdmin

if __name__ == "__main__":
    if generateAdmin():
        print('Created NEW Default Admin')
        
    serve(app, host='127.0.0.1', port=8080)




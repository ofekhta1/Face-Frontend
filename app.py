from flask import Flask, render_template, request, session, url_for, redirect, jsonify
import os
import requests as req
from flask import send_from_directory
from routes import register_routes
from modules import AppPaths,upload_from_request,extract_face_selection_from_request,upload_from_zip,upload_from_url
APP_DIR = os.path.dirname(__file__)
STATIC_FOLDER = os.path.join(APP_DIR, "static")
SERVER_URL = AppPaths.SERVER_URL
# Create the folders if they don't exist
os.makedirs(STATIC_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_FOLDER)
register_routes(app)

@app.route("/pool/<path:filename>")
def custom_static(filename):
	return SERVER_URL + "/pool/" + filename
	# return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/static_images/<path:filename>")
def processed_static(filename):
	return send_from_directory(STATIC_FOLDER, filename)

app.secret_key = "your_secret_key"
app.config["ROOT_FOLDER"] = APP_DIR
app.config["SERVER_URL"] = SERVER_URL


if __name__ == "__main__":
	try:
		app.run(debug=True, port=5000)
	except Exception as e:
		print(f"Error: {e}")

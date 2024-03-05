from flask import Flask, render_template, request, session, url_for, redirect, jsonify
import os
import requests as req
from flask import send_from_directory
import tempfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json


APP_DIR = os.path.dirname(__file__)
STATIC_FOLDER = os.path.join(APP_DIR, "static")
SERVER_URL = "http://127.0.0.1:5057"
# Create the folders if they don't exist
os.makedirs(STATIC_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_FOLDER)


@app.route("/pool/<path:filename>")
def custom_static(filename):
    return SERVER_URL + "/pool/" + filename
    # return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/static_images/<path:filename>")
def processed_static(filename):
    return send_from_directory(STATIC_FOLDER, filename)


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# Function to download and save an image
def save_image(url, directory):
    response = req.get(url, stream=True)
    if response.status_code == 200:
        # Extract the filename from the URL
        filename = os.path.join(directory, os.path.basename(url))
        with open(filename, "w+b") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
            return filename;


app.secret_key = "your_secret_key"


app.config["ROOT_FOLDER"] = APP_DIR
app.config["SERVER_URL"] = SERVER_URL


def saveTempFiles(temp_dir, files):
    saved_files = {}
    for key, file in files.items():
        if file.filename != "":
<<<<<<< HEAD
            file_path = os.path.join(temp_dir,file.filename);
=======
            file_path = os.path.join(temp_dir,file.filename)
>>>>>>> a6e5f0c28dc663d2a110759abee6ad54f7daf7c8
            file.save(file_path)
            saved_files[key] = open(file_path, "rb")
    return saved_files


@app.route("/clustering", methods=["GET", "POST"])
def clustering():
    errors = []
    messages = []
    groups = session.get("groups", {})
    if request.method == "POST":
        try:
            jsonStr = request.form.get("jsonData", "")
            groups = json.loads(jsonStr)
            session["groups"] = groups
        except Exception as e:
            print("failed to display clustering results because:")
            print(e)
    return render_template(
        "clustering.html",
        groups=groups,
        errors=errors,
        messages=messages,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    images = []
    messages = []
    errors = []

    uploaded_images = session.get("uploaded_images", [])
    faces_length = session.get("faces_length", [0, 0])
    current_images = session.get("current_images", [])
    combochanges = session.get("selected_faces", [-2, -2])

    if request.method == "POST":
        face_num_1 = request.form.get("face_num1")
        face_num_2 = request.form.get("face_num2")
        face_num_1 = -2 if request.form.get("face_num1") == "" else int(face_num_1)
        face_num_2 = -2 if request.form.get("face_num2") == "" else int(face_num_2)
        combochanges = [face_num_1, face_num_2]
        action = request.form.get("action")
        if action == "Upload":
            with tempfile.TemporaryDirectory() as temp_dir:
                saved_files = saveTempFiles(temp_dir, request.files)
                if len(saved_files) > 0:
                    response = req.post(SERVER_URL + "/api/upload", files=saved_files)
                    data = response.json()
                    saved_files
                    errors = errors + data["errors"]
                    if len(data["images"]) > 0:
                        max_size = 2
                        initial = len(current_images) - 1
                        uploaded = [
                            x.filename
                            for x in request.files.values()
                            if x.filename != ""
                        ]
                        for i in range(len(uploaded)):
                            current_index = (initial + 1 + i) % max_size
                            if current_index == initial + 1:
                                current_images.append(data["images"][i])
                            else:
                                current_images[current_index] = data["images"][i]
                            faces_length[current_index] = data["faces_length"][i]

                    uploaded_images = uploaded_images + data["images"]
                    for saved in saved_files.values():
                        saved.close();
                else:
                    errors.append(
                        "Saving Images failed,make sure you uploaded 2 valid images"
                    )

        elif action in ["Detect", "Align"]:
            if action == "Align":
                url = SERVER_URL + "/api/align"

            elif action == "Detect":
                url = SERVER_URL + "/api/detect"
            if len(current_images) > 0:
                response = req.post(url, data={"images": current_images})
                data = response.json()
                uploaded_images = uploaded_images + data["images"]
                errors = errors + data["errors"]
                # current_images=data['images']
                messages = messages + data["messages"]
                # faces_length = data["faces_length"]
                for i in range(len(data['faces_length'])):
                    faces_length[i]=data['faces_length'][i]
            else:
                errors.append("No images uploaded!")
        elif action == "Clear":
            uploaded_images = []
            current_images = []
            faces_length = [0, 0]

        elif action == "Compare":
            url = SERVER_URL + "/api/compare"
            response = req.post(
                url, data={"images": current_images, "selected_faces": combochanges}
            )
            data = response.json()
            errors = errors + data["errors"]
            messages = messages + data["messages"]

        elif action == "Check":
            url = SERVER_URL + "/api/check"
            if len(current_images) > 0:
                response = req.post(
                    url,
                    data={"image": current_images[0], "selected_face": combochanges[0]},
                )
                data = response.json()
                errors = errors + data["errors"]
                messages = messages + data["messages"]
                most_similar_image = data["image"]
                if most_similar_image:
                    if len(current_images) == 1:
                        current_images.append(most_similar_image)
                    else:
                        current_images[1] = most_similar_image
                    combochanges[1] = data["face"]
                    faces_length[1] = data["face_length"]
            else:
                errors.append("No images uploaded!")
        
        elif action == "improve":
            url = SERVER_URL + "/api/improve"
            response = req.post(url, data={"images": current_images})
            data = response.json()
            errors = errors + data["errors"]
            current_images.clear()
            if len(data) > 1:
                current_images=data["enhanced_images"];

        elif action == "Check_family":
            url = SERVER_URL + "/api/check_family"
            response = req.post(url, data={"images": current_images})
            data = response.json()
            errors = errors + data["errors"]
            messages = messages + data["messages"]


        session["current_images"] = current_images
        session["selected_faces"] = combochanges
        session["uploaded_images"] = uploaded_images
        session["faces_length"] = faces_length

    images = uploaded_images

    return render_template(
        "image.html",
        images=images,
        current=current_images,
        faces_length=faces_length,
        selected_faces=combochanges,
        errors=errors,
        messages=messages,
    )


@app.route("/download", methods=["POST"])
def download():
    errors=[]
    website_url = request.form.get("website_url")
    with tempfile.TemporaryDirectory() as temp_dir:
        downloaded_images={};
        response = req.get(website_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            img_tags = soup.find_all("img")
            i=0;
            for img in img_tags:
                i=i+1;
                img_url = img.get("src")
                img_url = urljoin(website_url, img_url)
                fileName=save_image(img_url, temp_dir)
                downloaded_images[f"image{i}"] =  open(fileName,'rb')
            print("Images downloaded and saved successfully.")
            if len(downloaded_images) > 0:
                response = req.post(SERVER_URL + "/api/upload", files=downloaded_images)
                data = response.json()
                errors = errors + data["errors"]
    
        else:
            print(f"Failed to fetch the website. Status code: {response.status_code}")

    return redirect(url_for("index"))



if __name__ == "__main__":
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"Error: {e}")

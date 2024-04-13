from flask import Flask, render_template, request, session, url_for, redirect, jsonify
import os
import requests as req
from flask import send_from_directory
import json
from modules import AppPaths,upload_from_request,extract_face_selection_from_request,upload_from_zip,upload_from_url

APP_DIR = os.path.dirname(__file__)
STATIC_FOLDER = os.path.join(APP_DIR, "static")
SERVER_URL = AppPaths.SERVER_URL
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


app.secret_key = "your_secret_key"


app.config["ROOT_FOLDER"] = APP_DIR
app.config["SERVER_URL"] = SERVER_URL


@app.route("/search",methods=["GET","POST"])
def search():
    messages = []
    errors = []

    faces_length = session.get("faces_length",[0,0])
    current_images = session.get("current_images", [None,None])
    images=[]
    combochanges = session.get("selected_faces", [-2, -2])
    if request.method == "POST":
        combochanges= extract_face_selection_from_request(request);
        action = request.form.get("action")
        if(action=="Upload"):
            upload_from_request(request,current_images,faces_length)
        elif(action== "improve"):
            url = SERVER_URL + "/api/improve"
            length=len(current_images)
            index=request.form.get("index",type=int);
            if index is not None and index<length:
                if(current_images[index].startswith('enhanced_')):
                    current_images[index]=current_images[index].replace("enhanced_","")
                else:
                    response = req.post(url, data={"image": current_images[index]})
                    data = response.json()
                    errors = errors + data["errors"]
                    messages = messages+data["messages"]
                    current_images[index]=data['enhanced_image']
        elif(action=="Search"):
            k=request.form.get("k",3);
            url = SERVER_URL + "/api/check_many"
            response = req.post(url, data={"image": current_images[0],"selected_face":combochanges[0],"number_of_images":k})
            data = response.json()
            errors = errors + data["errors"]
            images = images + data["images"]
        elif action == "Clear":
            length=len(current_images)
            index=request.form.get("index",type=int);
            if index is not None and index<length:
                del current_images[index]
                del faces_length[index]
                del combochanges[index]
                faces_length.append(0)
                combochanges.append(0)

            

    session["current_images"] = current_images
    session["selected_faces"] = combochanges
    session["faces_length"] = faces_length
    return render_template(
        "search.html",
        images=images,
        current=current_images[0] if len(current_images)>0 else None,
        faces_length=faces_length[0],
        selected_face=combochanges[0],
        errors=errors,
        messages=messages,
    )

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
@app.route("/check_family", methods=["GET", "POST"])
def check_family():
    images = []
    messages = []
    errors = []

    faces_length = session.get("faces_length", [0, 0])
    current_images = session.get("current_images", [])
    combochanges = session.get("selected_faces", [-2, -2])
    if request.method == "POST":
        combochanges= extract_face_selection_from_request(request);
        action = request.form.get("action")
        if(action=="Upload"):
            upload_from_request(request,current_images,faces_length)
        elif(action== "improve"):
            url = SERVER_URL + "/api/improve"
            length=len(current_images)
            index=request.form.get("index",type=int);
            if index is not None and index<length:
                if(current_images[index].startswith('enhanced_')):
                    current_images[index]=current_images[index].replace("enhanced_","")
                else:
                    response = req.post(url, data={"image": current_images[index]})
                    data = response.json()
                    errors = errors + data["errors"]
                    messages = messages+data["messages"]
                    current_images[index]=data['enhanced_image']
        elif(action=="Check_Family"):
            url = SERVER_URL + "/api/check_family"
            response = req.post(url, data={"images": current_images,"selected_faces":combochanges})
            data = response.json()
            errors = errors + data["errors"]
            messages = messages + data["messages"]
        elif action == "Clear":
            length=len(current_images)
            index=request.form.get("index",type=int);
            if index is not None and index<length:
                del current_images[index]
                del faces_length[index]
                del combochanges[index]
                faces_length.append(0)
                combochanges.append(0)

            

    session["current_images"] = current_images
    session["selected_faces"] = combochanges
    session["faces_length"] = faces_length
    return render_template(
        "check_family.html",
        images=images,
        current=current_images,
        faces_length=faces_length,
        selected_faces=combochanges,
        errors=errors,
        messages=messages,
    )
@app.route("/upload",methods=["GET","POST"])
def upload():
    messages = []
    errors = []
    if(request.method=="POST"):
        method=request.form.get("type","url");
        if(method=="url"):
            messages,errors=upload_from_url(website_url=request.form.get('website_url'))
        elif(method=="zipfile"):
            file = request.files['zip_file']  
            file_like_object = file.stream._file  
            messages,errors=upload_from_zip(file_like_object)

        
    return render_template(
        "upload.html",
        errors=errors,
        messages=messages,
    )
@app.route("/template_matching", methods=["GET", "POST"])
def template_matching():
    messages = []
    errors = []
    box=[]
    current_images = session.get("current_template_images", [])
    if request.method == "POST":
        action = request.form.get("action")
        if(action=="Upload"):
            upload_from_request(request,current_images,[0,0],save_invalid=True)
        elif(action=="Match_Template"):
            if(len(current_images)==0):
                errors.append("Upload a template first!")
            else:
                url = SERVER_URL + "/api/check_template"
                response = req.post(url, data={"template": current_images[0]})
                data = response.json()
                errors = errors + data["errors"]
                if(len(errors)==0):
                    if(len(current_images)==1):
                        current_images.append(data['image']);
                    else:
                        current_images[1]=data['image']
                    box=data['box'];
                messages = messages + data["messages"]
        elif action == "Clear":
            current_images = []
    

    session["current_template_images"] = current_images
    return render_template(
        "template_matching.html",
        box=box,
        current=current_images,
        errors=errors,
        messages=messages,
    )

@app.route("/", methods=["GET", "POST"])
def index():
    images = []
    messages = []
    errors = []
    action = request.form.get("action")

    uploaded_images = session.get("uploaded_images", [])
    faces_length = session.get("faces_length", [0, 0])
    current_images = session.get("current_images", [])
    #current_detect_images="detected_"+current_images
    combochanges = session.get("selected_faces", [-2, -2])

    if request.method == "POST":
        combochanges= extract_face_selection_from_request(request);
        if action == "Upload":
            temp_err=upload_from_request(request,current_images,faces_length)
            errors=errors+temp_err
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
             
                for i in range(len(data['faces_length'])):
                    faces_length[i]=data['faces_length'][i]
            else:
                errors.append("No images uploaded!")
        elif action == "Clear":
            length=len(current_images)
            index=request.form.get("index",type=int);
            if index is not None and index<length:
                del current_images[index]
                del faces_length[index]
                del combochanges[index]
                faces_length.append(0)
                combochanges.append(0)

                uploaded_images = []
            

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
            length=len(current_images)
            index=request.form.get("index",type=int);
            if index is not None and index<length:
                if(current_images[index].startswith('enhanced_')):
                    current_images[index]=current_images[index].replace("enhanced_","")
                else:
                    response = req.post(url, data={"image": current_images[index]})
                    data = response.json()
                    errors = errors + data["errors"]
                    messages = messages+data["messages"]
                    current_images[index]=data['enhanced_image']

 

        
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


if __name__ == "__main__":
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"Error: {e}")

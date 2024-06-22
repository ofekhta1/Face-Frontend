from flask import Blueprint, render_template, request, session
from modules import upload_from_zip,upload_from_url

upload_bp = Blueprint('upload', __name__)

@upload_bp.route("/upload", methods=["GET", "POST"])
def upload():
    messages = []
    errors = []
    embedder_name = session.get("embedder_name", "")
    detector_name = session.get("detector_name", "")
    if(request.method=="POST"):
        detector_name=request.form.get("detector_name",default="SCRFD10G",type=str);
        embedder_name=request.form.get("embedder_name",default="ResNet100GLint360K",type=str);
        method=request.form.get("type","url");
        #check if to upload images data  from url/zip file
        if(method=="url"):
            messages,errors=upload_from_url(website_url=request.form.get('website_url'))
        elif(method=="zipfile"):
            file = request.files['zip_file']  
            file_like_object = file.stream._file  
            messages,errors=upload_from_zip(file_like_object)

    session["detector_name"] = detector_name
    session["embedder_name"] = embedder_name
        
    return render_template(
        "upload.html",
        errors=errors,
        messages=messages,
        detector_name=detector_name,
        embedder_name=embedder_name
    )
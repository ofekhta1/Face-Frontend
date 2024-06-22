from flask import Blueprint, render_template, request, session
from modules import AppPaths
import requests as req

gallery_bp = Blueprint('gallery', __name__)

@gallery_bp.route("/gallery", methods=["GET"])
def gallery():
    errors = []
    messages = []
    detector_name=request.form.get("detector_name",default="SCRFD10G",type=str);
    embedder_name=request.form.get("embedder_name",default="ResNet100GLint360K",type=str);

    try:
        url = AppPaths.SERVER_URL + "/api/gallery"
        response = req.get(url, params={"detector_name": detector_name,
                                        "embedder_name":embedder_name
                                        })
        data = response.json()

        images=data
    except Exception as e:
        print("failed to display gallery results because:")
        print(e)

        
    session["detector_name"] = detector_name
    session["embedder_name"] = embedder_name

    return render_template(
        "gallery.html",
        images=images,
        embedder_name=embedder_name,
        detector_name=detector_name,
        errors=errors,
        messages=messages,
    )

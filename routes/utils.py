from flask import Blueprint, jsonify, request, session
from modules import AppPaths
import json
import requests as req
utils_bp = Blueprint('utils', __name__)

@utils_bp.route("/update_selection", methods=[ "POST"])
def update_selection():
    data = request.json

    idx=data.get("index",0)
    image_name=data.get("image","")
    detector_name=data.get("detector_name","")
    embedder_name=data.get("embedder_name","")
    parts=image_name.split('_',2);
    filename=parts[-1];
    face_num=int(parts[-2])
    current_images = session.get("current_images", [])
    combochanges = session.get("selected_faces", [-2, -2])
    faces_indices = session.get("faces_indices", [{},{}])
    # get faces_indices
   
    if len(current_images)>idx:
        current_images[idx]=filename
    else:
        current_images.append(filename)
    combochanges[idx]=face_num


    url = AppPaths.SERVER_URL + "/api/get_indices"
    response = req.post(
        url, data={"images": current_images,"detector_name":detector_name,
        "embedder_name":embedder_name,"image":filename}
    )
    result_data = response.json()
    faces_indices[idx]=result_data['detector_indices']

    session["faces_indices"] = faces_indices
    session["current_images"]=current_images
    session["selected_faces"]=combochanges
    return jsonify(current_images),200
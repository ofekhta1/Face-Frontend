from flask import Blueprint, render_template, request, session
from modules import AppPaths,upload_from_request,extract_face_selection_from_request
import requests as req

search_bp = Blueprint('search', __name__)

@search_bp.route("/search", methods=["GET", "POST"])
def search():
    messages = []
    errors = []
    detector_name = session.get("detector_name","")
    embedder_name = session.get("embedder_name","")
    faces_indices = session.get("faces_indices",[{},{}])
    current_images = session.get("current_images", [])
    parameters = session.get("parameters", {})
    images=[]
    combochanges = session.get("selected_faces", [-2, -2])
    if request.method == "POST":
        detector_name=request.form.get("detector_name",default="SCRFD10G",type=str);
        embedder_name=request.form.get("embedder_name",default="ResNet100GLint360K",type=str);
        combochanges= extract_face_selection_from_request(request,faces_indices);
        similarity_thresh=request.form.get("SimilarityThreshold",default=0.5,type=float);
        parameters['similarity_thresh']=similarity_thresh
        action = request.form.get("action")
        if(action=="Upload"):
            upload_from_request(request,current_images,faces_indices,detector_name,embedder_name)
        elif(action== "improve"):
            url = AppPaths.SERVER_URL + "/api/improve"
            length=len(current_images)
            index=request.form.get("index",type=int);
            if index is not None and index<length:
                if(current_images[index].startswith('enhanced_')):
                    current_images[index]=current_images[index].replace("enhanced_","")
                else:
                    response = req.post(url, data={"image": current_images[index],"detector_name":detector_name,
                                    "embedder_name":embedder_name})
                    data = response.json()
                    errors = errors + data["errors"]
                    messages = messages+data["messages"]
                    current_images[index]=data['enhanced_image']
        elif(action=="Search"):
            k=request.form.get("k",3);
            url = AppPaths.SERVER_URL + "/api/check_many"
            response = req.post(url, data={"image": current_images[0],
                                            "selected_face":combochanges[0],
                                            "similarity_thresh":similarity_thresh,
                                            "number_of_images":k,
                                            "detector_name":detector_name,"embedder_name":embedder_name})
            data = response.json()
            errors = errors + data["errors"]
            images = images + data["images"]
        elif action == "Clear":
            length=len(current_images)
            index=request.form.get("index",type=int);
            if index is not None and index<length:
                del current_images[index]
                del faces_indices[index]
                del combochanges[index]
                faces_indices.append(0)
                combochanges.append(0)

    session["parameters"] = parameters
    session["current_images"] = current_images
    session["detector_name"] = detector_name
    session["embedder_name"] = embedder_name
    session["selected_faces"] = combochanges
    session["faces_indices"] = faces_indices
    return render_template(
        "search.html",
        images=images,
        embedder_name=embedder_name,
        detector_name=detector_name,
        current=current_images[0] if len(current_images)>0 else None,
        faces_indices=faces_indices[0],
        selected_face=combochanges[0],
        parameters=parameters,
        errors=errors,
        messages=messages,
    )

from flask import Blueprint, render_template, request, session
from modules import AppPaths,upload_from_request,extract_face_selection_from_request
import requests as req

check_family_bp = Blueprint('check_family', __name__)

@check_family_bp.route("/check_family", methods=["GET", "POST"])
def check_family():
    images = []
    messages = []
    errors = []
    #get parmetes values and call the selected action's api
    detector_name = session.get("detector_name","")
    embedder_name = session.get("embedder_name","")
    faces_indices = session.get("faces_indices", [{},{}])
    parameters = session.get("parameters", {})
    current_images = session.get("current_images", [])
    combochanges = session.get("selected_faces", [-2, -2])
    if request.method == "POST":
        similarity_thresh=request.form.get("SimilarityThreshold",default=0.5,type=float);
        parameters['similarity_thresh']=similarity_thresh
        detector_name=request.form.get("detector_name",default="SCRFD10G",type=str);
        embedder_name=request.form.get("embedder_name",default="ResNet100GLint360K",type=str);
        combochanges= extract_face_selection_from_request(request,faces_indices);
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
                    response = req.post(url, data={"image": current_images[index],"detector_name":detector_name,"embedder_name":embedder_name})
                    data = response.json()
                    errors = errors + data["errors"]
                    messages = messages+data["messages"]
                    current_images[index]=data['enhanced_image']
        elif(action=="Check_Family"):
            url = AppPaths.SERVER_URL + "/api/check_family"
            response = req.post(url, data={"images": current_images,
                                            "selected_faces":combochanges,
                                            "similarity_thresh":similarity_thresh,
                                            "detector_name":detector_name,
                                            "embedder_name":embedder_name})
            data = response.json()
            errors = errors + data["errors"]
            messages = messages + data["messages"]
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
    session["selected_faces"] = combochanges
    session["detector_name"] = detector_name
    session["embedder_name"] = embedder_name
    session["faces_indices"] = faces_indices
    return render_template(
        "check_family.html",
        images=images,
        current=current_images,
        embedder_name=embedder_name,
        detector_name=detector_name,
        faces_indices=faces_indices,
        selected_faces=combochanges,
        parameters=parameters,
        errors=errors,
        messages=messages,
    )
    
    

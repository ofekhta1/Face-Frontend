from flask import Blueprint, render_template, request, session
from modules import upload_from_request
import requests as req
from modules import AppPaths
template_matching_bp = Blueprint('template_matching', __name__)

@template_matching_bp.route("/template_matching", methods=["GET", "POST"])
def template_matching():
    messages = []
    errors = []
    box=[]
    embedder_name = session.get("embedder_name", "")
    detector_name = session.get("detector_name", "")
    current_images = session.get("current_template_images", [])
    parameters = session.get("parameters", {})
    

    if request.method == "POST":
        #get the params values
        detector_name=request.form.get("detector_name",default="SCRFD10G",type=str);
        embedder_name=request.form.get("embedder_name",default="ResNet100GLint360K",type=str);
        action = request.form.get("action")
        similarity_thresh=request.form.get("SimilarityThreshold",default=0.5,type=float);
        parameters['similarity_thresh']=similarity_thresh
        if(action=="Upload"):
            upload_from_request(request,current_images,[0,0],detector_name,embedder_name,save_invalid=True)
        elif(action=="Match_Template"):
            if(len(current_images)==0):
                errors.append("Upload a template first!")
            else:
                url = AppPaths.SERVER_URL + "/api/check_template"
                response = req.post(url, data={"template": current_images[0],"similarity_thresh":similarity_thresh})
                data = response.json()
                errors = errors + data["errors"]
                if(len(errors)==0):
                    if(len(current_images)==1):
                        current_images.append(data['image']);
                    else:
                        current_images[1]=data['image']
                    box=data['box'];
                messages = messages + data["messages"]
        #clear the arr if the user click on clear        
        elif action == "Clear":
            current_images = []
	
    session["detector_name"] = detector_name
    session["embedder_name"] = embedder_name
    session["parameters"] = parameters
    session["current_template_images"] = current_images
    return render_template(
        "template_matching.html",
        parameters=parameters,
        box=box,
        current=current_images,
        embedder_name=embedder_name,
        detector_name=detector_name,
        errors=errors,
        messages=messages,
    )

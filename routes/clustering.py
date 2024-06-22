from flask import Blueprint, render_template, request, session
import json

clustering_bp = Blueprint('clustering', __name__)

@clustering_bp.route("/clustering", methods=["GET", "POST"])
def clustering():
    errors = []
    messages = []
    groups = session.get("groups", {})
    detector_name = session.get("detector_name","")
    embedder_name = session.get("embedder_name","")
    parameters = session.get("parameters", {})



    if request.method == "POST":
        detector_name=request.form.get("detector_name",default="SCRFD10G",type=str);
        embedder_name=request.form.get("embedder_name",default="ResNet100GLint360K",type=str);
        try:
            #cluster the images from the jsondata accroding to the selected threshold and group size
            jsonStr = request.form.get("jsonData", "")
            data = json.loads(jsonStr)
            groups=data["groups"]
            parameters['cluster_family'] = data.get("cluster_family", False)
            parameters['similarity_thresh']=data["similarity_thresh"];
            parameters['min_group_size']=data["min_group_size"];

            session["groups"] = groups
        except Exception as e:
            print("failed to display clustering results because:")
            print(e)

        
    session["detector_name"] = detector_name
    session["embedder_name"] = embedder_name
    session["parameters"] = parameters

    return render_template(
        "clustering.html",
        groups=groups,
        embedder_name=embedder_name,
        detector_name=detector_name,
        errors=errors,
        parameters=parameters,
        messages=messages,
    )

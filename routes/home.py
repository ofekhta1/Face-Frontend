from flask import Blueprint, render_template, request, session
from modules import AppPaths,upload_from_request,extract_face_selection_from_request
import requests as req

home_bp = Blueprint('home', __name__)

@home_bp.route("/", methods=["GET", "POST"])
def home():
    messages = []
    errors = []
    action = request.form.get("action")
    embedder_name = session.get("embedder_name", "")
    detector_name = session.get("detector_name", "")
    faces_indices = session.get("faces_indices", [{},{}])
    current_images = session.get("current_images", [])
    parameters = session.get("parameters", {})
    combochanges = session.get("selected_faces", [-2, -2])

    if request.method == "POST":
        detector_name=request.form.get("detector_name",default="SCRFD10G",type=str);
        embedder_name=request.form.get("embedder_name",default="ResNet100GLint360K",type=str);
        similarity_thresh=request.form.get("SimilarityThreshold",default=0.5,type=float);
        parameters['similarity_thresh']=similarity_thresh
        combochanges= extract_face_selection_from_request(request,faces_indices);
        if action == "Upload":
            temp_err=upload_from_request(request,current_images,faces_indices,detector_name,embedder_name)
            errors=errors+temp_err
        elif action in ["Detect", "Align"]:
            if action == "Align":
                url = AppPaths.SERVER_URL + "/api/align"

            elif action == "Detect":
                url = AppPaths.SERVER_URL + "/api/detect"
            if len(current_images) > 0:
                response = req.post(url, data={"images": current_images,"detector_name":detector_name})
                data = response.json()
                uploaded_images = uploaded_images + data["images"]
                errors = errors + data["errors"]
                # current_images=data['images']
                messages = messages + data["messages"]
                
                for i in range(len(data['faces_indices'])):
                    faces_indices[i]=data['faces_indices'][i]
            else:
                errors.append("No images uploaded!")
        elif action == "Clear":
            length=len(current_images)
            index=request.form.get("index",type=int);
            if index is not None and index<length:
                del current_images[index]
                del faces_indices[index]
                del combochanges[index]
                faces_indices.append({})
                combochanges.append(0)

                uploaded_images = []
            

        elif action == "Compare":
            url = AppPaths.SERVER_URL + "/api/compare"
            response = req.post(
                url, data={"images": current_images,"detector_name":detector_name,
                "embedder_name":embedder_name, "selected_faces": combochanges,"similarity_thresh":similarity_thresh}
            )
            data = response.json()
            errors = errors + data["errors"]
            messages = messages + data["messages"]

        elif action == "Check":
            url = AppPaths.SERVER_URL + "/api/check"
            if len(current_images) > 0:
        
            
                response = req.post(
                    url,
                    data={"image": current_images[0],
                            "detector_name":detector_name,
                            "embedder_name":embedder_name,
                            "selected_face": combochanges[0],
                            "similarity_thresh":similarity_thresh}
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
                    faces_indices[1] = data["detector_indices"]
                else:
                    if len(current_images) == 2:
                        del current_images[1]
                    combochanges[1]=-2
                    faces_indices[1]={}

            else:
                
                errors.append("No images uploaded!")
        
        elif action == "improve":
            url = AppPaths.SERVER_URL + "/api/improve"
            length=len(current_images)
            index=request.form.get("index",type=int);
            if index is not None and index<length:
                if(current_images[index].startswith('enhanced_')):
                    current_images[index]=current_images[index].replace("enhanced_","")
                else:
                    response = req.post(url, data={"image": current_images[index],"detector_name":detector_name})
                    data = response.json()
                    errors = errors + data["errors"]
                    messages = messages+data["messages"]
                    current_images[index]=data['enhanced_image']


        
        session["parameters"] = parameters
        session["detector_name"] = detector_name
        session["embedder_name"] = embedder_name
        session["current_images"] = current_images
        session["selected_faces"] = combochanges
        session["faces_indices"] = faces_indices


    return render_template(
        "image.html",
        embedder_name=embedder_name,
        detector_name=detector_name,
        parameters=parameters,
        current=current_images,
        faces_indices=faces_indices,
        selected_faces=combochanges,
        errors=errors,
        messages=messages,
    )
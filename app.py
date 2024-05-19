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
			url = SERVER_URL + "/api/improve"
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
			url = SERVER_URL + "/api/check_many"
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

@app.route("/clustering", methods=["GET", "POST"])
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

@app.route("/check_family", methods=["GET", "POST"])
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
			url = SERVER_URL + "/api/improve"
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
			url = SERVER_URL + "/api/check_family"
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
@app.route("/upload",methods=["GET","POST"])
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
@app.route("/template_matching", methods=["GET", "POST"])
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
                url = SERVER_URL + "/api/check_template"
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

@app.route("/", methods=["GET", "POST"])
def index():
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
				url = SERVER_URL + "/api/align"

			elif action == "Detect":
				url = SERVER_URL + "/api/detect"
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
			url = SERVER_URL + "/api/compare"
			response = req.post(
				url, data={"images": current_images,"detector_name":detector_name,
			   "embedder_name":embedder_name, "selected_faces": combochanges,"similarity_thresh":similarity_thresh}
			)
			data = response.json()
			errors = errors + data["errors"]
			messages = messages + data["messages"]

		elif action == "Check":
			url = SERVER_URL + "/api/check"
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
			url = SERVER_URL + "/api/improve"
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


if __name__ == "__main__":
	try:
		app.run(debug=True, port=5000)
	except Exception as e:
		print(f"Error: {e}")

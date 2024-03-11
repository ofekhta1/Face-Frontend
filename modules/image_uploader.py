import tempfile
from .app_paths import AppPaths
import requests as req
import os

def saveTempFiles(temp_dir, files):
    saved_files = {}
    for key, file in files.items():
        if file.filename != "":
            file_path = os.path.join(temp_dir,file.filename)
            file.save(file_path)
            saved_files[key] = open(file_path, "rb")
    return saved_files


def upload_from_request(request,current_images,faces_length,save_invalid=False):
    errors=[]
    with tempfile.TemporaryDirectory() as temp_dir:
        saved_files = saveTempFiles(temp_dir, request.files)
        if len(saved_files) > 0:
            response = req.post(AppPaths.SERVER_URL + "/api/upload",data={"save_invalid":save_invalid}, files=saved_files)
            data = response.json()
            errors = errors + data["errors"]
            if len(data["images"]) > 0 or (save_invalid and len(data["invalid_images"])>0):
                max_size = 2
                initial = len(current_images) - 1
                uploaded = data['images']+data['invalid_images'] if save_invalid else data['images']
                for i in range(len(uploaded)):
                    current_index = (initial + 1 + i) % max_size
                    if current_index == initial + 1:
                        current_images.append(uploaded[i])
                    else:
                        current_images[current_index] = uploaded[i]
                    faces_length[current_index] = data["faces_length"][i]


            for saved in saved_files.values():
                saved.close();
        else:
            errors.append(
                "Saving Images failed,make sure you uploaded 2 valid images"
            )
        return errors;
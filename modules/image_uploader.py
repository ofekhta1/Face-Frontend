import tempfile
from .app_paths import AppPaths
import requests as req
from flask import Request
import os
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse

def saveTempFiles(temp_dir, files):
    saved_files = {}
    for key, file in files.items():
        if file.filename != "":
            file_path = os.path.join(temp_dir,file.filename)
            file.save(file_path)
            saved_files[key] = open(file_path, "rb")
    return saved_files

def save_image_from_url(url, directory):
    response = req.get(url, stream=True)
    if response.status_code == 200:
        # Extract the filename from the URL
        filename = os.path.join(directory, os.path.basename(url))
        with open(filename, "w+b") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
            return filename;

def saveZipTempFiles(temp_dir,zip_file:zipfile.ZipFile):
    saved_files = {}

    files = zip_file.namelist()
    # Filter names to only include the filetype that you want:
    ALLOWED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp"
    }
    file_names = [(file) for file in files if os.path.splitext(file)[1].lower() in ALLOWED_EXTENSIONS]
    for file in file_names:
        file_path = os.path.join(temp_dir,file)
        result =zip_file.extract(file,temp_dir)
        saved_files[file] = open(file_path, "rb")
    return saved_files

def upload_from_zip(zip_file,save_invalid=False):
    zipfile_ob = zipfile.ZipFile(zip_file)
    errors=[]
    messages=[]
    with tempfile.TemporaryDirectory() as temp_dir:
        saved_files=saveZipTempFiles(temp_dir,zipfile_ob);  
        if len(saved_files) > 0:
            response = req.post(AppPaths.SERVER_URL + "/api/upload",data={"save_invalid":save_invalid}, files=saved_files)
            data = response.json()
            errors = errors + data["errors"]
            if len(data["images"]) > 0 or (save_invalid and len(data["invalid_images"])>0):
                uploaded = data['images']+data['invalid_images'] if save_invalid else data['images']
                messages.append(f"{len(uploaded)} images were saved") 
            messages.append(f"no faces detected in {data['invalid_images']}")
        else:
            errors.append(
                "Saving Images failed"
            )
        for saved in saved_files.values():
                saved.close();
        return messages,errors;      


def upload_from_url(website_url):
    with tempfile.TemporaryDirectory() as temp_dir:
        downloaded_images={};
        files=[]
        errors=[]
        messages=[]
        response = req.get(website_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            img_tags = soup.find_all("img")
            i=0;
            for img in img_tags:
                i=i+1;
                img_url = img.get("src")
                img_url = urljoin(website_url, urlparse(img_url).path)
                fileName=save_image_from_url(img_url, temp_dir)
                if fileName:
                    files.append(fileName)
            downloaded_images= {f"image{i}": open(files[i],"rb") for i in range(len(files))}
           
            # messages.append("Images downloaded and saved successfully.")
            if len(downloaded_images) > 0:
                response = req.post(AppPaths.SERVER_URL + "/api/upload", files=downloaded_images)
                data = response.json()
                for image in downloaded_images.values():
                    image.close();
                errors = errors + data["errors"]
    
        else:
            print(f"Failed to fetch the website. Status code: {response.status_code}")
        return messages,errors;
def upload_from_request(request:Request,current_images:list[str],faces_length:list[dict[str,list[int]]],
                        detector_name:str,embedder_name:str,save_invalid=False):
    errors=[]
    with tempfile.TemporaryDirectory() as temp_dir:
        saved_files = saveTempFiles(temp_dir, request.files)
        if len(saved_files) > 0:
            response = req.post(AppPaths.SERVER_URL + "/api/upload",data={"save_invalid":save_invalid,
                                                                          "detector_name":detector_name,
                                                                          "embedder_name":embedder_name}
                                                                          , files=saved_files)
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
                    faces_length[current_index] = data["detector_indices"][i]


            for saved in saved_files.values():
                saved.close();
        else:
            errors.append(
                "Saving Images failed,make sure you uploaded 2 valid images"
            )
        return errors;
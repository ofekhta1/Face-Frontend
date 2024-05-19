from flask import Request
import json
def extract_face_selection_from_request(request:Request,faces_indices:list[dict[str,list[int]]]):

    face_num_1 = request.form.get("face_num1",type=int,default=-2)
    face_num_2 = request.form.get("face_num2",type=int,default=-2)
    combochanges = [face_num_1, face_num_2]
    jsonStr = request.form.get("jsonData")
    if(jsonStr):
        data = json.loads(jsonStr)
        if("old_detector" in data and "new_detector" in data):
            new=data["new_detector"]
            old=data["old_detector"]
            if(old!=new):
                for i in range(2):
                    if(old in faces_indices[i] and new in faces_indices[i]):
                        if(combochanges[i]>-1):
                            old_face=faces_indices[i][old][combochanges[i]]
                            combochanges[i]=faces_indices[i][new].index(old_face)
    return combochanges;
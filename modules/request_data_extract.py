def extract_face_selection_from_request(request):
    face_num_1 = request.form.get("face_num1")
    face_num_2 = request.form.get("face_num2")
    face_num_1 = -2 if (face_num_1 is None or  face_num_1 == "")   else int(face_num_1)
    face_num_2 = -2 if (face_num_2 is None or  face_num_2 == "") else int(face_num_2)
    combochanges = [face_num_1, face_num_2]
    return combochanges;
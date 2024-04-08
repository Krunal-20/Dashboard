import cv2
import os
import numpy as np
from ultralytics import YOLO
from werkzeug.utils import secure_filename
from base import app
from base.com.vo.detection_vo import FileVO, PotholeVO, CattleVO
from base.com.dao.detection_dao import FileDAO, PotholeDAO, CattleDAO
import torch
import cvzone


def validate_user(username, password):
    if username == 'admin' and password == 'admin@21189':
        return True 
    return False


def pothole_count_save(pothole_file_id, frame_id, counts):
    pothole_vo = PotholeVO()
    pothole_vo.pothole_file_id = pothole_file_id
    pothole_vo.frame_id = frame_id
    pothole_vo.pothole_counts = counts
    pothole_dao = PotholeDAO()
    pothole_dao.insert_data(pothole_vo)
    
    
def cattle_count_save(cattle_file_id, frame_id, counts):
    cattle_vo = CattleVO()
    cattle_vo.cattle_file_id = cattle_file_id
    cattle_vo.frame_id = frame_id
    cattle_vo.cattle_counts = counts
    cattle_dao = CattleDAO()
    cattle_dao.insert_data(cattle_vo)
        
    
def perform_inference(uploaded_file, model_name):
    try:
        file_vo = FileVO()
        file_dao = FileDAO()
        
        infer_file = secure_filename(uploaded_file.filename)
        
        if file_dao.check_file_exists(infer_file):
            name, ext = os.path.splitext(infer_file)
            index = 1
            while True:
                new_filename = f"{name} ({index}){ext}"
                if not file_dao.check_file_exists(new_filename):
                    infer_file = new_filename
                    break 
                index += 1
        
        # model loading
        model_path=f'base/static/models/{model_name}.pt'
        model = YOLO(model_path)
        
        # saving filename in database
        file_vo.file_name = infer_file
        file_dao.insert_file(file_vo)
        
        save_inputs = os.path.join(app.config['UPLOAD_FOLDER'], infer_file)
        uploaded_file.save(save_inputs)
        save_outputs = os.path.join(app.config['OUTPUT_FOLDER'], infer_file)
        
        # select classes according to the model 
        if model_name == 'cattle':
            classes = [15, 16, 17, 18, 19, 20, 21, 22, 23]
        elif model_name == 'pothole':
            classes = [1]
        else:
            classes = [0]
            
        device = 0 if torch.cuda.is_available() else 'cpu'
            
        # if uploaded file is an image
        if infer_file.endswith(('.jpg', '.png', '.jpeg')):
            image = cv2.imread(save_inputs)
            image = cv2.resize(image, (720, 480))
            results = model.predict(image, classes=classes, device=device)
            is_garbage = False
            if results[0].boxes is not None:
                boxes = results[0].boxes.xyxy.cpu()
                for box in boxes:
                    x1, y1, x2, y2 = box
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) 
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 100, 250), 2)
            else:
                boxes = results[0].obb.xyxyxyxy.cpu()
                for box in boxes:
                    points = np.array(box, np.int32)
                    points = points.reshape((-1,1,2))
                    cv2.polylines(image, [points], isClosed=True, color=(0, 100, 250), thickness=2)
            counts = len(results[0])
            frame_id = 1
            file_id = file_dao.get_file_id(infer_file)
            if model_name == 'pothole':
                pothole_count_save(file_id, frame_id, counts)
                cvzone.putTextRect(image, f'Pothole Counts: {counts}', [30, 40], scale=1, thickness=2, colorR=(0,0,0), colorT=(0,100,250),border=2, colorB=(0,100,250),font=cv2.FONT_HERSHEY_SIMPLEX)
                
            elif model_name == 'cattle':
                cattle_count_save(file_id, frame_id, counts)
                cvzone.putTextRect(image, f'Cattle Counts: {counts}', [30, 40], scale=1, thickness=2, colorR=(0,0,0), colorT=(0,100,250),border=2, colorB=(0,100,250),font=cv2.FONT_HERSHEY_SIMPLEX)
                
            else:
                if counts > 0:
                    is_garbage = True
                cvzone.putTextRect(image, f'Is Garbage: {is_garbage}', [30, 40], scale=1, thickness=2, colorR=(0,0,0), colorT=(0,100,250),border=2, colorB=(0,100,250),font=cv2.FONT_HERSHEY_SIMPLEX)

            cv2.imwrite(save_outputs, image)
            return {'file_id': file_id, 'model_name': model_name}
        
        elif infer_file.endswith(('.mp4', '.mov', '.avi', 'mkv')):
            cap = cv2.VideoCapture(save_inputs)
            # Get video properties (fps, width, height)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Define the codec and create VideoWriter object
            codec = int(cap.get(cv2.CAP_PROP_FOURCC))
            fourcc = cv2.VideoWriter_fourcc(*chr(codec & 0xFF), chr((codec >> 8) & 0xFF), chr((codec >> 16) & 0xFF), chr((codec >> 24) & 0xFF))
            out = cv2.VideoWriter(save_outputs, fourcc, 1, (width, height))
            
            # Calculate frame interval to achieve desired frame rate (1 frame per second)
            actual_fps = int(fps)  # Adjust if needed
            frame_number = 0
            frame_id = -1
            file_id = file_dao.get_file_id(infer_file)
            
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    frame_number += 1
                    
                    if frame_number % actual_fps == 0:
                        frame_id += 1
                        results = model.predict(frame, classes=classes, device=device)
                        counts = len(results[0])
                        is_garbage = False

                        if results[0].boxes is not None:
                            boxes = results[0].boxes.xyxy.cpu()
                            for box in boxes:
                                x1, y1, x2, y2 = box
                                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) 
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 100, 250), 2)
                        else:
                            boxes = results[0].obb.xyxyxyxy.cpu()
                            for box in boxes:
                                points = np.array(box, np.int32)
                                points = points.reshape((-1,1,2))
                                cv2.polylines(frame, [points], isClosed=True, color=(0, 100, 250), thickness=2)
                        if model_name == 'pothole':
                            pothole_count_save(file_id, frame_id, counts)
                            cvzone.putTextRect(frame, f'Pothole Counts: {counts}', [30, 40], scale=1, thickness=2, colorR=(0,0,0), colorT=(0,100,250),border=2, colorB=(0,100,250),font=cv2.FONT_HERSHEY_SIMPLEX)
                            
                        elif model_name == 'cattle':
                            cattle_count_save(file_id, frame_id, counts)
                            cvzone.putTextRect(frame, f'Cattle Counts: {counts}', [30, 40], scale=1, thickness=2, colorR=(0,0,0), colorT=(0,100,250),border=2, colorB=(0,100,250),font=cv2.FONT_HERSHEY_SIMPLEX)
                            
                        else:
                            if counts > 0:
                                is_garbage = True
                            cvzone.putTextRect(frame, f'Is Garbage: {is_garbage}', [30, 40], scale=1, thickness=2, colorR=(0,0,0), colorT=(0,100,250),border=2, colorB=(0,100,250),font=cv2.FONT_HERSHEY_SIMPLEX)
                            
                            # cvzone.putTextRect(frame, f'Garbage Counts: {counts}', [30, 40], scale=1, thickness=2, colorR=(0,0,0), colorT=(0,100,250),border=2, colorB=(0,100,250),font=cv2.FONT_HERSHEY_SIMPLEX)
                            
                        out.write(frame)
                            
                    else:
                        continue
                else:
                    break    
                
            cap.release()
            out.release()
            return {'file_id': file_id, 'model_name': model_name}
        
        else:
            raise ValueError('Unsupported file.')
          
    except Exception as e:
        print(f'An error occured: {e}')
        
        
def get_file_data(file_id, model_name):
    try:
        if model_name == 'pothole':
            pothole_dao = PotholeDAO()
            pothole_vo_list = pothole_dao.get_file_data(file_id)
            return pothole_vo_list
        
        elif model_name == 'cattle':
            cattle_dao = CattleDAO()
            cattle_vo_list = cattle_dao.get_file_data(file_id)
            return cattle_vo_list
        
        elif model_name == 'garbage':
            file_dao = FileDAO()
            filename = file_dao.get_filename(file_id)
            return filename
        
    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
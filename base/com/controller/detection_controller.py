from flask import redirect, render_template, flash, request, session, url_for
from base import app
import os
from base.com.service_layer.detection_service import PerformDetection
from base.com.vo.detection_vo import CattleVO, PotholeVO, FileVO
from base.com.dao.detection_dao import CattleDAO, PotholeDAO, FileDAO
from werkzeug.utils import secure_filename


@app.route('/', methods=['GET', 'POST'])
def load_login_page():
    try:
        return render_template("loginPage.html")
    except Exception as e:
        return render_template('errorPage.html', error=e)
    
    
@app.route('/login', methods=['GET', 'POST'])
def validate_login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password') 
            if username == 'admin' and password == 'admin@21189':
                session['logged_in'] = True
                return redirect('/dashboard')
            flash('Invalid Credentials')
            return redirect(url_for('load_login_page'))
    except Exception as e:
        return render_template('errorPage.html', error=e)
    

@app.route('/dashboard')
def load_dashboard_page():
    try:    
        if session.get('logged_in', False):    
            return render_template('dashboardPage.html')
        flash("Login Required..!!")
        return redirect('/')

    except Exception as e:
        return render_template('errorPage.html', error=e)
    
        
@app.route('/upload')
def load_upload_page():
    try:    
        if session.get('logged_in', False):    
            return render_template('uploadPage.html')
        flash("Login Required..!!")
        return redirect('/')

    except Exception as e:
        return render_template('errorPage.html', error=e)
             
           
@app.route('/upload-file', methods=['POST'])
def upload_file():
    try:
        selected_model = request.form.get('model')
        uploaded_file = request.files.get('uploadedFile')

        file_vo = FileVO()
        file_dao = FileDAO()
        cattle_vo = CattleVO()
        cattle_dao = CattleDAO()
        pothole_vo = PotholeVO()
        pothole_dao = PotholeDAO()

        detection_service = PerformDetection(selected_model)

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

        file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], infer_file)
        file_output_path = os.path.join(app.config['OUTPUT_FOLDER'], infer_file)
        uploaded_file.save(file_save_path)

        file_type = None
        detection_service_output = None
        if infer_file.endswith(('.jpg', '.png', '.jpeg')):
            file_type = 'image'
            detection_service_output \
                = detection_service.image_detection_service(file_save_path,
                                                            file_output_path)
        elif infer_file.endswith(('.mp4', '.mov', '.avi', 'mkv')):
            file_type = 'video'
            detection_service_output \
                = detection_service.video_detection_service(file_save_path,
                                                            file_output_path)

        file_vo.file_save_path = app.config['UPLOAD_FOLDER']
        file_vo.file_output_path = app.config['OUTPUT_FOLDER']
        file_vo.file_name = infer_file
        file_vo.file_type = file_type
        file_vo.model = selected_model

        file_dao.insert_file(file_vo)

        file_id = file_dao.get_file_id(infer_file)

        if file_type == 'image':
            if selected_model == 'cattle':
                cattle_vo.cattle_counts = detection_service_output.get(
                    'counts')
                cattle_vo.cattle_file_id = file_id
                cattle_dao.insert_data(cattle_vo)
            elif selected_model == 'pothole':
                pothole_vo.pothole_counts = detection_service_output.get(
                    'counts')
                pothole_vo.pothole_file_id = file_id
                pothole_dao.insert_data(pothole_vo)

        if file_type == 'video':
            counts_list = detection_service_output.get('counts')

            if selected_model == 'cattle':
                for idx, count in enumerate(counts_list):
                    cattle_vo = CattleVO()
                    cattle_vo.cattle_file_id = file_id
                    cattle_vo.frame_id = idx
                    cattle_vo.cattle_counts = count
                    cattle_dao.insert_data(cattle_vo)
            elif selected_model == 'pothole':
                for idx, count in enumerate(counts_list):
                    pothole_vo = PotholeVO()
                    pothole_vo.pothole_file_id = file_i
                    pothole_vo.frame_id = idx
                    pothole_vo.cattle_counts = count
                    pothole_dao.insert_data(pothole_vo)

        return redirect(f'/results?file_id={file_id}&model_name={selected_model}')
    except Exception as e:
        return render_template('errorPage.html', error=e)
    
    
@app.route('/results')
def load_results():
    try:
        if session.get('logged_in', False):
            file_id = request.args.get('file_id')
            model_name = request.args.get('model_name')
            vo_list = None
            if model_name == 'cattle':
                cattle_dao = CattleDAO()
                vo_list = cattle_dao.get_file_data(file_id)
            elif model_name == 'pothole':
                pothole_dao = PotholeDAO()
                vo_list = pothole_dao.get_file_data(file_id)
            else:
                garbage_detail = FileDAO()
                vo_list = garbage_detail.get_file_data(file_id)
            return render_template('resultsPage.html', vo_list=vo_list,
                                   model_name=model_name)
        flash("Login Required..!!")
        return redirect('/')
    except Exception as e:
        return render_template('errorPage.html', error=e)
    
    
@app.route('/view-analytics')
def load_analytics_page():
    try:
        if session.get('logged_in', False):
            file_id = request.args.get('file_id')
            model_name = request.args.get('model_name')
            vo_list = None
            if model_name == 'cattle':
                cattle_dao = CattleDAO()
                vo_list = cattle_dao.get_file_data(file_id)
            elif model_name == 'pothole':
                pothole_dao = PotholeDAO()
                vo_list = pothole_dao.get_file_data(file_id)
            return render_template('analyticsPage.html', vo_list=vo_list, model_name=model_name)
        flash("Login Required..!!")
        return redirect('/')
    except Exception as e:
        return render_template('errorPage.html', error=e)
           
        
@app.route('/logout')
def logout():
    try:
        if session.get('logged_in', False):
            session.clear()
            return redirect('/')
        flash("Login Required..!!")
        return redirect('/')

    except Exception as e:
        return render_template('errorPage.html', error=e)
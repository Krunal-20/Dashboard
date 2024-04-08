from flask import redirect, render_template, flash, request, session, url_for
from base import app
import os
from base.com.service_layer.detection_service import perform_inference, get_file_data, validate_user


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
            is_auth = validate_user(username, password)
            if is_auth:
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
        results = perform_inference(uploaded_file, selected_model)
        file_id = results.get('file_id')
        model_name = results.get('model_name')
        return redirect(f'/results?file_id={file_id}&model_name={model_name}')
    except Exception as e:
        return render_template('errorPage.html', error=e)
    
    
@app.route('/results')
def load_results():
    try:
        if session.get('logged_in', False):
            file_id = request.args.get('file_id')
            model_name = request.args.get('model_name')
            vo_list = get_file_data(file_id, model_name)
            return render_template('resultsPage.html', model_name=model_name, vo_list=vo_list)
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
            vo_list = get_file_data(file_id, model_name)
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
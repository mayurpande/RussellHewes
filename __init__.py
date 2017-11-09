from flask import Flask, render_template, flash, url_for, request, redirect, jsonify
from flask_mail import Mail,Message
from db import connection
#flask mail config file
from config_mail import username,pw
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = '/var/www/html/RussellHewes/RussellHewes/static/img/'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'gif','png'])

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.config.update(
  MAIL_SERVER='auth.smtp.1and1.co.uk',
  MAIL_PORT = 587,
  MAIL_USERNAME = username,
  MAIL_PASSWORD = pw,
  MAIL_USE_TLS = True,
  MAIL_USE_SSL = False
)

mail = Mail(app)

@app.route('/',methods=['GET','POST'])
def main():

  if request.method == 'POST':
    name = request.form['username']
    email = request.form['email']
    message = request.form['text-content']
    if name and email:

      msg = Message(subject='New Enquiry from first page',sender='enquiries@russellhewes.co.uk', recipients = ['enquiries@russellhewes.co.uk','chanelle@russellhewes.co.uk'])
      msg.body = 'Hello Russell you cunt!\n\nSomeone has sent you an enquiry probably best to mail them back.\n\nTheir name is;\n\n' + name.title() + '\n\nTheir email is;\n\n' + email + '\n\nTheir message said this;\n\n' + message
      mail.send(msg)

      msg = Message(subject='Russell Hewes - Enquiry',sender='enquiries@russellhewes.co.uk', recipients = [email])
      msg.body = 'Dear ' + name.title() + ',\n\nThank you for your enquiry.\n\nOne of our members of staff will be in touch shortly.\n\nKind Regards,\n\nRussell Hewes'
      mail.send(msg)
      flash('Thank you for your enquiry, someone from our team will be in contact with you very shortly','success')
      return redirect(url_for('main'))
    else:
      flash('You have not filled in all mandatory fields, please try again','danger')
      return redirect(url_for('main',_anchor='contact'))
  else:
    #use pymysql cursor
    with connection.cursor() as cursor:
      text_content_query = "SELECT * FROM `home_page`"
      cursor.execute(text_content_query,(),)
      result = cursor.fetchall()


    return render_template('index.html',data=result)


@app.route('/<type>',methods=['GET','POST'])
def job(type):

  if request.method == 'POST':
    email = request.form['email']
    name = request.form['username']
    message = request.form['text-content']
    subject_type = request.form['email-type']
    if name and email:
      subject = 'New enqiury about ' + subject_type
      msg = Message(subject=subject,sender='enquiries@russellhewes.co.uk', recipients = ['enquiries@russellhewes.co.uk','chanelle@russellhewes.co.uk'])
      msg.body = 'Hello Russell you cunt!\n\nSomeone has sent you an enquiry about ' + subject_type + ' probably best to mail them back.\n\nTheir name is;\n\n' + name.title() + '\n\nTheir email is;\n\n' + email + '\n\nTheir message said this;\n\n' + message
      mail.send(msg)
      subject = 'Russell Hewes - ' + subject_type.title()
      msg = Message(subject=subject,sender='enquiries@russellhewes.co.uk', recipients = [email])
      msg.body = 'Dear ' + name.title() + ',\n\nThank you for your enquiry regarding our ' + subject_type + ' team.\n\nOne of our members of staff will be in touch shortly.\n\nKind Regards,\n\nRussell Hewes'
      mail.send(msg)
      flash('Thank you for your enquiry, someone from our ' + subject_type + ' team will be in contact with you very shortly','success')

    else:
      flash('You have not filled in all mandatory fields, please try again','danger')

    return redirect(url_for('job',type=subject_type))
  else:
    #use pymysql cursor
    with connection.cursor() as cursor:
      cursor.execute("SELECT * FROM {0}".format(type))
      result = cursor.fetchall()
      print(result)

      cursor.execute("SELECT brief FROM {0}_info".format(type))
      #INNER JOIN {1} ON {2}.id = {3}_info.ref_id".format(type,type,type,type))
      rows = cursor.fetchall()

      cursor.execute("SELECT img_name FROM {0}_back".format(type))
      title_img = cursor.fetchall()
      title = None
      for x in title_img:
        title = x['img_name']

  return render_template('content.html',data=result,brief=rows,type=type,title=title)



@app.route('/home-images')
def home_images():
    with connection.cursor() as cursor:

      img_name_query = "SELECT * FROM `home_page_img`"
      cursor.execute(img_name_query,(),)
      picture_rows = cursor.fetchall()

    return jsonify(picture_rows)

@app.route('/admin')
def admin():

  return render_template('admin.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/admin-home-img',methods=['GET','POST'])
def admin_home_img():


    if request.method == 'POST':

        caption = request.form['caption']


        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part','danger')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file','danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            with connection.cursor() as cursor:

                 upload_img_name_query = "INSERT INTO home_page_img (img_name,img_caption) VALUES (%s,%s)"
                 cursor.execute(upload_img_name_query,(filename,caption),)
                 connection.commit()
                 flash('New image/text uploaded','success')
                 return redirect(request.url)
    return render_template('admin-home.html')

@app.route('/admin-home-delete',methods=['GET','POST'])
def admin_home_delete():

    if request.method == 'POST':
        check_boxes = request.form.getlist('check')


        try:
            with connection.cursor() as cursor:
                for x in check_boxes:
                    delete_query = "DELETE FROM home_page_img WHERE id = %s"
                    cursor.execute(delete_query,(x),)
                    connection.commit()
            flash('You have deleted item(s)', 'success')
            return redirect(url_for('admin_home_delete'))
        except Exception as e:
            flash('You have not deleted item','danger')
            return redirect(url_for('admin_home_delete'))
    else:
        with connection.cursor() as cursor:
            select_home_img = 'SELECT * FROM home_page_img'
            cursor.execute(select_home_img,(),)
            rows = cursor.fetchall()
            return render_template('admin-home-delete.html',data=rows)


@app.route('/admin-home-update',methods=['GET','POST'])
def admin_home_update():

    if request.method == 'POST':

        id = request.form['id']
        caption = request.form['caption']
        try:

            if 'file' not in request.files:
                 flash('No file part','danger')
                 return redirect(request.url)

            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file','danger')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


                with connection.cursor() as cursor:

                     update_img_name_query = "UPDATE home_page_img set img_name = %s, img_caption = %s WHERE id = %s"
                     cursor.execute(update_img_name_query,(filename,caption,id),)
                     connection.commit()
                     flash('You have updated successfully','success')
                     return redirect(url_for('admin_home_update'))
        except Exception as e:
            print(str(e))
            flash('You  have not updated successfully','danger')
            return redirect(url_for('admin_home_update'))

    else:
        with connection.cursor() as cursor:
            select_home_img = 'SELECT * FROM home_page_img'
            cursor.execute(select_home_img,(),)
            rows = cursor.fetchall()
            #select home_page table data
            select_home_query = "SELECT * FROM home_page"
            cursor.execute(select_home_query,(),)
            results = cursor.fetchall()

            return render_template('admin-home-update.html',data=rows,result=results)

@app.route('/admin-home-text-update',methods=['POST'])
def admin_home_text_update():
    caption = request.form['caption']
    try:
        with connection.cursor() as cursor:
            update_home_page_text_query = "UPDATE home_page SET content = %s WHERE id = %s"
            cursor.execute(update_home_page_text_query,(caption,1))
            flash('Home page text updated','success')
            return redirect(url_for('admin_home_update'))
    except Exception as e:
        print()
        print(str(e))
        print()
        flash('Home page text not updated','danger')
        return redirect(url_for('admin_home_update'))

@app.route('/admin-project-add',methods=['GET','POST'])
def admin_project_add():
    if request.method == 'POST':
        caption = request.form['caption']
        project = request.form['optradio']
        try:

            if project:
                if 'file' not in request.files:
                     flash('No file part','danger')
                     return redirect(request.url)

                file = request.files['file']
                # if user does not select file, browser also
                # submit a empty part without filename
                if file.filename == '':
                    flash('No selected file','danger')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


                    with connection.cursor() as cursor:

                        if caption:

                             insert_into_img_query = "INSERT INTO {0} (img_name,img_text) VALUES (%s,%s)".format(project)
                             cursor.execute(insert_into_img_query,(filename,caption),)
                             connection.commit()
                             flash('You have added img name/caption to ' + project + ' successfully','success')
                        else:
                             insert_into_img_query = "INSERT INTO {0} (img_name) VALUES (%s)".format(project)
                             cursor.execute(insert_into_img_query,(filename),)
                             connection.commit()
                             flash('You have added img name to ' + project + ' successfully','success')

                return redirect(url_for('admin_project_add'))
            else:
                flash('You have not selected type','danger')
                return redirect(url_for('admin_project_add'))
        except Exception as e:
            print(str(e))
            flash('You  have not updated successfully','danger')
            return redirect(url_for('admin_project_add'))
    else:
        return render_template('admin-projects-add.html')



@app.route('/admin-project-gallery',methods=['GET','POST'])
def admin_project_gallery_update():
    if request.method == 'POST':
        project = request.form['optradio']
        action = request.form['action']
        if 'update' in action:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM {0}".format(project))
                rows = cursor.fetchall()
                return render_template('admin-projects-update-gallery-post.html',data=rows,project = project)
        elif 'delete' in action:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM {0}".format(project))
                rows = cursor.fetchall()
                return render_template('admin-projects-delete-gallery-post.html',data=rows,project = project)
        else:
            with connection.cursor() as cursor:
                #select from <project_name>_info table
                cursor.execute("SELECT * FROM {0}_info".format(project))
                rows = cursor.fetchall()
                #select from <project_name>_back table
                cursor.execute("SELECT * FROM {0}_back".format(project))
                results = cursor.fetchall()
                return render_template('admin-projects-update-content-post.html',data=rows,project = project, result=results)

    else:
        return render_template('admin-projects-gallery-update.html')


@app.route('/admin-projects-delete-gallery-post',methods=['POST'])
def admin_project_delete_gallery_post():

    check_boxes = request.form.getlist('check')
    project = request.form['project']


    try:
        with connection.cursor() as cursor:
            for x in check_boxes:
                delete_query = "DELETE FROM {0} WHERE id = %s".format(project)
                cursor.execute(delete_query,(x),)
                connection.commit()
        flash('You have deleted item(s)', 'success')
        return redirect(url_for('admin_project_gallery_update'))
    except Exception as e:
        print()
        print(str(e))
        print()
        flash('You have not deleted item','danger')
        return redirect(url_for('admin_project_gallery_update'))




@app.route('/admin-projects-gallery-update-post',methods=['POST'])
def admin_project_gallery_update_post():
    id = request.form['id']
    project = request.form['project']
    caption = request.form['caption']

    try:

        if 'file' not in request.files:
             flash('No file part','danger')
             return redirect(request.url)

        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file','danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


            with connection.cursor() as cursor:
                if caption:
                     update_img_name_query = "UPDATE {0} set img_name = %s, img_text = %s WHERE id = %s".format(project)
                     cursor.execute(update_img_name_query,(filename,caption,id),)
                     connection.commit()
                     flash('You have updated successfully','success')
                else:
                     update_img_name_query = "UPDATE {0} set img_name = %s WHERE id = %s".format(project)
                     cursor.execute(update_img_name_query,(filename,id),)
                     connection.commit()
                     flash('You have updated ' + project + ' gallery successfully' ,'success')

                return redirect(url_for('admin_project_gallery_update'))
    except Exception as e:
        print(str(e))
        flash('You  have not updated ' + project + ' gallery successfully','danger')
        return redirect(url_for('admin_project_gallery_update'))


    return redirect(url_for('admin_project_gallery_update'))






if __name__ == "__main__":
    app.run(debug=True)

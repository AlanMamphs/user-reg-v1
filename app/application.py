from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, send_from_directory
from models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/media')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


print(APP_ROOT)
print(UPLOAD_FOLDER)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
login_manager.init_app(app)




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route("/")
@login_required
def index():
	return render_template("index.html", name=current_user.name)


@app.route("/register", methods=["POST", "GET"])
def register():
	if request.method == 'POST':
		username = request.form.get("username")
		password = request.form.get("password")
		email = request.form.get("email")
		name = request.form.get("name")
		surname = request.form.get("surname")
		mobile = request.form.get("mobile")
		birthday = request.form.get("birthday")

		user = user = User.query.filter(User.username.ilike(username)).first()
		user_email = User.query.filter(User.email.ilike(email)).first()

		if not user and not user_email:
			password = generate_password_hash(password, method="sha256")
			new_user = User(username=username, password=password, email=email, name=name,
						surname=surname, mobile=mobile, birthday=birthday)
			db.session.add(new_user)
			db.session.commit()
			flash(u"You have successfully registered! Please login with your new credentials", 'success')
			return redirect(url_for('index'))

		elif user:
			flash(u"This user already exists!", 'error')
		elif email:
			flash(u"This email is already in use", 'error')

	return render_template('register.html')


@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		user = User.query.filter(User.username.ilike(username)).first()

		if user:
			if check_password_hash(user.password, password):
				login_user(user)
				flash(u"You have successfully logged in!", 'success')
				return redirect(url_for('index'))
			else:
				flash(u"Invalid password!", 'error')
		else:
			flash(u"Invalid username!", 'error')
	return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
	user = User.query.get(username)
	print (user)
	if request.method == 'POST':
	    # check if the post request has the file part
		if 'file' not in request.files:
			flash(u'No file part', 'error')
			return redirect(request.url)
		file = request.files['file']
	    # if user does not select file, browser also
	    # submit a empty part without filename
		if file.filename == '':
			flash(u'No selected file', 'error')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			flash(u'successfull uploaded file', 'success')
			

			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('uploaded_file',
		                            filename=filename))
	return render_template('edit.html')



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
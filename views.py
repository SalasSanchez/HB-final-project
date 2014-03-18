from flask import Flask, render_template, redirect, request, g, session, url_for, flash
from model import User, Post
from flask.ext.login import LoginManager, login_required, login_user, current_user
from flaskext.markdown import Markdown
import config
import forms
import model

app = Flask(__name__)
app.config.from_object(config)

# Stuff to make login easier
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# End login stuff

# Adding markdown capability to the app
Markdown(app)

@app.route("/")
@login_required
def index():
    user_id = current_user.id
    codes = model.Code.query.filter_by(user_id=user_id).all() 
    return render_template("index.html", codes=codes)

# @app.route("/post/<int:id>")
# def view_post(id):
#     post = Post.query.get(id)
#     return render_template("post.html", post=post)

# @app.route("/post/new")
# @login_required
# def new_post():
#     return render_template("new_post.html")

@app.route("/new_code", methods=["POST"])
@login_required
def add_code():
    form = forms.NewCodeForm(request.form)
    if not form.validate():
        flash("Error, all fields are required")
        return render_template("new_code.html")

    code = Code(company=form.company.data, code=form.code.data)
    current_user.codes.append(code) 
    
    model.session.commit()
    model.session.refresh(code)

    return redirect(url_for("index")

    #TODO: Check the redirects- is this correct if the new-code form is already on index.html?


@app.route("/set_user")
def set_user():
    return render_template("set_user.html")

@app.route("/set_user", methods=["POST"])
def authenticate():
    form = forms.LoginForm(request.form)
    if not form.validate():
        flash("Incorrect username or password") 
        return render_template("set_user.html")

    email = form.email.data
    password = form.password.data

    user = User.query.filter_by(email=email).first()

    if not user or not user.authenticate(password):
        flash("Incorrect username or password") 
        return render_template("set_user.html")

    login_user(user)
    return redirect(request.args.get("next", url_for("index")))
    #what's this 'next'

def create_user():
    form= forms.NewUserForm(request.form)
    if not form.validate():
        flash("Please, fill out all fields")
        return render_template("set_user.html")

    first_name = form.first_name.data
    last_name = form.last_name.data
    email = form.email.data
    password = form.password.data

    user = insert(users, first_name=first_name,
                             last_name= last_name,
                             email=email,
                             password=password)

    login_user(user)
    return redirect(request.args.get("next", url_for("index")))



if __name__ == "__main__":
    app.run(debug=True)
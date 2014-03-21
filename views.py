from flask import Flask, render_template, redirect, request, g, session, url_for, flash
import model
from flask.ext.login import LoginManager, login_required, login_user, current_user
from flaskext.markdown import Markdown
import config
import forms

app = Flask(__name__)
app.config.from_object(config)

# Stuff to make login easier
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return model.User.query.get(user_id)

# End login stuff

# Adding markdown capability to the app
Markdown(app)

@app.route("/")
def set_user():
    return render_template("set_user.html")


@app.route("/log_in", methods=["POST"])
def authenticate():
    login_form = forms.LoginForm(request.form)
    if not login_form.validate():
        flash("Incorrect username or password") 
        return "It didn't work"
        #return render_template("set_user.html")

    email = login_form.email.data
    password = login_form.password.data

    user = model.User.query.filter_by(email=email).first() 
    
    print user 

    if not user or not user.authenticate(password):
        flash("Incorrect username or password") 
        return "wrong"
        #return render_template("set_user.html")

    login_user(user)
    return "You're logged in"
    #return redirect(request.args.get("next", url_for("index")))
    #what's this 'next'



@app.route("/register", methods=["POST"])

def create_user():
    new_user_form = forms.NewUserForm(request.form)
    if not new_user_form.validate():
        flash("Please, fill out all fields")
        return "It didn't work" 
        #render_template("wallet.html")

    first_name = new_user_form.first_name.data
    last_name = new_user_form.last_name.data
    email = new_user_form.email.data
    password = new_user_form.password.data

    user = model.User(first_name=first_name,
                      last_name= last_name,
                      email=email,
                      password=password)
    user.set_password(password)
    model.session.add(user)
    model.session.commit()
    return "You've created a profile"
#     login_user(user)
#     return redirect(request.args.get("next", url_for("index")))









# @app.route("/")
# @login_required
# def index():
#     user_id = current_user.id
#     codes = model.Code.query.filter_by(user_id=user_id).all() 
#     return "This is the main page"
#         #render_template("index.html", codes=codes)

# # @app.route("/post/<int:id>")
# # def view_post(id):psycopg2==2.5.1

# #     post = Post.query.get(id)
# #     return render_template("post.html", post=post)

# # @app.route("/post/new")
# # @login_required
# # def new_post():
# #     return render_template("new_post.html")

# @app.route("/new_code", methods=["POST"])
# @login_required
# def add_code():
#     form = forms.NewCodeForm(request.form)
#     if not form.validate():
#         flash("Error, all fields are required")
#         return render_template("new_code.html")

#     code = Code(company=form.company.data, code=form.code.data)
#     current_user.codes.append(code) 
    
#     model.session.commit()
#     model.session.refresh(code)

#     return redirect(url_for("index"))

#     #TODO: Check the redirects- is this correct if the new-code form is already on index.html?



if __name__ == "__main__":
    app.run(debug=True)
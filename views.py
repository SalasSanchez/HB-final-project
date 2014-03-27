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
        return render_template("set_user.html")

    email = login_form.email.data
    password = login_form.password.data

    user = model.User.query.filter_by(email=email).first() 
    
    

    if not user or not user.authenticate(password):
        flash("Incorrect username or password") 
        return render_template("set_user.html")

    login_user(user)
    flash("You're logged in")

    return redirect(url_for("main_wallet"))
    


@app.route("/register", methods=["POST"])

def create_user():
    new_user_form = forms.NewUserForm(request.form)
    if not new_user_form.validate():
        flash("Please, fill out all fields")
        return render_template("set_user.html")

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
    
    login_user(user)
    return redirect(url_for("main_wallet"))


@app.route("/main_wallet")
@login_required
def main_wallet():
    user_id = current_user.id
    codes = model.Code.query.filter_by(user_id=user_id).all() 

    return render_template("main_wallet.html", codes=codes)
    


@app.route("/see_details/<int:code_id>")
@login_required
def code_details(code_id):
    details= model.Code.query.filter_by(id=code_id).one() 
    
    #print dir(details)

    referral_code= details.referral_code
    company_id= details.company_id
    company = model.Company.query.filter_by(id=company_id).one()
    company_name = company.name
    expiry_date= details.expiry_date
    
    if details.description:
        description= details.description
    else:
        description= "No description provided"
    
    if details.url:
        url= details.url
    else:
        url= "No URL provided"

    return render_template("code_details.html", referral_code=referral_code,
                                                company_name= company_name,
                                                expiry_date=expiry_date,
                                                description=description,
                                                url=url)



@app.route("/new_code", methods=["POST"])
@login_required
def add_code():
    form = forms.NewCodeForm(request.form)
    if not form.validate():
        flash("Error, all fields are required")
        return render_template("main_wallet.html")

    if model.Company.query.filter_by(name=form.company.data).first():
        company = model.Company.query.filter_by(name=form.company.data).first()
    
    else:
        company = model.Company(name=form.company.data)
        model.session.add(company)
        model.session.commit()
        company = model.Company.query.filter_by(name=form.company.data).first()

    company_id = company.id

    if form.expiry_date.data=="":
        form.expiry_date.data = None

    code = model.Code(company_id=company_id,
                referral_code=form.code.data, 
                url=form.url.data,
                expiry_date=form.expiry_date.data,
                description=form.description.data)

    current_user.codes.append(code) 
    
    model.session.commit()
    model.session.refresh(code)
    flash("You've added a code to your wallet")

    return redirect(url_for("main_wallet"))



@app.route("/buddies")
@login_required
def see_buddies():
    user_id= current_user.id
    friendships = model.Friendship.query.filter_by(user_id=user_id).all()
    buddies_ids = []

#TODO: This can be made easier wit backrefs:    
    for friendship in friendships:
        buddy_id = friendship.buddy_id
        buddies_ids.append(buddy_id)


    buddies = []

    for buddy in buddies_ids:
        user = model.User.query.filter_by(id=buddy).one()
        buddies.append(user)

    return  render_template("buddies.html", buddies=buddies)


# @app.route("/new_buddy", methods=["POST"])
# @login_required
# def add_buddy():
#     form = forms.NewBuddyForm(request.form)
    
#     if not form.validate():
#         flash("Error, all fields are required")
#         return render_template("buddies.html")

#     if model.User.query.filter_by(email=form.email.data).first():
#         buddy = model.User.query.filter_by(email=form.email.data).first()

#     else:
#         buddy = model.Invitation(email=form.email.data, 
#                            first_name=form.first_name.data,
#                            last_name=form.last_name.data)

#         model.session.add(buddy)
#         model.session.commit()
    

#     buddy_id = buddy.id

#     buddy = model.Code(company_id=company_id,
#                 referral_code=form.code.data, 
#                 url=form.url.data,
#                 expiry_date=form.expiry_date.data,
#                 description=form.description.data)

#     current_user.codes.append(code) 
    
#     model.session.commit()
#     model.session.refresh(code)
#     flash("You've added a code to your wallet")

#     return render_template("buddies.html")

# return 






@app.route("/buddy/<int:id>")
@login_required
def see_buddy(id):
    details= model.User.query.filter_by(id=id).one() 
    
    first_name = details.first_name
    last_name = details.last_name
    email = details.email
    codes= details.codes

    return render_template("buddy_details.html", first_name=first_name,
                                                 last_name=last_name,
                                                 email=email,
                                                 codes=codes)





if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True port=port)
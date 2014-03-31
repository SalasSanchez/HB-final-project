from flask import Flask, render_template, redirect, request, g, session, url_for, flash, jsonify
import model
from flask.ext.login import LoginManager, login_required, login_user, current_user
from flaskext.markdown import Markdown
import config
import forms
import os
import json
import requests


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



@app.route("/new_buddy", methods=["POST"])
@login_required
def add_buddy():
    form = forms.NewBuddyForm(request.form)
    
    if not form.validate():
        flash("Please, fill out all required fields")
        return render_template("buddies.html")

    if model.User.query.filter_by(email=form.email.data).first():
        buddy = model.User.query.filter_by(email=form.email.data).first()
        
        if form.message.data:
            message=form.message.data
        else:
            message=""

        invitation = model.Invitation(first_name=buddy.first_name,
                                      last_name=buddy.last_name,
                                      invitee_email=buddy.email,
                                      message=message,
                                      inviter_id=current_user.id,
                                      invitee_id=buddy.id,
                                      status= "Open")

        model.session.add(invitation)
        model.session.commit()

        flash("A invitation has been sent")
        return render_template("buddies.html")


    else:
        if form.message.data:
            message=form.message.data
        else:
            message=""

        buddy = model.Invitation(invitee_email=form.email.data, 
                           first_name=form.first_name.data,
                           last_name=form.last_name.data,
                           message= message,
                           inviter_id= current_user.id,
                           status="Open")

        model.session.add(buddy)
        model.session.commit()
    
        flash("A invitation has been sent")
        return render_template("buddies.html")




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


@app.route("/codes")
@login_required
def codes_available():
    user_id= current_user.id
    
    buddies = model.Friendship.query.filter_by(user_id=user_id).all()
    
    codes_list=[]

    for buddy in buddies:
        #codes = buddy.codes
        buddy_id = buddy.buddy_id
        codes = model.Code.query.filter_by(user_id=buddy_id).all()
        for code in codes:
            codes_list.append(code)

    return render_template("codes_available.html", codes= codes_list)




@app.route('/ajax/get_codes', methods = ['GET'])
@login_required
def get_codes(code_id):
    #must get url to just get the codes for the site in question.
    user = current_user
    user_id=user.id
    codes = model.Code.query.filter_by(user_id=user_id).all()
    codes_dict ={}
    for code in codes:
        name=code.company.name
        codes_dict.update({name: name})     

    return jsonify(codes_dict)

#def new_code_popup /ajax/new_code

# @app.route("/ajax/new_code", methods=["POST"])
# #@login_required
# def add_code(data):
#     form_info= request.form.get(data)
#     print form_info

    




#     form = forms.NewCodeForm(request.form)
#     if not form.validate():
#         flash("Error, all fields are required")
#         return render_template("main_wallet.html")

#     if model.Company.query.filter_by(name=form.company.data).first():
#         company = model.Company.query.filter_by(name=form.company.data).first()
    
#     else:
#         company = model.Company(name=form.company.data)
#         model.session.add(company)
#         model.session.commit()
#         company = model.Company.query.filter_by(name=form.company.data).first()

#     company_id = company.id

#     if form.expiry_date.data=="":
#         form.expiry_date.data = None

#     code = model.Code(company_id=company_id,
#                 referral_code=form.code.data, 
#                 url=form.url.data,
#                 expiry_date=form.expiry_date.data,
#                 description=form.description.data)

#     current_user.codes.append(code) 
    
#     model.session.commit()
#     model.session.refresh(code)
#     flash("You've added a code to your wallet")

#     return redirect(url_for("main_wallet"))




if __name__ == "__main__":
    #port = int(os.environ.get("PORT", 5000))
    app.run(debug=True)   #, port=port
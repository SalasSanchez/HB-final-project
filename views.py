from flask import Flask, render_template, redirect, request, g, session, url_for, flash, jsonify
import model
from flask.ext.login import LoginManager, login_required, login_user, current_user
from flaskext.markdown import Markdown
import config
import forms
import os
import json
import re


app = Flask(__name__)
app.config.from_object(config)

# Stuff to make login easier
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "set_user"

@login_manager.user_loader
def load_user(user_id):
    return model.User.query.get(user_id)

# End login stuff

# Adding markdown capability to the app
Markdown(app)


# Defining some useful functions to make routes easier:

def finds_company_id(company_name):
    company = model.Company.query.filter_by(name=company_name).first()

    if not company:
        company = model.Company(name=company_name)
        model.session.add(company)
        model.session.commit()

    return company.id

def finds_category_id(category_name):
    category=model.Category.query.filter_by(name=category_name).first()

    if category==None:
        category=model.Category(name=category_name)
        model.session.add(category)
        model.session.commit()

    return category.id


def buddies_list(user_id):
    friendships = model.Friendship.query.filter_by(user_id=user_id).all()
    buddies_ids = []

#TODO: This can be made easier with backrefs:    
    for friendship in friendships:
        buddy_id = friendship.buddy_id
        buddies_ids.append(buddy_id)

    buddies = []

    for buddy in buddies_ids:
        user = model.User.query.filter_by(id=buddy).one()
        buddies.append(user)

    return buddies

def open_invitations_list(user_id):
    invitations = model.Invitation.query.filter_by(inviter_id=user_id).all()

    open_invitations = []

    for invite in invitations:
        if invite.status == "Open":
            open_invitations.append(invite)


    return open_invitations




############ Routes start here #######################

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
    flash("Welcome to Referraly!")
    return redirect(url_for("main_wallet"))



@app.route("/main_wallet")
@login_required
def main_wallet():
    user_id = current_user.id
    codes_shared = model.Code.query.filter_by(user_id=user_id).all() 
    
    buddies = model.Friendship.query.filter_by(user_id=user_id).all()
    
    codes_list=[]

    for buddy in buddies:
        #codes = buddy.codes
        buddy_id = buddy.buddy_id
        codes = model.Code.query.filter_by(user_id=buddy_id).all()
        for code in codes:
            codes_list.append(code)

    return render_template("main_wallet.html", codes_for_user= codes_list,
                                               codes_shared=codes_shared)

    

#This route shows the details of the codes the user is sharing with others:
@app.route("/see_details/<int:code_id>")
@login_required
def code_details(code_id):
    details= model.Code.query.filter_by(id=code_id).one() 

    referral_code= details.referral_code
    company_id= details.company_id
    company = model.Company.query.filter_by(id=company_id).one()
    company_name = company.name
    expiry_date_long= details.expiry_date

    expiry_date=re.sub('00:00:00', '', str(expiry_date_long))
    
    if details.description:
        description= details.description
    else:
        description= "No description provided"
    
    # category=model.CodesCat.query.filter_by(code_id=code_id).first()
    # category_name=""
    # if category:
    #     category_details=model.Category.query.filter_by(id=category.id).first()
    #     category_name=category_details.name 
    # else:
    #     category_name="No category provided"

    if details.url:
        url= details.url
    else:
        url= "No URL provided"

    return render_template("code_details.html", referral_code=referral_code,
                                                company_name= company_name,
                                                expiry_date=expiry_date,
                                                description=description,
                                                # category=category_name,
                                                url=url)


#This route shows the details of the codes the user's buddies have shared with her, 
#it shows the same as see_details() but it adds the name of the buddy.
@app.route("/code_for_user/<int:code_id>")
@login_required
def code_for_user(code_id):
    details= model.Code.query.filter_by(id=code_id).one() 
    

    referral_code= details.referral_code
    company_id= details.company_id
    company = model.Company.query.filter_by(id=company_id).one()
    company_name = company.name
    
    expiry_date_long= details.expiry_date
    expiry_date=re.sub('00:00:00', '', str(expiry_date_long))

    user_id= details.user_id

    user = model.User.query.filter_by(id=user_id).first()

    first_name = user.first_name
    #last_name = user.last_name

    name = first_name  #+" "+last_name

    if details.description:
        description= details.description
    else:
        description= "No description provided"
    
    # category=model.CodesCat.query.filter_by(code_id=code_id).first()
    # category_name=""
    # if category:
    #     category_details=model.Category.query.filter_by(id=category.id).first()
    #     category_name=category_details.name 
    # else:
    #     category_name="No category provided"

    if details.url:
        url= details.url
    else:
        url= "No URL provided"



    return render_template("code_for_user.html", referral_code=referral_code,
                                                company_name= company_name,
                                                expiry_date=expiry_date,
                                                description=description,
                                                name=name,
                                                # category=category_name,
                                                url=url)



#This route allows the user to add a new code to her wallet:
@app.route("/new_code", methods=["POST"])
@login_required
def add_code():
    form = forms.NewCodeForm(request.form)
    if not form.validate():
        flash("Error, all fields are required")
        return render_template("main_wallet.html")

    company= form.company.data

    company_id = finds_company_id(company)

    category_name=form.category.data
    
    category_id=finds_category_id(category_name)

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

    code_category = model.CodesCat(code_id=code.id,
                                  category_id=category_id)

    model.session.add(code_category)
    model.session.commit()
    model.session.refresh(code_category)

    flash("You've added a code to your wallet")

    return redirect(url_for("main_wallet"))



# This shows the buddies that the user has:
@app.route("/buddies")
@login_required
def see_buddies():
    user_id = current_user.id
    buddies = buddies_list(user_id)

    return  render_template("buddies.html", buddies=buddies)



#This allows the user to invite someone to be their buddy.
# It only creates the invitation:
@app.route("/new_buddy", methods=["POST"])
@login_required
def add_buddy():
    form = forms.NewBuddyForm(request.form)
    
    if not form.validate():
        flash("Please, fill out all required fields")
        return render_template("buddies.html")

    if form.message.data:
            message = form.message.data
    else:
        message = ""

    #Get the buddies list to be able to repopulate the buddies main page:
    user_id = current_user.id
    buddies = buddies_list(user_id)

    buddy = model.User.query.filter_by(email=form.email.data).first()

    if buddy:
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
        return render_template("buddies.html", buddies=buddies)

    else:

        buddy = model.Invitation(invitee_email=form.email.data, 
                           first_name=form.first_name.data,
                           last_name=form.last_name.data,
                           message= message,
                           inviter_id= current_user.id,
                           status="Open")

        model.session.add(buddy)
        model.session.commit()
    
        flash("A invitation has been sent")
        return render_template("buddies.html", buddies=buddies)




@app.route("/buddy/<int:id>")
@login_required
def see_buddy(id):
    details= model.User.query.filter_by(id=id).one() 
    
    first_name = details.first_name
    #last_name = details.last_name
    email = details.email
    codes= details.codes

    return render_template("buddy_details.html", first_name=first_name,
                                                 #last_name=last_name,
                                                 email=email,
                                                 codes=codes)




#These four admin routes allow the administrator to accept invitations 
#for the invitees and thus create the friendships.
@app.route("/admin")
def manage_invites():

    return render_template("open_invitations.html")


@app.route("/admin/<int:user_id>")
def invitations_by_id(user_id):

    invitations = open_invitations_list(user_id)

    return render_template("open_invitations.html", invitations=invitations)


@app.route("/admin/by_email", methods=["POST"])
def invitations_by_email():
    email_form = forms.EmailForm(request.form)
    email = email_form.email.data

    user = model.User.query.filter_by(email=email).one()
    user_id = user.id

    invitations = open_invitations_list(user_id)

    return render_template("open_invitations.html", invitations=invitations)



@app.route("/admin/accept_invite/<int:id>")
def accept_invite(id):
    invite = model.Invitation.query.filter_by(id=id).one()

    #We change the status of the invitation:
    invite.status = "Accepted"
    model.session.commit()

    #We create the user:
    buddy = model.User(first_name=invite.first_name,
                       last_name=invite.last_name,
                       email=invite.invitee_email,
                       password="Password")

    model.session.add(buddy)
    model.session.commit()
    model.session.refresh(buddy)

    #We create the friendship, symmetrical:
    friendship = model.Friendship(user_id=invite.inviter_id,
                                  buddy_id=buddy.id,
                                  is_active="True")

    model.session.add(friendship)

    friendship_back = model.Friendship(user_id=buddy.id,
                                       buddy_id=invite.inviter_id,
                                       is_active="True")

    model.session.add(friendship_back)
    model.session.commit()
    model.session.refresh(friendship)
    model.session.refresh(friendship_back)

    flash("The users are now friends")

    #We refresh the list of pending invitations:
    invitations = open_invitations_list(invite.inviter_id)


    return render_template("open_invitations.html", invitations=invitations)




#These are the routes for the chrome extension popup:

@app.route("/ajax/new_code", methods=["POST"])
@login_required
def add_code_plugin():
    company= request.form.get('company')
    
    company_id = finds_company_id(company)

    referral_code = request.form.get('code')

    if request.form.get('url'):
        url = request.form.get('url')
    else:
        url = "No URL provided"


    if request.form.get('expiry_date'):
        expiry_date = request.form.get('expiry_date')
    else: 
        expiry_date = ""


    if request.form.get('description'):
        description = request.form.get('description')
    else:
        description = "No description"

    user_id = current_user

    code = model.Code(company_id=company_id,
                referral_code=referral_code, 
                url=url,
                expiry_date=expiry_date,
                description=description,
                user_id=user_id)

    current_user.codes.append(code) 
    
    model.session.commit()
    model.session.refresh(code)

    return "A new code was added"


@app.route("/ajax/popup/", methods=["GET"])
@login_required
def get_codes_by_site():
    long_url = request.args.get("site")
    url_list=long_url.split("/")
    p = re.compile("www.")
    
    url = ""
    for item in url_list:
        if p.match(item):
            url=item

    if url == "":
        codes=[]
    else:

        buddies=model.Friendship.query.filter_by(user_id=current_user.id).all()
        buddy_ids=[]
        for buddy in buddies:
            buddy_ids.append(buddy.buddy_id)

        codes = model.Code.query.filter(model.Code.user_id.in_(buddy_ids), model.Code.url.like('%'+url+'%')).all()
    
    if codes==[]:
        flash("Sorry, no codes available for this site")

    return render_template("popup_content.html", codes=codes)


if __name__ == "__main__":
    #port = int(os.environ.get("PORT", 5000))
    app.run(debug=True)   #, port=port
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



@app.route('/get_codes', methods = ['GET'])
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



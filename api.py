from flask import Flask, jsonify
import model
import json





app = Flask(__name__)




@app.route('/sites', methods = ['GET'])
def get_tasks():
	codes = model.Codes.query.all()

    return "Hello"

    #jsonify( {"codes": codes} )



# @app.route('/newcode', methods = ['POST'])

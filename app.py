import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from jinja2 import FileSystemBytecodeCache
import json

from core.canvas_services import canvas_services as canvasCore
from core.google_services import google_services as googleCore

# # Canvas API URL
# canvas_base_url = "https://canvas.uw.edu/api/v1/"

# Canvas API URL for TESTING
canvas_base_url = "https://uw.beta.instructure.com/api/v1/"

# Canvas access token
f = open("canvasCredentials.json")
json_object = json.load(f)
canvas_access_token = json_object['token']
f.close()

# Initialize a new canvas_services object
canvas = canvasCore(canvas_base_url, canvas_access_token)

app = Flask(__name__)
CORS(app)

### EXAMPLE FUNCTIONS ###
# -----------------------------------------------------------------------------
# Returns to the front end with courses listed as favorites for 
# the user to choose from
@app.route('/courseFavorites')
def coursesFavorites():
    """ returns a list of favorited courses"""
    app.logger.info("A user requested favorite courses")
    subset = ('name', 'id')
    favorites = canvas.getFavorites(subset)
    return jsonify(courses=favorites)

# -----------------------------------------------------------------------------
# Imports groups into Canvas via a csv file
@app.route('/importStudentGroups', methods=['GET', 'POST'])
def importStudents():
    """ imports groups into Canvas via a csv file """
    courseID = request.form.get('courseId') 
    try:
        file = request.files["file"]
    except KeyError:
        return {"Response": "Please Select A File to Upload"}

    result = canvas.importStudentGroups(courseID, file)
    if result == 'success':
        return jsonify(message="Groups created",status_code=200)
    return jsonify(message="Failed", status_code=500)

# -----------------------------------------------------------------------------
# Creates a csv file full of students and their groups from a specified course
@app.route('/exportStudentGroups', methods=['GET', 'POST'])
def exportStudentGroups():
    """ creates a csv file of students and their groups from a 
        specified course 
    """
    response = request.get_json(force=True)
    courseID = response.get('course')
    if request.method == 'POST':
        result = canvas.exportGroupsCSV(courseID)
        # return Functions.exportStudents.exportManager()
        if result == 'success':
            return jsonify(message="Created CSV", status_code=200)
        return jsonify(message="CSV creation failed", status_code=500)

# -----------------------------------------------------------------------------
# Exports a json of the students with a given key
@app.route('/exportGroups', methods=['GET', 'POST'])
def exportGroupsJson():
    """ exports a JSON of all groups and their members with a given key """
    response = request.get_json(force=True)
    courseId = response["courseId"]
    targetKey = response['key']
    roster = canvas.exportGroupsJSON(courseId, key=targetKey)
    return {"Response": roster}

# -----------------------------------------------------------------------------
# Exports a json of the students with a given key
@app.route('/exportGroup', methods=['GET', 'POST'])
def exportGroupJson():
    """ exports a JSON of a group and its members with a given key """
    response = request.get_json(force=True)
    print(response)
    courseId = response["courseId"]
    targetKey = response['key']
    teamName = response['teamName']
    roster = canvas.exportGroupsJSON(courseId, key=targetKey)
    try:
        group = roster[teamName]
    except KeyError:
        return {"Response": "No Group Found"}

    return {"Response": group}

# Returns a list of all the groups in a course
@app.route('/listGroups', methods=['POST', 'GET'])
def getAllGroups():
    """ returns a list of all the groups in a course """
    response = request.get_json(force=True)
    courseID = response['courseID']
    groups = canvas.getGroupsList(courseID)
    return jsonify(response=groups)

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)  # debug=True, in run() for dev purposes

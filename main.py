#!/usr/bin/env python

from wsgiref import simple_server
from flask import Flask, request, render_template
from flask import Response
import os
from flask_cors import CORS, cross_origin
from prediction_Validation_Insertion import pred_validation
from trainingModel import trainModel
from training_Validation_Insertion import train_validation
import flask_monitoringdashboard as dashboard
from predictFromModel import prediction
import json

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
dashboard.bind(app)
CORS(app)

### ================== ###
## PARAMS

training_batch_folder_path = "Training_Batch_Files"

### ================== ###

# Home Route..
@app.route("/", methods=['GET'])
@cross_origin()
def home():
    """ '/' route for application
    
    methods=['GET']

    :return: render_template()
    """

    return render_template('index.html')

# Prediction..
@app.route("/predict", methods=['POST'])
@cross_origin()
def predictRouteClient():
    """'/predict' route for application

    methods=['POST']

    :return: Response Object
    :rtype: Flask Response Object
    """

    try:
        # For Testing Through Postman.
        if request.json is not None:
            path = request.json['filepath']

            pred_val = pred_validation(path)  # object initialization

            pred_val.prediction_validation()  # calling the prediction_validation function

            pred = prediction(path)  # object initialization

            # predicting for dataset present in database
            path, json_predictions = pred.predictionFromModel()
            return Response("Prediction File created at !!!" + str(path) + 'and few of the predictions are ' + str(
                json.loads(json_predictions)))
        # For Testing Through Webapp.
        elif request.form is not None:
            path = request.form['filepath']

            pred_val = pred_validation(path)  # object initialization

            pred_val.prediction_validation()  # calling the prediction_validation function

            pred = prediction(path)  # object initialization

            # predicting for dataset present in database
            path, json_predictions = pred.predictionFromModel()
            return Response("Prediction File created at !!!" + str(path) + 'and few of the predictions are ' + str(
                json.loads(json_predictions)))
        else:
            print('Nothing Matched')
    except ValueError:
        return Response("Error Occurred! %s" % ValueError)
    except KeyError:
        return Response("Error Occurred! %s" % KeyError)
    except Exception as e:
        return Response("Error Occurred! %s" % e)

# Training..
@app.route("/train", methods=['GET', 'POST'])
@cross_origin()
def trainRouteClient():
    """'/train' route for application

    methods=['GET', 'POST']

    :return: Response Object
    :rtype: Flask Response Object
    """

    try:
        # if request.json['folderPath'] is not None:
        
        # path = request.json['folderPath']
        if training_batch_folder_path is not None:
            path = training_batch_folder_path

            train_valObj = train_validation(path)  # object initialization

            train_valObj.train_validation()  # calling the training_validation function

            trainModelObj = trainModel()  # object initialization
            trainModelObj.trainingModel()  # training the model for the files in the table


    except ValueError:

        return Response("Error Occurred! %s" % ValueError)

    except KeyError:

        return Response("Error Occurred! %s" % KeyError)

    except Exception as e:

        return Response("Error Occurred! %s" % e)
    return Response("Training successful!!")


port = int(os.getenv("PORT", 5000))

if __name__ == "__main__":
    host = '0.0.0.0'
    # port = 5000
    httpd = simple_server.make_server(host, port, app)
    print('Default Serving on http://127.0.0.1:5000/')
    
    # print("Serving on %s %d" % (host, port))
    httpd.serve_forever()
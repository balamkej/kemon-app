import os
from flask import Flask, render_template, request, redirect, url_for, send_file
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
# from werkzeug.utils import secure_filename



def mushingIndex(treadleRow):
    return [i for i, j in enumerate(treadleRow) if j == 1]

def mushing(threading,treadleRow):
    row = np.zeros(len(threading[0]), int)
    for i in mushingIndex(treadleRow):
        row = row + threading[i]
        np.clip(row,0,1,row)
    return row

def mushing2(treadleRow,tieup):
    row = np.zeros(len(tieup[0]), int)
    for i in mushingIndex(treadleRow):
        row = row + tieup[:,i]
        np.clip(row,0,1,row)
    return row

def weave(treadle, threading, tieup):
    pattern = np.zeros((len(treadle[:,0]),len(threading[0])), int)
    for i in range(len(treadle[:,0])):
        pattern[i] = mushing(threading, mushing2(treadle[i],tieup))
    # numpy.savetxt("test.csv", pattern, fmt='%i', delimiter=",")
    return pattern

# UPLOAD_FOLDER = 'uploads'

ALLOWED_EXTENSIONS = set(['csv'])

#File extension checking
def allowed_filename(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# returns True if upload extension is valid
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def main():
    return render_template('index.html')

@app.route('/create', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        treadle = request.files['treadle']
        threading = request.files['threading']
        tieup = request.files['tieup']
        outname = treadle.filename.rsplit('.', 1)[0] + '-' + threading.filename.rsplit('.', 1)[0] + '-' + tieup.filename.rsplit('.', 1)[0]


        extCheck = allowed_file(treadle.filename) and allowed_filename(threading.filename) and allowed_filename(tieup.filename)

        if extCheck:
        
            treadleArray = np.genfromtxt(treadle, delimiter=",")
            treadleArray = np.nan_to_num(treadleArray)

            threadingArray = np.genfromtxt(threading, delimiter=",")
            threadingArray = np.nan_to_num(threadingArray)

            tieupArray = np.genfromtxt(tieup, delimiter=",")
            tieupArray = np.nan_to_num(tieupArray)

            if request.form.get('Rotate') != None: 
                treadleArray = np.rot90(treadleArray)

            weaving = weave(treadleArray,threadingArray,tieupArray)
            plt.imsave('uploads/' + outname + '.png', weaving, cmap=cm.gray)

            return send_file('uploads/' + outname + '.png', mimetype='image/png', as_attachment=True, attachment_filename=outname + '.png')
    return render_template('create.html')

@app.route('/rotate', methods=['GET', 'POST'])
def rotate():
    if request.method == 'POST':
        file = request.files['file']
        option = request.form['rotation']

        extCheck = allowed_file(file.filename)

        if extCheck:
            fileArray = np.genfromtxt(file, delimiter=",")
            fileArray = np.nan_to_num(fileArray)
            fileArray = np.int_(fileArray)

            if option == "Right":
            	fileArray = np.rot90(fileArray)
                outname = file.filename.rsplit('.', 1)[0] + '-rotR90'
            else:
            	fileArray = np.rot90(fileArray,3)
                outname = file.filename.rsplit('.', 1)[0] + '-rotL90'

	        np.savetxt('uploads/' + outname + '.csv', fileArray, fmt='%i', delimiter=',')
	        return send_file('uploads/' + outname + '.csv', as_attachment=True, attachment_filename=outname + '.csv')
    return render_template('rotate.html')


if __name__ == "__main__":
    app.run()
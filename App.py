
from flask import Flask, render_template, flash, request, session, send_file, jsonify
from flask import render_template, redirect, url_for, request
import mysql.connector

import pickle
import numpy as np
import pandas as pd


app = Flask(__name__)
app.config['DEBUG']
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/AdminLogin")
def AdminLogin():
    return render_template('AdminLogin.html')


@app.route('/NewUser')
def NewUser():
    return render_template('NewUser.html')


@app.route('/UserLogin')
def UserLogin():
    return render_template('UserLogin.html')


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        if request.form['uname'] == 'admin' and request.form['password'] == 'admin':
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='2medicalchatnewdb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb")
            data = cur.fetchall()

            return render_template('AdminHome.html', data=data)
        else:
            flash("UserName or Password Incorrect!")

            return render_template('AdminLogin.html')

@app.route("/AdminHome")
def AdminHome():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='2medicalchatnewdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb")
    data = cur.fetchall()
    return render_template('AdminHome.html', data=data)


@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        name = request.form['uname']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='2medicalchatnewdb')
        cursor = conn.cursor()
        cursor.execute(
            "insert into regtb values('','" + name + "','" + mobile + "','" + email + "','"+ address +"','" + username + "','" + password + "')")
        conn.commit()
        conn.close()
        flash("Record Saved!")
    return render_template('UserLogin.html')


@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['password']
        session['uname'] = request.form['uname']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='2medicalchatnewdb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username='" + username + "' and password='" + password + "'")
        data = cursor.fetchone()
        if data is None:

            flash("UserName Or Password Incorrect..!")
            return render_template('UserLogin.html', data=data)
        else:
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='2medicalchatnewdb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb where username='" + username + "' and password='" + password + "'")
            data = cur.fetchall()

            flash("you are successfully logged in")
            return render_template('UserHome.html', data=data)


@app.route("/UserHome")
def UserHome():
    uname = session['uname']
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='2medicalchatnewdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb where username='" + uname + "' ")
    data = cur.fetchall()
    return render_template('UserHome.html', data=data)



@app.route('/Predict')
def Predict():
    return render_template('Predict.html')  # Render the HTML form


@app.route('/predict', methods=['POST'])
def predict():
    import tensorflow as tf
    import numpy as np
    from keras.preprocessing import image
    from keras.applications.vgg16 import preprocess_input
    import cv2



    file = request.files['file']
    file.save('static/Out/Test.jpg')
    org = 'static/Out/Test.jpg'

    import_file_path = 'static/Out/Test.jpg'
    img1 = cv2.imread(import_file_path)

    img1S = cv2.resize(img1, (400, 400))

    cv2.imshow('Original image', img1S)

    dst = cv2.fastNlMeansDenoisingColored(img1, None, 10, 10, 7, 21)
    dst = cv2.resize(dst, (400, 400))
    cv2.imshow("Noise Removal", dst)

    import warnings
    warnings.filterwarnings('ignore')

    import tensorflow as tf
    classifierLoad = tf.keras.models.load_model('Vggmodel.h5')

    test_image = image.load_img('./static/Out/Test.jpg', target_size=(200, 200))
    test_image = image.img_to_array(test_image)
    test_image = preprocess_input(test_image)  # Apply VGG16 preprocessing
    test_image = np.expand_dims(test_image, axis=0)  # Add batch dimension

    # Predict
    result = classifierLoad.predict(test_image)

    # Identify the predicted class
    ind = np.argmax(result)

    out = ''
    # re = ''
    if ind == 0:
        print("thyroid_cancer")
        out = "thyroid_cancer"
        pre = "Sorafenib, lenvatinib, vandetanib, cabozantinib, selpercatinib, larotrectinib, entrectinib, " \
              "and pralsetinib are used to treat certain types of thyroid cancer "
    elif ind == 1:
        print("thyroid_ditis")
        out = "thyroid_ditis"
        pre = "Drugs such as aspirin or ibuprofen are used to control pain in mild cases"
    elif ind == 2:
        print("thyroid_hyper")
        out = "thyroid_hyper"
        pre = "The main treatments for an overactive thyroid are: medicines such as carbimazole and propylthiouracil."
    elif ind == 3:
        print("thyroid_nodule")
        out = "thyroid_nodule"
        pre = "These medications, such as methimazole (Tapazole) and propylthiouracil, reduce the amount of hormone " \
              "produced by the thyroid. "
    else:
        out = "Nil"
        pre = "Nil"

    #sendmsg(mobile, "Prediction Result: " + str(out))

    return render_template('Result.html', result=out, pre=pre, org=org)







if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)


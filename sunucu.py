from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_restful import Resource, Api
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,FileField,SubmitField
import email_validator
import base64
from passlib.hash import sha256_crypt
from functools import wraps
import os
import cv2
import numpy as np
from PIL import Image



#kullanıcı giriş decorater

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için giriş yapınız..","danger")
            return redirect((url_for("login")))
    return decorated_function


#kullanıcı kayıt formu

class registerform(Form):
    name = StringField("İsim",validators=[validators.length(min=2,max=25),validators.data_required()])
    surname = StringField("Soyisim",validators=[validators.length(min=2,max=30),validators.data_required()])
    username = StringField("Kullanıcı Adı", validators=[validators.length(min=4, max=25), validators.data_required()])
    email = StringField("E-mail", validators=[validators.email(message="lütfen geçerli bir E-mail adresi giriniz.")])
    password = PasswordField("Parola:",validators=[
        validators.DataRequired("lütfen bir parola belirleyin."),
        validators.EqualTo(fieldname="confirm",message="parolalar uyuşmuyor.")

    ])


    confirm= PasswordField("parola doğrula.")
    file = FileField("resminizi yükleyin...")



class loginform(Form):
    username=StringField("Kullanıcı Adı")
    password= PasswordField("Parola")



app = Flask(__name__)
app.secret_key= "yuztanima"
api = Api(app)

app.config["MYSQL_HOST"] = "localhost" #/ana sunucuda bura değiştirilcek mysql config
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "yuztanima"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql=MySQL(app)

class yuztanıma():
    def resimokuma(names):
        for root, dirs, files in os.walk(os.getcwd()+"\\static\\images\\"):
            for name in files:

                     resim = os.path.abspath(os.path.join(root, name))

                     img=cv2.imread(resim)

                     yuz_casc = cv2.CascadeClassifier("face.xml")

                     griton = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                     yüzler = yuz_casc.detectMultiScale(griton, scaleFactor=1.2, minNeighbors=5, minSize=(50, 50),flags=cv2.CASCADE_SCALE_IMAGE)

                     for (x, y, w, h) in yüzler:
                         cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
                         cv2.imwrite("veriler/" + "viper-" + name , griton[y:y + h, x:x + w])



    def eğitim(names):
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        cascadePath = "face.xml"
        faceCascade = cv2.CascadeClassifier(cascadePath)
        path = 'veriler'

        def get_images_and_labels(path):
            image_paths = [os.path.join(path, f) for f in os.listdir(path)]
            images = []
            labels = []
            for image_path in image_paths:
                image_pil = Image.open(image_path).convert('L')
                image = np.array(image_pil, 'uint8')
                nbr = int(os.path.split(image_path)[1].split(".")[0].replace("viper-", ""))

                faces = faceCascade.detectMultiScale(image)
                for (x, y, w, h) in faces:
                    images.append(image[y: y + h, x: x + w])
                    labels.append(nbr)
                    cv2.imshow("Adding faces to traning set...", image[y: y + h, x: x + w])
                    cv2.waitKey(10)
            return images, labels

        images, labels = get_images_and_labels(path)
        cv2.imshow('test', images[0])
        cv2.waitKey(1)

        recognizer.train(images, np.array(labels))
        recognizer.write('egitim/trainer.yml')
        cv2.destroyAllWindows()

    def karsilastirma(namess):
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read('egitim/trainer.yml')
        cascadePath = "face.xml"
        faceCascade = cv2.CascadeClassifier(cascadePath)
        path = 'yuzverileri'

        cursor2 = mysql.connection.cursor()
        sorgu2 = """select * from users """

        result = cursor2.execute(sorgu2)

        data = cursor2.fetchall()


        if result > 0:

            namesss=session["username"]


            for root, dirs, files in os.walk(os.getcwd()+"\\download"):
                for name in files:
                    if name == namesss+".png":

                        resim = os.path.abspath(os.path.join(root, name))

                        img=cv2.imread(resim)

                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(50, 50),flags=cv2.CASCADE_SCALE_IMAGE)
                        for data2 in data:

                            for (x, y, w, h) in faces:
                                tahminEdilenKisi, conf = recognizer.predict(gray[y:y + h, x:x + w])
                                cv2.rectangle(img, (x, y), (x + w, y + h), (225, 0, 0), 2)


                                if (tahminEdilenKisi==data2["id"]):
                                    session["tahid"]=data2["id"]

                                else:
                                    print("eşleşme yok!!!")








@app.route("/")
def index():
    return render_template("index.html")



veriyitut=""

#kayıt olma sitesi
tamyol=os.getcwd()+"\images"
@app.route("/register",methods=["GET","POST"])
def register():
    form= registerform(request.form)

    if request.method == "POST" and form.validate():
#phpmyadmin üzerinden gerekirse değiştirilcek
        names = form.name.data
        surname = form.surname.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()
        sorgu = " insert into users(name,surname,username,email,password) values(%s,%s,%s,%s,%s) "
        cursor.execute(sorgu,(names,surname,username,email,password))
        mysql.connection.commit()
        cursor.close()

        mysql.connection.commit()
        cursor.close()


        flash("Devam edebilmek için yüzünüzün net belli olduğu resim yükleyin...", "success")
        return render_template("upload.html")
    else:
        return render_template("register.html",form=form)


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
@app.route("/upload", methods=['POST'])
def upload():
    target = os.path.join(APP_ROOT, 'static/images/')
    flash("Başarılı bir şekilde kayıt olundu.", "success")
    cursor = mysql.connection.cursor()
    sorgu = """  select id from users """
    result=cursor.execute(sorgu)

    if result>0:
        data=cursor.fetchall()
        for data2 in data:
            ids=data2["id"]



    mysql.connection.commit()
    cursor.close()

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):

        filename = file.filename
        destination = "/".join([target, filename])
        file.save(destination)

        with open(destination,"rb") as files:
            resim=base64.encodestring(files.read())

        cursor = mysql.connection.cursor()
        sorgu = """  UPDATE users SET resim=%s WHERE id= %s """

        cursor.execute(sorgu,(resim,ids))
        mysql.connection.commit()
        cursor.close()
        os.rename(destination,os.getcwd()+"\\static\\images\\"+str(ids)+".png")


    return redirect(url_for("login"))


#login işlemi

@app.route("/login",methods=["GET","POST"])
def login():
    form=loginform(request.form)

    if request.method == "POST":
        username=form.username.data
        password_ent=form.password.data

        cursor= mysql.connection.cursor()

        sorgu= "select * from users where username = %s"
        sorgu2 = """ select * from users """

        result2 = cursor.execute(sorgu2)
        yol=os.getcwd()+"\\static\\images\\"
        if result2 > 0:
            data = cursor.fetchall()
            for data2 in data:
                deneme=open(yol+str(data2["id"])+".png","wb")
                deneme.write(base64.b64decode(data2["resim"]))
                deneme.close()

        result = cursor.execute(sorgu,(username,))

        if result > 0:
            data = cursor.fetchone()
            real_passw=data["password"]
            name=data["name"]
            surname=data["surname"]
            ids=data["id"]
            if sha256_crypt.verify(password_ent,real_passw):
                flash("Başarıyla giriş yapıldı...","success")

                yuztanıma.resimokuma("dedem")


                session["logged_in"]=True
                session["username"]=username
                session["name"]=name
                session["surname"]=surname
                session["id"]=ids
                return redirect(url_for("index"))
            else:
                flash("sistemde uyuşan parola bulunamadı...","danger")
                return redirect(url_for("login"))

        else:
            flash("Böyle bir kullanıcı bulunmuyor...","danger")
            return redirect(url_for("login"))

        sorgu2 = """ select * from users """

        result2 = cursor.execute(sorgu2)

        if result2 > 0:
            data = cursor.fetchall()
            for data2 in data:
                print(data2["id"])

    return render_template("login.html",form=form)


#logout işlemleri

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/profil/<string:username>")
def profil(username):
    form=registerform(request.form)



    return render_template("profil.html",form=form),username




tamyol2=os.getcwd()+"\download"
tamyol3="C:\\Users"

@app.route("/resimekle",methods=["GET","POST"])
@login_required
def resimekle():
    yuztanıma.eğitim("dedem")
    target = os.path.join(APP_ROOT, 'download/')


    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, session["username"]+".png"])
        print(destination)
        file.save(destination)

        yuztanıma.karsilastirma("dede")
        return redirect(url_for("sonuc"))



    return  render_template("resimekle.html")

@app.route('/display/<filename>')
def display_image(filename):
	pass

@app.route("/sonuc")
def sonuc():
    form=registerform(request.form)

    ids=session["tahid"]
    cursor=mysql.connection.cursor()
    sorgu=""" select * from users where id=%s  """
    result=cursor.execute(sorgu,(ids,))
    data=cursor.fetchone()
    if result>0:
        session["tahname"]=data["name"]
        session["tahsurname"] = data["surname"]
        session["tahusername"] = data["username"]
        session["tahname"] = data["name"]
        session["tahemail"] = data["email"]
        session["iids"]=data["id"]




    return render_template("sonuc.html",form=form)


if __name__ == '__main__':
    app.run(debug=True)
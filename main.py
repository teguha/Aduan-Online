from multiprocessing.dummy import active_children
from flask import Flask , render_template, url_for , request ,redirect , session, flash
from flask_mysqldb import MySQLdb
import pymysql
import uuid
import re
import time
import os 
import bcrypt
import hashlib
import numpy as np

salt = bcrypt.gensalt()

from werkzeug.utils import secure_filename

app = Flask(__name__)
localtime = time.localtime(time.time())
app.secret_key="wakandacountry"
mydb = pymysql.connect(
    host ='localhost',
    user='root',
    passwd='',
    database='aduans'
)

ALLOWED_EXTENSION = set(['.png', '.jpeg' , '.jpg','.img'])  


@app.route("/")
@app.route("/home")
def home():
    query = "SELECT * FROM aduan ORDER BY id_aduan ASC"
    mycursor = mydb.cursor()
    mycursor.execute(query)
    datas = mycursor.fetchall()
    return render_template('index.html',title="wakanda report" , data = datas)

@app.route("/aduan")
def aduan():
    if 'id' in session :
        query = "SELECT * FROM aduan ORDER BY id_aduan ASC"
        mycursor = mydb.cursor()
        mycursor.execute(query)
        datas = mycursor.fetchall()
        return render_template('aduan.html', title="aduan publik" , data = datas)
    else:
        return redirect(url_for('home'))

@app.route("/dsh" ,  methods=['GET' , 'POST'])
def dsh():
    if 'id' in session:
        bulans=[]
        tahun=0
        if request.method =='POST':
            tahun = request.form['years']
        else:
            tahun=2022
        if tahun ==0:
            year=2022
        else:
            year = tahun
        for x in np.arange(1,13):
            query = "SELECT COUNT(id_aduan) FROM aduan WHERE MONTH(tanggal_aduan) =%s and YEAR(tanggal_aduan) =%s"
            value = (x,year)
            mycursor = mydb.cursor()
            mycursor.execute(query,value)
            month1 = mycursor.fetchall()
            # print(month1)
            a2= list(month1[0])
            bulans.append(a2)

        labels= [row[0] for row in bulans]
        print(labels)
            

        query = "SELECT COUNT(id_aduan) FROM aduan WHERE  status_aduan = 'terkirim'"
        mycursor = mydb.cursor()
        mycursor.execute(query)
        datas1 = mycursor.fetchall()
        a1= list(datas1[0])
        

        query = "SELECT COUNT(id_aduan) FROM aduan WHERE  status_aduan != 'terkirim'"
        mycursor = mydb.cursor()
        mycursor.execute(query)
        datas2 = mycursor.fetchall()
        a2= list(datas2[0])

        # else:
        #     for x in np.arange(1,13):
        #         query = "SELECT COUNT(id_aduan) FROM aduan WHERE MONTH(tanggal_aduan) =%s and YEAR(tanggal_aduan) =%s"
        #         value = (x,year)
        #         mycursor = mydb.cursor()
        #         mycursor.execute(query,value)
        #         month1 = mycursor.fetchall()
        #         # print(month1)
        #         a2= list(month1[0])
        #         bulans.append(a2)
        
        return render_template('dashboard.html', title="dashbord" , a=a1[0], b=a2[0],labeld=labels)
    else:
        return redirect(url_for('home'))

@app.route("/profile")
def profile():
    # error = None
    if 'id' in session:
        sesion = session['id']
        query = "SELECT * FROM admin WHERE id_admin=%s"
        value = (sesion)
        mycursor = mydb.cursor()
        mycursor.execute(query,value)
        datas = mycursor.fetchone()
        

        #print(datas[1])

        # sesion = session['username']
        # query = "SELECT * FROM admin WHERE username=%s"
        # value = (sesion)
        # mycursor = mydb.cursor()
        # mycursor.execute(query,value)
        # datas = mycursor.fetchone()
        # if datas is not None and len(datas) >0:
        #     new_username = request.form['username']
        #     new_password = request.form['password']
        #     query = "UPDATE admin WHERE username=%s"
        #     value = (sesion)
        #     mycursor = mydb.cursor()
        #     mycursor.execute(query,value)
        #     datas = mycursor.fetchone()
        flash('You were successfully logged in')
        # return redirect(url_for('profile'))
        return render_template('profile.html', title="profile", data= datas)
    else:
        #error = "silahkan login terlebihdahulu"
        return redirect(url_for('home'))

@app.route("/login" , methods=['GET' , 'POST'])
def login():
    error = None
    if request.method =='POST':
        username = request.form['username']
        passw = request.form['password'].encode('utf-8')
        md5 = hashlib.md5()
        md5.update(passw)
        psw = md5.hexdigest()
        # hash_password = bcrypt.hashpw(passw, bcrypt.gensalt())
        query = "SELECT * FROM admin WHERE username= %s and passwd=%s"
        values = (username,psw)
        mycursor = mydb.cursor()
        mycursor.execute(query,values)
        datas = mycursor.fetchone()
        print(values)
        #print(bcrypt.hashpw(passw,salt))
        #print(hash_password)
    
        if datas is not None and len(datas) > 0:
            session['id'] = datas[0]
            print("succes")
            return redirect(url_for('dsh'))
        else :
            error ="Gagal Username dan Password salah !"
            return render_template('login.html',title='login', error=error)
    else :
        return render_template('login.html' , title='login' , error = error)

@app.route("/report_send" , methods=['POST'])
def report_send():
    error = None
    # hasil = {"status:gagal mengirim aduan"
    
    try:
        name= request.form['nama']
        no_handphones = request.form['no_hp']
        aduann = request.form['aduan']
        status = "terkirim"

        if request.method == 'POST':
            file = request.files['bukti_aduan']
            extension = os.path.splitext(file.filename)[1]
            if extension in ALLOWED_EXTENSION :
                f_name = str(uuid.uuid4()) + extension
                app.config['UPLOAD_FOLDER'] = 'static/uploads'
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))

                #cek nomor hp
                hitung = len(str(no_handphones))
                lis = list(str(no_handphones))
                cek = no_handphones.count("+")
                if hitung > 14 and hitung < 10 :
                    print("masikmal karakter 14 dan minimal 0 dan karakter harus diawali huruf 0 atau +")
                elif lis[0] =="0" and lis[1] =="8" and cek == 0:
                    query = "INSERT INTO aduan (nama , no_hp , aduan , bukti_aduan ,tanggal_aduan , status_aduan ) VALUES(%s,%s,%s,%s,%s,%s)"
                    values = (name.title() , no_handphones,aduann,f_name,localtime, status , )
                    mycursor = mydb.cursor()
                    mycursor.execute(query,values)
                    mydb.commit()
                        # return redirect(url_for("home") , data ="Berhasil mengirim aduan")
                    return redirect(url_for("home"))
                    
                elif lis[0] == "+" and lis[1] == "6" and cek == 1 :
                    query = "INSERT INTO aduan (nama , no_hp , aduan , bukti_aduan ,tanggal_aduan , status_aduan ) VALUES(%s,%s,%s,%s,%s,%s)"
                    values = (name.title() , no_handphones,aduann,f_name,localtime, status , )
                    mycursor = mydb.cursor()
                    mycursor.execute(query,values)
                    mydb.commit()
                        # return redirect(url_for("home") , data ="Berhasil mengirim aduan")
                    return redirect(url_for("home"))
                else :
                    print("salah")
                    error='salah'
                    return redirect(url_for("home"), error= error)
        return redirect(url_for("home"))
        
    except Exception as e:
        print("Error: " + str(e))
        # return redirect(url_for("home") , data ="Gagal mengrim aduan" +str(e))
        return redirect(url_for("home"))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    error = None
    if 'id' in session:
        sesion = session['id']
        query = "SELECT * FROM admin WHERE id_admin=%s"
        value = (sesion)
        mycursor = mydb.cursor()
        mycursor.execute(query,value)
        datas = mycursor.fetchone()

        new_username = request.form['username']
        if request.form['password'] == datas[2]:
            query = "UPDATE admin SET username =%s  WHERE id_admin=%s "
            value = (new_username,sesion)
            mycursor = mydb.cursor()
            mycursor.execute(query,value)
            mydb.commit()
            
            flash("Username dan Password berhasil di update !")

        elif len(request.form['password']) > 0 or request.form['password'] != datas[2]:
            new_password = request.form['password'].encode('utf-8')
            md5 = hashlib.md5()
            md5.update(new_password)
            psw = md5.hexdigest()
            query = "UPDATE admin SET username =%s , passwd=%s  WHERE id_admin=%s "
            value = (new_username,psw,sesion)
            mycursor = mydb.cursor()
            mycursor.execute(query,value)
            mydb.commit()
          
            flash("Username dan Password berhasil di update !")
        
        else:
            error="Data yang diupdate tidak boleh kosong !"

        query = "SELECT * FROM admin WHERE id_admin=%s"
        value = (sesion)
        mycursor = mydb.cursor()
        mycursor.execute(query,value)
        datas = mycursor.fetchone()
        
        return render_template('profile.html', title="profile",data =datas , error= error)
    else:
        error = "Login terlebih dahulu !"
        return redirect(url_for('home'), error=error)


@app.route('/update_data_aduan', methods=['POST'])
def update_data_aduan():
    if 'id' in session:
        try:
            ids= session['id']
            tanggapan = request.form['tanggapan']
            id = request.form['id_data']
            query = "UPDATE aduan SET tanggapan_aduan = %s , tanggal_respon = %s, status_aduan =%s , id_admin = %s WHERE id_aduan=%s"
            values = (tanggapan, localtime , "diterima" ,ids , id ,)
            
            mycursor = mydb.cursor()
            mycursor.execute(query, values)
            mydb.commit()
            return redirect(url_for("aduan"))
        except Exception as e:
            print("Error:" + str(e))
            return redirect(url_for("login"))
    else:
        return redirect(url_for('home'))
        # return redirect(url_for("login") , data ="update aduan gagal"+ str(e))

@app.route('/delete_data_aduan/<string:id_data>', methods=['POST'])
def delete_data_aduan(id_data):
    if 'id' in session :
        try:
            query = "DELETE FROM aduan WHERE id_aduan = %s"
            values = ( id_data ,)
            mycursor = mydb.cursor()
            mycursor.execute(query, values)
            mydb.commit()
            return redirect(url_for("login"))
        except Exception as e:
            print("Error:" + str(e))
            return redirect(url_for("login"))
        # return redirect(url_for("login") , data ="update aduan gagal"+ str(e))
    else:
        return redirect(url_for('home'))

@app.route('/logout', methods=['POST'])
def logout():
    if 'id' in session :
        session.clear()
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))
  

if __name__ == '__main__':
    app.run(port=235555 , debug=True)
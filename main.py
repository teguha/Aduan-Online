from multiprocessing.dummy import active_children
from flask import Flask , render_template, url_for , request ,redirect
import pymysql
import uuid
import re
import time
import os 

from werkzeug.utils import secure_filename

app = Flask(__name__)
localtime = time.localtime(time.time())


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
    query = "SELECT * FROM aduan ORDER BY id_aduan ASC"
    mycursor = mydb.cursor()
    mycursor.execute(query)
    datas = mycursor.fetchall()
    return render_template('aduan.html', title="aduan publik" , data = datas)

@app.route("/login" , methods=['GET'])
def login():
    return render_template('dsh.html', title="wakanda dashbord")

@app.route("/report_send" , methods=['POST'])
def report_send():
    # hasil = {"status:gagal mengirim aduan"}

    try:
        name= request.form['nama']
        no_handphones = request.form['no_hp']
        aduann = request.form['aduan']
        status = "terkirim"

        hitung = len(str(no_handphones))
        lis = list(str(no_handphones))
        cek = no_handphones.count("+")
        if hitung > 14 and hitung < 10 :
            print("masikmal karakter 14 dan minimal 0")
        elif lis[0] != "0" and cek == 0:
            print("karakter harus diawali huruf 0 atau +")
        else :
            print("salah")

        
        if request.method == 'POST':
            file = request.files['bukti_aduan']
            extension = os.path.splitext(file.filename)[1]
            if extension in ALLOWED_EXTENSION :
                f_name = str(uuid.uuid4()) + extension
                app.config['UPLOAD_FOLDER'] = 'static/uploads'
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))

                query = "INSERT INTO aduan (nama , no_hp , aduan , bukti_aduan ,tanggal_aduan , status_aduan ) VALUES(%s,%s,%s,%s,%s,%s)"
                values = (name.title() , no_handphones,aduann,f_name,localtime, status , )
                mycursor = mydb.cursor()
                mycursor.execute(query,values)
                mydb.commit()
                    # return redirect(url_for("home") , data ="Berhasil mengirim aduan")
                return redirect(url_for("home"))
            return redirect(url_for("home"))
        return redirect(url_for("home"))
        
    except Exception as e:
        print("Error: " + str(e))
        # return redirect(url_for("home") , data ="Gagal mengrim aduan" +str(e))
        return redirect(url_for("home"))

@app.route('/update_data_aduan', methods=['POST'])
def update_data_aduan():
	
    try:
        tanggapan = request.form['tanggapan']
        id = request.form['id_data']
        query = "UPDATE aduan SET tanggapan_aduan = %s , tanggal_respon = %s, status_aduan =%s , id_admin = %s WHERE id_aduan=%s"
        values = (tanggapan, localtime , "diterima" ,1 , id ,)
        
        mycursor = mydb.cursor()
        mycursor.execute(query, values)
        mydb.commit()
        return redirect(url_for("login"))
    except Exception as e:
        print("Error:" + str(e))
        return redirect(url_for("login"))
        # return redirect(url_for("login") , data ="update aduan gagal"+ str(e))



@app.route('/delete_data_aduan/<string:id_data>', methods=['POST'])
def delete_data_aduan(id_data):
	
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
  

if __name__ == '__main__':
    app.run(port=235555 , debug=True)
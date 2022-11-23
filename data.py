import pymysql
import bcrypt

salt = bcrypt.gensalt()

from werkzeug.utils import secure_filename

mydb = pymysql.connect(
    host ='localhost',
    user='root',
    passwd='',
    database='aduans'
)

passw = 'admin123'.encode('utf-8')
hash_password = bcrypt.hashpw(passw, bcrypt.gensalt())
print(hash_password)
query = "INSERT INTO admin (username,passwd ) VALUES(%s,%s)"
values = ('admin' , hash )
mycursor = mydb.cursor()
mycursor.execute(query,values)
mydb.commit()
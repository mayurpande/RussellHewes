import pymysql.cursors
connection = pymysql.connect(host='Your Host',
                             user='Your Username',
                             password='Your Password',
                             db='carpenter',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

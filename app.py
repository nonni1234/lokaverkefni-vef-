import os
import pymysql.cursors
from flask import Flask, render_template as template, session, url_for, request, redirect
from datetime import datetime
app = Flask(__name__)
app.secret_key = os.urandom(16)
print(app.secret_key)
# Sql stuff
try: # þetta checkar á byrjunni á forritinu og leyfir það ekki að runna ef database tenging er ekki available
    connection = pymysql.connect(
        host='tsuts.tskoli.is',
        user='1809022520',
        password='mypassword',
        db='1809022520_verk7',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
        )
    sql = "SELECT * FROM USERS;"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)
    connection.close()
except pymysql.OperationalError:
    print("Connection Failed (Checkaðu hvort þú ert á tækniskóla wifi-inu)")
    quit()
@app.route("/")
def home(): # Index síðan
    sql = "SELECT * FROM posts"
    args = []
    connection = pymysql.connect(
        host='tsuts.tskoli.is',
        user='1809022520',
        password='mypassword',
        db='1809022520_verk7',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
        )
    with connection.cursor() as cursor:
        cursor.execute(sql)
        posts = cursor.fetchall()
    for x in posts:
        args.append({
            "nr": x["postID"],
            "post": x["post"],
            "nafn": x["nafn"],
            "dagsetning": x["dagsetning"]
        })
    connection.close()
    return template("index.html",posts = args)

@app.route("/user",methods=["GET"])
def user(): # Heimasíða Users
    if not session.get("logged_in"):
        return redirect("/")
    else:
        connection = pymysql.connect(
        host='tsuts.tskoli.is',
        user='1809022520',
        password='mypassword',
        db='1809022520_verk7',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            nafn = session.get("nafn")
            sql = "SELECT post,dagsetning,postID from posts WHERE nafn='%s'" %(nafn)
            cursor.execute(sql)
            results = cursor.fetchall()
            print(results)
            print(nafn)
        connection.close()
        return template("user.html", posts=results, nafn=nafn)

@app.route("/nyttpost", methods=["POST","GET"])
def nytt(): # Bæta við post
    if session.get("logged_in"):
        post = request.form.get("post")
        nafn = session["nafn"]
        time = datetime.now()
        dags = time.strftime("%Y-%m-%d %H:%M:%S")
        dags = str(dags)
        print(dags)
        sql = f"INSERT INTO posts(nafn,post,dagsetning) values('{nafn}','{post}','{dags}')"
        connection = pymysql.connect(
            host='tsuts.tskoli.is',
            user='1809022520',
            password='mypassword',
            db='1809022520_verk7',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
            )
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()
        connection.close()
        return template("done.html",msg="Post hefur verið bætt við")
    else:
        return redirect("/")

@app.route("/eyda", methods=["POST","GET"])
def eyda(): # Eyda Post
    id = request.form.get("postid")
    if session.get("logged_in"):
        name = session["nafn"]
        sql = f"DELETE FROM posts WHERE postID = {id} AND nafn = '{name}'"
        connection = pymysql.connect(
                host='tsuts.tskoli.is',
                user='1809022520',
                password='mypassword',
                db='1809022520_verk7',
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor
                )
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()
            connection.close()
        return redirect(url_for("user"))
    else:
        return redirect("/")
@app.route("/breyta", methods=["POST","GET"])
def breyta(): # Breyta Post
    if request.method == "POST" and session.get("logged_in"):
        connection = pymysql.connect(
        host='tsuts.tskoli.is',
        user='1809022520',
        password='mypassword',
        db='1809022520_verk7',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
        )
        postid = request.form["postid"]
        print(postid)
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT post FROM posts WHERE postID = {postid}")
            i = cursor.fetchone()
            connection.close()
        return template("breyta.html",postid=postid, post=i["post"])

    else:
        return redirect("/")
@app.route("/breytasubmit",methods=["POST","GET"])
def breytasubmit(): # Submit Routeið fyrir Breyta síðuna
    if session.get("logged_in"):
        breyttpost = request.form.get("breyttpost")
        postid = request.form.get("postid")
        nafn = session["nafn"]
        connection = pymysql.connect(
            host='tsuts.tskoli.is',
            user='1809022520',
            password='mypassword',
            db='1809022520_verk7',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
            )
        with connection.cursor() as cursor:
            sql = f"UPDATE posts SET post='{breyttpost}' WHERE postID={postid} AND nafn='{nafn}'"
            cursor.execute(sql)
            connection.commit()
            connection.close()
        return template("done.html",msg="Post hefur verið breytt")
    else:
        return redirect("/")

@app.route("/login", methods=["GET","POST"])
def loginsite():
    if session.get("logged_in"):
        return redirect("/")
    elif request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        sql = f"SELECT * FROM users WHERE user_name = '{name}' AND user_password = '{password}'"
        connection = pymysql.connect(
            host='tsuts.tskoli.is',
            user='1809022520',
            password='mypassword',
            db='1809022520_verk7',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchone()
            connection.close()
            if results == None:
                return template("done.html", msg="rangt lykilorð eða notendanafn")
            else:
                session["logged_in"] = True
                session["nafn"] = results["user_name"]
                return template("done.html",msg="Þú hefur verið skráð/skráður inn!")
    else:
        return template("login.html")

@app.route("/signup", methods=["POST","GET"])
def signup():
    if session.get("logged_in"):
        return redirect("/")
    elif request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        connection = pymysql.connect(
            host='tsuts.tskoli.is',
            user='1809022520',
            password='mypassword',
            db='1809022520_verk7',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            sql = f"INSERT INTO users values('{name}','{email}','{password}');"
            try:
                cursor.execute(sql)
                connection.commit()
            except pymysql.IntegrityError:
                return template("done.html",msg="Þetta email/username er núþegar skráð!")
            finally:
                connection.close()
        return template("done.html",msg="Þú hefur verið registered! Vinsamlegast skráðu þig inn")
    else:
        return template("signup.html")

@app.route("/signout")
def signout():
    if "logged_in" in session:
        session["logged_in"] = False # User er ennþá í session en það ætti ekki að skipta máli því það verður bara overrided
        return template("done.html",msg="Þú hefur verið skráð/skráður út!")
    else:
        return redirect("/")
@app.errorhandler(404)
def pagenotfound(error):
    return template("404.html"), 404

if __name__ == '__main__':
    app.run()
    #app.run(debug=True)
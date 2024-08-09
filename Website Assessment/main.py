from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3, re, base64,os
def get_image_from_blob():
    with open('static/default_profile.jpg', 'rb') as f:
        image_data = str(base64.b64encode(f.read()))
    # Convert from a string to a byte

    # Create a new image file with the data from the blob
    return image_data
def get_profile_picture(username):
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    # Retrieve the image
    query = f"SELECT ProfileImage FROM tUsers WHERE [Username] = '{username}'"
    c = cursor.execute(query)

    # Fetch the data
    image_data = c.fetchone()
    # Convert from a tuple to a byte
    file = str(image_data).strip('(" ",)')
    finalFile = file.strip("b' '")
    # Decode the file
    blob = base64.b64decode(finalFile)
    # Create a new image file with the data from the blob
    text_file = open("static/"+username+".jpg", 'wb')
    text_file.write(blob)
    text_file.close()

    print("Image retrieved and written to file.")

    return username+".jpg"

#Unused but here as a reference template for sql executions
def execute_sql(sql,val):
    """This function commits sql changes to the database."""
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    if val != ():
        cursor.execute(sql, val)
        db.commit()
    else:
        cursor.execute(sql)
        db.commit() ##
app = Flask(__name__)


app.secret_key = 'beans on toast'

# Home route
@app.route('/',methods=("GET", "POST"))
def home():
    if request.method == 'POST':
        search_term = request.form['search']  # Get search term (ID of dictionary
        sql = f"SELECT * FROM 'tUsers' WHERE [Username] = '{search_term}'"
        DATABASE = "database.db"
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        print("beans on toast")
        c = cursor.execute(sql)
        rows = c.fetchall()
        db.close()
        try:
            row_true=rows[0]
            profile_pic = get_profile_picture(row_true[1])
            # Return the combo view page
            return render_template('results.html', search_term=search_term, rows=rows,profile_pic=profile_pic,results=True)
        except:
            return render_template('results.html',results=False)

    sql = "SELECT * FROM 'tUsers'"
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    c = cursor.execute(sql)
    rows = c.fetchall()
    db.close()

    def sortFunc(e):
        return e[4]

    rows.sort(reverse=True, key=sortFunc)
    top1 = rows[0]
    top2 = rows[1]
    top3 = rows[2]
    prof1 = get_profile_picture(top1[1])
    prof2 = get_profile_picture(top2[1])
    prof3 = get_profile_picture(top3[1])


    loggedIn = False

    try:
        if session['loggedin'] == True:
            print(session['username'])
            loggedIn = True

    except:
        print("Beans")


    return render_template('index.html',rows=rows,loggedIn = loggedIn,top1 = top1, top2 = top2, top3 = top3,prof1=prof1,prof2=prof2,prof3=prof3)  # Return index page

# Log In system
@app.route('/signup',methods=['GET','POST'])
def signup():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        DATABASE = "database.db"
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute(f'SELECT * FROM tUsers WHERE [Username] = "{username}"', )
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            image = get_image_from_blob()
            cursor.execute(f'INSERT INTO tUsers VALUES (NULL,"{username}","{password}","{email}",0,"{image}")')
            db.commit()
            msg = 'You have successfully registered !'

    return render_template('signup.html',msg =msg)
@app.route('/login',methods=['GET','POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        DATABASE = "database.db"
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute(f'SELECT * FROM tUsers WHERE [Username] = "{username}" AND [Password] = "{password}"')
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = username
            msg = 'Logged in successfully !'
            sql = "SELECT * FROM 'tUsers'"
            DATABASE = "database.db"
            db = sqlite3.connect(DATABASE)
            cursor = db.cursor()
            c = cursor.execute(sql)
            rows = c.fetchall()
            db.close()

            def sortFunc(e):
                return e[4]

            rows.sort(reverse=True, key=sortFunc)
            top1 = rows[0]
            top2 = rows[1]
            top3 = rows[2]
            prof1 = get_profile_picture(top1[1])
            prof2 = get_profile_picture(top2[1])
            prof3 = get_profile_picture(top3[1])
            return render_template('index.html', msg = msg,top1= top1,top2=top2,top3=top3,prof1=prof1,prof2=prof2,prof3=prof3)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('home'))

#User Pages & Posts
@app.route('/page/<username>',methods=['GET','POST'])
def userpage(username):
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM tUsers WHERE [Username] = "{username}"')
    user = cursor.fetchone()
    print(user[4])
    profile_picture = get_profile_picture(user[1])
    print(profile_picture)
    loggedIn = False

    try:
        if session['loggedin'] == True:
            print(session['username'])
            loggedIn = True

    except:
        print("Beans")
    if loggedIn == True:
        loggedInUser = session['username']
    else:
        loggedInUser = "N/A"
    print(user[1] + " " + loggedInUser)

    return render_template("userpage.html",username = user[1],followerCount = user[4],profile_picture = profile_picture,loggedIn = loggedIn, loggedInUser=loggedInUser)

@app.route('/subscribe/<username>',methods=['GET','POST'])
def subscribe(username):
    print("hello")
# Run the app
if __name__ == "__main__":
    app.run(port=8080, debug=True)
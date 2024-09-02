from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import re
import base64
import os


def get_default_image():  # Gets the image data from the default profile image. Set to newly created accounts
    with open('static/default_profile.jpg', 'rb') as f:
        # Convert to Base64 for easy transfer
        image_data = str(base64.b64encode(f.read()))
    return image_data
def return_image(image_name, username):  # Returns image from user posts
    # Connect to database
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    # Get image data from posts table.
    query = f"SELECT ImageData FROM tPosts WHERE [Username] = '{username}' AND [PostName] = '{image_name}'"
    c = cursor.execute(query)
    image_data = c.fetchone()
    # Convert the data from tuple to a byte
    file = str(image_data).strip('(" ",)')
    finalFile = file.strip("b' '")
    # Decode the file
    blob = base64.b64decode(finalFile)
    # Create a new image file with the data from the blob
    img_file = open("static/" + image_name + "_" + username + ".jpg", 'wb')
    img_file.write(blob)
    img_file.close()

    print("Image retrieved and written to file.")
    # Name and return the image. Stores in /static/.
    return image_name+"_"+username + ".jpg"
def return_all_posts(username):  # Returns all posts from a user's page
    # Connect to database
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    # Get image data from posts table
    query = f"SELECT PostName FROM tPosts WHERE [Username] = '{username}'"
    c = cursor.execute(query)
    images = c.fetchall()
    imageList = []
    # Loop through each image in the query
    for i in range(len(images)):
        # Add the current image to the ImageList list, using return_image to convert
        imageList.append(return_image(str(images[i]).strip("(' ',)"), username))
    # Return all the images in the list
    return imageList
def delete_image_files():  # For cleanup. Removes profile images from static/ when not in use
    # Select from the Users table
    sql = "SELECT * FROM 'tUsers'"
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    c = cursor.execute(sql)
    rows = c.fetchall()
    db.close()
    # Loop through all profile pictures, deleting them if they exist
    # If any are on the current page, they'll be re-added in that path.
    for i in range(len(rows)):
        os.remove(f"static/{get_profile_picture(rows[i][1])}")
def delete_post_files():  # For cleanup. Deletes Post images from static/ when not in use.
    # Get each username to delete profile pics from
    sql = "SELECT * FROM 'tUsers'"
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    c = cursor.execute(sql)
    rows = c.fetchall()
    db.close()
    # Loop through each username
    for i in range(len(rows)):
        # Select posts from that username
        sql = f'SELECT PostName FROM tPosts WHERE [Username] = "{rows[i][1]}"'
        DATABASE = "database.db"
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        c = cursor.execute(sql)
        files = c.fetchall()
        db.close()
        # Loop through files
        for f in range(len(files)):
            # Convert files from tuple to string
            file = str(files[f]).strip("(' ',)")
            try:
                os.remove(f"static/{file}_{rows[i][1]}.jpg")  # If file exists, make it not exist
            except:
                print("File does not exist")  # If file doesn't exist, good.
def get_profile_picture(username):  # Gets the profile picture for each account
    # Connect to the database
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
def execute_sql(sql, val):  # Unused but here as a reference template for sql executions

    """This function commits sql changes to the database."""
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    if val != ():
        cursor.execute(sql, val)
        db.commit()
    else:
        cursor.execute(sql)
        db.commit()
# Define the app
app = Flask(__name__)

# Secret key because society
app.secret_key = 'beans on toast'
# Home route
@app.route('/', methods=("GET", "POST"))
def home():
    if request.method == 'POST':  # If we want to search for something
        delete_post_files()  # Remove the posts
        delete_image_files()  # Remove the profile pictures
        search_term = request.form['search']  # Get search term (ID of dictionary)
        # Find the correct search term from user table
        sql = f"SELECT * FROM 'tUsers' WHERE [Username] = '{search_term}'"
        DATABASE = "database.db"
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        c = cursor.execute(sql)
        rows = c.fetchall()
        db.close()
        try:  # If we have results, put them through
            row_true = rows[0]
            profile_pic = get_profile_picture(row_true[1])
            # Return the combo view page
            return render_template('results.html', search_term=search_term, rows=rows, profile_pic=profile_pic, results=True,loggedIn = session["loggedIn"])
        except:  # If we don't have results, send through negative responses
            return render_template('results.html', results=False,loggedIn = session["loggedIn"])
    delete_post_files()  # Remove post files just in case
    # Grab top 3 accounts to display/idolize/etc.
    # Select all accounts
    sql = "SELECT * FROM 'tUsers'"
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    c = cursor.execute(sql) 
    rows = c.fetchall()
    db.close()

    # Sort function
    def sort_func(e):
        return e[4]
    # Sort the rows so the highest are at the front
    rows.sort(reverse=True, key=sort_func)
    print(len(rows))

    top1 = rows[0]
    top2 = rows[1]
    top3 = rows[2]
    # Get profile pics of top accounts
    prof1 = get_profile_picture(top1[1])
    prof2 = get_profile_picture(top2[1])
    prof3 = get_profile_picture(top3[1])

    sql = "SELECT * FROM 'tPosts'"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    c = cursor.execute(sql)
    posts = c.fetchall()
    db.close()

    # Sort function
    def sort_func(e):
        return e[4]
    # Sort the rows so the highest are at the front
    posts.sort(reverse=True, key=sort_func)
    topPost1 = return_image(posts[0][3], posts[0][1])
    topPost2 = return_image(posts[1][3], posts[1][1])
    topPost3 = return_image(posts[2][3], posts[2][1])
    # Check if we're logged in or not
    loggedIn = False
    try:
        if session['loggedin']:
            print(session['username'])
            loggedIn = True

    except:
        print("Nothing happens here")

    # Return the index page
    return render_template('index.html', loggedIn=loggedIn, top1=top1, top2=top2, top3=top3, prof1=prof1, prof2=prof2, prof3=prof3, topPost1=topPost1, topPost2=topPost2, topPost3=topPost3)  # Return index page
# Log In system
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    delete_image_files()  # Delete profile pics
    msg = ''
    if request.method == 'POST' and 'username' and 'password' and 'email' in request.form:  # AKA if all data is in its proper place
        # Set variables to the inputs
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Connect to the database
        DATABASE = "database.db"
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute(f'SELECT * FROM tUsers WHERE [Username] = "{username}"', )
        account = cursor.fetchone()
        if account:  # If the account is already in use
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):  # If email is invalid
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):  # If username has invalid letters
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:  # If the form's not filled out properly
            msg = 'Please fill out the form!'
        else:  # Everything is correct!
            image = get_default_image()  # get default profile image
            cursor.execute(f'INSERT INTO tUsers VALUES (NULL,"{username}","{password}","{email}",0,"{image}", "PUBLIC", "True", "")')  # add new account to database
            db.commit()
            msg = 'You have successfully registered !'
    # Return signup page
    return render_template('signup.html', msg=msg)
@app.route('/login', methods=['GET', 'POST'])
def login():
    delete_image_files()  # Delete old profile images
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:  # If inputs are correct
        # Set variables to inputs
        username = request.form['username']
        password = request.form['password']
        # connect to database
        DATABASE = "database.db"
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute(f'SELECT * FROM tUsers WHERE [Username] = "{username}" AND [Password] = "{password}"')
        account = cursor.fetchone()
        if account:  # if it exists, log in
            session['loggedin'] = True
            session['username'] = username
            msg = 'Logged in successfully !'
            # everything below is prep for the index page since we go there now
            sql = "SELECT * FROM 'tUsers'"
            DATABASE = "database.db"
            db = sqlite3.connect(DATABASE)
            cursor = db.cursor()
            c = cursor.execute(sql)
            rows = c.fetchall()
            db.close()

            def sort_func(e):
                return e[4]

            rows.sort(reverse=True, key=sort_func)
            top1 = rows[0]
            top2 = rows[1]
            top3 = rows[2]
            prof1 = get_profile_picture(top1[1])
            prof2 = get_profile_picture(top2[1])
            prof3 = get_profile_picture(top3[1])
            return render_template('index.html', msg=msg, top1=top1, top2=top2, top3=top3, prof1=prof1, prof2=prof2, prof3=prof3)
        else:  # If username/password is wrong/doesn't exist
            msg = 'Incorrect username / password !'
    # Return login page
    return render_template('login.html', msg=msg)
@app.route('/*')
def logout():
    # Remove everything
    session['loggedIn'] = False
    session.pop('id', None)
    session.pop('username', None)
    # Go to the home page
    return redirect(url_for('home'))
# User Pages & Posts
@app.route('/page/<username>', methods=['GET', 'POST'])
def userpage(username):
    delete_image_files()  # Remove all profile pics
    # Connect to database
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM tUsers WHERE [Username] = "{username}"')
    user = cursor.fetchone()
    profile_picture = get_profile_picture(user[1])  # Get user profile pic
    # Get all posts
    image = return_all_posts(username)
    # Check if logged in
    loggedIn = False
    try:
        if session['loggedin']:
            print(session['username'])
            loggedIn = True
    except:
        print("Nothing happens here")
    if loggedIn:
        loggedInUser = session['username']
        # Check if we're subscribed
        var = cursor.execute(f'SELECT * FROM tSubscriptions WHERE [Subscriber] = "{loggedInUser}" AND [To Which User] = "{username}"')
        db.commit()
        isSubscribed = var.fetchone()
        if isSubscribed is None:
            subscribed = False
        else:
            subscribed = True
        # The page we're going to is ours, so make sure we know that
    else:
        loggedInUser = "N/A"  # Page we're going to is not ours, so it doesn't matter whose it is
        subscribed = False  # Since there's no user, we can't be subscribed anyway

    # Return user page
    return render_template("userpage.html", username=user[1], followerCount=user[4], profile_picture=profile_picture, loggedIn=loggedIn, loggedInUser=loggedInUser, post=image, len=len(image), subscribed=subscribed)
@app.route('/subscribe/<username>', methods=['GET', 'POST'])
def subscribe(username):  # Serves as a reload of the userpage but adding the subscription
    # Check if logged in, for safety reasons
    loggedIn = False
    try:
        if session['loggedin']:
            print(session['username'])
            loggedIn = True
    except:
        print("Nothing happens here")
    if loggedIn:
        loggedInUser = session['username']  # We are logged in, so supply that to the database
    else:
        loggedInUser = "N/A"  # We are not logged in. This should never happen, but it would be funny if it did.
    # Connect to database
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    # Insert into subscriptions table
    cursor.execute(f'INSERT INTO tSubscriptions VALUES (NULL,"{loggedInUser}","{username}")')
    db.commit()
    # Get Follower count and convert from tuple to integer
    FollowerCount = cursor.execute(f"SELECT FollowerCount FROM tUsers WHERE Username = '{username}'")
    FollowerInt = int(str(FollowerCount.fetchone()).strip("( ),")) + 1
    # Update tUsers to add 1 to followerCount
    cursor.execute(f"UPDATE tUsers SET FollowerCount = {FollowerInt} WHERE Username = '{username}'")
    db.commit()
    db.close()
    print("Subscribed!")
    return redirect(url_for("userpage", username=username))
@app.route('/unsubscribe/<username>', methods=['GET', 'POST'])
def unsubscribe(username):  # Serves as a reload of the userpage but removing the subscription
    # Check if logged in, for safety reasons
    loggedIn = False
    try:
        if session['loggedin']:
            print(session['username'])
            loggedIn = True
    except:
        print("Nothing happens here")
    if loggedIn:
        loggedInUser = session['username']  # We are logged in, so supply that to the database
    else:
        loggedInUser = "N/A"  # We are not logged in. This should never happen, but it would be funny if it did.
    # Connect to database
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    # Remove from subscriptions table
    cursor.execute(f'DELETE FROM tSubscriptions WHERE Subscriber = "{loggedInUser}" AND [To Which User] = "{username}"')
    db.commit()
    # Get Follower count and convert from tuple to integer
    FollowerCount = cursor.execute(f"SELECT FollowerCount FROM tUsers WHERE Username = '{username}'")
    FollowerInt = int(str(FollowerCount.fetchone()).strip("( ),")) - 1
    # Update tUsers to remove 1 from followerCount
    cursor.execute(f"UPDATE tUsers SET FollowerCount = {FollowerInt} WHERE Username = '{username}'")
    db.commit()
    db.close()
    print("Subscribed!")
    return redirect(url_for("userpage", username=username))
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    delete_image_files()
    delete_post_files()
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    c = cursor.execute(f'SELECT [Content Filter] FROM tUsers WHERE [Username] = "{session["username"]}"')
    filter = str(c.fetchone()).strip("(' ',)")
    c = cursor.execute(f'SELECT [Privacy] FROM tUsers WHERE [Username] = "{session["username"]}"')
    privacy = str(c.fetchone()).strip("(' ',)")
    return render_template('settings.html', prechecked=filter, privacy=privacy)
@app.route('/newpost', methods=['GET', 'POST'])
def add_post():
    delete_image_files()
    delete_post_files()
    return render_template('addpost.html', loggedIn = session['loggedIn'])
@app.route('/uploader', methods=['GET', 'POST'])
def reload_settings():
    if request.method == 'POST':
        DATABASE = "database.db"
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        if request.form['username']:
            uname = request.form['username']
            cursor.execute(
                f'UPDATE tUsers SET [Username] = "{uname}" WHERE Username = "{session["username"]}"')
            session['username'] = uname
        if request.form['email']:
            email = request.form['email']
            cursor.execute(
                f'UPDATE tUsers SET [Email] = "{email}" WHERE Username = "{session["username"]}"')
        if request.form['password']:
            pword = request.form['password']
            cursor.execute(f'UPDATE tUsers SET [Password] = "{pword}" WHERE Username = "{session["username"]}"')

        if 'filter' not in request.form:
            filter = False
        else:
            filter = True
        cursor.execute(
            f'UPDATE tUsers SET [Content Filter] = "{filter}" WHERE Username = "{session["username"]}"')
        if request.form['privacy']:
            privacy = request.form['privacy']
            cursor.execute(
                f'UPDATE tUsers SET [Privacy] = "{privacy}" WHERE Username = "{session["username"]}"')
        if request.form['bio']:
            bio = request.form['bio']
            cursor.execute(
                f'UPDATE tUsers SET [Bio] = "{bio}" WHERE Username = "{session["username"]}"')
        if request.files['file']:
            file = request.files['file']
            file.save(f"static/temp_image.jpg")
            with open('static/temp_image.jpg', 'rb') as f:
                # Convert to Base64 for easy transfer
                image_data = str(base64.b64encode(f.read()))
            os.remove("static/temp_image.jpg")
            cursor.execute(f'UPDATE tUsers SET [ProfileImage] = "{image_data}" WHERE Username = "{session["username"]}"')
        db.commit()
        return redirect(url_for("settings"))
@app.route('/poster', methods=['GET', 'POST'])
def new_post():
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    #PRETEND THiS POSTS ; CONTINUE WORKING LATER
    return redirect(url_for("userpage", username=session["username"]))
# Run the app
if __name__ == "__main__":
    app.run(port=8080, debug=True)

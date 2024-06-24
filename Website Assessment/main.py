from flask import Flask, render_template, request
import sqlite3
def execute_sql(sql,val):
    """This function commits sql changes to the database."""
    DATABASE = "U:\profile\Documents\Website Assessment\Website Assessment\database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    print("beans on toast")
    if val != ():
        cursor.execute(sql, val)
        db.commit()
    else:
        cursor.execute(sql)
        db.commit()
app = Flask(__name__)

# Home route
@app.route('/',methods=("GET", "POST"))
def home():
    temp = execute_sql("SELECT * FROM 'tUsers'",())
    return render_template('index.html',temp=temp)  # Return index page

@app.route('/signup')
def signup():
    return render_template('signup.html')
# Run the app
if __name__ == "__main__":
    app.run(port=8080, debug=True)
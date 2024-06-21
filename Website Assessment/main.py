from flask import Flask, render_template, request
import sqlite3

"""def execute_sql():
    DATABASE = "database.db"
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    print("beans on toast")
    if val != ():
        cursor.execute(sql, val)
        db.commit()
    else:
        cursor.execute(sql)
        db.commit()"""


app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return render_template('index.html')  # Return index page

# Run the app
if __name__ == "__main__":
    app.run(port=8080, debug=True)
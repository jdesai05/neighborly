from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Change if needed
app.config['MYSQL_PASSWORD'] = 'epichaibro'  # Change to your MySQL password
app.config['MYSQL_DB'] = 'neighborly'

# File Upload Configuration
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'xls', 'xlsx'}

mysql = MySQL(app)

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get form data
        society_name = request.form["society_name"]
        address = request.form["address"]
        city = request.form["city"]
        state = request.form["state"]
        pincode = request.form["pincode"]
        president = request.form["president"]
        secretary = request.form["secretary"]
        treasurer = request.form["treasurer"]
        contact = request.form["contact"]
        email = request.form["email"]

        # Handle file uploads
        bylaws_file = request.files["bylaws"]
        member_list_file = request.files["member_list"]
        registration_proof_file = request.files["registration_proof"]

        if bylaws_file and allowed_file(bylaws_file.filename):
            bylaws_filename = secure_filename(bylaws_file.filename)
            bylaws_path = os.path.join(app.config['UPLOAD_FOLDER'], bylaws_filename)
            bylaws_file.save(bylaws_path)
        else:
            return "Invalid bylaws file type!"

        if member_list_file and allowed_file(member_list_file.filename):
            member_list_filename = secure_filename(member_list_file.filename)
            member_list_path = os.path.join(app.config['UPLOAD_FOLDER'], member_list_filename)
            member_list_file.save(member_list_path)
        else:
            return "Invalid member list file type!"

        if registration_proof_file and allowed_file(registration_proof_file.filename):
            registration_proof_filename = secure_filename(registration_proof_file.filename)
            registration_proof_path = os.path.join(app.config['UPLOAD_FOLDER'], registration_proof_filename)
            registration_proof_file.save(registration_proof_path)
        else:
            return "Invalid registration proof file type!"

        # Insert into MySQL database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO housing_society (society_name, address, city, state, pincode, president, secretary, treasurer, contact, email, bylaws, member_list, registration_proof)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (society_name, address, city, state, pincode, president, secretary, treasurer, contact, email, bylaws_filename, member_list_filename, registration_proof_filename))

        mysql.connection.commit()
        cur.close()

        return "Registration Successful!"

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

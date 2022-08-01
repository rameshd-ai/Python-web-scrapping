import os
import csv

# from crypt import methods
import secrets
from flask import Flask, render_template, Response, redirect
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
from scrappy import runUrl

from forms import UploadFileForm, GenerateReportForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "ahh23h2vhvdhhjv1216722v"
app.config["UPLOAD_PATH"] = "static/files"
app.config["BASE_DIR"] = os.path.abspath(os.path.dirname(__file__))


"""--------------------------  CHANGE THE FOLLOWING VALUES ------------------------------"""
app.config["MYSQL_HOST"] = "localhost"  # localhost
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "wave_scrapping"

mysql = MySQL(app)


def add_new_file(file_name, path):
    if os.path.exists(path):
        i = 1
        while True:
            temp_path = path.split(".")
            temp_path = temp_path[0] + "_" + str(i) + "." + temp_path[1]

            temp_file_name = file_name.split(".")
            temp_file_name = temp_file_name[0] + "_" + str(i) + "." + temp_file_name[1]
            if not os.path.exists(temp_path):
                path = temp_path
                file_name = temp_file_name
                break
            i += 1

    return file_name, path


def read_csv_file(filename):
    with open(filename, newline="") as f:
        reader = csv.reader(f)
        data = list(reader)

    return data


def save_csv_file(file):

    file_name = secure_filename(file.filename)
    file_save_path = os.path.join(
        app.config["BASE_DIR"],
        app.config["UPLOAD_PATH"],
        file_name,
    )
    file_name, file_save_path = add_new_file(file_name, file_save_path)
    file.save(file_save_path)

    return file_name, file_save_path


def validate_csv(file):
    with open(file, "r") as csv:
        first_line = csv.readline()
        ncol = first_line.count(",") + 1
        if ncol > 1:
            return False
    return True


@app.route("/", methods=["GET", "POST"])
def home():
    form = UploadFileForm()
    cur = mysql.connection.cursor()

    error = None

    if form.validate_on_submit():
        file = form.file.data
        file_name, file_path = save_csv_file(file)
        data = read_csv_file(file_path)

        csv_is_valid = True

        if len(data[0]) > 1:
            csv_is_valid = False

        if csv_is_valid:
            for row in data:
                cur.execute(
                    "INSERT INTO web_url(fileName, web_urls, report_generated) values(%s, %s, %s)",
                    (
                        file_name,
                        row[0],
                        0,
                    ),
                )
                mysql.connection.commit()
        else:
            error = "The CSV file contains more than one column"
        # generate_report = True

    cur.execute(
        """ SELECT fileName, report_generated, deleted FROM web_url
            GROUP BY fileName, report_generated, deleted
            ORDER BY report_generated
        """
    )
    result = cur.fetchall()

    temp = []
    for row in result:
        temp_row = list(row)
        if str(row[1]) == "1":
            temp_row[1] = True
        elif str(row[1]) == "0":
            temp_row[1] = False

        if str(row[2]) == "1":
            temp_row[2] = True
        elif str(row[2]) == "0":
            temp_row[2] = False
        temp.append(temp_row)

    result = temp
    cur.close()

    return render_template(
        "home.html",
        form=form,
        result=result,
        length=len(result),
        error=error,
    )


@app.route("/delete/<file_name>/")
def delete(file_name):
    cur = mysql.connection.cursor()
    cur.execute(
        """
            DELETE FROM scrapping_data
            WHERE fileName = %s;
        """,
        (file_name,),
    )
    mysql.connection.commit()
    cur.execute("UPDATE web_url SET deleted=1 WHERE fileName=%s", (file_name,))

    mysql.connection.commit()
    cur.close()
    return redirect("/")


@app.route("/generate_report/<file_name>/")
def generate_report(file_name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT web_urls FROM web_url WHERE fileName=%s", (file_name,))

    urls = cur.fetchall()
    urls = [u[0] for u in urls]

    for url in urls:
        sql_stmt = runUrl(url, file_name)
        cur.execute(sql_stmt)

    mysql.connection.commit()

    cur.execute("UPDATE web_url SET report_generated=1 WHERE fileName=%s", (file_name,))

    mysql.connection.commit()
    cur.close()

    return redirect("/")


@app.route("/download_csv/<file_name>/")
def download_csv(file_name):
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
    # csv = read_csv_file(file_name)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM scrapping_data WHERE fileName=%s", (file_name,))
    column_names = [i[0] for i in cur.description]
    rows = cur.fetchall()

    csv = ""
    for col in column_names:
        csv += col + ","
    csv = csv[:-1]
    csv += "\n"

    for row in rows:
        csv += ",".join([str(r) for r in row])
        csv += "\n"

    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={file_name}"},
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

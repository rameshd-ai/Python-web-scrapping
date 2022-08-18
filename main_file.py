import os
import csv

import secrets
from flask import Flask, render_template, Response, redirect
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
from scrappy import runUrl

from forms import UploadFileForm, ChangeWaitTimeForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "safe_key"
app.config["UPLOAD_PATH"] = "static/files"
app.config["BASE_DIR"] = os.path.abspath(os.path.dirname(__file__))


"""--------------------------  CHANGE THE FOLLOWING VALUES ------------------------------"""
app.config["MYSQL_HOST"] = "localhost"  # localhost
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "scraper"

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


def failed_urls(file_name):

    cur = mysql.connection.cursor()
    cur.execute(
        """
            SELECT id, web_url, critical_error, contrast_error FROM scrapping_data
            WHERE fileName = %s
        """,
        (file_name,),
    )

    result = []

    for row in cur.fetchall():
        if row[2] == "?" or row[3] == "?":
            result.append((row[0], row[1]))

    return result


def get_wait_time():
    cur = mysql.connection.cursor()

    cur.execute(
        """
            SELECT wait_time FROM utilities
        """
    )

    wait_time = cur.fetchone()
    if wait_time is not None:
        return wait_time[0]
    else:
        cur.execute(
            """
                INSERT INTO utilities (wait_time) VALUES (40)
            """
        )
        mysql.connection.commit()
        return 40


@app.route("/change_wait_time/<int:wait_time>/")
def change_wait_time(wait_time):

    form = ChangeWaitTimeForm()
    cur = mysql.connection.cursor()

    error = None

    if form.validate_on_submit():
        wait_time = form.wait_time
        cur.execute("UPDATE utilities SET wait_time = %s", (wait_time,))


@app.route("/", methods=["GET", "POST"])
def home():
    form = UploadFileForm()
    cur = mysql.connection.cursor()

    error = None

    wait_time_form = ChangeWaitTimeForm()

    if wait_time_form.validate_on_submit():
        wait_time = wait_time_form.wait_time.data
        cur.execute("UPDATE utilities SET wait_time = %s", (wait_time,))
        mysql.connection.commit()

    current_wait_time = get_wait_time()

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
        """ SELECT fileName, report_generated, deleted, max_wait_time FROM web_url
            GROUP BY fileName, report_generated, deleted, max_wait_time
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

        count_failed_urls = len(failed_urls(temp_row[0]))
        temp_row.append(count_failed_urls)

        temp.append(temp_row)

    result = temp
    cur.close()

    return render_template(
        "home.html",
        form=form,
        wait_time_form=wait_time_form,
        current_wait_time=current_wait_time,
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


@app.route("/generate_report_for_failed_urls/<file_name>/")
def generate_report_for_failed_urls(file_name):
    cur = mysql.connection.cursor()

    urls = failed_urls(file_name)

    wait_time = get_wait_time()

    for url in urls:
        sql_stmts = runUrl(url[1], file_name, wait_time)
        for stmt in sql_stmts:
            cur.execute(stmt)
            mysql.connection.commit()

    max_wait_time = get_wait_time()
    cur.execute("UPDATE web_url SET report_generated=1 WHERE fileName=%s", (file_name,))

    cur.execute(
        "UPDATE web_url SET deleted=0, max_wait_time=GREATEST(%s, max_wait_time) WHERE fileName=%s",
        (
            max_wait_time,
            file_name,
        ),
    )

    [cur.execute("DELETE FROM scrapping_data WHERE id=%s", (row[0],)) for row in urls]
    mysql.connection.commit()
    cur.close()

    return redirect("/")


@app.route("/generate_report/<file_name>/")
def generate_report(file_name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT web_urls FROM web_url WHERE fileName=%s AND report_generated=%s", (file_name,0,))

    urls = cur.fetchall()
    urls = [u[0] for u in urls]

    wait_time = get_wait_time()

    for url in urls:
        sql_stmts = runUrl(url, file_name, wait_time)
        for stmt in sql_stmts:
            cur.execute(stmt)
            max_wait_time = get_wait_time()
            cur.execute("UPDATE web_url SET report_generated=1 WHERE fileName=%s AND web_urls=%s", (file_name,url,))
            cur.execute(
                "UPDATE web_url SET deleted=0, max_wait_time=%s WHERE fileName=%s AND web_urls=%s",
                (
                    max_wait_time,
                    file_name,
                    url,
                ),
            )
            mysql.connection.commit()



    mysql.connection.commit()
    cur.close()

    return redirect("/")


@app.route("/download_csv/<file_name>/")
def download_csv(file_name):
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
    # csv = read_csv_file(file_name)
    cur = mysql.connection.cursor()
    cur.execute("SELECT web_url,critical_error,contrast_error,report_link,created_at,critical_error_details FROM scrapping_data WHERE fileName=%s", (file_name,))
    column_names = [i[0] for i in cur.description]
    rows = cur.fetchall()

    print(rows)

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
        mimetype="text/xlsx",
        headers={"Content-disposition": f"attachment; filename={file_name}"},
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)

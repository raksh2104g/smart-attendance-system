import csv
import os
from flask import Flask, render_template, request, redirect, send_from_directory

from collections import defaultdict
from datetime import datetime
app = Flask(__name__)

# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html")


# ================= ADMIN LOGIN =================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin_id = request.form.get("admin_id")
        password = request.form.get("password")

        if admin_id == "admin" and password == "admin123":
            return redirect("/admin-dashboard")

        return render_template("admin_login.html", error="Invalid Admin Credentials")

    return render_template("admin_login.html")


@app.route("/admin")
def admin_redirect():
    return redirect("/admin-login")


# ================= ADMIN DASHBOARD =================
@app.route("/admin-dashboard")
def admin_dashboard():
    attendance = []
    student_map = {}

    # ---- Student Map ----
    with open("data/students.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            student_map[str(r["student_id"]).strip()] = r["name"]

    # ---- Attendance ----
    if os.path.exists("attendance"):
        files = sorted(os.listdir("attendance"))
        if files:
            latest = files[-1]

            with open(f"attendance/{latest}", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sid = str(row.get("Student ID", "")).strip()

                    attendance.append({
    "student_id": sid,
    "name": student_map.get(sid, "Unknown"),
    "time": row.get("Time") or row.get("time") or "",
    "status": (
        row.get("Status")
        or row.get("status")
        or row.get("STATUS")
        or ""
    )
})


    return render_template("admin_dashboard.html", attendance=attendance)





@app.route("/admin/attendance-history")
def attendance_history():
    daily_stats = []

    if os.path.exists("attendance"):
        for file in sorted(os.listdir("attendance")):
            present = 0
            total = 0

            with open(f"attendance/{file}", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    total += 1
                    status = r.get("Status") or r.get("status") or ""
                    if status.lower() == "present":
                        present += 1

            daily_stats.append({
                "date": file,
                "present": present,
                "absent": total - present
            })

    return render_template(
        "admin_attendance_history.html",
        stats=daily_stats
    )







@app.route("/admin/attendance-stats")
def attendance_stats():
    stats = {}

    if os.path.exists("attendance"):
        for file in os.listdir("attendance"):
            present = 0
            absent = 0

            with open(f"attendance/{file}", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    status = row.get("Status", "").lower()

                    if status == "present":
                        present += 1
                    else:
                        absent += 1

            stats[file] = {
                "present": present,
                "absent": absent
            }

    return stats




# ================= ADMIN ADD STUDENT =================
@app.route("/admin/add-student", methods=["GET", "POST"])
def admin_add_student():
    if request.method == "POST":
        with open("data/students.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                request.form.get("student_id"),
                request.form.get("name"),
                request.form.get("father_name"),
                request.form.get("mother_name"),
                request.form.get("address"),
                request.form.get("mobile"),
                request.form.get("course"),
                request.form.get("semester"),
                request.form.get("college")
            ])
        return redirect("/admin/add-student")

    return render_template("admin_add_student.html")


# ================= ADMIN VIEW STUDENTS =================
@app.route("/admin/view-students")
def admin_view_students():
    students = []

    if os.path.exists("data/students.csv"):
        with open("data/students.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            students = list(reader)

    return render_template("admin_view_students.html", students=students)


# ================= START ATTENDANCE =================
@app.route("/start-attendance")
def start_attendance():
    os.system("python recognize_attendance.py")
    return "Attendance Started <br><a href='/admin-dashboard'>Back</a>"


# ================= VIEW ATTENDANCE FILES =================
@app.route("/admin/view-attendance")
def admin_view_attendance():
    files = []
    if os.path.exists("attendance"):
        files = os.listdir("attendance")
    return render_template("admin_view_attendance.html", files=files)


@app.route("/attendance/<filename>")
def attendance_file(filename):
    return send_from_directory("attendance", filename)


# ================= STUDENT LOGIN =================
@app.route("/student-login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        student_id = request.form.get("student_id")
        mobile = request.form.get("mobile")

        with open("data/students.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r["student_id"] == student_id and r["mobile"] == mobile:
                    return redirect(f"/student/{student_id}")

        return render_template("student_login.html", error="Invalid Credentials")

    return render_template("student_login.html")


# ================= STUDENT DASHBOARD =================
@app.route("/student/<student_id>")
def student_dashboard(student_id):
    with open("data/students.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["student_id"] == student_id:
                return render_template("student_dashboard.html", student=r)

    return "Student not found"


# ================= STUDENT ATTENDANCE =================
@app.route("/student/attendance/<student_id>")
def student_attendance(student_id):
    records = []

    if os.path.exists("attendance"):
        for file in os.listdir("attendance"):
            with open(f"attendance/{file}", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("Student ID") == student_id:
                        records.append({
                            "date": file,
                            "time": row.get("Time"),
                            "status": row.get("Status")
                        })

    return render_template(
        "student_attendance.html",
        records=records,
        student_id=student_id
    )


# ================= STUDENT SCORE =================


@app.route("/student/score/<student_id>")
def student_score(student_id):
    monthly = defaultdict(int)
    total = 0
    attended = 0

    if os.path.exists("attendance"):
        for file in os.listdir("attendance"):
            if not file.endswith(".csv"):
                continue

            # 👉 filename se month nikalna (safe)
            try:
                date = datetime.strptime(
                    file.replace("attendance_", "").replace(".csv", ""),
                    "%Y-%m-%d"
                )
                month = date.strftime("%b")
            except:
                continue

            total += 1

            with open(f"attendance/{file}", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("Student ID") == student_id and row.get("Status") == "Present":
                        attended += 1
                        monthly[month] += 1

    percent = round((attended * 100) / total, 2) if total else 0

    return render_template(
        "student_score.html",
        student_id=student_id,
        total=total,
        attended=attended,
        percent=percent,
        months=list(monthly.keys()),
        values=list(monthly.values())
    )


# ================= FACE CAPTURE =================
@app.route("/capture-face")
def capture_face():
    os.system("python dataset_creator.py")
    return "Face Capture Started <br><a href='/admin-dashboard'>Back</a>"





@app.route("/test-profile")
def test_profile():
    return "PROFILE ROUTE WORKING"





@app.route("/student/profile/<student_id>")
def student_profile(student_id):
    import csv
    with open("data/students.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["student_id"] == student_id:
                return render_template("student_profile.html", student=r)

    return "Student not found"









@app.route("/admin/delete-student/<student_id>")
def delete_student(student_id):
    students = []

    with open("data/students.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["student_id"] != student_id:
                students.append(r)

    with open("data/students.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=students[0].keys())
        writer.writeheader()
        writer.writerows(students)

    return redirect("/admin/view-students")







@app.route("/admin/edit-student/<student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    students = []
    target = None

    with open("data/students.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["student_id"] == student_id:
                target = r
            students.append(r)

    if request.method == "POST":
        for r in students:
            if r["student_id"] == student_id:
                r["name"] = request.form["name"]
                r["mobile"] = request.form["mobile"]
                r["course"] = request.form["course"]
                r["semester"] = request.form["semester"]
                r["college"] = request.form["college"]

        with open("data/students.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=students[0].keys())
            writer.writeheader()
            writer.writerows(students)

        return redirect("/admin/view-students")

    return render_template("admin_edit_student.html", student=target)


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)





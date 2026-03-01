import cv2
import yaml
import csv
import os
from datetime import datetime, date

# ================= LOAD TRAINED DATA =================
with open("trainer/trainer.yml", "rb") as f:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trainer/trainer.yml")

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ================= DATE & FILE SETUP =================
today = date.today().strftime("%Y-%m-%d")
attendance_file = f"attendance/attendance_{today}.csv"

os.makedirs("attendance", exist_ok=True)

already_marked = set()

# ---------- Load already marked students ----------
if os.path.exists(attendance_file):
    with open(attendance_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            already_marked.add(r["Student ID"])

# ================= CAMERA =================
cap = cv2.VideoCapture(0)

print("[INFO] Camera started. Press Q to stop.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face_img = gray[y:y+h, x:x+w]
        id_, confidence = recognizer.predict(face_img)

        # -------- CONFIDENCE CHECK --------
        if confidence < 70:
            student_id = str(id_)

            # -------- ONLY ONCE PER DAY --------
            if student_id not in already_marked:
                time_now = datetime.now().strftime("%H:%M:%S")

                file_exists = os.path.exists(attendance_file)

                with open(attendance_file, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(["Student ID", "Time", "Status"])

                    writer.writerow([student_id, time_now, "Present"])

                already_marked.add(student_id)
                print(f"[MARKED] Student {student_id} at {time_now}")

            label = f"ID: {student_id}"
            color = (0, 255, 0)

        else:
            label = "Unknown"
            color = (0, 0, 255)

        cv2.rectangle(frame, (x,y), (x+w,y+h), color, 2)
        cv2.putText(frame, label, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow("Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ================= CLEANUP =================
cap.release()
cv2.destroyAllWindows()

print("[INFO] Attendance process stopped.")

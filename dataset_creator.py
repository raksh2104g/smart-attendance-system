
import cv2
import os

if not os.path.exists("dataset"):
    os.makedirs("dataset")

face_detector = cv2.CascadeClassifier(
    "haarcascade/haarcascade_frontalface_default.xml"
)

cam = cv2.VideoCapture(0)
face_id = input("Enter Numeric User ID: ")
count = 0

while True:
    ret, img = cam.read()
    if not ret:
        print("Camera not working")
        break

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        count += 1
        cv2.imwrite(
            f"dataset/User.{face_id}.{count}.jpg",
            gray[y:y+h, x:x+w]
        )
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

    cv2.imshow("Dataset Creator", img)

    if cv2.waitKey(1) & 0xFF == ord('q') or count >= 50:
        break

cam.release()
cv2.destroyAllWindows()

print("Dataset creation completed")

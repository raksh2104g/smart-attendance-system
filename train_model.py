import cv2
import numpy as np
import os
from PIL import Image

dataset_path = "dataset"
trainer_path = "trainer"

if not os.path.exists(trainer_path):
    os.makedirs(trainer_path)

recognizer = cv2.face.LBPHFaceRecognizer_create()
face_detector = cv2.CascadeClassifier(
    "haarcascade/haarcascade_frontalface_default.xml"
)

def get_images_and_labels(path):
    face_samples = []
    ids = []

    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    for image_path in image_paths:
        if not image_path.endswith(".jpg"):
            continue

        img = Image.open(image_path).convert('L')
        img_np = np.array(img, 'uint8')

        # filename: user.<id>.<count>.jpg
        id_ = int(os.path.split(image_path)[-1].split(".")[1])

        faces = face_detector.detectMultiScale(img_np)
        for (x, y, w, h) in faces:
            face_samples.append(img_np[y:y+h, x:x+w])
            ids.append(id_)

    return face_samples, ids

faces, ids = get_images_and_labels(dataset_path)

if len(faces) == 0:
    print("❌ No faces found. Training aborted.")
else:
    recognizer.train(faces, np.array(ids))
    recognizer.save(os.path.join(trainer_path, "trainer.yml"))
    print("✅ Training completed. Model saved at trainer/trainer.yml")

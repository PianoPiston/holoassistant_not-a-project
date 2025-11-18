import cv2
import mediapipe as mp
import threading

class FaceTracker:
    def __init__(self):
        self.nose_x = 0.5   # default (center)
        self.nose_y = 0.5
        self.running = True

        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        mp_face = mp.solutions.face_mesh
        mp_draw = mp.solutions.drawing_utils
        face_mesh = mp_face.FaceMesh(static_image_mode=False,
                                     max_num_faces=1,
                                     refine_landmarks=True,
                                     min_detection_confidence=0.5,
                                     min_tracking_confidence=0.5)

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = face_mesh.process(rgb)

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                nose = face_landmarks.landmark[1]

                # Store normalized nose position
                self.nose_x = nose.x
                self.nose_y = nose.y

        cap.release()

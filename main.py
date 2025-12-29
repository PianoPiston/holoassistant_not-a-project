from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from math import sin, cos, radians
from tracker import FaceTracker
from math import sin, cos, radians
from talkassistant import VoiceAgent ## added
import threading ## added

# the code will load a panda model, track the user's nose position via camera in another thread
# then compute the model's center (as a node) and radius to position the camera at a good distance,
# and then it will move the camera around the node based on nose position with some trigonometry

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.tracker = FaceTracker()
        self.voice_agent = VoiceAgent("test api key commit") ## added

        # Load Panda model
        self.panda = self.loader.loadModel("panda")
        self.panda.reparentTo(self.render)
        self.panda.setScale(0.3)
        self.panda.setPos(0, 0, 0)
        self.panda.setH(180)   # orient model to face camera
        self.setBackgroundColor(0, 0, 0)
        
        # --- Compute model bounds and center (in world / render coordinates) ---
        # getTightBounds(relativeTo) gives (minPoint, maxPoint) in coordinates of 'relativeTo'.
        min_pt, max_pt = self.panda.getTightBounds(self.render)
        if min_pt is None or max_pt is None:
            # fallback if bounds cannot be computed
            min_pt = Point3(0, 0, 0)
            max_pt = Point3(0, 0, 1)

        # world-space center of the model
        self.model_center = (min_pt + max_pt) * 0.5

        # model "radius" (half of bounding box diagonal)
        bbox_diag = (max_pt - min_pt).length()
        self.model_radius = bbox_diag * 0.5

        # choose camera distance as a multiple of model_radius
        self.camera_distance = max(5.0, self.model_radius * 3.5)

        self.center_node = self.render.attachNewNode("model_center")
        self.center_node.setPos(self.model_center)

        self.camera.setPos(self.model_center + (0, -self.camera_distance, 0))
        self.camera.lookAt(self.model_center)

        # Add update task
        self.taskMgr.add(self.update_camera, "UpdateCameraTask")
        self.voice_thread = threading.Thread(target=self.voice_agent.start_loop, daemon=True) 
        self.voice_thread.start() ## added## added

    def servo_x(self, direction):
        if direction == "right":
            print(f"Servo X moved {direction}")
        if direction == "left":
            print(f"Servo X moved {direction}")

    def servo_y(self, direction):
        if direction == "up":
            print(f"Servo Y moved {direction}")
        if direction == "down":
            print(f"Servo Y moved {direction}")

    def update_camera(self, task):
        # read normalized nose coords 0..1
        nx = self.tracker.nose_x
        ny = self.tracker.nose_y

        # ----- MAPPINGS -----
        # Horizontal: (0..1) -> -90..+90 degrees where right movement -> positive yaw
        orbit_h_deg = (0.5 - nx) * 180.0   # tweak scale if you want smaller range

        # Vertical: (0..1) -> -90..+90 degrees (tilt up/down)
        orbit_v_deg = (0.5 - ny) * 180.0    # vertical tilt range, bigger = stronger tilt

        # Convert to radians
        h = radians(orbit_h_deg)
        v = radians(orbit_v_deg)

        # Spherical direction vector where:
        #  - h is heading around vertical axis (yaw)
        #  - v is elevation above horizontal (pitch)
        # Use cos(v) for horizontal projection
        dir_x = sin(h) * cos(v)
        dir_y = cos(h) * cos(v)
        dir_z = sin(v)

        if nx >= 0.9:
            self.servo_x("right")
        if nx <= 0.1:
            self.servo_x("left")
        if ny >= 0.9:
            self.servo_y("up")
        if ny <= 0.1:   
            self.servo_y("down")

        # Camera world position = center + direction * distance
        cam_offset = Vec3(dir_x, dir_y, dir_z) * self.camera_distance
        cam_pos_world = self.model_center + cam_offset

        self.camera.setPos(cam_pos_world)
        self.camera.lookAt(self.model_center)

        return task.cont


app = MyApp()
app.run()

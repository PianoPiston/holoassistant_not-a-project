from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from math import sin, cos, radians
from tracker import FaceTracker
from math import sin, cos, radians
from talkassistant import VoiceAgent ## added
import threading ## added
import pigpio
import time

# testing code

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.tracker = FaceTracker()
        self.voice_agent = VoiceAgent("AIzaSyCqUdgFeN6Ft20NLGvJ7-BK2rgk-OXZBX8_asdfasdf") ## added

        # Load Panda model
        self.panda = self.loader.loadModel("Car")
        self.panda.reparentTo(self.render)
        self.panda.setScale(0.1) #0.3
        self.panda.setPos(0, 0, 0)
        # self.panda.setH(180)   # orient model to face camera
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

        # choose camera distance as a multiple of model_radius (tweak factor for taste)
        self.camera_distance = max(5.0, self.model_radius * 3.5)

        # Optionally create a node at center if you want to reference it
        self.center_node = self.render.attachNewNode("model_center")
        self.center_node.setPos(self.model_center)

        # initial camera placement (so there's no flash)
        self.camera.setPos(self.model_center + (0, -self.camera_distance, 0))
        self.camera.lookAt(self.model_center)

        # Add update task
        self.taskMgr.add(self.update_camera, "UpdateCameraTask")
        
        self.voice_thread = threading.Thread(target=self.voice_agent.start_loop, daemon=True) 
        self.voice_thread.start() ## added## added

        self.SERVO_PIN = 21        
        self.init_servo()    
        
    def init_servo(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpio daemon not running")

        self.pi.set_mode(self.SERVO_PIN, pigpio.OUTPUT)
        self.current_servo_angle = 90
        self.set_servo_angle(90)


    def set_servo_angle(self, angle):
        angle = max(0, min(180, angle))
        pulse = int(500 + (angle / 180) * 2000)
        self.pi.set_servo_pulsewidth(self.SERVO_PIN, pulse)
        self.current_servo_angle = angle

    def update_servo_from_face(self, nx):
        target = int(90 + (nx - 0.5) * 90)
        step = 2
        # Only move if the difference is significant
        if abs(target - self.current_servo_angle) >= step:
            if target > self.current_servo_angle:
                new_angle = self.current_servo_angle + step
            # FIX: Original code's logic was broken here.
            # This ensures it moves left if the target is lower.
            elif target < self.current_servo_angle: 
                new_angle = self.current_servo_angle - step
            else: # Should be caught by abs() check, but good safety.
                return 

            self.set_servo_angle(new_angle)

    def servo_x(self, direction):
        step = 10

        if direction == "right":
            new_angle = self.current_servo_angle + step
            print("Moving RIGHT")
            self.set_servo_angle(new_angle)

        elif direction == "left":
            new_angle = self.current_servo_angle - step
            print("Moving LEFT")
            self.set_servo_angle(new_angle)

    def servo_y(self, direction):
        step = 10

        if direction == "up":
            print(f"Servo Y moved {direction}")
        if direction == "down":
            print(f"Servo Y moved {direction}")
            

    def update_camera(self, task):
        # read normalized nose coords 0..1
        nx = self.tracker.nose_x
        ny = self.tracker.nose_y

        #calls the servo
        # self.update_servo_from_face(nx)

        # ----- MAPPINGS -----
        # Horizontal: (0..1) -> -90..+90 degrees where right movement -> positive yaw
        orbit_h_deg = (nx - 0.5) * 90.0   # tweak scale if you want smaller range

        # Vertical: (0..1) -> -90..+90 degrees (tilt up/down)
        orbit_v_deg = (0.5 - ny) * 90.0    # vertical tilt range, bigger = stronger tilt

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

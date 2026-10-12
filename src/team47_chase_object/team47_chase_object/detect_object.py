#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
import cv2
import numpy as np
import math

class DetectObjectNode(Node):
    def __init__(self):
        super().__init__('detect_object')
        self.bridge = CvBridge()
        self.image_sub = self.create_subscription(Image, '/image_raw', self.image_callback, qos_profile_sensor_data)
        self.bearing_pub = self.create_publisher(Point, '/object_bearing', 10)
        self.get_logger().info("Detect Object Node started.")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"Camera crash: {e}")
            return

        height, width = frame.shape[:2]
        hsv = cv2.cvtColor(cv2.GaussianBlur(frame, (11, 11), 0), cv2.COLOR_BGR2HSV)

        # Red thresholds
        mask1 = cv2.inRange(hsv, np.array([0, 100, 50]), np.array([10, 255, 255]))
        mask2 = cv2.inRange(hsv, np.array([165, 100, 50]), np.array([179, 255, 255]))
        red_mask = cv2.morphologyEx(cv2.bitwise_or(mask1, mask2), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 500:
                M = cv2.moments(largest)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    
                    # Pixel to angle (FOV = 62.5 degrees)
                    fov_rad = math.radians(62.5)
                    angle_rad = ((width / 2.0) - cx) * (fov_rad / width)
                    
                    point_msg = Point()
                    point_msg.x = float(angle_rad)
                    self.bearing_pub.publish(point_msg)
                    return

        # No valid object was found 
        point_msg = Point()
        point_msg.x = 999.0 
        self.bearing_pub.publish(point_msg)

def main():
    rclpy.init()
    rclpy.spin(DetectObjectNode())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
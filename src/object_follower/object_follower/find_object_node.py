#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
import cv2
import numpy as np

class FindObjectNode(Node):
    def __init__(self):
        super().__init__('find_object_node')
        
        # ROS images to OpenCV images
        self.bridge = CvBridge()
        
        # Subscribe to the robot's camera
        self.image_sub = self.create_subscription(
            Image, 
            '/image_raw', 
            self.image_callback, 
            qos_profile_sensor_data)
            
        # Publish the object's X, Y coordinates to the second node
        self.location_pub = self.create_publisher(Point, '/object_location', 10)
        
        self.get_logger().info("Find Object Node started. Waiting for /image_raw...")

    def image_callback(self, msg):
        # ROS Image message to OpenCV
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"Image conversion failed: {e}")
            return

        # Width of the camera frame
        height, width = frame.shape[:2]

        # Lab 1
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        lower_red1 = np.array([0, 100, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([165, 100, 50])
        upper_red2 = np.array([179, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(mask1, mask2)

        kernel = np.ones((5, 5), np.uint8)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_DILATE, kernel)

        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            if area > 500:
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # Publish the location
                    point_msg = Point()
                    point_msg.x = float(cx)
                    point_msg.y = float(cy)
                    
                    # use 'z' to pass the width to the second node
                    point_msg.z = float(width) 
                    
                    self.location_pub.publish(point_msg)

                    x, y, w, h = cv2.boundingRect(largest_contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

        cv2.imshow("Robot Camera View", frame)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = FindObjectNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
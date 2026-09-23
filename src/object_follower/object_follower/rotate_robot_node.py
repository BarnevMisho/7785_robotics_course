#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from geometry_msgs.msg import Twist

class RotateRobotNode(Node):
    def __init__(self):
        super().__init__('rotate_robot_node')
        
        self.loc_sub = self.create_subscription(
            Point, 
            '/object_location', 
            self.location_callback, 
            10)
            
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.kp = 0.01 # rotation speed
        
        # center calculated only once
        self.camera_center = None
        
        self.get_logger().info("Rotate Robot Node started. Waiting for target...")

    def location_callback(self, msg):
        target_x = msg.x
        
        # for the first message calculate the center
        if self.camera_center is None:
            camera_width = msg.z
            self.camera_center = camera_width / 2.0
            self.get_logger().info(f"Camera width detected as {camera_width}. Locked center at {self.camera_center}.")
        
        # Calculate error 
        error = self.camera_center - target_x 
        
        twist_msg = Twist()
        twist_msg.linear.x = 0.0 # only rotation
        twist_msg.angular.z = self.kp * error # rotation
        self.cmd_pub.publish(twist_msg)

def main(args=None):
    rclpy.init(args=args)
    node = RotateRobotNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
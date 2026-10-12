#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, Twist

class ChaseObjectNode(Node):
    def __init__(self):
        super().__init__('chase_object')
        self.range_sub = self.create_subscription(Point, '/object_range', self.range_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.kp_linear = 0.6
        self.kp_angular = 0.8
        self.target_distance = 0.25 
        
        self.get_logger().info("Chase Object Node started. Ready to hunt.")

    def range_callback(self, msg):
        twist_msg = Twist()
        
        # Brake if the target is lost
        if msg.x == 999.0:
            twist_msg.linear.x = 0.0
            twist_msg.angular.z = 0.0
            self.cmd_pub.publish(twist_msg)
            return

        current_distance = msg.x
        current_angle = msg.y
        
        linear_error = current_distance - self.target_distance
        angular_error = current_angle - 0.0 
        
        twist_msg.linear.x = self.kp_linear * linear_error
        twist_msg.angular.z = self.kp_angular * angular_error
        
        twist_msg.linear.x = max(min(twist_msg.linear.x, 0.2), -0.2)
        twist_msg.angular.z = max(min(twist_msg.angular.z, 0.5), -0.5)
        
        self.cmd_pub.publish(twist_msg)

def main():
    rclpy.init()
    rclpy.spin(ChaseObjectNode())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
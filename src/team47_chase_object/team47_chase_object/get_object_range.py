#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Point
from rclpy.qos import qos_profile_sensor_data
import math

class GetObjectRangeNode(Node):
    def __init__(self):
        super().__init__('get_object_range')
        self.target_angle_rad = 999.0
        
        self.bearing_sub = self.create_subscription(Point, '/object_bearing', self.bearing_callback, 10)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, qos_profile_sensor_data)
        self.range_pub = self.create_publisher(Point, '/object_range', 10)
        self.get_logger().info("Get Object Range Node started.")

    def bearing_callback(self, msg):
        self.target_angle_rad = msg.x

    # Broadcast a STOP
    def publish_stop_signal(self):
        out_msg = Point()
        out_msg.x = 999.0 
        out_msg.y = 0.0
        self.range_pub.publish(out_msg)

    def scan_callback(self, msg):
        if self.target_angle_rad == 999.0:
            self.publish_stop_signal()
            return 

        # LIDAR points for this frame  
        num_ranges = len(msg.ranges)
        if num_ranges == 0:
            return 
            
        rough_angle_deg = math.degrees(self.target_angle_rad)
        angle_min = int(rough_angle_deg - 10)
        angle_max = int(rough_angle_deg + 10)
        
        valid_points = [] 

        # Use the array length to wrap the angle
        for angle in range(angle_min, angle_max):
            wrapped_angle = angle % num_ranges
            dist = msg.ranges[wrapped_angle]
            if 0.1 < dist < 2.0: 
                valid_points.append((dist, angle))
                
        if len(valid_points) < 3:
            self.publish_stop_signal()
            return 
            
        valid_points.sort(key=lambda p: p[0])
        robust_min_dist = valid_points[2][0]
        object_cluster = [p for p in valid_points if p[0] <= robust_min_dist + 0.15]
        
        if not object_cluster:
            self.publish_stop_signal()
            return

        true_distance = sum(p[0] for p in object_cluster) / len(object_cluster)
        true_angle_deg = sum(p[1] for p in object_cluster) / len(object_cluster)
        
        out_msg = Point()
        out_msg.x = float(true_distance)
        out_msg.y = float(math.radians(true_angle_deg))
        self.range_pub.publish(out_msg)

def main():
    rclpy.init()
    rclpy.spin(GetObjectRangeNode())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
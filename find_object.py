#!/usr/bin/env python3
"""
Lab 1: Object Following - find_object.py
Partner 1: Mihail Barnev
Partner 2: Yanbo Jin
"""

import cv2
import numpy as np

# Minimum size required to qualify as the tracked object
MIN_AREA_THRESHOLD = 500

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Tracking red object... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Smooth and convert to HSV
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # HSV thresholds for Red
    lower_red1 = np.array([0, 100, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([165, 100, 50])
    upper_red2 = np.array([179, 255, 255])

    # Mask
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # Mask opening and closing
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_DILATE, kernel)

    # Find contours in mask
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Pick the largest
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)

        if area > MIN_AREA_THRESHOLD:
            # pixel location
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                print(f"Object Center: X={cx}, Y={cy} | Area={int(area)}")

                # Annotate with bounding box and marker
                x, y, w, h = cv2.boundingRect(largest_contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

                coord_text = f"({cx}, {cy})"
                cv2.putText(frame, coord_text, (cx + 10, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Display  
    cv2.imshow("Object Tracker", frame)
    cv2.imshow("Mask", red_mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
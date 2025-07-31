import math

def calculate_distance(p1, p2):
    x1, y1 = p1[1], p1[2]
    x2, y2 = p2[1], p2[2]
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def is_valid_hand_distance(landmarks, min_thresh=10, max_thresh=300):
    if len(landmarks) < 5:
        return False
    dist = calculate_distance(landmarks[0], landmarks[4]) 
    return min_thresh < dist < max_thresh

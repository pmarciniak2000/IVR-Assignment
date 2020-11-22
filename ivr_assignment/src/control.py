#!/usr/bin/env python
from __future__ import print_function

import sys
import rospy
import cv2
import numpy as np
from std_msgs.msg import Float64MultiArray


class control:

    # Defines publisher and subscriber
    def __init__(self):
        # initialize the node named forward_kinematics
        rospy.init_node('forward_kinematics', anonymous=True)
        # initialize a publisher to publish the end effector position calculated by FK
        self.end_effector_pub = rospy.Publisher("/end_effector_position", Float64MultiArray, queue_size=10)
        self.end_effector_position = Float64MultiArray()
        self.joints = np.array([0.1, 0.2, 0.3, 0.4]) #set this to the value of rostopic inputs to validate FK

    def fk_end_effector_estimate(self):
        
        end_effector = self.calculate_fk(self.joints)
        print("FK  x: {:.2f}, y: {:.2f}, z: {:.2f}".format(end_effector[0], end_effector[1], end_effector[2]), end='\r')
        self.end_effector_position.data = end_effector
        self.end_effector_pub.publish(self.end_effector_position)

    def calculate_fk(self, joints):
        s1 = np.sin(joints[0])
        s2 = np.sin(joints[1])
        s3 = np.sin(joints[2])
        s4 = np.sin(joints[3])
        c1 = np.cos(joints[0])
        c2 = np.cos(joints[1])
        c3 = np.cos(joints[2])
        c4 = np.cos(joints[3])
        
        x = (-c1 * s3 + s1 * s2 * c3) * (2 * c4 + 3) + 2 * s4 * (-s1 * s2 * s3 - c1 * c3)
        y = (-s1 * s3 - c1 * s2 * c3) * (2 * c4 + 3) + 2 * s4 * (-c1 * s2 * s3 + s1 * c3)
        z = c2 * c3 * (2 * c4 + 3) + 2 * (- s4 * c2 * s3 + 1)
        end_effector = np.array([x, y, z])
        
        return end_effector

    def calculate_jacobian(self, angles):
        # calc. Jacobian 
        pass

    def control_closed(self, angles):
        # gets list of initial joints [q1, q2, q3, q4] from somewhere?
        # returns joints angles [q1, q2, q3, q4]
        
        # P gain
        K_p = np.array([[1, 0, 0],
                        [0, 1, 0],
                        [0, 0, 1]])
        # D gain
        K_d = np.array([[0.1, 0, 0],
                        [0, 0.1, 0],
                        [0, 0, 0.1]])

        cur_time = rospy.get_time()
        dt = cur_time - self.time_previous
        self.time_previous = cur_time
        # get robot end-effector position using methods from img processing.py
        pos_end = 0
        # get target position using methods from img processing
        pos_target = 0
        # estimate derivative of error
        self.error_d = ((pos_target - pos_end) - self.error)/dt
        # estimate error
        self.error = pos_target - pos_end
        J_inv = np.linalg.pinv(self.calculate_jacobian(angles))  # calculate the psudeo inverse of Jacobian
        # angular velocity of joints
        dq_d = np.dot(J_inv, (np.dot(K_d, self.error_d.T) + np.dot(K_p, self.error.T)))
        # angular position of joints
        q_d = angles + (dt * dq_d)
        return q_d

# call the class
def main(args):
    control = control()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")
    cv2.destroyAllWindows()


# run the code if the node is called
if __name__ == '__main__':
    main(sys.argv)
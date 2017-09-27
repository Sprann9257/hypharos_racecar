#!/usr/bin/env python



import rospy
import time
import sys
import math
import serial
import string
from geometry_msgs.msg import Twist
from ackermann_msgs.msg import AckermannDriveStamped

class BaseControl:
    def __init__(self, baseId, device_port, baudrate):
        # Serial Communication
        try:
            self.serial = serial.Serial(device_port, baudrate, timeout=10)
	    rospy.loginfo("Communication success !")
	    # ROS handler        
            self.sub = rospy.Subscriber('/ackermann_cmd', AckermannDriveStamped, self.cmdCB, queue_size=10)  
            self.timer_cmd = rospy.Timer(rospy.Duration(0.1), self.timerCmdCB) # 10Hz
            self.baseId = baseId
            # variable        
            self.trans_x = 0.0
            self.rotat_z = 0.0
        except serial.serialutil.SerialException:
            rospy.logerr("Can not receive data from the port: "+device_port + 
            ". Did you specify the correct port in the launch file?")
            self.serial.close
            sys.exit(0) 

    def cmdCB(self, data):
        self.trans_x = data.drive.speed
	self.rotat_z = data.drive.steering_angle
    def timerCmdCB(self, event):
        # send cmd to motor
        self.turn = self.rotat_z#*180/3.1415926+90
        self.throttle = self.trans_x#*(-100)+1530
        values = [str(self.turn), str(self.throttle), '0']
        values[2] = str(len(values[0]) + len(values[1]))
        cmd = ",".join(values).encode()
	rospy.logerr(cmd)        
        self.serial.flushInput()
	self.serial.write(cmd)
if __name__ == "__main__":
    try:    
        # ROS Init    
        rospy.init_node('base_control', anonymous=True)

        # Get params
        baseId = rospy.get_param('~base_id', 'base_link') # base link
        device_port = rospy.get_param('~port', '/dev/uno') # device port
        baudrate = float( rospy.get_param('~baudrate', '57600') ) 
        # Constract BaseControl Obj
        rospy.loginfo("Start base control node ...")
        bc = BaseControl(baseId, device_port, baudrate)
        rospy.spin()
    except KeyboardInterrupt:
        bc.serial.close
    print("shutting down")

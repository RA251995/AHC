#!/usr/bin/python

import smbus
import math
import time
import sys

#Power Management Registers
power_mgmt_1 = 0x6B
power_mgmt_2 = 0x6C

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if val >= 0x8000:
        return -((65535 - val) + 1)
    else:
        return val

def dist(a, b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return -math.degrees(radians)

def get_x_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)

bus = smbus.SMBus(1)
address = 0x68

# Wake up 6050 as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)

angleX = 0.0
angleY = 0.0
prev_time = time.time()

while True:
#print "Gyro Data"
#print "---------"

    gyro_xout = read_word_2c(0x43)
    gyro_yout = read_word_2c(0x45)
    gyro_zout = read_word_2c(0x47)

#print "Gyro X: ", gyro_xout, " scaled: ", (gyro_xout/131)
#print "Gyro Y: ", gyro_yout, " scaled: ", (gyro_yout/131)
#print "Gyro Z: ", gyro_zout, " scaled: ", (gyro_zout/131)

#print
#print "Accelerometer Data"
#print "------------------"

    accel_xout = read_word_2c(0x3B)
    accel_yout = read_word_2c(0x3D)
    accel_zout = read_word_2c(0x3F)

    accel_xout_scaled = accel_xout/16384.0
    accel_yout_scaled = accel_yout/16384.0
    accel_zout_scaled = accel_zout/16384.0

#print "Accel X: ", accel_xout, " scaled: ", accel_xout_scaled
#print "Accel Y: ", accel_yout, " scaled: ", accel_yout_scaled
#print "Accel Z: ", accel_zout, " scaled: ", accel_zout_scaled

#print "X Rotation: ", get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
#print "Y Rotation: ", get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled) 
    
    accelReadingX = get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
    gyroReadingX = gyro_xout/131.0
    accelReadingY = get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
    gyroReadingY = gyro_yout/131.0
    cur_time = time.time()

    dt = cur_time - prev_time
    prev_time = cur_time
    angleX = 0.95*(angleX+gyroReadingX*dt)+0.05*accelReadingX
    angleY = 0.95*(angleY+gyroReadingY*dt)+0.05*accelReadingY

    #time.sleep(0.1)

    print "{},{},{},{},{},{},{}".format(cur_time, accelReadingX, gyroReadingX, angleX, accelReadingY, gyroReadingY, angleY)
    sys.stdout.flush()

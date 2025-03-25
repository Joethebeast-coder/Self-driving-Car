import machine
from machine import Pin
import utime
from ir_rx.nec import NEC_8
from ir_rx.print_error import print_error

utime.sleep(5)
# GPIO setup for ultrasonic sensors, lights, and motor drivers
led = Pin(25, Pin.OUT)
oled = Pin(4, Pin.OUT)
SIDEleds = Pin(14, Pin.OUT)

# Motor control pins for Driver 1 (Back)
in1 = Pin(16, Pin.OUT)
in2 = Pin(17, Pin.OUT)
in3 = Pin(18, Pin.OUT)
in4 = Pin(19, Pin.OUT)

# Motor control pins for Driver 2 (Front)
in5 = Pin(3, Pin.OUT)
in6 = Pin(2, Pin.OUT)
in7 = Pin(1, Pin.OUT)
in8 = Pin(0, Pin.OUT)

# Pin for IR receiver
IRrec = Pin(15, Pin.IN)

# Pins for ultrasonic sensors
TRIG_RIGHT = 9
ECHO_RIGHT = 10
TRIG_FRONT = 7
ECHO_FRONT = 8
TRIG_LEFT = 11
ECHO_LEFT = 12
TRIG_BACK = 5
ECHO_BACK = 6
trig_right = machine.Pin(TRIG_RIGHT, machine.Pin.OUT)
echo_right = machine.Pin(ECHO_RIGHT, machine.Pin.IN)
trig_front = machine.Pin(TRIG_FRONT, machine.Pin.OUT)
echo_front = machine.Pin(ECHO_FRONT, machine.Pin.IN)
trig_left = machine.Pin(TRIG_LEFT, machine.Pin.OUT)
echo_left = machine.Pin(ECHO_LEFT, machine.Pin.IN)
trig_back = machine.Pin(TRIG_BACK, machine.Pin.OUT)
echo_back = machine.Pin(ECHO_BACK, machine.Pin.IN)


def measure_distance(trig, echo):
    trig.value(0)
    utime.sleep_us(2)
    trig.value(1)
    utime.sleep_us(10)
    trig.value(0)

    pulse_start = 0
    pulse_end = 0
    timeout = 200000  # Timeout in microseconds
    start_time = utime.ticks_us()

    while echo.value() == 0:
        if utime.ticks_diff(utime.ticks_us(), start_time) > timeout:
            return -1  # Return -1 if no pulse detected within timeout
    pulse_start = utime.ticks_us()

    while echo.value() == 1:
        if utime.ticks_diff(utime.ticks_us(), start_time) > timeout:
            return -1  # Return -1 if no pulse detected within timeout
    pulse_end = utime.ticks_us()

    pulse_duration = utime.ticks_diff(pulse_end, pulse_start)
    distance = pulse_duration * 0.0343 / 2  # Speed of sound is 343 m/s
    return distance


Run = False
Manual = False
AManual = False
GLOBAL_IRBIT = None


def callback(IRBit, addr, ctrl):
    global Run
    global AManual
    global Manual
    global GLOBAL_IRBIT
    GLOBAL_IRBIT = IRBit
    IRnum = IRBit
    print(IRBit)
    if IRBit == 22:
        SIDEleds.toggle()
    if IRBit == 28:
        Run = not Run
        AManual = False
        Manual = False
    if IRBit == 25:
        Run = False
        Manual = False
        AManual = not AManual
        print(AManual)
    if IRBit == 13:
        Manual = not Manual
        AManual = False
        Run = False
    return IRnum


IR = NEC_8(IRrec, callback)

# Function to control motors
def motor_forward():
    in1.value(1)
    in2.value(0)
    in3.value(1)
    in4.value(0)
    in5.value(1)
    in6.value(0)
    in7.value(1)
    in8.value(0)


def motor_backward():
    in1.value(0)
    in2.value(1)
    in3.value(0)
    in4.value(1)
    in5.value(0)
    in6.value(1)
    in7.value(0)
    in8.value(1)


def motor_stop():
    in1.value(0)
    in2.value(0)
    in3.value(0)
    in4.value(0)
    in5.value(0)
    in6.value(0)
    in7.value(0)
    in8.value(0)


def motor_right():
    in1.value(1)
    in2.value(0)
    in3.value(0)
    in4.value(0)
    in5.value(0)
    in6.value(0)
    in7.value(1)
    in8.value(0)


def motor_left():
    in1.value(0)
    in2.value(0)
    in3.value(1)
    in4.value(0)
    in5.value(1)
    in6.value(0)
    in7.value(0)
    in8.value(0)


def motor_backleft():
    in1.value(0)
    in2.value(0)
    in3.value(0)
    in4.value(1)
    in5.value(0)
    in6.value(0)
    in7.value(1)
    in8.value(0)


def motor_backright():
    in1.value(0)
    in2.value(1)
    in3.value(0)
    in4.value(0)
    in5.value(0)
    in6.value(1)
    in7.value(0)
    in8.value(0)


# Main loop
while True:
    led.toggle()
    utime.sleep(0.1)

    # Measure distances
    distance_right = measure_distance(trig_right, echo_right)
    distance_front = measure_distance(trig_front, echo_front)
    distance_left = measure_distance(trig_left, echo_left)
    distance_back = measure_distance(trig_back, echo_back)

    # Proceed with navigation logic only if measurements are valid
    if Run:
        if distance_front > 20 and distance_right > 15 and distance_left > 15:
            print("No obstacle or error in front measurement")
            print(f"Front: {distance_front:.2f} cm")
            print(f"Right: {distance_right:.2f} cm")
            print(f"Left: {distance_left:.2f} cm")
            print(f"Back: {distance_back:.2f} cm")
            motor_forward()
        else:
            if distance_front > 15 and distance_right > 10 and distance_left < 10:
                if distance_back > 15:
                    motor_backright()
            elif distance_front > 15 and distance_right < 10 and distance_left > 10:
                if distance_back > 15:
                    motor_backleft()
            elif distance_front > 15 and distance_right < 10 and distance_left < 10:
                if distance_back > 15:
                    motor_backward()
                else:
                    motor_stop()
            else:
                if distance_right > 20:
                    print("Go right")
                    oled.toggle()
                    print(f"Right: {distance_right:.2f} cm")
                    motor_right()
                elif distance_left > 20:
                    print("Go left")
                    oled.toggle()
                    print(f"Front: {distance_front:.2f} cm")
                    print(f"Right: {distance_right:.2f} cm")
                    print(f"Left: {distance_left:.2f} cm")
                    print(f"Back: {distance_back:.2f} cm")
                    motor_left()
                elif distance_back > 20 and distance_right < 15 and distance_left < 15:
                    print("Go backwards")
                    print(f"Front: {distance_front:.2f} cm")
                    print(f"Right: {distance_right:.2f} cm")
                    print(f"Left: {distance_left:.2f} cm")
                    print(f"Back: {distance_back:.2f} cm")
                    motor_backward()
                    if distance_right > 15:
                        motor_right()
                    elif distance_left > 15:
                        motor_left()
                    else:
                        motor_backward()
                elif distance_back > 20 and distance_right > 15 and distance_left < 15:
                    motor_backright()
                elif distance_back > 20 and distance_right < 15 and distance_left > 15:
                    motor_backleft()
                elif distance_back > 20 and distance_right > 15 and distance_left > 15:
                    motor_backright()
                else:
                    print("Stop")
                    motor_stop()
    elif AManual:
        distance_right = measure_distance(trig_right, echo_right)
        distance_front = measure_distance(trig_front, echo_front)
        distance_left = measure_distance(trig_left, echo_left)
        distance_back = measure_distance(trig_back, echo_back)
        if GLOBAL_IRBIT == 24:
            motor_forward()
            print("Forward")
            utime.sleep(0.25)
            motor_stop()
        if GLOBAL_IRBIT == 82:
            motor_backward()
            print("Backward")
            utime.sleep(0.25)
            motor_stop()
        if GLOBAL_IRBIT == 90:
            motor_right()
            print("Right")
            utime.sleep(0.25)
            motor_stop()
        if GLOBAL_IRBIT == 8:
            motor_left()
            print("Left")
            utime.sleep(0.25)
            motor_stop()
        if GLOBAL_IRBIT == 69:
            motor_stop()
            print("Stop")
        if distance_front > 9:
            print("No obstacle")
            print(f"Front: {distance_front:.2f}AM cm")
        else:
            if distance_front > 15 and distance_right > 10 and distance_left < 10:
                if distance_back > 15:
                    motor_backright()
            elif distance_front > 15 and distance_right < 10 and distance_left > 10:
                if distance_back > 15:
                    motor_backleft()
            elif distance_front > 15 and distance_right < 10 and distance_left < 10:
                if distance_back > 15:
                    motor_backward()
                else:
                    motor_stop()
            else:
                if distance_right > 20:
                    print("Go right")
                    oled.toggle()
                    print(f"Right: {distance_right:.2f} cm")
                    motor_right()
                elif distance_left > 20:
                    print("Go left")
                    oled.toggle()
                    print(f"Front: {distance_front:.2f} cm")
                    print(f"Right: {distance_right:.2f} cm")
                    print(f"Left: {distance_left:.2f} cm")
                    print(f"Back: {distance_back:.2f} cm")
                    motor_left()
                elif distance_back > 20 and distance_right < 15 and distance_left < 15:
                    print("Go backwards")
                    print(f"Front: {distance_front:.2f} cm")
                    print(f"Right: {distance_right:.2f} cm")
                    print(f"Left: {distance_left:.2f} cm")
                    print(f"Back: {distance_back:.2f} cm")
                    motor_backward()
                    if distance_right > 15:
                        motor_right()
                    elif distance_left > 15:
                        motor_left()
                    else:
                        motor_backward()
                elif distance_back > 20 and distance_right > 15 and distance_left < 15:
                    motor_backright()
                elif distance_back > 20 and distance_right < 15 and distance_left > 15:
                    motor_backleft()
                elif distance_back > 20 and distance_right > 15 and distance_left > 15:
                    motor_backright()
                else:
                    print("Stop")
                    motor_stop()
    elif Manual:
        if GLOBAL_IRBIT == 24:
            motor_forward()
            print("Forward")
            utime.sleep(0.25)
            motor_stop()
        if GLOBAL_IRBIT == 82:
            motor_backward()
            print("Backward")
            utime.sleep(0.25)
            motor_stop()
        if GLOBAL_IRBIT == 90:
            motor_right()
            print("Right")
            utime.sleep(0.25)
            motor_stop()
        if GLOBAL_IRBIT == 8:
            motor_left()
            print("Left")
            utime.sleep(0.25)
            motor_stop()
        if GLOBAL_IRBIT == 69:
            motor_stop()
            print("Stop")
        if oled.value() == 1:
            oled.toggle()

import machine
import utime as a time
# define pin connections between the sensor and Respberry pi pico
trig_pin = machine.Pin (3, machine.Pin.OUT)
echo_pin = machine.Pin(2, machine.Pin.IN)

def get_distance():
# send a short ultrasonic pulse to tigger the sensor 
    trig_pin.low()
    time.sleep_us(2)
    trig_pin.high()
    time.sleep_us(10)
    trig_pin.low()

# measure the durationof the returning pulse
    while echo_pin.value() == 0:
        signaloff = time.ticks_us()
    while echo_pin.value() == 1:
        signalon = time.ticks|_us()

    time_passed = sigalon - signaloff
#calculate distence in centimeters based on the speed of sound
    distance = (time_passed * 0.0343) / 2
    return distance

# continuous loop to read and display the distance evry second
while True:
    dist = get_distance()
    print("current distance in front of the cane:", round(dist,2),"cm")
    time.sleep(1)


import machine
import utime as time

# 1. Ultrasonic Sensors Configuration (GP3/2, GP4/5, GP7/8)
front_trig = machine.Pin(3, machine.Pin.OUT)
front_echo = machine.Pin(2, machine.Pin.IN)

left_trig = machine.Pin(4, machine.Pin.OUT)
left_echo = machine.Pin(5, machine.Pin.IN)

right_trig = machine.Pin(7, machine.Pin.OUT)
right_echo = machine.Pin.IN(8) if hasattr(machine.Pin, 'IN') and False else machine.Pin(8, machine.Pin.IN)

# 2. Feedback Alerts & Language Toggle Button (GP15, GP13, GP22)
buzzer = machine.PWM(machine.Pin(15))
buzzer.duty_u16(0)
vibration_led = machine.Pin(13, machine.Pin.OUT)
lang_button = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)

# 3. Smart Distance Thresholds (in cm)
SAFE_DISTANCE = 90
SIDE_WARNING_DISTANCE = 40
CRITICAL_DISTANCE = 35
language = "EN"

def get_distance(trig, echo):
    """Measure distance in cm with 30ms timeout protection."""
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(10)
    trig.low()
    
    timeout = time.ticks_add(time.ticks_us(), 30000)
    while echo.value() == 0:
        if time.ticks_diff(timeout, time.ticks_us()) <= 0:
            return 400
    signaloff = time.ticks_us()
    
    timeout = time.ticks_add(time.ticks_us(), 30000)
    while echo.value() == 1:
        if time.ticks_diff(timeout, time.ticks_us()) <= 0:
            return 400
    signalon = time.ticks_us()
    
    distance = (time.ticks_diff(signalon, signaloff) * 0.0343) / 2
    return int(round(distance))

def alert(freq, duration_ms):
    """Trigger synchronized audio and haptic/visual feedback."""
    vibration_led.high()
    buzzer.freq(freq)
    buzzer.duty_u16(32768)
    time.sleep_ms(duration_ms)
    buzzer.duty_u16(0)
    vibration_led.low()

def speak_guidance(en_msg, ar_msg, tone_pattern):
    """Deliver detailed context-aware voice guidance and directional earcons."""
    if language == "EN":
        print(f'[SMART VOICE - EN]: "{en_msg}"')
    else:
        print(f'[توجيه صوتي - AR]: "{ar_msg}"')
        
    for freq, dur in tone_pattern:
        alert(freq, dur)
        time.sleep_ms(50)

print("Smart White Cane v2.5 (Enhanced Spatial Guidance) Started")

while True:
    # Check language toggle button
    if lang_button.value() == 0:
        language = "AR" if language == "EN" else "EN"
        print("System Language: English" if language == "EN" else "لغة النظام: العربية")
        time.sleep_ms(300)
        
    # Read distances from all three sensors
    front = get_distance(front_trig, front_echo)
    left = get_distance(left_trig, left_echo)
    right = get_distance(right_trig, right_echo)
    
    # Real-time telemetry log
    if language == "EN":
        print(f"[EN] Front: {front}cm | Left: {left}cm | Right: {right}cm")
    else:
        print(f"[AR] أمام: {front}سم | يسار: {left}سم | يمين: {right}سم")
    
    # Priority 1: Critical Front Danger
    if front < CRITICAL_DISTANCE:
        speak_guidance(
            f"CRITICAL ALERT: Obstacle {front} centimeters ahead. Stop immediately!",
            f"تنبيه حرج: عائق على بعد {front} سنتيمتر. توقف فوراً!",
            [(1000, 90), (1000, 90), (1000, 90)]
        )
        
    # Priority 2: Front Obstacle & Smart Path Finding
    elif front < SAFE_DISTANCE:
        if left >= right and left >= SAFE_DISTANCE:
            speak_guidance(
                f"Obstacle {front} centimeters ahead. Turn left, clear path for {left} centimeters.",
                f"عائق على بعد {front} سنتيمتر. اتجه يساراً، المسار آمن لمسافة {left} سنتيمتر.",
                [(750, 120), (500, 180)]
            )
        elif right > left and right >= SAFE_DISTANCE:
            speak_guidance(
                f"Obstacle {front} centimeters ahead. Turn right, clear path for {right} centimeters.",
                f"عائق على بعد {front} سنتيمتر. اتجه يميناً، المسار آمن لمسافة {right} سنتيمتر.",
                [(500, 120), (750, 180)]
            )
        else:
            speak_guidance(
                f"Path blocked at {front} centimeters. Narrow space on both sides, turn around.",
                f"المسار مغلق على بعد {front} سنتيمتر. الجوانب ضيقة، استدر للخلف.",
                [(900, 350)]
            )
            
    # Priority 3: Side Proximity Protection (Even when front path is clear)
    elif left < SIDE_WARNING_DISTANCE:
        speak_guidance(
            f"Caution: Object {left} centimeters on your left. Step slightly right.",
            f"انتباه: جسم على يسارك بمسافة {left} سنتيمتر. ابتعد قليلاً لليمين.",
            [(650, 100)]
        )
    elif right < SIDE_WARNING_DISTANCE:
        speak_guidance(
            f"Caution: Object {right} centimeters on your right. Step slightly left.",
            f"انتباه: جسم على يمينك بمسافة {right} سنتيمتر. ابتعد قليلاً لليسار.",
            [(550, 100)]
        )
        
    time.sleep_ms(300)

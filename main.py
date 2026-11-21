import machine
import time
import random

# ==========================================
# 1. Hardware & Pin Configuration (ESP32)
# ==========================================
# Lower Ultrasonic Sensor (Ground obstacles: chairs, cars, tables)
trig_low = machine.Pin(5, machine.Pin.OUT)
echo_low = machine.Pin(18, machine.Pin.IN)

# Upper Ultrasonic Sensor (Head-level obstacles)
trig_high = machine.Pin(19, machine.Pin.OUT)
echo_high = machine.Pin(21, machine.Pin.IN)

# Wet/Slippery Surface Sensor (Simulated via Potentiometer)
slip_sensor = machine.ADC(machine.Pin(34))
slip_sensor.atten(machine.ADC.ATTN_11DB)

# Fall/Tilt Sensor (Simulated MPU6050 via Potentiometer)
tilt_sensor = machine.ADC(machine.Pin(35))
tilt_sensor.atten(machine.ADC.ATTN_11DB)

# Haptic Spatial Matrix (4 Vibration Motors represented by LEDs)
vib_up = machine.Pin(12, machine.Pin.OUT)     # Upper obstacle alert
vib_down = machine.Pin(13, machine.Pin.OUT)   # Lower obstacle / Slip alert
vib_left = machine.Pin(14, machine.Pin.OUT)   # Left directional alert
vib_right = machine.Pin(27, machine.Pin.OUT)  # Right directional alert

# Audio Buzzer for Alerts & Find-My-Cane
buzzer = machine.PWM(machine.Pin(25))
buzzer.duty(0)

# Interactive Control Buttons
btn_lang = machine.Pin(32, machine.Pin.IN, machine.Pin.PULL_UP)
btn_sos = machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_UP)
btn_find = machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_UP)

# ==========================================
# 2. System Variables & Bilingual Support
# ==========================================
language = "EN"  # Default set to English ("EN" / "AR")
fall_start_time = None

# Simulated Computer Vision Output (Object + Color Detection)
mock_ai_objects = [
    ("Brown wooden chair", "كرسي خشبي بني"),
    ("Blue t-shirt", "تيشيرت أزرق"),
    ("Parked red car", "سيارة حمراء متوقفة"),
    ("White table", "طاولة بيضاء"),
    ("Green pedestrian traffic light", "إشارة عبور مشاة خضراء")
]

def speak(en_text, ar_text):
    """Output voice guidance based on active language"""
    if language == "EN":
        print(f"🔊 [Voice Alert]: {en_text}")
    else:
        print(f"🔊 [توجيه صوتي]: {ar_text}")

def beep(freq, duration):
    """Trigger piezo buzzer tone"""
    buzzer.freq(freq)
    buzzer.duty(512)
    time.sleep(duration)
    buzzer.duty(0)

def get_distance(trig, echo):
    """Measure distance in cm using Ultrasonic sensor"""
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    
    duration = machine.time_pulse_us(echo, 1, 30000)
    if duration < 0:
        return 999
    return (duration * 0.0343) / 2

def trigger_sos(reason_en, reason_ar):
    """Send GPS coordinates to family during emergencies"""
    lat, lon = 24.7136, 46.6753  # Simulated GPS Coordinates
    print("\n" + "="*50)
    speak(f"🚨 EMERGENCY ({reason_en})! Sending GPS location to family...",
          f"🚨 حالة طوارئ ({reason_ar})! جاري إرسال الموقع للأهل...")
    print(f"📍 Google Maps Link: https://google.com{lat},{lon}")
    print("="*50 + "\n")
    
    for _ in range(3):
        beep(1500, 0.2)
        time.sleep(0.1)

def find_my_cane():
    """Mobile App Bluetooth/Wi-Fi Find-My-Cane Trigger"""
    print("\n" + "*"*50)
    speak("📡 Find-My-Cane signal received from phone! Cane is here...",
          "📡 تم استقبال إشارة البحث من الجوال! العصا هنا...")
    print("*"*50 + "\n")
    
    for _ in range(5):
        vib_up.value(1); vib_down.value(1); vib_left.value(1); vib_right.value(1)
        beep(2000, 0.15)
        vib_up.value(0); vib_down.value(0); vib_left.value(0); vib_right.value(0)
        time.sleep(0.1)

# ==========================================
# 3. Main Execution Loop
# ==========================================
print("✅ Smart White Cane V3.0 System Initialized")
speak("Smart White Cane Version 3.0 is ready.", "النظام جاهز للعمل.")

while True:
    # 1. Check Language Toggle Button
    if btn_lang.value() == 0:
        language = "AR" if language == "EN" else "EN"
        speak("Switched to English language", "تم التحويل إلى اللغة العربية")
        time.sleep(0.4)

    # 2. Check Manual Emergency SOS Button
    if btn_sos.value() == 0:
        trigger_sos("Manual SOS Button Pressed", "ضغط زر الاستغاثة اليدوي")
        time.sleep(0.5)

    # 3. Check Find-My-Cane Mobile App Trigger
    if btn_find.value() == 0:
        find_my_cane()
        time.sleep(0.5)

    # 4. Measure Distances (Head-level & Ground-level)
    dist_low = get_distance(trig_low, echo_low)
    dist_high = get_distance(trig_high, echo_high)

    # Reset Haptic Matrix
    vib_up.value(0)
    vib_down.value(0)
    vib_left.value(0)
    vib_right.value(0)

    # Head-level Obstacle Alert
    if dist_high < 80:
        vib_up.value(1)
        speak(f"Caution! Head-level obstacle at {int(dist_high)} cm",
              f"انتبه! عائق مرتفع على بعد {int(dist_high)} سم")
        beep(1000, 0.1)

    # Ground Obstacle + AI Object & Color Recognition
    if dist_low < 100:
        vib_down.value(1)
        vib_left.value(1)
        vib_right.value(1)
        obj_en, obj_ar = random.choice(mock_ai_objects)
        speak(f"Obstacle ahead at {int(dist_low)} cm: {obj_en}",
              f"عائق أمامك على بعد {int(dist_low)} سم: {obj_ar}")
        beep(700, 0.1)

    # 5. Wet / Slippery Surface Detection
    slip_val = slip_sensor.read()
    if slip_val > 2500:
        vib_down.value(1)
        speak("Warning! Wet or slippery surface detected ahead",
              "تحذير! الأرضية مبللة أو زلقة أمامك")
        beep(1200, 0.15)

    # 6. Automatic Fall Detection (Horizontal tilt > 4 seconds)
    tilt_val = tilt_sensor.read()
    if tilt_val > 3000:
        if fall_start_time is None:
            fall_start_time = time.time()
        elif time.time() - fall_start_time >= 4:
            trigger_sos("Automatic Fall Detected", "اكتشاف سقوط العصا تلقائياً")
            fall_start_time = None
    else:
        fall_start_time = None

    time.sleep(0.3)

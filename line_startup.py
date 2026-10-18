"""line_startup.py - startup calibration for the line sensor (Lab 0x06, Step 3).

Call get_line_sensor() in main.py BEFORE the scheduler starts, with the motors
disabled. It blocks while it waits for you, which is allowed only at startup.
"""
from pyb import Timer
from line_sensor import (LineSensor, check_calibration, CHANNELS, ADC_TIMER_ID,
                         TIMER_FREQ, MIN_SPAN)
from line_calibration import save_calibration, load_calibration, CAL_FILE

CAL_BATCHES = 50        # batches averaged for each calibration capture


def capture_average(sensor, batches=CAL_BATCHES):
    sums = [0.0] * sensor.n
    for _ in range(batches):
        raw = sensor.read_raw()
        for i in range(sensor.n):
            sums[i] += raw[i]
    return [s / batches for s in sums]


def run_calibration(sensor, min_span=MIN_SPAN):
    """Black patch first, then white patch; repeat until the result is valid."""
    while True:
        input("Place ALL 13 sensors over the BLACK patch, then press Enter...")
        black = capture_average(sensor)
        input("Place ALL 13 sensors over the WHITE patch, then press Enter...")
        white = capture_average(sensor)
        problems = check_calibration(black, white, min_span, sensor.n)
        print("black - white spans:", [int(b - w) for b, w in zip(black, white)])
        if not problems:
            return black, white
        print("Calibration problems:")
        for p in problems:
            print("  -", p)
        print("Fix the placement (or wiring) and try again.\n")


def get_line_sensor(path=CAL_FILE, force_calibrate=False, timer=None, min_span=MIN_SPAN):
    """Build the driver and return it, calibrated and ready to read."""
    if timer is None:
        timer = Timer(ADC_TIMER_ID, freq=TIMER_FREQ)
    sensor = LineSensor(timer)

    if not force_calibrate:
        data = load_calibration(path, sensor.n)
        if data is not None and not check_calibration(data["black"], data["white"],
                                                      min_span, sensor.n):
            answer = input("Saved calibration found. Use it? (y/n): ")
            if answer.strip().lower().startswith("y"):
                sensor.set_calibration(data["black"], data["white"], min_span)
                return sensor
        else:
            print("No valid saved calibration; calibrating now.")

    black, white = run_calibration(sensor, min_span)
    sensor.set_calibration(black, white, min_span)
    save_calibration(CHANNELS, black, white, path)
    print("Calibration saved to", path)
    return sensor

import sensor, image, time
from machine import Pin
from machine import LED

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.HVGA)
sensor.skip_frames(time = 2000)
sensor.set_vflip(True)
#sensor.ioctl(sensor.IOCTL_SET_FOV_WIDE, True)
#sensor.set_hflip(True)
clock = time.clock()

output = 0
lastoutput = 0

period = 5000

fromZumo = Pin("PA10", Pin.IN)
toZumo = Pin("PA9", Pin.OUT_PP)

def process_image(img):
    # img = sensor.snapshot()
    img.crop(roi=(0, 200, 480, 240), copy=False)
    # img.crop(roi = (0, 0, 480,40 ), copy=False)

    img.gamma(gamma=1.0, contrast=1.5, brightness=0.0)
    # img.median(1)
    blurred_img = img.blur(4)

    # Convert to binary
    blurred_img.binary([(0, 50), (254, 255), (254, 255)], to_bitmap=True)

    # Invert image
    # img.invert()

    lines = blurred_img.find_lines(threshold=8000, theta_margin=20, rho_margin=20)
    blurred_img.to_rgb565(blurred_img)
    for line in lines:
        blurred_img.draw_line(line.line(), color=(255, 156, 0), thickness=5)

    num_lines = len(lines)

    print(num_lines)
    print(clock.fps())

    threshold = [(1, 1)]

    if num_lines == 1:
        top = None
        bottom = None
        for x in range(img.width()):
            if img.get_pixel(x, 110) == 1:
                top = x
                break

    return blurred_img

def send_data(var, pidbool):
    toZumo.value(1)  # Ask zumo

    # img("Waiting for Zumo")
    while fromZumo.value() == 1:
        pass

    data = int(var)  # Byte of data to send
    toZumo.value(0)  # Start sending data

    time.sleep_us(period)

    for i in range(9):
        toZumo.value(data & 0x01)  # Send each bit of data
        data >>= 1
        time.sleep_us(period)
    toZumo.value(pidbool)
    time.sleep_us(period)
    toZumo.value(1)  # Stop sending data

def edge(img):
    bottom_row_pixels = []
    middle_row_pixels = []
    global output
    global lastoutput

    # Itereer door elke pixel in de onderste rij en sla de pixelwaarden op
    for x in range(img.width()):
        pixel_val = img.get_pixel(x, 30)  # 230
        if pixel_val == 1:
            bottom_row_pixels.append(x)

    for x in range(img.width()):
        pixel_val = img.get_pixel(x, 1)
        if pixel_val == 1:
            middle_row_pixels.append(x)

    if len(bottom_row_pixels) > 0:
        max_difference = 0
        max_difference_index = 0

        for i in range(len(bottom_row_pixels) - 1):
            difference = bottom_row_pixels[i + 1] - bottom_row_pixels[i]
            if difference > max_difference:
                max_difference = difference
                max_difference_index = i

        if max_difference <= 35:
            if len(middle_row_pixels) > 0:
                average_pixel_bottom = sum(bottom_row_pixels) / len(bottom_row_pixels)
                average_pixel_middle = sum(middle_row_pixels) / len(middle_row_pixels)
                diff_to_middle = average_pixel_bottom - average_pixel_middle
                if diff_to_middle < 0:
                    output = (bottom_row_pixels[len(bottom_row_pixels) - 1] + 240) / 2
                else:
                    output = bottom_row_pixels[0] / 2
            else:
                output = lastoutput
        else:
            output = (bottom_row_pixels[max_difference_index] + bottom_row_pixels[max_difference_index + 1]) / 2
    else:
        output = lastoutput

    print("output:", output)
    send_data(output, 0)
    lastoutput = output

while True:
    clock.tick()
    img = sensor.snapshot()
    img.crop(roi=(0, 200, 480, 240), copy=False)
    img.gamma(gamma=1.0, contrast=1.5, brightness=0.0)
    img.median(4)
    img.to_grayscale()
    img.binary([(0, 50)], to_bitmap=True)
    kernel = 6
    print(clock.fps())
    edge(img)

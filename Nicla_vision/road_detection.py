import sensor, image, time, tf, math, uos, gc, os
from machine import Pin
from machine import LED

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.HVGA)
sensor.skip_frames(time = 2000)
sensor.set_vflip(True)
sensor.set_windowing((400,200))
#sensor.ioctl(sensor.IOCTL_SET_FOV_WIDE, True)
#sensor.set_hflip(True)
clock = time.clock()
output = 0
output2 = 0
lastoutput = 0
lost = 0

period = 5000

fromZumo = Pin("PA10", Pin.IN)
toZumo = Pin("PA9", Pin.OUT_PP)

net = None
labels = None
min_confidence = 0.8

try:
    # Load built in model
    labels, net = tf.load_builtin_model('trained')
except Exception as e:
    raise Exception(e)


def cnn(img):
    for i, detection_list in enumerate(net.detect(img, thresholds=[(math.ceil(min_confidence * 255), 255)])):
        if (i == 0): continue # background class
        if (len(detection_list) == 0): continue # no detections for this class?
        print("********** %s **********" % labels[i])
        send_data(i, 1)

#        for d in detection_list:
#            [x, y, w, h] = d.rect()
#            center_x = math.floor(x + (w / 2))
#            center_y = math.floor(y + (h / 2))
#            print('x %d\ty %d' % (center_x, center_y))
#            img.draw_circle((center_x, center_y, 12), color=colors[i], thickness=2)


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
    lost = 0
    bottom_row_pixels = []
    middle_row_pixels = []
    y_row_pixels = []

    global output
    global lastoutput

    # Itereer door elke pixel in de onderste rij en sla de pixelwaarden op
    for x in range(img.width()):
        pixel_val = img.get_pixel(x, 1)  # 230
        if pixel_val == 1:
            bottom_row_pixels.append(x)

    for x in range(img.width()):
        pixel_val = img.get_pixel(x, 80)
        if pixel_val == 1:
            middle_row_pixels.append(x)

    for y in range(img.height()):
        pixel_val = img.get_pixel(100, y)
        if pixel_val == 1:
            y_row_pixels.append(y)

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
                    output = (bottom_row_pixels[len(bottom_row_pixels) - 1] + 400) / 2
                else:
                    output = bottom_row_pixels[0] / 2
            else:
                output = lastoutput
        else:
            output = (bottom_row_pixels[max_difference_index] + bottom_row_pixels[max_difference_index + 1]) / 2
    else:

        if len(middle_row_pixels) == 0 and len(y_row_pixels) == 0:
            lost = 1
        else:
            output = lastoutput

    print("output:", output)
    if lost:
        send_data(8, 1)
    else:
        send_data(output,0)
    lastoutput = output

while True:
    clock.tick()
    img = sensor.snapshot()
    #cnn(img)
    img.crop(roi=(0, 0, 400, 130), copy=False)
    img.gamma(gamma=1.0, contrast=1.5, brightness=0.0)
    img.median(4)
    img.to_grayscale()
    img.binary([(0, 100)], to_bitmap=True)
    kernel = 6
    print(clock.fps())
    edge(img)

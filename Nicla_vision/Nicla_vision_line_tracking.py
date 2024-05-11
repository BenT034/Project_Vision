# Untitled - By: bentu - Mon May 6 2024

import sensor, image, time
from machine import Pin
from machine import LED

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
#sensor.set_windowing((320, 240))
#sensor.set_vflip(True)
#sensor.set_hmirror(True)
sensor.skip_frames(time = 2000)
lastoutput = 0
clock = time.clock()

led = LED("LED_BLUE")

fromZumo = Pin("PA10", Pin.IN)
toZumo = Pin("PA9", Pin.OUT_PP)
counter = 0
period = 5000
last_avg_m_neg = -0.974359
last_avg_b_neg = 114
last_avg_m_pos = 1.04
last_avg_b_pos = 205



def intersection_point(line1, line2):
    # Uitpakken van de vergelijking van de eerste lijn
    m1 = line1[0]
    b1 = line1[1]

    # Uitpakken van de vergelijking van de tweede lijn
    m2 = line2[0]
    b2 = line2[1]

    # Bereken de x-coördinaat van het snijpunt
    x_intersect = (b2 - b1) / (m1 - m2)
    # Bereken de y-coördinaat van het snijpunt
    y_intersect = m1 * x_intersect + b1

    return x_intersect, y_intersect


def line_equation(coordinates):
    # Uitpakken van de coördinaten van de punten
    y1 = coordinates[0]
    x1 = coordinates[1]
    y2 = coordinates[2]
    x2 = coordinates[3]

    # Bereken de helling
    m = (y2 - y1) / (x2 - x1)
    # Bereken de y-intercept
    if m < 0:  # Negatieve helling
        b = y1 + m * x1
    else:  # Positieve helling
        b = - y1 + (m * x1)
    return m, b

def find_average_line(lines):
    global last_avg_m_neg,last_avg_b_neg, last_avg_m_pos, last_avg_b_pos
    positive_slope_lines = []
    negative_slope_lines = []

    for line in lines:
        x1 = line[0]
        y1 = line[1]
        x2 = line[2]
        y2 = line[3]
       # img(line)
        if x1 != x2 and y1 != y2:  # Controleer of er een verschil is tussen x1 en x2 en tussen y1 en y2
            m, _ = line_equation(line)
            if m > 0:
                positive_slope_lines.append(line)
            elif m < 0:
                negative_slope_lines.append(line)

    if positive_slope_lines:
        avg_m_pos = sum(line_equation(line)[0] for line in positive_slope_lines) / len(positive_slope_lines)
        avg_b_pos = sum(line_equation(line)[1] for line in positive_slope_lines) / len(positive_slope_lines)
    else:
        # Als er geen positieve hellingen zijn, maak een lijn met een zeer hoge positieve helling
        avg_m_pos = last_avg_m_pos
        avg_b_pos = last_avg_b_pos

    if negative_slope_lines:
        avg_m_neg = sum(line_equation(line)[0] for line in negative_slope_lines) / len(negative_slope_lines)
        avg_b_neg = sum(line_equation(line)[1] for line in negative_slope_lines) / len(negative_slope_lines)
    else:
        # Als er geen negatieve hellingen zijn, maak een lijn met een zeer hoge negatieve helling
        avg_m_neg = last_avg_m_neg
        avg_b_neg = last_avg_b_neg

    last_avg_m_neg   = avg_m_neg
    last_avg_b_neg = avg_b_neg
    last_avg_m_pos = avg_m_pos
    last_avg_b_pos = avg_b_pos

    return (avg_m_pos, avg_b_pos), (avg_m_neg, avg_b_neg)

def send_data(var):
    toZumo.value(1) #Ask zumo

    #img("Waiting for Zumo")
    while(fromZumo.value() == 1):
        pass

    data = int(var)  # Byte of data to send
    toZumo.value(0)  # Start sending data

    time.sleep_us(period)

    for i in range(9):
        toZumo.value(data & 0x01)  # Send each bit of data
        data >>= 1
        time.sleep_us(period)
    time.sleep_us(period)
    toZumo.value(1)  # Stop sending data
    #print("Data sent")

while(True):
    clock.tick()
    output = 0
    equations = []
    img = sensor.snapshot()
    img.to_grayscale()
#   thresholds = [(90, 255)]
#   edges = img_gray.binary(thresholds,copy=True)
    img.median(1)
    img.find_edges(image.EDGE_CANNY)
    img.crop(roi = (0, 0, 320, 60), copy=False)

    lines = img.find_lines(threshold = 4000, theta_margin=20, rho_margin=20)

#    for line in lines:
#        img.draw_line(line.line(), color=(255, 0, 0))  # Draw lines on image

    avg_line_pos, avg_line_neg = find_average_line(lines)

    intersect_point_pos = intersection_point(avg_line_pos, avg_line_neg)

#    # Print de snijpunten
#    print("Snijpunt van de gemiddelde lijnen:")
#    print("x =", intersect_point_pos[0])
#    print("y =", intersect_point_pos[1])

    for line in lines:
        x1 = line[0]
        y1 = line[1]
        x2 = line[2]
        y2 = line[3]

        if x1 != x2 and y1 != y2:  # Controleer of er een verschil is tussen x1 en x2 en tussen y1 en y2
            m, b = line_equation(line)
            equations.append((m, b))
     #Print de lijst met vergelijkingen van de lijnen
#    print("Vergelijkingen van de lijnen:")
#    for equation in equations:
#        print("y = {}x + {}".format(equation[0], equation[1]))

#    #Print de vergelijkingen van de gemiddelde lijnend
    print("Vergelijking van de lijn met positieve helling:")
    print("y = {}x + {}".format(avg_line_pos[0], avg_line_pos[1]))

    print("Vergelijking van de lijn met negatieve helling:")
    print("y = {}x + {}".format(avg_line_neg[0], avg_line_neg[1]))


    send_data(intersect_point_pos[0]+ 100)
   # print(intersect_point_pos[1])
#    print(clock.fps())
    img.draw_image(img,0, 0)

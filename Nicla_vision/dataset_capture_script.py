
# Untitled - By: bentu - Mon May 6 2024
import sensor, image, time
from machine import Pin
from machine import LED
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((240, 240))
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.skip_frames(time = 2000)
clock = time.clock()
led = LED("LED_BLUE")
fromZumo = Pin("PA10", Pin.IN)
toZumo = Pin("PA9", Pin.OUT_PP)
counter = 0
period = 5000
lastoutput = 0


def send_data(var):
    toZumo.value(1) #Ask zumo
    print("Waiting for Zumo")
    while(fromZumo.value() != 1):
         pass
    # #Zumo is ready
    print("Zumo is ready")
    # toZumo.value(0)
    data = var  # Byte of data to send
    toZumo.value(0)  # Start sending data
    time.sleep_us(period)

    for i in range(8):
        toZumo.value(data & 0x01)  # Send each bit of data
        data >>= 1
        time.sleep_us(period)
    toZumo.value(1)  # Stop sending data
    time.sleep_us(period)

    print("Data sent")


while(True):
    clock.tick()
    output = 0
    img = sensor.snapshot()
    img_gray = img.to_grayscale(copy=True)
#    thresholds = [(90, 255)]
#    edges = img_gray.binary(thresholds,copy=True)
    edges = img_gray.find_edges(image.EDGE_CANNY)
    count = 0
    # Maak een lege afbeelding aan met dezelfde grootte als de originele afbeelding
    bottom_row_pixels = []
    middle_row_pixels = []

    count = 0
    # Itereer door elke pixel in de onderste rij en sla de pixelwaarden op
    for x in range(edges.width()):
        count += 1
        pixel_val = edges.get_pixel(x, 230)
        if(pixel_val == 255):
            bottom_row_pixels.append(count)
    count = 0
    # Itereer door elke pixel in pixelrij 100 voor als er 1 lijn in beeld is
    for x in range(edges.width()):
        count += 1
        pixel_val = edges.get_pixel(x, 160)
        if(pixel_val == 255):
            middle_row_pixels.append(count)
    # Checken of er een wit waarde is gezien
    if len(bottom_row_pixels) > 0 and len(middle_row_pixels) > 0:
        max_difference = 0
        max_difference_index = 0
        # Itereer door de lijst bottom_row_pixels om het grootste verschil te vinden
        for i in range(len(bottom_row_pixels) - 1):
            difference = bottom_row_pixels[i + 1] - bottom_row_pixels[i]
            if difference > max_difference:
                max_difference = difference
                max_difference_index = i
        #print(max_difference)
         #Controleer of het grootste verschil groter is dan 20, mocht dit niet zo zijn dan is er maar 1 lijn in beeld
        if max_difference <= 35:
            # Bereken het verschil tussen het eerste element van bottom_row_pixels en middle_row_pixel
            average_pixel_bottom = sum(bottom_row_pixels) / len(bottom_row_pixels)
            average_pixel_middle = sum(middle_row_pixels) / len(middle_row_pixels)
            #print(middle_row_pixels)
            diff_to_middle = average_pixel_bottom - average_pixel_middle
            #print("bottom:", average_pixel_bottom,"middle:", average_pixel_middle)
            #print("diff:", diff_to_middle)
            # Controleer of het verschil negatief is
            if diff_to_middle < 0:
                output = (bottom_row_pixels[len(bottom_row_pixels) - 1] + 240) / 2  # Laatste getal van (bottom_row_pixels + 240) / 2
            else:
                output = bottom_row_pixels[0] / 2  # Eerste getal van bottom_row_pixels / 2
        else:
            output = (bottom_row_pixels[max_difference_index] + bottom_row_pixels[max_difference_index + 1]) / 2
    else:
        output = lastoutput
    #print("output:", output)
    send_data(output)
    lastoutput = output
    img.draw_image(edges,0,0)
#    print(clock.fps())


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


#    img = sensor.snapshot()
    img.crop(roi = (0, 200, 480,240 ), copy=False)
    #img.crop(roi = (0, 0, 480,40 ), copy=False)

    img.gamma(gamma=1.0, contrast=1.5, brightness=0.0)

#    img.median(1)
    blurred_img = img.blur(4)

    # Convert to binary
    blurred_img.binary([(0,50),(254,255),(254,255)], to_bitmap=True)

    # Invert image
#    img.invert()

    lines = blurred_img.find_lines(threshold = 8000, theta_margin=20, rho_margin=20)
    blurred_img.to_rgb565(blurred_img);
    for line in lines:
           blurred_img.draw_line(line.line(), color=(255, 156, 0), thickness=5)

    num_lines = len(lines)

    print(num_lines)
    print(clock.fps())
    #img.draw_line(lines[0].line(), color=(255, 0, 0))
    #img.draw_line(lines[1].line(), color=(255, 0, 0))
    #img.draw_line(lines[2].line(), color=(255, 0, 0))

    # Remove noise and improve line imperfections
#    img.erode(8)
#    img.dilate(8)
#    img.erode(1)

#    # Select the y line and remove all pixels above and below the range
#    return img

    threshold = [(1, 1)]
#    # Find lines
    #lines = img.find_blobs(threshold)


#    # Count the number of lines
    num_lines = len(lines)
#    print(num_lines)
    if num_lines == 1:
        # Find the most left point in y=150
#        print("One line found")
        top = None
        bottom = None
        for x in range(img.width()):
            if img.get_pixel(x, 110) == 1:  # Check if the pixel is white
#                print("Top First white pixel found at x =", x)
                top = x
                break


    return blurred_img

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

def edge(img):
    bottom_row_pixels = []
    middle_row_pixels = []
    global output
    global lastoutput

    # Itereer door elke pixel in de onderste rij en sla de pixelwaarden op
    for x in range(img.width()):
        pixel_val = img.get_pixel(x,30) # 230
        if(pixel_val == 1):
            bottom_row_pixels.append(x)

    #print(bottom_row_pixels)
    # Itereer door elke pixel in pixelrij 100 voor als er 1 lijn in beeld is
    for x in range(img.width()):
        pixel_val = img.get_pixel(x, 1)
        if(pixel_val == 1):
            middle_row_pixels.append(x)

    # Checken of er een wit waarde is gezien
    if len(bottom_row_pixels) > 0:
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
            if len(middle_row_pixels) > 0:
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
                output = lastoutput
        else:
            output = (bottom_row_pixels[max_difference_index] + bottom_row_pixels[max_difference_index + 1]) / 2
    else:
        output = lastoutput
    print("output:", output)
    #print(output)
    send_data(output)
    lastoutput = output
while(True):
    clock.tick()
    img = sensor.snapshot()
    img.crop(roi = (0, 200, 480,240 ), copy=False)
    #img.crop(roi = (0, 0, 480,40 ), copy=False)
    img.gamma(gamma=1.0, contrast=1.5, brightness=0.0)
#    img.median(1)
    img.median(4)
    img.to_grayscale();
    # Convert to binary
    img.binary([(0,50)], to_bitmap=True)
    kernel = 6
#    img.erode(kernel)
#    img.erode(kernel)
#    img.dilate(kernel)
#    img.dilate(kernel)
    #img.erode()
    print(clock.fps())
    #image_store = process_image(img)
    #img.draw_image(img, 0, 0)
    edge(img)


# import sensor, image, time

# def process_image():
#     sensor.reset()
#     sensor.set_pixformat(sensor.GRAYSCALE)
#     sensor.set_framesize(sensor.QVGA)
#     sensor.skip_frames(time = 2000)

#     img = sensor.snapshot()

#     # Increase contrast
#     img.contrast(3)

#     # Convert to binary
#     img.binary([(100, 255)])

#     # Invert image
#     img.invert()

#     # Remove noise and improve line imperfections
#     img.erode(1)
#     img.dilate(1)

#     # Select the y line and remove all pixels above and below the range
#     img.crop(roi = (0, 0, 320, 60), copy=False)

#     # Find lines
#     lines = img.find_lines(threshold = 4000, theta_margin=20, rho_margin=20)

#     # Count the number of lines
#     num_lines = len(lines)

#     if num_lines == 1:
#         # Find the left point of the top of the range and bottom and determine the direction
#         line = lines[0]
#         img.draw_line(line.line(), color=(255, 0, 0))
#     elif num_lines == 2:
#         # Find the middle point and display it on the image
#         line1, line2 = lines
#         mid_point = ((line1.x1() + line2.x1()) // 2, (line1.y1() + line2.y1()) // 2)
#         img.draw_circle(mid_point[0], mid_point[1], 5, color=(255, 0, 0))

#     return img

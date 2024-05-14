# Line detection - By: dinordi - Tue May 14 2024

import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.HVGA)
sensor.skip_frames(time = 2000)
sensor.set_vflip(True)
#sensor.ioctl(sensor.IOCTL_SET_FOV_WIDE, True)
#sensor.set_hflip(True)
clock = time.clock()

def process_image(img):


#    img = sensor.snapshot()
    img.crop(roi = (0, 140, 400, 180), copy=False)

    img.gamma(gamma=1.0, contrast=1.5, brightness=0.0)

#    img.median(1)
    img.gaussian(1)

    # Convert to binary
    img.binary([(0,50),(254,255),(254,255)], to_bitmap=True)

    # Invert image
#    img.invert()

    lines = img.find_lines(threshold = 16000, theta_margin=1, rho_margin=1)

    num_lines = len(lines)

    print(num_lines)
    img.draw_line(lines[0].line(), color=(255, 0, 0))
    img.draw_line(lines[1].line(), color=(255, 0, 0))
    img.draw_line(lines[2].line(), color=(255, 0, 0))

    # Remove noise and improve line imperfections
#    img.erode(8)
#    img.dilate(8)
#    img.erode(1)

#    # Select the y line and remove all pixels above and below the range
    return img

    threshold = [(1, 1)]
#    # Find lines
    lines = img.find_blobs(threshold)

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

        for x in range(img.width()):
            if img.get_pixel(x, 140) == 1:  # Check if the pixel is white
                bottom = x
#                print("Bottom First white pixel found at x =", x)
                break
        d = top-bottom
        if d > 0:
            print("Facing right")
        else:
            print("Facing left")

    elif num_lines == 2:
#        line1, line2 = lines
        print("Two lines found")
#        mid_point = ((line1.x1() + line2.x1()) // 2, (line1.y1() + line2.y1()) // 2)
#        img.draw_circle(mid_point[0], mid_point[1], 5, color=(255, 0, 0))


    return img


while(True):
    clock.tick()
    img = sensor.snapshot()
#    print(clock.fps())
    img.draw_image(process_image(img), 0, 0)



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

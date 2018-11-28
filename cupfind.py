
import sensor, image, time


#进行边缘增强
def edge_Enhance(img):
    kernel_size = 1 # kernel width = (size*2)+1, kernel height = (size*2)+1
    kernel = [-1, 0,1,\
              -1, 0,1,\
              -1, 0,1]
    thresholds = [(100, 255)] # grayscale thresholds
    img.morph(kernel_size, kernel)
    #img.binary(thresholds)
    return img


#进行茶杯检测
def cup_Detection(img,cup_Width):
    resultList = []
    img = edge_Enhance(img)
    lineList = img.find_lines(threshold = 3000, theta_margin = 50, rho_margin = 25)
    for l in lineList:
        for l1 in lineList:
            if(l.theta()<10)and(l1.theta()<10):
                if(abs(l.x1()-l1.x1())>(cup_Width-5))and(abs(l.x1()-l1.x1())<(cup_Width+5)):
                    resultList.append(l)
                    resultList.append(l1)
                    return resultList
    return resultList



sensor.reset()#
sensor.set_pixformat(sensor.GRAYSCALE) # grayscale is faster
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
clock = time.clock()

min_degree = 0
max_degree = 50

if (sensor.get_id() == sensor.OV7725):
    sensor.__write_reg(0xAC, 0xDF)
    sensor.__write_reg(0x8F, 0xFF)

print(sensor.get_id())
print(sensor.OV7725)

while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    result =cup_Detection(img,40)
    print(len(result))
    for i in result:
        img.draw_line(i.line(), color = (255, 255, 0))

    print("FPS %f" % clock.fps())

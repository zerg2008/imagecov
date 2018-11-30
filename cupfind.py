
import sensor, image, time,pyb


#进行纵向边缘增强
def edge_Enhance_Vertical(img):
    kernel_size = 2 # kernel width = (size*2)+1, kernel height = (size*2)+1
    kernel = [0,-1, 0,1,0,\
              0,-1, 0,1,0,\
              0,-1, 0,1,0,\
              0,-1, 0,1,0,\
              0,-1, 0,1,0]
    thresholds = [(100, 255)] # grayscale thresholds

    kernel1_size = 1 # kernel width = (size*2)+1, kernel height = (size*2)+1
    kernel1 = [-1, -1, -1,\
              -1, +9, -1,\
              -1, -1, -1]
    img.erode(1, threshold = 2)
    img.morph(kernel_size, kernel)
    #img.morph(kernel1_size, kernel1)
    #img.median(1, percentile=0.5)
    img.mean(1)
    #img.mode(1)
    #img.midpoint(1, bias=0.5)
    img.morph(kernel1_size, kernel1)
    #img.binary(thresholds)
    return img


#进行茶杯检测
def cup_Detection(img,cup_Width):
    resultList = []
    theta1_Angle = False
    theta2_Angle = False
    img = edge_Enhance_Vertical(img)
    lineList = img.find_lines(threshold = 3000, theta_margin = 40, rho_margin = 20)
    for l in lineList:
        for l1 in lineList:
            theta1_Angle = True if((l.theta()<10)or(l.theta()>170)) else False
            theta2_Angle = True if((l1.theta()<10)or(l1.theta()>170)) else False
            if(theta1_Angle)and(theta2_Angle):
                if(abs(l.x1()-l1.x1())>(cup_Width-8))and(abs(l.x1()-l1.x1())<(cup_Width+8)):
                    resultList.append(l)
                    resultList.append(l1)
                    return resultList
    return resultList

#对横向边缘进行增强
def edge_Enhance_Horizontal(img):
    kernel_size = 2 # kernel width = (size*2)+1, kernel height = (size*2)+1
    kernel = [0, 0, 0, 0, 0,\
              1, 1, 1, 1, 1,\
              0, 0, 0, 0, 0,\
             -1,-1, -1,-1,-1,\
              0, 0, 0, 0, 0]
    thresholds = [(100, 255)] # grayscale thresholds

    kernel1_size = 1 # kernel width = (size*2)+1, kernel height = (size*2)+1
    kernel1 = [-1, -1, -1,\
              -1, +9, -1,\
              -1, -1, -1]

    img.morph(kernel_size, kernel)
    img.mean(1)
    img.morph(kernel1_size, kernel1)
    return img

#对水位线进行检测
def water_Level_Detection(img,water_Level):
    resultList = []
    img = edge_Enhance_Horizontal(img)
    lineList = img.find_lines(threshold = 3000, theta_margin = 40, rho_margin = 20)
    for l in lineList:
        if(l.theta()>85)and(l.theta()<95):
            if(l.y1()<water_Level):
                resultList.append(l)
                return resultList
    return resultList


led = pyb.LED(2)
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
iCount = 0
haveCount = 0
resultList = []

contral_Switch = False

led.on()
time.sleep(150)
led.off()
while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.5)

    result =cup_Detection(img,70)
    if(len(result)):
        print("result: %d" % len(result))
        haveCount = haveCount +1
        #resultList = result
    iCount = iCount + 1
    if(iCount >= 5):
        print("iCount: %d" % iCount)
        if(haveCount >=2):
            print("haveCount: %d"% haveCount)
            contral_Switch = True
        else:
            contral_Switch = False
        iCount = 0
        haveCount = 0

    # water level detection,if the contral_Switch is true ,
    # it means there is a cup ,then,we need to detect the water level

    if(contral_Switch):
        img = sensor.snapshot().lens_corr(1.5)
        water_Level_Line = water_Level_Detection(img,100)
        if(len(water_Level_Line)):
            for i in water_Level_Line:
                if(i.y1()>80):
                    contral_Switch = False

        #for i in resultList:
            #img.draw_line(i.line(), color = (255, 255, 0))
            #print(i)

    if(contral_Switch):
        time.sleep(150)
        led.on()
    else:
        led.off()
        time.sleep(150)

    print("FPS %f" % clock.fps())

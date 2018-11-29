
import sensor, image, time,pyb




#进行边缘增强
def edge_Enhance(img):
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
    img = edge_Enhance(img)
    lineList = img.find_lines(threshold = 3000, theta_margin = 40, rho_margin = 20)
    for l in lineList:
        for l1 in lineList:
            if(l.theta()<10)and(l1.theta()<10):
                if(abs(l.x1()-l1.x1())>(cup_Width-8))and(abs(l.x1()-l1.x1())<(cup_Width+8)):
                    resultList.append(l)
                    resultList.append(l1)
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

led.on()
time.sleep(150)
led.off()
while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.5)
    #img.morph(kernel_size, kernel)
    #img.binary(thresholds)
    img.erode(1, threshold = 2)
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
            time.sleep(150)
            led.on()
        else:
            time.sleep(150)
            led.off()
        iCount = 0
        haveCount = 0
        #for i in resultList:
            #img.draw_line(i.line(), color = (255, 255, 0))
            #print(i)


    print("FPS %f" % clock.fps())

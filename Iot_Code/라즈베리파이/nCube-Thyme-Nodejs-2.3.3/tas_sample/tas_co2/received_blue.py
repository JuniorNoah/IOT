from bluetooth import *
import struct
from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import time
from threading import Thread

RED   = 0
GREEN = 5
BLUE  = 6
# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 
GPIO.setup(13, GPIO.OUT)
pan = GPIO.PWM(13, 1000)
pan.start(0)
GPIO.setup(12, GPIO.OUT)
humi = GPIO.PWM(12, 1000)
humi.start(0)
GPIO.setup(RED, GPIO.LOW)
GPIO.setup(GREEN, GPIO.LOW)
GPIO.setup(BLUE, GPIO.LOW)
        
#Data Receive and txt file Save
def dataRC():
    msg=client_socket.recv(1024)
    #print(msg)
    temp=float(msg[:5])
    humi=float(msg[5:10])
    dust=float(msg[10:18])
    ppm=float(msg[18:])
    #print("recived temp: %.2f" %temp)
    #print("recived humi: %.2f" %humi)
    #print("recived dust: %.2f" %dust)
    #print("recived ppm: %.2f" %ppm)
    data= [temp,humi,dust,ppm]
    #print(data)
    now = datetime.now()
    wdata = str(now) + "," + str(temp)+","+str(humi)+","+str(dust)+","+str(ppm)

    #print("finished")
    f = open("./rcData.txt", 'w')
    f.write(wdata)
    f.close()
    
#RS Power Management
def powerManage():
    f = open("./powerManage.txt", 'r')
    powerMange = f.readline()
    #Hpower = powerMange[0]
    #Vpower = powerMange[1]
    #heater = powerMange[2]
    #aircon = powerMange[3]
    #print("Hpower : "+Hpower)
    #print("Vpower : "+Vpower)
    #print("heater : "+heater)
    #print("aircon : "+aircon)
    f.close()
    return powerMange

#thead
def work():
    try:
        powerM = powerManage()
        Hpower = powerM[0]
        Vpower = powerM[1]
        heater = powerM[2]
        aircon = powerM[3]
    except:
        Hpower = "0"
        Vpower = "0"
        heater = "0"
        aircon = "0"
    
    if(Hpower == "1"): humi.ChangeDutyCycle(100)
    else : humi.ChangeDutyCycle(0)
    
    if(Vpower == "1"): pan.ChangeDutyCycle(100)
    else : pan.ChangeDutyCycle(0)
    
    if(heater == "1" and aircon == "1"):
        GPIO.output(RED, GPIO.HIGH)
        GPIO.output(GREEN, GPIO.LOW)
        GPIO.output(BLUE, GPIO.HIGH)
    elif(heater == "1"):
        GPIO.output(RED, GPIO.HIGH)
        GPIO.output(GREEN, GPIO.LOW)
        GPIO.output(BLUE, GPIO.LOW)
    elif(aircon == "1"):
        GPIO.o7utput(RED, GPIO.LOW)
        GPIO.output(GREEN, GPIO.LOW)
        GPIO.output(BLUE, GPIO.HIGH)
    else:
        GPIO.output(RED, GPIO.LOW)
        GPIO.output(GREEN, GPIO.LOW)
        GPIO.output(BLUE, GPIO.LOW)
    
    print("Hpower : "+Hpower + " Vpower : "+Vpower + " heater : "+heater + " aircon : "+aircon)

client_socket=BluetoothSocket( RFCOMM )
client_socket.connect(("98:DA:60:01:4F:94",1))
#print("bluetooth Connected")
while True:
    #print("2")
    dataRC()
    work()
    time.sleep(0.6)
client_socket.close()



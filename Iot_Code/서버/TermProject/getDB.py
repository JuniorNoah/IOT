import http.client
import datetime
import socket
import time

# 데이터베이스에서 센싱 데이터 가져오기
def getDB():
    conn = http.client.HTTPConnection("localhost:7579")

    headers = {
        'x-m2m-ri': "12345",
        'x-m2m-origin': "rigin",
        'accept': "application/text",
        'from': "mobius",
        'cache-control': "no-cache",
        'postman-token': "e3348335-8696-7489-fd67-aacc7e9450ca"
        }

    conn.request("GET", "/Mobius/SOPHIE_DEMO/sensor/latest", headers=headers)

    res = conn.getresponse()
    data = res.read()
    sensor = data.decode("utf-8")
    temp_result = sensor.split('con')
    result = temp_result[1]
    print(result)
    result = result.split(",")
    result[0] = result[0].split(":\"")[1]
    result[4] = result[4].split("\"")[0]

    print(result)
    return result


# 기상 API에서 온도 습도 가져오기
def getAPI_TH():
    conn = http.client.HTTPSConnection("api.openweathermap.org")

    headers = {
        'cache-control': "no-cache",
        'postman-token': "a49060ff-160b-b5db-d566-a1dd6df96d43"
        }

    conn.request("GET", "/data/2.5/onecall?lat=36.8065&lon=127.1522&exclude=minutely&appid=8e740cfe9ceb59eef74d95ae4d5dac5d&units=metric&lang=kr", headers=headers)

    res = conn.getresponse()
    data = res.read()

    api = data.decode("utf-8")
    temp = api.split("temp\":")
    temp = temp[1].split(",")[0]

    humi = api.split("humidity\":")
    humi = humi[1].split(",")[0]

    print("Atemp : "+temp+" C")
    print("Ahumi : "+humi+" %")
    return [temp, humi]


# 기상 API에서 공기질 가져오기
def getAPI_P():
    conn = http.client.HTTPConnection("api.openweathermap.org")

    headers = {
        'cache-control': "no-cache",
        'postman-token': "176baa04-b19a-b002-3985-6986b14cf90c"
        }

    conn.request("GET", "/data/2.5/air_pollution?lat=36.8065&lon=127.1522&appid=8e740cfe9ceb59eef74d95ae4d5dac5d", headers=headers)

    res = conn.getresponse()
    data = res.read()

    api = data.decode("utf-8")
    pollution = api.split("aqi\":")
    pollution = pollution[1].split("}")[0]

    print("Apoll : "+pollution)
    return pollution


# 계정 정보 반환
def get_season():
    now = datetime.datetime.now()
    n1 = int(now.strftime("%m"))

    if n1 == 12 or n1 == 1 or n1 == 2:
        result = "winter"
    elif n1 == 3 or n1 == 4 or n1 == 5:
        result = "spring"
    elif n1 == 6 or n1 == 7 or n1 == 8:
        result = "summer"
    elif n1 == 9 or n1 == 10 or n1 == 11:
        result = "fall"
        
    return result


# 엑츄에이터 제어 알고리즘
def power_manage(th, poll):
    db = getDB()
    # Stime = float(db[0]) #센서시간
    Stemp = float(db[1]) #센서온도
    Shumi = float(db[2]) #센서습도
    Sdust = float(db[3]) #센서먼지
    Sgas = float(db[4])  #센서가스

    #api = getAPI_TH()
    api = th
    Atemp = float(api[0]) #api온도
    Ahumi = float(api[1]) #api습도

    # print("atemp : "+str(Atemp))
    # print("ahumi : "+str(Ahumi))

    #Apoll = int(getAPI_P()) 
    Apoll = poll        #api공기오염도
    seaseon = get_season() #계절

    Hpower = 0 #가습기 전원
    Vpower = 0 #환풍기 전원
    Heater = 0 #히터 전원
    Aircon = 0 #에어컨 전원


    #가습기 전원제어
    if( 50.0 < Shumi):
        Hpower = 0
    else:
        Hpower = 1


    #환풍기 전원제어
    if( 4 == Apoll): #외부 공기가 나쁨이라면
        Vpower = 0 #환풍기를 끈다
        if(7000 < Sdust or 15000 < Sgas):
            Vpower = 1
    elif( 5 == Apoll): #외부 공기가 매우 나쁨이라면
        Vpower = 0 
        if(10000 < Sdust or 100000 < Sgas):
            Vpower = 1
    else:
        if(4000 < Sdust or 40000 < Sgas):
            Vpower = 1
        if( 60.0 < Shumi and Shumi < Ahumi):
            Vpower = 1



    #히터,에어컨 전원제어
    if seaseon == "winter" or seaseon == "fall":
        if(18 < Atemp and Stemp < Atemp ):
            Vpower = 1
        elif(Stemp < 18):
            Heater = 1
    else:
        if(Atemp < 20 and Atemp < Stemp ):
            Vpower = 1
        elif(Stemp > 20):
            Aircon = 1

    
    result = str(Hpower) + str(Vpower) + str(Heater) + str(Aircon)
    # print("가습기 : " + str(Hpower))
    # print("환풍기 : " + str(Vpower))
    # print("히터 : " + str(Heater))
    # print("에어컨 : " + str(Aircon))
    return result
        

# 테스트 set
def test_manage():
    result = "1001"
    return result
    
th = getAPI_TH()
poll = int(getAPI_P())

print(power_manage(th, poll))

while(1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    msg = power_manage(th, poll)
    #msg = test_manage()                                    # 시연을 위한 테스트 셋
    sock.sendto(msg.encode(), ("192.168.1.12", 3000))       # 라즈베리 파이 주소

    print("send message: ", msg)
    time.sleep(1.65)
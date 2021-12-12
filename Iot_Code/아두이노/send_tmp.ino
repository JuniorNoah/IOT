#include <SoftwareSerial.h>
#include <DHT11.h>
#include <MQ135.h>
 
int RX=7;
int TX=8;
int t_pin=4;
int d_pin = 10;
int powerPin = 3;
#define PIN_MQ135 A2


unsigned long duration;
unsigned long starttime;
unsigned long sampletime_ms = 30000;//sampe 30s ;
unsigned long lowpulseoccupancy = 0;
float ratio = 0;
float concentration = 0;
char strcon[30] = "     0.0";

SoftwareSerial bluetooth(RX, TX);
DHT11 dht11(t_pin); 
MQ135 mq135_sensor(PIN_MQ135);
 
void setup(){
  pinMode(powerPin, OUTPUT);
  Serial.begin(9600);
  bluetooth.begin(9600);
  pinMode(10, INPUT);
  starttime = millis();//get the current time;
}
 
void loop(){
  int err;
  float temp, humi;
  char strtemp[30];
  char strhumi[30]; 
  char strppm[30];

  // 받기
  if (bluetooth.available()) {
    char data = char(bluetooth.read());
    if(data == '1') analogWrite(powerPin,255);
    else if(data == '0') analogWrite(powerPin,0);
    else{}
  }
  
  // 온습도 센싱
    if((err=dht11.read(humi, temp))==0){
      //String strtemp = "temperature" + String(temp);
      //String strhumi = "huminity"+String(humi);
      dtostrf(temp, 5, 2, strtemp);
      dtostrf(humi, 5, 2, strhumi);
      //bluetooth.write(strtemp);      
      //bluetooth.write(strhumi);
      Serial.print("\nt: ");
      Serial.print(strtemp);
      Serial.print(" / h:");
      Serial.print(strhumi);
    }
    else
    {
      bluetooth.write(Serial.print("Error No :"));
      bluetooth.write(Serial.print(err));
    }

    
  // 먼지 센싱
  duration = pulseIn(d_pin, LOW);
  lowpulseoccupancy += duration;
  if ((millis() - starttime) > sampletime_ms) //every 30 sec.
  {
    ratio = lowpulseoccupancy / (sampletime_ms * 10.0); // Integer percentage 0=>100
    concentration = 1.1 * pow(ratio, 3) - 3.8 * pow(ratio, 2) + 520 * ratio + 0.62; // using spec sheet curve
    //Serial.print("concentration = ");
    Serial.print(" / c:");
    dtostrf(concentration, 8, 2, strcon);
    Serial.print(concentration);
    //Serial.println(" pcs/0.01cf");
    //bluetooth.write(strcon);
    lowpulseoccupancy = 0;
    starttime = millis();
  }
  
  float correctedPPM = mq135_sensor.getCorrectedPPM(temp, humi);
  dtostrf(correctedPPM, 10, 2, strppm);
  Serial.print(" / p: ");
  Serial.print(correctedPPM);
  
  bluetooth.write(strtemp);      
  bluetooth.write(strhumi);
  bluetooth.write(strcon);
  bluetooth.write(strppm);

  delay(DHT11_RETRY_DELAY); //delay for reread

}

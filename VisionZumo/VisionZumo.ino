#include <Zumo32U4.h>
const int toNicla = 13;
const int fromNicla = 14;
const int baudRate = 9600;
const int bitPeriod = 5000; // microseconds
int last_error = 0;
int val = 0;
unsigned int Uval = 0;
float I = 0;
Zumo32U4Motors motors;
Zumo32U4OLED display;
bool NiclaWantsToSend = false;

int time =0;
int time_last    =0;
void pidDrive()
{
 
  time = millis() - time_last;
 
  display.clear();
  display.print(val);
  int error = 188 - val; // calculate error
  float P= 0.50*error; // error correction for P 0.31 GOED
  I = I + ( time * error * 0.000); //0.00013 GOED
  float D= (0*((error-last_error))/time); // calculate error correction for K 15 GOED
//   Serial.print("P: ");
//   Serial.print(P);
//   Serial.print(" D: ");
//   Serial.print(D);
  int speed = 60; // set motorspeed
  motors.setSpeeds(speed+(P+I+D),speed-(P+I+D));
 last_error = error;
 time_last = millis();
 
}
 

void readByte();
// void writeByte();
void setup()
{
  pinMode(toNicla, OUTPUT);
  pinMode(fromNicla, INPUT_PULLUP);
  Serial.begin(9600);
  display.clear();
  display.print(F("Press A"));
  display.clear();
  motors.setSpeeds(100,-100);
  delay(300);
  motors.setSpeeds(0,0);
  delay(1000);
  motors.setSpeeds(-100,100);
  delay(600);
  motors.setSpeeds(0,0);
  delay(1000);
  motors.setSpeeds(100,-100);
  delay(300);
  motors.setSpeeds(0,0);
}

//Reading 0 means a 1 from the nicla
void loop() {
  static int count = 0;
  if(digitalRead(fromNicla)==0 && NiclaWantsToSend != true) //If Nicla wants to send data
  {
  //  Serial.println("Nicla wants to send");
    delay(100);
    NiclaWantsToSend = true;
  }
  if(NiclaWantsToSend)
  {
    readByte();
    digitalWrite(toNicla, LOW);
    if(count > 10)
    pidDrive();
    NiclaWantsToSend = false;
  }
  count++;
}
void readByte()
{
  digitalWrite(toNicla, HIGH); // Acknowledge Nicla
  delay(5); // Wait for stabilization
  
  // Read a byte
  val = 0;
  while (digitalRead(fromNicla) == LOW); // Wait for start bit

  delay(5 * 1.4); // Wait for the middle of the start bit
  digitalWrite(toNicla, LOW);

  for (int offset = 0; offset < 9; offset++) {
    if (digitalRead(fromNicla) == LOW) {
      val |= (1 << offset); // Set bit to 1
    }

    // delayMicroseconds(bitPeriod);
    delay(5);
  }

//  // Check if the last bit is 1 for two's complement
//  if (val & (1 << 8)) {
//    // If it is, convert to two's complement
//    val = ((val | (1 << 15)) & ~(1 << 8));
//  }

  Serial.print("Received: ");
  Serial.println(val);
}

 

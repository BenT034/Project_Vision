#include <Zumo32U4.h>
const int toNicla = 13;
const int fromNicla = 14;
const int baudRate = 9600;
const int bitPeriod = 500000; // microseconds
int last_error = 0;
byte val;
Zumo32U4Motors motors;
Zumo32U4OLED display;
bool NiclaWantsToSend = false;
 
void pidDrive()
{
  display.clear();
  int error = val - 147; // calculate error
  last_error = error;
  float P= 0.2*error; // error correction for P
  float D= (0.01*(error-last_error)); // calculate error correction for K
  int speed = 50; // set motorspeed
  motors.setSpeeds(speed-(P+D),speed+(P+D));
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
}
 
//Reading 0 means a 1 from the nicla
void loop() {
 
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
    pidDrive();
    NiclaWantsToSend = false;
  }
}
void readByte()
{
  digitalWrite(toNicla, HIGH); //Acknowledge Nicla
  // delay(10);
  // Read a byte
  val = 0;
  while (digitalRead(fromNicla) == LOW); // wait for start bit
 
  // delayMicroseconds(bitPeriod*1.4); // wait for the middle of the start bit
  // Serial.println("READ START BIT");
  delay(5*1.4);
  digitalWrite(toNicla, LOW);
  for (int offset = 0; offset < 8; offset++) {
    if (digitalRead(fromNicla) == LOW) {
      val |= (1 << offset);
      // Serial.println("1 READ");
    }
    else
    {
      // Serial.println("0 READ");
    }
 
    // delayMicroseconds(bitPeriod);
    delay(5);
  }
  Serial.print("Received: ");
  Serial.println(val);
}
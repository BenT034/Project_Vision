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
bool sended = 0;
bool pidDriveBool = 0;
int time =0;
int time_last    =0;


// Functie voor het rijden met PID controller
void pidDrive()
{
  time = millis() - time_last;
  int error = 210 - val; // calculate error
  float P = 0.25 * error; 
  I = I + (time * error * 0.000); // not used at this moment
  float D = (20 * ((error - last_error)) / time); // calculate error correction for K 20 GOED
  int baseSpeed = 60; // set base motor speed
  int pidCorrection = (P + I + D);
  int motor1, motor2;
  motor1 = baseSpeed + pidCorrection;
  motor2 = baseSpeed - pidCorrection;
  motors.setSpeeds(motor1, motor2);
  last_error = error;
  time_last = millis();
}

 
void readByte();

void setup()
{
  pinMode(toNicla, OUTPUT);
  pinMode(fromNicla, INPUT_PULLUP);
  Serial.begin(9600);
  display.clear();
  display.print(F("Press A"));
  display.clear();
  pidDriveBool = 1;
}

//Reading 0 means a 1 from the nicla
void loop() {
  loopFunction();
}

bool loopFunction()
{
  NiclaWantsToSend = false;
  if(digitalRead(fromNicla)==0 && NiclaWantsToSend != true) //If Nicla wants to send data
  {
  //  Serial.println("Nicla wants to send");
    delay(100);
    Serial.print("Nicla wants to send");
    NiclaWantsToSend = true;
  }
  if(NiclaWantsToSend) //bool so that the robot won't drive during setup
  {
    readByte();
    digitalWrite(toNicla, LOW);
    if (pidDriveBool)
      pidDrive();
  }
  return NiclaWantsToSend;
}

void readByte()
{
  Serial.print("Reading byte");
  digitalWrite(toNicla, HIGH); // Acknowledge Nicla
  delay(5); // Wait for stabilization
  
  // Read a byte
  val = 0;
  while (digitalRead(fromNicla) == LOW)
  {
   Serial.print("waiting for nicla");          ; // Wait for start bit
  }

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

  //Serial.print("Received: ");
  //Serial.println(val);
  display.clear();
  display.print(val);
}

 

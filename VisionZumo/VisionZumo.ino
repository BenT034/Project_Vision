#include <Zumo32U4.h>
const int toNicla = 13;
const int fromNicla = 14;
const int baudRate = 9600;
const int bitPeriod = 5000; // microseconds
const int baseSpeed = 60;
const int middle = 210;
int last_error = 0;
int received = 0;
float I = 0;
Zumo32U4Motors motors;
Zumo32U4OLED display;
bool NiclaWantsToSend = false;
bool sended = 0;
bool pidDriveBool = 0;
int time =0;
int time_last    =0;
int counter = 0;
int speed = baseSpeed; // set motor speed

// Functie voor het rijden met PID controller
void pidDrive()
{
  time = millis() - time_last;
  int error = middle - received; // calculate error

  float P = 0.21 * error; // error correction for P 0.31 GOED
  I = I + (time * error * 0.000); // 0.00013 GOED
  float D = (20 * ((error - last_error)) / time); // calculate error correction for K 15 GOED

  int pidCorrection = (P + I + D);
  int motor1, motor2;
  motor1 = speed + pidCorrection;
  motor2 = speed - pidCorrection;
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
  if(counter > 10){                   //if the counter is bigger than 10 the basespeed is set to the normal 60
    counter = 0;
    speed = baseSpeed;
  }
  counter++;
  loopFunction();
}
bool loopFunction()
{
  NiclaWantsToSend = false;
  if(digitalRead(fromNicla)==0 && NiclaWantsToSend != true) //If Nicla wants to send data
  {
    delay(100);
    Serial.print("Nicla wants to send");
    NiclaWantsToSend = true;
  }
  if(NiclaWantsToSend) //bool so that the robot won't drive during setup
  {
    readByte();
    digitalWrite(toNicla, LOW);
    if (pidDriveBool){
      pidDrive();
    }
    else{
      switch(received){
        case 1:                       //if the sign of dead end is seen the robot will turn around
          display.clear();
          display.print("dead end");
          motors.setSpeeds(-80,80);
          delay(2300);                 //fine tuning needed for turn around delay
          motors.setSpeeds(0,0);
          break;
        case 2:                       //if a stop sign is detected the robot will stand still for a second and then it continues driving
          display.clear();
          display.print("stop");
          motors.setSpeeds(0,0);
          delay(3000);
          motors.setSpeeds(60,60);
          delay(500);
          break;

        case 3:
          display.clear();
          display.print("green");

          break;
        case 4:
          display.clear();
          display.print("orange");
          speed = 110;
          counter = 0;
          break;
        
        case 5:                       //if the robot sees it is on a priority road it will speed up
          display.clear();
          display.print("priority");
          speed = 90;
          counter = 0;
          break;
        case 6:                       //the robot sees a sign that it cannot park here but it can stand still so it will move to the right of the road and stand still
          display.clear();
          display.print("cant park");
          for(int i = 0; i < 12;i++){  //the loop is used to alter the normal pid drive so the robot moves to the right
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
            received = received - 50;           //this line of code cause the error to be 50 smaller so the robot moves to the right
            digitalWrite(toNicla, LOW);
            if (pidDriveBool)
              pidDrive();
            }
          }
          motors.setSpeeds(0,0);      //the robot stops for half a second and then it will continue driving normally
          delay(4000);
          break;
        case 7:
          display.clear();
          display.print("red");
          motors.setSpeeds(0,0);
          delay(3000);
          motors.setSpeeds(60,60);
          delay(500);
          break; 
        case 8:                       //the robot sees a 90 degree turn or a T-junction so it will turn to the right
          motors.setSpeeds(60, 60);
          delay(850);
          motors.setSpeeds(100,-100);
          delay(800);
          motors.setSpeeds(0,0);
          break;

      }
    }
  }
  return NiclaWantsToSend;
}



void readByte()
{
  Serial.print("Reading byte");
  digitalWrite(toNicla, HIGH); // Acknowledge Nicla
  delay(5); // Wait for stabilization
  // Read a byte
  received = 0;
  while (digitalRead(fromNicla) == LOW)
  {
   Serial.print("waiting for nicla");          ; // Wait for start bit
  }
  delay(5 * 1.4); // Wait for the middle of the start bit
  digitalWrite(toNicla, LOW);
  for (int offset = 0; offset < 9; offset++) {  //9 bits value for a maximum value of 511
    if (digitalRead(fromNicla) == LOW) {
      received |= (1 << offset); // Set bit to 1
    }
    delay(5);
  }
  if (digitalRead(fromNicla) == LOW) {
      pidDriveBool = false;                      //set pidDriveBool to false when another function is sent by the nicla
    }
    else{
      pidDriveBool = true;                       //set pidDriveBool to true when nicla sends the error
    }
    delay(5);
  display.clear();
  display.print(received);
  display.print(pidDriveBool);
}
 

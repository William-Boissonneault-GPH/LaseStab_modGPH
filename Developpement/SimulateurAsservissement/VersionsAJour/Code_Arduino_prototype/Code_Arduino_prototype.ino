#include <Arduino.h>
#include <avr/interrupt.h> // Needed for ISR definitions
#include <math.h>          // For the log() function

void shiftZ(float arr[]){
  arr[2] = arr[1];
  arr[1] = arr[0];
  arr[0] = 999;
};
// Pin assignments
const int THERMISTOR1_PIN = A0;
const int THERMISTOR2_PIN = A1;
const int THERMISTOR3_PIN = A2;
const int PWM_OUTPUT_PIN   = 5;  // PWM pin for analog-like output


//Température Ambiante
const float Tamb = 24.0;
const float TempMax = 35.0;
const float TempMin = 15.0;
volatile float T_vise = 24.0;
volatile float T_asserv = 24.0;  //Pour anti wind-up

////Lecture de température
// Résistance pull-up et constante de la thermistance
const float R25 = 10000.0;      // Résistance nominale à 25 °C (10 kΩ)
// Coefficients pour le calcul de la température
const float A1_coeff = 0.003354;
const float B1_coeff = 0.00026;
const float C1_coeff = 2.6e-6;
const float D1_coeff = 6.3e-8;
//Conditionneur
const float gainConditionneur = 4.35;
const float VsubConditionneur = 1.95;
//Diviseur de tension
const float R_PULLUP = 10000.0; // Résistance pull-up (10 kΩ)

////Driving du TEC
const float GainSourceCourant = 3.1564;
const float GainAmpereVersVcontrole = 1 / GainSourceCourant;
const float VsubControle = 0.8323;

//Initialisation Temperature initiale (updated in the ISR)
//[T, T-1, T-2, T-3]
volatile float T1[3] = {Tamb, Tamb, Tamb};
volatile float T2[3] = {Tamb, Tamb, Tamb};
volatile float T3[3] = {Tamb, Tamb, Tamb};

volatile float T3_EST[3] = {Tamb, Tamb, Tamb};

float clock = 0;
//Regulateur temporaire
volatile float REG[6] = {1.0, -1.9104, 0.9115, 1.0, -1.9257, 0.9257};

//Selection d'asservissement basé sur Estimé (0) ou sur T3 (1)
volatile int Asserv_T3EST_False_T3_True = 0;

//////////////////////////////////////
//SECTION DE COMMANDE D'ASSERVISSEMENT
/////////////////////////////////////
volatile float ERREUR[3] = {0.0, 0.0, 0.0};
volatile float COMMANDE[3] = {0.0, 0.0, 0.0};

float DELTAT3_based_T2[3] = {0.0, 0.0, 0.0};
float DELTAT3_based_T1[3] = {0.0, 0.0, 0.0};


void calculerMeilleurRegulateur(float consigne) {
  //Calculer quel régulateur en fonction de la consigne!
  
  //pour l'instant régulateur fixe
  float num0 = 1.0;
  float num1 = -1.9104;
  float num2 = 0.9115;

  float deno0 = 1.0;
  float deno1 = -1.9257;
  float deno2 = 0.9257;

  REG[0] = num0;
  REG[1] = num1;
  REG[2] = num2;
  REG[3] = deno0;
  REG[4] = deno1;
  REG[5] = deno2;
};

float Comparateur(float T_consigne, float T3_asserv[]){
  float erreur = T_consigne - T3_asserv[0];

  //Début d'une nouvelle boucle, repousse toute les valeurs!
  shiftZ(ERREUR);
  shiftZ(COMMANDE);
  shiftZ(T1);
  shiftZ(T2);
  shiftZ(T3);
  shiftZ(T3_EST);
  shiftZ(DELTAT3_based_T2);
  shiftZ(DELTAT3_based_T1);

  ERREUR[0] = erreur;
  return erreur;
};

float Regulateur() {
  float GainREG = 0.5;
  //Commande = Amperage voulu
  float Commande = REG[0]*ERREUR[0]*GainREG;
  Commande += REG[1]*ERREUR[1]*GainREG;
  Commande += REG[2]*ERREUR[2]*GainREG;
  Commande -= REG[4]*COMMANDE[1];
  Commande -= REG[5]*COMMANDE[2];

  Commande = (Commande / REG[3]);
  COMMANDE[0] = Commande;
  //Anti wind up flag d'erreur?
  return Commande;
};


//////////////////////////////////////
//SECTION : Mesures 
/////////////////////////////////////

float recalculerEstimateurAjuster() {
  //Ajustment de l'estimateur de temperature

};

float estimateurT3() {
  float GT1T3[6] = {0.0, 0.0031, 0.0028, 1.0, -1.7751, 0.7841};
  float GT2T3[4] = {0.0, 0.0833, 1.0, -0.9024};

  float alpha = 0.5;
  float beta = 1.0 - alpha; 

  ///DELTAT3_based_T2
  float DeltaT3_b_T2 = (T2[0]-Tamb)*GT2T3[0];
  DeltaT3_b_T2 += (T2[1]-Tamb)*GT2T3[1];
  DeltaT3_b_T2 -= (DELTAT3_based_T2[1])*GT2T3[3];
  DeltaT3_b_T2 = DeltaT3_b_T2 / GT2T3[2];

  DELTAT3_based_T2[0] = DeltaT3_b_T2;



  ///DELTAT3_based_T1
  float DeltaT3_b_T1 = (T1[0]-Tamb)*GT1T3[0];
  DeltaT3_b_T1 += (T1[1]-Tamb)*GT1T3[1];
  DeltaT3_b_T1 += (T1[2]-Tamb)*GT1T3[2];
  DeltaT3_b_T1 -= (DELTAT3_based_T1[1])*GT1T3[4];
  DeltaT3_b_T1 -= (DELTAT3_based_T1[2])*GT1T3[5];
  DeltaT3_b_T1 = DeltaT3_b_T1 / GT1T3[3];

  DELTAT3_based_T1[0] = DeltaT3_b_T1;

  float dT = DeltaT3_b_T1 * alpha + DeltaT3_b_T2 * beta;

  float T3_estime = Tamb + dT;
  T3_EST[0] = T3_estime;
  return T3_estime;
};

float traduireTemperatureC(int adcValue) {
  // ADC vers v_in (dans pins)

  float V_in = (adcValue * 5.0) / 1023.0;

  // Calculer V_out_diviseur (tension sortant diviseur):
  float V_out_div = (V_in / gainConditionneur) + VsubConditionneur;

  // Calculer Resistance
  float rThermoRes = R_PULLUP * ( V_out_div / (5.0 - V_out_div) );

  float lnR = log(rThermoRes / R25);
  float temperatureKelvin = 1.0 / (A1_coeff + B1_coeff * lnR + C1_coeff * pow(lnR, 2.0) + D1_coeff * pow(lnR, 3.0));

  return temperatureKelvin - 273.15;
}

//////////////////////////////////////
//SECTION : Controle TEC
/////////////////////////////////////

int CommandeVersPWM(float Commande) {

  float V_controle = GainAmpereVersVcontrole * Commande;

  float DutyCycle = 100.0 * (V_controle + VsubControle) / (2*VsubControle);
  int PWMout = 2.55 * DutyCycle;

  // Ensure PWMout is within 0-255
  PWMout = constrain(PWMout, 0, 255);
  return PWMout;
};

// ============ SETUP ============

void setup() {
  Serial.begin(9600);
  pinMode(PWM_OUTPUT_PIN, OUTPUT);
  pinMode(THERMISTOR1_PIN, INPUT);
  pinMode(THERMISTOR2_PIN, INPUT);
  pinMode(THERMISTOR3_PIN, INPUT);
  
  noInterrupts();          // Disable interrupts while configuring Timer1
  TCCR1A = 0;              // Clear Timer1 control registers
  TCCR1B = 0;
  TCNT1  = 0;              // Initialize counter to 0
  
  // Configure Timer1 for a 0.01 s interrupt:
  // For a 16 MHz clock with 1024 prescaler:
  //   Counts per second = 16,000,000 / 1024 ≈ 15625.
  // For 2 s period, compare value = 15625 * 0.01 ≈ 156.25, so use OCR1A = 156.
  OCR1A  = 31250;          
  TCCR1B |= (1 << WGM12);              // CTC mode: Clear Timer on Compare Match
  TCCR1B |= (1 << CS12) | (1 << CS10);   // Prescaler 1024
  TIMSK1 |= (1 << OCIE1A);               // Enable compare-match interrupt
  interrupts();                        // Enable global interrupts
}

// ============ MAIN LOOP ============

void loop() {
  //ECOUTE POUR COMMUNICATION SERIAL (CHANGEMENT DE CONSIGNE)
  if (Serial.available()) {
    String command = Serial.readString();
    if (command.startsWith("SETPOINT:")) {
      T_vise = command.substring(9).toFloat();  // Extract setpoint value
    }

    if (command.startsWith("ASSERVT3:")) {
      Asserv_T3EST_False_T3_True = command.substring(9).toInt();  // Extract setpoint value
    }
  }

  delay(500);  // 1 second delay for readability
}

ISR(TIMER1_COMPA_vect) {
  clock += 2;

  //Anti wind-up
  T_asserv = T_vise;
  if (T_vise > TempMax){
    T_asserv = TempMax;
  } else if (T_vise < TempMin){
    T_asserv = TempMin;
  } 

  float e;
  //1. Comparateur et shift de mémoire, ERREUR OK
  if (Asserv_T3EST_False_T3_True == 0){
    e = Comparateur(T_asserv, T3_EST);
  }else{
    e = Comparateur(T_asserv, T3);
  }

  Serial.print("erreur:");
  Serial.print(e);

  //2. Regulateur, COMMANDE OK
  float c = Regulateur();

  //3. Changer la commande
  int PWM_commande = CommandeVersPWM(c);
  analogWrite(PWM_OUTPUT_PIN, PWM_commande);
  //analogWrite(PWM_OUTPUT_PIN, 127);

  Serial.print(",  PWM comande :");
  Serial.print(PWM_commande);
  Serial.print(", Setpoint :");
  Serial.println(T_vise);


  //4. Mesurer T
  int adcValue1 = analogRead(THERMISTOR1_PIN);
  int adcValue2 = analogRead(THERMISTOR2_PIN);
  int adcValue3 = analogRead(THERMISTOR3_PIN);

  T1[0] = traduireTemperatureC(adcValue1);
  T2[0] = traduireTemperatureC(adcValue2);
  T3[0] = traduireTemperatureC(adcValue3);

  //5. Estimer T3
  float t3_estime = estimateurT3();

  //6. Envoyer données pour log et interfaces
  Serial.print(clock);
  Serial.print(",");
  Serial.print(T1[0]);
  Serial.print(",");
  Serial.print(T2[0]);
  Serial.print(",");
  Serial.print(t3_estime);
  Serial.print(",");
  Serial.println(T3[0]);
}

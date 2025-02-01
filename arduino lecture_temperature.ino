// Configuration des broches des thermistances
const int THERMISTOR1_PIN = A0;
const int THERMISTOR2_PIN = A1;
const int THERMISTOR3_PIN = A2;

// Résistance pull-up et constante de la thermistance
const float R_PULLUP = 10000.0; // Résistance pull-up (10 kΩ)
const float R25 = 10000.0;      // Résistance nominale à 25 °C (10 kΩ)

// Coefficients pour le calcul de la température
const float A1_coeff = 0.00335;
const float B1_coeff = 0.00026;
const float C1_coeff = 2.6e-6;
const float D1_coeff = 6.3e-8;

// Fonction pour lire la tension
float lireTension(int pin) {
  int analogValue = analogRead(pin);
  return analogValue * (5.0 / 1023.0);
}

// Fonction pour calculer la résistance
float calculerResistance(float tension) {
  return (R_PULLUP * tension) / (5.0 - tension);
}

// Fonction pour calculer la température
float calculerTemperature(float resistance) {
  float lnR = log(resistance / R25);
  float temperatureKelvin = 1.0 / (A1_coeff + B1_coeff * lnR + C1_coeff * pow(lnR, 2) + D1_coeff * pow(lnR, 3));
  return temperatureKelvin - 273.15; // Conversion en °C
}

void setup() {
  // Initialisation du port série
  Serial.begin(9600);
  Serial.println("Temps (s), T1 (°C), T2 (°C), T3 (°C)"); // En-tête CSV
}

void loop() {
  static unsigned long startTime = millis();
  unsigned long elapsedTime = (millis() - startTime) / 1000; // Temps écoulé en secondes

  // Lecture des tensions
  float tension1 = lireTension(THERMISTOR1_PIN);
  float tension2 = lireTension(THERMISTOR2_PIN);
  float tension3 = lireTension(THERMISTOR3_PIN);

  // Calcul des résistances
  float resistance1 = calculerResistance(tension1);
  float resistance2 = calculerResistance(tension2);
  float resistance3 = calculerResistance(tension3);

  // Calcul des températures
  float temperature1 = calculerTemperature(resistance1);
  float temperature2 = calculerTemperature(resistance2);
  float temperature3 = calculerTemperature(resistance3);

  // Envoi des données au port série
  Serial.print(elapsedTime);
  Serial.print(",");
  Serial.print(temperature1);
  Serial.print(",");
  Serial.print(temperature2);
  Serial.print(",");
  Serial.println(temperature3);

  delay(1000); // Pause entre les mesures (1 seconde)
}

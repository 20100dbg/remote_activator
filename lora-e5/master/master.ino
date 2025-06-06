#include <RadioLib.h>

// no need to configure pins, signals are routed to the radio internally
STM32WLx radio = new STM32WLx_Module();

// set RF switch configuration for Nucleo WL55JC1
// NOTE: other boards may be different!
//       Some boards may not have either LP or HP.
//       For those, do not set the LP/HP entry in the table.
static const uint32_t rfswitch_pins[] = {PC_3,  PC_4,  PC_5, RADIOLIB_NC, RADIOLIB_NC};
static const Module::RfSwitchMode_t rfswitch_table[] = {
  {STM32WLx::MODE_IDLE,  {LOW,  LOW,  LOW}},
  {STM32WLx::MODE_RX,    {HIGH, HIGH, LOW}},
  {STM32WLx::MODE_TX_LP, {HIGH, HIGH, HIGH}},
  {STM32WLx::MODE_TX_HP, {HIGH, LOW,  HIGH}},
  END_OF_MODE_TABLE,
};

static const int max_size = 256;
byte serial_buffer[max_size];


volatile bool receivedFlag = false;
void setFlag(void) {
  receivedFlag = true;
}


void setup() {
  Serial.begin(115200);
  Serial.setTimeout(100);

  // set RF switch control configuration
  // this has to be done prior to calling begin()
  radio.setRfSwitchTable(rfswitch_pins, rfswitch_table);

  float freq = 495.5; //150-960mhz
  float bw = 250.0; //125,250,500
  uint8_t sf = 10; //7,8,9,10,11,12
  uint8_t cr = 6; //5,6,7,8
  uint8_t syncWord = RADIOLIB_SX126X_SYNC_WORD_PRIVATE;
  int8_t power = 22; //22, 17, 14, 10
  uint16_t preambleLength = 8;

  int state = radio.begin(freq, bw, sf, cr, syncWord, power, preambleLength);
  // set appropriate TCXO voltage for Nucleo WL55JC1
  //state = radio.setTCXO(1.7);
  
  radio.setDio1Action(setFlag);
  radio.startReceive();
  Serial.print("ready");
}


void loop() {

  if(receivedFlag) {
    receivedFlag = false;

    int count = radio.getPacketLength(true);

    if (count > 0) {
      byte received_buffer[count];
      int state = radio.readData(received_buffer, count);


      if (state == RADIOLIB_ERR_NONE) {
        Serial.write(received_buffer, count);
      }
    }
  }
  
  size_t count = Serial.readBytes(serial_buffer, max_size);
  
  if (count > 0) {
    
    radio.clearDio1Action();

    byte send_buffer[count];
    memcpy(send_buffer, serial_buffer, count);
    radio.transmit(send_buffer, count);
    
    radio.setDio1Action(setFlag);
    radio.startReceive();
  }

}

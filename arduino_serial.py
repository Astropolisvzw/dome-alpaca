from serial import Serial
import serial
import encoder_checksum as ec
import logging

class ArduinoSerial:
    serial_port = None
    characterT = 'T'.encode('utf-8')
    characterP = 'P'.encode('utf-8')
    characterR = 'R'.encode('utf-8')
    version = 0x40 # @ char

    def __init__(self, port, baud=9600, timeout=5):
        self.serial_port = Serial(port=port,
                        baudrate = baud,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS,
                        timeout=timeout)

    # Deleting (Calling destructor)
    def __del__(self):
        self.close()

    def close(self):
        if self.serial_port is not None:
            self.serial_port.close()

    def get_version(self):
        return self._send_command_with_one_result(self.version)

    def get_steps(self):
        _, result, check, _, _ = self._send_command_with_two_results(self.characterP)
        return result, check

    def get_turns(self):
        _, result, check, _, _ = self._send_command_with_two_results(self.characterT)
        return result, check

    def _process_results(self, lowbyte, highbyte):
            try:
                lowh = int(lowbyte.hex(), 16)
                # print("lowbyte is", lowh)
                highh = int(highbyte.hex(), 16)
                # print("highbyte is", highh)
                wordresult = ec.bytes_to_word(lowh, highh)
            except Exception as e:
                print("Error with result:", lowbyte, highbyte, e)
                return -1, -1
            real_value = ec.get_result(wordresult)
            return wordresult, real_value

    def _send_command_with_one_result(self, command):
            logging.debug(f"Writing {command}")
            self.serial_port.write(command)
            result = self.serial_port.read(1)
            return result

    def _send_command_with_two_results(self, command):
        logging.debug(f"ArduinoSerial: writing {command}")
        self.serial_port.write(command)
        plowbyte = self.serial_port.read(1)
        phighbyte = self.serial_port.read(1)
        logging.debug(f"ArduinoSerial: received {command} result: {plowbyte}, {phighbyte}")
        resp, real_result = self._process_results(plowbyte, phighbyte)
        check = ec.check_checksum(resp)
        return resp, real_result, check, plowbyte, phighbyte




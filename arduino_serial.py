from typing import List
from serial import Serial
import serial
import encoder_checksum as ec
import logging
import struct
from utils import synchronized_method, Relay

class ArduinoSerial:
    serial_port = None
    characterT = 'T'.encode('utf-8')
    characterP = 'P'.encode('utf-8')
    characterR = 'R'.encode('utf-8')
    characterN = 'N'.encode('utf-8')
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
        return self._generic_send_command_get_result([self.version], 1)

    def get_steps(self):
        _, result, check, _, _ = self._send_command_to_AMT(self.characterP)
        logging.info(f"Arduino steps:{result}, {check=}")
        return result, check

    def get_turns(self):
        _, result, check, _, _ = self._send_command_to_AMT(self.characterT)
        logging.info(f"Arduino turns:{result}, {check=}")
        return result, check

    def enable_relay(self, relayNr: Relay, seconds):
        results = self._generic_send_command_get_result([self.characterN, relayNr.value, seconds], 1)
        if len(results) != 1 and results[0] != seconds:
            logging.error("Did not receive expected result, {results=}")

    def disable_relay(self, relayNr: Relay):
        self.enable_relay(relayNr, 0)

    def disable_all_relays(self):
        for relay in Relay:
            self.disable_relay(relay)

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


    @synchronized_method
    def _generic_send_command_get_result(self, commands, nr_results: int):
            results = []
            for command in commands:
                # current commands are either pre-UTF8'ed strings, or ints that need to be packed
                if isinstance(command, int):
                    self.serial_port.write(struct.pack('!B',command))
                else:
                    self.serial_port.write(command)

            for _ in range(0, nr_results):
                results.append(self.serial_port.read(1))

            return results

    def _send_command_to_AMT(self, command):
        plowbyte, phighbyte = self._generic_send_command_get_result([command], 2)
        # logging.debug(f"ArduinoSerial: received {str(command)} result: {int(plowbyte.hex(),16):02x} {int(phighbyte.hex(),16):02x}")
        resp, real_result = self._process_results(plowbyte, phighbyte)
        check = ec.check_checksum(resp)
        return resp, real_result, check, plowbyte, phighbyte




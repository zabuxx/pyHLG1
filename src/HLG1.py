# SPDX-License-Identifier:  AGPL-3.0-or-later

import serial
import logging

class HLG1:
    def __init__(self,
                 serial_device = "/dev/ttyUSB0",
                 baud=115200,
                 id = "01"):
        self.cmd_base = "%" + id + "#"
        try:
            self.serial = serial.Serial(serial_device, baud, timeout=1)
        except:
            print("Failed to connecto to device", serial_device)
            sys.exit(1)

        logging.info("Connected to " + self.serial.name)
        

    def snd_cmd(self, cmd, sub_cmd="", sub_cmd_chr="+"):
        cmd_full = self.cmd_base + cmd

        if sub_cmd:
            cmd_full += sub_cmd_chr + sub_cmd

        cmd_full += "**\r"

        logging.debug("Sending:" + cmd_full)
        self.serial.write(cmd_full.encode())

    def rcv_output(self):
        x = " "

        result = bytes()
        while x != b"\r":
            x = self.serial.read(1)
            result += x

        logging.debug("Received:" + result.decode("ASCII"))

        return result

    def check_error(self, output):
        if output[3:4] == b"!":
            error_code = output[4:6].decode("ASCII")
            
            logging.warning("Rcv Error " + error_code + " : ")
            match output[4:6].decode("ASCII"):
                case "01":
                    logging.warning("!! Command error")
                case "02":
                    logging.warning("!! Address error")
                case "03":
                    logging.warning("!! Data error")
                case "04":
                    logging.warning("!! BCC error")
                case "11":
                    logging.warning("!! Communication error")
                case "21":
                    logging.warning("!! Control flow error")
                case "22":
                    logging.warning("!! Execution error")
                case "31":
                    logging.warning("!! Buffering condition error 1")
                case "32":
                    logging.warning("!! Buffering condition error 2")   
                case "33":
                    logging.warning("!! Buffering condition error 3")
                case _:
                    logging.warning("!! Unknown error code")

            return True
        return False
                    

    
    def get_sampling_cycle(self):
        logging.info("Samplerate= ")
        
        self.snd_cmd("RSP")
        output = self.rcv_output()

        if(self.check_error(output)):
            return 

        match chr(output[12]):
            case "0":
                logging.info("  200 us")
            case "1":
                logging.info("  500 us")
            case "2":
                logging.info("  1 ms")
            case "3":
                logging.info("  2 ms")
            case _:
                logging.info("  Unknown!")

        return chr(output[12])

    def get_shutter_time(self):
        logging.info("Shutter time= ")
        
        self.snd_cmd("RFB")
        output = self.rcv_output()

        if(self.check_error(output)):
            return 
        
        val = output[11:13].decode("ASCII")

        if val == "00":
            logging.info("  Auto")
        else:
            logging.info("  " + val)

        return output[11:13].decode("ASCII")

    def get_measurement(self):
        logging.info("Measurement=")
        self.snd_cmd("RMD")
        output = self.rcv_output()

        if(self.check_error(output)):
            return 

        logging.info(output[8:15].decode("ASCII"))
        
        return int(output[7:15].decode("ASCII"))

    def get_buffering_mode(self):
        logging.info("Buffering mode= ")        
        
        self.snd_cmd("RBD")
        output = self.rcv_output()

        if(self.check_error(output)):
            return 
        
        if output[12:13] == b"1":
            logging.info("  Triggered")
        else:
            logging.info("  Continuous")

    def set_buffering_mode(self, triggered=True):

        logging.info("Setting buffering mode")
        
        cmd = "WBD"
        if triggered:
            sub_cmd = "00001"
        else:
            sub_cmd = "00000"

        self.snd_cmd(cmd, sub_cmd)
        output = self.rcv_output()

        if(self.check_error(output)):
            return 


    def get_buffering_operation(self):
        logging.info("Buffering operation= ")
        
        self.snd_cmd("RBS")

        output = self.rcv_output()
        
        if(self.check_error(output)):
            return 

        if output[12:13] == b"1":
            logging.info("  Start")
        else:
            logging.info("  Stop")

    def set_buffering_operation(self, start=True):
        logging.info("Setting buffering operation")

        cmd = "WBS"
        if start:
            sub_cmd = "00001"
        else:
            sub_cmd = "00000"

        self.snd_cmd(cmd, sub_cmd)
        output = self.rcv_output()

        if(self.check_error(output)):
            return 
        

    def get_buffering_status(self):
        logging.info("Buffering status= ")
        
        self.snd_cmd("RTS")
        output = self.rcv_output()


        if(self.check_error(output)):
            return

        match output[12:13].decode("ASCII"):
            case "0":
                logging.info("  None-buffering")
            case "1":
                logging.info("  Wait for trigger")
            case "2":
                logging.info("  Accumulating")
            case "3":
                logging.info("  Accumulation completed")
            case _:
                logging.info("  Unknown!")

        return output[12:13].decode("ASCII")

    def get_last_datapoint(self):
        logging.info("Last datapoint= ")

        self.snd_cmd("RLD")
        output = self.rcv_output()

        logging.info("  " + output[9:13].decode("ASCII"))

        
        return int(output[9:13].decode("ASCII"))
        
    
    def read_data(self):
        logging.info("Setting read data")
        

        samples = self.get_last_datapoint()

        start_str = str(1).zfill(5)
        end_str   = str(samples).zfill(5)
        self.snd_cmd("RLA",start_str+end_str,"")

        output = self.rcv_output()
        
        if(self.check_error(output)):
            return

        output_str_lst = output[8:-3].decode("ASCII").replace("-", " -").replace("+", " ").split(" ")
        output_int_lst = [ int(i) for i in output_str_lst ]

        
        logging.info("  all data received ")

        return output_int_lst

        

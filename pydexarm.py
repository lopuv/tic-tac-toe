import serial
import re
import math


class Dexarm:

    # def  rotate_to(angle, speed, port):
    #     ser = serial.Serial('COM3', baudrate=115200, timeout=1)
    #     gcode= f"G0 R{angle} F{speed}\n"
    #     ser.write(gcode.encode())
    #     while ser.in_waiting == 0:
    #         pass
    #     response = ser.read(ser.in_waiting).decode()
    #     print(response)
    #     ser.close()

    def __init__(self, port):
        self.ser = serial.Serial(port, 115200, timeout=None)
        self.is_open = self.ser.isOpen()
        if self.is_open:
            print('pydexarm: %s open' % self.ser.name)
        else:
            print('Failed to open serial port')

    def _send_cmd(self, data):
        self.ser.write(data.encode())
        while True:
            str = self.ser.readline().decode("utf-8")
            if len(str) > 0:
                if str.find("ok") > -1:
                    print("read ok")
                    break
                else:
                    print("read：", str)

    def go_home(self):
        self._send_cmd("M1112\r")

    def set_workorigin(self):
        self._send_cmd("G92 X0 Y0 Z0 E0\r")

    def set_acceleration(self, acceleration, travel_acceleration, retract_acceleration=60):
        cmd = "M204" + "P" + str(acceleration) + "T" + str(travel_acceleration) + "T" + str(
            retract_acceleration) + "\r\n"
        self._send_cmd(cmd)

    def set_module_kind(self, kind):
        self._send_cmd("M888 P" + str(kind) + "\r")

    def get_module_kind(self):
        self.ser.write('M888\r'.encode())
        while True:
            str = self.ser.readline().decode("utf-8")
            if len(str) > 0:
                if str.find("PEN") > -1:
                    module_kind = 'PEN'
                if str.find("LASER") > -1:
                    module_kind = 'LASER'
                if str.find("PUMP") > -1:
                    module_kind = 'PUMP'
                if str.find("3D") > -1:
                    module_kind = '3D'
            if len(str) > 0:
                if str.find("ok") > -1:
                    return module_kind

    def move_to(self, x, y, z, feedrate=6000):
        cmd = "G1" + "F" + str(feedrate) + "X" + str(x) + "Y" + str(y) + "Z" + str(z) + "\r\n"
        self._send_cmd(cmd)

    def fast_move_to(self, x, y, z, feedrate=6000):
        cmd = "G0" + "F" + str(feedrate) + "X" + str(x) + "Y" + str(y) + "Z" + str(z) + "\r\n"
        self._send_cmd(cmd)

    def get_position(self):

        # Envía un comando para obtener la posición actual del brazo robótico
        self.ser.write(b"M114\n")

        # Lee la respuesta del brazo robótico y extrae las coordenadas cartesianas
        response = self.ser.readline().decode().strip()

        # Imprimir la respuesta del brazo robótico para depuración
        print(response)

        # Analizar la respuesta para obtener las coordenadas 'x' y 'y'
        pattern = re.compile(r"X:([-0-9]+) Y:([-0-9]+) Z:([-0-9]+) A:([-0-9]+) B:([-0-9]+) C:([-0-9]+)")
        match = pattern.search(response)
        if match:
            x = int(match.group(1))
            y = int(match.group(2))
            return x, y
        else:
            raise ValueError("Coordenadas no encontradas en la respuesta del brazo robótico")

    def get_x(self):
        self.ser.reset_input_buffer()
        self.ser.write('M114\r'.encode())
        x = None
        while True:
            serial_str = self.ser.readline().decode("utf-8")
            if len(serial_str) > 0:
                if serial_str.find("X:") > -1:
                    temp = re.findall(r"[-+]?\d*\.\d+|\d+", serial_str)
                    x = float(temp[0])
            if len(serial_str) > 0:
                if serial_str.find("ok") > -1:
                    return x
            print(x)

    def get_current_position(self):
        """
        Get the current position
        
        Returns:
            position x,y,z, extrusion e, and dexarm theta a,b,c
        """
        self.ser.reset_input_buffer()
        self.ser.write('M114\r'.encode())
        x, y = None, None,
        while True:
            serial_str = self.ser.readline().decode("utf-8")
            if len(serial_str) > 0:
                if serial_str.find("X:") > -1:
                    temp = re.findall(r"[-+]?\d*\.\d+|\d+", serial_str)
                    x = float(temp[0])
                    y = float(temp[1])
            if len(serial_str) > 0:
                if serial_str.find("ok") > -1:
                    return x, y

    """Delay"""

    def dealy_ms(self, value):
        self._send_cmd("G4 P" + str(value) + '\r')

    def dealy_s(self, value):
        self._send_cmd("G4 S" + str(value) + '\r')

    """SoftGripper & AirPicker"""

    def soft_gripper_pick(self):
        self._send_cmd("M1001\r")

    def soft_gripper_place(self):
        self._send_cmd("M1000\r")

    def soft_gripper_nature(self):
        self._send_cmd("M1002\r")

    def soft_gripper_stop(self):
        self._send_cmd("M1003\r")

    def air_picker_pick(self):
        self._send_cmd("M1000\r")

    def air_picker_place(self):
        self._send_cmd("M1001\r")

    def air_picker_nature(self):
        self._send_cmd("M1002\r")

    def air_picker_stop(self):
        self._send_cmd("M1003\r")

    """Laser"""

    def laser_on(self, value=0):
        self._send_cmd("M3 S" + str(value) + '\r')

    def laser_off(self):
        self._send_cmd("M5\r")

    """Conveyor Belt"""

    def conveyor_belt_forward(self, speed=0):
        self._send_cmd("M2012 S" + str(speed) + 'D0\r')

    def conveyor_belt_backward(self, speed=0):
        self._send_cmd("M2012 S" + str(speed) + 'D1\r')

    def conveyor_belt_stop(self, speed=0):
        self._send_cmd("M2013\r")

    def relative_mode(self):
        self._send_cmd("G91\r")

    def absolute_mode(self):
        self._send_cmd("G90\r")

    def grid(self):
        self.go_home
        self.absolute_mode()
        self.set_acceleration(0, 0, 4000)
        self.move_to(-30, 310, -83)
        self.move_to(30, 310, -83)
        self.move_to(30, 310, 0)
        self.move_to(-30, 290, 0)
        self.move_to(-30, 290, -83)
        self.move_to(30, 290, -83)
        self.move_to(30, 290, 0)
        self.move_to(10, 330, 0)
        self.move_to(10, 330, -83)
        self.move_to(10, 270, -83)
        self.move_to(10, 270, 0)
        self.move_to(-10, 330, 0)
        self.move_to(-10, 330, -83)
        self.move_to(-10, 270, -83)
        self.move_to(-10, 270, 0)

    def draw_cross(self):
        self.set_acceleration(0, 0, 50)
        self.relative_mode()
        self.move_to(5, 5, 0)
        self.move_to(0, 0, -80)
        self.move_to(-10, -10, 0)
        self.move_to(0, 0, 10)
        self.move_to(0, 10, 0)
        self.move_to(0, 0, -10)
        self.move_to(10, -10, 0)
        self.move_to(0, 0, 80)
        self.absolute_mode()

    def cirkel(self):

        # position = self.get_current_position()
        # if position is not None:
        #     x = position[0]
        #     y = position[1]
        #     # Calculamos las coordenadas del centro del cuadrado
        #     center_x = x + 50
        #     center_y = y + 50
        #     # Movemos el brazo robótico al centro del cuadrado
        #     self.move_to(x=center_x, y=center_y, z=10)
        #     # Dibujamos el círculo
        #     square_size = 60
        #     radius = square_size * 0.12
        #     steps = 50
        #     for i in range(steps):
        #         angle = i / steps * 2 * math.pi
        #         circle_x = center_x + 25 * math.cos(angle) * radius
        #         circle_y = center_y + 25 * math.sin(angle) * radius
        #         self.move_to(x=circle_x, y=circle_y, z=-80)
        # else:
        #     print("Error al obtener la posición actual")
        square_size = 60

        initial_x, initial_y = self.get_current_position()

        # initial_x =
        # initial_y =
        # radius = square_size / 2 - 5
        # square_x, square_y = self.get_current_position()
        # initial_x = 0
        # # initial_y = 300
        # initial_x = square_size / 2
        # initial_y = square_size / 2
        radius = square_size * 0.10
        z = -85
        feedrate = 2000

        self.move_to(x=initial_x, y=initial_y, z=0, feedrate=6000)
        print(initial_x, initial_y)

        # center_x, center_y = initial_x + square_size / 2, initial_y + square_size / 2
        # self.move_to(x=center_x, y=center_y,z=-70,feedrate=6000)

        steps = 50
        for i in range(steps):
            angle = i / steps * 2 * math.pi
            x = initial_x + math.cos(angle) * radius
            y = initial_y + math.sin(angle) * radius
            self.move_to(x=x, y=y, z=z, feedrate=feedrate)
        self.move_to(x=x, y=y, z=0, feedrate=feedrate)

    # def box_cross(self,box):
    #      box = 1 ==[self.move_to(-20,320,0)], 2 ==[self.move_to(0,320,0)]
    #      self.draw_cross()

    def crossA1(self):
        self.move_to(-20, 320, 0)
        self.draw_cross()

    def crossA2(self):
        self.move_to(0, 320, 0)
        self.draw_cross()

    def crossA3(self):
        self.move_to(20, 320, 0)
        self.draw_cross()

    def crossB1(self):
        self.move_to(-20, 300, 0)
        self.draw_cross()

    def crossB2(self):
        self.move_to(0, 300, 0)
        self.draw_cross()

    def crossB3(self):
        self.move_to(20, 300, 0)
        self.draw_cross()

    def crossC1(self):
        self.move_to(-20, 280, 0)
        self.draw_cross()

    def crossC2(self):
        self.move_to(0, 280, 0)
        self.draw_cross()

    def crossC3(self):
        self.move_to(20, 280, 0)
        self.draw_cross()

    def cirkelA1(self):
        self.move_to(-20, 320, 0)
        self.cirkel()

    def cirkelA2(self):
        self.move_to(0, 320, 0)
        self.cirkel()

    def cirkelA3(self):
        self.move_to(20, 320, 0)
        self.cirkel()

    def cirkelB1(self):
        self.move_to(-20, 300, 0)
        self.cirkel()

    def cirkelB2(self):
        self.move_to(0, 300, 0)
        self.cirkel()

    def cirkelB3(self):
        self.move_to(20, 300, 0)
        self.cirkel()

    def cirkelC1(self):
        self.move_to(-20, 280, 0)
        self.cirkel()

    def cirkelC2(self):
        self.move_to(0, 280, 0)
        self.cirkel()

    def cirkelC3(self):
        self.move_to(20, 280, 0)
        self.cirkel()

import socket
import threading
import time
import Queue
import sys
import pygame

class TCPSender(threading.Thread):
    def __init__(self, socket):
        super(TCPSender, self).__init__()
        self.queue = Queue.Queue()
        self.socket = socket
    
    def run(self):
        while True:
            to_send = self.queue.get(True)
            if to_send:
                try:
                    self.socket.send(to_send)
                except:
                    break
            else:
                break

    def send(self, data):
        self.queue.put(data)

    def stop(self):
        self.queue.put(None)

class TCPReciever(threading.Thread):
    def __init__(self, socket, callback):
        super(TCPReciever, self).__init__()
        self.callback = callback
        self.socket = socket
        self.active = True

    def run(self):
        while self.active:
            try:
                data = self.socket.recv(1024)
            except socket.error, msg:
                if msg == "timed out":
                    continue
                else:
                    print "ERROR", msg
                    break
            if not data:
                break
            self.callback(data)

    def stop(self):
        self.active = False

class TCPConnection(object):
    def __init__(self, callback):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #comment out to debug
        self.socket.connect(('192.168.11.123', 2000))
        self.socket.settimeout(0.1)
        self.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.sender = TCPSender(self.socket)
        self.reciever = TCPReciever(self.socket, callback)
        self.sender.start()
        self.reciever.start()

    def send(self, data):
        self.sender.send(data)

    def stop(self):
        self.sender.stop()
        self.reciever.stop()
        self.socket.close()

class Controller(object):
    def __init__(self):
        self.throttle = 0.
        self.pitch = 0.
        self.yaw = 0.
        self.trim = -6
        self.connection = TCPConnection(self.data_recieved)

    def format_str(self, chars):
        ret = ""
        for char in chars:
            ret += chr(char)
        return ret

    def fivebit(self, x):
        x = int(round(-x*0x1f))

        if (x < 0):
            x = -x | 0x80

        return x

    def deadzone(self, x):
        if (abs(x) < 0.1):
            x = 0

        return x
    
    def update(self):
        self.throttle = max(min(self.throttle, 1.), 0.)
        self.pitch = max(min(self.pitch, 1.), -1.)
        self.yaw = max(min(self.yaw, 1.), -1.)
        self.trim = max(min(self.trim, 31), -31)
        
        #print "throttle: %.02f" % self.throttle, "pitch: %.02f" % self.pitch, "yaw: %.02f" % self.yaw, "trim: %d" % self.trim
        
        throttle = int(round(self.throttle*0xff))
        if (throttle < 0x10):
            throttle = 0

        trim = self.fivebit(self.trim/31.)
        yaw = self.fivebit(self.yaw)
        pitch = self.fivebit(self.pitch)

        #print throttle, pitch, yaw, trim


##        The first byte has to be 0xaa.
##        The second one has to be 0x64.
##        The third byte is the power of the propellers.
##        The fourth byte controls the trim (with the same encoding than the yaw).
##        The fifth byte is the yaw : between 0 and 31, the helicopter will turn left, and between 128 and 160 it will turn right. The greater this number is, the faster it will turn.
##        The sixth byte is the pitch, with the same encoding than the yaw.
##        The seventh and eighth bytes are unused.
##        The ninth (last) byte has to be set to 0xbb.

        
        self.connection.send(self.format_str([0xaa, 0x64, throttle, trim,
                                              yaw, pitch, 0, 0, 0xbb]))

    def data_recieved(self, data):
        # [0xee, 0x64, 0x64, 0x32, battery(0x50 to 0), 0x00, ? (0x5-0xa), 0x00, 0xdd]
        # 0xa = motor just stopped
        print 'Data recieved : "%s"'%(data)

    def stop_engine(self):
        self.throttle = 0
        self.pitch = 0
        self.yaw = 0
        self.update()

    def stop(self):
        self.stop_engine()
        time.sleep(0.5)
        self.connection.stop()

if __name__=="__main__":
    controller = Controller()

    pygame.init()

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    if joystick is None:
        print "Sorry, you need a joystick for this!"
        exit()

    while True:
        #can't wait for additive throttle events
        #pygame.event.wait()
        time.sleep(0.1)
        pygame.event.pump()

        axis_x = joystick.get_axis(0)
        axis_y = joystick.get_axis(1)

        axis_trigger = joystick.get_axis(2)

        rstick_x = joystick.get_axis(4)
        rstick_y = joystick.get_axis(3)

        b_a = joystick.get_button(0)
        b_b = joystick.get_button(1)
        b_x = joystick.get_button(2)
        b_y = joystick.get_button(3)
        b_lt = joystick.get_button(4)
        b_rt = joystick.get_button(5)

        if (b_a):
            controller.stop_engine()
        if (b_b):
            controller.stop()
            break
        if (b_lt):
            controller.trim += 1
        if (b_rt):
            controller.trim -= 1

        #controller.yaw = controller.deadzone(axis_trigger)        
        controller.yaw = controller.deadzone(axis_y-rstick_y)
        #controller.pitch = controller.deadzone(axis_y)
        controller.pitch = controller.deadzone(axis_y+rstick_y)
        

        #controller.throttle -= controller.deadzone(rstick_y)/15
        controller.throttle -= controller.deadzone(axis_trigger)/15

        controller.update()
        #time.sleep(0.05)


    pygame.quit()

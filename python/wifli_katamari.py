import socket
import threading
import time
import Queue
import sys
import pygame
import errno

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
                except socket.error as e:
                    print "TX ERROR:", e.errno, e
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
            except socket.timeout:
                continue
            except socket.error as e:
                print "RX ERROR:", e.errno, e
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
        self.trim = -2
        self.battery = 100
        self.connection = TCPConnection(self.data_recieved)
        self.stop_engine()

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
            x = 0.

        #edge deadzone
        if (x > 0.9):
            x = 1.
        elif (x < -0.9):
            x = -1.

        return x

    def update(self):
        self.throttle = max(min(self.throttle, 1.), 0.)
        self.pitch = max(min(self.pitch, 1.), -1.)
        self.yaw = max(min(self.yaw, 1.), -1.)
        self.trim = max(min(self.trim, 31), -31)

        #FIXME?
        #does yaw need to be manually limited based on trim?

        print "throttle: %.02f" % self.throttle, "pitch: %.02f" % self.pitch, "yaw: %.02f" % self.yaw, "trim: %d" % self.trim

        #too low of a throttle causes issues
        #limit range to 0x10 to 0x80 (or 0)
        if self.throttle:
            throttle = int(round(self.throttle*0x70))+0x10
        else:
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
        # [0xee, 0x64, 0x64, 0x32, battery(0x64 to 0), 0x00, ? (0x5-0xa), 0x00, 0xdd]
        #byte 6 = packets processed per second?
        #one Rx packet every 2 seconds
        print 'Data recieved : "%s"' % (" ".join( "%02x" % ord(c) for c in data) )
        self.battery = ord(data[4])
        print 'Battery: %d%%' % self.battery

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
    pygame.init()
    joystick = None

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    if joystick is None:
        print "Sorry, you need a joystick for this!"
        exit()

    controller = Controller()

    pygame.event.set_allowed(None)
    pygame.event.set_allowed(pygame.JOYAXISMOTION)
    pygame.event.set_allowed(pygame.JOYBUTTONDOWN)
    pygame.event.set_allowed(pygame.QUIT)
    pygame.event.set_allowed(pygame.USEREVENT)

    packetclock = pygame.time.Clock()
    throttleclock = pygame.time.Clock()

    axis_y = 0.
    rstick_y = 0.
    throttle_adj = 0.

    run = True

    try:
        while run:
            if not throttle_adj:
                throttleclock.tick()
            
            update = False
            for event in pygame.event.get():
                #can't wait for additive throttle events
                if event.type == pygame.QUIT:
                    break
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: #A
                        controller.stop_engine()
                    elif event.button == 1: #B
                        controller.stop()
                        run = False
                        break
                    elif event.button == 2: #X
                        throttle_adj = 0.2
                    elif event.button == 4: #LT
                        controller.trim += 1
                        update = True
                    elif event.button == 5: #RT
                        controller.trim -= 1
                        update = True
                elif event.type == pygame.JOYAXISMOTION:
                    if event.axis == 1:
                        axis_y = event.value
                        update = True
                    elif event.axis == 2:
                        #throttle
                        axis_trigger = event.value
                        throttle_adj = controller.deadzone(axis_trigger)
                    elif event.axis == 3:
                        rstick_y = event.value
                        update = True
                elif event.type == pygame.USEREVENT:
                    #timer to force updates
                    update = True

            if controller.battery <= 1:
                throttle_adj = 0.2

            #don't wait if there is an active throttle adjustment
            if throttle_adj and not (
                (throttle_adj > 0. and controller.throttle == 0.) or
                (throttle_adj < 0. and controller.throttle == 1.) ): 
                controller.throttle -= (throttle_adj*throttleclock.get_time())/1500
                throttleclock.tick()
                update = True

            if not update:
                #delay until an event is received here
                #HACK
                pygame.event.post(pygame.event.wait())
                continue

            #clear/set the timer here to force an update if no events occur
            #minimum of 1 every 5 seconds
            pygame.time.set_timer(pygame.USEREVENT, 0)
            pygame.time.set_timer(pygame.USEREVENT, 1000)


            #katamari mode: yaw is difference in sticks
            controller.yaw = controller.deadzone(axis_y-rstick_y)

            controller.pitch = controller.deadzone(axis_y+rstick_y)

            controller.update()
            #ensure we send a max of 15 updates/s (that is the max i think)
            packetclock.tick(15)




    finally:
        controller.stop()
        pygame.quit()

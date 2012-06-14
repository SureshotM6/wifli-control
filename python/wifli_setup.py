import fileinput
import os
import pygame
import sys

class PadSetup:
    def __init__(self):
        self.used_axis = []
        self.used_buttons = []
        self.lstick_haxis = -1
        self.lstick_vaxis = -1
        self.rstick_haxis = -1
        self.rstick_vaxis = -1
        self.button_x = -1
        self.button_y = -1
        self.button_a = -1
        self.button_b = -1
        self.button_back = -1
        self.button_start = -1
        self.lshoulder = -1
        self.rshoulder = -1
        self.ltrigger_axis = -1
        self.rtrigger_axis = -1

    def flush_events(self):
        for event in pygame.event.get():
            continue

    def get_axis(self):
        the_axis = -1
        self.flush_events()
            
        while the_axis==-1:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION and event.axis not in self.used_axis and (event.value > 0.75 or event.value < -0.75):
                    the_axis = event.axis
        self.used_axis.append(the_axis)
        return the_axis

    def get_button(self):
        the_button = -1
        self.flush_events()

        while the_button==-1:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN and event.button not in self.used_buttons:
                    the_button = event.button
        self.used_buttons.append(the_button)
        return the_button

    def setup(self):
        axis = -1;
        print "Please press up on the left stick"
        self.lstick_vaxis = self.get_axis()
        print "Please press right on the left stick"
        self.lstick_haxis = self.get_axis()
        print "Please press up on the right stick"
        self.rstick_vaxis = self.get_axis()
        print "Please press right on the right stick"
        self.rstick_haxis = self.get_axis()
        print "Please press the left trigger"
        self.ltrigger_axis = self.get_axis()
        print "Please press the right trigger"
        self.rtrigger_axis = self.get_axis()
        print "Please press the left shoulder button"
        self.lshoulder = self.get_button()
        print "Please press the right shoulder button"
        self.rshoulder = self.get_button()
        print "Please press 'a'"
        self.button_a = self.get_button()
        print "Please press 'b'"
        self.button_b = self.get_button()
        print "Please press 'x'"
        self.button_x = self.get_button()
        print "Please press 'y'"
        self.button_y = self.get_button()
        print "Please press the back button"
        self.button_back = self.get_button()
        print "Please press the start button"
        self.button_start = self.get_button()

    def cfg_exists(self):
        return os.path.isfile("wifli.cfg")

    def read_cfg(self):
        for line in fileinput.input("wifli.cfg"):
            tokens = line.split(": ")
            if len(tokens)==2:
                key = tokens[0]
                val = int(tokens[1])
                if key == "lstick_haxis":
                    self.lstick_haxis = val
                elif key == "lstick_vaxis":
                    self.lstick_vaxis = val
                elif key == "rstick_haxis":
                    self.rstick_haxis = val
                elif key == "rstick_vaxis":
                    self.rstick_vaxis = val
                elif key == "lshoulder":
                    self.lshoulder = val
                elif key == "rshoulder":
                    self.rshoulder = val
                elif key == "a":
                    self.button_a = val
                elif key == "b":
                    self.button_b = val
                elif key == "x":
                    self.button_x = val
                elif key == "y":
                    self.button_y = val
                elif key == "back":
                    self.button_back = val
                elif key == "start":
                    self.button_start = val

    def write_cfg(self):
        f = open("wifli.cfg", "w")
        f.write("lstick_haxis: %d\n" % self.lstick_haxis)
        f.write("lstick_vaxis: %d\n" % self.lstick_vaxis)
        f.write("rstick_haxis: %d\n" % self.rstick_haxis)
        f.write("rstick_vaxis: %d\n" % self.rstick_vaxis)
        f.write("a: %d\n" % self.button_a)
        f.write("b: %d\n" % self.button_b)
        f.write("x: %d\n" % self.button_x)
        f.write("y: %d\n" % self.button_y)
        f.write("lshoulder: %d\n" % self.lshoulder)
        f.write("rshoulder: %d\n" % self.rshoulder)
        f.write("back: %d\n" % self.button_back)
        f.write("start: %d\n" % self.button_start)
        f.close()

    def print_cfg(self):
        print("lstick_haxis: %d" % self.lstick_haxis)
        print("lstick_vaxis: %d" % self.lstick_vaxis)
        print("rstick_haxis: %d" % self.rstick_haxis)
        print("rstick_vaxis: %d" % self.rstick_vaxis)
        print("a: %d" % self.button_a)
        print("b: %d" % self.button_b)
        print("x: %d" % self.button_x)
        print("y: %d" % self.button_y)
        print("lshoulder: %d" % self.lshoulder)
        print("rshoulder: %d" % self.rshoulder)
        print("back: %d" % self.button_back)
        print("start: %d" % self.button_start)

if __name__=="__main__":
    pygame.init()
    joystick = None

    if pygame.joystick.get_count > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    else:
        print "Sorry, you need a joystick for this!"
        sys.exit(1)

    padSetup = PadSetup()

    try:
        if 0: #padSetup.cfg_exists():
            padSetup.read_cfg()
            padSetup.print_cfg()
        else:
            padSetup.setup()
            padSetup.write_cfg()
    finally:
        pygame.quit()

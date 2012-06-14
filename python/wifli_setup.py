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

    def write_cfg(self):
        f = open("wifli.cfg", "w")
        f.write("lstick_haxis: %d\n" % self.lstick_haxis)
        f.write("lstick_vaxis: %d\n" % self.lstick_vaxis)
        f.write("rstick_haxis: %d\n" % self.rstick_haxis)
        f.write("rstick.vaxis: %d\n" % self.rstick_vaxis)
        f.write("a: %d\n" % self.button_a)
        f.write("b: %d\n" % self.button_b)
        f.write("x: %d\n" % self.button_x)
        f.write("y: %d\n" % self.button_y)
        f.write("lshoulder: %d\n" % self.lshoulder)
        f.write("yshoulder: %d\n" % self.rshoulder)
        f.write("back: %d\n" % self.button_back)
        f.write("start: %d\n" % self.button_start)
        f.close()

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
        padSetup.setup()
        padSetup.write_cfg()
    finally:
        pygame.quit()

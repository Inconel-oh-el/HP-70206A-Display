import pyvisa  as visa 
import sys, signal
import time

# this program uses pyvisa and GPIB stuff to print text onto an HP 70206A Display.
# The display speaks HP Plotter talk (HP-GL) with some variations.  

def signal_handler(signal, frame):
    #cancel program operation w/ ctrl+c
    print("\nprogram exiting gracefully")
    sys.exit(0)



class debugInstr:
    #print to terminal instead of instrument 
    def write(self,message):
        print(message)
    def query(self,message):
        print(message)
        return 1

class label:
    #display
    id = 0
    x = 0
    y = 0
    displayed = 'False'
    text = []
    height = 15
    maxChars = 50
    
    def __init__(self,lbID,display):
        self.display = display
        self.id = lbID
        print(self.id)
    def setText(self,message):
        # fuckey ceiling division
        self.lines = (len(message) + self.maxChars - 1) // self.maxChars
        a = 0
        b = self.maxChars
        for i in range(self.lines+1):
            self.text.append(message[a:b])
            a = i*self.maxChars
            b = (i+1)*self.maxChars
        del self.text[1]
        return self.lines
    def printToDisplay(self,position):
        self.x,self.y = position
        self.display.write("IT%d;CL %d,%d;OR %d,%d;" % (self.id,self.lines,self.maxChars,self.x,self.y))
        for i in self.text:
            self.display.write('LB%s#' % i)
        self.displayed = True
    def blank(self):
        self.displayed = False
        print('blank me pls')
    def delete(self):
        print("IT%d;DL;" % self.id)
    def vertShift(self,amount):
        self.y += amount
                #print("vert shift amount: %d" % amount)
                #print("vert shift new origin: %d" % self.y)
        self.display.write("IT%d;OR %d,%d;" %(self.id,self.x,self.y))

class labelManager:
    #display
    allLabels = []
    activeLabels = []
    n = 0
    x = 112
    y = 45 
    lh = 15
    maxY = y
    minY = 30
    atBottom = False    
    nMax = 6

    
    def __init__(self,display):
        self.display = display
    
    def add(self,text):
        self.n +=1
        lb = label(self.n,self.display)
        lines = lb.setText(text)
        # shift existing labels up
        self.shiftUp(lines+1)
        # set new origin just below and print
        self.y = self.minY + self.lh * lines 
        lb.printToDisplay([self.x,self.y])
        # update active
        self.activeLabels.append(lb)

    def shiftUp(self,nLines):
        i = 0
        if nLines >> 0:
            for lb in self.activeLabels:
                # okay to shift up
                print(lb.y)
                #print("label %d shift up new origin: %d" %(lb.id,lb.y + (nLines)*self.lh))
                #print("label %d bottom position: %d" %(lb.id,lb.y - (lb.lines)*self.lh))
                if lb.y + nLines * self.lh <= self.maxY:
                    lb.vertShift(self.lh * nLines)
                # delete label from display memory
                #else:
                    #lb.delete()
                    #del self.activeLabels[i]
                i +=1
        return
    def shiftDown(self,nLines):
        i = 0
        if nLines << 0:
            for lb in self.activeLabels:
                # okay to shift up
                print(lb.y)
                #print("label %d shift up new origin: %d" %(lb.id,lb.y + (nLines)*self.lh))
                #print("label %d bottom position: %d" %(lb.id,lb.y - (lb.lines)*self.lh))
                if lb.y - nLines * self.lh <= self.minY:
                    lb.vertShift(self.lh * nLines)
                # delete label from display memory
                #else:
                    #lb.delete()
                    #del self.activeLabels[i]
                i +=1
        return


signal.signal(signal.SIGINT, signal_handler)
debug = False 
if not debug:
    rm = visa.ResourceManager()
    #visa.log_to_screen()

    display = rm.open_resource('GPIB0::4::INSTR') 
    display.read_termination = '\r\n'

    ID=display.query("*IDN?") 
    display.write('DE;DT#;')
    #ID = "70206A"

    print(ID) 
    if ID == "70206A": 
        print("Connection Successful") 
    else:print("Connection Failed")
else:
    display = debugInstr()


a = 'Peepeepoopoo'
b = "The quick brown fox jumped over the lazy dog"
with open('navyseal.txt', 'r') as file:
    c = file.read().replace('\n', '')

#labels = labelManager(display)
#labels.add(a)

#labels.add(b)
#labels.shiftUp(10)

lb = label(1,display)
n = lb.setText(c)
lb.printToDisplay([112,50])
while(True):
    pulses = int(str(display.query('RP;')))
    if not pulses ==0:
        #print(pulses)
        #labels.shiftUp(pulses)
        #labels.shiftDown(pulses)
        lb.vertShift(pulses)
    time.sleep(.05)















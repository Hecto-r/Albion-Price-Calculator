#Author: Hector Cabrera

from PIL import ImageGrab
import pytesseract
from tkinter import *
import tkinter.font as font
import cv2
import os
import mss.tools
from pynput.keyboard import Key, Listener

total = 0
after_id = None
delay = 5
x1, y1, x2, y2 = 828, 691, 1089, 748

def calculatecost():
    global after_id
    global total
    global delay
    # Grab some screen
    screen = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    # Make greyscale
    w = screen.convert('L')

    # Save so we can see what we grabbed
    w.save('grabbed.png')

    # YOU NEED THIS FOR FINAL EXECUTABLE
    pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\Tesseract.exe'

    # YOU NEED THIS ONE ENABLED FOR TESTING (Change path to wherever you installed tesseract)
    # pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(w)

    # Replacing commas and new line to put everything into an array
    s = text.replace(",", "").replace("\n", "")
    # Removing unnecessary text s2[0] contains Setup Fee s2[2] contains total
    s2 = re.split(r'[(|)]', s)

    try:
        # Convert textblob into string and then int
        if len(s2) == 5:
            intConversion = int(float(str(s2[4]))) - int(float(str(s2[2])))
        else:
            intConversion = int(float(str(s2[2]))) - int(float(str(s2[0])))
    except ValueError:
        intConversion = 0
    except IndexError:
        try:
            intConversion = int(float(str(s2[0])))
        except ValueError:
            intConversion = 0

    total += intConversion

    myFont = font.Font(size=15)
    priceLabel.config(text="Total: $" + str(total))
    recentLabel.config(text="Recent: " + str(intConversion))

    priceLabel['font'] = myFont
    recentLabel['font'] = myFont

    if(delay > 1000):
        after_id = root.after(delay, calculatecost)

def keyPressed(event=None): #set event to None to take the key argument from .bind
    calculatecost()


def startbutton():
    calculatecost()


def pausebutton():
    global after_id
    if after_id:
        root.after_cancel(after_id)
        after_id = None


def submitbutton():
    global total
    repair = int(repairCost.get())
    total -= repair
    recentLabel.config(text="Recent: -" + str(repair))
    priceLabel.config(text="Total: $" + str(total))


def updatedelay(var):
    global delay
    delay = delaySlider.get() * 1000


# ***THIS IS CODE FOR SELECTING REGION***

drawing = False
num = 0

def draw_rect(event, x, y, flags, param):
    global x1, y1, drawing, num, img, img2, x2, y2
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x1, y1 = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            a, b = x, y
            if a != x & b != y:
                img = img2.copy()

                cv2.rectangle(img, (x1, y1), (x, y), (0, 255, 0), 2)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        num += 1
        x2 = x
        y2 = y


def updateregion():
    global img, img2
    with mss.mss() as sct:
        sct.shot()

    key = ord('a')
    img = cv2.imread('monitor-1.png')  # reading image
    img2 = img.copy()
    cv2.namedWindow("main", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("main", draw_rect)
    cv2.setWindowProperty("main", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # PRESS w to confirm save selected bounded box
    while key != ord('w'):
        cv2.imshow("main", img)
        key = cv2.waitKey(1) & 0xFF
    if key == ord('w'):
        cv2.destroyAllWindows()
        os.remove('monitor-1.png')

def copy_button():
    clip = Tk()
    clip.withdraw()
    clip.clipboard_clear()
    clip.clipboard_append(priceLabel.cget("text"))
    clip.destroy()

# ***END OF SELECTING REGION CODE*** (Could use some refactoring)


# GUI GUI GUI
root = Tk()
root.title("Price Calculator")

copyButton = Button(root, text="COPY", width=5, command=copy_button)
root.bind('<+>', keyPressed)

priceLabel = Label(root, fg="dark green")
recentLabel = Label(root, fg="red")
startButton = Button(root, bg="light green", text="START", width=25, command=startbutton)
pauseButton = Button(root, bg="orange", text="PAUSE", width=25, command=pausebutton)

repairButton = Button(root, text="SUBMIT", command=submitbutton)
repairLabel = Label(root, text="Repair Cost: ")
repairCost = Entry(root)

delayLabel = Label(root, text="Adjust Delay")
delaySlider = Scale(root, from_=1, to=5, orient=HORIZONTAL, command=updatedelay)
delaySlider.set(5)

regionButton = Button(root, text="Select Region: 'W' to confirm", command=updateregion)

repairLabel.grid(row=0, column=0)
repairCost.grid(row=1, column=0)
repairButton.grid(row=2, column=0)
delaySlider.grid(row=3, column=0)
delayLabel.grid(row=4, column=0)
regionButton.grid(row=5, column=0)

recentLabel.grid(row=0, column=1)
priceLabel.grid(row=1, column=1)
copyButton.grid(row=2, column = 1)
startButton.grid(row=3, column=1)
pauseButton.grid(row=4, column=1)

root.wm_attributes("-topmost", 1)
root.mainloop()

print("Final Total: $" + str(total))
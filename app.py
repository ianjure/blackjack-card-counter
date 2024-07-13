from ultralytics import YOLO
from count_card import getCount
from win32 import win32gui
import cv2
import math
import cvzone
import win32.lib.win32con as win32con

# FOR WEBCAM
cap = cv2.VideoCapture(0) # -- WEBCAM TO USE
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800) # -- WIDTH 
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800) # -- HEIGHT

# INITIALIZE MODEL
model = YOLO("model/yolov8s.pt")

classNames = ['10C', '10D', '10H', '10S',
              '2C', '2D', '2H', '2S',
              '3C', '3D', '3H', '3S',
              '4C', '4D', '4H', '4S', 
              '5C', '5D', '5H', '5S', 
              '6C', '6D', '6H', '6S', 
              '7C', '7D', '7H', '7S', 
              '8C', '8D', '8H', '8S', 
              '9C', '9D', '9H', '9S', 
              'AC', 'AD', 'AH', 'AS', 
              'JC', 'JD', 'JH', 'JS',
              'KC', 'KD', 'KH', 'KS', 
              'QC', 'QD', 'QH', 'QS']

# GLOBAL VARIABLES
all_history = [] # -- FOR MANY DECKS
one_history = [] # -- FOR ONE DECK
currentCard = ""
runningCount = 0
trueCount = 0
finishedDeck = 0
decks = 1 # -- SET THE NUMBER OF DECKS

while True:
    success, img = cap.read()
    results = model(img, stream=True)

    for result in results:
        boxes = result.boxes

        for box in boxes:
            # BOUNDING BOX
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2-x1, y2-y1

            # CONFIDENCE
            conf = math.ceil((box.conf[0] * 100)) / 100

            # CLASS NAME
            cls = int(box.cls[0])

            # CHECK CONFIDENCE
            if conf > 0.9:
                currentClass = classNames[cls]
                cvzone.cornerRect(img, (x1, y1, w, h), l=0, colorR=(0,255,0),
                                  colorC=(0,255,0), t=1, rt=2)
                
                # CHECK IF SPECIFIED NUMBER OF DECK IS NOT ONE
                if decks != 1:

                    # ADD TO HISTORY
                    if currentCard != currentClass:
                        all_history.append(currentClass)
                        currentCard = currentClass
                        count = getCount(currentClass)
                        runningCount += count
                        trueCount = math.floor(runningCount / (decks - finishedDeck)) # -- TRUE COUNT = RUNNING COUNT / REMAINING DECKS
                    
                    # CHECK IF 52 CARDS ARE SCANNED (1 DECK)
                    if len(all_history) == 52:
                        all_history.clear()
                        all_history.append(currentClass)
                        currentCard = currentClass
                        count = getCount(currentClass)
                        runningCount += count
                        finishedDeck += 1

                        # CHECK IF ALL THE DECKS ARE SCANNED
                        if finishedDeck == decks:
                            finishedDeck = 0
                            trueCount = 0
                
                # IF DECK IS ONLY ONE, USE A DIFFERENT ALGORITHM
                else:

                    # ADD TO HISTORY
                    if currentClass not in list(set(one_history)):
                        one_history.append(currentClass)
                        currentCard = currentClass
                        count = getCount(currentClass)
                        runningCount += count
                        trueCount = runningCount # -- TRUE COUNT = RUNNING COUNT
                    
                    # CHECK IF 52 CARDS ARE SCANNED (1 DECK)
                    if len(list(set(one_history))) == 52:

                        # CHECK IF CURRENT SCANNED CARD IS NOT THE PREVIOUS CARD
                        if currentClass != currentCard:
                            one_history.clear()
                            one_history.append(currentClass)
                            currentCard = currentClass
                            count = getCount(currentClass)
                            runningCount += count
                            trueCount = runningCount # -- TRUE COUNT = RUNNING COUNT

        # IMPORTING GRAPHICS (RUNNING COUNT & TRUE COUNT)
        graphics3 = cv2.imread(f"graphics/count label.png", cv2.IMREAD_UNCHANGED)
        count_graphics = cv2.resize(graphics3, (250, 128))
        cvzone.overlayPNG(img, count_graphics, (0, 0)) # -- COUNT

        # RUNNING COUNT
        cv2.putText(img, text=f'{runningCount}', fontFace=1, org=(168,44), fontScale=2.5,
                    thickness=2, color=(255,255,255))
        
        # TRUE COUNT
        cv2.putText(img, text=f'{trueCount}', fontFace=1, org=(168,110), fontScale=2.5,
                    thickness=2, color=(255,255,255))
        
        # NUMBER OF DECKS
        cv2.putText(img, text=f'{finishedDeck + 1}/{decks}', fontFace=1, org=(130,457), fontScale=2.5,
                    thickness=2, color=(255,255,255))

    # IMPORTING GRAPHICS (CURRENT CARD LABEL)
    graphics1 = cv2.imread(f"graphics/card label.png", cv2.IMREAD_UNCHANGED)
    card_label_graphics = cv2.resize(graphics1, (90, 39))
    cvzone.overlayPNG(img, card_label_graphics, (535, 300)) # -- CURRENT CARD LABEL

    # IMPORTING GRAPHICS (CURRENT CARD)
    if len(currentCard) == 0:
        graphics2 = cv2.imread(f"graphics/blue.png", cv2.IMREAD_UNCHANGED)
        card_graphics = cv2.resize(graphics2, (90, 125))
    else:
        graphics2 = cv2.imread(f"graphics/{currentCard.lower()}.png", cv2.IMREAD_UNCHANGED)
        card_graphics = cv2.resize(graphics2, (90, 125))
    cvzone.overlayPNG(img, card_graphics, (535, 342)) # -- CURRENT CARD

    # IMPORTING GRAPHICS (DECKS REMAINING)
    graphics4 = cv2.imread(f"graphics/deck label.png", cv2.IMREAD_UNCHANGED)
    deck_graphics = cv2.resize(graphics4, (100, 39))
    cvzone.overlayPNG(img, deck_graphics, (20, 425)) # -- DECK

    # SHOW WINDOW
    cv2.imshow("Blackjack Card Counter", img)

    # ICON
    hwnd = win32gui.FindWindow(None, "Blackjack Card Counter")
    icon_path = "graphics/icon.ico" # -- FILE SHOULD BE .ICO
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG,
                        win32gui.LoadImage(None, icon_path, win32con.IMAGE_ICON,
                        0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE))
    
    # KEYBIND
    k = cv2.waitKey(1) & 0xFF
    if k == 27: # -- 'ESC' KEY
        break
    elif cv2.getWindowProperty("Blackjack Card Counter", cv2.WND_PROP_VISIBLE) < 1: # -- CLOSE BUTTON 
        break

cv2.destroyAllWindows()

    
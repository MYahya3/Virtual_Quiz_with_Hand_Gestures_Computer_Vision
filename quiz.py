import cv2
import csv
from cvzone.HandTrackingModule import HandDetector
import time
from  MCQ_class import MCQ
from utilis import put_text_rectangle,update_score_in_csv, create_login_window

def display_instructions(frame, text, position=(50, 50), font_size=0.6, color=(255, 255, 255), thickness=2):
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_size, color, thickness)

# Import csv file data
pathCSV = "mcqs.csv"
with open(pathCSV, newline='\n') as f:
    reader = csv.reader(f)
    dataAll = list(reader)[1:]

# Create Object for each MCQ
mcqList = []
for q in dataAll:
    # print(q)
    mcqList.append(MCQ(q))
print("Total MCQ Objects Created:", len(mcqList))

qTotal = len(dataAll)

# To draw Bounding Box
x = 30
y = 60
offset = 10
scale = 1.25
font=cv2.FONT_HERSHEY_PLAIN

# Initialize Video
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    ("Could not access to camera")
    exit()

cap.set(3, 1280)
cap.set(4, 720)
detector = HandDetector(detectionCon=0.70, maxHands=1)

qNo = 0 # Quiz Ans Counter
startqz = False # To start quiz
restart = False
finish = False
entry_user = False

counterRight = 0
counterLeft = 0

windowname = "Orignal"

countdown_duration = qTotal * 30  # Set the countdown duration (in seconds)
countdown_start_time = 0
remaining_time = 0
background = cv2.imread("download.jpg")
csv_file = "user_data.csv"
user, psw = None, None
fps = cap.get(cv2.CAP_PROP_FPS)

# To write output video in mp4 format
while True:
    if not entry_user:
        try:
            cv2.destroyAllWindows()
        except: pass
        login_successful, user, psw = create_login_window(csv_file=csv_file)
        entry_user = True

    success, img = cap.read()
    if not  success:
        break
    bg = cv2.resize(background, (img.shape[1], img.shape[0]))

    img = cv2.flip(img, 1)  # To make image normal view
    dummy = img.copy() # To swtich to new Screen when start quiz

    hands, img = detector.findHands(img, flipType=False, draw=True)

    img = bg.copy()
    if not startqz and not restart and entry_user:

        img, startbbox = put_text_rectangle(img, "START", [int(img.shape[1]/2.7), int(img.shape[0]/2.2)], scale=1.9, thickness=2, offset=20, colorT = (0,0,0), colorR=(170,178,32), font=cv2.FONT_HERSHEY_TRIPLEX, rect=False)
        # display_instructions(img, "Use your index finger as cursor to choose an option", (10, 40))

        if hands:
            lmList = hands[0]['lmList']
            cursor = lmList[8][0:2]

            cv2.circle(img, (cursor[0], cursor[1]), 12, (140,230,240), -1)
            choice = True
            tx1, ty1, tx2, ty2 = startbbox
            if tx1 < cursor[0] < tx2 and ty1 < cursor[1] < ty2:
                counterRight += 1
                if counterRight > 30:
                    windowname = "Orignal"
                    try:
                        cv2.destroyWindow("Demo")
                    except: pass
                    startqz = True
                    counterRight = 0
                    # choice = False

    if startqz and countdown_start_time == 0:
        countdown_start_time = time.time()  # Start the countdown timer when startqz becomes True

    if startqz:
        windowname = "Quiz"
        try:
            cv2.destroyWindow("Orignal")
        except:
            pass
        img = dummy
        img = bg.copy()
        if remaining_time == 1:
            qNo = qTotal
        if qNo < qTotal:
            mcq = mcqList[qNo]
            # print(mcq.userAns, qNo)
            img, bbox = put_text_rectangle(img, mcq.question, [x, y], scale=0.55, thickness=1, offset=offset, colorT = (10,0,10), font=cv2.FONT_HERSHEY_TRIPLEX,rect=False)
            img, bbox1 = put_text_rectangle(img, f"{mcq.choice1}", [bbox[0]+35, bbox[3] + 60], scale=scale, thickness=1, offset=offset, colorT = (10,0,10), is_selected=(mcq.userAns == 1))
            img, bbox2 = put_text_rectangle(img, f"{mcq.choice2}", [bbox1[0]+10, bbox1[3] + 50], scale=scale, thickness=1, offset=offset, colorT = (10,0,10), is_selected=(mcq.userAns == 2))
            img, bbox3 = put_text_rectangle(img, f"{mcq.choice3}", [bbox2[0]+10, bbox2[3] + 50], scale=scale, thickness=1, offset=offset, colorT = (10,0,10), is_selected=(mcq.userAns == 3))
            img, bbox4 = put_text_rectangle(img, f"{mcq.choice4}", [bbox3[0]+10, bbox3[3] + 50], scale=scale, thickness=1, offset=offset, colorT = (10,0,10), is_selected=(mcq.userAns == 4))
            img, bbox5 = put_text_rectangle(img, f"Back", [x+10, y*7], scale=scale-0.3, thickness=1, offset=5, colorT = (220,220,220), colorR=(50,50,50), font=cv2.FONT_HERSHEY_TRIPLEX)

            if qNo == qTotal - 1:
                img, finishbox = put_text_rectangle(img, f"Finish", [x + 10, y * 8], scale=scale-0.3, thickness=1, offset=5, colorT = (250,250,250), colorR=	(34,139,34), font=cv2.FONT_HERSHEY_TRIPLEX)
                finish = True
            else:
                img, bbox6 = put_text_rectangle(img, f"Next", [x + 140, y * 7], scale=scale-0.3, thickness=1, offset=5, colorT = (220,220,220), colorR=(50,50,50), font=cv2.FONT_HERSHEY_TRIPLEX)
                finish = False
            if hands:
                lmList = hands[0]['lmList']
                cursor = lmList[8][0:2]
                mf = lmList[12][0:2]
                cv2.circle(img, (cursor[0], cursor[1]), 12, (140, 230, 240), -1)
                if bbox5[0] < cursor[0] < bbox5[2] and bbox5[1] < cursor[1] < bbox5[3]:
                    counterRight += 1
                    if counterRight > 10:

                        # Go to the previous question
                        qNo = max(0, qNo - 1)
                        choice = False
                        time.sleep(0.2)
                        answered = False
                        counterRight = 0

                elif mcq.userAns is not None and bbox6[0] < cursor[0] < bbox6[2] and bbox6[1] < cursor[1] < bbox6[3] and not finish:
                    counterLeft += 1
                    if counterLeft > 10:
                        # Go to the next question
                        qNo = min(qTotal - 1, qNo + 1)
                        answered = False
                        counterLeft = 0
                elif qNo >= 0 and bbox6[0] < cursor[0] < bbox6[2] and bbox6[1] < cursor[1] < bbox6[3] and not finish:
                    counterLeft += 1
                    if counterLeft > 10:
                        # Go to the next question
                        qNo = min(qTotal - 1, qNo + 1)
                        answered = False
                        counterLeft = 0
                elif finish and finishbox[0] < cursor[0] < finishbox[2] and finishbox[1] < cursor[1] < finishbox[3]:
                    qNo += 1

                else:
                    answered = mcq.update(cursor, [bbox1, bbox2, bbox3,bbox4], img=img)

            elapsed_time = time.time() - countdown_start_time
            remaining_time = max(0, countdown_duration - int(elapsed_time))
            # Convert remaining time to minutes and seconds
            minutes = remaining_time // 60
            seconds = remaining_time % 60

            # Display the countdown timer on the screen
            countdown_text = f"{minutes:02}:{seconds:02}"
            # img, _ = cvzone.putTextRect(img, countdown_text, [20, 20], 2, 2, offset=20, colorR=(255, 0, 0))
            img = cv2.putText(img,countdown_text, (int(img.shape[1]/1.1), 30), fontScale=0.8, thickness=2, color=(50,50,50), fontFace=cv2.FONT_HERSHEY_COMPLEX, lineType=cv2.LINE_AA)
            img = cv2.putText(img, f'{qNo + 1}/{qTotal}', [int(img.shape[1] / 2), img.shape[0]-30], fontScale=0.8, thickness=1, color=(0,0,0), fontFace=cv2.FONT_HERSHEY_COMPLEX, lineType=cv2.LINE_AA)
        else:
            score = 0
            # print(len(mcqList))
            for mcq in mcqList:
                if mcq.answer == mcq.userAns:
                    score += 1

            score = round((score / qTotal) * 100, 2)
            # img, _ = cvzone.putTextRect(img, "Quiz Completed", [250, 300], 2, 2, offset=50, border=5, colorR=(170,178,32))
            img, scorebbox = put_text_rectangle(img, f'Your Score: {score}%', [int(img.shape[1]/3.2), int(img.shape[0]/3)], scale=scale, thickness=2, offset=25, colorR=(105,105,105), font=cv2.FONT_HERSHEY_TRIPLEX, rect=False)
            update_score_in_csv(csv_file=csv_file, entered_username=user, entered_password=psw, new_score=score)
            if score >= 80:
                img, _ = put_text_rectangle(img, "Pass", [int((scorebbox[0]+ scorebbox[2])/2.05),int(scorebbox[3] + 40)], scale=scale-0.3, thickness=1, offset=offset, colorT = (225,228,255), colorR=(34,139,34), font=cv2.FONT_HERSHEY_TRIPLEX)
            else:
                img, _ = put_text_rectangle(img, f"Fail", [int((scorebbox[0]+ scorebbox[2])/2.05),int(scorebbox[3] + 40)], scale=scale-0.3, thickness=1, offset=offset, colorT = (255,240,245), rect=True, colorR=(72,99,250), font=cv2.FONT_HERSHEY_TRIPLEX)
            # Add restart option
            img, restart_box = put_text_rectangle(img, "Main Menu", (5,50), scale=0.8, thickness=2, offset=5,
                                                  colorT = (255, 240, 245), colorR=(72, 99, 250), rect=True, font=cv2.FONT_HERSHEY_TRIPLEX)

            if hands:
                lmList = hands[0]['lmList']
                cursor = lmList[8][0:2]
                cv2.circle(img, (cursor[0], cursor[1]), 10, (140,230,240), -1)
                if restart_box[0] < cursor[0] < restart_box[2] and restart_box[1] < cursor[1] < restart_box[3]:
                    restart = True
                    startqz = False
                    windowname = "Orignal"
                    try:
                        cv2.destroyWindow("Quiz")
                    except:  pass
                    countdown_start_time = 0
                    remaining_time = 0
                    qNo = 0
                    score = 0
                    for mcq in mcqList:
                        mcq.userAns = None
                    time.sleep(0.3)
                    restart = False
                    entry_user = True

    cv2.namedWindow(windowname, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(windowname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.namedWindow(windowname, cv2.WINDOW_FULLSCREEN)

    cv2.imshow(windowname, img)
    key = cv2.waitKey(1)
    if key == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()

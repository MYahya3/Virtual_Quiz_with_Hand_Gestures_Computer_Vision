import cv2

class MCQ():
    def __init__(self, data):

        if len(data) != 6:
            raise ValueError("Invalid data format. Expected a list of length 6.")
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])
        self.userAns = None

    def update(self, cursor, bboxs, img):
        answered = False
        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                self.userAns = x + 1
                answered = True
                cv2.rectangle(img, (x1, y1), (x1+10, y2), (180, 50, 70), cv2.FILLED)
        return answered
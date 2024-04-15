import cv2
import tkinter as tk
from tkinter import messagebox
import csv
# Global variable to store the user's score
def playVideo(video):
    cap = cv2.VideoCapture(video)
    windowname = "Demo"
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.namedWindow(windowname, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(windowname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow(windowname, frame)
        cv2.waitKey(10)
    cap.release()
    cv2.destroyAllWindows()

def put_text_rectangle(img, text, pos, rect = True, scale=3, thickness=3, colorT=(255, 255, 255),
                colorR=(102, 205, 170), font=cv2.FONT_HERSHEY_PLAIN,
                offset=10, is_selected = False):
    overlay = img.copy()
    ox, oy = pos
    frame_width = img.shape[1]
    (w, h), _ = cv2.getTextSize(text, font, scale, thickness)
    x1, y1, x2, y2 = ox - offset, oy + offset, ox + int(w*0.90) + offset, oy - h - offset

    if is_selected:
        colorR = (34,139,34)  # Change the color for the selected option

    if w > frame_width / 1.4:
        # Split text into two lines without breaking words
        words = text.split(' ')
        first_line = ''
        second_line = ''
        current_line = first_line
        for word in words:
            if cv2.getTextSize(current_line + ' ' + word, font, scale, thickness)[0][0] < frame_width / 1.4:
                current_line += ' ' + word
            else:
                if first_line == '':
                    first_line += current_line.lstrip()
                else:
                    second_line += current_line.lstrip()
                current_line = word
        text_lines = [line.lstrip() for line in [first_line, second_line, current_line] if line]
        if rect == True:
            (w_1, h_1), _ = cv2.getTextSize(text_lines[0], font, scale, thickness)
            (w_2, h_2), _ = cv2.getTextSize(text_lines[1], font, scale, thickness)
            img = cv2.rectangle(img, (ox-offset, oy - h_1 - offset), (int(frame_width / 1.38), oy+h_2+offset), colorR, -1)
        for i, line in enumerate(text_lines):
            cv2.putText(img, line, (ox, int(oy + i * h * 1.5)), font, scale, colorT, thickness,cv2.LINE_AA)
    else:
        if rect == True:

            (w1, h1), _ = cv2.getTextSize(text, font, scale, thickness)
            x, y, w, h = ox - offset, oy + offset, ox + w1 + offset, oy - h1 - offset
            img = cv2.rectangle(overlay, (x, y), (w, h), colorR, -1)
        cv2.putText(img, text, (ox, oy), font, scale, colorT, thickness, cv2.LINE_AA)
    return img, [x1, y2, x2, y1]


def update_score_in_csv(csv_file,entered_username, entered_password , new_score):
    # Update the CSV file with the new score for the given username
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        rows = list(csvreader)
        for row in rows:
            username_from_file = row['Username']
            password_from_file = row['Password']
            if  entered_username == username_from_file and entered_password == password_from_file:
                # Retrieve and store the user's score
                row['Score'] = f"{new_score}%"
        with open(csv_file, 'w', newline='') as csvfile:
            fieldnames = ['Username', 'Password', 'Score']
            csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csvwriter.writeheader()
            csvwriter.writerows(rows)


user_score = None

def validate_login(csv_file):
    global user_score, entered_username, entered_password  # Declare user_score as a global variable
    entered_username = username_entry.get()
    entered_password = password_entry.get()

    if not entered_username or not entered_password:
        messagebox.showwarning("Invalid Input", "Username and Password cannot be empty")
        return

    # Check credentials against data in the CSV file
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            username_from_file = row['Username']
            password_from_file = row['Password']
            if entered_username == username_from_file and entered_password == password_from_file:
                # Retrieve and store the user's score
                user_score = row['Score']
                root.destroy()
                return True  # Indicate successful login

    messagebox.showerror("Login Failed", "Invalid username or password")
    return False  # Indicate failed login


def create_login_window(csv_file):
    global username_entry, password_entry, root, entered_username, entered_password
    root = tk.Tk()
    root.title("Login System")

    tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=10)
    tk.Label(root, text="Password:").grid(row=1, column=0, padx=10, pady=10)

    username_entry = tk.Entry(root)
    password_entry = tk.Entry(root, show="*")

    username_entry.grid(row=0, column=1, padx=10, pady=10)
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    login_result = tk.BooleanVar()  # Variable to store the login result

    def on_login_click():
        login_result.set(validate_login(csv_file=csv_file))

    tk.Button(root, text="Login", command=on_login_click).grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()

    return login_result.get(), entered_username, entered_password# Return the login result after the Tkinter loop
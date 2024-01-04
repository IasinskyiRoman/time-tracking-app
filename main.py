
# from plyer import notification
# import logging
# import os
# from datetime import datetime, timezone
# import time
# from time import sleep
# import tkinter as tk
# from tkinter import simpledialog
# import csv
# from aw_client import ActivityWatchClient
# from aw_core.log import setup_logging
# from aw_core.models import Event
# # from .config import parse_args
# from aw_watcher_window.config import parse_args
# # from .exceptions import FatalError
# from aw_watcher_window.exceptions import FatalError
# # from .lib import get_current_window
# from aw_watcher_window.lib import get_current_window
# # from .macos_permissions import background_ensure_permissions
# from aw_watcher_window.macos_permissions import background_ensure_permissions
# import sys
# from tkinter import font

# logger = logging.getLogger(__name__)

# logger = logging.getLogger(__name__)

# notification_clicked = False


# def show_notification_popup():
#     global notification_clicked
#     notification.notify(
#         title='Task Description',
#         message='Click this notification to describe your task',
#         app_name='YourAppName',
#         timeout=10
#     )
#     time.sleep(3)
#     notification_clicked = True

# def display_popup(current_window_title):
#     root = tk.Tk()
#     root.withdraw()

#     task_description = tk.simpledialog.askstring(
#         "Task Description",
#         f"Please describe your task for {current_window_title}:",
#         parent=root
#     )

#     root.destroy()
#     return task_description


# def heartbeat_loop(client, bucket_id, poll_time, strategy, exclude_title=False):
#     global notification_clicked
#     timer = 0
#     popup_threshold = 10
#     prev_app = None
#     prev_title = None
#     popup_shown_for_title = None

#     while True:
#         if os.getppid() == 1:
#             logger.info("window-watcher stopped because parent process died")
#             break

#         current_window = None
#         try:
#             current_window = get_current_window(strategy)
#             logger.debug(current_window)
#         except (FatalError, OSError):
#             logger.exception("Fatal error, stopping")
#             break
#         except Exception:
#             logger.exception("Exception thrown while trying to get an active window")

#         if current_window is None:
#             logger.debug("Unable to fetch the window, trying again on the next poll")
#         else:
#             if current_window["title"] != prev_title:
#                 timer = 0
#                 prev_app = current_window["app"]
#                 prev_title = current_window["title"]

#             if exclude_title:
#                 current_window["title"] = "excluded"

#             now = datetime.now(timezone.utc)
#             current_window_event = Event(timestamp=now, data=current_window)
#             client.heartbeat(bucket_id, current_window_event, pulsetime=poll_time + 1.0, queued=True)

#             if timer >= popup_threshold and popup_shown_for_title != prev_title:
#                 show_notification_popup()
#                 if notification_clicked:
#                     task_description = display_popup(prev_app)
#                     if task_description is not None:
#                         save_to_csv(now, current_window, task_description, strategy)
#                         popup_shown_for_title = prev_title
#                         notification_clicked = False

#         timer += poll_time
#         sleep(poll_time)

# def save_to_csv(timestamp, window_info, task_description, strategy):
#     csv_filename = "./task_log.csv"
#     data = [
#         {
#             "Timestamp": timestamp.isoformat(),
#             "Program": window_info["app"],
#             "Program File Name": window_info["title"],
#             "Task Description": task_description,
#         }
#     ]
#     file_exists = os.path.isfile(csv_filename)
#     with open(csv_filename, mode="a", newline="") as csv_file:
#         fieldnames = ["Timestamp", "Program", "Program File Name", "Task Description"]
#         writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#         if not file_exists:
#             writer.writeheader()
#         writer.writerows(data)

# def main():
#     args = parse_args()
#     setup_logging(
#         name="aw-watcher-window",
#         testing=args.testing,
#         verbose=args.verbose,
#         log_stderr=True,
#         log_file=True,
#     )

#     if sys.platform == "darwin":
#         background_ensure_permissions()

#     client = ActivityWatchClient(
#         "aw-watcher-window", host=args.host, port=args.port, testing=args.testing
#     )

#     bucket_id = f"{client.client_name}_{client.client_hostname}"
#     event_type = "currentwindow"
#     client.create_bucket(bucket_id, event_type, queued=True)

#     logger.info("aw-watcher-window started")
#     sleep(1)
#     with client:
#         heartbeat_loop(
#             client,
#             bucket_id,
#             poll_time=args.poll_time,
#             strategy=args.strategy,
#             exclude_title=args.exclude_title,
#         )

# if __name__ == "__main__":
#     main()




import logging
import os
from datetime import datetime, timezone
import time
from time import sleep
from aw_client import ActivityWatchClient
from aw_core.log import setup_logging
from aw_core.models import Event
from aw_watcher_window.config import parse_args
from aw_watcher_window.exceptions import FatalError
from aw_watcher_window.lib import get_current_window
from aw_watcher_window.macos_permissions import background_ensure_permissions
import sys
import csv

from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QMessageBox, QWidget

logger = logging.getLogger(__name__)
app = QApplication(sys.argv)

class CustomTitleBar(QWidget):
    def __init__(self, title, icon_path, close_callback=None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setSpacing(5)  # Reduced spacing for items

        # Create a QLabel for the icon
        icon_label = QLabel(self)
        icon_pixmap = QPixmap(icon_path)
        if icon_pixmap.isNull():
           logger.warning(f"Failed to load icon from path: {icon_path}")
        else:
           icon_pixmap = icon_pixmap.scaled(25, 25)
           icon_label.setPixmap(icon_pixmap)
           layout.addWidget(icon_label)

        # Create a QLabel for the title text
        title_label = QLabel(title, self)
        font = title_label.font()
        font.setPointSize(15)
        title_label.setFont(font)
        layout.addWidget(title_label, alignment=Qt.AlignLeft)  # Align to left 

        layout.addStretch(1)  # Add stretch to push items to left and right

        # Create close button
        self.close_button = QPushButton(self)
        button_image = QPixmap('./close.png').scaled(20,20)
        self.close_button.setIcon(QIcon(button_image))
        button_size = QSize(15, 15)
        self.close_button.setIconSize(button_image.size())
        self.close_button.setFixedSize(button_size)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;  /* Transparent background */
                border: none;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                background-color: transparent;  /* Transparent background on hover */
            }
        """)

        if close_callback:
           self.close_button.mousePressEvent = close_callback


        layout.addWidget(self.close_button, alignment=Qt.AlignTop)


        # Adjust padding for the title bar
        layout.setContentsMargins(3, 10, 3, 8)
        

class TaskDescriptionInput(QDialog):
    def __init__(self, window_title, icon_path, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        


        self.title_bar = CustomTitleBar(window_title, icon_path, self.close_notification)
        
        
        
        self.setStyleSheet("""
            QDialog {
                background-color: #343541;
                border-radius: 10px;
            }
            QLineEdit {
                background-color: #202123; 
                border: 2px solid white; 
                color: white; 
                height: 30px;
                font-size: 16px;
            }
            QLabel {
                color: #c5c5d2;
                font-family: Helvetica;
                margin-bottom: 15px;
            }
            QPushButton {
                background-color: #343541;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #e5e5e5;
            }
        """)
    

        # Close button (as a QLabel with text)
        # self.close_button = QLabel("X", self)
        # self.close_button.setAlignment(Qt.AlignCenter)
        # self.close_button.setStyleSheet("""
        #     QLabel {
        #         background-color: #343541;
        #         color: white;
        #         border-radius: 5px;  /* Round button shape */
        #         padding: 8px;
        #         margin: 3px;
        #         font-size: 16px;
        #         cursor: pointer;  /* Change cursor to hand when hovering */
        #     }
        #     QLabel:hover {
        #         background-color: #e5e5e5;
        #     }
        # """)

        # Connect the close button's mousePressEvent to close the dialog


        # Label (your existing code)
        # self.label = QLabel(window_title, self)

        # Input field and Submit button arranged in a horizontal layout
        self.input_layout = QHBoxLayout()
        self.label = QLabel("Please enter your task description.", self)
        label_font = QFont()
        label_font.setPointSize(14)  # Set the desired font size
        self.label.setFont(label_font)  # Apply the font to the label
        self.input_field = QLineEdit(self)
        self.submit_button = QPushButton(self)
        button_image = QPixmap('./images.png').scaled(20,20)
        self.submit_button.setIcon(QIcon(button_image))
        button_size = QSize(20, 20)
        self.submit_button.setIconSize(button_image.size())
        self.submit_button.setFixedSize(button_size)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;  /* Transparent background */
                border: none;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                background-color: transparent;  /* Transparent background on hover */
            }
        """)
   
          
        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.input_field)
        self.input_layout.addWidget(self.submit_button)

        # Add widgets to the main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.title_bar)  # Important: Add your CustomTitleBar to the layout
        self.main_layout.addWidget(self.label)
        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addSpacing(20)
        # Submit button click event
        self.submit_button.clicked.connect(self.close_notification)

    def close_notification(self, event):
        task_description = self.input_field.text()
        if not task_description:
            # If no task description was entered, show a notification
            QMessageBox.warning(self, "Task Description", "Please enter a task description.")
            return  # Return without closing the dialog

        self.accept()  # Close the dialog if a description is entered

    def get_description(self):
        return self.input_field.text()

    def showEvent(self, event):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        new_geometry = QRect(
            screen_geometry.width() - self.width() - 10,
            screen_geometry.height() - self.height() - 10,
            self.width(),
            self.height()
        )
        self.setGeometry(new_geometry)

def show_notification_popup(current_window_title):
    window_title = "Task Description"  # Set your desired window title
    icon_path = './icon.png'
    dialog = TaskDescriptionInput(window_title, icon_path)
    result = dialog.exec_()
    if result == QDialog.Accepted:
        task_description = dialog.get_description()
        return task_description
    return None




def heartbeat_loop(client, bucket_id, poll_time, strategy, exclude_title=False):
    timer = 0
    popup_threshold = 5
    prev_app = None
    prev_title = None
    popup_shown_for_title = None

    while True:
        if os.getppid() == 1:
            logger.info("window-watcher stopped because parent process died")
            break

        current_window = None
        try:
            current_window = get_current_window(strategy)
            logger.debug(current_window)
        except (FatalError, OSError):
            logger.exception("Fatal error, stopping")
            break
        except Exception:
            logger.exception("Exception thrown while trying to get an active window")

        if current_window is None:
            logger.debug("Unable to fetch the window, trying again on the next poll")
        else:
            if current_window["title"] != prev_title:
                timer = 0
                prev_app = current_window["app"]
                prev_title = current_window["title"]

            if exclude_title:
                current_window["title"] = "excluded"

            now = datetime.now(timezone.utc)
            current_window_event = Event(timestamp=now, data=current_window)
            client.heartbeat(bucket_id, current_window_event, pulsetime=poll_time + 1.0, queued=True)

            if timer >= popup_threshold and popup_shown_for_title != prev_title:
                task_description = show_notification_popup(prev_app)
                if task_description:
                    save_to_csv(now, current_window, task_description, strategy)
                    popup_shown_for_title = prev_title

        timer += poll_time
        sleep(poll_time)


def save_to_csv(timestamp, window_info, task_description, strategy):
    csv_filename = "./task_log.csv"
    data = [
        {
            "Timestamp": timestamp.isoformat(),
            "Program": window_info["app"],
            "Program File Name": window_info["title"],
            "Task Description": task_description,
        }
    ]
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, mode="a", newline="") as csv_file:
        fieldnames = ["Timestamp", "Program", "Program File Name", "Task Description"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)


def main():
    args = parse_args()
    setup_logging(
        name="aw-watcher-window",
        testing=args.testing,
        verbose=args.verbose,
        log_stderr=True,
        log_file=True,
    )

    if sys.platform == "darwin":
        background_ensure_permissions()

    client = ActivityWatchClient(
        "aw-watcher-window", host=args.host, port=args.port, testing=args.testing
    )

    bucket_id = f"{client.client_name}_{client.client_hostname}"
    event_type = "currentwindow"
    client.create_bucket(bucket_id, event_type, queued=True)

    logger.info("aw-watcher-window started")
    sleep(1)
    with client:
        heartbeat_loop(
            client,
            bucket_id,
            poll_time=args.poll_time,
            strategy=args.strategy,
            exclude_title=args.exclude_title,
        )

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()



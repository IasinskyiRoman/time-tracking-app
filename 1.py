
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QApplication, QMessageBox, QWidget
from PyQt5.QtGui import QPixmap  # Import QPixmap for displaying an image
from PyQt5.QtCore import Qt, QRect
import sys
import logging

logger = logging.getLogger(__name__)
class CustomTitleBar(QWidget):
    def __init__(self, title, icon_path, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)  # Changed to QHBoxLayout

        # Create a QLabel for the icon
        icon_label = QLabel(self)
        icon_pixmap = QPixmap(icon_path)
        if icon_pixmap.isNull():
            logger.warning(f"Failed to load icon from path: {icon_path}")
        else:
            icon_pixmap = icon_pixmap.scaled(25, 25, Qt.KeepAspectRatio)  # Keep aspect ratio
            icon_label.setPixmap(icon_pixmap)
            layout.addWidget(icon_label)

        # Create a QLabel for the title text
        title_label = QLabel(title, self)
        font = title_label.font()
        font.setPointSize(24)
        title_label.setFont(font)
        layout.addWidget(title_label)


        # Apply padding to the title bar
        layout.setContentsMargins(10, 10, 10, 10)

def test_custom_titlebar():
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)
    
    title_bar = CustomTitleBar("Test Title", "icon.png")
    layout.addWidget(title_bar)

    window.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    test_custom_titlebar()

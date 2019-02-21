from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QLabel


def flag_label(language, height, **kwargs):
        flag = QLabel()
        pixmap = QPixmap("../resources/icons/{}-flag-small.png".format(language[0]), **kwargs)
        flag.setPixmap(pixmap.scaledToHeight(height))

        return flag


def image_label(image, height, **kwargs):
        label = QLabel()
        pixmap = QPixmap("images/No_Cover.jpg")
        if image is not None:
            pixmap.loadFromData(image)
        label.setPixmap(pixmap.scaledToHeight(height))

        return label

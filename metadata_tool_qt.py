# Build a small qt interface to navigate through the images: it displays both recto and verso images,
# loads the metadata if it exists in text boxes, allows to modify the metadata and save it back to the json file with a button
# Add a button to go to the next image or previous image
# Add a button to go to a specific image
# Add a button to go to the first image
# Add a button to go to the last image

# Let's make a V2 with a better layout and more information displayed
# I want the images on top of each other, on the left side
# The text boxes on the right side (smaller columns), with a title above each text box
# The buttons at the bottom of the window
# At first the images are resized to fit the window

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os
import json
from collections import defaultdict


class MetadataToolV2(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Metadata Tool V2')
        # Open full screen
        self.showMaximized()
        # self.showFullScreen()

        self.img_recto = QLabel()
        self.img_verso = QLabel()

        self.recto_description = QTextEdit()
        self.recto_texte = QTextEdit()
        self.verso_emetteur = QTextEdit()
        self.verso_lieu_emetteur = QTextEdit()
        self.verso_destinataire = QTextEdit()
        self.verso_lieu_destinataire = QTextEdit()
        self.verso_date = QTextEdit()
        self.verso_contenu = QTextEdit()

        self.btn_previous = QPushButton('Previous')
        self.btn_next = QPushButton('Next')
        self.btn_goto = QPushButton('Go to')
        self.btn_first = QPushButton('First')
        self.btn_last = QPushButton('Last')
        self.btn_save = QPushButton('Save')

        self.edit_goto = QLineEdit()

        self.main_layout = QVBoxLayout()

        self.content_layout = QHBoxLayout()

        self.layout_left = QVBoxLayout()
        self.layout_left.addWidget(self.img_recto)
        self.layout_left.addWidget(self.img_verso)

        self.layout_right = QVBoxLayout()
        self.layout_right.addWidget(QLabel('Description'))
        self.layout_right.addWidget(self.recto_description)
        self.layout_right.addWidget(QLabel('Texte'))
        self.layout_right.addWidget(self.recto_texte)
        self.layout_right.addWidget(QLabel('Emetteur'))
        self.layout_right.addWidget(self.verso_emetteur)
        self.layout_right.addWidget(QLabel('Lieu Emetteur'))
        self.layout_right.addWidget(self.verso_lieu_emetteur)
        self.layout_right.addWidget(QLabel('Destinataire'))
        self.layout_right.addWidget(self.verso_destinataire)
        self.layout_right.addWidget(QLabel('Lieu Destinataire'))
        self.layout_right.addWidget(self.verso_lieu_destinataire)
        self.layout_right.addWidget(QLabel('Date'))
        self.layout_right.addWidget(self.verso_date)
        self.layout_right.addWidget(QLabel('Contenu'))
        self.layout_right.addWidget(self.verso_contenu)

        self.content_layout.addLayout(self.layout_left)
        self.content_layout.addLayout(self.layout_right)

        self.layout_buttons = QHBoxLayout()
        self.layout_buttons.addWidget(self.btn_previous)
        self.layout_buttons.addWidget(self.btn_next)
        self.layout_buttons.addWidget(self.btn_goto)
        self.layout_buttons.addWidget(self.edit_goto)
        self.layout_buttons.addWidget(self.btn_first)
        self.layout_buttons.addWidget(self.btn_last)
        self.layout_buttons.addWidget(self.btn_save)

        self.main_layout.addLayout(self.content_layout)
        self.main_layout.addLayout(self.layout_buttons)
        self.setLayout(self.main_layout)

        self.btn_previous.clicked.connect(self.previous)
        self.btn_next.clicked.connect(self.next)
        self.btn_goto.clicked.connect(self.goto)
        self.btn_first.clicked.connect(self.first)
        self.btn_last.clicked.connect(self.last)
        self.btn_save.clicked.connect(self.save)

        self.show()

    def load_metadata(self, i):

        if not os.path.exists(f'metadata/{i+1}_metadata.json'):
            return

        with open(f'metadata/{i+1}_metadata.json', 'r') as f:
            metadata = json.load(f)
        # Convert to default dict to avoid key errors
        metadata = defaultdict(lambda: defaultdict(str), metadata)
        self.recto_description.setText(metadata['recto']['Description'])
        self.recto_texte.setText(metadata['recto']['Texte'])
        self.verso_emetteur.setText(metadata['verso']['Emetteur'])
        self.verso_lieu_emetteur.setText(metadata['verso']['Lieu Emetteur'])
        self.verso_destinataire.setText(metadata['verso']['Destinataire'])
        self.verso_lieu_destinataire.setText(metadata['verso']['Lieu Destinataire'])
        self.verso_date.setText(metadata['verso']['Date'])
        self.verso_contenu.setText(metadata['verso']['Contenu'])

    def save_metadata(self, i):
        metadata = {
            'recto': {
                'Description': self.recto_description.toPlainText(),
                'Texte': self.recto_texte.toPlainText()
            },
            'verso': {
                'Emetteur': self.verso_emetteur.toPlainText(),
                'Lieu Emetteur': self.verso_lieu_emetteur.toPlainText(),
                'Destinataire': self.verso_destinataire.toPlainText(),
                'Lieu Destinataire': self.verso_lieu_destinataire.toPlainText(),
                'Date': self.verso_date.toPlainText(),
                'Contenu': self.verso_contenu.toPlainText()
            }
        }
        with open(f'metadata/{i+1}_metadata.json', 'w') as f:
            json.dump(metadata, f, ensure_ascii=False)

    def previous(self):
        self.i -= 1
        self.load_image(self.i)
        self.load_metadata(self.i)

    def next(self):
        self.i += 1
        self.load_image(self.i)
        self.load_metadata(self.i)

    def goto(self):
        self.i = int(self.edit_goto.text()) - 1
        self.load_image(self.i)
        self.load_metadata(self.i)

    def first(self):
        self.i = 0
        self.load_image(self.i)
        self.load_metadata(self.i)

    def last(self):
        self.i = self.n - 1
        self.load_image(self.i)
        self.load_metadata(self.i)

    def save(self):
        self.save_metadata(self.i)

    def load_image(self, i):
        """
        Load the images from the cropped folder
        Resize the images to fit the window, keeping the aspect ratio
        """
        img_path_recto = f'cropped/{i+1}_recto_cropped.jpg'
        img_path_verso = f'cropped/{i+1}_verso_cropped.jpg'
        img_recto = QPixmap(img_path_recto)
        img_verso = QPixmap(img_path_verso)

        # Resize the images to fit the window
        img_recto = img_recto.scaledToWidth(800)
        img_verso = img_verso.scaledToWidth(800)

        self.img_recto.setPixmap(img_recto)
        self.img_verso.setPixmap(img_verso)

    def show(self):
        self.n = len(os.listdir('cropped')) // 2
        self.i = 0
        self.load_image(self.i)
        self.load_metadata(self.i)

        super().show()


class MetadataToolV3(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Metadata Tool V3')
        # Open full screen
        self.showMaximized()

        # Initial i
        self.i = 0

        self.img_recto = QLabel()
        self.img_verso = QLabel()

        self.recto_description = QLineEdit()
        self.recto_texte = QTextEdit()
        self.verso_emetteur = QLineEdit()
        self.verso_lieu_emetteur = QLineEdit()
        self.verso_destinataire = QLineEdit()
        self.verso_lieu_destinataire = QLineEdit()
        self.verso_date = QLineEdit()
        self.verso_contenu = QTextEdit()

        self.btn_previous = QPushButton('Previous')
        self.btn_next = QPushButton('Next')
        self.btn_goto = QPushButton('Go to')
        self.btn_first = QPushButton('First')
        self.btn_last = QPushButton('Last')
        self.btn_save = QPushButton('Save')

        self.edit_goto = QLineEdit()

        self.main_layout = QVBoxLayout()

        self.main_title = QVBoxLayout()
        self.main_title_text = f'Image {self.i+1}'
        self.main_title.addWidget(QLabel(self.main_title_text))
        self.main_layout.addLayout(self.main_title)

        self.content_layout = QHBoxLayout()

        self.layout_left = QVBoxLayout()
        self.layout_left.addWidget(self.img_recto)
        self.layout_left.addWidget(QLabel('Description'))
        self.layout_left.addWidget(self.recto_description)
        self.layout_left.addWidget(QLabel('Texte'))
        self.layout_left.addWidget(self.recto_texte)

        self.layout_right = QVBoxLayout()
        self.layout_right.addWidget(self.img_verso)
        self.layout_right.addWidget(QLabel('Emetteur'))
        self.layout_right.addWidget(self.verso_emetteur)
        self.layout_right.addWidget(QLabel('Lieu Emetteur'))
        self.layout_right.addWidget(self.verso_lieu_emetteur)
        self.layout_right.addWidget(QLabel('Destinataire'))
        self.layout_right.addWidget(self.verso_destinataire)
        self.layout_right.addWidget(QLabel('Lieu Destinataire'))
        self.layout_right.addWidget(self.verso_lieu_destinataire)
        self.layout_right.addWidget(QLabel('Date'))
        self.layout_right.addWidget(self.verso_date)
        self.layout_right.addWidget(QLabel('Contenu'))
        self.layout_right.addWidget(self.verso_contenu)

        self.content_layout.addLayout(self.layout_left)
        self.content_layout.addLayout(self.layout_right)

        self.layout_buttons = QHBoxLayout()
        self.layout_buttons.addWidget(self.btn_previous)
        self.layout_buttons.addWidget(self.btn_next)
        self.layout_buttons.addWidget(self.btn_goto)
        self.layout_buttons.addWidget(self.edit_goto)
        self.layout_buttons.addWidget(self.btn_first)
        self.layout_buttons.addWidget(self.btn_last)
        self.layout_buttons.addWidget(self.btn_save)

        self.main_layout.addLayout(self.content_layout)
        self.main_layout.addLayout(self.layout_buttons)
        self.setLayout(self.main_layout)

        self.btn_previous.clicked.connect(self.previous)
        self.btn_next.clicked.connect(self.next)
        self.btn_goto.clicked.connect(self.goto)
        self.btn_first.clicked.connect(self.first)
        self.btn_last.clicked.connect(self.last)
        self.btn_save.clicked.connect(self.save)

        self.show()

    def load_metadata(self, i):

        if not os.path.exists(f'metadata/{i+1}_metadata.json'):
            return

        with open(f'metadata/{i+1}_metadata.json', 'r') as f:
            metadata = json.load(f)
        # Convert to default dict to avoid key errors
        metadata = defaultdict(lambda: defaultdict(str), metadata)
        self.recto_description.setText(metadata['recto']['Description'])
        self.recto_texte.setText(metadata['recto']['Texte'])
        self.verso_emetteur.setText(metadata['verso']['Emetteur'])
        self.verso_lieu_emetteur.setText(metadata['verso']['Lieu Emetteur'])
        self.verso_destinataire.setText(metadata['verso']['Destinataire'])
        self.verso_lieu_destinataire.setText(metadata['verso']['Lieu Destinataire'])
        self.verso_date.setText(metadata['verso']['Date'])
        self.verso_contenu.setText(metadata['verso']['Contenu'])

    def save_metadata(self, i):
        metadata = {
            'recto': {
                'Description': self.recto_description.toPlainText(),
                'Texte': self.recto_texte.toPlainText()
            },
            'verso': {
                'Emetteur': self.verso_emetteur.toPlainText(),
                'Lieu Emetteur': self.verso_lieu_emetteur.toPlainText(),
                'Destinataire': self.verso_destinataire.toPlainText(),
                'Lieu Destinataire': self.verso_lieu_destinataire.toPlainText(),
                'Date': self.verso_date.toPlainText(),
                'Contenu': self.verso_contenu.toPlainText()
            }
        }
        with open(f'metadata/{i+1}_metadata.json', 'w') as f:
            json.dump(metadata, f, ensure_ascii=False)

    def previous(self):
        self.i -= 1
        self.load_image(self.i)
        self.load_metadata(self.i)
        self.update_title()

    def next(self):
        self.i += 1
        self.load_image(self.i)
        self.load_metadata(self.i)
        self.update_title()

    def goto(self):
        self.i = int(self.edit_goto.text()) - 1
        self.load_image(self.i)
        self.load_metadata(self.i)
        self.update_title()

    def first(self):
        self.i = 0
        self.load_image(self.i)
        self.load_metadata(self.i)
        self.update_title()

    def last(self):
        self.i = self.n - 1
        self.load_image(self.i)
        self.load_metadata(self.i)
        self.update_title()

    def save(self):
        self.save_metadata(self.i)

    def load_image(self, i):
        """
        Load the images from the cropped folder
        Resize the images to fit the window, keeping the aspect ratio
        """
        img_path_recto = f'cropped/{i+1}_recto_cropped.jpg'
        img_path_verso = f'cropped/{i+1}_verso_cropped.jpg'
        img_recto = QPixmap(img_path_recto)
        img_verso = QPixmap(img_path_verso)

        # Resize the images to fit the window
        img_recto = img_recto.scaledToWidth(800)
        img_verso = img_verso.scaledToWidth(800)

        self.img_recto.setPixmap(img_recto)
        self.img_verso.setPixmap(img_verso)

    def update_title(self):
        self.main_title_text = f'Image {self.i+1}/{self.n}'

    def show(self):
        self.n = len(os.listdir('cropped')) // 2
        self.i = 0
        self.load_image(self.i)
        self.load_metadata(self.i)
        self.update_title()

        super().show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MetadataToolV3()
    sys.exit(app.exec_())   # Start the application

# To run the script, open a terminal and type:
# python metadata_tool.py
# The interface should appear
# You can navigate through the images with the buttons
# You can modify the metadata and save it back to the json file
# You can also go to a specific image with the Go to button
# You can also go to the first or last image with the First and Last buttons
# When you close the interface, the script will stop

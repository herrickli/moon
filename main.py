import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsScene, QGraphicsPixmapItem
from interface import *
import os
import cv2
import xml.etree.ElementTree as ET

class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)

        self.btn_img_folder.clicked.connect(self.choose_img_folder)
        self.btn_xml_folder.clicked.connect(self.choose_xml_folder)
        self.btn_pred_folder.clicked.connect(self.choose_pred_folder)

        self.btn_next.clicked.connect(self.next_pic)
        self.btn_pre.clicked.connect(self.pre_pic)

        self.cbx_gt_box.stateChanged.connect(self.is_gt_box_draw)
        self.cbx_pred_box.stateChanged.connect(self.is_pred_box_draw)

        self.current_page = 0
        self.xml_folder_name = ''
        self.img_folder_name = ''
        self.pred_folder_name = ''

        self.ids = None
        self.id = ''
        self.gt_boxes = None


    def is_gt_box_draw(self):
        print(self.xml_folder_name)
        if self.xml_folder_name != '':
            self.refresh()

    def is_pred_box_draw(self):
        print(self.pred_folder_name)
        if self.pred_folder_name != '':
            self.refresh()

    def choose_img_folder(self):
        folder = QFileDialog.getExistingDirectory()
        if folder != '':
            if self.id +'.jpg' not in os.listdir(folder):
                text = 'Picture folder is not corresponding with prediction folder !'
                self.set_info_label_text_color(text, 'red')
            else:
                self.img_folder_name = folder
                self.lbl_img_folder.setText(self.img_folder_name)
                self.refresh()

    def choose_xml_folder(self):
        folder = QFileDialog.getExistingDirectory()
        if folder != '':
            if self.id + '.xml' not in os.listdir(folder):
                text = 'Annotations folder is not corresponding with predictions folder !'
                self.set_info_label_text_color(text, 'red')
                self.gt_boxes = None
            else:
                self.set_info_label_text_color('')
                self.xml_folder_name = folder
                self.lbl_xml_folder.setText(self.xml_folder_name)
                self.find_corresponding_xml()

    def choose_pred_folder(self):
        folder = QFileDialog.getExistingDirectory()
        if folder != '':
            if 'txt' not in [x.split('.')[-1] for x in os.listdir(folder)]:
                text = "No '.txt' prediction files found in this folder."
                self.set_info_label_text_color(text, 'red')
            else:
                self.set_info_label_text_color('')
                self.pred_folder_name = folder
                self.lbl_pred_folder.setText(self.pred_folder_name)
                self.ids = [x.split('.')[0] for x in os.listdir(folder) if x.endswith('.txt')]
                self.id = self.ids[self.current_page]
                self.find_corresponding_pred()


    def find_corresponding_xml(self):
        if self.xml_folder_name != '':
            gt_boxes = list()
            anno = ET.parse(os.path.join(self.xml_folder_name, self.id + '.xml'))
            for object in anno.findall('object'):
                box = dict()
                box['name'] = object.find('name').text
                box['coords'] = list()
                for tag in ['xmin', 'ymin', 'xmax', 'ymax']:
                    box['coords'].append(int(float(object.find('bndbox').find(tag).text)))
                gt_boxes.append(box)
            self.gt_boxes = gt_boxes

    def find_corresponding_pred(self):
        pred_boxes = list()
        txt_file = os.path.join(self.pred_folder_name, self.id + '.txt')
        with open(txt_file, 'r') as f:
            for line in f.readlines():
                box = dict()
                obj_name, score, xmin, ymin, xmax, ymax = line.split(' ')
                box['name'], box['score'] = obj_name, score
                box['bndbox'] = list()
                for tag in [xmin, ymin, xmax, ymax]:
                    box['bndbox'].append(int(float(tag)))
                pred_boxes.append(box)
        self.pred_boxes = pred_boxes

    def next_pic(self):
        self.current_page += 1
        self.refresh()

    def pre_pic(self):
        self.current_page -= 1
        self.refresh()

    def set_info_label_text_color(self, text, color='black'):
        self.pe = QPalette()
        if color == 'red':
            self.pe.setColor(QPalette.WindowText, Qt.red)
        else:
            self.pe.setColor(QPalette.WindowText, Qt.black)
        self.info_label.setText(text)
        self.info_label.setPalette(self.pe)

    def refresh(self):
        self.id = self.ids[self.current_page]
        img_path = os.path.join(self.img_folder_name, self.id+'.jpg')
        self.find_corresponding_xml()
        self.find_corresponding_pred()
        self.set_info_label_text_color('Current img:' + img_path)
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        y, x = img.shape[0], img.shape[1]

        if self.cbx_gt_box.isChecked():
            print('Ground Truth:', self.gt_boxes)
            for box in self.gt_boxes:
                xmin, ymin, xmax, ymax = box['coords']
                cv2.putText(img, box['name'], (xmin,ymin), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0, 255), 1)
                cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0, 255), 1)

        if self.cbx_pred_box.isChecked():
            print('Predictions:', self.pred_boxes)
            for box in self.pred_boxes:
                xmin, ymin, xmax, ymax = box['bndbox']
                cv2.putText(img, box['name'] + ' ' + box['score'], (xmin, ymin), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0, 255), 1)
                cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (255, 0, 0, 255), 1)

        frame = QImage(img, x, y, QImage.Format_RGBA8888)
        pix = QPixmap.fromImage(frame)
        item = QGraphicsPixmapItem(pix)
        scene = QGraphicsScene()
        scene.addItem(item)
        self.graphicsView.setScene(scene)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())

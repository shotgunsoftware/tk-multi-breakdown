# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from sgtk.platform.qt import QtCore
for name, cls in QtCore.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls

from sgtk.platform.qt import QtGui
for name, cls in QtGui.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls


from ..scene_browser import SceneBrowserWidget

from  . import resources_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(490, 618)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.browser = SceneBrowserWidget(Dialog)
        self.browser.setObjectName(u"browser")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.browser.sizePolicy().hasHeightForWidth())
        self.browser.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.browser)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.groupBox = QGroupBox(Dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.chk_green = QCheckBox(self.groupBox)
        self.chk_green.setObjectName(u"chk_green")
        icon = QIcon()
        icon.addFile(u":/res/green_bullet.png", QSize(), QIcon.Normal, QIcon.Off)
        self.chk_green.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.chk_green)

        self.chk_red = QCheckBox(self.groupBox)
        self.chk_red.setObjectName(u"chk_red")
        icon1 = QIcon()
        icon1.addFile(u":/res/red_bullet.png", QSize(), QIcon.Normal, QIcon.Off)
        self.chk_red.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.chk_red)

        self.horizontalLayout_3.addWidget(self.groupBox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.select_all = QPushButton(Dialog)
        self.select_all.setObjectName(u"select_all")

        self.horizontalLayout_3.addWidget(self.select_all)

        self.update = QPushButton(Dialog)
        self.update.setObjectName(u"update")

        self.horizontalLayout_3.addWidget(self.update)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Scene Breakdown", None))
        self.groupBox.setTitle("")
        self.label.setText(QCoreApplication.translate("Dialog", u"Filters:", None))
        self.select_all.setText(QCoreApplication.translate("Dialog", u"Select All Red", None))
        self.update.setText(QCoreApplication.translate("Dialog", u"Update Selected", None))
    # retranslateUi

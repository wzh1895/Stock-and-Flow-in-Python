# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interactive_sfd_ui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_widget_interactive_sfd(object):
    def setupUi(self, widget_interactive_sfd):
        widget_interactive_sfd.setObjectName("widget_interactive_sfd")
        widget_interactive_sfd.resize(640, 480)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(widget_interactive_sfd.sizePolicy().hasHeightForWidth())
        widget_interactive_sfd.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(widget_interactive_sfd)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_modifier = QtWidgets.QFrame(widget_interactive_sfd)
        self.frame_modifier.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_modifier.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_modifier.setObjectName("frame_modifier")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_modifier)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_add_stock = QtWidgets.QPushButton(self.frame_modifier)
        self.pushButton_add_stock.setObjectName("pushButton_add_stock")
        self.horizontalLayout.addWidget(self.pushButton_add_stock)
        self.pushButton_add_flow = QtWidgets.QPushButton(self.frame_modifier)
        self.pushButton_add_flow.setObjectName("pushButton_add_flow")
        self.horizontalLayout.addWidget(self.pushButton_add_flow)
        self.pushButton_add_aux = QtWidgets.QPushButton(self.frame_modifier)
        self.pushButton_add_aux.setObjectName("pushButton_add_aux")
        self.horizontalLayout.addWidget(self.pushButton_add_aux)
        self.pushButton_add_connector = QtWidgets.QPushButton(self.frame_modifier)
        self.pushButton_add_connector.setObjectName("pushButton_add_connector")
        self.horizontalLayout.addWidget(self.pushButton_add_connector)
        self.verticalLayout.addWidget(self.frame_modifier)
        self.graphicsView_interactive_sfd = QtWidgets.QGraphicsView(widget_interactive_sfd)
        self.graphicsView_interactive_sfd.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.graphicsView_interactive_sfd.setObjectName("graphicsView_interactive_sfd")
        self.verticalLayout.addWidget(self.graphicsView_interactive_sfd)

        self.retranslateUi(widget_interactive_sfd)
        QtCore.QMetaObject.connectSlotsByName(widget_interactive_sfd)

    def retranslateUi(self, widget_interactive_sfd):
        _translate = QtCore.QCoreApplication.translate
        widget_interactive_sfd.setWindowTitle(_translate("widget_interactive_sfd", "Form"))
        self.pushButton_add_stock.setText(_translate("widget_interactive_sfd", "Stock"))
        self.pushButton_add_flow.setText(_translate("widget_interactive_sfd", "Flow"))
        self.pushButton_add_aux.setText(_translate("widget_interactive_sfd", "Aux"))
        self.pushButton_add_connector.setText(_translate("widget_interactive_sfd", "Connector"))

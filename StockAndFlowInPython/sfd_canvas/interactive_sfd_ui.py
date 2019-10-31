# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interactive_sfd_ui.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
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
        self.pushButton_add_graph = QtWidgets.QPushButton(self.frame_modifier)
        self.pushButton_add_graph.setObjectName("pushButton_add_graph")
        self.horizontalLayout.addWidget(self.pushButton_add_graph)
        self.pushButton_del_element = QtWidgets.QPushButton(self.frame_modifier)
        self.pushButton_del_element.setObjectName("pushButton_del_element")
        self.horizontalLayout.addWidget(self.pushButton_del_element)
        self.verticalLayout.addWidget(self.frame_modifier)
        self.graphicsView_interactive_sfd = QtWidgets.QGraphicsView(widget_interactive_sfd)
        self.graphicsView_interactive_sfd.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.graphicsView_interactive_sfd.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.graphicsView_interactive_sfd.setObjectName("graphicsView_interactive_sfd")
        self.verticalLayout.addWidget(self.graphicsView_interactive_sfd)
        self.frame_simulation_control = QtWidgets.QFrame(widget_interactive_sfd)
        self.frame_simulation_control.setMaximumSize(QtCore.QSize(16777215, 70))
        self.frame_simulation_control.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_simulation_control.setObjectName("frame_simulation_control")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_simulation_control)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.widget_simulation_buttons = QtWidgets.QWidget(self.frame_simulation_control)
        self.widget_simulation_buttons.setObjectName("widget_simulation_buttons")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_simulation_buttons)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_start = QtWidgets.QPushButton(self.widget_simulation_buttons)
        self.pushButton_start.setObjectName("pushButton_start")
        self.horizontalLayout_3.addWidget(self.pushButton_start)
        self.pushButton_pause = QtWidgets.QPushButton(self.widget_simulation_buttons)
        self.pushButton_pause.setObjectName("pushButton_pause")
        self.horizontalLayout_3.addWidget(self.pushButton_pause)
        self.pushButton_reset = QtWidgets.QPushButton(self.widget_simulation_buttons)
        self.pushButton_reset.setObjectName("pushButton_reset")
        self.horizontalLayout_3.addWidget(self.pushButton_reset)
        self.horizontalLayout_2.addWidget(self.widget_simulation_buttons)
        self.simulation_slider = QtWidgets.QSlider(self.frame_simulation_control)
        self.simulation_slider.setOrientation(QtCore.Qt.Horizontal)
        self.simulation_slider.setObjectName("simulation_slider")
        self.horizontalLayout_2.addWidget(self.simulation_slider)
        self.label_time = QtWidgets.QLabel(self.frame_simulation_control)
        self.label_time.setObjectName("label_time")
        self.horizontalLayout_2.addWidget(self.label_time)
        self.verticalLayout.addWidget(self.frame_simulation_control)

        self.retranslateUi(widget_interactive_sfd)
        QtCore.QMetaObject.connectSlotsByName(widget_interactive_sfd)

    def retranslateUi(self, widget_interactive_sfd):
        _translate = QtCore.QCoreApplication.translate
        widget_interactive_sfd.setWindowTitle(_translate("widget_interactive_sfd", "Form"))
        self.pushButton_add_stock.setText(_translate("widget_interactive_sfd", "Stock"))
        self.pushButton_add_flow.setText(_translate("widget_interactive_sfd", "Flow"))
        self.pushButton_add_aux.setText(_translate("widget_interactive_sfd", "Aux"))
        self.pushButton_add_connector.setText(_translate("widget_interactive_sfd", "Connector"))
        self.pushButton_add_graph.setText(_translate("widget_interactive_sfd", "Graph"))
        self.pushButton_del_element.setText(_translate("widget_interactive_sfd", "Delete"))
        self.pushButton_start.setText(_translate("widget_interactive_sfd", "Run"))
        self.pushButton_pause.setText(_translate("widget_interactive_sfd", "Pause"))
        self.pushButton_reset.setText(_translate("widget_interactive_sfd", "Reset"))
        self.label_time.setText(_translate("widget_interactive_sfd", "00:00"))


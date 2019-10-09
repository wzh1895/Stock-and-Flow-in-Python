import sys
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QApplication

class InteractiveSFD(QGraphicsView):
    def __init__(self):
        super(InteractiveSFD, self).__init__()
        self.scene = QGraphicsScene()
        self.scene.addText('Hello')
        self.setScene(self.scene)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    interactive_sfd = InteractiveSFD()
    interactive_sfd.show()
    sys.exit(app.exec_())
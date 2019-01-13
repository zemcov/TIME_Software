from pyqtgraph import QtGui,QtCore
import sys
import ui_main
import numpy as np
import matplotlib.pylab
import time
import pyqtgraph
import sine_wave as sw
import multiprocessing as mp

class ExampleApp(QtGui.QMainWindow, ui_main.Ui_MainWindow):
    def __init__(self, parent=None):
        pyqtgraph.setConfigOption('background', 'w') #before loading widget
        super(ExampleApp, self).__init__(parent)
        self.setupUi(self)
        self.btnAdd.clicked.connect(self.update)
        self.grPlot.plotItem.showGrid(True, True, 0.7)
        # these will init the thread and allow it to send messages
        self.update()

    def update(self):
        # connecting thread functions
        self.updater = MyThread()
        self.updater.new_data.connect(self.data_update)
        self.updater.start()

    def data_update(self, t1, X, Y):
        C=pyqtgraph.hsvColor(time.time()/5%1,alpha=.5)
        pen=pyqtgraph.mkPen(color=C,width=10)
        self.grPlot.plot(X,Y,pen=pen,clear=True)
        print("update took %.02f ms"%((time.clock()-t1)*1000))

class MyThread(QtCore.QThread):

    new_data = QtCore.pyqtSignal(object,object,object)

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False

    def __del__(self):
        self.exiting = True
        self.wait()

    def run(self):
        queue = mp.Queue()
        p = mp.Process(target=sw.wave(queue))
        p.start()
        p.join()
        while not self.exiting :
            points=100 #number of data points
            X=np.arange(points)
            Y=np.sin(np.arange(points)/points*3*np.pi+time.time())
            data = queue.get()
            if data == 'done':
                break
            else :
                self.new_data.emit(data,X,Y)

if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()
    print("DONE")

import sys
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
import pafy, threading, ffmpeg
from os import remove, system


class DownloadTubeApp(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('./GuiFiles/RadioVerdeTubeGui.ui',self)

        # Estado inicial de los botones
        self.pushDownload.setEnabled(False) # Desabilitado
        self.pushOpen.setEnabled(False)     # Desabilitado
        self.pushSelectDir.setDefault(True) # Foco principal

        # Objeto Pafy
        self.audio = None

        # Inicialización datos de entrada
        self.url = ''; self.name = ''; self.artist = ''; self.format = ''
        self.dir = ''; self.cont = 0

        # Acción para recetear los botones
        self.pushClear.clicked.connect(self.reset)
        # Acción para abrir la carpeta de destino
        self.pushOpen.clicked.connect(self.openFolder)
        # Acción Para seleccionar la carpeta de destino
        self.pushSelectDir.clicked.connect(self.selecDir)
        # Acción para descargar el audio
        self.pushDownload.clicked.connect(self.downloadAudio)
        # Eliminar barra de títtulo
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        # Mover ventana
        self.frame_superior.mouseMoveEvent = self.moveWindow
    
    # Abrir la carpeta de destino
    def openFolder(self):
        dir = self.dir.replace('/', '\\')
        system('start %windir%\explorer.exe '+ dir)

    # Ejecuta la descarga del audio
    def callAudio(self, total,recvd,ratio,rate,eta):
        self.cont = ratio*100
        self.progressBar.setValue(self.cont)

    def downloadAudio(self):
        try:
            # Inicio de descarga
            self.audio = pafy.new(self.url).getbestaudio()
            self.audio.download(filepath='./temp/file', quiet=True, callback=self.callAudio)
            self.pushOpen.setEnabled(True)
            # Fin de descarga
            # Inicio de conversion
            stream = ffmpeg.input('./temp/file')
            filename = self.dir+'/'+self.name+self.format
            stream = ffmpeg.output(stream, filename, **{'metadata:':'artist='+self.artist,'metadata':'title='+self.name})
            ffmpeg.run(stream, quiet=True)
            remove('./temp/file')
        except:
            self.pushDownload.setEnabled(False)
    
    def downloadThread(self):
        self.th = threading.Thread(target=self.downloadAudio)
        self.th.start()

    # Selecciona directorio de destino
    def selecDir(self):
        if self.isCompleteData():
            self.dir = QFileDialog.getExistingDirectory()
            self.pushDownload.setEnabled(True)
        else:
            pass

    # Guardar los datos de los Inputs
    def recordInputs(self):    
        self.url = self.lineUrlVideo.text()
        self.name = self.lineNameFile.text()
        self.artist = self.lineArtist.text()
        self.format = self.comboFormat.currentText()
    
    # Validar si el formulario está completo
    def isCompleteData(self):
        self.recordInputs()
        return all([self.url,self.name,self.artist])

    # Modulos mover ventana
    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()
    
    def moveWindow(self, event):
        if self.isMaximized() == False:
            self.move(self.pos() + event.globalPos() - self.clickPosition)
            self.clickPosition = event.globalPos()
    
    def reset(self):
        self.pushOpen.setEnabled(False)
        self.pushDownload.setEnabled(False)


if __name__ == '__main__':
        app = QApplication(sys.argv)
        win = DownloadTubeApp()
        win.show()
        sys.exit(app.exec_())
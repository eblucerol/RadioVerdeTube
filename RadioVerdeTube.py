import sys
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import QThread, pyqtSignal
import pafy, ffmpeg
from os import remove, system, listdir

class Worker(QThread):
    sig = pyqtSignal(float)

    def __init__(self,audio,metadata):
        super().__init__()
        self.ratio = 0#int(ratio * 100)
        self.audio = audio
        self.filename,self.artist,self.name = metadata
    
    def callAudio(self, total,recvd,ratio,rate,eta):
        self.sig.emit(ratio)
        print(ratio)

    def downloadAudio(self):
        try:
            self.audio.download(filepath='./temp/file', quiet=True, callback=self.callAudio)
            stream = ffmpeg.input('./temp/file')
            stream = ffmpeg.output(stream, self.filename, **{'metadata:':'artist='+self.artist,'metadata':'title='+self.name})
            ffmpeg.run(stream, quiet=True)
            remove('./temp/file')
        except:
            print('Error')

    def run(self):
        self.downloadAudio()
        self.sig.emit(12.5)

class InfoWind(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('./GuiFiles/info.ui',self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

class DownloadTubeApp(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('./GuiFiles/RadioVerdeTubeGui.ui',self)

        # Limpia la carpeta temp de reciduos de anteriores descargas
        self.clearTemp()

        # Estado inicial de los botones
        self.pushDownload.setEnabled(False) # Desabilitado
        self.pushOpen.setEnabled(False)     # Desabilitado
        self.pushSelectDir.setDefault(True) # Foco principal

        # Objeto Pafy
        self.audio = None

        # Inicialización datos de entrada
        self.url = ''; self.name = ''; self.artist = ''; self.format = ''
        self.dir = ''

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

        # Ventana de información
        self.infowin = InfoWind()
        self.btnInfo.clicked.connect(self.infowin.show)
    
    # Abrir la carpeta de destino
    def openFolder(self):
        dir = self.dir.replace('/', '\\')
        system('start %windir%\explorer.exe '+ dir)

    # Ejecuta la descarga del audio
    def callAudio(self, total,recvd,ratio,rate,eta):
        print(ratio)

    def downloadAudio(self):
        try:
            # Borrar carpeta temporal
            self.clearTemp()

            filename = self.dir+'/'+self.name+self.format
            metadata = (filename,self.artist,self.name)
            # Inicio de descarga y conversion
            self.audio = pafy.new(self.url).getbestaudio()
            self.th = Worker(self.audio,metadata)
            self.th.sig.connect(self.updateProgressBar)
            self.th.start()
            self.setEnabled(False)
        except:
            self.pushDownload.setEnabled(False)
    
    def updateProgressBar(self, d):
        self.pbDownload.setValue(int(d*100))
        if d == 12.5:
            self.setEnabled(True)
            self.pushOpen.setEnabled(True)

    # Selecciona directorio de destino
    def selecDir(self):
        self.clearTemp()
        if self.isCompleteData():
            self.dir = QFileDialog.getExistingDirectory(directory='../')
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
    
    # Reinicia todo el control
    def reset(self):
        self.clearTemp()
        self.pushOpen.setEnabled(False)
        self.pushDownload.setEnabled(False)
        self.pbDownload.reset()
    
    # Borra contenido temporal
    def clearTemp(self):
        listFiles = listdir('./temp')
        for f in listFiles:
            remove('./temp/'+f)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = DownloadTubeApp()
    win.show()
    sys.exit(app.exec_())
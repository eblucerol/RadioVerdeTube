# Llamado a las herramientas básica
import sys
from os import system, listdir
from PyQt5 import sip
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from GUI.RadioVerdeTubeGui import Ui_radioVerdeGui
from pytube import YouTube
from os import remove
from time import sleep
import ffmpeg

# Definición de la clase principal de la aplicación
class TubeDownloadApp(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_radioVerdeGui()
        self.ui.setupUi(self)
        self.createDir()
        
        self.ui.pushSelectDir.setDefault(True)
        self.ui.pushDownload.setEnabled(False)
        self.ui.pushOpen.setEnabled(False)
        self.ui.pushSelectDir.clicked.connect(self.selectDir)
        self.ui.pushDownload.clicked.connect(self.downLoadAudio)
        self.ui.pushOpen.clicked.connect(self.openFile)
        self.ui.pushClear.clicked.connect(self.blockButton)

    def createDir(self):
        try:
            listdir().index('dir')
        except:
            f = open('dir','w')
            f.close()

    def blockButton(self):
        self.ui.pushOpen.setEnabled(False)
        self.ui.pushDownload.setEnabled(False)
        self.ui.pushSelectDir.setDefault(True)

    def selectDir(self):
        url = self.ui.lineUrlVideo.text()
        name = self.ui.lineNameFile.text()
        artist = self.ui.lineArtist.text()

        if all((url,name,artist)):
            dir = QFileDialog.getExistingDirectory()
            self.writeDir(dir)
            try:
                self.yt = YouTube(url)
                self.ui.pushDownload.setEnabled(True)
            except:
                print('mala url')
        else:
            self.ui.pushDownload.setEnabled(False)
            self.ui.pushOpen.setEnabled(False)

    
    def writeDir(self, directory):
        f = open('dir','w')
        f.write(directory)
        f.close()
    
    def readDir(self):
        f = open('dir','r')
        dir = f.read()
        f.close()
        return dir
    
    def downLoadAudio(self):
        dir = self.readDir()
        dir = dir.replace('/','\\')
        name = self.ui.lineNameFile.text()
        artist = self.ui.lineArtist.text()
        formt = self.ui.comboFormat.currentText()
        try:
            stream = self.yt.streams.filter(only_audio=True).order_by('abr').desc().first().download(output_path=dir, filename='file.webm')
            conv = ffmpeg.input(stream)
            conv = ffmpeg.output(conv, dir+'/'+name+formt,**{'metadata:':'artist='+artist,'metadata':'title='+name})
            ffmpeg.run(conv)
            remove(stream)
            self.ui.pushOpen.setEnabled(True)
        except:
            self.ui.pushDownload.setEnabled(False)
    
    def openFile(self):
        dir = self.readDir()
        dir = dir.replace('/','\\')
        system('start %windir%\explorer.exe '+ dir)
        print(dir)

if __name__ == '__main__':
        app = QApplication(sys.argv)
        win = TubeDownloadApp()
        win.show()
        sys.exit(app.exec_())
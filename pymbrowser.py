#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import signal
import shutil
import shelve
import pickle
#from PyQt4 import QtCore, QtGui, QtSql, Qt
#from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import *

import settings

class NoFocusDelegate(QStyledItemDelegate):

    def paint(self, painter, option, index):
    	itemOption = QStyleOptionViewItem(option)
    	if itemOption.state & QStyle.State_HasFocus:
    		itemOption.state ^= QStyle.State_HasFocus

    	QStyledItemDelegate.paint(self, painter, itemOption, index)


class Tree(QTreeView):

    def __init__(self, parent):

    	QTreeView.__init__(self)
    	self.setAttribute(Qt.WA_MacShowFocusRect, 0)

    	self.parent = parent
    	delegate = NoFocusDelegate()
    	self.setItemDelegate(delegate)
    	
    def keyPressEvent (self, e):
        print e.key()
        #if e.key() == 16777216:
        #	sys.exit()
        print self.currentIndex().data().toString()
        path = unicode(self.model().fileInfo(self.currentIndex()).absoluteFilePath())

        if e.key() == 16777223:

            
            if os.path.isdir(path):
                path_type = "directory"
            else:
                path_type = "file"

            msgBox = QMessageBox()
            msgBox.setText("Do you want to delete the "+ path_type +"\n"+ path);
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No);
            msgBox.setDefaultButton(QMessageBox.No)
            ret = msgBox.exec_()

            if ret == QMessageBox.Yes:				
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.unlink(path)

            self.model().refresh()

        elif e.key() == Qt.Key_B:
            print "B!"
            #print self.parent().objectName()
            if os.path.isfile(path):
                print "file"
                print unicode(self.model().fileInfo(self.currentIndex()).absoluteFilePath())
                self.parent.getBookmarks().append(unicode(self.model().fileInfo(self.currentIndex()).absoluteFilePath()))
                self.parent.playlist.model().setStringList(self.parent.bookmarks)

        else:
            QTreeView.keyPressEvent(self, e)
    	


class App(QApplication):

    def __init__(self, argv):
        QApplication.__init__(self, argv)
        self.bookmarks = []
        self.newfilesDB = []
        self.setupPlayed()
        self.setupUi()
        self.startTimer()


    def getBookmarks(self):
        return self.bookmarks

    def setupPlayed(self): 	
    	#test['apa'] = ['asdasd', 'asdasd']
    	try:
    		with open('bookmarks.pickle', 'rb') as f:
    			self.bookmarks = pickle.load(f)
    		f.close()
    	except:
    		pass

    	print self.bookmarks


    	
    def startTimer(self):
    	self.timer = QTimer()
    	self.connect(self.timer, SIGNAL('timeout()'), self.update)
    	#self.connect(self.dirtree, SIGNAL('activated(QModelIndex)'), self.startItemInPlayer)
    	#self.timer.start(300000)
    	self.timer.start(settings.REFRESH_RATE * 600)
    	
    def update(self):
    	#print "."
    	self.dirmodel.refresh()

    def toggleNewFiles(self):

        if self.newfiles.isVisible():
            self.newfiles.hide()
            self.dirtree.setFocus()
        else:
            self.newfiles.show()
            self.newfiles.setFocus()

    def togglePlaylist(self):
    	#print "klick"
    	#print dir(self.playlist)
    	if self.playlist.isVisible():
    		self.playlist.hide()
    		self.dirtree.setFocus()
    	else:
    		self.playlist.show()
    		self.playlist.setFocus()
    	
    def setupUi(self):
    	
    	self.main = QWidget()
    	self.mainLayout = QVBoxLayout()
    	self.main.setLayout(self.mainLayout)
    	
    	self.window = QMainWindow()
    	self.window.setWindowTitle("mediaspelare")
    	self.window.setCentralWidget(self.main)

        self.playlist = QListView()
        self.playlist.setModel(QStringListModel(self.bookmarks))
        self.playlist.hide()


        self.newfiles = QListView()
        self.newfiles.setModel(QStringListModel(self.newfilesDB))
        self.newfiles.hide()

    	
    	css_file = open("style.css", "r")
    	css = css_file.read()
    	css_file.close()

    	self.window.setStyleSheet(css)
    	self.main.setStyleSheet(css)
    	
    	self.dirmodel = QDirModel()
    	self.dirmode.setSorting(QDir.DirsFirst)
    	self.dirmodel.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
    	self.dirmodel.setNameFilters(settings.FILETYPES)
    	
    	self.dirtree = Tree(self)
    	self.dirtree.setModel(self.dirmodel)
    	#self.dirtree.setRootIndex(self.dirmodel.index(QDir.currentPath()))
    	self.dirtree.setRootIndex(self.dirmodel.index(settings.BASE_DIR))
    	
    	self.dirtree.hideColumn(1)
    	self.dirtree.hideColumn(2)
    	self.dirtree.hideColumn(3)
    	self.dirtree.header().hide()
    	self.dirtree.setFont(QFont("Gill Sans", 60))
    	self.dirtree.setIndentation(30)
    	self.dirtree.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    	self.dirtree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    	self.dirtree.setFrameStyle(QFrame.NoFrame)
    	self.dirtree.setIconSize(QSize(100, 100))
    	
    	self.connect(self.dirtree, SIGNAL('activated(QModelIndex)'), self.startItemInPlayer)

    	self.button = QPushButton("Hello")
    	#self.button.setGeometry(5, 10, 100, 25)

        
    	#self.mainLayout.addWidget(self.button)
    	self.mainLayout.addWidget(self.playlist)
    	self.mainLayout.addWidget(self.dirtree)
    	self.window.resize(1000, 700)
    	#self.window.showFullScreen()

    	self.window.installEventFilter(self)
    	#self.window.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
    	#self.main.showMaximized()

    	self.window.show()


    	self.connect(self.button, SIGNAL('clicked()'), self.togglePlaylist)

    	animate = QPropertyAnimation(self.playlist, "geometry")
    	animate.setDuration (10000)
    	animate.setStartValue (QRect (0, 0, 100, 30))
    	animate.setEndValue (QRect (2500, 2500, 100, 30))

    	#animate.start()
    	print "done"

    def addToPlayed(self, path):
    	print path

    def savePlaylist(self):
        print self.bookmarks
    	with open('bookmarks.pickle', 'wb') as f:
    		pickle.dump(self.bookmarks, f)   
    		f.close()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key = event.key() 
            if key == Qt.Key_F12:
            	self.togglePlaylist()
            if key == Qt.Key_F11:
                if self.window.isFullScreen():
                    self.window.setWindowFlags(self._flags)
                    if self._state == 'm':
                        self.window.showMaximized()
                    else:
                        self.window.showNormal()
                        self.window.setGeometry(self._geometry)
                else:
                    self._state = 'm' if self.window.isMaximized() else 'n'
                    self._flags = self.window.windowFlags()
                    self._geometry = self.window.geometry()
                    self.window.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
                    self.window.showFullScreen()
                return True
            elif key == Qt.Key_Escape:
                self.savePlaylist()
                self.window.close()
        return QWidget.eventFilter(self, obj, event)


    def startItemInPlayer(self, i):
    	#print "fil", self.dirmodel.filePath(i)
    	if not self.dirmodel.isDir(i):
    		os.system("killall vlc")
    		self.addToPlayed(unicode(self.dirmodel.filePath(i)))
    		#L = ['vlc', '-f', '--video-on-top', '--no-show-intf',  str(self.dirmodel.filePath(i)), 'vlc:quit']
    		L = ['cvlc', '-I lirc', '-f', unicode(self.dirmodel.filePath(i))]
    		#L = ['vlc', '-f', str(self.dirmodel.filePath(i))]
    		os.spawnvp(os.P_NOWAIT, 'cvlc', L)
    		#os.system('wmctrl -r "VLC My Video Output" -b add,above')
    	
    	
if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	app = App(sys.argv)
	app.exec_()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import signal
import shutil
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

	def __init__(self):

		QTreeView.__init__(self)
		self.setAttribute(Qt.WA_MacShowFocusRect, 0)

		delegate = NoFocusDelegate()
		self.setItemDelegate(delegate)
		
	def keyPressEvent (self, e):
		if e.key() == 16777223:
		
			path = unicode(self.model().fileInfo(self.currentIndex()).absoluteFilePath())
			if os.path.isdir(path):
				type = "directory"
			else:
				type = "file"
			
			msgBox = QMessageBox()
			msgBox.setText("Do you want to delete the "+ type +"\n"+ path);
			msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No);
			msgBox.setDefaultButton(QMessageBox.No)
			ret = msgBox.exec_()
			
			if ret == QMessageBox.Yes:				
				if os.path.isdir(path):
					shutil.rmtree(path)
				else:
					os.unlink(path)
					
				self.model().refresh()			
		else:
			QTreeView.keyPressEvent(self, e)
		
	

class App(QApplication):

	def __init__(self, argv):
		QApplication.__init__(self, argv)
		self.setupUi()
		self.startTimer()
		
	def startTimer(self):
		self.timer = QTimer()
		self.connect(self.timer, SIGNAL('timeout()'), self.update)
		#self.connect(self.dirtree, SIGNAL('activated(QModelIndex)'), self.startItemInPlayer)
		#self.timer.start(300000)
		self.timer.start(settings.REFRESH_RATE * 600)
		
	def update(self):
		#print "."
		self.dirmodel.refresh()
		
	def setupUi(self):
		
		self.main = QWidget()
		self.mainLayout = QVBoxLayout()
		self.main.setLayout(self.mainLayout)
		
		self.main.setStyleSheet (" \
                QWidget {background: #201F21; color: #D9D9D9;}") 
		
		self.window = QMainWindow()
		self.window.setWindowTitle("mediaspelare")
		self.window.setCentralWidget(self.main)
		
		self.window.setStyleSheet (" \
                QTreeView { \
                	background: #201F21; \
                	color: #D9D9D9; \
                	font-size: 36px; \
                	show-decoration-selected: 0; \
                } \
                QTreeView::item:selected { \
                	background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4F4E50, stop: 1 #201F21); \
					border: 2px solid #201F21; \
					outline: none; \
					border-radius: 8px; \
				} \
				QTreeView::branch { \
					background: #201F21; \
					color: #201F21 \
				} \
		") 
		
		self.dirmodel = QDirModel()
		self.dirmodel.setSorting(QDir.DirsFirst)
		self.dirmodel.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
		self.dirmodel.setNameFilters(['*.mpg', '*.wmv', '*.avi', '*.iso', '*.mkv'])
		
		self.dirtree = Tree()
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
		
		self.mainLayout.addWidget(self.dirtree)
		self.window.resize(1000, 700)
		#self.window.showFullScreen()

		self.window.show()
	
	def startItemInPlayer(self, i):
		#print "fil", self.dirmodel.filePath(i)
		if not self.dirmodel.isDir(i):
			os.system("killall vlc")
			#L = ['vlc', '-f', '--video-on-top', '--no-show-intf',  str(self.dirmodel.filePath(i)), 'vlc:quit']
			L = ['cvlc', '-I lirc', '-f', unicode(self.dirmodel.filePath(i))]
			#L = ['vlc', '-f', str(self.dirmodel.filePath(i))]
			os.spawnvp(os.P_NOWAIT, 'cvlc', L)
			#os.system('wmctrl -r "VLC My Video Output" -b add,above')
		
		
if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	app = App(sys.argv)
	app.exec_()

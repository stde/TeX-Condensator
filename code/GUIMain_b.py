# -*- coding: utf-8 -*-
import sys 
from PyQt4 import QtGui, QtCore
from texGUI import Ui_Dialog as DI

class MyDialog(QtGui.QDialog, DI): 
	
	global changed, entryText, authors, title, subtitle, institute, date, mail, keyWordPriority, numberOfSlides, 			charactersPerSlide, dirName
	changed = False
	dirName = ""

	def __init__(self): 
		QtGui.QDialog.__init__(self) 
		self.setupUi(self)
		self.connect(self.buttonOK, QtCore.SIGNAL("clicked()"), self.onOK) 
		self.connect(self.buttonQuit, QtCore.SIGNAL("clicked()"), self.onQuit)  
		self.connect(self.buttonOpenDir, QtCore.SIGNAL("clicked()"), self.dir_dialog)
		self.connect(self.buttonOpenFile, QtCore.SIGNAL("clicked()"), self.file_dialog)
		self.connect(self.textEntry, QtCore.SIGNAL("selectionChanged()"), self.onTextEntry)
		self.connect(self.keyWordPrioritySlider, QtCore.SIGNAL("valueChanged(int)"),self.onkeyWordPrioritySlider)
		self.connect(self.slidesSlider, QtCore.SIGNAL("valueChanged(int)"), self.onslidesSlider)
		self.connect(self.charsSlider, QtCore.SIGNAL("valueChanged(int)"), self.oncharsSlider)
		self.setFixedSize(self.size())
		self.setTabOrder(self.lineEditAuthors, self.lineEditTitle)
		self.setTabOrder(self.lineEditTitle, self.lineEditSubtitle)
		self.setTabOrder(self.lineEditSubtitle, self.lineEditInstitute)
		self.setTabOrder(self.lineEditInstitute, self.lineEditDate)
		self.setTabOrder(self.lineEditDate, self.lineEditMail)
		self.setTabOrder(self.lineEditMail, self.doubleSpinBox)
		self.setTabOrder(self.doubleSpinBox, self.spinBox)
		self.setTabOrder(self.spinBox, self.charsSpinBox)
		self.setTabOrder(self.charsSpinBox, self.buttonOK)

		self.buttonQuit.setFocus()
		self.doubleSpinBox.setRange(0.0,1.0)
		self.doubleSpinBox.setSingleStep(0.01)
		self.keyWordPrioritySlider.setRange(0,100)
		self.keyWordPrioritySlider.setSingleStep(1)
		self.spinBox.setMinimum(0)
		self.spinBox.setSingleStep(1)
		self.slidesSlider.setMinimum(0)
		self.slidesSlider.setSingleStep(1)
		self.charsSpinBox.setRange(0,1000)
		self.charsSpinBox.setSingleStep(1)
		self.charsSpinBox.setValue(400)
		self.charsSlider.setRange(0,1000)
		self.charsSlider.setSingleStep(1)
		

	def onOK(self):
		global entryText, authors, title, subtitle, institute, date, mail, keyWordPriority, numberOfSlides, 			charactersPerSlide
		entryText = self.textEntry.toPlainText()
		authors = self.lineEditAuthors.text()
		title = self.lineEditTitle.text()
		subtitle = self.lineEditSubtitle.text()
		institute = self.lineEditInstitute.text()
		date = self.lineEditDate.text()
		mail = self.lineEditMail.text()
		keyWordPriority = self.doubleSpinBox.value()
		numberOfSlides = self.spinBox.value()
		charactersPerSlide = self.charsSpinBox.value()
		self.close()

	def onQuit(self): 
		self.close()
		sys.exit()

	def onkeyWordPrioritySlider(self):
		self.doubleSpinBox.setValue(self.keyWordPrioritySlider.value()/100.0)

	def onslidesSlider(self):
		self.spinBox.setValue(self.slidesSlider.value())

	def oncharsSlider(self):
		self.charsSpinBox.setValue(self.charsSlider.value())	

	def onTextEntry(self):
		global changed
		if not changed:
			color = QtGui.QColor()
			color.setNamedColor("black")
			self.textEntry.setTextColor(color)
			self.textEntry.setFontItalic(False)
			self.textEntry.setText("")
			changed = True

	def file_dialog(self):
		global changed 
		if not self.textEntry.isReadOnly():
			fd = QtGui.QFileDialog(self)
			self.filename = fd.getOpenFileName()
			from os.path import isfile
			if isfile(self.filename):
				import codecs
				fobj = open(self.filename,'r')
				s = ""
				for line in fobj:
					s += line
				self.textEntry.setText(s)
				changed = True

	def dir_dialog(self):
		global dirName, changed
		if self.textEntry.toPlainText() == "" or not changed:
			d = QtGui.QFileDialog(self)
			dirName = d.getExistingDirectory()
			print dirName
			if not dirName == "":
				self.onTextEntry()
				self.textEntry.setReadOnly(True)

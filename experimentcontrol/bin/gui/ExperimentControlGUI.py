"""
__version__ = "$Revision: 1.10 $"
__date__ = "$Date: 2004/08/12 19:14:23 $"

PythonCard implementation of a GUI for the ExperimentControl
"""

import os, sys
import wx
from wx.html import HtmlEasyPrinting
from PythonCard import configuration, dialog, model
from sofiehdfformat.core.SofiePyTableAccess import SofiePyTableAccess
import time
import thread

STARTBUTTON_BACKGROUNDCOLOR_START=(0, 255, 0, 255)
STARTBUTTON_BACKGROUNDCOLOR_STOP=(255,0, 0, 255)
EXPERIMENTSTATUS_INACTIVE='INACTIVE'
EXPERIMENTSTATUS_SETTINGUP='SETTING UP'
EXPERIMENTSTATUS_RUNNING='DO THE EXPERIMENT NOW'
EXPERIMENTSTATUS_TEARINGDOWN='EXPERIMENT BUSY SHUTTING DOWN'

def textToHtml(txt):
    # the wxHTML classes don't require valid HTML
    # so this is enough
    html = txt.replace('\n\n', '<P>')
    html = html.replace('\n', '<BR>')
    return html


class ExperimentControlBackground(model.Background):
    filename=None
    arDevice=None
    imuDevice=None
    imuhost = '127.0.0.1'
    imuPort = 1234
    runName=None
    running = False
    
    def _updateRunList(self):
        self.components.runList.clear()           
        self.components.runList.insertItems(SofiePyTableAccess.getRunsInTheFile(self.filename),0)
        
    def _getPathFromDialog(self, 
               wildCard = "USB Serial device (*ttyUSB*)|*ttyUSB*|Serial device (*tty*)|*tty*|All files (*.*)|*.*"):
        result = dialog.openFileDialog(wildcard=wildCard)
        if result.accepted:
            return result.paths[0]
        else:
            return '';
    def _testSerialDevice(self,device,errorString):
        if device:
            try:
                
                if not os.path.exists(device):
                    dialog.alertDialog(self,'The '+errorString+' is not a serial device','Device Problem')
                    return False
            except:
                dialog.alertDialog(self,'The '+errorString+' cannot be opened.'+\
                                   str(device),'Device Problem')
                return False
        return True
    
    def _updateGlobalExperimentFeedback(self,status):
        self.components.globalExperimentFeedback.clear()
        self.components.globalExperimentFeedback.writeText(status)
            
    def on_initialize(self, event):
        # if you have any initialization
        # including sizer setup, do it here
        # self.loadConfig()
        self.startTitle = self.title

    def loadConfig(self):
        pass

    def saveConfig(self):
        pass

    def doExit(self):
        return 1

    def on_close(self, event):
        if self.doExit():
            # self.saveConfig()
            self.fileHistory = None
            self.printer = None
            event.skip()

    def on_filename_mouseDoubleClick(self, event):
        self.filename = self._getPathFromDialog(wildCard = "HDF 5 File (*.h5)|*.H5;*.h5|All files (*.*)|*.*")
        self.components.filename.writeText(self.filename)
        self.title = os.path.split(self.filename)[-1] + ' - ' + self.startTitle
        self.statusBar.text = self.filename
        self._updateRunList()  
        
    def on_runList_mouseUp(self, event):
        self.runName = self.components.runList.stringSelection
        self.components.runName.clear()
        self.components.runName.writeText(self.runName)

    def on_runName_loseFocus(self, event=None):
        self.runName = self.components.runName.getLineText(0)
        if not self.runName:
            dialog.alertDialog(self,'The Run Name is not set.','Check you run name')
            return False
        if self.filename:
            if self.runName in SofiePyTableAccess.getRunsInTheFile(self.filename):
                dialog.alertDialog(self,'The Run Name already exists.','Check you run name')
                return False
        return True
    def on_imuDevice_mouseDoubleClick(self, event):
        self.imuDevice = self._getPathFromDialog()
        self.components.imuDevice.writeText(self.imuDevice)
    def on_arDevice_mouseDoubleClick(self, event):
        self.arDevice = self._getPathFromDialog(
                wildCard = "Serial device (*video*)|*video*|All files (*.*)|*.*")
        self.components.arDevice.writeText(self.arDevice)
    def on_startStopButton_mouseClick(self,event):  
        if not self.on_runName_loseFocus():
            return False
        if not self._testSerialDevice(self.arDevice,' AR DEVICE'):
            return False
        if not self._testSerialDevice(self.imuDevice,' IMU DEVICE'):
            return False
        if self.components.startStopButton.checked:
            #------- dialog.alertDialog(self,'Startng RUN','Check you run name')
            self.components.startStopButton.label = 'Stop'
            self.components.startStopButton.backgroundColor = STARTBUTTON_BACKGROUNDCOLOR_STOP
            self.running = True;
        else:
            #------ dialog.alertDialog(self,'Stopping RUN','Check you run name')
            self.components.startStopButton.label = 'Start'
            self.components.startStopButton.backgroundColor = STARTBUTTON_BACKGROUNDCOLOR_START
            self.running = False;
    def on_menuFilePrint_select(self, event):
        # put your code here for print
        # the commented code below is from the textEditor tool
        # and is simply an example
        
        #source = textToHtml(self.components.fldDocument.text)
        #self.printer.PrintText(source)
        pass
    def on_menuFilePrintPreview_select(self, event):
        # put your code here for print preview
        # the commented code below is from the textEditor tool
        # and is simply an example
        
        #source = textToHtml(self.components.fldDocument.text)
        #self.printer.PreviewText(source)
        pass
    def on_menuFilePageSetup_select(self, event):
        self.printer.PageSetup()
    # the following was copied and pasted from the searchexplorer sample
    def on_menuEditUndo_select(self, event):
        widget = self.findFocus()
        if hasattr(widget, 'editable') and widget.canUndo():
            widget.undo()
    def on_menuEditRedo_select(self, event):
        widget = self.findFocus()
        if hasattr(widget, 'editable') and widget.canRedo():
            widget.redo()
    def on_menuEditCut_select(self, event):
        widget = self.findFocus()
        if hasattr(widget, 'editable') and widget.canCut():
            widget.cut()
    def on_menuEditCopy_select(self, event):
        widget = self.findFocus()
        if hasattr(widget, 'editable') and widget.canCopy():
            widget.copy()
    def on_menuEditPaste_select(self, event):
        widget = self.findFocus()
        if hasattr(widget, 'editable') and widget.canPaste():
            widget.paste()
    def on_menuEditClear_select(self, event):
        widget = self.findFocus()
        if hasattr(widget, 'editable'):
            if widget.canCut():
                # delete the current selection,
                # if we can't do a Cut we shouldn't be able to delete either
                # which is why i used the test above
                sel = widget.replaceSelection('')
            else:
                ins = widget.getInsertionPoint()
                try:
                    widget.replace(ins, ins + 1, '')
                except:
                    pass
    def on_menuEditSelectAll_select(self, event):
        widget = self.findFocus()
        if hasattr(widget, 'editable'):
            widget.setSelection(0, widget.getLastPosition())
    def on_doHelpAbout_command(self, event):
        # put your About box here
        pass
    
    def updateGlobalExperimentFeedBackSettingUp(self):
        self._updateGlobalExperimentFeedback(EXPERIMENTSTATUS_SETTINGUP)
    def updateGlobalExperimentFeedBackRunning(self):
        self._updateGlobalExperimentFeedback(EXPERIMENTSTATUS_RUNNING)
    def updateGlobalExperimentFeedBackTearingDown(self):
        self._updateGlobalExperimentFeedback(EXPERIMENTSTATUS_TEARINGDOWN)
    def updateGlobalExperimentFeedBackInactive(self):
        self._updateGlobalExperimentFeedback(EXPERIMENTSTATUS_INACTIVE)

def ExecutionThread(*argtuple):
        """
        The Experiment Control Thread.
        """
        print "ExecutionThread: entered"
        experimentControlBackground = argtuple[0]
        print "ExecutionThread: starting loop"
        while True:
            #Waiting to run
            print 'Waiting to run.'
            while experimentControlBackground.running == False:
                time.sleep(0.5)
            #In A Run Cycle
            #Setting up
            print 'Settting Up'
            experimentControlBackground.updateGlobalExperimentFeedBackSettingUp()
            i=8;
            while i>0:
                time.sleep(1)
                i -= 1
                print '.'
            print 'Running'
            experimentControlBackground.updateGlobalExperimentFeedBackRunning()
            while experimentControlBackground.running == True:
                time.sleep(0.25)
            #Tearing Down
            print 'Tear down'
            experimentControlBackground.updateGlobalExperimentFeedBackTearingDown()
            i=8;
            while i>0:
                time.sleep(1)
                i -= 1
                print '.'
            print 'Stopped'
            experimentControlBackground.updateGlobalExperimentFeedBackInactive()
            
if __name__ == '__main__':
    app = model.Application(ExperimentControlBackground)
    thread.start_new_thread(ExecutionThread, (app.getCurrentBackground(),))
    app.MainLoop()

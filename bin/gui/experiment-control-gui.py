#!/usr/bin/python
"""
__version__ = "$Revision: 1.10 $"
__date__ = "$Date: 2004/08/12 19:14:23 $"

PythonCard implementation of a GUI for the ExperimentControl
"""

import os, sys          
#from wx.html import HtmlEasyPrinting
from PythonCard import configuration, dialog, model
from sofiehdfformat.core.SofiePyTableAccess import SofiePyTableAccess
from experimentcontrol.core.control import startExperiment, syncListeners,shutDownExperiment,isCorrectFilename
from experimentcontrol.core.Exceptions import OutFileMustBeAbsolutePath, OutFileMustBeh5Extention
from wxAnyThread import anythread
import roslib; roslib.load_manifest('sofiehdfformat_rosdriver')
from sofiehdfformat_rosdriver.import_csv_data import exportBagData
import time
import threading
import traceback
import logging
import subprocess
from experimentcontrol.core.experimentcontrollogging import setLogger

ITERATIONS_SETTING_UP=8
ITERATIONS_TEARING_DOWN=2

UNTITLEDFILENAME='untitled.h5'

STARTBUTTON_BACKGROUNDCOLOR_START=(0, 255, 0, 255)
STARTBUTTON_BACKGROUNDCOLOR_STOP=(255,0, 0, 255)
STARTBUTTON_START='Start'
STARTBUTTON_WAIT='Wait'
STARTBUTTON_STOP='Stop'

EXPERIMENTSTATUS_INACTIVE='INACTIVE'
EXPERIMENTSTATUS_SETTINGUP='SETTING UP'
EXPERIMENTSTATUS_RUNNING='DO THE EXPERIMENT NOW'
EXPERIMENTSTATUS_TEARINGDOWN='EXPERIMENT BUSY SHUTTING DOWN'
EXPERIMENTSTATUS_ERRORSETTINGUP='ERROR SETTING UP'
EXPERIMENTSTATUS_ERRORTEARINGDOWN='ERROR TEARINGDOWN'
EXPERIMENTSTATUS_ERRORRUNNING='ERROR RUNNING'

def textToHtml(txt):
    # the wxHTML classes don't require valid HTML
    # so this is enough
    html = txt.replace('\n\n', '<P>')
    html = html.replace('\n', '<BR>')
    return html


class ExperimentControlBackground(model.Background):
    filename=None
    serialAr=None
    serialImu=None
    serialAnt=None
    imuHost = '127.0.0.1'
    imuPort = 1234
    runName=None
    running = False
    
    def _updateRunList(self):
        self.components.runList.clear()
        runList = list(set([self._getBaseRunName(runName) for runName in 
                    SofiePyTableAccess.getRunsInTheFile(self.filename)
                    if runName != '/RunMeta'
                    ] ))      
        self.components.runList.insertItems(runList,0)
        
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
    def _getBaseRunName(self,runName):
        runNameSplit = runName.split('/')
        if len(runNameSplit) >= 2:
            return runNameSplit[1]
        return runName
    
    def _updateGlobalExperimentFeedback(self,status):
        self.components.globalExperimentFeedback.clear()
        self.components.globalExperimentFeedback.writeText(status)
        
    def _getTextArea(self,textAreaName):
        numberOflines = self.components.get(textAreaName).getNumberOfLines()
        theText = '\n'.join([self.components.get(textAreaName).getLineText(i) 
                   for i in range(0,numberOflines)])
        logging.debug("GETTEXT AREA:"+theText)
        return theText
    
    def _setText(self,textComponentName,theText):
        self.components.get(textComponentName).clear()
        if theText:
            self.components.get(textComponentName).appendText(theText)
        
    def _setRunMeta(self,runName):
        if not runName:
            logging.debug('Run name not set.')
            return
        runName = self._getBaseRunName(runName)
        runMeta = {'runName':runName,
                    'runExperimentType': self.components.runExperimentType.getLineText(0),
                           'runSubject':self.components.runSubject.getLineText(0),
                           'runObject':self.components.runObject.getLineText(0),
                           'runSuccessful':self.components.runSuccessful.checked,
                           'runCorrupted':self.components.runCorrupted.checked,
                           'runNotes':self._getTextArea('runNotes')
                           }
        logging.debug(runMeta)
        SofiePyTableAccess.setRunMetaInFile(self.filename,runName,runMeta)
        
    def _getRunMeta(self,runName):
        runMeta = SofiePyTableAccess.getRunMetaInFile(self.filename, runName)
        if runMeta:
            runNotes =runMeta['runNotes']
            runSubject =runMeta['runSubject']
            runObject =runMeta['runObject']
            runSuccessful =runMeta['runSuccessful']
            runCorrupted =runMeta['runCorrupted']
            runExperimentType =runMeta['runExperimentType']
            
            self._setText('runExperimentType',runExperimentType)
            self._setText('runNotes',runNotes)
            self._setText('runSubject',runSubject)
            self._setText('runObject',runObject)
            self.components.runSuccessful.checked = runSuccessful
            self.components.runCorrupted.checked = runCorrupted
            self._setText('runExperimentType',runExperimentType)
        else:
            self._setText('runExperimentType',None)
            self._setText('runNotes',None)
            self._setText('runSubject',None)
            self._setText('runObject',None)
            self.components.runSuccessful.checked = False
            self.components.runCorrupted.checked = False
            self._setText('runExperimentType',None)
        
            
    def on_initialize(self, event):
        # if you have any initialization
        # including sizer setup, do it here
        # self.loadConfig()
        self.startTitle = self.title
        self.executionThread = ExecutionThread(self)
        self.executionThread.start()

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
        if not self.filename:
            return;
        self.components.filename.clear()
        self.components.filename.writeText(self.filename)
        self.on_filename_closeField()
    def on_menuFileOpen_select(self,event):
        self.on_filename_mouseDoubleClick(event)
        
    def on_filename_closeField(self, event=None):
        self.filename = self.components.filename.getLineText(0)
        try:
            isCorrectFilename(self.filename);
        except OutFileMustBeh5Extention:
            dialog.alertDialog(self,"The filename ({0}) must be specified with an '.h5' extension.".\
                format(self.filename),'Check you filename')
            return
        except OutFileMustBeAbsolutePath:
            dialog.alertDialog(self,"The filename ({0}) must be an absolute path.".\
                format(self.filename),'Check you filename')
            return
        self.title = os.path.split(self.filename)[-1] + ' - ' + self.startTitle
        self.statusBar.text = self.filename
        self._updateRunList()  
    def on_runList_mouseUp(self, event):
        self.runName = self._getBaseRunName(self.components.runList.stringSelection)
        self.components.runName.clear()
        self.components.runName.writeText(self.runName)
        self._getRunMeta(self.runName)
    #--------------------- def on_runExperimentType_loseFocus(self, event=None):
        #---------------------------------------- self._setRunMeta(self.runName)
    #---------------------------- def on_runSubject_loseFocus(self, event=None):
        #---------------------------------------- self._setRunMeta(self.runName)
    #----------------------------- def on_runObject_loseFocus(self, event=None):
        #---------------------------------------- self._setRunMeta(self.runName)
    #------------------------- def on_runSuccessful_loseFocus(self, event=None):
        #---------------------------------------- self._setRunMeta(self.runName)
    #-------------------------- def on_runCorrupted_loseFocus(self, event=None):
        #---------------------------------------- self._setRunMeta(self.runName)
    #------------------------------ def on_runNotes_loseFocus(self, event=None):
        #---------------------------------------- self._setRunMeta(self.runName)
    def on_runName_loseFocus(self, event=None):
        self.runName = self.components.runName.getLineText(0)
        if not self.runName:
            dialog.alertDialog(self,'The Run Name is not set.','Check you run name')
            return False
        self._setRunMeta(self.runName)
        if self.filename:
            theRuns = [self._getBaseRunName(runName) for runName in SofiePyTableAccess.getRunsInTheFile(self.filename)];
            if self.runName in theRuns:
                dialog.alertDialog(self,'The Run Name already exists.','Check you run name')
                return False
        return True
    
    def on_serialImu_mouseDoubleClick(self, event):
        self.serialImu = self._getPathFromDialog()
        self.components.serialImu.writeText(self.serialImu)
    def on_serialAr_mouseDoubleClick(self, event):
        self.serialAr = self._getPathFromDialog(
                wildCard = "Serial device (*video*)|*video*|All files (*.*)|*.*")
        self.components.serialAr.writeText(self.serialAr)
        
    def on_openInVitables_mouseClick(self,event):
        if self.filename:
            subprocess.Popen(["vitables", self.filename])
    
    def on_viewVideo_mouseClick(self,event):
        if not self.runName:
            dialog.alertDialog(self,'The Run Name is not set.','Check you run name')
            return
        if not self.filename:
            dialog.alertDialog(self,"The filename is not correct".\
                format(self.filename),'Check you filename')
            return
        exportBagData(self.filename,self.runName)
        
    def on_saveMetaData_mouseClick(self,event):  
         self._setRunMeta(self.runName)
    
    def on_startStopButton_mouseClick(self,event):  
        if not self.on_runName_loseFocus():
            return False
        try:
            isCorrectFilename(self.filename);
        except:
            dialog.alertDialog(self,"The filename is not correct".\
                format(self.filename),'Check you filename')
            return
        if not self._testSerialDevice(self.serialAr,' AR DEVICE'):
            return False
        if not self._testSerialDevice(self.serialImu,' IMU DEVICE'):
            return False
        if self.components.startStopButton.checked:
            #------- dialog.alertDialog(self,'Startng RUN','Check you run name')
            #------------------------------------ self._setRunMeta(self.runName)
            self.components.startStopButton.label = STARTBUTTON_STOP
            self.components.startStopButton.backgroundColor = STARTBUTTON_BACKGROUNDCOLOR_STOP
            self.running = True;
        elif self.running:
            #------ dialog.alertDialog(self,'Stopping RUN','Check you run name')
            self.running = False;
            self.components.startStopButton.label = STARTBUTTON_WAIT
            self.components.startStopButton.enabled = False;
            
    def on_verboseCheckBox_mouseClick(self,event):
        if self.components.verboseCheckBox.checked:
            setLogger(logging.DEBUG)
            logging.getLogger().setLevel(logging.DEBUG)
            print 'Verbose mode on.'
            logging.debug('Verbose on.')
        else:
            logging.getLogger().setLevel(logging.CRITICAL)
            print 'Verbose mode off.'
            logging.debug('Verbose off.')
            
    def on_menuFileNew_select(self, event):
        result = dialog.directoryDialog(self, 'Choose a directory', '')
        if result.accepted:
            self.filename = os.path.join(result.path,UNTITLEDFILENAME)
            self._setText('filename',self.filename)
            
        else:
            return '';
         
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
    
    @anythread 
    def updateGlobalExperimentFeedBackSettingUp(self):
        self._updateGlobalExperimentFeedback(EXPERIMENTSTATUS_SETTINGUP)
    @anythread 
    def updateGlobalExperimentFeedBackRunning(self):
        self._updateGlobalExperimentFeedback(EXPERIMENTSTATUS_RUNNING)
    @anythread 
    def updateGlobalExperimentFeedBackTearingDown(self):
        self._updateGlobalExperimentFeedback(EXPERIMENTSTATUS_TEARINGDOWN)
    @anythread 
    def updateGlobalExperimentFeedBackInactive(self):
        self._updateGlobalExperimentFeedback(EXPERIMENTSTATUS_INACTIVE)
    @anythread 
    def updateGlobalExperimentFeedBackErrorSettingUp(self):
        self._updateGlobalExperimentFeedback(EXPERIMENTSTATUS_ERRORSETTINGUP)
    @anythread 
    def updateGlobalExperimentFeedBackErrorTearingDown(self):
        self._updateGlobalExperimentFeedback(EXPERIMENTSTATUS_ERRORTEARINGDOWN)
    @anythread 
    def updateGlobalExperimentFeedBackErrorRunning(self):
        self._updateGlobalExperimentFeedback(EXPERIMENTSTATUS_ERRORRUNNING)
    @anythread 
    def updateStartButtonStart(self):
        self.components.startStopButton.label = STARTBUTTON_START
        self.components.startStopButton.backgroundColor = STARTBUTTON_BACKGROUNDCOLOR_START
        self.components.startStopButton.enabled = True;
        self._updateRunList()
        
    @anythread
    def setRunning(self,trueOrFalse):
        self.running =  trueOrFalse

class ExecutionThread(threading.Thread):
    """
        The Experiment Control Thread.
    """
    def __init__ (self, experimentControlBackground):
        self.experimentControlBackground = experimentControlBackground
        threading.Thread.__init__ (self)
    def run (self):
        print "ExecutionThread: starting loop"
       
        while True:
            #Waiting to run
            print 'Waiting to run.'
            while self.experimentControlBackground.running == False:
                time.sleep(0.5)
            #In A Run Cycle
            #Setting up
            print 'Settting Up'
            try:
                self.experimentControlBackground.\
                    updateGlobalExperimentFeedBackSettingUp()
                listeners = \
                startExperiment(self.experimentControlBackground.filename, 
                                self.experimentControlBackground.runName,
                        self.experimentControlBackground.serialImu,
                        self.experimentControlBackground.serialAnt,
                        self.experimentControlBackground.serialAr,
                        imuPort=self.experimentControlBackground.imuPort,
                        imuHost=self.experimentControlBackground.imuHost)
                i=ITERATIONS_SETTING_UP;
                while i>0:
                    time.sleep(1)
                    i -= 1
                    print '.'
            except Exception as ex:
                print 'ERROR SETTING UP:{0}'.format(str(ex))
                self.experimentControlBackground.\
                    updateGlobalExperimentFeedBackErrorSettingUp()
            print 'Running'
            try:
                self.experimentControlBackground.\
                    updateGlobalExperimentFeedBackRunning()
                while self.experimentControlBackground.running == True:
                    syncListeners(listeners)
                    time.sleep(0.25)
            except Exception as ex:
                print 'ERROR RUNNING:{0}'.format(str(ex))
                self.experimentControlBackground.updateGlobalExperimentFeedBackErrorRunning()
            #Tearing Down
            print 'Tear down'
            try:
                self.experimentControlBackground.\
                    updateGlobalExperimentFeedBackTearingDown()
                i=ITERATIONS_TEARING_DOWN;
                while i>0:
                    time.sleep(1)
                    i -= 1
                    print '.'
                print 'Stopped'
                shutDownExperiment(listeners)
                self.experimentControlBackground.updateStartButtonStart()
                self.experimentControlBackground.\
                    updateGlobalExperimentFeedBackInactive()
                #Clean Up
                listeners = []
            except Exception as ex:
                print 'ERROR RUNNING:{0}:\n{1}'.format(str(ex),traceback.print_exc())
                self.experimentControlBackground.\
                    updateGlobalExperimentFeedBackErrorTearingDown()
                time.sleep(2)
                self.experimentControlBackground.setRunning(False)
                self.experimentControlBackground.updateStartButtonStart()
                self.experimentControlBackground.\
                    updateGlobalExperimentFeedBackInactive()
            
if __name__ == '__main__':
    app = model.Application(ExperimentControlBackground)
    app.MainLoop()
#    while True:
#        txt = sys.stdout.readline()
#        if not txt: 
#            break
#        txt=txt.replace("\r\n","\n").replace("\r\n","\n").replace('\\\\','\\')
#        self.components.taStdout.appendText(txt)

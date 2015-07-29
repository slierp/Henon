; CLW file contains information for the MFC ClassWizard

[General Info]
Version=1
LastClass=CChildView
LastTemplate=CDialog
NewFileInclude1=#include "stdafx.h"
NewFileInclude2=#include "Henon.h"
LastPage=0

ClassCount=5
Class1=CHenonApp
Class3=CMainFrame
Class4=CAboutDlg

ResourceCount=6
Resource1=IDD_VARIABLE_DIALOG (Dutch (Netherlands))
Resource2=IDD_ABOUTBOX
Class2=CChildView
Resource3=IDR_MAINFRAME (English (U.S.))
Resource4=IDD_ABOUTBOX (English (U.S.))
Class5=CHenDialog
Resource5=IDD_VARIABLE_DIALOG
Resource6=IDR_MAINFRAME

[CLS:CHenonApp]
Type=0
HeaderFile=Henon.h
ImplementationFile=Henon.cpp
Filter=M
LastObject=CHenonApp

[CLS:CChildView]
Type=0
HeaderFile=ChildView.h
ImplementationFile=ChildView.cpp
Filter=C
LastObject=CChildView
BaseClass=CWnd 
VirtualFilter=WC

[CLS:CMainFrame]
Type=0
HeaderFile=MainFrm.h
ImplementationFile=MainFrm.cpp
Filter=C
LastObject=ID_DEMO4
BaseClass=CFrameWnd
VirtualFilter=fWC




[CLS:CAboutDlg]
Type=0
HeaderFile=Henon.cpp
ImplementationFile=Henon.cpp
Filter=D
LastObject=CAboutDlg

[DLG:IDD_ABOUTBOX]
Type=1
Class=CAboutDlg
ControlCount=4
Control1=IDOK,button,1342373889
Control2=IDC_STATIC,static,1342308352
Control3=IDC_STATIC,static,1342308352
Control4=IDC_STATIC,static,1342308352

[MNU:IDR_MAINFRAME]
Type=1
Class=CMainFrame
Command1=ID_REDRAW
Command2=ID_STOP_EVALUATION
Command3=ID_START_VDIALOG
Command4=ID_ZOOM_OUT
Command5=ID_ANIMATE
Command6=ID_SWICTHVARTOANIM
Command7=ID_APP_EXIT
Command8=ID_WHOLE_ORBIT
Command9=ID_DRAW_LINES
Command10=ID_ANIMCLEAN
Command11=ID_VIEW_TOOLBAR
Command12=ID_VIEW_STATUS_BAR
Command13=ID_README
Command14=ID_APP_ABOUT
Command15=ID_DEMO1
Command16=ID_DEMO2
Command17=ID_DEMO3
Command18=ID_DEMO4
CommandCount=18

[ACL:IDR_MAINFRAME]
Type=1
Class=CMainFrame
Command1=ID_ANIMATE
Command2=ID_ANIMCLEAN
Command3=ID_EDIT_COPY
Command4=ID_DRAW_LINES
Command5=ID_APP_EXIT
Command6=ID_README
Command7=ID_SWICTHVARTOANIM
Command8=ID_START_VDIALOG
Command9=ID_EDIT_PASTE
Command10=ID_EDIT_UNDO
Command11=ID_EDIT_CUT
Command12=ID_STOP_EVALUATION
Command13=ID_NEXT_PANE
Command14=ID_PREV_PANE
Command15=ID_EDIT_COPY
Command16=ID_EDIT_PASTE
Command17=ID_REDRAW
Command18=ID_WHOLE_ORBIT
Command19=ID_EDIT_CUT
Command20=ID_ZOOM_OUT
Command21=ID_EDIT_UNDO
CommandCount=21

[TB:IDR_MAINFRAME (English (U.S.))]
Type=1
Class=?
Command1=ID_APP_EXIT
Command2=ID_START_VDIALOG
Command3=ID_STOP_EVALUATION
Command4=ID_ZOOM_OUT
Command5=ID_APP_ABOUT
CommandCount=5

[MNU:IDR_MAINFRAME (English (U.S.))]
Type=1
Class=CMainFrame
Command1=ID_START_VDIALOG
Command2=ID_ZOOM_OUT
Command3=ID_STOP_EVALUATION
Command4=ID_APP_EXIT
Command5=ID_VIEW_TOOLBAR
Command6=ID_VIEW_STATUS_BAR
Command7=ID_APP_ABOUT
CommandCount=7

[ACL:IDR_MAINFRAME (English (U.S.))]
Type=1
Class=CMainFrame
Command1=ID_EDIT_COPY
Command2=ID_APP_EXIT
Command3=ID_START_VDIALOG
Command4=ID_EDIT_PASTE
Command5=ID_EDIT_UNDO
Command6=ID_EDIT_CUT
Command7=ID_STOP_EVALUATION
Command8=ID_NEXT_PANE
Command9=ID_PREV_PANE
Command10=ID_EDIT_COPY
Command11=ID_EDIT_PASTE
Command12=ID_EDIT_CUT
Command13=ID_ZOOM_OUT
Command14=ID_EDIT_UNDO
CommandCount=14

[DLG:IDD_ABOUTBOX (English (U.S.))]
Type=1
Class=CAboutDlg
ControlCount=3
Control1=IDOK,button,1342373889
Control2=IDC_STATIC,static,1342308352
Control3=IDC_STATIC,static,1342308352

[DLG:IDD_VARIABLE_DIALOG]
Type=1
Class=CHenDialog
ControlCount=8
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1342242816
Control3=IDC_HENA,edit,1350631552
Control4=IDC_STATIC,static,1342308352
Control5=IDC_STATIC,static,1342308352
Control6=IDC_STATIC,static,1342308352
Control7=IDC_HENB,edit,1350631552
Control8=IDC_HENN,edit,1350631552

[CLS:CHenDialog]
Type=0
HeaderFile=HenDialog.h
ImplementationFile=HenDialog.cpp
BaseClass=CDialog
Filter=D
VirtualFilter=dWC
LastObject=IDC_neglectN

[TB:IDR_MAINFRAME]
Type=1
Class=?
Command1=ID_APP_EXIT
Command2=ID_START_VDIALOG
Command3=ID_STOP_EVALUATION
Command4=ID_ZOOM_OUT
Command5=ID_README
CommandCount=5

[DLG:IDD_VARIABLE_DIALOG (Dutch (Netherlands))]
Type=1
Class=CHenDialog
ControlCount=26
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1342242816
Control3=IDC_HENA,edit,1350631552
Control4=IDC_STATIC,static,1342308352
Control5=IDC_STATIC,static,1342308352
Control6=IDC_STATIC,static,1342308352
Control7=IDC_HENB,edit,1350631552
Control8=IDC_HENN,edit,1350631552
Control9=IDC_STATIC,static,1342308352
Control10=IDC_INCREMENT,edit,1350631552
Control11=IDC_STATIC,static,1342308352
Control12=IDC_RANGE,edit,1350631552
Control13=IDC_STATIC,static,1342308352
Control14=IDC_XLeft,edit,1350631552
Control15=IDC_STATIC,static,1342308352
Control16=IDC_XRight,edit,1350631552
Control17=IDC_STATIC,static,1342308352
Control18=IDC_YTop,edit,1350631552
Control19=IDC_STATIC,static,1342308352
Control20=IDC_YBottom,edit,1350631552
Control21=IDC_STATIC,button,1342177287
Control22=IDC_STATIC,button,1342177287
Control23=IDC_STATIC,static,1342308352
Control24=IDC_Nlimit,edit,1350631552
Control25=IDC_STATIC,static,1342308352
Control26=IDC_neglectN,edit,1350631552


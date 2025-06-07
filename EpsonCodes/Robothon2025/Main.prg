Global Integer Xmax, Xmin, Ymax, Ymin, Zmin, xpos, ypos, gap, radius, x, y, z, u, x1, x2, y1, y2
Global String p$, px1$, px2$, py1$, py2$

Function main
	String indata$(0), receive$
  	Integer i, camX, camY, camZ

	Motor On
	Power High
	Speed 10
	SpeedR 10
	Accel 10, 10
	AccelR 10, 10
	SpeedS 10
	AccelS 10, 10
	AutoLJM On
	
	
' going to camera position
  Go CameraPoint
  On 10
  
  SetNet #201, "192.168.1.2", 2001, CRLF
  ' SetNet #201, "127.0.0.1", 2001, CRLF
  OpenNet #201 As Server
  Print "Robot ready, listening to network"
  WaitNet #201
  OnErr GoTo ehandle

  Do
   Input #201, receive$
   ParseStr receive$, indata$(), " "
   Print "Received message: ", receive$
   'Print "indata(0): ", indata$(0)
   'Print "indata(1): ", indata$(1)
   'Print "indata(2): ", indata$(2)
   
   
  
   ' if the command is jump3
   If indata$(0) = "jump3" Then
     	x = Val(Trim$(indata$(1)))
    	y = Val(Trim$(indata$(2)))
	    z = Val(indata$(3))
	    u = Val(indata$(4))
    
   		Print "Jumping to x=", x, " y=", y, " z=", z
	   	Jump3 Here +Z(50), Here :X(0) :Y(y) :Z(z + 50), Here :X(x) :Y(y) :Z(z) :U(u)
   EndIf
   
   If LCase$(indata$(0)) = "go" Then
     	x = Val(Trim$(indata$(1)))
    	y = Val(Trim$(indata$(2)))
	    z = Val(indata$(3))
    
   		Print "Going to x=", x, " y=", y, " z=", z
	   	Go Here :X(x) :Y(y) :Z(z)
	   	sayOK
   EndIf
   
   If LCase$(indata$(0)) = "m" Then
     	p$ = Trim$(indata$(1))
    
   		Print "Going to ", p$
	   	Move P(PNumber(p$))
   EndIf
   
   If LCase$(indata$(0)) = "p" Then
   		P333 = Here
   		Print "Current location is ", P333
	   	Print #201, P333
   EndIf
  	
   If LCase$(indata$(0)) = "local" Then ' map to local coordinate
   ' Python has to issue command to EPSON in this format: local blueX,blueY,redX,redY
   		Real px1, py1, px2, py2
     	px1 = Val(Trim$(indata$(1)))
        py1 = Val(Trim$(indata$(2)))
        px2 = Val(Trim$(indata$(3)))
        py2 = Val(Trim$(indata$(4)))
        
   		Print "Mapping world coordinate to local"
   		Print "Blue button:", px1, ",", py1, "  Red button:", px2, ",", py2
		Real ZOffset
		ZOffset = 500
		P332 = Here :X(px1) :Y(py1) :Z(ZOffset) ' blue	
		P333 = Here :X(px2) :Y(py2) :Z(ZOffset) ' red
		SavePoints "robot1.pts"
		Print Local(1)
		Local 1,(calBlue:P332),(calRed:P333) ' map those points to Local BB and RB at z=521
		
		Print Local(1)
		Power High
		Speed 20
		SpeedR 20
		Accel 20, 20
		AccelR 20, 20
		SpeedS 20
		AccelS 20, 20
		sayOK
   EndIf
   
 
	' --------- tasks -------
   	
    If indata$(0) = "go_pressRedBlueRed" Then
      Print "run go_pressRedBlueRed"
      go_pressRedBlueRed
    EndIf

   	If indata$(0) = "go_pressRedOnly" Then
	   	Print 'run pressRedOnly'
   		go_pressRedOnly
   	EndIf
   	
	If indata$(0) = "go_pressBlueOnly" Then
	   	Print 'run pressBlueOnly'
   		go_pressBlueOnly
   	EndIf
   	
	If indata$(0) = "go_penPick" Then
	   	Print 'run pen pick'
   		go_penPick
   	EndIf
   	
	If indata$(0) = "go_screenCamera" Then
   		Print 'run screenCamera'
   		go_screenCamera
   	EndIf
   	
	If indata$(0) = "go_drawCircle" Then
   		Print 'run drawCircle'
   		go_drawCircle
   	EndIf
   	
    If indata$(0) = "go_drawTriangle" Then
   		Print 'run drawTriangle'
   		go_drawTriangle
   	EndIf
   	
   	If indata$(0) = "go_drawSquare" Then
   		Print 'run drawSquare'
   		go_drawSquare
   	EndIf

   	If indata$(0) = "go_tapA" Then
   		Print 'run tapA'
   		go_tapA
   	EndIf
 
 	If indata$(0) = "go_tapB" Then
   		Print 'run tapB'
   		go_tapB
   	EndIf
   	
   	If indata$(0) = "go_tapBackground" Then
   		Print 'run tapBackground'
   		go_tapBackground
   	EndIf
   	
   	If indata$(0) = "go_doubletapA" Then
   		Print 'run doubletapA'
   		go_doubletapA
   	EndIf
   	
   	If indata$(0) = "go_doubletapB" Then
   		Print 'run doubletapB'
   		go_doubletapB
   	EndIf
   	
   	If indata$(0) = "go_doubletapBackground" Then
   		Print 'run doubletapBackground'
   		go_doubletapBackground
   	EndIf
   	
   	If indata$(0) = "go_swipeAB" Then
   		Print 'run swipeAB'
   		go_swipeAB
   	EndIf
   	
   	If indata$(0) = "go_swipeBA" Then
   		Print 'run swipeBA'
   		go_swipeBA
   	EndIf
   	
   	If indata$(0) = "go_swipeABackground" Then
   		Print 'run swipeABackground'
   		go_swipeABackground
   	EndIf
   	
   	If indata$(0) = "go_swipeBBackground" Then
   		Print 'run swipeBBackground'
   		go_swipeBBackground
   	EndIf
   	
   	If indata$(0) = "go_swipeBackgroundA" Then
   		Print 'run swipeBackgroundA'
   		go_swipeBackgroundA
   	EndIf
   	
   	If indata$(0) = "go_swipeBackgroundB" Then
   		Print 'run swipeBackgroundB'
   		go_swipeBackgroundB
   	EndIf
   	
   	If indata$(0) = "go_ballMaze1" Then
   		Print 'run ballMaze1'
   		go_ballMaze1
   	EndIf
   	
   	If indata$(0) = "go_ballMaze2" Then
   		Print 'run ballMaze2'
   		go_ballMaze2
   	EndIf
   	
   	If indata$(0) = "go_penPlace" Then
   		Print 'run pen place'
   		go_penPlace
   	EndIf
   	
  Loop

  Exit Function

  ehandle:
	Call ErrFunc
    EResume Next
Fend
Function ErrFunc

  Print ErrMsg$(Err(0))
  Select Err(0)
   Case 2902
     OpenNet #201 As Server
     WaitNet #201

   Case 2910
     OpenNet #201 As Server

     WaitNet #201

   Default
     Error Err(0)

  Send
Fend
Function go_pressRedBlueRed
	Go CameraPoint LJM
	Go RedPress +Z(100) LJM
	Go RedPress +Z(30) LJM
	Go redpress LJM
	Go RedPress +Z(30) LJM
	'Go MidPointRedBlue LJM
	Go BluePress +Z(30) LJM
	Go BluePress LJM
	Go BluePress +Z(30) LJM
	Go RedPress +Z(30) LJM
	Go redpress LJM
	Go RedPress +Z(30) LJM
	Go camRedBlueButtons LJM
	sayOK
Fend
Function go_pressRedOnly
	Go RedPress +Z(30) LJM
	Go redpress LJM
	Go RedPress +Z(300) LJM
	sayOK
Fend
Function go_pressBlueOnly
	Go BluePress +Z(30) LJM
	Go Bluepress LJM
	Go BluePress +Z(300) LJM
	sayOK
Fend
Function go_penPick
	Power High
	Speed 10
	SpeedR 10
	Accel 10, 10
	AccelR 10, 10
	SpeedS 10
	AccelS 10, 10
	Go FlippingPoint LJM
	Go penApproach LJM
	Off 10
	Go penPick LJM
	On 10
	Wait 1
	Go penPickRetract LJM
	Speed 15
	SpeedR 15
	Accel 10, 10
	AccelR 10, 10
	SpeedS 15
	AccelS 10, 10
	sayOK
Fend
Function go_ballMaze1
	Speed 7
	SpeedR 7
	Accel 8, 8
	AccelR 8, 8
	SpeedS 7
	AccelS 8, 8
	Go penFlippedReadyforBall LJM
	Go BallSensor1 +Z(20) LJM
	Go BallSensor1 LJM
	Go BallWpt1 LJM
	Go ballwpt2 LJM
	Go BallSensor2 LJM
	'Go ballHole LJM
	Wait 1
	'Go ballHole +Z(50) LJM
	'' --- now go back to base (ballSensor1)
	Go BallWpt2 LJM
	Go ballwpt1 LJM
	Go BallSensor1 LJM
	'' -- now retract and press blue button
	Go ballPenRetractPoint LJM
	Go penBluePressApproach LJM
	Go penBluePress LJM
	Wait 4
	Go penBluePressApproach LJM
	sayOK
Fend
Function go_ballMaze2 'must be executed right after go_ballMaze1
	Go BallSensor1 LJM
	Go BallWpt1 LJM
	Go ballwpt2 LJM
	Go BallSensor2 LJM
	Wait 1
	Go BallWpt3 LJM
	Go BallWpt4 LJM
	Go BallWpt5 LJM
	Go BallWpt6 LJM
	Go BallWpt7 LJM
	Go BallWpt8 LJM
	Go BallSensor3a LJM
	Go BallSensor3b LJM
	Go BallWpt9 LJM
	Go BallWpt10 LJM
	Go BallWpt11 LJM
	Go ballsensor1 LJM
	Go ballPenRetractPoint LJM
	Go ballPenRetractPoint +Z(200) LJM
	Speed 10
	SpeedR 10
	Accel 10, 10
	AccelR 10, 10
	SpeedS 10
	sayOK
Fend
Function go_ballMazeAll
	go_penPick
	go_ballMaze1
	go_ballMaze2
Fend
Function go_penPlace
	Speed 15
	SpeedR 15
	Accel 10, 10
	AccelR 10, 10
	SpeedS 15
	AccelS 10, 10
	Go penDropApproach +Z(20) LJM
	Go penDropApproach LJM
	Go penDrop LJM
	Off 10
	Go penDropApproach +Z(20) LJM
	On 10
	Go CameraPoint LJM
	sayOK
Fend
Function go_screenCamera
	Go screenCameraPoint :Z(700) LJM
	Go screenCameraPoint LJM
	sayOK
	
Fend
Function go_tapA
	'Go screenA +Z(10) LJM
	Go screenA +Z(3) LJM
	Wait 1
	'Go screenA +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
	
Fend
Function go_tapB
	'Go screenB +Z(10) LJM
	Go screenB +Z(3) LJM
	Wait 1
	'Go screenB +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
Fend
Function go_tapBackground
	'Go screenABmid +Z(10) LJM
	Go screenABmid +Z(3) LJM
	Wait 1
	'Go screenABmid +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
Fend
Function go_doubletapA
	'Go screenA +Z(10) LJM
	Go screenA +Z(3) LJM
	Go screenA +Z(5) LJM
	Go screenA +Z(3) LJM
	'Go screenA +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
Fend
Function go_doubletapB
	'Go screenB +Z(10) LJM
	Go screenB +Z(3) LJM
	Go screenB +Z(4) LJM
	Go screenB +Z(3) LJM
	'Go screenB +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
	
Fend
Function go_doubletapBackground
	'Go screenABmid +Z(10) LJM
	Go screenABmid LJM
	Go screenABmid +Z(4) LJM
	Go screenABmid LJM
	'Go screenABmid +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
	
Fend
Function go_swipeAB
	'Go screenA +Z(10) LJM
	Go screenA +Z(3) LJM
	Go screenB +Z(3) LJM
	'Go screenB +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
Fend
Function go_swipeBA
	'Go screenB +Z(10) LJM
	Go screenB +Z(2.5) LJM
	Go screenA +Z(2.5) LJM
	'Go screenA +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
Fend
Function go_swipeBackgroundA
	'Go screenABmid +Z(10) LJM
	Go screenABmid +Z(2.5) LJM
	Go screenA +Z(2.5) LJM
	Go screenA +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
Fend
Function go_swipeBackgroundB
	'Go screenABmid +Z(10) LJM
	Go screenABmid +Z(2.5) LJM
	Go screenB +Z(2.5) LJM
	'Go screenB +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
Fend
Function go_swipeABackground
	'Go screenA +Z(10) LJM
	Go screenA +Z(2.5) LJM
	Go screenABmid LJM
	Go screenABmid +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
Fend
Function go_swipeBBackground
	'Go screenB +Z(10) LJM
	Go screenB +Z(3) LJM
	Go screenABmid LJM
	'Go screenABmid +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
Fend
Function go_drawCircle
	'Go screenABmid -Y(5) +Z(10) LJM
	Go screenABmid -Y(5) +Z(3) LJM
	Arc3 Here -X(5) +Y(5), Here +X(0) +Y(10)
	Arc3 Here +X(5) -Y(5), Here +X(0) -Y(10)
	'Go Here +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
Fend
Function go_drawTriangle
	'Go screenABmid +Z(10) LJM
	Go screenABmid +Z(3) LJM
	Go Here +Y(10) -X(10)
	Go Here +X(20)
	Go Here -X(10) -Y(10)
	'Go Here +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
Fend
Function go_drawSquare
	'Go screenA +Z(10) LJM
	Go screenA +Z(3) LJM
	Go Here +Y(10)
	Go Here +X(20)
	Go Here -Y(10)
	Go Here -X(20)
	'Go Here +Z(10) LJM
	Go screenCameraPoint LJM
	sayOK
Fend
Function sayOK
	Print "OK, task done!"
	Print #201, "OK"
Fend
Function testSequence
	Go CameraPoint LJM
	go_pressRedBlueRed
	go_pressRedOnly
	go_penPick
	go_screenCamera
	go_drawCircle
	go_drawTriangle
	go_drawSquare
	go_tapA
	go_swipeAB
	go_tapB
	go_ballMaze1
	go_ballMaze2
	go_penPlace
Fend
Function penUp
	Move Here +Z(10)
Fend
Function penDown
	Move Here -Z(10)
Fend

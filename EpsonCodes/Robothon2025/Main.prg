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

  SetNet #201, "192.168.1.2", 2001, CRLF
  ' SetNet #201, "127.0.0.1", 2001, CRLF
  OpenNet #201 As Server
  Print "Robot ready, listening to network"
  WaitNet #201
  OnErr GoTo ehandle

  Do
   Input #201, receive$
   ParseStr receive$, indata$(), " " ' convert to lower case
   Print "Received message: ", receive$
   
  
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
   		Real px1, py1, px2, py2
     	px1 = Val(Trim$(indata$(1)))
        py1 = Val(Trim$(indata$(2)))
        px2 = Val(Trim$(indata$(3)))
        py2 = Val(Trim$(indata$(4)))
        
   		Print "Mapping world coordinate to local"
   		Print "Blue button:", px1, ",", py1, "  Knob:", px2, ",", px2
		Real ZOffset
		ZOffset = 522
		P332 = Here :X(px1) :Y(py1) :Z(ZOffset) ' blue	
		P333 = Here :X(px2) :Y(py2) :Z(ZOffset) ' knob
		Local 3,(LBB:P332),(LK:P333) ' map those points to Local BB and Local Knob at z=521
		Power High
		Speed 20
		SpeedR 20
		Accel 20, 20
		AccelR 20, 20
		SpeedS 20
		AccelS 20, 20
   EndIf
   
 
'	' --------- tasks -------
'	If LCase$(indata$(0)) = "go_click_m5" Then
'   		go_click_m5
'   	EndIf
'   	
'	If LCase$(indata$(0)) = "go_press_blue_button" Then
'		Speed 50
'   		go_press_blue_button
'   	EndIf

   	
'	If LCase$(indata$(0)) = "go_approach_slider" Then
'		Speed 15
'		Real starting_pos
'		starting_pos = Val(Trim$(indata$(1)))
'   		go_approach_slider(starting_pos)
'   	EndIf
'   	
'	If LCase$(indata$(0)) = "go_check_display" Then
'		Speed 50
'   		go_check_display
'   	EndIf
'   	
'	If LCase$(indata$(0)) = "go_slide" Then
'		Speed 20
'		Real mm
'		mm = Val(Trim$(indata$(1)))
'   		go_slide(mm)
'   	EndIf
'   	
' 	If LCase$(indata$(0)) = "go_tool_up" Then
'   		go_tool_up
'   	EndIf
'
'   	If LCase$(indata$(0)) = "go_approach_plug1" Then
'   		go_approach_plug1
'   	EndIf
'   	
'   	If LCase$(indata$(0)) = "go_approach_plug2" Then
'   		go_approach_plug2
'   	EndIf
'   	
'   	If LCase$(indata$(0)) = "go_approach_plug3" Then
'   		go_approach_plug3
'   	EndIf
'   	
'	If LCase$(indata$(0)) = "go_open_door" Then
'   		go_open_door
'   	EndIf
'   	
'	If LCase$(indata$(0)) = "go_probe1" Then
'   		go_probe1
'   	EndIf
'   	
'	If LCase$(indata$(0)) = "go_probe2" Then
'   		go_probe2
'   	EndIf
'   	
'	If LCase$(indata$(0)) = "go_probedrop" Then
'   		go_probedrop
'   	EndIf
'   	   	
'   	If LCase$(indata$(0)) = "go_approach_cable" Then
'   		go_approach_cable
'   	EndIf
'
'   	If LCase$(indata$(0)) = "go_wind_cable" Then
'   		go_wind_cable
'   	EndIf
'
'	If LCase$(indata$(0)) = "go_catch_probe" Then
'   		go_catch_probe
'   	EndIf
'   	
'	If LCase$(indata$(0)) = "go_stow" Then
'   		go_stow
'   	EndIf
'
'	If LCase$(indata$(0)) = "go_stow_finished" Then
'   		go_stow_finished
'   	EndIf
'   	
'	If LCase$(indata$(0)) = "go_press_red_button" Then
'   		go_press_red_button
'   	EndIf
	' --------- end tasks -------
   
    ' ---- demo ---
' 	If LCase$(indata$(0)) = "approaching_meter" Then
'   		approaching_meter
'   	EndIf
' 	If LCase$(indata$(0)) = "turn_meter" Then
'   		turn_meter
'   	EndIf
' 	If LCase$(indata$(0)) = "approaching_probe" Then
'   		approaching_probe
'   	EndIf
' 	If LCase$(indata$(0)) = "probing" Then
'   		probing
'   	EndIf
' 	If LCase$(indata$(0)) = "probe_done" Then
'   		probe_done
'   	EndIf
   	
   
	P777 = Here
	Print #201, P777
	
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

Function drawCircle
	Arc3 Here -X(radius), Here -X(radius) +Y(radius) CP
	Arc3 Here +X(radius), Here +X(radius) -Y(radius) CP
Fend


Function dots
	Integer i, j
	Move Here :X(-100) :Y(500) :Z(600)
	For i = 0 To 6
		Go Here :X(-150 + (i * 50)) LJM
		For j = 1 To 5
			Go Here :Y(500 + (j * 50)) LJM
			Move Here :Z(399.3)
			penUp
			'circle
			MsgBox "Next stop", MB_OK
		Next
	Next
Fend
Function circle
	penUp
	Move Here -X(10)
	penDown
	Arc3 Here +X(10) +Y(10), Here +X(20) +Y(0) CP
	Arc3 Here +X(-10) +Y(-10), Here +X(-20) +Y(0)
	Move Here +X(20)
	penUp
	Move Here -X(10) -Y(10)
	penDown
	Move Here +Y(20)
	penUp
	Move Here -Y(10)
Fend
Function penUp
	Move Here +Z(10)
Fend
Function penDown
	Move Here -Z(10)
Fend

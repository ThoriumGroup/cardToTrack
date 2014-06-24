
def corn3D():
    import nuke
    u = nuke.selectedNodes()
    x = 0
    for u in u:
        x=x+1
    if x == 3:               
        frame = nuke.frame()
        panel = nuke.Panel("Card to track")
        first = nuke.Root().knob('first_frame').getValue()
        first = int(first)
        first = str(first)
        last = nuke.Root().knob('last_frame').getValue()
        last = int(last)
        last = str(last)
        basicRange = first+"-"+last
        panel.addSingleLineInput("Range:", basicRange)
        panel.addEnumerationPulldown("Output:", "Tracker CornerPin Both ")
        panel.addSingleLineInput("Ref frame:", frame)
        panel.show()
    
        basicRange = panel.value("Range:")
        refFrame = panel.value("Ref frame:")
        Output = panel.value("Output:")
    
    
        refFrame = float(refFrame)
        rangeA = basicRange.split("-")[0]
        rangeA=int(rangeA)
        rangeB = basicRange.split("-")[1]
        rangeB=int(rangeB)
        rangeA=int(rangeA)
        rangeB=int(rangeB)    
        n = nuke.selectedNodes("Card2")
        for n in n:
            x = n['xpos'].value()
            y = n['ypos'].value()
    
            trans = n['translate'].value()
            rot = n['rotate'].value()
            scalex = n['scaling'].value(0)
            scaley = n['scaling'].value(1)
            labelC = n['label'].value()
            mainA = nuke.nodes.Axis()
            mainA['translate'].setValue(trans)
            mainA['rotate'].setValue(rot)
            mainA['name'].setValue("mainA")
            mainA['xpos'].setValue(x)
            mainA['ypos'].setValue(y)
            
            LU = nuke.nodes.Axis()
            LU['translate'].setValue([-0.5,0.5,0])
            LU.setInput(0,mainA)
            LU['name'].setValue('LU')
            LU['xpos'].setValue(x)
            LU['ypos'].setValue(y)        
            
            RU = nuke.nodes.Axis()
            RU['translate'].setValue([0.5,0.5,0])
            RU.setInput(0,mainA)
            RU['name'].setValue('RU')
            RU['xpos'].setValue(x)
            RU['ypos'].setValue(y)
            
            LL = nuke.nodes.Axis()
            LL['translate'].setValue([-0.5,-0.5,0])
            LL.setInput(0,mainA)
            LL['name'].setValue('LL')
            LL['xpos'].setValue(x)
            LL['ypos'].setValue(y)
            
            
            RL= nuke.nodes.Axis()
            RL['translate'].setValue([0.5,-0.5,0])
            RL.setInput(0,mainA)
            RL['name'].setValue('RL')
            RL['xpos'].setValue(x)
            RL['ypos'].setValue(y)
        
        n = nuke.selectedNodes()
        for n in n:
            if n.Class() != "Card2" and n.Class() != "Camera2":
                BG=n
            if n.Class() != "Card" and n.Class() != "Camera":
                BG=n
            if n.Class() == "Camera2":
                Cam=n
            if n.Class() == "Camera":
                Cam=n
        
        LUP = nuke.nodes.Reconcile3D()
        LUP.setInput(2,LU)
        LUP.setInput(1,Cam)
        LUP.setInput(0,BG)
        LUP['name'].setValue("P4")
        LUP['xpos'].setValue(x)
        LUP['ypos'].setValue(y)
        
        RUP = nuke.nodes.Reconcile3D()
        RUP.setInput(2,RU)
        RUP.setInput(1,Cam)
        RUP.setInput(0,BG)
        RUP['name'].setValue("P3")
        RUP['xpos'].setValue(x)
        RUP['ypos'].setValue(y)
        
        LLP = nuke.nodes.Reconcile3D()
        LLP.setInput(2,LL)
        LLP.setInput(1,Cam)
        LLP.setInput(0,BG)
        LLP['name'].setValue("P1")
        LLP['xpos'].setValue(x)
        LLP['ypos'].setValue(y)    
        
        RLP = nuke.nodes.Reconcile3D()
        RLP.setInput(2,RL)
        RLP.setInput(1,Cam)
        RLP.setInput(0,BG)
        RLP['name'].setValue("P2")
        RLP['xpos'].setValue(x)
        RLP['ypos'].setValue(y)
    
    
        n = nuke.nodes.Tracker3()
        n['xpos'].setValue(x)
        n['ypos'].setValue(y)
        n['enable1'].setValue(1)
        n['enable2'].setValue(1)
        n['enable3'].setValue(1)
        n['enable4'].setValue(1)
        
        P1 = nuke.toNode("P1")
        nuke.execute(P1,rangeA,rangeB)
        P1p = P1['output'].value()
        
        P2 = nuke.toNode("P2")
        nuke.execute(P2,rangeA,rangeB)
        P2p = P2['output'].value()
        
        P3 = nuke.toNode("P3")
        nuke.execute(P3,rangeA,rangeB)
        P3p = P3['output'].value()
        
        P4 = nuke.toNode("P4")
        nuke.execute(P4,rangeA,rangeB)
        P4p = P4['output'].value()
        
        n['track1'].copyAnimations(P1['output'].animations())
        n['track2'].copyAnimations(P2['output'].animations())
        n['track3'].copyAnimations(P3['output'].animations())
        n['track4'].copyAnimations(P4['output'].animations())
        n['use_for1'].setValue(7)
        n['use_for2'].setValue(7)
        n['use_for3'].setValue(7)
        n['use_for4'].setValue(7)
    
        n['xpos'].setValue(x+100)
        n['ypos'].setValue(y)
        n['label'].setValue(labelC)
    
        # corner pin 
        corner = nuke.nodes.CornerPin2D()  
        corner['to1'].copyAnimations(P1['output'].animations())
        corner['to2'].copyAnimations(P2['output'].animations())
        corner['to3'].copyAnimations(P3['output'].animations())
        corner['to4'].copyAnimations(P4['output'].animations())
        P1val = P1['output'].getValueAt(refFrame)
        P2val = P2['output'].getValueAt(refFrame)
        P3val = P3['output'].getValueAt(refFrame)
        P4val = P4['output'].getValueAt(refFrame)
        corner['from1'].setValue(P1val)
        corner['from2'].setValue(P2val)
        corner['from3'].setValue(P3val)
        corner['from4'].setValue(P4val)
        corner['xpos'].setValue(x+200)
        corner['ypos'].setValue(y)
        refFrame = int(refFrame)
        refFrame = str(refFrame)
        corner["label"].setValue("ref frame: " + refFrame)
    
       
        # cleanup    
        mainA = nuke.toNode("mainA")
        LU = nuke.toNode("LU")
        RU = nuke.toNode("RU")
        LL = nuke.toNode("LL")
        RL = nuke.toNode("RL")
    
        
     
        nuke.delete(mainA)
        nuke.delete(LU)
        nuke.delete(RU)
        nuke.delete(LL)
        nuke.delete(RL)
        nuke.delete(P1)
        nuke.delete(P2)
        nuke.delete(P3)
        nuke.delete(P4)
        if Output == "Tracker":
            nuke.delete(corner)
        if Output == "CornerPin":
            nuke.delete(n)

    else:
        nuke.message("upps... I think you forgot to select Camera+BG+Card")        






















def corn3D():
    import nuke
    u = nuke.selectedNodes()
    x = 0
    for u in u:
        x=x+1
    if x == 3:               
        frame = nuke.frame()
        panel = nuke.Panel("Card to track")
        first = nuke.Root().knob('first_frame').getValue()
        first = int(first)
        first = str(first)
        last = nuke.Root().knob('last_frame').getValue()
        last = int(last)
        last = str(last)
        basicRange = first+"-"+last
        panel.addSingleLineInput("Range:", basicRange)
        panel.addEnumerationPulldown("Output:", "Tracker CornerPin Both ")
        panel.addSingleLineInput("Ref frame:", frame)
        panel.addBooleanCheckBox('Translate Only', False)
        panel.show()
    
        basicRange = panel.value("Range:")
        refFrame = panel.value("Ref frame:")
        Output = panel.value("Output:")
        Axis = panel.value("Translate Only")
    
    
        refFrame = float(refFrame)
        rangeA = basicRange.split("-")[0]
        rangeA=int(rangeA)
        rangeB = basicRange.split("-")[1]
        rangeB=int(rangeB)
        rangeA=int(rangeA)
        rangeB=int(rangeB)

        if Axis == False:
            n = nuke.selectedNodes("Card2")
            for n in n:
                x = n['xpos'].value()
                y = n['ypos'].value()
        
                trans = n['translate'].value()
                rot = n['rotate'].value()
                scalex = n['scaling'].value(0)
                scaley = n['scaling'].value(1)
                labelC = n['label'].value()
                mainA = nuke.nodes.Axis()
                mainA['translate'].setValue(trans)
                mainA['rotate'].setValue(rot)
                mainA['name'].setValue("mainA")
                mainA['xpos'].setValue(x)
                mainA['ypos'].setValue(y)
                
                LU = nuke.nodes.Axis()
                LU['translate'].setValue([-0.5,0.5,0])
                LU.setInput(0,mainA)
                LU['name'].setValue('LU')
                LU['xpos'].setValue(x)
                LU['ypos'].setValue(y)        
                
                RU = nuke.nodes.Axis()
                RU['translate'].setValue([0.5,0.5,0])
                RU.setInput(0,mainA)
                RU['name'].setValue('RU')
                RU['xpos'].setValue(x)
                RU['ypos'].setValue(y)
                
                LL = nuke.nodes.Axis()
                LL['translate'].setValue([-0.5,-0.5,0])
                LL.setInput(0,mainA)
                LL['name'].setValue('LL')
                LL['xpos'].setValue(x)
                LL['ypos'].setValue(y)
                
                
                RL= nuke.nodes.Axis()
                RL['translate'].setValue([0.5,-0.5,0])
                RL.setInput(0,mainA)
                RL['name'].setValue('RL')
                RL['xpos'].setValue(x)
                RL['ypos'].setValue(y)
            
            n = nuke.selectedNodes()
            for n in n:
                if 'fstop' in n.knobs():
                    Cam = n
                elif 'orientation' in n.knobs():
                    print "."
                else:
                    BG = n 
            
            LUP = nuke.nodes.Reconcile3D()
            LUP.setInput(2,LU)
            LUP.setInput(1,Cam)
            LUP.setInput(0,BG)
            LUP['name'].setValue("P4")
            LUP['xpos'].setValue(x)
            LUP['ypos'].setValue(y)
            
            RUP = nuke.nodes.Reconcile3D()
            RUP.setInput(2,RU)
            RUP.setInput(1,Cam)
            RUP.setInput(0,BG)
            RUP['name'].setValue("P3")
            RUP['xpos'].setValue(x)
            RUP['ypos'].setValue(y)
            
            LLP = nuke.nodes.Reconcile3D()
            LLP.setInput(2,LL)
            LLP.setInput(1,Cam)
            LLP.setInput(0,BG)
            LLP['name'].setValue("P1")
            LLP['xpos'].setValue(x)
            LLP['ypos'].setValue(y)    
            
            RLP = nuke.nodes.Reconcile3D()
            RLP.setInput(2,RL)
            RLP.setInput(1,Cam)
            RLP.setInput(0,BG)
            RLP['name'].setValue("P2")
            RLP['xpos'].setValue(x)
            RLP['ypos'].setValue(y)
        
        
            n = nuke.nodes.Tracker3()
            n['enable1'].setValue(1)
            n['enable2'].setValue(1)
            n['enable3'].setValue(1)
            n['enable4'].setValue(1)
            
            P1 = nuke.toNode("P1")
            nuke.execute(P1,rangeA,rangeB)
            P1p = P1['output'].value()
            
            P2 = nuke.toNode("P2")
            nuke.execute(P2,rangeA,rangeB)
            P2p = P2['output'].value()
            
            P3 = nuke.toNode("P3")
            nuke.execute(P3,rangeA,rangeB)
            P3p = P3['output'].value()
            
            P4 = nuke.toNode("P4")
            nuke.execute(P4,rangeA,rangeB)
            P4p = P4['output'].value()
            
            n['track1'].copyAnimations(P1['output'].animations())
            n['track2'].copyAnimations(P2['output'].animations())
            n['track3'].copyAnimations(P3['output'].animations())
            n['track4'].copyAnimations(P4['output'].animations())
            n['use_for1'].setValue(7)
            n['use_for2'].setValue(7)
            n['use_for3'].setValue(7)
            n['use_for4'].setValue(7)
        
            n['xpos'].setValue(x+100)
            n['ypos'].setValue(y)
            n['label'].setValue(labelC)
        
            # corner pin 
            corner = nuke.nodes.CornerPin2D()  
            corner['to1'].copyAnimations(P1['output'].animations())
            corner['to2'].copyAnimations(P2['output'].animations())
            corner['to3'].copyAnimations(P3['output'].animations())
            corner['to4'].copyAnimations(P4['output'].animations())
            P1val = P1['output'].getValueAt(refFrame)
            P2val = P2['output'].getValueAt(refFrame)
            P3val = P3['output'].getValueAt(refFrame)
            P4val = P4['output'].getValueAt(refFrame)
            corner['from1'].setValue(P1val)
            corner['from2'].setValue(P2val)
            corner['from3'].setValue(P3val)
            corner['from4'].setValue(P4val)
            corner['xpos'].setValue(x+200)
            corner['ypos'].setValue(y)
            refFrame = int(refFrame)
            refFrame = str(refFrame)
            corner["label"].setValue("ref frame: " + refFrame)
        
           
            # cleanup    
            mainA = nuke.toNode("mainA")
            LU = nuke.toNode("LU")
            RU = nuke.toNode("RU")
            LL = nuke.toNode("LL")
            RL = nuke.toNode("RL")
        
            
         
            nuke.delete(mainA)
            nuke.delete(LU)
            nuke.delete(RU)
            nuke.delete(LL)
            nuke.delete(RL)
            nuke.delete(P1)
            nuke.delete(P2)
            nuke.delete(P3)
            nuke.delete(P4)
            if Output == "Tracker":
                nuke.delete(corner)
            if Output == "CornerPin":
                nuke.delete(n)
        else:
            n = nuke.selectedNodes("Card2")
            for n in n:
                x = n['xpos'].value()
                y = n['ypos'].value()        
                trans = n['translate'].value()
                rot = n['rotate'].value()
                scalex = n['scaling'].value(0)
                scaley = n['scaling'].value(1)
                labelC = n['label'].value()
                mainA = nuke.nodes.Axis()
                mainA['translate'].setValue(trans)
                mainA['rotate'].setValue(rot)
                mainA['name'].setValue("mainA")
                mainA['xpos'].setValue(x)
                mainA['ypos'].setValue(y)
            
            n = nuke.selectedNodes()
            for n in n:
                if 'fstop' in n.knobs():
                    Cam = n
                elif 'orientation' in n.knobs():
                    print "."
                else:
                    BG = n 
            
            LUP = nuke.nodes.Reconcile3D()
            LUP.setInput(2,mainA)
            LUP.setInput(1,Cam)
            LUP.setInput(0,BG)
            LUP['name'].setValue("rec")
            LUP['xpos'].setValue(x)
            LUP['ypos'].setValue(y)
                
            n = nuke.nodes.Tracker3()
            n['enable1'].setValue(1)
            
            P1 = nuke.toNode("rec")
            nuke.execute(LUP,rangeA,rangeB)
            P1p = P1['output'].value()
    
            n['track1'].copyAnimations(LUP['output'].animations())
            n['xpos'].setValue(x+100)
            n['ypos'].setValue(y)
            n['label'].setValue(labelC)
                   
            # cleanup    
            mainA = nuke.toNode("mainA")
            rec = nuke.toNode("rec")     
            nuke.delete(mainA)
            nuke.delete(rec)

    else:
        nuke.message("upps... I think you forgot to select Camera+BG+Card") 

    





















 

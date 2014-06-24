def corn3D():
    import nuke

    nodes = nuke.selectedNodes()

    if len(nodes) != 3:
        nuke.message(
            "Please make sure you've selected a camera, a background and the "
            "card you wish to track"
        )
        return

    # here are basic stuff i will use later frame range and a table
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
    panel.addEnumerationPulldown("Output:", "All CornerPin CornerPin(matrix) Roto Tracker")
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


    #here is coming the main part where tracker and corner pin are created
    if Axis == False:
        n = nuke.selectedNodes("Card2")
        for n in n:


            width = float(n.width())
            heght = float(n.height())
            aspect =  heght/width

            x = n['xpos'].value()
            y = n['ypos'].value()
            unifscale = n['uniform_scale'].value()
            scalingx = n['scaling'].value(0)
            scalingy = n['scaling'].value(1)
            trans = n['translate'].value()
            rot = n['rotate'].value()

            traA = n['translate'].isAnimated()
            rotA = n['rotate'].isAnimated()

            labelC = n['label'].value()
            mainA = nuke.nodes.Axis()

            #mainA['translate'].setValue(trans)
            #mainA['rotate'].setValue(rot)
            mainA['xform_order'].setValue(3)
            if traA is True:
                mainA['translate'].copyAnimations(n['translate'].animations())
            else:
                mainA['translate'].setValue(trans)

            if rotA is True:
                mainA['rotate'].copyAnimations(n['rotate'].animations())
            else:
                mainA['rotate'].setValue(rot)



            mainA['name'].setValue("mainA")
            mainA['xpos'].setValue(x)
            mainA['ypos'].setValue(y)

            LU = nuke.nodes.Axis()
            LU['xform_order'].setValue(1)
            LU['translate'].setValue([-0.5*unifscale*scalingx,aspect*0.5*unifscale*scalingy,0])
            LU.setInput(0,mainA)
            LU['name'].setValue('LU')
            LU['xpos'].setValue(x)
            LU['ypos'].setValue(y)

            RU = nuke.nodes.Axis()
            RU['xform_order'].setValue(1)

            RU['translate'].setValue([0.5*unifscale*scalingx,aspect*0.5*unifscale*scalingy,0])
            RU.setInput(0,mainA)
            RU['name'].setValue('RU')
            RU['xpos'].setValue(x)
            RU['ypos'].setValue(y)

            LL = nuke.nodes.Axis()
            LL['translate'].setValue([-0.5*unifscale*scalingx,aspect*-0.5*unifscale*scalingy,0])
            LL.setInput(0,mainA)
            LL['name'].setValue('LL')
            LL['xpos'].setValue(x)
            LL['ypos'].setValue(y)


            RL= nuke.nodes.Axis()
            RL['translate'].setValue([0.5*unifscale*scalingx,aspect*-0.5*unifscale*scalingy,0])
            RL.setInput(0,mainA)
            RL['name'].setValue('RL')
            RL['xpos'].setValue(x)
            RL['ypos'].setValue(y)

        n = nuke.selectedNodes()
        for n in n:
            if 'fstop' in n.knobs():
                Cam = n
            elif 'orientation' in n.knobs():
                print "by Alexey Kuchinsky"
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
        n['xpos'].setValue(x+100)
        n['ypos'].setValue(y)
        n['label'].setValue(labelC)
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
        corner["label"].setValue(labelC  + "ref frame: " + refFrame)





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
        if Output == "CornerPin(matrix)" or Output == "All" or Output == "Roto":
            print "by Alexey Kuchinsky"
            projectionMatrixTo = nuke.math.Matrix4()
            projectionMatrixFrom = nuke.math.Matrix4()

            #dir(projectionMatrix)
            theCornerpinNode = corner
            theNewCornerpinNode = nuke.nodes.CornerPin2D()
            theNewCornerpinNode['transform_matrix'].setAnimated()

            imageWidth = float(theCornerpinNode.width())
            imageHeight = float(theCornerpinNode.height())

            first = rangeA
            last = rangeB
            frame = first
            while frame<last+1:
                to1x = theCornerpinNode['to1'].valueAt(frame)[0]
                to1y = theCornerpinNode['to1'].valueAt(frame)[1]
                to2x = theCornerpinNode['to2'].valueAt(frame)[0]
                to2y = theCornerpinNode['to2'].valueAt(frame)[1]
                to3x = theCornerpinNode['to3'].valueAt(frame)[0]
                to3y = theCornerpinNode['to3'].valueAt(frame)[1]
                to4x = theCornerpinNode['to4'].valueAt(frame)[0]
                to4y = theCornerpinNode['to4'].valueAt(frame)[1]


                from1x = theCornerpinNode['from1'].valueAt(frame)[0]
                from1y = theCornerpinNode['from1'].valueAt(frame)[1]
                from2x = theCornerpinNode['from2'].valueAt(frame)[0]
                from2y = theCornerpinNode['from2'].valueAt(frame)[1]
                from3x = theCornerpinNode['from3'].valueAt(frame)[0]
                from3y = theCornerpinNode['from3'].valueAt(frame)[1]
                from4x = theCornerpinNode['from4'].valueAt(frame)[0]
                from4y = theCornerpinNode['from4'].valueAt(frame)[1]

                projectionMatrixTo.mapUnitSquareToQuad(to1x,to1y,to2x,to2y,to3x,to3y,to4x,to4y)
                projectionMatrixFrom.mapUnitSquareToQuad(from1x,from1y,from2x,from2y,from3x,from3y,from4x,from4y)
                theCornerpinAsMatrix = projectionMatrixTo*projectionMatrixFrom.inverse()
                theCornerpinAsMatrix.transpose()

                a0 = theCornerpinAsMatrix[0]
                a1 = theCornerpinAsMatrix[1]
                a2 = theCornerpinAsMatrix[2]
                a3 = theCornerpinAsMatrix[3]
                a4 = theCornerpinAsMatrix[4]
                a5 = theCornerpinAsMatrix[5]
                a6 = theCornerpinAsMatrix[6]
                a7 = theCornerpinAsMatrix[7]
                a8 = theCornerpinAsMatrix[8]
                a9 = theCornerpinAsMatrix[9]
                a10 = theCornerpinAsMatrix[10]
                a11 = theCornerpinAsMatrix[11]
                a12 = theCornerpinAsMatrix[12]
                a13 = theCornerpinAsMatrix[13]
                a14 = theCornerpinAsMatrix[14]
                a15 = theCornerpinAsMatrix[15]

                theNewCornerpinNode['transform_matrix'].setValueAt(a0,frame,0)
                theNewCornerpinNode['transform_matrix'].setValueAt(a1,frame,1)
                theNewCornerpinNode['transform_matrix'].setValueAt(a2,frame,2)
                theNewCornerpinNode['transform_matrix'].setValueAt(a3,frame,3)
                theNewCornerpinNode['transform_matrix'].setValueAt(a4,frame,4)
                theNewCornerpinNode['transform_matrix'].setValueAt(a5,frame,5)
                theNewCornerpinNode['transform_matrix'].setValueAt(a6,frame,6)
                theNewCornerpinNode['transform_matrix'].setValueAt(a7,frame,7)
                theNewCornerpinNode['transform_matrix'].setValueAt(a8,frame,8)
                theNewCornerpinNode['transform_matrix'].setValueAt(a9,frame,9)
                theNewCornerpinNode['transform_matrix'].setValueAt(a10,frame,10)
                theNewCornerpinNode['transform_matrix'].setValueAt(a11,frame,11)
                theNewCornerpinNode['transform_matrix'].setValueAt(a12,frame,12)
                theNewCornerpinNode['transform_matrix'].setValueAt(a13,frame,13)
                theNewCornerpinNode['transform_matrix'].setValueAt(a14,frame,14)
                theNewCornerpinNode['transform_matrix'].setValueAt(a15,frame,15)


                theNewCornerpinNode['xpos'].setValue(x+300)
                theNewCornerpinNode['ypos'].setValue(y)
                theNewCornerpinNode['label'].setValue(labelC +"matrix")

                frame = frame + 1



        if Output == "CornerPin(matrix)":
            nuke.delete(corner)
            nuke.delete(n)

        if Output == "Roto" or Output == "All":
            def cornerToPaint():
                first = nuke.Root().knob('first_frame').getValue()
                first = int(first)
                last = nuke.Root().knob('last_frame').getValue()
                last = int(last)+1
                frame = first

                cor = theNewCornerpinNode
                Roto = nuke.nodes.Roto()
                Roto['xpos'].setValue(x+400)
                Roto['ypos'].setValue(y)
                Roto['label'].setValue(labelC)
                Knobs = Roto['curves']
                root=Knobs.rootLayer
                transform = root.getTransform()

                while frame<last:

                    cm0 = cor['transform_matrix'].getValueAt(frame,0)
                    cm1 = cor['transform_matrix'].getValueAt(frame,1)
                    cm2 = cor['transform_matrix'].getValueAt(frame,2)
                    cm3 = cor['transform_matrix'].getValueAt(frame,3)
                    cm4 = cor['transform_matrix'].getValueAt(frame,4)
                    cm5 = cor['transform_matrix'].getValueAt(frame,5)
                    cm6 = cor['transform_matrix'].getValueAt(frame,6)
                    cm7 = cor['transform_matrix'].getValueAt(frame,7)
                    cm8 = cor['transform_matrix'].getValueAt(frame,8)
                    cm9 = cor['transform_matrix'].getValueAt(frame,9)
                    cm10 = cor['transform_matrix'].getValueAt(frame,10)
                    cm11 = cor['transform_matrix'].getValueAt(frame,11)
                    cm12 = cor['transform_matrix'].getValueAt(frame,12)
                    cm13 = cor['transform_matrix'].getValueAt(frame,13)
                    cm14 = cor['transform_matrix'].getValueAt(frame,14)
                    cm15 = cor['transform_matrix'].getValueAt(frame,15)

                    matr = transform.getExtraMatrixAnimCurve(0,0)
                    matr.addKey(frame,cm0)
                    matr = transform.getExtraMatrixAnimCurve(0,1)
                    matr.addKey(frame,cm1)
                    matr = transform.getExtraMatrixAnimCurve(0,2)
                    matr.addKey(frame,cm2)
                    matr = transform.getExtraMatrixAnimCurve(0,3)
                    matr.addKey(frame,cm3)
                    matr = transform.getExtraMatrixAnimCurve(0,4)
                    matr.addKey(frame,cm4)
                    matr = transform.getExtraMatrixAnimCurve(0,5)
                    matr.addKey(frame,cm5)
                    matr = transform.getExtraMatrixAnimCurve(0,6)
                    matr.addKey(frame,cm6)
                    matr = transform.getExtraMatrixAnimCurve(0,7)
                    matr.addKey(frame,cm7)
                    matr = transform.getExtraMatrixAnimCurve(0,8)
                    matr.addKey(frame,cm8)
                    matr = transform.getExtraMatrixAnimCurve(0,9)
                    matr.addKey(frame,cm9)
                    matr = transform.getExtraMatrixAnimCurve(0,10)
                    matr.addKey(frame,cm10)
                    matr = transform.getExtraMatrixAnimCurve(0,11)
                    matr.addKey(frame,cm11)
                    matr = transform.getExtraMatrixAnimCurve(0,12)
                    matr.addKey(frame,cm12)
                    matr = transform.getExtraMatrixAnimCurve(0,13)
                    matr.addKey(frame,cm13)
                    matr = transform.getExtraMatrixAnimCurve(0,14)
                    matr.addKey(frame,cm14)
                    matr = transform.getExtraMatrixAnimCurve(0,15)
                    matr.addKey(frame,cm15)
                    frame = frame+1
            cornerToPaint()


        if Output == "Roto":
            nuke.delete(corner)
            nuke.delete(n)
            nuke.delete(theNewCornerpinNode)

   # here is a code for Reconcile only
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
            mainA['xform_order'].setValue(3)
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
                print "by Alexey Kuchinsky"
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

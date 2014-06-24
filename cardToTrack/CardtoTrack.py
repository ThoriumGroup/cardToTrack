try:
    import nuke
except ImportError:
    pass


def _card_to_track_panel():
    """GUI panel for getting card_to_track settings

    Args:
        N/A

    Returns:
        {
            'frange': (str) Frame Range,
            'first': (int) First Frame,
            'last': (int) Last Frame,
            'ref_frame': (int) Reference Frame,
            'output': Output Type,
            'axis': Translate Only Bool
         }

    Raises:
        N/A

    """
    # Grab our current frame to be used as default for ref_frame
    frame = nuke.frame()

    panel_results = {}

    # And our current frange to use as the default for range
    first = int(nuke.Root()['first_frame'].value())
    last = int(nuke.Root()['last_frame'].value())

    # Construct our panel
    panel = nuke.Panel("Card to track")

    panel.addSingleLineInput(
        "Range:",
        "{first}-{last}".format(
            first=first,
            last=last,
        )
    )
    panel.addEnumerationPulldown(
        "Output:",
        "All "
        "CornerPin "
        "CornerPin(Matrix) "
        "Roto Tracker"
    )
    panel.addSingleLineInput("Ref frame:", frame)
    panel.addBooleanCheckBox('Translate Only', False)

    # Show Panel
    if not panel.show():
        return

    # Get our entered values
    panel_results['frange'] = panel.value("Range:")
    panel_results['ref_frame'] = int(panel.value("Ref frame:"))
    panel_results['output'] = panel.value("Output:")
    panel_results['axis'] = panel.value("Translate Only")

    # Split returned range
    first, last = panel_results['frange'].split("-")
    panel_results['first'] = int(first)
    panel_results['last'] = int(last)

    return panel_results


def corn3D():
    nodes = nuke.selectedNodes()

    if len(nodes) != 3:
        nuke.message(
            "Please make sure you've selected a camera, a background and the "
            "card you wish to track"
        )
        return

    # Assign all of our required nodes to variables
    for node in nodes:
        if node.Class() == 'Camera2':
            camera = node
        elif node.Class() == 'Card2':
            card = node
        else:
            background = node

    # Check that we have a node at each variable
    if not camera or not card or not background:
        nuke.message(
            "No {camera}{cc}{card}{cb}{background} selected. Please select a "
            "camera, a background, and the card you wish to track.".format(
                camera='camera' if not camera else '',
                cc=', ' if not camera and not card else '',
                card='card' if not card else '',
                cb=', ' if (not camera or not card) and not background else '',
                background='background' if not background else ''
            )
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
    if not Axis:

        # Create our axis for corners
        width = float(card.width())
        height = float(card.height())
        aspect = height/width

        x = card['xpos'].value()
        y = card['ypos'].value()
        uniform_scale = card['uniform_scale'].value()
        scaling_x = card['scaling'].value(0)
        scaling_y = card['scaling'].value(1)
        translate = card['translate'].value()
        rotate = card['rotate'].value()

        card_label = card['label'].value()
        main_axis = nuke.nodes.Axis()

        main_axis['xform_order'].setValue(3)

        if card['translate'].isAnimated():
            main_axis['translate'].copyAnimations(
                card['translate'].animations()
            )
        else:
            main_axis['translate'].setValue(translate)

        if card['rotate'].isAnimated():
            main_axis['rotate'].copyAnimations(
                card['rotate'].animations()
            )
        else:
            main_axis['rotate'].setValue(rotate)

        main_axis['name'].setValue("mainA")
        main_axis['xpos'].setValue(x)
        main_axis['ypos'].setValue(y)

        upper_left = nuke.nodes.Axis()
        upper_left['xform_order'].setValue(1)
        upper_left['translate'].setValue(
            [
                -0.5 * uniform_scale * scaling_x,
                aspect * 0.5 * uniform_scale * scaling_y,
                0
            ]
        )
        upper_left.setInput(0, main_axis)
        upper_left['name'].setValue('UpperLeft')
        upper_left['xpos'].setValue(x)
        upper_left['ypos'].setValue(y)

        upper_right = nuke.nodes.Axis()
        upper_right['xform_order'].setValue(1)
        upper_right['translate'].setValue(
            [
                0.5 * uniform_scale * scaling_x,
                aspect * 0.5 * uniform_scale * scaling_y,
                0
            ]
        )
        upper_right.setInput(0, main_axis)
        upper_right['name'].setValue('UpperRight')
        upper_right['xpos'].setValue(x)
        upper_right['ypos'].setValue(y)

        lower_left = nuke.nodes.Axis()
        lower_left['translate'].setValue(
            [
                -0.5 * uniform_scale * scaling_x,
                aspect * -0.5 * uniform_scale * scaling_y,
                0
            ]
        )
        lower_left.setInput(0, main_axis)
        lower_left['name'].setValue('LowerLeft')
        lower_left['xpos'].setValue(x)
        lower_left['ypos'].setValue(y)

        lower_right = nuke.nodes.Axis()
        lower_right['translate'].setValue(
            [
                0.5 * uniform_scale * scaling_x,
                aspect * -0.5 * uniform_scale * scaling_y,
                0
            ]
        )
        lower_right.setInput(0, main_axis)
        lower_right['name'].setValue('LowerRight')
        lower_right['xpos'].setValue(x)
        lower_right['ypos'].setValue(y)

        upper_left_track = nuke.nodes.Reconcile3D()
        upper_left_track.setInput(2, upper_left)
        upper_left_track.setInput(1, camera)
        upper_left_track.setInput(0, background)
        upper_left_track['name'].setValue("UpperLeftTrack")
        upper_left_track['xpos'].setValue(x)
        upper_left_track['ypos'].setValue(y)

        upper_right_track = nuke.nodes.Reconcile3D()
        upper_right_track.setInput(2, upper_right)
        upper_right_track.setInput(1, camera)
        upper_right_track.setInput(0, background)
        upper_right_track['name'].setValue("UpperRightTrack")
        upper_right_track['xpos'].setValue(x)
        upper_right_track['ypos'].setValue(y)

        lower_left_track = nuke.nodes.Reconcile3D()
        lower_left_track.setInput(2, lower_left)
        lower_left_track.setInput(1, camera)
        lower_left_track.setInput(0, background)
        lower_left_track['name'].setValue("LowerLeftTrack")
        lower_left_track['xpos'].setValue(x)
        lower_left_track['ypos'].setValue(y)

        lower_right_track = nuke.nodes.Reconcile3D()
        lower_right_track.setInput(2, lower_right)
        lower_right_track.setInput(1, camera)
        lower_right_track.setInput(0, background)
        lower_right_track['name'].setValue("LowerRightTrack")
        lower_right_track['xpos'].setValue(x)
        lower_right_track['ypos'].setValue(y)

        card = nuke.nodes.Tracker3()
        card['xpos'].setValue(x + 100)
        card['ypos'].setValue(y)
        card['label'].setValue(card_label)
        card['enable1'].setValue(1)
        card['enable2'].setValue(1)
        card['enable3'].setValue(1)
        card['enable4'].setValue(1)

        nuke.execute(lower_left_track, rangeA, rangeB)
        nuke.execute(lower_right_track, rangeA, rangeB)
        nuke.execute(upper_right_track, rangeA, rangeB)
        nuke.execute(upper_left_track, rangeA, rangeB)

        card['track1'].copyAnimations(lower_left_track['output'].animations())
        card['track2'].copyAnimations(lower_right_track['output'].animations())
        card['track3'].copyAnimations(upper_right_track['output'].animations())
        card['track4'].copyAnimations(upper_left_track['output'].animations())
        card['use_for1'].setValue(7)
        card['use_for2'].setValue(7)
        card['use_for3'].setValue(7)
        card['use_for4'].setValue(7)

        # corner pin
        corner = nuke.nodes.CornerPin2D()
        corner['to1'].copyAnimations(lower_left_track['output'].animations())
        corner['to2'].copyAnimations(lower_right_track['output'].animations())
        corner['to3'].copyAnimations(upper_right_track['output'].animations())
        corner['to4'].copyAnimations(upper_left_track['output'].animations())
        corner['from1'].setValue(lower_left_track['output'].getValueAt(refFrame))
        corner['from2'].setValue(lower_right_track['output'].getValueAt(refFrame))
        corner['from3'].setValue(upper_right_track['output'].getValueAt(refFrame))
        corner['from4'].setValue(upper_left_track['output'].getValueAt(refFrame))
        corner['xpos'].setValue(x + 200)
        corner['ypos'].setValue(y)
        corner["label"].setValue(
            "{label} ref frame: {ref_frame}".format(
                label=card_label,
                ref_frame=refFrame
            )
        )

        # Cleanup our created nodes
        nuke.delete(main_axis)
        nuke.delete(upper_left)
        nuke.delete(upper_right)
        nuke.delete(lower_left)
        nuke.delete(lower_right)
        nuke.delete(lower_left_track)
        nuke.delete(lower_right_track)
        nuke.delete(upper_right_track)
        nuke.delete(upper_left_track)

        if Output == "Tracker":
            nuke.delete(corner)
        elif Output == "CornerPin":
            nuke.delete(card)
        elif Output in ["CornerPin(matrix)", "All", "Roto"]:

            to_matrix = nuke.math.Matrix4()
            from_matrix = nuke.math.Matrix4()

            corner_new = nuke.nodes.CornerPin2D()
            corner_new['transform_matrix'].setAnimated()

            first = rangeA
            last = rangeB
            frame = first
            while frame < last + 1:

                # We'll grab all of our current frame's corners using
                # some list comprehensions.
                to_corners = [
                    corner[knob].valueAt(frame) for knob in [
                        'to1', 'to2', 'to3', 'to4'
                    ]
                ]
                # This will return a list with 4 elements, but those
                # elements will be a tuple pair. We need to unpack the two
                # members of each tuple into a flat list.
                to_corners = [
                    value for values in to_corners for value in values
                ]

                # Same as the above. We get a list with tuple elements, then
                # unpack it into a flat list.
                from_corners = [
                    corner[knob].valueAt(frame) for knob in [
                        'from1', 'from2', 'from3', 'from4'
                    ]
                ]
                from_corners = [
                    value for values in from_corners for value in values
                ]

                # Pass our flat lists into the matrix methods.
                to_matrix.mapUnitSquareToQuad(*to_corners)
                from_matrix.mapUnitSquareToQuad(*from_corners)

                corner_pin_matrix = to_matrix * from_matrix.inverse()
                corner_pin_matrix.transpose()

                for i in xrange(16):
                    corner_new['transform_matrix'].setValueAt(
                        corner_pin_matrix[i],
                        frame,
                        i
                    )

                corner_new['xpos'].setValue(x + 300)
                corner_new['ypos'].setValue(y)
                corner_new['label'].setValue(
                    "{label}Matrix".format(label=card_label)
                )

                frame += 1



        if Output == "CornerPin(matrix)":
            nuke.delete(corner)
            nuke.delete(card)

        if Output == "Roto" or Output == "All":
            def cornerToPaint():
                first = nuke.Root().knob('first_frame').getValue()
                first = int(first)
                last = nuke.Root().knob('last_frame').getValue()
                last = int(last)+1
                frame = first

                cor = corner_new
                Roto = nuke.nodes.Roto()
                Roto['xpos'].setValue(x+400)
                Roto['ypos'].setValue(y)
                Roto['label'].setValue(card_label)
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
            nuke.delete(card)
            nuke.delete(corner_new)

   # here is a code for Reconcile only
    else:
        card = nuke.selectedNodes("Card2")
        for card in card:
            x = card['xpos'].value()
            y = card['ypos'].value()
            translate = card['translate'].value()
            rotate = card['rotate'].value()
            scalex = card['scaling'].value(0)
            scaley = card['scaling'].value(1)
            card_label = card['label'].value()
            main_axis = nuke.nodes.Axis()
            main_axis['xform_order'].setValue(3)
            main_axis['translate'].setValue(translate)
            main_axis['rotate'].setValue(rotate)
            main_axis['name'].setValue("mainA")
            main_axis['xpos'].setValue(x)
            main_axis['ypos'].setValue(y)

        card = nuke.selectedNodes()
        for card in card:
            if 'fstop' in card.knobs():
                camera = card
            elif 'orientation' in card.knobs():
                print "by Alexey Kuchinsky"
            else:
                background = card

        upper_left_track = nuke.nodes.Reconcile3D()
        upper_left_track.setInput(2,main_axis)
        upper_left_track.setInput(1,camera)
        upper_left_track.setInput(0,background)
        upper_left_track['name'].setValue("rec")
        upper_left_track['xpos'].setValue(x)
        upper_left_track['ypos'].setValue(y)

        card = nuke.nodes.Tracker3()
        card['enable1'].setValue(1)

        lower_left_track = nuke.toNode("rec")
        nuke.execute(upper_left_track,rangeA,rangeB)
        P1p = lower_left_track['output'].value()

        card['track1'].copyAnimations(upper_left_track['output'].animations())
        card['xpos'].setValue(x+100)
        card['ypos'].setValue(y)
        card['label'].setValue(card_label)

        # cleanup
        main_axis = nuke.toNode("mainA")
        rec = nuke.toNode("rec")
        nuke.delete(main_axis)
        nuke.delete(rec)

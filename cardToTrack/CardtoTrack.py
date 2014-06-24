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

    settings = _card_to_track_panel()
    if not settings:  # If panel canceled, we'll cancel.
        return

    frange = nuke.FrameRange(settings['frange'])

    #here is coming the main part where tracker and corner pin are created
    if not settings['axis']:

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

        def create_axis(offset_x, offset_y, name, xform=True):
            """Creates an axis matching a corner of a card"""
            axis = nuke.nodes.Axis()
            if xform:
                axis['xform_order'].setValue(1)

            axis['translate'].setValue(
                [
                    offset_x * uniform_scale * scaling_x,
                    offset_y * aspect * uniform_scale * scaling_y,
                    0
                ]
            )
            axis.setInput(0, main_axis)
            axis['name'].setValue(name)
            axis['xpos'].setValue(x)
            axis['ypos'].setValue(y)

            return axis

        upper_left = create_axis(-0.5, 0.5, 'UpperLeft')
        upper_right = create_axis(0.5, 0.5, 'UpperRight')
        lower_left = create_axis(-0.5, -0.5, 'LowerLeft', False)
        lower_right = create_axis(0.5, -0.5, 'LowerRight', False)

        axes = [upper_left, upper_right, lower_left, lower_right]

        def create_track(axis, name):
            """Creates a reconcile3D node attached to the axis"""
            track = nuke.nodes.Reconcile3D()
            track.setInput(2, axis)
            track.setInput(1, camera)
            track.setInput(0, background)
            track['name'].setValue(name)
            track['xpos'].setValue(x)
            track['ypos'].setValue(y)

            return track

        upper_left_track = create_track(upper_left, "UpperLeftTrack")
        upper_right_track = create_track(upper_right, "UpperRightTrack")
        lower_left_track = create_track(lower_left, "LowerLeftTrack")
        lower_right_track = create_track(lower_right, "LowerRightTrack")

        tracks = [
            lower_left_track, lower_right_track,
            upper_right_track, upper_left_track,
        ]

        card = nuke.nodes.Tracker3()
        card['xpos'].setValue(x + 100)
        card['ypos'].setValue(y)
        card['label'].setValue(card_label)
        for knob in ['enable1', 'enable2', 'enable3', 'enable4']:
            card[knob].setValue(1)

        for node in tracks:
            nuke.execute(node, settings['first'], settings['last'])

        for i, knob in enumerate(['track1', 'track2', 'track3', 'track4']):
            card[knob].copyAnimations(tracks[i]['output'].animations())
        for knob in ['use_for1', 'use_for2', 'use_for3', 'use_for4']:
            card[knob].setValue(7)

        # corner pin
        corner = nuke.nodes.CornerPin2D()
        for i, knob in enumerate(['to1', 'to2', 'to3', 'to4']):
            corner[knob].copyAnimations(tracks[i]['output'].animations())
        for i, knob in enumerate(['from1', 'from2', 'from3', 'from4']):
            corner[knob].setValue(tracks[i]['output'].getValueAt(settings['ref_frame']))
        corner['xpos'].setValue(x + 200)
        corner['ypos'].setValue(y)
        corner["label"].setValue(
            "{label} ref frame: {ref_frame}".format(
                label=card_label,
                ref_frame=settings['ref_frame']
            )
        )

        # Cleanup our created nodes
        for node in axes + tracks:
            nuke.delete(node)

        if settings['output'] == 'Tracker':
            nuke.delete(corner)
        elif settings['output'] == 'CornerPin':
            nuke.delete(card)
        elif settings['output'] in ['CornerPin(matrix)', 'All', 'Roto']:

            to_matrix = nuke.math.Matrix4()
            from_matrix = nuke.math.Matrix4()

            corner_new = nuke.nodes.CornerPin2D()
            corner_new['transform_matrix'].setAnimated()

            for frame in frange:

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

            if settings['output'] == "CornerPin(matrix)":
                nuke.delete(corner)
                nuke.delete(card)
            else:

                roto = nuke.nodes.Roto()
                roto['xpos'].setValue(x+400)
                roto['ypos'].setValue(y)
                roto['label'].setValue(card_label)
                transform = roto['curves'].rootLayer.getTransform()

                for frame in frange:

                    corner_matrix = [
                        corner_new['transform_matrix'].getValueAt(frame, i) for i in xrange(16)
                    ]

                    for i, value in enumerate(corner_matrix):
                        matrix_curve = transform.getExtraMatrixAnimCurve(0, i)
                        matrix_curve.addKey(frame, value)

                if settings['output'] == "Roto":
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
        nuke.execute(upper_left_track,settings['first'],settings['last'])
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

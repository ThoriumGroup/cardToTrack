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
    panel = nuke.Panel("Card to Track")

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
        "Roto "
        "Tracker"
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


def card_to_track():

    # Grab our selected nodes, there should only be three and we'll iterate
    # over them to determine which is which.
    nodes = nuke.selectedNodes()

    if len(nodes) != 3:
        nuke.message(
            "Please make sure you've selected a camera, a background and the "
            "card you wish to track"
        )
        return

    camera = None
    card = None
    background = None

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

    # Open a panel to grab our required settings and return a dictionary.
    settings = _card_to_track_panel()
    if not settings:  # If panel canceled, we'll cancel.
        return

    # Turn our frame range into a nuke.FrameRange object we can iterate over.
    frange = nuke.FrameRange(settings['frange'])

    # Card values
    card_pos_x = card['xpos'].value()
    card_pos_y = card['ypos'].value()
    card_width = float(card.width())
    card_height = float(card.height())
    card_aspect = card_height/card_width
    card_uniform_scale = card['uniform_scale'].value()
    card_scaling_x = card['scaling'].value(0)
    card_scaling_y = card['scaling'].value(1)
    card_translate = card['translate'].value()
    card_rotate = card['rotate'].value()
    card_label = card['label'].value()

    # Create our Main Axis node
    main_axis = nuke.nodes.Axis()
    main_axis['xform_order'].setValue(3)
    main_axis['translate'].setValue(card_translate)
    main_axis['rotate'].setValue(card_rotate)
    main_axis['name'].setValue("MainAxis")
    main_axis['xpos'].setValue(card_pos_x)
    main_axis['ypos'].setValue(card_pos_y + 40)

    def create_axis(offset_x, offset_y, parent_axis, name, xform=True):
        """Creates an axis matching a corner of a card"""
        axis = nuke.nodes.Axis()
        if xform:
            axis['xform_order'].setValue(1)

        axis['translate'].setValue(
            [
                offset_x * card_uniform_scale * card_scaling_x,
                offset_y * card_aspect * card_uniform_scale * card_scaling_y,
                0
            ]
        )
        axis.setInput(0, parent_axis)
        axis['name'].setValue(name)

        return axis

    def create_track(axis, name):
        """Creates a reconcile3D node attached to the axis"""
        track = nuke.nodes.Reconcile3D()
        track.setInput(2, axis)
        track.setInput(1, camera)
        track.setInput(0, background)
        track['name'].setValue(name)
        track['xpos'].setValue(card_pos_x)
        track['ypos'].setValue(card_pos_y)

        return track

    # Full card_to_track:
    if not settings['axis']:

        # Check if our card translates in space
        if card['translate'].isAnimated():
            main_axis['translate'].copyAnimations(
                card['translate'].animations()
            )

        # Check if our card rotates in space
        if card['rotate'].isAnimated():
            main_axis['rotate'].copyAnimations(
                card['rotate'].animations()
            )

        # TODO: What about animated scaling?

        # Create our axes at the corners of the card.
        upper_left = create_axis(-0.5, 0.5, main_axis, 'UpperLeft')
        upper_right = create_axis(0.5, 0.5, main_axis, 'UpperRight')
        lower_left = create_axis(-0.5, -0.5, main_axis, 'LowerLeft', False)
        lower_right = create_axis(0.5, -0.5, main_axis, 'LowerRight', False)

        axes = [upper_left, upper_right, lower_left, lower_right]

        # Position our axes nicely
        for i, axis in enumerate(axes):
            x = -100 if i % 2 else 100
            y = -100 if i < 2 else 100
            axis['xpos'].setValue(card_pos_x + x)
            axis['ypos'].setValue(card_pos_y + y)

        # Crate our reconcile3D nodes pointing to those axes
        upper_left_track = create_track(upper_left, "UpperLeftTrack")
        upper_right_track = create_track(upper_right, "UpperRightTrack")
        lower_left_track = create_track(lower_left, "LowerLeftTrack")
        lower_right_track = create_track(lower_right, "LowerRightTrack")

        tracks = [
            lower_left_track, lower_right_track,
            upper_right_track, upper_left_track,
        ]

        # Position our reconcile3D nodes
        for i, track in enumerate(tracks):
            x = -110 if i % 3 else 90
            y = 160 if i < 2 else -40
            track['xpos'].setValue(card_pos_x + x)
            track['ypos'].setValue(card_pos_y + y)

        tracker = nuke.nodes.Tracker3()
        tracker['xpos'].setValue(card_pos_x - 150)
        tracker['ypos'].setValue(card_pos_y + 60)
        tracker['label'].setValue(card_label)
        for knob in ['enable1', 'enable2', 'enable3', 'enable4']:
            tracker[knob].setValue(1)

        for node in tracks:
            nuke.execute(node, settings['first'], settings['last'])

        for i, knob in enumerate(['track1', 'track2', 'track3', 'track4']):
            tracker[knob].copyAnimations(tracks[i]['output'].animations())
        for knob in ['use_for1', 'use_for2', 'use_for3', 'use_for4']:
            tracker[knob].setValue(7)

        # corner pin
        corner = nuke.nodes.CornerPin2D()
        for i, knob in enumerate(['to1', 'to2', 'to3', 'to4']):
            corner[knob].copyAnimations(tracks[i]['output'].animations())
        for i, knob in enumerate(['from1', 'from2', 'from3', 'from4']):
            corner[knob].setValue(tracks[i]['output'].getValueAt(settings['ref_frame']))
        corner['xpos'].setValue(card_pos_x - 50)
        corner['ypos'].setValue(card_pos_y + 60)
        corner["label"].setValue(
            "{label} ref frame: {ref_frame}".format(
                label=card_label,
                ref_frame=settings['ref_frame']
            )
        )

        # Cleanup our created nodes
        for node in axes + tracks:
            nuke.delete(node)
        nuke.delete(main_axis)

        if settings['output'] == 'Tracker':
            nuke.delete(corner)
        elif settings['output'] == 'CornerPin':
            nuke.delete(tracker)
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

                corner_new['xpos'].setValue(card_pos_x + 50)
                corner_new['ypos'].setValue(card_pos_y + 60)
                corner_new['label'].setValue(
                    "{label}Matrix".format(label=card_label)
                )

            if settings['output'] == "CornerPin(matrix)":
                nuke.delete(corner)
                nuke.delete(tracker)
            else:

                roto = nuke.nodes.Roto()
                roto['xpos'].setValue(card_pos_x + 150)
                roto['ypos'].setValue(card_pos_y + 60)
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
                    nuke.delete(tracker)
                    nuke.delete(corner_new)

    # Here we'll only do translation
    else:

        main_track = create_track(main_axis, "MainTrack")

        tracker = nuke.nodes.Tracker3()
        tracker['enable1'].setValue(1)

        nuke.execute(main_track, settings['first'], settings['last'])

        tracker['track1'].copyAnimations(main_track['output'].animations())
        tracker['xpos'].setValue(card_pos_x + 100)
        tracker['ypos'].setValue(card_pos_y)
        tracker['label'].setValue(card_label)

        # cleanup
        nuke.delete(main_axis)
        nuke.delete(main_track)

Card To Track
=============

- **Author:** Alexey Kuchinski
- **Maintainer:** Sean Wallitsch
- **Email:** sean@grenadehop.com
- **License:** MIT
- **Status:** Development
- **Python Versions:** 2.6-2.7
- **Nuke Versions:** 6.3 and up

Converts a 3d card's corners to tracking points, corner pins or a
matrix calculation for use on a corner pin or roto.

Usage
-----

Select a camera, the card to track, and a background plate (for calculating
image resolution) and select CardToTrack from the menu. Fill out the desired
frame range, the type of output requested (Defaults to "All", which will export
a Tracker node with 4 tracking points, a Corner Pin node with the corner's
tracked, a Corner Pin node set with a matrix calculation, and a Roto set with
a matrix calculation), and the desired reference frame. If you only want the
translation tracked, check that box.

CardToTrack will then create the intermediate nodes required to calculate the
final desired output, run through the frame range, create the output nodes, and
finally clean up after itself.

More usage information is available in this YouTube video from the creator,
Alexey Kuchinski:

https://www.youtube.com/watch?v=-NTdTy2PzQ0

Installation
------------

To install, simply ensure the 'cardToTrack' directory is in your .nuke
directory or anywhere else within the Nuke python path.

Then, add the following lines to your 'menu.py' file:
::
    import cardToTrack
    cardToTrack.run()

Changelog
---------

*New in version 6.0:*

- Massive refactor and code cleanup
- Will no longer install menu items automatically on import, you need to call `cardToTrack.run()`
- The main function for executing cardToTrack has been renamed from `corn3D()` to `card_to_track_wrapper()`. If you already have python objects for your camera, card and background you can call `card_to_track()` which takes those arguments.
- New functions!
    - `corner_pin_to_corner_matrix()` transforms a CornerPin with keyframes to and from points into a transformation matrix based CornerPin, leaving the to/from knobs completely free.
    - `matrix_to_roto_matrix()` copies any node's transformation matrix into a Roto node's matrix.
    - `reconcile_to_corner()` that takes 4 Reconcile3D nodes in a list, and returns a CornerPin.
    - `reconcile_to_tracks()` takes up to 4 Reconcile3D nodes in a list, and returns a Tracker with those Reconcile3D's converted to tracks.

License
-------

    The MIT License (MIT)

    cardToTrack
    Copyright (c) 2011-2014, Alexey Kuchinski and Sean Wallitsch

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

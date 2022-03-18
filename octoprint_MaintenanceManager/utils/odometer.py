
# coding=utf-8
from __future__ import absolute_import

import math
import re
# copied from gcodeinterpreter.py Version OP 1.7.2

class Vector3D(object):
    """
    3D vector value

    Supports addition, subtraction and multiplication with a scalar value (float, int) as well as calculating the
    length of the vector.

    Examples:

    >>> a = Vector3D(1.0, 1.0, 1.0)
    >>> b = Vector3D(4.0, 4.0, 4.0)
    >>> a + b == Vector3D(5.0, 5.0, 5.0)
    True
    >>> b - a == Vector3D(3.0, 3.0, 3.0)
    True
    >>> abs(a - b) == Vector3D(3.0, 3.0, 3.0)
    True
    >>> a * 2 == Vector3D(2.0, 2.0, 2.0)
    True
    >>> a * 2 == 2 * a
    True
    >>> a.length == math.sqrt(a.x ** 2 + a.y ** 2 + a.z ** 2)
    True
    >>> copied_a = Vector3D(a)
    >>> a == copied_a
    True
    >>> copied_a.x == a.x and copied_a.y == a.y and copied_a.z == a.z
    True
    """

    def __init__(self, *args):
        if len(args) == 3:
            (self.x, self.y, self.z) = args

        elif len(args) == 1:
            # copy constructor
            other = args[0]
            if not isinstance(other, Vector3D):
                raise ValueError("Object to copy must be a Vector3D instance")

            self.x = other.x
            self.y = other.y
            self.z = other.z

    @property
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def __add__(self, other):
        try:
            if len(other) == 3:
                return Vector3D(self.x + other[0], self.y + other[1], self.z + other[2])
        except TypeError:
            # doesn't look like a 3-tuple
            pass

        try:
            return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
        except AttributeError:
            # also doesn't look like a Vector3D
            pass

        raise TypeError(
            "other must be a Vector3D instance or a list or tuple of length 3"
        )

    def __sub__(self, other):
        try:
            if len(other) == 3:
                return Vector3D(self.x - other[0], self.y - other[1], self.z - other[2])
        except TypeError:
            # doesn't look like a 3-tuple
            pass

        try:
            return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
        except AttributeError:
            # also doesn't look like a Vector3D
            pass

        raise TypeError(
            "other must be a Vector3D instance or a list or tuple of length 3"
        )

    def __mul__(self, other):
        try:
            return Vector3D(self.x * other, self.y * other, self.z * other)
        except TypeError:
            # doesn't look like a scalar
            pass

        raise ValueError("other must be a float or int value")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __abs__(self):
        return Vector3D(abs(self.x), abs(self.y), abs(self.z))

    def __eq__(self, other):
        if not isinstance(other, Vector3D):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __str__(self):
        return "Vector3D(x={}, y={}, z={}, length={})".format(
            self.x, self.y, self.z, self.length
        )


regex_command = re.compile(
    r"^\s*((?P<codeGM>[GM]\d+)(\.(?P<subcode>\d+))?|(?P<codeT>T)(?P<tool>\d+))"
)
"""Regex for a GCODE command."""


class Odometer(object):

    def __init__(self, extrusionChangedListener=None, totalAxisTraveling = None, totalExtrusionTraveleing = None):
        # self._logger = logging.getLogger(__name__)
        self.extrusionChangedListener = extrusionChangedListener
        self.max_extruders = 10
        self.g90_extruder = False

        self.scale = 1.0    # mm or inch
        if (totalAxisTraveling == None):
            self.totalAxisTraveling = Vector3D(0.0, 0.0, 0.0)
        else:
            self.totalAxisTraveling = totalAxisTraveling
        if (totalExtrusionTraveleing == None):
            self.totalExtrusionTraveleing = [0.0]
        else:
            self.totalExtrusionTraveleing = totalExtrusionTraveleing
        self.reset()

    def set_g90_extruder(self, flag=False):
        self.g90_extruder = flag

    def reset(self):
        self.currentE = [0.0]
        self.totalExtrusion = [0.0]
        self.lastTotalExtrusion = [0.0]
        self.maxExtrusion = [0.0]
        self.currentExtruder = 0    # Tool Id
        self.relativeE = False
        self.relativeMode = False
        self.duplicationMode = False
        self.scale = 1.0
        self.lastPos = Vector3D(0.0, 0.0, 0.0)
        self.pos = Vector3D(0.0, 0.0, 0.0)
        # self.totalAxisTraveling = Vector3D(0.0, 0.0, 0.0)
        # self.totalExtrusionTraveleing = [0.0]
        # self._fireExtrusionChangedEvent()
        pass

    # reset only the extruded ammount, the other values like relative/absolute mode must be untouched
    def reset_extruded_length(self):
        # for toolIndex in range(len(self.maxExtrusion)):
        # 	self.maxExtrusion[toolIndex] = 0.0
        # 	self.totalExtrusion[toolIndex] = 0.0
        # yes, it it changed, but the UI should present last used value self._fireExtrusionChangedEvent()
        pass

    def processGCodeLine(self, line):

        # save last position
        self.lastPos = self.pos
        self.lastTotalExtrusion = self.totalExtrusion.copy()

        move = False
        match = regex_command.search(line)
        gcode = tool = None
        if match:
            values = match.groupdict()
            if "codeGM" in values and values["codeGM"]:
                gcode = values["codeGM"]
            elif "codeT" in values and values["codeT"]:
                gcode = values["codeT"]
                tool = int(values["tool"])

        # G codes
        if gcode in ("G0", "G1"):  # Move
            x = self._getCodeFloat(line, "X")
            y = self._getCodeFloat(line, "Y")
            z = self._getCodeFloat(line, "Z")
            e = self._getCodeFloat(line, "E")
            f = self._getCodeFloat(line, "F")

            if x is not None or y is not None or z is not None:
                # this is a move
                move = True
            else:
                # print head stays on position
                move = False

            oldPos = self.pos

            # Use new coordinates if provided. If not provided, use prior coordinates (minus tool offset)
            # in absolute and 0.0 in relative mode.
            newPos = Vector3D(
                x * self.scale if x is not None else (0.0 if self.relativeMode else self.pos.x),
                y * self.scale if y is not None else (0.0 if self.relativeMode else self.pos.y),
                z * self.scale if z is not None else (0.0 if self.relativeMode else self.pos.z),
            )

            if self.relativeMode:
                # Relative mode: add to current position
                self.pos += newPos
            else:
                # Absolute mode: apply tool offsets
                self.pos = newPos

            # if f is not None and f != 0:
            #     feedrate = f

            if e is not None:
                if self.relativeMode or self.relativeE:
                    # e is already relative, nothing to do
                    pass
                else:
                    e -= self.currentE[self.currentExtruder]

                # If move with extrusion, calculate new min/max coordinates of model
                # if e > 0 and move:
                #     # extrusion and move -> oldPos & pos relevant for print area & dimensions
                #     self._minMax.record(oldPos)
                #     self._minMax.record(pos)

                self.totalExtrusion[self.currentExtruder] += e
                self.currentE[self.currentExtruder] += e
                self.maxExtrusion[self.currentExtruder] = max(
                    self.maxExtrusion[self.currentExtruder], self.totalExtrusion[self.currentExtruder]
                )

                if self.currentExtruder == 0 and len(self.currentE) > 1 and self.duplicationMode:
                    # Copy first extruder length to other extruders
                    for i in range(1, len(self.currentE)):
                        self.totalExtrusion[i] += e
                        self.currentE[i] += e
                        self.maxExtrusion[i] = max(self.maxExtrusion[i], self.totalExtrusion[i])
            else:
                e = 0

            # # move time in x, y, z, will be 0 if no movement happened
            # moveTimeXYZ = abs((oldPos - pos).length / feedrate)
            #
            # # time needed for extruding, will be 0 if no extrusion happened
            # extrudeTime = abs(e / feedrate)
            #
            # # time to add is maximum of both
            # totalMoveTimeMinute += max(moveTimeXYZ, extrudeTime)
            #
            # # process layers if there's extrusion
            # if e:
            #     self._track_layer(pos)
        # - arc movement not used at the moment
        if gcode in ("xxxG2", "xxxG3"):  # Arc Move
            x = self._getCodeFloat(line, "X")
            y = self._getCodeFloat(line, "Y")
            z = self._getCodeFloat(line, "Z")
            e = self._getCodeFloat(line, "E")
            i = self._getCodeFloat(line, "I")
            j = self._getCodeFloat(line, "J")
            r = self._getCodeFloat(line, "R")
            f = self._getCodeFloat(line, "F")

            # this is a move or print head stays on position
            move = (
                x is not None
                or y is not None
                or z is not None
                or i is not None
                or j is not None
                or r is not None
            )

            oldPos = self.pos

            # Use new coordinates if provided. If not provided, use prior coordinates (minus tool offset)
            # in absolute and 0.0 in relative mode.
            newPos = Vector3D(
                x * self.scale if x is not None else (0.0 if self.relativeMode else self.pos.x),
                y * self.scale if y is not None else (0.0 if self.relativeMode else self.pos.y),
                z * self.scale if z is not None else (0.0 if self.relativeMode else self.pos.z),
            )

            if self.relativeMode:
                # Relative mode: add to current position
                self.pos += newPos
            else:
                # Absolute mode: apply tool offsets
                self.pos = newPos

            # if f is not None and f != 0:
            #     feedrate = f

            # get radius and offset
            i = 0 if i is None else i
            j = 0 if j is None else j
            r = math.sqrt(i * i + j * j) if r is None else r

            # calculate angles
            centerArc = Vector3D(oldPos.x + i, oldPos.y + j, oldPos.z)
            startAngle = math.atan2(oldPos.y - centerArc.y, oldPos.x - centerArc.x)
            endAngle = math.atan2(self.pos.y - centerArc.y, self.pos.x - centerArc.x)

            if gcode == "G2":
                startAngle, endAngle = endAngle, startAngle
            if startAngle < 0:
                startAngle += math.pi * 2
            if endAngle < 0:
                endAngle += math.pi * 2

            # from now on we only think in counter-clockwise direction
            if e is not None:
                if self.relativeMode or self.relativeE:
                    # e is already relative, nothing to do
                    pass
                else:
                    e -= self.currentE[self.currentExtruder]

                # If move with extrusion, calculate new min/max coordinates of model
                # if e > 0 and move:
                #     # extrusion and move -> oldPos & pos relevant for print area & dimensions
                #     self._minMax.record(oldPos)
                #     self._minMax.record(self.pos)
                #     self._addArcMinMax(
                #         self._minMax, startAngle, endAngle, centerArc, r
                #     )

                self.totalExtrusion[self.currentExtruder] += e
                self.currentE[self.currentExtruder] += e
                self.maxExtrusion[self.currentExtruder] = max(
                    self.maxExtrusion[self.currentExtruder], self.totalExtrusion[self.currentExtruder]
                )

                if self.currentExtruder == 0 and len(self.currentE) > 1 and self.duplicationMode:
                    # Copy first extruder length to other extruders
                    for i in range(1, len(self.currentE)):
                        self.totalExtrusion[i] += e
                        self.currentE[i] += e
                        self.maxExtrusion[i] = max(self.maxExtrusion[i], self.totalExtrusion[i])
            else:
                e = 0

            # # move time in x, y, z, will be 0 if no movement happened
            # moveTimeXYZ = abs((oldPos - pos).length / feedrate)
            #
            # # time needed for extruding, will be 0 if no extrusion happened
            # extrudeTime = abs(e / feedrate)
            #
            # # time to add is maximum of both
            # totalMoveTimeMinute += max(moveTimeXYZ, extrudeTime)
            #
            # # process layers if there's extrusion
            # if e:
            #     self._track_layer(
            #         pos,
            #         {
            #             "startAngle": startAngle,
            #             "endAngle": endAngle,
            #             "center": centerArc,
            #             "radius": r,
            #         },
            #     )

        elif gcode == "G20":  # Units are inches
            self.scale = 25.4
        elif gcode == "G21":  # Units are mm
            self.scale = 1.0
        elif gcode == "G28":  # Home
            x = self._getCodeFloat(line, "X")
            y = self._getCodeFloat(line, "Y")
            z = self._getCodeFloat(line, "Z")
            origin = Vector3D(0.0, 0.0, 0.0)
            if x is None and y is None and z is None:
                self.pos = origin
            else:
                self.pos = Vector3D(self.pos)
                if x is not None:
                    self.pos.x = origin.x
                if y is not None:
                    self.pos.y = origin.y
                if z is not None:
                    self.pos.z = origin.z
        elif gcode == "G90":  # Absolute position
            self.relativeMode = False
            if self.g90_extruder:
                self.relativeE = False
        elif gcode == "G91":  # Relative position
            self.relativeMode = True
            if self.g90_extruder:
                self.relativeE = True

        elif gcode == "G92":    # Set Position
            x = self._getCodeFloat(line, "X")
            y = self._getCodeFloat(line, "Y")
            z = self._getCodeFloat(line, "Z")
            e = self._getCodeFloat(line, "E")

            if e is None and x is None and y is None and z is None:
                # no parameters, set all axis to 0
                self.currentE[self.currentExtruder] = 0.0
                self.pos.x = 0.0
                self.pos.y = 0.0
                self.pos.z = 0.0
            else:
                # some parameters set, only set provided axes
                if e is not None:
                    self.currentE[self.currentExtruder] = e
                if x is not None:
                    self.pos.x = x
                if y is not None:
                    self.pos.y = y
                if z is not None:
                    self.pos.z = z
        # M codes
        elif gcode == "M82":  # Absolute E
            self.relativeE = False
        elif gcode == "M83":  # Relative E
            self.relativeE = True

        if (move):
            currentAxisTraveling = self.pos - self.lastPos
            self.totalAxisTraveling.x = self.totalAxisTraveling.x + abs(currentAxisTraveling.x)
            self.totalAxisTraveling.y = self.totalAxisTraveling.y + abs(currentAxisTraveling.y)
            self.totalAxisTraveling.z = self.totalAxisTraveling.z + abs(currentAxisTraveling.z)
            # print("LastPosition: " + str(self.lastPos)+ " NewPosition:" + str(self.pos))
            # print("Moved: " + str(currentAxisTraveling))
            # print("TotalTraveling: " + str(self.totalAxisTraveling))


        currentExtrusionTraveling = self._calcCurrentExtrusionTraveleing(self.totalExtrusion, self.lastTotalExtrusion)
        self.totalExtrusionTraveleing = self._calcTotalExtrusionTraveling(currentExtrusionTraveling, self.totalExtrusionTraveleing)
        # print("******")
        # print("CurrentExtrusion: " + str(self.currentE))
        # print("TotalExtrusion: " + str(self.totalExtrusion))
        # # print("MaxExtrusion: " + str(self.maxExtrusion))
        # print("currentExtrusionTraveling: " + str(currentExtrusionTraveling))
        # print("totalExtrusionTraveleing: " + str(self.totalExtrusionTraveleing))
        # print("******")
        pass


    def getTotalAxisTraveling(self):
        return self.totalAxisTraveling

    def getTotalExtrusionTraveling(self):
        return self.totalExtrusionTraveleing


    def _fireExtrusionChangedEvent(self):
        if (self.extrusionChangedListener != None):
            self.extrusionChangedListener(self.getExtrusionAmount())

    def _calcCurrentExtrusionTraveleing(self, totalExtrusion, lastTotalExtrusion):
        result = []
        for toolIndex in range(len(totalExtrusion)):
            total = totalExtrusion[toolIndex]
            last = lastTotalExtrusion[toolIndex]
            result.append(abs(last - total))
        return result

    def _calcTotalExtrusionTraveling(self, currentExtrusionTraveling, totalExtrusionTraveleing):
        result = []
        for toolIndex in range(len(currentExtrusionTraveling)):
            currentTravel = currentExtrusionTraveling[toolIndex]
            totalTravel = totalExtrusionTraveleing[toolIndex]
            result.append(totalTravel + currentTravel)
        return result


    def _getCodeInt(self, line, code):
        return self._getCode(line, code, int)

    def _getCodeFloat(self, line, code):
        return self._getCode(line, code, float)

    def _getCode(self, line, code, c):
        n = line.find(code) + 1
        if n < 1:
            return None
        m = line.find(" ", n)
        try:
            if m < 0:
                result = c(line[n:])
            else:
                result = c(line[n:m])
        except ValueError:
            return None

        if math.isnan(result) or math.isinf(result):
            return None

        return result




if __name__ == "__main__":
    print("START !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    odometer = Odometer()

    odometer.processGCodeLine("G0 X12")
    # odometer.processGCodeLine("G0 X-12")
    # odometer.processGCodeLine("G91")
    # odometer.processGCodeLine("G0 X-1")
    # odometer.processGCodeLine("G0 X12")

    # odometer.processGCodeLine("G0 E12")
    # odometer.processGCodeLine("G91")
    # odometer.processGCodeLine("G0 E-13")



    # odometer.processGCodeLine("G2 X125 Y32 I10.5 J10.5")
    # odometer.processGCodeLine("G0 F1500 ; set the feedrate to 1500 mm/min")
    # odometer.processGCodeLine("G1 X90.6 Y13.8 ; move to 90.6mm on the X axis and 13.8mm on the Y axis")

    # filename = "/Users/o0632/Library/Application Support/OctoPrint/uploads/prusa22-messschieber_boden.gcode"
    filename = "/Users/o0632/0_Projekte/3DDruck/OctoPrint/OctoPrint-MaintenanceManager/testdata/xyzCalibration_cube.gcode"
    lines = None
    with open(filename) as file:
        lines = file.readlines()
    for line in lines:
        odometer.processGCodeLine(line)

    print("Axis-Traveling: " + str(odometer.getTotalAxisTraveling()))
    print("Extrusion-Traveling: " + str(odometer.getTotalExtrusionTraveling()))

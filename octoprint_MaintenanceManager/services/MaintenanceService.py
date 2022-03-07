# coding=utf-8
from __future__ import absolute_import
import re

class MaintenanceService():

    def __init__(self):
        pass




if __name__ == "__main__":

    # s = "G1 Y-3.0 Z5.0 ; set nozzle 5mm above bed while waiting for temp"
    #
    # semiPostion = s.find(";")
    # print (semiPostion)
    #
    #
    # command = s[:semiPostion]
    # print(command)

    service = MaintenanceService()

    # filepath = '/Users/o0632/0_Projekte/3DDruck/OctoPrint/GitHub-Issues/DisplayLayerProgress/issue124/RobinsonCrusoe_A_0.2mm_PLA_MK3S_10h57m-OCTO.gcode'
    # with open(filepath) as fp:
    #     line = fp.readline()
    #     cnt = 1
    #     while line:
    #         line = line.strip()
    #         if len(line) >= 3:
    #             gcode = line.split()[0]
    #
    #             semiPostion = line.find(";")
    #             command = line[:semiPostion]
    #             service.analyseGCode(gcode, command)
    #         line = fp.readline()

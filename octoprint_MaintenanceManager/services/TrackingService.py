# coding=utf-8
from __future__ import absolute_import

import sys
import time
import json
import os
from time import perf_counter as now

from datetime import datetime

from octoprint_MaintenanceManager.utils import StringUtils
from octoprint_MaintenanceManager.utils.odometer import Odometer
from octoprint_MaintenanceManager.utils.odometer import Vector3D
from octoprint.util import RepeatedTimer


class TrackingService():

    STORAGE_TIMER_INTERVAL = 1.0

    STORAGE_FILENAME = "trackingValues.json"

    TRACKING_STATE_STOPPED = "stopped"
    TRACKING_STATE_TRACKING = "tracking"
    TRACKING_STATE_PAUSE = "pause"

    def __init__(self):
        self.currentTrackingState = self.TRACKING_STATE_STOPPED
        self.trackingStartedDateTime = None
        self.startTime = None
        self.odometer = None

        self.pluginDataFolder = None
        self.totalDuration = 0
        self.axisTraveling = None
        self.extrusionTraveling = None

        self._isInitiallized = False
        pass

    def initialize(self, pluinDataFolder, logger = None):
        self.pluginDataFolder = pluinDataFolder

        self._loadInitialValues()
        self.odometer = Odometer(totalAxisTraveling=self.axisTraveling,
                                 totalExtrusionTraveleing=self.extrusionTraveling)

        if (self.trackingStartedDateTime == None):
            self.trackingStartedDateTime = datetime.now()
            self._saveCurrentValues()

        self._initStorageTimer()

        self._isInitiallized = True
        pass

    def _storageTimerFunction(self):
        self._saveCurrentValues()
        print(".")
        pass

    def _initStorageTimer(self):
        storageTimer = RepeatedTimer(self.STORAGE_TIMER_INTERVAL, self._storageTimerFunction)
        storageTimer.start()

    def _loadInitialValues(self):
        result = {}
        try:
            storageFileLocation = os.path.join(self.pluginDataFolder, self.STORAGE_FILENAME)
            f = open(storageFileLocation, "rt")
            dictAsJson = json.load(f)
            result = dictAsJson

            # assign last values
            dateTimeStr = result["trackingStartedDateTime"]
            if (dateTimeStr != None):
                self.trackingStartedDateTime = datetime.strptime(dateTimeStr, "%Y-%m-%d %H:%M:%S.%f")

            self.totalDuration = result["totalDuration"]
            if ("axisTraveling.x" in result):
                x = result["axisTraveling.x"]
                y = result["axisTraveling.y"]
                z = result["axisTraveling.z"]

                self.axisTraveling = Vector3D(x,y,z)

            self.extrusionTraveling = result["extrusionTraveling"]

        except Exception as e:
            # Firsttime we expect FileNotFoundError
            if (type(e) != FileNotFoundError):
                print("BOOOOOMMMM")
                print(e)


    def _saveCurrentValues(self):

        currentTotalDuration = self.getCurrentTotalDuration()
        axisTraveling = self.getAxisTraveling()
        extrusionTraveling =  self.getExtrusionTraveling()

        axis = Vector3D(1.0, 2.0, 3.0)
        valuesAsDict = {
            "trackingStartedDateTime": self.trackingStartedDateTime,
            "totalDuration": self.totalDuration,
            "axisTraveling.x": axisTraveling.x,
            "axisTraveling.y": axisTraveling.y,
            "axisTraveling.z": axisTraveling.z,
            "extrusionTraveling": extrusionTraveling
        }
        dictAsJson = json.dumps(valuesAsDict, indent=4, default=str)

        storageFileLocation = os.path.join(self.pluginDataFolder, self.STORAGE_FILENAME)
        f = open(storageFileLocation, "wt")
        f.write(dictAsJson)
        f.close()

        pass

    def startTracking(self):
        if (self._isInitiallized == False or self.pluginDataFolder == None):
            raise AssertionError("Before you start, you need to call 'initialize' and assign a pluginDataFolder")
        if (self.currentTrackingState != self.TRACKING_STATE_STOPPED):
            raise AssertionError("Start Tracking not possible, because tracking is currently not stopped. Current state: "+self.currentTrackingState)
        print("Start Tracking ")

        self.currentTrackingState = self.TRACKING_STATE_TRACKING
        self.startTime = now()
        pass

    def pauseTracking(self):
        if (self.currentTrackingState != self.TRACKING_STATE_TRACKING):
            raise AssertionError("Pause Tracking not possible, because tracking is currently not tracking. Current state: "+self.currentTrackingState)
        print("Pause Tracking ")
        self.currentTrackingState = self.TRACKING_STATE_PAUSE

        # nowTime = int(now())
        # startTime = int(self.startTime)
        # currentDuration = (nowTime - startTime)
        # self.totalDuration = self.totalDuration + currentDuration
        self.totalDuration = self._calcTotalDuration()

        self._saveCurrentValues()

    def resumeTracking(self):
        if (self.currentTrackingState != self.TRACKING_STATE_PAUSE):
            raise AssertionError("Resume Tracking not possible, because tracking is currently not paused. Current state: "+self.currentTrackingState)
        print("Resume Tracking ")
        self.currentTrackingState = self.TRACKING_STATE_TRACKING
        self.startTime = now()

    def stopTracking(self):
        # if (self.currentTrackingState != self.TRACKING_STATE_TRACKING and self.currentTrackingState != self.TRACKING_STATE_PAUSE):
        #     raise AssertionError("Stop Tracking not possible, because tracking is currently not tracking. Current state: "+self.currentTrackingState)
        print("Stop Tracking ")
        self.currentTrackingState = self.TRACKING_STATE_STOPPED

        if (self.currentTrackingState != self.TRACKING_STATE_PAUSE):
            nowTime = int(now())
            startTime = int(self.startTime)
            currentDuration = (nowTime - startTime)
            self.totalDuration = self.totalDuration + currentDuration

        self._saveCurrentValues()

    def processGCodeLine(self, gcodeLine:str):
        # if (self.currentTrackingState != self.TRACKING_STATE_TRACKING):
        #     raise AssertionError("Process Tracking not possible, because tracking is currently not tracking. Current state: "+self.currentTrackingState)
        print("Process Tracking ")
        self.odometer.processGCodeLine(gcodeLine)
        pass

    def getTrackingSince(self):
        return self.trackingStartedDateTime

     # Get the totalDuration of this tracking. Can be called after pause or stop, NOT in betweeen. Use getCurrentTotalDuration if you need it in between.
    def getTotalDuration(self):
        return self.totalDuration

    # Calculates the currentTotalDuration
    def getCurrentTotalDuration(self):
        if (self.currentTrackingState == self.TRACKING_STATE_PAUSE or
            self.currentTrackingState ==self.TRACKING_STATE_STOPPED or
            self.startTime == None):
            return self.totalDuration

        return self._calcTotalDuration()

    def getAxisTraveling(self):
        return self.odometer.getTotalAxisTraveling()

    def getExtrusionTraveling(self):
        return self.odometer.getTotalExtrusionTraveling()

    def _calcTotalDuration(self):
        nowTime = int(now())
        startTime = int(self.startTime)
        currentDuration = (nowTime - startTime)
        return self.totalDuration + currentDuration


if __name__ == "__main__":


    service = TrackingService()
    service.initialize(".")

    service.startTracking()
    service.processGCodeLine("123")
    time.sleep(3)
    service.processGCodeLine("G1 X50 Y25.3 E22.4")
    service.pauseTracking()
    time.sleep(5)
    service.resumeTracking()
    service.processGCodeLine("G1 X60 Y35.3 E32.4")
    time.sleep(4)
    service.stopTracking()
    # service.startTracking()
    # time.sleep(4)

    print("*************")
    print("Final Total-Duration: " + StringUtils.secondsToText(service.getTotalDuration()))

    print("Axis-Traveling: " + str(service.getAxisTraveling()))
    print("Extrusion-Traveling: " + str(service.getExtrusionTraveling()))

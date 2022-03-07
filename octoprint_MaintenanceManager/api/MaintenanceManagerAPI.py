# coding=utf-8
from __future__ import absolute_import

import logging

import octoprint.plugin
import datetime
import flask
from flask import jsonify, request, make_response, Response, send_file, abort
import json

from octoprint_MaintenanceManager.utils import StringUtils


class MaintenanceManagerAPI(octoprint.plugin.BlueprintPlugin):

    #######################################################################################   LOAD TRACKING INFORMATION
    @octoprint.plugin.BlueprintPlugin.route("/trackingInformation", methods=["GET"])
    def loadDatabaseMetaData(self):

        trackingInformation = None

        if (self.trackingService != None):
            trackingSince = self.trackingService.getTrackingSince()
            totalPrintTime = self.trackingService.getCurrentTotalDuration()
            axisTraveleing = self.trackingService.getAxisTraveling()
            extrusionTraveleing = self.trackingService.getExtrusionTraveling()

            trackingSince = StringUtils.formatDateTime(trackingSince)
            totalPrintTime = StringUtils.secondsToText(totalPrintTime)
            xMovement = StringUtils.mmToText(axisTraveleing.x)
            yMovement = StringUtils.mmToText(axisTraveleing.y)
            zMovement = StringUtils.mmToText(axisTraveleing.z)

            eMovement = StringUtils.mmToText(extrusionTraveleing[0])
            trackingInformation = {
                "trackingSince": trackingSince,
                "totalPrintTime": totalPrintTime,
                "xMovement": xMovement,
                "yMovement": yMovement,
                "zMovement": zMovement,
                "eMovement": eMovement
            }
        return flask.jsonify({
            "trackingInformation": trackingInformation
        })


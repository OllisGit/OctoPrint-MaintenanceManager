# coding=utf-8
from __future__ import absolute_import



import octoprint.plugin
from octoprint.events import Events

from octoprint_MaintenanceManager.api.MaintenanceManagerAPI import MaintenanceManagerAPI
from octoprint_MaintenanceManager.services.MaintenanceService import MaintenanceService
from octoprint_MaintenanceManager.services.TrackingService import TrackingService


class MaintenanceManagerPlugin(
    MaintenanceManagerAPI,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.EventHandlerPlugin
):

    def initialize(self):
        self.maintenanceService = MaintenanceService()
        self.trackingService = TrackingService()
        self.trackingService.initialize(self.get_plugin_data_folder(), self._logger)

    def on_event(self, event, payload):
        if event == Events.PRINT_STARTED:
            self.trackingService.startTracking()
            return
        if event == Events.PRINT_PAUSED:
            self.trackingService.pauseTracking()
            return
        if event == Events.PRINT_RESUMED:
            self.trackingService.resumeTracking()
            return
        if event == Events.PRINT_DONE or event == Events.PRINT_FAILED or event == Events.PRINT_CANCELLED:
            self.trackingService.stopTracking()
            return

    # eval g-code (comm.sending_thread)
    def sentGCodeHook(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        # self.maintenanceService.analyseGCode(gcode, cmd) # cmd = M110 N0, gcode = M110
        self.trackingService.processGCodeLine(cmd) # cmd = M110 N0, gcode = M110

        return

    ##~~ SettingsPlugin mixin
    def get_settings_defaults(self):
        return dict(
            installed_version=self._plugin_version
        )

    ##~~ TemplatePlugin mixin
    def get_template_configs(self):
        return [
            dict(type="tab", name="Maintenance Manager"),
            dict(type="settings", custom_bindings=True, name="Maintenance Manager")
        ]
    ##~~ AssetPlugin mixin
    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": [
                "js/MaintenanceManager.js",
                "js/MaintenanceManager-APIClient.js"],
            "css": ["css/MaintenanceManager.css"],
            "less": ["less/MaintenanceManager.less"]
        }

    ##~~ Softwareupdate hook
    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return dict(
            MaintenanceManager=dict(
                displayName="MaintenanceManager Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="OllisGit",
                repo="OctoPrint-MaintenanceManager",
                current=self._plugin_version,

                # Release channels
                stable_branch=dict(
                    name="Only Release",
                    branch="master",
                    comittish=["master"]
                ),
                prerelease_branches=[
                    dict(
                        name="Release & Candidate",
                        branch="pre-release",
                        comittish=["pre-release", "master"],
                    ),
                    dict(
                        name="Release & Candidate & under Development",
                        branch="development",
                        comittish=["development", "pre-release", "master"],
                    )
                ],

                # update method: pip
                pip="https://github.com/OllisGit/OctoPrint-MaintenanceManager/releases/download/{target_version}/master.zip"
            )
        )

# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "MaintenanceManager Plugin"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
__plugin_pythoncompat__ = ">=3,<4" # only python 3
#__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = MaintenanceManagerPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.sent": __plugin_implementation__.sentGCodeHook,
    }

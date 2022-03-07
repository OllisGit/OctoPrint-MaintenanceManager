/*
 * View model for MaintenanceManager
 *
 * Author: OllisGit
 * License: AGPLv3
 */
$(function() {
    function MaintenanceManagerViewModel(parameters) {

        var PLUGIN_ID = "MaintenanceManager"; // from setup.py plugin_identifier
        var self = this;

        // assign the injected parameters, e.g.:
        self.settingsViewModel = parameters[0];
        self.pluginSettings = null;

        self.apiClient = new MaintenanceManagerAPIClient(PLUGIN_ID, BASEURL);

        self.trackingDisplay = null;
        self.trackingDisplayVisible = false;
        self.trackingDisplayCloseFunction = function(){
            self.trackingDisplayVisible = false;
        }

        self.updateTrackingDisplayText = function(trackingInformation){
            var trackingSince  = "-";
            var totalPrintTime  = "-";
            var xMovement  = "-";
            var yMovement  = "-";
            var zMovement  = "-";
            var eMovement  = "-";

            if (trackingInformation){
                trackingSince = trackingInformation["trackingSince"];
                totalPrintTime = trackingInformation["totalPrintTime"];
                xMovement = trackingInformation["xMovement"];
                yMovement = trackingInformation["yMovement"];
                zMovement = trackingInformation["zMovement"];
                eMovement = trackingInformation["eMovement"];
            }

            self.trackingDisplay.update("Tracking since: <b>" + trackingSince + "</b><br>" +
                            "Total print time: <b>"+totalPrintTime+"</b><br>" +
                            "Total Movement:<br>" +
                            "<ul>" +
                            "<li>X: <b>" + xMovement + "</b></li>" +
                            "<li>Y: <b>" + yMovement + "</b></li>" +
                            "<li>Z: <b>" + zMovement + "</b></li>" +
                            "<li>T0: <b>" + eMovement + "</b></li>" +
                            "</ul>");
        }

        self._initUpdater = function(){
            if (self.trackingDisplay == null){
                self.trackingDisplay = new PNotify({
                                                    title: 'Tracking Display',
                                                    type: 'info',
                                                    // width: data.printerDisplayWidth,
                                                    //addclass: "stack-bottomleft",
                                                    addclass: "stack-bottomright",
                                                    stack: {"dir1": "left", "dir2": "up", "push": "top"},
                                                    hide: false,
                                                    after_close: self.trackingDisplayCloseFunction,
                                                    buttons:{
                                                        closer_hover: false,
                                                        sticker: false
                                                    }
                                                    });

                self.updateTrackingDisplayText(null);

                self.trackingDisplayVisible = true;
            }

            self.updateTrackingDisplayWorker = function() {
                // var clockVisible = self.settingsViewModel.settings.plugins.DisplayLayerProgress.showTimeInNavBar();
                if (self.trackingDisplayVisible) {
                    self.apiClient.callTrackingInformation(function(responseData){
                        if (responseData.trackingInformation){
                            var trackingInformaiton = responseData.trackingInformation;
                            self.updateTrackingDisplayText(trackingInformaiton);
                        }
                    });
                    window.setTimeout(self.updateTrackingDisplayWorker, 1000);
                } else {
                    // // hide clock and stop clock
                    // $("#dlpNavBarTime-left").hide();
                    // $("#dlpNavBarTime-right").hide();
                }
            };

            self.updateTrackingDisplayWorker();
        }

        ///////////////////////////////////////////////////// START: OctoPrint Hooks

        self.onBeforeBinding = function() {
            // assign current pluginSettings
            self.pluginSettings = self.settingsViewModel.settings.plugins[PLUGIN_ID];
        }


        self.onAfterBinding = function (){
            // alert("Hallo");
        }

        self.onAllBound = function(){

            // init timer
            self._initUpdater();

        }

        // receive data from server
        self.onDataUpdaterPluginMessage = function (plugin, data) {

            if (plugin != PLUGIN_ID) {
                return;
            }

            // if ("" == data.action){
            //
            // }

        }

        ///////////////////////////////////////////////////// END: OctoPrint Hooks
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: MaintenanceManagerViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [
            "settingsViewModel"
        ],
        // Elements to bind to, e.g. #settings_plugin_MaintenanceManager, #tab_plugin_MaintenanceManager, ...
        elements: [
            "#settings_plugin_MaintenanceManager"
        ]
    });
});

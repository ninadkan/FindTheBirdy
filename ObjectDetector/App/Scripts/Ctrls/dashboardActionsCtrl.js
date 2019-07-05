(function () {

    // // The HTML for this View
    var viewHTML;

    function btnRefresh(obj){
        console.log("Actions:btnRefresh");
        var jsonData = {
            _sourceFileShareFolderName: 'linuxraspshare',
            _sourceDirectoryName: ['Share', 'backup'],
            _destinationFileShareFolderName: 'experiment-data',
            _destinationDirectoryName: 'object-detection',
            _outputFolderName: 'output',
            _fileExtensionFilter: '.jpg'
        };

        var updatedTagJson = JSON.stringify(jsonData);
        $('#dynamicTable').empty();
        $('#lblResult').html("");

        PushPop_Wraper.pushElement(obj.id);
        
        InvokeWebAPIGeneric(    'DashBoardGetAllFilesInfo',
                                updatedTagJson,
                                processDestinationFileData);        
    }

    function btnDestinationRefresh(obj) {
        console.log("Actions:btnDestinationRefresh");
        var jsonData = {
            _destinationFileShareFolderName: 'experiment-data',
            _destinationDirectoryName: 'object-detection',
            _outputFolderName: 'output',
            _fileExtensionFilter: '.jpg'
        };

        var updatedTagJson = JSON.stringify(jsonData);
        $('#dynamicTable').empty();
        $('#lblResult').html("");

        PushPop_Wraper.pushElement(obj.id);
        InvokeWebAPIGeneric(    'DashBoardGetAllDestinationFilesInfo',
                                updatedTagJson,
                                processDestinationFileData);
    }

    function processDestinationFileData(data) {
        PushPop_Wraper.popElement();
        var $dataContainer = $(".data-container");
        $dataContainer.empty();

        var $html = $(viewHTML);
        var $template = $html.find(".data-container");
        var outputData = '';
        var $entry = $template;

        if (data) {
            console.log(data);
            var tp = $.parseJSON(data);
            if (tp) {
                console.log(tp);
                var elapsedTime = tp["elapsedTime"];
                $('#lblResult').html("Elapsed Time = " + elapsedTime);

                var result = tp["result"];
                //console.log(result);
                if (result) {
                    for (var i = 0; i < result.length; i++) {
                        console.log(result[i]);
                        var experimentName = result[i]["ExperimentName"];
                        var Properties = result[i]["Properties"];
                        $entry.find(".view-data-experiment-run-date").html(experimentName);
                        $entry.find(".view-data-number-of-images-captured").html(Properties[0]);
                        $entry.find(".view-data-experiment-source-folder-size").html(humanFileSize(Properties[1], true));
                        $entry.find(".view-data-destination-experiment-folder-exists").html(Properties[2]);
                        $entry.find(".view-data-number-of-images-in-destination-folder").html(Properties[3]);
                        $entry.find(".view-data-image-size-destination-folder").html(humanFileSize(Properties[4], true));
                        $entry.find(".view-data-mask-file-exists").html(Properties[5]);
                        $entry.find(".view-data-number-of-images-detected-by-openCV").html(Properties[6]);
                        $entry.find(".view-data-size-of-openCV-images-detected").html(humanFileSize(Properties[7], true));
                        $entry.find(".view-data-place-holder").html("");           
                        outputData += $entry.html();
                    }
                }
            }
        }
        $dataContainer.html(outputData);
    }


    function humanFileSize(bytes, si) {
        var thresh = si ? 1000 : 1024;
        if (Math.abs(bytes) < thresh) {
            return bytes + ' B';
        }
        var units = si
            ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
            : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'];
        var u = -1;
        do {
            bytes /= thresh;
            ++u;
        } while (Math.abs(bytes) >= thresh && u < units.length - 1);
        return bytes.toFixed(1) + ' ' + units[u];
    }

    function registerViewClickHandlers() {
        console.log("Actions:registerDataClickHandlers");
        $(".btn-refresh").click(function (event) {
            var element = document.getElementById("btnRefresh");
            btnRefresh(element);
        });

        $(".btn-destination-refresh ").click(function (event) {
            var element = document.getElementById("btnDestinationRefresh");
            btnDestinationRefresh(element);
        });
    };

    // Module
    window.dashboardActionsCtrl = {
        requireADLogin: true,
        preProcess: function (html) {

        },
        postProcess: function (html) {
            console.log("dashboardActionsCtrl:postProcess");
            viewHTML = html;
            registerViewClickHandlers();
        },
    };

}());


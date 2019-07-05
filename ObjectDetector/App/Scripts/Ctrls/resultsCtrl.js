(function () {
    // The HTML for this View
    var viewHTML;
    var internalPaginationCtrl = null; 
    var _previousResultData = '';

    function btnRefreshHandler(id) {
        PushPop_Wraper.pushElement(id);
        InvokeWebAPIGeneric('returnAllExperimentResult', 
                                '', 
                                processSourceFileData,
                                'GET',
                                null,
                                AZURE_PYTOHN_COSMOS_WEB_API);
    }

    function processSourceFileData(data) {
        PushPop_Wraper.popElement();  
        $('#dynamicTable').empty();
        if (data) {
            var tp = $.parseJSON(data);
            if (tp) {
                var result = tp["result"];
                if (result && result.length > 0) {
                    _previousResultData = result;
                    internalPaginationCtrl.resetPaginationData(result.length);
                    // Pagination control will call us back to refresh the display
                }
            }
        }
    }


    // This function is predominantely called by the pagination control. 
    function refreshMainPage(_currentSelectedPage, _itemsPerPage, _totalSize) {
        $('#dynamicTable').empty();
        var startIndex = (_currentSelectedPage - 1) * _itemsPerPage;
        var endIndex = startIndex + _itemsPerPage * 1;
        if (endIndex > _totalSize) endIndex = _totalSize;

        for (var i = startIndex; i < endIndex; i++) {
            resultElement = _previousResultData[i];
            var output = [];
            populateDefaultOutput(output);
            var experimentName = resultElement["ExperimentName"];

            var user = 0;
            var openCV = 0;
            var yolo = 0;
            var mobile = 0;
            var azure = 0;
            var google = 0;


            output[2] = experimentName; // Populate the Experiment Value
            var DetectionResult = resultElement["DetectionResult"];
            if (DetectionResult && DetectionResult.length > 0) {
                DetectionResult.forEach(function (detectionResultElement) {
                    var DetectorName = detectionResultElement["DetectorName"];
                    nListLength = 0;
                    var Images = detectionResultElement["Images"];
                    if (Images) {
                        nListLength = Images.length;
                    }

                    switch (DetectorName) {
                        case "openCVDetector":
                            openCV = nListLength;
                            break;
                        case "userDetection":
                            user = nListLength;
                            break;
                        case "yoloDetection":
                            yolo = nListLength;
                            break;
                        case "mobileDetection":
                            mobile = nListLength;
                            break;
                        case "azureDetection":
                            azure = nListLength;
                            break;
                        case "googleDetection":
                            google = nListLength;
                            break;
                    }
                });
            }
            AnalyseResults(user, openCV, yolo, mobile, azure, google, output);
            output.push('</tr>');
            $('#dynamicTable').append(output.join(''));
        }
    }

    function populateDefaultOutput(output) {
        output.push('<tr>');
        output.push('<th class="bg-primary" align="middle">', '{experimentName}', '</th>');
        output.push('<td class="bg-info" align="middle">', '0', '</td>');  // openCV [5]
        output.push('<td class="bg-light" align="middle">', '0', '</td>');  // True - user [8]
        output.push('<td class="bg-light"  align="middle">', '0', '</td>');  // yolo [11]
        output.push('<td class="bg-light" align="middle">', '0', '</td>');  // mobile [14]
        output.push('<td class="bg-light" align="middle">', '0', '</td>');  // azure [17]
        output.push('<td class="bg-light" align="middle">', '0', '</td>');  // Google [20]
        //output.push('<td class="bg-light" align="middle">', '0', '</td>');  // Analysis [23]
        output.push('</tr>');
    }


    function AnalyseResults(user, openCV, yolo, mobile, azure, google, output) {
        var listItems = [
            { id: 'user', value: user, index: 5 },
            { id: 'openCV', value: openCV, index: 8 },
            { id: 'yolo', value: yolo, index: 11 },
            { id: 'mobile', value: mobile, index: 14 },
            { id: 'azure', value: azure, index: 17 },
            { id: 'google', value: google, index: 20 }
        ];

        listItems.forEach(function (element) {
            output[element.index] = element.value;
        });

        // for opencv, 65, 35,
        if (openCV && openCV > 0) {
            user / openCV > .65 ? plugSuccess(7, output) : ((user / openCV) > .35) ? plugWarning(7, output) : plugDanger(7, output);
        }


        if (user && user > 0) {
            for (var i = 2; i < listItems.length; i++) {
                listItems[i].value / user > .65 ? plugSuccess(listItems[i].index - 1, output) : listItems[i].value / user > .35 ? plugWarning(listItems[i].index - 1, output) : plugDanger(listItems[i].index - 1, output)
            }
        }
        else {
            if (user == 0) {
                for (var i = 2; i < listItems.length; i++) {
                    listItems[i].value == 0 ? plugSuccess(listItems[i].index - 1, output) : listItems[i].value > 3 ? plugWarning(listItems[i].index - 1, output) : plugDanger(listItems[i].index - 1, output)
                }
            }
        }
    }

    function plugSuccess(index, output) {
        output[index] = '<td class="bg-success" align="middle">';
    }

    function plugWarning(index, output) {
        output[index] = '<td class="bg-warning" align="middle">';
    }

    function plugDanger(index, output) {
        output[index] = '<td class="bg-danger" align="middle">';
    }

    function PlugInFunction() // called when the body is ready
    {
        console.log("resultsCtrl:PlugInFunction");
        internalPaginationCtrl = paginationCtrl;
        if (internalPaginationCtrl)
        {
            internalPaginationCtrl.setCallBacks(refreshMainPage, btnRefreshHandler, document.getElementById('btnRefresh'))
            internalPaginationCtrl.postProcess(viewHTML);
        }
    }    

    function registerViewClickHandlers() {
        console.log("resultsCtrl:registerDataClickHandlers");
        $(".btn-refresh").click(function (event) {
            console.log(event.target.id);
            var element = document.getElementById(event.target.id);
            btnRefreshHandler(element);
        });
        PlugInFunction()
    }  

    // Module
    window.resultsCtrl = {
        requireADLogin: true,
        preProcess: function (html) {

        },
        postProcess: function (html) {
            console.log("resultsCtrl:postProcess");
            viewHTML = html;
            registerViewClickHandlers();
        },
    };
}());


(function () {

    var sourceShare = '';
    var destinationShare = '';
    var sourceDirectory = '';
    var destinationDirectory = '';
    var fileFilter = '';
    var _experimentName = '';

    var _btnGetUniqueExperimentNames;
    var _btnGetNonProcessedExperiments;
    var _btnCopyFiles;

    // $(function () // called when the body is ready
    // {
    //     console.log("Home Run");
    // });

    function getAllValues() {
        sourceShare = $('#txtSourceShare').val();
        destinationShare = document.getElementById('txtDestinationShare').value;
        sourceDirectory = document.getElementById('txtSourceDirectory').value;
        destinationDirectory = document.getElementById('txtDestinationDirectory').value;
        fileFilter = document.getElementById('txtFileFilter').value;
        _btnGetUniqueExperimentNames = document.getElementById('btnGetUniqueExperimentNames');
        _btnGetNonProcessedExperiments = document.getElementById('btnGetNonProcessedExperiments');
        _btnCopyFiles = document.getElementById('btnCopyFiles');
    }

    function checkParameters() {
        getAllValues();

        if (sourceShare == null || sourceShare.length < 1) {
            alert('Please enter a valid storage sourceShare name!');
            return false;
        }
        if (destinationShare == null || destinationShare.length < 1) {
            alert('Please enter a valid destinationShare Token!');
            return false;
        }

        // check additional parameters
        if (sourceDirectory == null || sourceDirectory.length < 1) {
            alert('Please enter a valid Source Directory name!');
            return false;
        }

        if (destinationDirectory == null || destinationDirectory.length < 1) {
            alert('Please enter a valid Destination Directory name!');
            return false;
        }

        if (fileFilter == null || fileFilter.length < 1) {
            alert('Please enter a valid File Filter name!');
            return false;
        }
        return true;
    }

    function btnCopyFileHandler() {
        console.log("copyFilesAndCreateExperimentCtrl:btnCopyFileHandler");
        var checkOK = checkParameters();
        if (!checkOK)
            return;

        _experimentName = $('#ExperimentCollection option:selected').val();
        if (_experimentName == null || _experimentName.length < 1) {
            alert('Please enter a valid Experiment name!');
            return false;
        }

        var jsonData = {
            _sourceFileShareFolderName: sourceShare, _sourceDirectoryName: sourceDirectory,
            _destinationFileShareFolderName: destinationShare, _destinationDirectoryName: destinationDirectory,
            _ExperimentName: _experimentName, _fileExtensionFilter: fileFilter
        };
        var updatedJson = JSON.stringify(jsonData);
        _btnCopyFiles.setAttribute("class", "btn btn-default");
        InvokeWebAPIGeneric('CopySourceDestination', updatedJson, handlerCopySourceDestination);

    }

    function handlerCopySourceDestination(data) {
        console.log("copyFilesAndCreateExperimentCtrl:handlerCopySourceDestination");
        $("body").css("cursor", "default");
        UpdateTextDivObject(data);
        _btnCopyFiles.setAttribute("class", "btn btn-primary");
    }

    /* ============================================================ */
    function btnGetUniqueExperimentNamesHandler() {
        console.log("copyFilesAndCreateExperimentCtrl:btnGetUniqueExperimentNamesHandler");
        var checkOK = checkParameters();
        if (!checkOK)
            return;

        var jsonData = {
            _sourceFileShareFolderName: sourceShare,
            _sourceDirectoryName: sourceDirectory,
            _fileExtensionFilter: fileFilter
        };
        var updatedJson = JSON.stringify(jsonData);
        _btnGetNonProcessedExperiments.setAttribute("class", "btn btn-default");
        _btnGetUniqueExperimentNames.setAttribute("class", "btn btn-default");
        InvokeWebAPIGeneric('GetAllSourceUniqueExperimentNames', updatedJson, handlerGetUniqueExperimentNames);
    }

    function handlerGetUniqueExperimentNames(response) {
        UpdateTextDivObject(response)
        populateComboBox(response)
        _btnGetNonProcessedExperiments.setAttribute("class", "btn btn-primary");
        _btnGetUniqueExperimentNames.setAttribute("class", "btn btn-primary");
        $("body").css("cursor", "default");        
    }

    function populateComboBox(response) {
        $('#ExperimentCollection').empty();
        var rv = $.parseJSON(response);
        if (rv) {
            var elapsedTime = rv["elapsedTime"];
            $('#lblResult').text(elapsedTime);
            var outerElements = rv["result"];
            for (var i = 0, j = outerElements.length; i < j; i++) {
                var obj = outerElements[i];
                var option = '';
                option += '<option value="' + obj + '">' + obj + '</option>';
                $('#ExperimentCollection').append(option);
            }
        }
    }
    /* ============================================================ */
    function btnGetNonProcessedExperimentsHandler() {
        console.log("copyFilesAndCreateExperimentCtrl:btnGetUniqueExperimentNamesHandler");
        var checkOK = checkParameters();
        if (!checkOK)
            return;

        experimentNames = []

        var options = document.getElementById('ExperimentCollection').options;
        for (var i = 0, j = options.length; i < j; i++) {
            experimentNames.push(options[i].value);
        }

        var jsonData = {
            _destinationFileShareFolderName: destinationShare,
            _destinationDirectoryName: destinationDirectory,
            _experimentNames: experimentNames
        };
        var updatedJson = JSON.stringify(jsonData);
        // Not the best option....
        //TODO:: improve how to pass parameter to handlers.
        _btnGetNonProcessedExperiments.setAttribute("class", "btn btn-default");
        _btnGetUniqueExperimentNames.setAttribute("class", "btn btn-default");
        InvokeWebAPIGeneric('GetAllExperimentsFilesNotCopied', updatedJson, handlerGetUniqueExperimentNames);
    }



    /* ============================================================ */
    function UpdateTextDivObject(displayString) {
        $('#lblResult').text(displayString);
    }


    function registerViewClickHandlers(){
        console.log("copyFilesAndCreateExperimentCtrl:registerDataClickHandlers");
        $(".btn-Get-Unique-ExperimentNames").click(function (event) {
            btnGetUniqueExperimentNamesHandler();
        });

        $(".btn-Get-Non-Processed-Experiments").click(function (event) {
            btnGetNonProcessedExperimentsHandler();
        });

        $(".btn-Copy-File-Handler").click(function (event) {
            btnCopyFileHandler();
        });

        getAllValues();
    }


    window.copyFilesAndCreateExperimentCtrl = {
        requireADLogin: true,
        preProcess: function (html) {
            // This function is only declared as a placeholder for future improvements.
        },
        postProcess: function (html) {
            registerViewClickHandlers();
        },
    };
}());
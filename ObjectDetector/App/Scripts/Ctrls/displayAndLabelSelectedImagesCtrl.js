(function () {


    var _timer;
    var _updatedPresenceTag = [];
    var _currentFileName = '';
    var _startAnimation = 'Start';
    var _stopAnimation = 'Stop';
    var _idUserDetector = "userDetector"; // this is the id to be used for detecting the
    var _collectionID = '';

    function ctrlReady() // called when the body is ready
    {
        console.log("displayAndLabelSelectedImagesCtrl:ctrlReady")
        // one time invocation
        //InstantiateAnimation();
        // Caching elements and values
        var SelectedValue = $('#ExperimentCollection option:selected').val();
        _collectionID = $('#SelectedQuestionAnswerID').val();
        if (SelectedValue != null) {
            console.log(SelectedValue);
            onExperimentCollChanged();
        }
        // setup Event Handlers
        $('#ExperimentCollection').on('change', onExperimentCollChanged);
    }

    function btnStartStopAnimationHandler() {
        console.log('btnStartStopAnimationHandler');
        
        existingText = $('#btnStartStopAnimation').text();
        if (existingText == _startAnimation) {
            var timerValue = $('#txtTimer').val();
            if (!$.isNumeric(timerValue)) {
                timerValue=1000
            }
            _timer = setInterval(TimerHandler, timerValue);
            $("#btnStartStopAnimation").html(_stopAnimation);
            $("#btnStartStopAnimation").attr("class", "btn btn-warning btn-block");
        }
        else {
            clearTimeout(_timer);
            $("#btnStartStopAnimation").html(_startAnimation);
            $("#btnStartStopAnimation").attr("class", "btn btn-success btn-block");
        }
    }

    function TimerHandler() {
        console.log("Timer Invoked");
        // select the next item from the comboBox
        $('#ExperimentCollection option:selected').next().attr('selected', 'selected');
        // this does not invoke the comboBox change handler. need to do that manually
        onExperimentCollChanged();
        checkifLastItemSelectedAndDisableTimer();
    }

    function checkifLastItemSelectedAndDisableTimer() {
        var lastValue = $('#ExperimentCollection option:last-child').val();
        var sv = $('#ExperimentCollection option:selected').val();
        if (lastValue === sv) {
            btnStartStopAnimationHandler();
        }
    }

    function btnAddPresenceTagHandler() {
        console.log('btnAddPresenceTagHandler');
        if (_updatedPresenceTag.indexOf(_currentFileName) >= 0) {
            // ignore. Already exists
        }
        else { _updatedPresenceTag.push(_currentFileName); }
    }

    function btnRemovePresenceTagHandler() {
        console.log('btnRemovePresenceTagHandler');
        var index = _updatedPresenceTag.indexOf(_currentFileName);
        if (index > -1) {
            _updatedPresenceTag.splice(index, 1);
        }
    }

    function btnSavePresenceTagHandler() {
        console.log('btnSavePresenceTagHandler');
        // copy the updatedPresenceTag information to cosmosDB.
        l = _updatedPresenceTag.length;
        var i;
        var objArray=[]; 
        for (i = 0; i < l; i++) {
            var tempObj = { ImageName: _updatedPresenceTag[i], ConfidenceScore: 1.0 };
            objArray.push(tempObj); 
        }

        var dataVal = { id:_idUserDetector, detectedItems: objArray };
        var updatedTagJson = JSON.stringify(dataVal);
        InvokeWebAPI(updatedTagJson); 
    }

    function currentTagValue(sv) {
        if (_updatedPresenceTag.indexOf(sv) >= 0) {
            return true;
        }
        return false;
    }

    function btnRefreshLoadHandler() {
        $("body").css("cursor", "progress");
        var loadLocation = $('#txtLoadLocation').val();
        var ExperimentName = $('#txtLoadFilter').val();

        console.log(ExperimentName);
        console.log(loadLocation); 

        if (!loadLocation || loadLocation.length > 0) {
            if (!ExperimentName || ExperimentName.length > 0) {
                FileNames = GetFileNamesFromAzureStorage(loadLocation, ExperimentName)
            }
        }
        $("body").css("cursor", "default");
    }

    // Combo box changed event handler
    function onExperimentCollChanged() {
        $("body").css("cursor", "progress");
        console.log("onExperimentCollChanged");

        $('#dynamicImage').empty();
        $('#PresenceTag').text("");

        var loadLocation = $('#txtLoadLocation').val();

        if (loadLocation == null || loadLocation.length < 1) { // default
            loadLocation = 'experiment-findthebird/data/outputopencv/';
        }
        
        var sv = $('#ExperimentCollection option:selected').val();

        _currentFileName = sv;
        var currentTag = currentTagValue(sv);

        fileUri = 'https://' + account + '.file.core.windows.net/';

        var imgTag = '<img src ="' + fileUri + loadLocation + sv + sas + '" alt="ALT" height="650" width="800" />';
        
        $('#dynamicImage').append(imgTag);
        $('#PresenceTag').text(currentTag);
        $("body").css("cursor", "default");
    }

    var invocation = new XMLHttpRequest();
    var invocationHistoryText;

    function InvokeWebAPI(dataVal) {
        var body = dataVal;
        var collectionId = $('#selectedCollectionId').val();
        var urlEncodeCollectionId = encodeURIComponent(collectionId);
        var url = 'http://localhost:5001/comsosDB/v1.0/insert_doc_collection?collId=' + urlEncodeCollectionId;

        if (invocation) {
            invocation.open('POST', url, true);
            invocation.setRequestHeader('Content-Type', 'application/json');
            invocation.onreadystatechange = handler;
            invocation.send(body);
        }
        else {
            invocationHistoryText = "No Invocation TookPlace At All";
            UpdateTextDivObject(invocationHistoryText);
        }

    }

    function handler(evtXHR) {
        if (invocation.readyState == 4) {
            if (invocation.status == 200) {
                var response = invocation.responseText;
                //ProcessJsonResponse(response);
                UpdateTextDivObject(response);
            }
            else {
                var AppendedText = "Invocation Errors Occured " + invocation.readyState + " and the status is " + invocation.status;
                UpdateTextDivObject(AppendedText);
            }
        }
        else {

            UpdateTextDivObject("currently the application is at" + invocation.readyState);
        }
    }

    function btnLoadPresenceTagHandler() {
        console.log('btnLoadPresenceTagHandler');
        // in the end ensure that the data is copied to the updatedPresenceTag
        var collectionId = $('#selectedCollectionId').val();
        var urlEncodeCollectionId = encodeURIComponent(collectionId);
        var url = 'http://localhost:5001/comsosDB/v1.0/get_doc_collection?collId=' + urlEncodeCollectionId + '&docId=' + _idUserDetector;


        if (invocation) {
            invocation.open('GET', url, true);
            invocation.setRequestHeader('Content-Type', 'application/json');
            invocation.onreadystatechange = handlerReturnValue;
            invocation.send();
        }
        else {
            invocationHistoryText = "No Invocation TookPlace At All";
            UpdateTextDivObject(invocationHistoryText);
        }
    }

    function handlerReturnValue(evtXHR) {
        if (invocation.readyState == 4) {
            if (invocation.status == 200) {
                var response = invocation.responseText;

                var json = JSON.parse(response.toString());

                var obj = json[0].detectedImages;
                var lengthOfObj = obj.length;
                var i = 0;

                for (i = 0; i < lengthOfObj; i++) {
                    if (_updatedPresenceTag.indexOf(obj[i].ImageName) >= 0) {
                        // ignore. Already exists
                    }
                    else {
                        //UpdateTextDivObject(obj[i].ImageName);
                        _updatedPresenceTag.push(obj[i].ImageName);
                    }
                }
            }
            else {
                var AppendedText = "Invocation Errors Occured " + invocation.readyState + " and the status is " + invocation.status;
                UpdateTextDivObject(AppendedText);
            }
        }
        else {

            //UpdateTextDivObject("currently the application is at" + invocation.readyState);
        }
    }

    function UpdateTextDivObject(displayString) {
        var temp = document.createTextNode(displayString);
        var textDiv = document.getElementById("textDiv");
        textDiv.appendChild(temp);
    }

    var account = 'nkdsvm';
    var sas = '';
    var fileShare = 'linuxraspshare';
    var directory = 'Share';
    var outputFiles = [];


    function GetFileNamesFromAzureStorage(loadLocation, ExperimentName) {
        console.log('GetFileNamesFromAzureStorage')
        var fileService = getFileService();
        if (!fileService)
            return;

        if (fileShare.length < 1) {
            alert('Please select one file share!');
            return;
        }
        $("body").css("cursor", "progress");
        fileService.listFilesAndDirectoriesSegmented(fileShare, directory, null, function (error, results) {
            console.log('listFilesAndDirectoriesSegmented')
            if (error) {
                console.log(error);
                $("body").css("cursor", "default");
            } else {
                outputFiles = []; 
                for (var i = 0, file; file = results.entries.files[i]; i++) {
                    //this could be a big list!!!
                    if (file.name.includes(ExperimentName)) {
                        outputFiles.push(file.name);
                        console.log(file.name);
                    }
                    $("body").css("cursor", "default");
                }

                // interesting, if we do it somewhere else, that code get executed, and the fileService code 
                // gets executed later. 
                // DONT change the location of this code.
                if (outputFiles.length > 0) {
                    $('#ExperimentCollection').empty(); // not convinced this does anything
                    var option = '';
                    for (var i = 0; i < outputFiles.length; i++) {
                        option += '<option value="' + outputFiles[i] + '">' + outputFiles[i] + '</option>';
                    }
                    $('#ExperimentCollection').append(option);
                    console.log('append');
                }
                else {
                    console.log('outputFile length = 0');
                }
            }
        });
    }

    function checkParameters() {
        if (account == null || account.length < 1) {
            alert('Please enter a valid storage account name!');
            return false;
        }
        if (sas == null || sas.length < 1) {
            alert('Please enter a valid SAS Token!');
            return false;
        }

        return true;
    }

    function getFileService() {
        if (!checkParameters())
            return null;

        fileUri = 'https://' + account + '.file.core.windows.net';
        var fileService = AzureStorage.File.createFileServiceWithSas(fileUri, sas).withFilter(new AzureStorage.File.ExponentialRetryPolicyFilter());
        return fileService;
    }

    function plugInHandlers(){
        $('#btnStartStopAnimation').on('click', btnStartStopAnimationHandler);
        $('#btnLoadPresenceTag').on('click', btnLoadPresenceTagHandler);
        $('#btnSavePresenceTag').on('click', btnSavePresenceTagHandler);
        $('#btnAddPresenceTag').on('click', btnAddPresenceTagHandler);
        $('#btnRemovePresenceTag').on('click', btnRemovePresenceTagHandler);
        $('#btnRefreshLoad').on('click', btnRefreshLoadHandler);
    }


    window.displayAndLabelSelectedImagesCtrl = {
        requireADLogin: true,
        preProcess: function (html) {
            // This function is only declared as a placeholder for future improvements.
        },
        postProcess: function (html) {
            // This view does not need to load any data, it is blank.
            plugInHandlers();
        },
    };
}());
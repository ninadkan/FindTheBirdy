(function () {
    

    function readyCtrl() // called when the function is ready
    {
        console.log('reviewAllExperimentsCtrl:readyCtrl')
        // setup Event Handlers
        $('#ExperimentCollection').on('change', onExperimentCollChanged);
        $('#btnLoadCollections').on('click', btnLoadCollections);
    }

    function btnLoadCollections(){
        // Caching elements and values
        $("#btnLoadCollections").attr("class", "btn btn-warning btn-block");
        InvokeWebAPIGeneric('collections', '', populateAllCollections, 'GET', null, AZURE_PYTOHN_COSMOS_WEB_API);
        
    }

    function populateAllCollections(data){
        console.log('reviewAllExperimentsCtrl:populateAllCollections')
        $('#ExperimentCollection').empty();
        $("#btnLoadCollections").attr("class", "btn btn-success btn-block");
        
        if (data) {
            var tp = $.parseJSON(data);
            if (tp) {
                console.log(tp)
                var result = tp["result"];
                if (result && result.length > 0) {
                    var endIndex = result.length;
                    for (var i = 0; i < endIndex; i++) {
                        resultElement = result[i];
                        var option = '';
                        option += '<option value="' + resultElement._self + '">' + resultElement.id + '</option>';
                        $('#ExperimentCollection').append(option);
                    }                 
                }
            }
        }
        
        triggerComboBoxSelection();
    }

    function triggerComboBoxSelection(){
        console.log('reviewAllExperimentsCtrl:triggerComboBoxSelection')
        var SelectedValue = $('#ExperimentCollection option:selected').val()
        if (SelectedValue != null) {
            console.log(SelectedValue)
            onExperimentCollChanged();
        }
        else {
            console.log("reviewAllExperimentsCtrl: Selectd Value is null!")
        }
    }

    // Combo box changed event handler
    function onExperimentCollChanged() {
        console.log("reviewAllExperimentsCtrl:onExperimentCollChanged");
        var SelectedValue = $('#ExperimentCollection option:selected').val();
        PopulateDocumentArea(SelectedValue)
    }

    function PopulateDocumentArea(SelectedValue) {
        console.log("reviewAllExperimentsCtrl:PopulateDocumentArea");
        var dataVal = '{"collectionLink":"' + SelectedValue + '"}';
        console.log(dataVal);
        InvokeWebAPIGeneric('documents', dataVal, handler, 'POST', null, AZURE_PYTOHN_COSMOS_WEB_API )
    }

    function handler(data) {
        console.log("reviewAllExperimentsCtrl:handler");
        ProcessJsonResponse(data); 
        UpdateTextDivObject("Data Loaded"); 
    }

    function UpdateTextDivObject(displayString) {
        console.log("reviewAllExperimentsCtrl:UpdateTextDivObject");
        var temp = document.createTextNode(displayString); 
        var textDiv = document.getElementById("textDiv");
        textDiv.appendChild(temp);
    }

    function ProcessJsonResponse(response) {
        console.log("reviewAllExperimentsCtrl:ProcessJsonResponse");
        if (response != null) {
            $('#dynamicExperimentData').empty();
            var sv = $('#ExperimentCollection option:selected').val();
            var svEncoded = encodeURIComponent(sv);
            //console.log(svEncoded);
            var json = $.parseJSON(response);

            var applyFilter = false;
            var checkForNull = false;
            
            var filterKey = $('#txtFilterKey').val();
            var filterValue = $('#txtFilterValue').val();
            if (filterKey != null && filterKey.trim().length > 0 && filterValue != null && filterValue.trim().length > 0) {
                console.log("Applying filter");
                applyFilter = true;
                if (filterValue.trim() == 'null')
                {
                    console.log("checkFor null is true");
                    checkForNull = true; 
                }
            }


            if (json){
                console.log(json)
                result = json["result"];
                var html = '<tr>';
                $.each(result, function (i, item) {
                    if (selectRecord(item, applyFilter, checkForNull, filterKey, filterValue )){
                       
                    var defId = item["_self"]
                    var defIdEncoded = encodeURIComponent(defId);
                    var idProvider = item["id"]
                    idProvider= encodeURIComponent(idProvider)
                    //var dataVal = $.validator.format('"/Experiment/{0}/{1}/?docId={2}&collectionId={3}"', [idProvider, 0, defIdEncoded, svEncoded]);
                    // ?d=d parameter added for the next search to happen correctly. 
                    var dataVal = $.validator.format('"/#DocumentGetDetails/?d=d&provider={0}&docId={1}&collectionId={2}"', [idProvider, defIdEncoded, svEncoded]);
                    var datavaluesResult = $.validator.format('"ImageDetectionProvider ={0} ; DateTime= {1} ; ExperimentName = {2} ; MessageId = {3}, ElapsedTime = {4}"', [item["ImageDetectionProvider"], item["DateTime"],item["ExperimentName"], item["MessageId]"], item["ElapsedTime"]]);                    
                    var datavalues = $.validator.format('"Experiment Name ={0} ; MessageId= {1} ; Consumer Group = {2} ; DateTime = {3}, Last Offset = {4}"', [item["ConsumerGroup"], item["EventLog"],item["MessageType"], item["PartitionId]"], item["LastOffset"]]);
                    //console.log(dataVal);
                    html += '<tr id="' + defId + '">';
                    html += '<td>' + '<textarea class="col-md-12 form-control nopadding" rows="3" type="text" id="' + defId + '__id">' + item["id"] + '</textarea></td>';
                    html += '<td>' + '<textarea class="col-md-12 form-control nopadding" rows="3" type="text" id="' + defId + '__Self">' + datavaluesResult + '</textarea></td>';
                    html += '<td>' + '<textarea class="col-md-12 form-control nopadding" rows="3" type="text" id="' + defId + '__ElapsedTime">' + datavalues + '</textarea></td>';
                    //html += '<td><input type="button" value="Details" class="btn btn-warning" id="' + defId + '__btnDetails" onclick="showDetails(\'' + sv + '\',\'' + defId + '\',\'' + idProvider + '\')"/></td>';
                    html += '<td><a class="btn btn-xs btn-success" href=' + dataVal + '>Show Details</a></td>';
                    html += '<td><button class="btn btn-xs btn-warning btn-delete-record" id=' + item["id"] + ' onclick=reviewAllExperimentsCtrl.deleteRecord("' + item["id"] + '")>Delete Record</button></td>';
                    html += dataVal;
                    html += '</tr>';
                    }
                });
                html += '</tr>';
                $('#dynamicExperimentData').append(html);
            }
        }
    }

    function selectRecord(item, applyFilter, checkForNull, filterKey, filterValue  ){
        
        var rv = false;
        if (applyFilter){
            if (checkForNull){
                if ((item[filterKey] === null ) || (item[filterKey] === undefined)){
                    console.log("reviewAllExperimentsCtrl:selectRecord: filterKey null");
                    rv = true
                }
            }
            else{
                if (item[filterKey] == filterValue ){
                    console.log("reviewAllExperimentsCtrl:selectRecord: filterKey match value");
                    rv = true
                }
            }
        }
        else{
            console.log("reviewAllExperimentsCtrl:selectRecord: NO MATCH");
            rv = true; 
        }

        return rv
    }

    var _deleteButtonPressedId = "" 

    function deleteRecord(buttonId){
        console.log("reviewAllExperimentsCtrl:deleteRecord");
        _deleteButtonPressedId = "#"+ buttonId
        $(_deleteButtonPressedId).attr("class", "btn btn-warning btn-block");
        //console.log(buttonId)
        var dataVal = '{"id":"' + buttonId + '"}';
        //console.log(dataVal);

        var selectedComboBoxValue = $('#ExperimentCollection option:selected').text().trim();
        if ( selectedComboBoxValue == 'Operations'.trim()){
            InvokeWebAPIGeneric('removeExistingDocumentDict', dataVal, dummyHandler, 'POST', null, AZURE_PYTOHN_COSMOS_WEB_API )
        }
        else if (selectedComboBoxValue == 'ResultsImageDetection'.trim()){
            InvokeWebAPIGeneric('removeExistingDocumentDictStatus', dataVal, dummyHandler, 'POST', null, AZURE_PYTOHN_COSMOS_WEB_API )
        }
        else{ 
            console.log("Bugger all selected");
        }
    }

    function dummyHandler(data)
    {
        console.log("reviewAllExperimentsCtrl:dummyHandler");
        console.log(data)
        $(_deleteButtonPressedId).attr("class", "btn btn-success btn-block");
    }

    function showDetails(CollectionId, Self, Provider) {
        var debugString = "CollectionID Passed = " + CollectionId + " , Self Passed = " + Self + "  , Provider passed = " + Provider;
        UpdateTextDivObject(debugString); 
        // next what? 
    }

    window.reviewAllExperimentsCtrl = {
        requireADLogin: true,
        preProcess: function (html) {
            // This function is only declared as a placeholder for future improvements.
        },
        postProcess: function (html) {
            readyCtrl(); 
        },
        deleteRecord : function(buttonId){
            deleteRecord(buttonId);
        }

    };
}());
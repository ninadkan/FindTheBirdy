(function () {
    
    function populateAllCollections(data){
        console.log('reviewAllExperimentsCtrl:populateAllCollections')
        $('#ExperimentCollection').empty();
        
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
    }

    function readyCtrl() // called when the function is ready
    {
        console.log('reviewAllExperimentsCtrl:readyCtrl')
        // Caching elements and values
        InvokeWebAPIGeneric('collections', '', populateAllCollections, 'GET', null, AZURE_PYTOHN_COSMOS_WEB_API);

        var SelectedValue = $('#ExperimentCollection option:selected').val()
        if (SelectedValue != null) {
            console.log(SelectedValue)
            onExperimentCollChanged();
        }
        else {
            console.log("reviewAllExperimentsCtrl: Selectd Value is null!")
        }
        // setup Event Handlers
        $('#ExperimentCollection').on('change', onExperimentCollChanged);
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
            if (json){
                result = json["result"];
                var html = '<tr>';
                $.each(result, function (i, item) {
                    var defId = item["_self"]
                    var defIdEncoded = encodeURIComponent(defId);
                    var idProvider = item["id"]
                    idProvider= encodeURIComponent(idProvider)
                    //var dataVal = $.validator.format('"/Experiment/{0}/{1}/?docId={2}&collectionId={3}"', [idProvider, 0, defIdEncoded, svEncoded]);
                    // ?d=d parameter added for the next search to happen correctly. 
                    var dataVal = $.validator.format('"/#DocumentGetDetails/?d=d&provider={0}&docId={1}&collectionId={2}"', [idProvider, defIdEncoded, svEncoded]);
                    //console.log(dataVal);
                    html += '<tr id="' + defId + '">';
                    html += '<td>' + '<textarea class="col-md-12 form-control nopadding" rows="2" type="text" id="' + defId + '__id">' + item["id"] + '</textarea></td>';
                    html += '<td>' + '<textarea class="col-md-12 form-control nopadding" rows="2" type="text" id="' + defId + '__Self">' + item["_self"] + '</textarea></td>';
                    html += '<td>' + '<textarea class="col-md-12 form-control nopadding" rows="2" type="text" id="' + defId + '__ElapsedTime">' + item["elapsedTime"] + '</textarea></td>';
                    //html += '<td><input type="button" value="Details" class="btn btn-warning" id="' + defId + '__btnDetails" onclick="showDetails(\'' + sv + '\',\'' + defId + '\',\'' + idProvider + '\')"/></td>';
                    html += '<td><a class="btn btn-xs btn-success" href=' + dataVal + '>Show Details</a></td>';
                    html += dataVal;
                    html += '</tr>';
                });
                html += '</tr>';
                $('#dynamicExperimentData').append(html);
            }
        }
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
    };
}());
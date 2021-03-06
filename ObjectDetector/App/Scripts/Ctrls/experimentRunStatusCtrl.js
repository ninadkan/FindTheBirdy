﻿(function () {
    var viewHTML = null;
    internalPaginationCtrl = null; 
    const _idPrefix = "btn-";
 
    var _time = new Date().getTime();

    function refresh() {
        if (new Date().getTime() - _time >= 5000) {
            console.log('Refresh')
        }
        else {
            console.log('Resetting Refresh timeout')
            setTimeout(refresh, 5000);
        }
    }    

    function btnLoadStatusHandler(obj) {
        console.log("experimentRunStatusCtrl:btnLoadStatusHandler");
        PushPop_Wraper.pushElement(obj.id);
        InvokeWebAPIGeneric(    'returnAllMessageIdGroupedList', 
                                '', 
                                processOperationsStatusData, 
                                'GET', 
                                null, 
                                AZURE_PYTOHN_COSMOS_WEB_API );
    }


    _previousResultData = null
    _keysArray = null


    function processOperationsStatusData(data) {
        console.log("experimentRunStatusCtrl:processOperationsStatusData");
        PushPop_Wraper.popElement();
        //$('#dynamicTable').empty();
        _previousResultData = null;
        _keysArray = null;
        if (data) {
            var tp = $.parseJSON(data);
            if (tp) {
                console.log(tp);
                console.log(Object.keys(tp))
                _keysArray = Object.keys(tp)
                //console.log(tp.length);
                //var result = tp["result"];
                // if (tp && tp.length > 0) {
                _previousResultData = tp;
                internalPaginationCtrl.resetPaginationData(_keysArray.length);
                    // Pagination control will call us back to refresh the display
                // }
            }
        }
    }

    function refreshMainPage(_currentSelectedPage, _itemsPerPage, _totalSize) {
        console.log("experimentRunStatusCtrl:refreshMainPage");
        // pass the current paging offset and indexes.
        var startIndex = (_currentSelectedPage - 1) * _itemsPerPage;
        var endIndex = startIndex + _itemsPerPage * 1;
        if (endIndex > _totalSize) endIndex = _totalSize;

        // Remove everything
        $('#dynamicTable').empty();
        output = [];

        for (var i = startIndex; i < endIndex; i++) {
            var firstRowPopulated = false
            messageId = _keysArray[i];
            //var messageId = Object.keys(resultElement)
            console.log(messageId)
            arrayItems = _previousResultData[messageId]
            for (var k = 0; k < arrayItems.length; k++) {
                innerRecord = arrayItems[k]
                var experimentName = innerRecord["ExperimentName"]
                if (!firstRowPopulated){
                    populateFirstRowOutput(output, messageId, experimentName)
                    firstRowPopulated = true
                }

                var createDateTime = innerRecord["DateTime"];
                console.log(createDateTime)
                //var dateParse = Date.parse(createDateTime)
                if (createDateTime){
                    console.log(createDateTime);
                    var d = new Date(createDateTime)
                    //d.setDate(dateParse);
                    if (d){
                        createDateTime = d.toLocaleDateString() + " " + d.toLocaleTimeString() //+ " " + d.toTimeString();//( d.getDate() + '/'+ d.getMonth()+1) + '/'  +  d.getFullYear() + ':' +d.getHours() + '::' +d.getMinutes() + '::' + d.getSeconds()
                    }
                }
                var id = innerRecord["id"];
                var provider = innerRecord["f_Provider"];
                var experimentName = innerRecord["ExperimentName"]
                if (provider != null) {
                    var elapsedTime = (innerRecord["f_ElapsedTime"] == null) ? 0 : parseFloat(innerRecord["f_ElapsedTime"]).toFixed(2);
                    var result = (innerRecord["f_Result"] == null) ? 0 : innerRecord["f_Result"];
                    var totalRecords = (innerRecord["f_TotalRecords"] == null) ? 0 : innerRecord["f_TotalRecords"];
                    populateOtherRowsOne(output, id, result, totalRecords, elapsedTime, provider, "", id, createDateTime)
                }
                else {
                    var currentCount = innerRecord["CurrentCount"];
                    var maxItems = innerRecord["MaxItems"];
                    var offset_Value = innerRecord["Offset_Value"];
                    var status = innerRecord["Status"];
                    var time = innerRecord["Time"];
                    populateOtherRows(output, id, currentCount, maxItems, offset_Value, status, time, id, createDateTime)
                }
            }
        }
        $('#dynamicTable').append(output.join(''));
    }

    function populateFirstRowOutput(output, messageId, experimentName, invalidData = false) {
        console.log("experimentRunStatusCtrl:populateFirstRowOutput");
        /*
        <tr>
            <td>878ed0da-4f9a-44ea-97be-d95020d268a9</td>
            <td>2018-04-15</td>
            <td colspan="6"><button id="btnLoadExperiments" class="btn btn-danger btn-block" onclick="btnLoadStatusHandler(this)">Delete !</button></td>
        </tr>
        */
        if (!invalidData)
        {
            if (messageId != null) {
                messageId = messageId.trim();
            }

            if (experimentName != null) {
                experimentName = experimentName.trim();
            } 
            output.push('<tr>');
            output.push('<td>');
            output.push(messageId);
            output.push('</td>');
            output.push('<td>');
            output.push(experimentName);
            output.push('</td>');
            output.push('<td colspan="6"><button id="');
            output.push(_idPrefix);
            output.push(messageId);
            output.push('" class="btn btn-danger btn-block"');
            output.push('onclick = "experimentRunStatusCtrl.btnDeleteMessageHandler(event)"')
            output.push('>Delete!</button ></td >');
            output.push('</tr>');
        }
        else
        {
            output.push('<tr>');
            output.push('<td>');
            output.push('Invalid Data');
            output.push('</td>');
            output.push('<td>');
            output.push('Invalid Data');
            output.push('</td>');
            output.push('<td colspan="6">');
            output.push('Invalid Data');
            output.push('</td>');
            output.push('</tr>');
        }
    }



    function populateOtherRowsOne(output, experimentName, result, totalRecords, elapsedTime, provider, time, id, createDateTime) {
        console.log("experimentRunStatusCtrl:populateOtherRows");
        /*
        <tr>
            <td></td>
            <td></td>
            <td>0</td>
            <td>102 , 102</td>
            <td>Error</td>
            <td>f4256f37-2023-4827-a063-390375a8230b</td>
        </tr>
        */
        output.push('<tr>');
        output.push('<td></td>');
        output.push('<td>');
        output.push(experimentName);
        output.push('</td>');
        output.push('<td>');
        output.push(createDateTime);
        output.push('</td>');
        output.push('<td>');
        output.push(elapsedTime);
        output.push('</td>');
        output.push('<td>');
        output.push(result + ";" + totalRecords );
        output.push('</td>');
        output.push('<td>');
        output.push(provider);
        output.push('</td>');
        output.push('</tr>');
    }
    
    

    function populateOtherRows(output, experimentName, currentCount, maxItems, offset_Value, status, time, id, createDateTime) {
        console.log("experimentRunStatusCtrl:populateOtherRows");
        /*
        <tr>
            <td></td>
            <td></td>
            <td>0</td>
            <td>102 , 102</td>
            <td>Error</td>
            <td>f4256f37-2023-4827-a063-390375a8230b</td>
        </tr>
        */
        output.push('<tr>');
        output.push('<td></td>');
        output.push('<td>');
        output.push(experimentName);
        output.push('</td>');
        output.push('<td>');
        output.push(createDateTime);
        output.push('</td>');
        output.push('<td>');
        output.push(offset_Value);
        output.push('</td>');
        output.push('<td>');
        output.push(currentCount + ";" + maxItems );
        output.push('</td>');
        output.push('<td>');
        output.push(status);
        output.push('</td>');
        output.push('</tr>');
    }

    //dynamically added
    function btnDeleteMessageHandler(event) {
        console.log("experimentRunStatusCtrl:btnDeleteMessageHandler");
        var id = event.target.id ;
        var res_id = id.substring(_idPrefix.length);
        console.log(res_id);
        var dataVal = {
            'MessageId': res_id
        };

        var updatedTagJson = JSON.stringify(dataVal);
        console.log(updatedTagJson);
        PushPop_Wraper.pushElement(event.target.id);
        InvokeWebAPIGeneric(   'removeAllDocumentsForSpecificMessageId', 
                                updatedTagJson, 
                                invokeButtonLoadStatusHandler,
                                'POST',
                                null,
                                AZURE_PYTOHN_COSMOS_WEB_API );
    }

    function invokeButtonLoadStatusHandler()
    {
        PushPop_Wraper.popElement();
        console.log("experimentRunStatusCtrl:invokeButtonLoadStatusHandler");
        var element = document.getElementById("btnLoadStatus");
        btnLoadStatusHandler(element);
    }

    function PlugInFunction() // called when the body is ready
    {
        console.log("experimentRunStatusCtrl:PlugInFunction");
        internalPaginationCtrl = paginationCtrl;
        if (internalPaginationCtrl)
        {
            internalPaginationCtrl.setCallBacks(refreshMainPage, btnLoadStatusHandler, document.getElementById('btnLoadStatus'))
            internalPaginationCtrl.postProcess(viewHTML);
        }
    }    

    function registerViewClickHandlers() {
        console.log("experimentRunStatusCtrl:registerDataClickHandlers");
        $(".btn-Load-Status").click(function (event) {
            console.log(event.target.id);
            var element = document.getElementById(event.target.id);
            btnLoadStatusHandler(element);
        });

        $(document.body).bind("mousemove keypress", function (e) {
            _time = new Date().getTime();
        });

        PlugInFunction();
    };

    // window.onload() = function () {
    //     console.log("experimentRunStatusCtrl.onload");
    // };

    window.experimentRunStatusCtrl = {
        requireADLogin: true,
        preProcess: function (html) {
            // This function is only declared as a placeholder for future improvements.
        },
        postProcess: function (html) {
            console.log("experimentRunStatusCtrl:postProcess");
            viewHTML = html;
            registerViewClickHandlers();
        },
        btnDeleteMessageHandler : function(event){
            console.log("experimentRunStatusCtrl:btnDeleteMessageHandler");
            btnDeleteMessageHandler(event);
        }
    };
}());


(function () {

    // The HTML for this View
    var viewHTML;

    function refreshViewData() {

        console.log("documentGetDetailsCtrl:refreshViewData")
        //https://localhost:6420/#ExperimentGetDetails/?507712ed8a&docId=dbs%2FgsUdAA%3D%3D%2Fcolls%2FgsUdAL45uV0%3D%2Fdocs%2FgsUdAL45uV1%2BGQAAAAAAAA%3D%3D%2F&collectionId=dbs%2FgsUdAA%3D%3D%2Fcolls%2FgsUdAL45uV0%3D%2F

        var urlParams = new URLSearchParams(window.location.href);
        //console.log(window.location.href);
        //console.log(urlParams.get('docId')); // true
        //console.log(urlParams.get('provider')); // "edit"
        //console.log(urlParams.get('collectionId')); // "edit"

        var dataVal = '{"docId":"' + encodeURIComponent(urlParams.get('docId')) + '"}';
        var queryURL = 'getDocument' 
        //queryURL += "/?docId=" + encodeURIComponent(urlParams.get('docId'));
        console.log(dataVal);
        //InvokeWebAPIGeneric('documents', dataVal, updateUI, 'POST', null, AZURE_PYTOHN_COSMOS_WEB_API, false )
        // Caching elements and values
        InvokeWebAPIGeneric(queryURL, dataVal, updateUI, 'POST', null, AZURE_PYTOHN_COSMOS_WEB_API, false);
        // var keys = urlParams.keys();
        // for(key of keys) { 
        // console.log(key); 
        // // 1st one is returned as https://localhost:6420/#DocumentGetDetails/?provider
        // // second onwards its fine. 
        // }
        // var entries = urlParams.entries();
        // for(pair of entries) { 
        // console.log(pair[0], pair[1]); 
        // }
    }




    function updateUI(data)
    {
        console.log("documentGetDetailsCtrl:updateUI")
        // Empty Old View Contents
        var $dataContainer = $(".data-container");
        $dataContainer.empty();

        var $html = $(viewHTML);
        var $template = $html.find(".data-container");
        var output = '';

        var json = $.parseJSON(data);
        if (json){
            console.log(json);
            for (var key in json) {
                if (json.hasOwnProperty(key)){
                var $entry = $template;
                $entry.find(".view-data-key").html(key);
                $entry.find(".view-data-value").html(json[key]);
                output += $entry.html();
                }
            }
        }        
        $dataContainer.html(output);
    }

    // Module
    window.documentGetDetailsCtrl = {
        requireADLogin: true,
        preProcess: function (html) {

        },
        postProcess: function (html) {
            viewHTML = html;
            refreshViewData();
        },
    };

}());


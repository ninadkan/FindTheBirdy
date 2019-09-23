function returnAllExperimentList() {
    var collection = getContext().getCollection();
    var experimentNames = [];
    var resultArray = []; 
      
    var sqlGetAllExperimetns = 'SELECT distinct(c.ExperimentName) FROM c';

    var isAccepted = collection.queryDocuments(
            collection.getSelfLink(),
            sqlGetAllExperimetns, function(err, feed, options){
                if (err) {  throw err;}
                    if (!feed || !feed.length) {
                    }
                    else {
                            for (var i =0; i < feed.length; i++){
                                strObject = {"ExperimentName" :feed[i]["ExperimentName"]};
                                experimentNames.push(strObject);
                        }

                        if (experimentNames.length > 0){
                            experimentNames.forEach(function (element){
                                var expName = element["ExperimentName"];
                                var rv = returnAllCount(expName);
                                var obj = {"ExperimentName": expName, "DetectionResult": rv}
                                resultArray.push(obj);
                            });
                        }
 
                        var response = getContext().getResponse();
                        var result = {'result': resultArray};
                        response.setBody(result);
            }
        }
    );
}



function returnAllCount(experimentName) {
    var collection = getContext().getCollection();
    var output = [];
    
    var commonSQL = 'SELECT d.ImageName as {b} FROM c JOIN d IN c.detectedItems WHERE ( c.ExperimentName = \'{experimentName}\' and c.ImageDetectionProvider = \'{a}\')';
    var commmonSQLwExperimentName = commonSQL.replace('{experimentName}', experimentName );
    
 
    // Query documents and take 1st item.
    var a = 'openCVPhotoExtractorClsImpl';
    var b = 'openCVDetector';    
    
    var isAccepted = processSQL(commmonSQLwExperimentName, a,b);
    

    if (isAccepted){
        a = 'yoloBirdImageDetector';
        b = 'yoloDetection';
        isAccepted = processSQL(commmonSQLwExperimentName, a,b);
    }

    if (isAccepted){
        a = 'mobileNetImageDetector';
        b = 'mobileDetection';
        isAccepted = processSQL(commmonSQLwExperimentName, a,b);
    }

    if (isAccepted){
        a = 'azureImageDetector';
        b = 'azureDetection';
        isAccepted = processSQL(commmonSQLwExperimentName, a,b);
    }

    if (isAccepted){
        a = 'googleImageDetector';
        b = 'googleDetection';
        isAccepted = processSQL(commmonSQLwExperimentName, a,b);
    }

    // this string is different
    if (isAccepted){
        a = 'userDetection';
        b = 'userDetection';
        isAccepted = processSQL(commmonSQLwExperimentName, a,b);
    }

        // this string is different
    if (isAccepted){
        a = 'userMainImageDetection';
        b = 'userMainImageDetection';
        isAccepted = processSQL(commmonSQLwExperimentName, a,b);
    }


    if (isAccepted){
        // var response = getContext().getResponse();
        // var result = {'result': output};
        // response.setBody(result);
        return output; 
    }


    function processSQL(commmonSQLwExperimentName, a, b){
        var tempSQL = commmonSQLwExperimentName.replace('{a}', a);
        var finalSQL = tempSQL.replace('{b}', b);
        // Query documents and take 1st item.
        var isAccepted = collection.queryDocuments(
            collection.getSelfLink(),
            finalSQL,
            returnValue
        ); 
        return isAccepted;        
    }

    function returnValue(err, feed, options){
        if (err) { carryOn = false;  throw err;}

        // Check the feed and if empty, set the body to 'no docs found', 
        // else take 1st element from feed
        if (!feed || !feed.length) {
            // var response = getContext().getResponse();
            // response.setBody('no docs found');
        }
        else {
            
            var detectorName = ''

            for (key in feed[0]) {
                detectorName = key;
            }  
            tempObj = [];
            for (var i =0; i < feed.length; i++){
                strObject = {"ImageName" :feed[i][key]};
                tempObj.push(strObject);
            }

            var finalObj = {"DetectorName": key, "Images": tempObj};
            output.push(finalObj);
        }
    }
    if (!isAccepted) throw new Error('The query was not accepted by the server.');
}

function returnAllCount(experimentName) {
    var collection = getContext().getCollection();
    var output = [];
    
    var commonSQL = 'SELECT count(d.ImageName) as {b} FROM c JOIN d IN c.detectedItems WHERE ( c.ExperimentName = \'{experimentName}\' and c.ImageDetectionProvider = \'{a}\')';
    var commmonSQLwExperimentName = commonSQL.replace('{experimentName}', experimentName );
    
 
    // Query documents and take 1st item.
    var a = 'openCVPhotoExtractor';
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


    if (isAccepted){
        var response = getContext().getResponse();
        var result = {'result': output};
        response.setBody(result);
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
            strObject = JSON.stringify(feed[0]);
            output.push(strObject);
        }
    }
    if (!isAccepted) throw new Error('The query was not accepted by the server.');
}
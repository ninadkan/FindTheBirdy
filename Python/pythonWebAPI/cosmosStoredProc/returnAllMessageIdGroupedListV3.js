function returnAllMessageIdGroupedListV3() {
    var collection = getContext().getCollection();
    var resultArray = [];
    var dictMessageIds = {};
    var strMessageIds = '';
      
    //var sqlGetAllMessageIds = 'SELECT distinct(c.MessageId) FROM c';
    // Following SQL will error if ExperimentName and MessageId are not 1:1 related !!!
    var sqlGetAllMessageIdsW_ExpName = 'SELECT c.MessageId, c.ExperimentName FROM c'
    //console.log(sqlGetAllMessageIdsW_ExpName);

    var requestOptions = {
        continuation: continuationToken,
        pageSize: 500
    };

    var isAccepted = collection.queryDocuments(
            collection.getSelfLink(),
            sqlGetAllMessageIdsW_ExpName, function(err, feed, requestOptions){
                if (err) {  throw err;}
                if (!feed || !feed.length) {
                    console.log('feed incorrect')
                }
                else {
                        for (var i =0; i < feed.length; i++){
                            dictMessageIds[feed[i]["MessageId"]]= feed[i]["ExperimentName"];
                        }

                        strMessageIds = "("
                        for(var key in dictMessageIds) {
                            strMessageIds += "\"";
                            strMessageIds +=  key;
                            strMessageIds += "\"";
                            if (i < (feed.length -1)){
                                strMessageIds += ","
                            }
                        }
                        // remove the last ',' 

                        var replacement = '';
                        strMessageIds = strMessageIds.replace(/,([^,]*)$/,replacement+'$1'); //a_b!c
                        console.log(strMessageIds)
                        strMessageIds += ")"
                        console.log(strMessageIds)

                    if (feed.length > 0){
                        // messageId.forEach(function (element){
                        //     var msgId = element["MessageId"];
                        //     var expName = element["ExperimentName"]
                        // var rv = returnAllMessages(strMessageIds);
                        //     var obj = {"MessageId": msgId, "ExperimentName": expName,  "DetectionResult": rv}
                        // resultArray.push(rv);
                        // });

                        var commonSQL = 'SELECT c.ExperimentName, c.Offset_Value, c.CurrentCount as CurrentCount, c.MaxItems as MaxItems, c.Time, c.Status, c.DateTime, c.id, c.ImageDetectionProvider as f_Provider, c.ElapsedTime as f_ElapsedTime, c["result - birdFound"] as f_Result, c["result - totalNumberOfRecords"] as f_TotalRecords FROM c WHERE ( c.MessageId  IN #messageId )';
                        var commmonSQL_w_messageId = commonSQL.replace('#messageId', strMessageIds );
                        console.log(commmonSQL_w_messageId)
                    }

                    var response = getContext().getResponse();
                    var result = {'result': strMessageIds};
                    response.setBody(result);
            }
        }
    );

    if (!isAccepted) throw new Error('The first query was not accepted by the server.');
}



function returnAllMessages(strMessageIds) {
    var collection = getContext().getCollection();
    var output = [];
    
    var commonSQL = 'SELECT c.ExperimentName, c.Offset_Value, c.CurrentCount as CurrentCount, c.MaxItems as MaxItems, c.Time, c.Status, c.DateTime, c.id, c.ImageDetectionProvider as f_Provider, c.ElapsedTime as f_ElapsedTime, c["result - birdFound"] as f_Result, c["result - totalNumberOfRecords"] as f_TotalRecords FROM c WHERE ( c.MessageId  IN #messageId )';
    var commmonSQL_w_messageId = commonSQL.replace('#messageId', strMessageIds );
    console.log(commmonSQL_w_messageId)
    
 
   
    var isAccepted = processSQL(commmonSQL_w_messageId);
    if (isAccepted){
        return output; 
    }    
    

    function processSQL(sqlQuery){
        // Query documents and take 1st item.
        var isAccepted = collection.queryDocuments(
            collection.getSelfLink(),
            sqlQuery,
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
            for (var i =0; i < feed.length; i++){
                output.push(feed[i]);
            }
        }
    }
    if (!isAccepted) throw new Error('The query was not accepted by the server.');
}

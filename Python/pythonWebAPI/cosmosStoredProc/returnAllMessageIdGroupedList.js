function returnAllMessageIdGroupedList() {
    var collection = getContext().getCollection();
    var messageId = [];
    var resultArray = []; 
      
    //var sqlGetAllMessageIds = 'SELECT distinct(c.MessageId) FROM c';
    // Following SQL will error if ExperimentName and MessageId are not 1:1 related !!!
    var sqlGetAllMessageIdsW_ExpName = 'SELECT distinct(c.MessageId), c.ExperimentName FROM c'

    var isAccepted = collection.queryDocuments(
            collection.getSelfLink(),
            sqlGetAllMessageIdsW_ExpName, function(err, feed, options){
                if (err) {  throw err;}
                if (!feed || !feed.length) {
                    }
                else {
                        for (var i =0; i < feed.length; i++){
                            strObject = {"MessageId":feed[i]["MessageId"], "ExperimentName":feed[i]["ExperimentName"]};
                            messageId.push(strObject);
                    }

                    if (messageId.length > 0){
                        messageId.forEach(function (element){
                            var msgId = element["MessageId"];
                            var expName = element["ExperimentName"]
                            var rv = returnAllCount(msgId);
                            var obj = {"MessageId": msgId, "ExperimentName": expName,  "DetectionResult": rv}
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



function returnAllCount(messageId) {
    var collection = getContext().getCollection();
    var output = [];
    
    var commonSQL = 'SELECT c.ExperimentName, c.Offset_Value, c.CurrentCount, c.MaxItems, c.Time, c.Status, c.DateTime, c.id FROM c WHERE ( c.MessageId = \'{messageId}\')';
    var commmonSQL_w_messageId = commonSQL.replace('{messageId}', messageId );
    
 
   
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

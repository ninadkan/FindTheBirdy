function returnAllMessageIdGroupedList() {
    var collection = getContext().getCollection();
    var messageId = [];
    var sqlGetAllMessageIdsW_ExpName = 'SELECT distinct(c.MessageId) FROM c'

    var isAccepted = collection.queryDocuments(
        collection.getSelfLink(),
        sqlGetAllMessageIdsW_ExpName, function(err, feed, options){
            if (err) {  throw err;}
            if (!feed || !feed.length) {
                }
            else {
                    for (var i =0; i < feed.length; i++){
                        strObject = {"MessageId":feed[i]["MessageId"]};
                        messageId.push(strObject);
                    }
            var response = getContext().getResponse();
            var result = {'result': messageId};
            response.setBody(result);
            }
        }
    );
    if (!isAccepted) throw new Error('The query was not accepted by the server.');
}

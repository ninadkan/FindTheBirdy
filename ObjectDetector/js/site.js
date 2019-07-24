// Please see documentation at https://docs.microsoft.com/aspnet/core/client-side/bundling-and-minification
// for details on configuring this project to bundle and minify static web assets.
// Write your JavaScript code.

var PushPop_Wraper = (function () {
    var _lastButton = [];
    var _lastButtonClass = [];

    return {
        pushElement: function (elementID) {
            var element = document.getElementById(elementID);
            if (element) {
                _lastButton.push(element);
                _lastButtonClass.push(element.getAttribute("class"));
                element.setAttribute("class", "btn btn-default");
                $("body").css("cursor", "progress");
            }
        },

        popElement: function () {
            var element = _lastButton.pop();
            var elementClass = _lastButtonClass.pop();
            if (element) {
                element.setAttribute("class", elementClass);
            }
            $("body").css("cursor", "default");
        }
    };
})();

var applicationConfig = {
    clientID: "f527ffe9-2b94-43ee-b087-e82bb7d1e455",
    authority: "https://login.microsoftonline.com/ninadkanthihotmail054.onmicrosoft.com",
    WebAPIScope: ['api://a0f6f329-4be6-425f-9e99-9e781e1efc80/user_impersonation']
};


    //AZURE_BASE_URL = 'http://localhost:5555/'
    AZURE_BASE_URL = 'https://computer-vision-proj.northeurope.cloudapp.azure.com:5555/'
    AZURE_PYTHON_FILE_STORAGE_WEB_API = AZURE_BASE_URL + 'azureStorage/v1.0/';
    AZURE_PYTOHN_COSMOS_WEB_API= AZURE_BASE_URL +'cosmosDB/v1.0/';

    INVOCATIONOBJ = new XMLHttpRequest();
    LAST_CALLBACK = null;
    // function MSAL_WRAPPER() {
    LAST_URL = [];
    LAST_DATA_VALUE = [];
    INVOCATION_METHOD = 'POST';
    RESPONSE_TYPE='text';
    // }

    function acquireTokenPopupAndCallPythonWebAPI() {
        console.log("acquireTokenPopupAndCallPythonWebAPI");
        clientApplication.acquireTokenSilent(applicationConfig.WebAPIScope).then(function (accessToken) {
            callPythonWebAPI(accessToken);
        }, function (error) {
            console.log(error);
            //|| error.indexOf("timeout") !== -1
            // call acquiretokenpopup (popup window) in case of acquiretokensilent failure due to consent or interaction required only
            if (error.indexOf("consent_required") !== -1 || error.indexOf("interaction_required") !== -1 || error.indexOf("login_required") !== -1) {
                clientApplication.acquireTokenPopup(applicationConfig.WebAPIScope).then(function (accessToken) {
                    callPythonWebAPI(accessToken);
                }, function (error) {
                    console.log(error);
                    pushErrorOut(error);
                });
            }
            else if (error.indexOf("timeout") !== -1) {
                pushErrorOut(error);
            }
            else
            {
                pushErrorOut(error);
            }
        });
    }

     function callPythonWebAPI(accessToken) {
        console.log("callPythonWebAPI");
        var theUrl = LAST_URL.pop();
        var dataVal = LAST_DATA_VALUE.pop();

        if (INVOCATIONOBJ) {
            if (INVOCATION_METHOD == 'GET'){
                INVOCATIONOBJ.open('GET', theUrl, true);
            }
            else 
            {
                INVOCATIONOBJ.open('POST', theUrl, true);
            }

            INVOCATIONOBJ.responseType = RESPONSE_TYPE;
            INVOCATIONOBJ.setRequestHeader('Content-Type', 'application/json');
            INVOCATIONOBJ.setRequestHeader('Authorization', 'Bearer ' + accessToken);
            INVOCATIONOBJ.onreadystatechange = handlerGetResult;
            INVOCATIONOBJ.send(dataVal);
        }
        else {
            console.log("No Invocation Object Available!");
        }
    }

    function handlerGetResult(evtxhr) {
        console.log("handlerGetResult");
        if (INVOCATIONOBJ){
            console.log(":readystate =" + INVOCATIONOBJ.readyState)
            if (INVOCATIONOBJ.readyState === 4) {
                
                if (INVOCATIONOBJ.status === 200) {
                    if (INVOCATIONOBJ.response) {
                        console.log("invoking callback status ok");
                        LAST_CALLBACK(INVOCATIONOBJ.status, INVOCATIONOBJ.response);
                    }
                    else {
                        var txt = "invoking callback status ready but no response";
                        LAST_CALLBACK(INVOCATIONOBJ.status, txt);
                    }
                }
                else {
                    console.log("invoking callback status error");
                    var errortxt = "invocation errors occured, state = " + INVOCATIONOBJ.readyState + " and the status is = " + INVOCATIONOBJ.status + " :data = " + INVOCATIONOBJ.response;
                    console.log(errortxt);
                    LAST_CALLBACK(INVOCATIONOBJ.status, errortxt);
                }
            }
            else {
                console.log("handlerGetResult :" + INVOCATIONOBJ.readyState);
            }
        }
        else
        {
            console.log("handlerGetResult: WTF, invocationObject has disappeared. !!!");
        }
    }

    function pushErrorOut(error) {
        console.log("pushErrorOut");
        status = 501;
        LAST_CALLBACK(status, error);
    }
    
    function InvokeWebAPIPostWithData(url, dataval, handler, invocationMethod='POST', responseType=null) {
        console.log("InvokeWebAPIPostWithData");
        LAST_URL.push(url);
        LAST_CALLBACK = handler;
        LAST_DATA_VALUE.push(dataval);
        INVOCATION_METHOD = invocationMethod;
        

        if (responseType)
        {
            RESPONSE_TYPE = responseType;
        }
        else
        {
            RESPONSE_TYPE = 'text';
        }

        if (clientApplication.getUser()) {// avoid duplicate code execution on page load in case of iframe and popup window.
            console.log("User Already Logged In");
            acquireTokenPopupAndCallPythonWebAPI();
        }
        else {
            console.log("Logging the user");
            // does not look like that the user is logged in. Let get that sorted. 
            clientApplication.loginPopup(applicationConfig.WebAPIScope).then(function (idToken) {
                console.log("Obtained Token!");
                acquireTokenPopupAndCallPythonWebAPI();
            }, function (error) {
                console.log(error);
                pushErrorOut(error);
            });
        }
    }


/* ================================= AJAX Call Handlers =============================*/
var _lastFunctionCallBack = null;
var _updateLabel = true;

function InvokeWebAPIGeneric(urlAdd, 
                            dataval, 
                            handler, 
                            invocationType='POST', 
                            responseType=null, 
                            baseURL = AZURE_PYTHON_FILE_STORAGE_WEB_API, 
                            updateLabel=true){
    var url = baseURL + urlAdd; 
    _lastFunctionCallBack = handler;
    _updateLabel = updateLabel;
    if (invocationType == 'GET'){
        InvokeWebAPIGenericGet(url, dataval, responseType);
    }
    else{
        InvokeWebAPIGenericPost(url, dataval, responseType);
    }
}

function InvokeWebAPIGenericGet(url, dataval, responseType) {
    console.log('reviewAllExperimentsCtrl:InvokeWebAPIGenericGet')
    InvokeWebAPIPostWithData(url, dataval, handlerGetAllExperiments, 'GET', responseType);        
}

function InvokeWebAPIGenericPost(url, dataval, responseType) {
    console.log('reviewAllExperimentsCtrl:InvokeWebAPIGenericPost')
    InvokeWebAPIPostWithData(url, dataval, handlerGetAllExperiments, 'POST', responseType);        
}

function handlerGetAllExperiments(state, data){
    console.log('reviewAllExperimentsCtrl:handlerGetAllExperiments')
    if (state == 200) {
        console.log("Actions:status = 200");
        _lastFunctionCallBack(data);
    }
    else
    {
        //TODO:: investigate how we can implement this as a promise
        console.log("Actions:status != 200");
        if (_updateLabel)
        {
            $('#lblResult').html(data); // this may not exist per page 
        }
        else
        {
            //_lastFunctionCallBack(data); // this could potentially cause havoc
        }
    }
}

/* ================================= AJAX Call Handlers =============================*/


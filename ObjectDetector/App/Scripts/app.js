// the AAD application
var clientApplication;

var GlobalWrapper = (function () {

    // Enter Global Config Values & Instantiate MSAL Client application
    window.config = {
        clientID: 'f527ffe9-2b94-43ee-b087-e82bb7d1e455',
        Tenant: 'ninadkanthihotmail054.onmicrosoft.com',
        authority: 'https://login.microsoftonline.com/ninadkanthihotmail054.onmicrosoft.com',
        authCallBackFn: authCallback
    };

    function authCallback(errorDesc, token, error, tokenType) {
        console.log("authCallback");
        //This function is called after loginRedirect and acquireTokenRedirect. Not called with loginPopup
        // msal object is bound to the window object after the constructor is called.
        if (token) {
            console.log(tokenType);
        }
        else {
            log(error + ":" + errorDesc);
        }
    }

    if (!clientApplication)
    {
        clientApplication = new Msal.UserAgentApplication(window.config.clientID, window.config.authority, window.config.authCallBackFn);
    }

    // Get UI jQuery Objects
    var $panel = $(".panel-body");
    var $userDisplay = $(".app-user");
    var $signInButton = $(".app-login");
    var $signOutButton = $(".app-logout");
    var $errorMessage = $(".app-error");
    onSignin(null);
 
    // Handle Navigation Directly to View
    window.onhashchange = function () {
        console.log("window.onhashchange");
        console.log(window.location.hash);
        loadView(stripHash(window.location.hash));
    };
    window.onload = function () {
        console.log("window.onload");
        $(window).trigger("hashchange");
    };

    // Register NavBar Click Handlers
    $signOutButton.click(function () {
        console.log("signOutButton.click");
        clientApplication.logout();
    });

    $signInButton.click(function () {
        console.log("signInButton.click");
        clientApplication.loginPopup().then(onSignin);
    });

    function onSignin(idToken)
    {
        // Check Login Status, Update UI
        console.log("onSignin");
        var user = clientApplication.getUser();
        if (user) {
            $userDisplay.html(user.name);
            $userDisplay.show();
            $signInButton.hide();
            $signOutButton.show();
        } else {
            $userDisplay.empty();
            $userDisplay.hide();
            $signInButton.show();
            $signOutButton.hide();
        }
    }

    // Route View Requests To Appropriate Controller
    function loadCtrl(view) {
        console.log("loadCtrl");
        console.log(view);

        switch (view.toLowerCase()) {
            case 'home':
                return homeCtrl;
            case 'todolist':
                return todoListCtrl;
            case 'userdata':
                return userDataCtrl;
            case 'dashboardactions':
                return dashboardActionsCtrl;
            case 'privacy':
                return privacyCtrl;
            case 'results':
                return resultsCtrl;
            case 'experimentrunstatus':
                return experimentRunStatusCtrl;
            case 'tobeimplemented':
                return tobeImplementedCtrl;
            case 'copyfilesandcreateexperiment':
                return copyFilesAndCreateExperimentCtrl; 
            case 'createviewupdatemask':
                return createViewUpdateMaskCtrl;
            case 'reviewallexperiments':
                return reviewAllExperimentsCtrl;
            case 'documentgetdetails':
                return documentGetDetailsCtrl;
            case 'displayandlabelselectedimages':
                return displayAndLabelSelectedImagesCtrl;
            case 'selectexperimentdisplayimagesandlabel':
                return selectExperimentDisplayImagesAndLabelCtrl;
                
        }
    }

    // Show a View
    function loadView(view) {
        console.log("loadView");

        $errorMessage.empty();
        var ctrl = loadCtrl(view);

        if (!ctrl)
            return;

        // Check if View Requires Authentication
        if (ctrl.requireADLogin && !clientApplication.getUser()) {
            clientApplication.loginPopup().then(onSignin);
            return;
        }

        // Load View HTML
        $.ajax({
            type: "GET",
            url: "App/Views/" + view + '.html',
            dataType: "html",
        }).done(function (html) {

        // Show HTML Skeleton (Without Data)
        var $html = $(html);
        $html.find(".data-container").empty();
        $panel.html($html.html());
        ctrl.postProcess(html);

        }).fail(function () {
            $errorMessage.html('Error loading page.');
        }).always(function () {

        });
    };

    function stripHash(view) {
        console.log("stripHash" + view);
        view = view.substr(view.indexOf('#') + 1);
        // next one is for query strings operations.
        if (view.indexOf('/') > 0)
        {
            view = view.substr(0, view.indexOf('/'));
        }

        console.log(view);
        return view; 
    }

    return{
        displayHomePage : function(){
            loadView('home');
        }
    };
}());



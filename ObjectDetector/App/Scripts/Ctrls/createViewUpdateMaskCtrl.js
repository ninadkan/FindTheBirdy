(function () {


    var _sourceShare = '';
    var _sourceDirectory = '';
    var _imageFileName = '';

    var _btnLoadExperiments;
    var _btnLoadImage; 
    var _btnUpdateMaskTags;
    var _btnSaveMask; 


    function ctrlReady() // called when the body is ready
    {
        console.log("Ready");

         _btnLoadExperiments = document.getElementById('btnLoadExperiments');
         _btnLoadImage = document.getElementById('btnLoadImage');
         _btnUpdateMaskTags = document.getElementById('btnUpdateMaskTags');
         _btnSaveMask = document.getElementById('btnSaveMask');

        $('#ExperimentCollection').on('change', onExperimentCollChanged);
        // ensure that the text displayed is the correct one for our button
        $('#btnUpdateMaskTags').val(_txtStartMaskUpdate);
        getAllNeededValues();
    }

    function checkNecessaryParameters() {
        getAllNeededValues();

        if (_sourceShare == null || _sourceShare.length < 1) {
            alert('Please enter a valid storage sourceShare name!');
            return false;
        }

        // check additional parameters
        if (_sourceDirectory == null || _sourceDirectory.length < 1) {
            alert('Please enter a valid Source Directory name!');
            return false;
        }
        return true;
    }

    function getAllNeededValues() {
        _sourceShare = document.getElementById('txtSourceShare').value;
        _sourceDirectory = document.getElementById('txtSourceDirectory').value;
    }

    // var invocation = new XMLHttpRequest();

    function btnLoadExperimentsHandler() {
        console.log('createViewUpdateMaskCtrl:btnLoadExperimentsHandler')
        $("body").css("cursor", "progress");

        var checkOK = checkNecessaryParameters();
        if (!checkOK)
            return;

        var jsonData = {
            _sourceFileShareFolderName: _sourceShare, _sourceDirectoryName: _sourceDirectory
        };

        var updatedTagJson = JSON.stringify(jsonData);
        _btnLoadExperiments.setAttribute("class", "btn btn-default");
        $("body").css("cursor", "progress");
        InvokeWebAPIGeneric('GetAllExperimentsWithMaskAndImageFile', updatedTagJson, handlerGetAllExperimentsFinal )
    }

    function handlerGetAllExperimentsFinal(data) {
        $("body").css("cursor", "default");
        console.log('createViewUpdateMaskCtrl:handlerGetAllExperimentsFinal')
        populateComboBox(data);
        onExperimentCollChanged();
        _btnLoadExperiments.setAttribute("class", "btn btn-info");
    }

    function populateComboBox(response) {
        console.log('createViewUpdateMaskCtrl:populateComboBox')
        $('#ExperimentCollection').empty();
        var result = $.parseJSON(response);


        $.each(result, function (i, item) {
            var experiment = item['experimentName'];
            var fileName = item['filename'];
            var maskTagsJson = item['maskContent'];

            var maskTags = '['
            for (var i = 0, l = maskTagsJson.length; i < l; i++) {
                maskTags += '[';
                maskTags += maskTagsJson[i];
                maskTags += ']';

                if (i < l - 1) {
                    maskTags += ','
                }
            }
            maskTags += ']';
            var option = '';

            option += '<option value="' + fileName + ";" + maskTags + '">' + experiment + '</option>';
            $('#ExperimentCollection').append(option);
        });
    }

    function btnLoadImageHandler() {
        console.log('createViewUpdateMaskCtrl:btnLoadImageHandler')
        loadImage();
    }

    function onExperimentCollChanged() {
        console.log('createViewUpdateMaskCtrl:onExperimentCollChanged');
        $("body").css("cursor", "progress");

        var comboBoxValue = $('#ExperimentCollection option:selected').val();

        var n = comboBoxValue.indexOf(";");
        var filename = comboBoxValue.substring(0, n);
        var maskTags = comboBoxValue.substring(n + 1);

        // update values
        $('#txtImageFileName').val(filename);
        $('#txtMaskPoints').val(maskTags);

        // Now invoke the web service call to get details about the images.
        // That will call the next web service call automatically
        loadImage();

        $("body").css("cursor", "default");
    }

    var _maskTags = '';
    var _experimentName = '';

    function checkExtraParameters() {
        _imageFileName = $('#txtImageFileName').val();
        if (_imageFileName == null || _imageFileName.length < 1) {
            alert('Please enter a valid image File name!');
            return false;
        }

        _experimentName = $('#ExperimentCollection option:selected').text();

        if (_experimentName == null || _experimentName.length < 1) {
            alert('Please select correct experiment first!');
            return false;
        }

        _maskTags = $('#txtMaskPoints').val();
        if (_maskTags == null || _maskTags.length < 1) {
            alert('Please enter a valid Masks Tags name!');
            return false;
        }

        return true;
    }

    function precheckLoadingImages() {
        var checkOK = checkNecessaryParameters();
        if (!checkOK)
            return false;

        checkOK = checkExtraParameters();
        if (!checkOK)
            return false;
        return true; 
    }

    function loadImage() {
        console.log('createViewUpdateMaskCtrl:loadImage');
        if (!precheckLoadingImages()) return; 
        $("body").css("cursor", "progress");

        var jsonData = {
            _sourceFileShareFolderName: _sourceShare,
            _sourceDirectoryName: _sourceDirectory + "/" + _experimentName,
            _imageFileName: _imageFileName
        };
        var updatedJson = JSON.stringify(jsonData);
        
        _btnLoadImage.setAttribute("class", "btn btn-default");
        InvokeWebAPIImageGeneric('GetRawSourceImage', updatedJson, HandlerGetRawImage);
        $("body").css("cursor", "default");
    }

    function HandlerGetRawImage(data) {
        console.log('createViewUpdateMaskCtrl:HandlerGetRawImage');
        if (!_dynamicImage)
        {
            _dynamicImage = document.getElementById("dynamicImage");
        }
        _dynamicImage.onload = imgOnLoad;
        _dynamicImage.src = window.URL.createObjectURL(data);
        $("body").css("cursor", "default");
    }

    function imgOnLoad() {
        console.log('createViewUpdateMaskCtrl:imgOnLoad');
        _imageHeight = dynamicImage.height;
        _imageWidth = dynamicImage.width;

        var displayString = JSON.stringify({ _imageHeight, _imageWidth });

        $('#lblImageDimensions').text(displayString);
        dynamicImage.style.display = "none"; // this means that although we've loaded the image, we are not going to display it
        initCanvasElements();
        loadMaskedImage();
        $("body").css("cursor", "default");
    }

    function InvokeWebAPIImageGeneric(apiFn, dataval, handler) {
        console.log('createViewUpdateMaskCtrl:InvokeWebAPIImageGeneric');
        $("body").css("cursor", "progress");
        InvokeWebAPIGeneric(apiFn, dataval, handler, 'POST', 'blob');
    }

    function loadMaskedImage() {
        console.log('createViewUpdateMaskCtrl:loadMaskedImage');
        precheckLoadingImages();
        $("body").css("cursor", "progress");

        var jsonData = {
            _sourceFileShareFolderName: _sourceShare,
            _sourceDirectoryName: _sourceDirectory + "/" + _experimentName,
            _imageFileName: _imageFileName,
            _maskTags: _maskTags
        };
        var updatedTagJson = JSON.stringify(jsonData);

        InvokeWebAPIImageGeneric('GetMaskedImage', updatedTagJson, HandlerGetMaskmage);
    }

    function HandlerGetMaskmage(data) {
        console.log('createViewUpdateMaskCtrl:HandlerGetMaskmage');
        $("body").css("cursor", "default");
        var maskImage = document.getElementById('maskImage');
        maskImage.setAttribute("width", _maxWidth);
        maskImage.setAttribute("height", _maxHeight);
        maskImage.src = window.URL.createObjectURL(data);
        _btnLoadImage.setAttribute("class", "btn btn-primary");
        // reset the response type 
    }

    function UpdateTextDivObject(displayString) {
        var temp = document.createTextNode(displayString);
        var textDiv = document.getElementById("lblResult");
        textDiv.appendChild(temp);
    }

    /* ====================== Canvas Handlers =====================================*/
    var _imageHeight;
    var _imageWidth;
    var _rowDim = 50;
    var _maxHeight = 400;
    var _maxWidth = 500;
    var _dynamicImage = document.getElementById("dynamicImage");
    var _imageCanvas = document.getElementById("imageCanvas");
    var _topCanvas = document.getElementById("topCanvas");
    var _sideCanvas = document.getElementById("sideCanvas");
    var _displayWidth;
    var _displayHeight;
    var _scaleWidthFactor = 1.0;
    var _scaleHeightFactor = 1.0;

    function initCanvasElements() {
        drawAllCanvas();
    }

    function drawAllCanvas() {
        drawImageCanvas();
        drawTopCanvas();
        drawSideCanvas();
    }

    function drawImageCanvas() {
        var ctx = imageCanvas.getContext("2d");

        _displayWidth = _imageWidth;
        if (_imageWidth > _maxWidth) {
            _displayWidth = _maxWidth;
            _scaleWidthFactor = _imageWidth / _displayWidth;
        }

        _displayHeight = _imageHeight;
        if (_imageHeight > _maxHeight) {
            _displayHeight = _maxHeight;
            _scaleHeightFactor = _imageHeight / _displayHeight;
        }

        imageCanvas.setAttribute("width", _displayWidth-_rowDim-2);
        imageCanvas.setAttribute("height", _displayHeight);
        ctx.drawImage(dynamicImage, 0, 0, _displayWidth-_rowDim-2, _displayHeight);
    }

    function drawTopCanvas() {
        topCanvas.setAttribute("width", _displayWidth);
        topCanvas.setAttribute("height", _rowDim);
        var topCtx = topCanvas.getContext("2d");
        drawHorizontalRuler(topCtx, _displayWidth, _rowDim);
    }

    function drawSideCanvas() {
        sideCanvas.setAttribute("width", _rowDim);
        sideCanvas.setAttribute("height", _displayHeight);
        var sideCtx = sideCanvas.getContext("2d");
        drawVerticalRuler(sideCtx, _rowDim, _displayHeight);
    }

    function drawHorizontalRuler(ctx, width, height) {
        // draw a line mid way througn to the end
        ctx.clearRect(0, 0, width, height);

        baseheight = height / 2 - 10;

        ctx.moveTo(0, baseheight);
        ctx.lineTo(width, baseheight);
        ctx.stroke();

        makers = getMarkers(width);

        var tickDistance = 96 / 25.4; // hard coded dpi and cms in an inch measurement

        var numTicks = width / tickDistance;

        var y0 = makers[0];
        // Bug that the first one is not displayed correctly
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, baseheight);
        ctx.lineTo(0, baseheight + y0);
        ctx.stroke();
        ctx.beginPath();
        for (var i = 0; i < numTicks; ++i) {
            var x = i * tickDistance;
            var y = makers[i % makers.length];
            ctx.moveTo(x, baseheight);
            ctx.lineTo(x, baseheight + y);
            if (i % (makers.length * 2) == 0) {
                //ctx.fillText(i/makers.length, x + 3, y-20);
                ctx.fillText((i * tickDistance * _scaleWidthFactor).toFixed(0), x + 3, y - 20);
            }
            ctx.stroke();
            ctx.beginPath();
        }
    }

    function drawVerticalRuler(ctx, width, height) {
        // draw a line mid way througn to the end


        ctx.clearRect(0, 0, width, height);

        baseWidth = width / 2;

        ctx.moveTo(baseWidth, 0);
        ctx.lineTo(baseWidth, height);
        ctx.stroke();

        makers = getMarkers(width);

        var tickDistance = 96 / 25.4

        var numTicks = height / tickDistance;

        var y0 = makers[0];
        // Bug that the first one is not displayed correctly
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(baseWidth, 0);
        ctx.lineTo(baseWidth - y0, 0);
        ctx.stroke();
        ctx.beginPath();

        for (var i = 0; i < numTicks; ++i) {
            var x = i * tickDistance;
            var y = makers[i % makers.length];
            ctx.moveTo(baseWidth, x);
            ctx.lineTo(baseWidth - y, x);
            if (i % makers.length == 0) {
                //ctx.fillText(i/makers.length, baseWidth + 3, x);
                if (i == 0) {
                    ctx.fillText((i * tickDistance * _scaleHeightFactor).toFixed(0), baseWidth + 3, x + 10);
                } else {
                    ctx.fillText((i * tickDistance * _scaleHeightFactor).toFixed(0), baseWidth + 3, x);
                }

            }
        }

        ctx.closePath();
        ctx.stroke();


    }

    function getMarkers() {
        markers = [];
        markers = [30, 10, 10, 10, 10, 20, 10, 10, 10, 10];
        return markers;
    }

    function addImageCanvasEventListeners() {
        // Add our event handlers
        // add event listeners
        imageCanvas.addEventListener('click', (e) => {
            const mousePos = {
                x: e.clientX - imageCanvas.offsetTop,
                y: e.clientY - imageCanvas.offsetLeft,
                orgX: e.clientX,
                orgY: e.clientY
            };
            onCanvasclick(mousePos);
        });


        imageCanvas.addEventListener('mousemove', (e) => {

            const mousePos = {
                x: e.clientX - imageCanvas.offsetTop,
                y: e.clientY - imageCanvas.offsetLeft,
                orgX: e.clientX,
                orgY: e.clientY
            };
            e.preventDefault();
            e.stopPropagation();

            onCanvasMouseOver(mousePos);
        });
    }

    var errorRange = 15;

    function onCanvasclick(evt) {
        var r = imageCanvas.getBoundingClientRect();

        if (r.left <= evt.orgX && evt.orgX <= r.left + r.width &&
            r.top <= evt.orgY && evt.orgY <= r.top + r.height) {

            var x = evt.orgX - r.left;
            var y = evt.orgY - r.top;

            x = (x * _scaleWidthFactor).toFixed(0);
            y = (y * _scaleHeightFactor).toFixed(0);

            // Mark edge boundaries
            if (x > _imageWidth - errorRange) x = _imageWidth;
            if (x < errorRange) x = 0;
            if (y > _imageHeight - errorRange) y = _imageHeight;
            if (y < errorRange) y = 0;

            // lets store these values in our array
            var jsonObj = '[' + x.toString() + ',' + y.toString() + ']';
            selectedMaskPoints.push(jsonObj);

            updateMaskDisplay();
        }
    }

    function updateMaskDisplay() {
        if (selectedMaskPoints.length > 0) {
            $('#txtMaskPoints').val('');
            var displayString = '[';

            for (var i = 0; i < selectedMaskPoints.length; i++) {
                displayString += selectedMaskPoints[i];
                if (i < selectedMaskPoints.length - 1) {
                    displayString += ' , ';
                }
            }

            displayString += ']';
            $('#txtMaskPoints').val(displayString);
        }
    }

    function onCanvasMouseOver(evt) {

        var ctx = imageCanvas.getContext("2d");
        var topCtx = topCanvas.getContext("2d");
        var sideCtx = sideCanvas.getContext("2d");

        var height = _imageHeight;
        var width = _imageWidth;

        var r = imageCanvas.getBoundingClientRect();

        if (r.left <= evt.orgX && evt.orgX <= r.left + r.width &&
            r.top <= evt.orgY && evt.orgY <= r.top + r.height) {

            var x = evt.orgX - r.left;
            var y = evt.orgY - r.top;

            ctx.drawImage(dynamicImage, 0, 0, _displayWidth, _displayHeight);

            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 3;

            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x + 1, y + 1);

            ctx.lineWidth = 1;

            ctx.moveTo(x, 0);
            ctx.lineTo(x, y - 5);

            ctx.moveTo(x + 5, y);
            ctx.lineTo(width, y);

            ctx.stroke();

            // horizontal ruler
            drawHorizontalRuler(topCtx, width, _rowDim);
            // previous Style
            var preStyle = sideCtx.strokeStyle;
            topCtx.strokeStyle = '#0f0'; //  ??
            topCtx.beginPath();
            topCtx.moveTo(x, (_rowDim * .2));
            topCtx.lineTo(x, (_rowDim));
            topCtx.fillText((x * _scaleWidthFactor).toFixed(0), x, _rowDim * .8);
            topCtx.stroke();
            // restore style
            topCtx.strokeStyle = preStyle;


            // vertical ruler
            drawVerticalRuler(sideCtx, _rowDim, height);

            // previous Style
            var preStyle = sideCtx.strokeStyle;
            sideCtx.strokeStyle = '#f00'; // red ??
            sideCtx.beginPath();
            sideCtx.moveTo(0, y);
            sideCtx.lineTo((_rowDim * .6), y);
            sideCtx.fillText((y * _scaleHeightFactor).toFixed(0), (_rowDim * .6), y);
            sideCtx.stroke();
            // restore style
            sideCtx.strokeStyle = preStyle;

        }

        //updateResult("onCanvasMouseOver");

    }

    // function drawOuterRectangle(ctx, width, height) {
    //     ctx.moveTo(0, 0);
    //     ctx.lineTo(width, 0);
    //     ctx.stroke();
    //     ctx.moveTo(width, 0);
    //     ctx.lineTo(width, height);
    //     ctx.stroke();
    //     ctx.moveTo(width, height);
    //     ctx.lineTo(0, height);
    //     ctx.stroke();
    //     ctx.moveTo(0, height);
    //     ctx.lineTo(0, 0);
    //     ctx.stroke();
    // }

    var errorRange = 15;
    var _txtStartMaskUpdate = 'Start Mask Update';
    var _txtStopMaskUpdate = 'Stop Mask Update';


    function btnUpdateMaskTagsHandler() {
        console.log('createViewUpdateMaskCtrl:btnUpdateMaskTagsHandler')
        var btnText = $('#btnUpdateMaskTags').text();

        if (_txtStartMaskUpdate.localeCompare(btnText) == 0) {
            $('#btnUpdateMaskTags').prop('class', 'btn btn-outline-success');
            $('#btnUpdateMaskTags').html(_txtStopMaskUpdate);
            $('#txtMaskPoints').val('');
            $('#lblResult').text('Scroll, click mouse over image to update mask poinst');
            $("#txtMaskPoints").prop("readonly", true);
            addImageCanvasEventListeners();
        }
        else {
            removeImageCanvasEventListeners();
            $('#lblResult').text('');
            $("#txtMaskPoints").prop("readonly", false);
            $('#btnUpdateMaskTags').html(_txtStartMaskUpdate);
            $('#btnUpdateMaskTags').prop('class', 'btn btn-success');
        }
    }

    function addImageCanvasEventListeners() {
        imageCanvas.addEventListener('click', onCanvasclick, false);
        imageCanvas.addEventListener('mousemove', onCanvasMouseOver, false);
    }

    function removeImageCanvasEventListeners() {
        imageCanvas.removeEventListener('click', onCanvasclick, false);
        imageCanvas.removeEventListener('mousemove', onCanvasMouseOver, false);
    }

    function onCanvasclick(e) {

        const mousePos = {
            x: e.clientX - imageCanvas.offsetTop,
            y: e.clientY - imageCanvas.offsetLeft,
            orgX: e.clientX,
            orgY: e.clientY
        };

        var evt = mousePos;

        var r = imageCanvas.getBoundingClientRect();

        if (r.left <= evt.orgX && evt.orgX <= r.left + r.width &&
            r.top <= evt.orgY && evt.orgY <= r.top + r.height) {

            var x = evt.orgX - r.left;
            var y = evt.orgY - r.top;

            x = (x * _scaleWidthFactor).toFixed(0);
            y = (y * _scaleHeightFactor).toFixed(0);

            // Mark edge boundaries
            if (x > _imageWidth - errorRange) x = _imageWidth;
            if (x < errorRange) x = 0;
            if (y > _imageHeight - errorRange) y = _imageHeight;
            if (y < errorRange) y = 0;

            // lets store these values in our array
            var newPoint = '[' + x.toString() + ',' + y.toString() + ']';
            updateMaskDisplay(newPoint);
        }
    }

    function updateMaskDisplay(newPoint) {
        maskPointText = $('#txtMaskPoints').val();
        if (maskPointText.trim().length == 0) {
            var startString = '[' + newPoint + ']';
            $('#txtMaskPoints').val(startString);
        }
        else {
            var nCurrentStringLength = maskPointText.length;
            var position = nCurrentStringLength - 1;
            var output = maskPointText.slice(0, position) + "," + newPoint + maskPointText.slice(position);

            $('#txtMaskPoints').val(output);
        }
    }

    function onCanvasMouseOver(e) {
        const mousePos = {
            x: e.clientX - imageCanvas.offsetTop,
            y: e.clientY - imageCanvas.offsetLeft,
            orgX: e.clientX,
            orgY: e.clientY
        };
        e.preventDefault();
        e.stopPropagation();

        var evt = mousePos;

        var ctx = imageCanvas.getContext("2d");
        var topCtx = topCanvas.getContext("2d");
        var sideCtx = sideCanvas.getContext("2d");

        var height = _imageHeight;
        var width = _imageWidth;

        var r = imageCanvas.getBoundingClientRect();

        if (r.left <= evt.orgX && evt.orgX <= r.left + r.width &&
            r.top <= evt.orgY && evt.orgY <= r.top + r.height) {

            var x = evt.orgX - r.left;
            var y = evt.orgY - r.top;



            ctx.drawImage(dynamicImage, 0, 0, _displayWidth, _displayHeight);

            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 3;

            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x + 1, y + 1);

            ctx.lineWidth = 1;

            ctx.moveTo(x, 0);
            ctx.lineTo(x, y - 5);

            ctx.moveTo(x + 5, y);
            ctx.lineTo(width, y);

            ctx.stroke();

            // horizontal ruler
            drawHorizontalRuler(topCtx, width, _rowDim);
            // previous Style
            var preStyle = sideCtx.strokeStyle;
            topCtx.strokeStyle = '#0f0'; //  ??
            topCtx.beginPath();
            topCtx.moveTo(x, (_rowDim * .2));
            topCtx.lineTo(x, (_rowDim));
            topCtx.fillText((x * _scaleWidthFactor).toFixed(0), x, _rowDim * .8);
            topCtx.stroke();
            // restore style
            topCtx.strokeStyle = preStyle;


            // vertical ruler
            drawVerticalRuler(sideCtx, _rowDim, height);

            // previous Style
            var preStyle = sideCtx.strokeStyle;
            sideCtx.strokeStyle = '#f00'; // red ??
            sideCtx.beginPath();
            sideCtx.moveTo(0, y);
            sideCtx.lineTo((_rowDim * .6), y);
            sideCtx.fillText((y * _scaleHeightFactor).toFixed(0), (_rowDim * .6), y);
            sideCtx.stroke();
            // restore style
            sideCtx.strokeStyle = preStyle;

        }

        //updateResult("onCanvasMouseOver");

    }

    function btnSaveMaskHandler() {
        if (!precheckLoadingImages()) return; 
        $("body").css("cursor", "progress");

        var jsonData = {
            _sourceFileShareFolderName: _sourceShare,
            _sourceDirectoryName: _sourceDirectory + "/" + _experimentName,
            _maskTags: _maskTags
        };
        var updatedJson = JSON.stringify(jsonData);
        _btnSaveMask.setAttribute("class", "btn btn-default");
        InvokeWebAPIGeneric('SaveMaskFileData', updatedJson, handlerSaveMaskFile)
    }

    function handlerSaveMaskFile(data) {
        UpdateTextDivObject(data);
            $("body").css("cursor", "default");     
            _btnSaveMask.setAttribute("class", "btn btn-success");
    }

    function PlugInHandlers(){
        ctrlReady();

        // $(document).on('click', '#btnUpdateMaskTags', createViewUpdateMaskCtrl.btnUpdateMaskTagsHandler);
        // $(document).on('click', '#btnSaveMask', createViewUpdateMaskCtrl.btnSaveMaskHandler);
        // $(document).on('click', '#btnLoadExperiments', createViewUpdateMaskCtrl.btnLoadExperimentsHandler);
        // $(document).on('click', '#btnLoadImage', createViewUpdateMaskCtrl.btnLoadImageHandler);

        $('#btnLoadExperiments').on('click', createViewUpdateMaskCtrl.btnLoadExperimentsHandler);
        $('#btnUpdateMaskTags').on('click', createViewUpdateMaskCtrl.btnUpdateMaskTagsHandler);
        $('#btnSaveMask').on('click', createViewUpdateMaskCtrl.btnSaveMaskHandler);
        $('#btnLoadImage').on('click', createViewUpdateMaskCtrl.btnLoadImageHandler);
    }

   

    window.createViewUpdateMaskCtrl = {
        requireADLogin: true,
        preProcess: function (html) {
            // This function is only declared as a placeholder for future improvements.
        },
        postProcess: function (html) {
            // This view does not need to load any data, it is blank.
            PlugInHandlers(); 
        },

        btnUpdateMaskTagsHandler : function(){
            btnUpdateMaskTagsHandler(); 
        },
        
        btnSaveMaskHandler : function(){
            btnSaveMaskHandler(); 
        }, 
        btnLoadExperimentsHandler : function(){
            btnLoadExperimentsHandler(); 
        }, 
        btnLoadImageHandler : function(){
            btnLoadImageHandler(); 
        },
        
        handlerGetAllExperiments : function (state, data){
            handlerGetAllExperiments(state,data); 
        }
    };
}());
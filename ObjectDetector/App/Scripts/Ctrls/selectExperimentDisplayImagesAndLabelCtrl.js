(function () {

    var _dataDirty = false;
    var viewHTML;
    var internalPaginationCtrl = null; 

        /* ================== Tag - unTag Functionality ================== */
        // image gallery
        // init the state from the input
        function initImages() {
            $(".image-checkbox").each(function () {
                if ($(this).find('input[type="checkbox"]').first().attr("checked")) {
                    $(this).addClass('image-checkbox-checked');
                }
                else {
                    $(this).removeClass('image-checkbox-checked');
                }
            });
            _dataDirty = false;
        }

        // Amazing way to resolve dynamic event mapping.
        // courtesy: https://jqueryhouse.com/jquery-on-method-the-issue-of-dynamically-added-elements/
        function initDynamicImages(){
            $('div#dynamicImages').on("click", "label", function (e) {
                $(this).toggleClass('image-checkbox-checked');
                //console.log($(this).attr('id'));
                var $checkbox = $(this).find('input[type="checkbox"]');
                $checkbox.prop("checked", !$checkbox.prop("checked"));
                _dataDirty = true;
                e.preventDefault();
            });
        }

        //// sync the state to the input
        //$(".image-checkbox").on("click", function (e) {
        //    $(this).toggleClass('image-checkbox-checked');
        //    var $checkbox = $(this).find('input[type="checkbox"]');
        //    $checkbox.prop("checked", !$checkbox.prop("checked"))
        //    e.preventDefault();
        //});

        //function btnClickImageHandler(obj) {
        //    $('#3').toggleClass('image-checkbox-checked');
        //    var $checkbox = $('#3').find('input[type="checkbox"]');
        //    $checkbox.prop("checked", !$checkbox.prop("checked"))
        //}

        /* ================== Tag - unTag Functionality ================== */

        /* ================== Ready and Click Handlers  ================== */
        function resetCtrl() // called when the body is ready
        {
            console.log("Ready");
            initImages();
            $('#ExperimentCollection').on('change', onExperimentCollChanged);

            $('#chkSourceDirectory').change(function () {
                if ($(this).is(":checked")) {
                    $("#txtOutputFolder").prop('disabled', true);
                }
                else {
                    $("#txtOutputFolder").prop('disabled', false);
                }
            });
            // /* Pagination stuff */
            // _itemsPerPage = parseInt($('#cmbItemsPerPage option:selected').val(), 10);
            // $('#cmbItemsPerPage').on('change', oncmbItemsPerPageChanged);

            // $(document).keyup(function (e) {
            //     if ($('#idPaginationMiddle')) {
            //         if ($('#idPaginationMiddle').is(":focus") && e.key == "Enter") {
            //             gotoParticularPageIndex(document.getElementById('idPaginationMiddle').value);
            //         }
            //     }
            // });
            // /* Pagination stuff */

            initDynamicImages();
        }

        function btnLoadExperimentsHandler() {
            // disable the checkBox as otherwise it'll just complicate the issue
            // one can load from output folder and can try and save the tag under main folder label. 
            $("#chkSourceDirectory").prop('disabled', true);
            getExperimentNames();
        }

        var _bSaveInvokedBecauseDataDirty = false;
        function onExperimentCollChanged() {
            if (_dataDirty) {
                // challenge is that the before save does first handshake, code carries on executing  and
                // Load of next item is called.
                _bSaveInvokedBecauseDataDirty = true;
                btnSaveTagHandler(document.getElementById('btnLoadTag'));
            }
            else {
                loadNextComboBoxValue();
            }
        }

        function loadNextComboBoxValue() {
            var comboBox = document.getElementById("ExperimentCollection");
            _currentExperimentName = comboBox.options[comboBox.selectedIndex].text.trim();
            if (_currentExperimentName != null || _currentExperimentName.length > 0) {
                btnLoadTagHandler();
            }
        }

        function btnLoadTagHandler() {
            loadTagValues(document.getElementById('btnLoadTag'));
        }

        function btnSaveTagHandler() {
            SaveTagHandler(document.getElementById('btnSaveTag'));
        }
        /* ====================== Ready and Click Handlers  ======================== */
        /* ====================== Loading Tag Values  ============================== */
        var _ID_FOR_USER_DETECTION = 'userDetection';
        var _ID_FOR_MAIN_IMAGE_TAGGING = 'userMainImageDetection'; 
        var _imageLabelTag = [];

        function loadTagValues(obj) {
            // lets first load all the images relavant to the current experiment + output folder.
            // Two variables, _outputImageFiles and _imageLabelTag are populated after successful invocation of this function.
            if (!getImageFileNames()) {
                return false;
            }

            _imageLabelTag = [];
         
            if (!document.getElementById('chkSourceDirectory').checked) {
                _outputFolder = $('#txtOutputFolder').val();
                if (_outputFolder == null || _outputFolder.trim().length < 1) {
                    alert('Please enter a valid output folder name!');
                    return false;
                }
            }

            var dataVal = {
                ImageDetectionProvider: _ID_FOR_USER_DETECTION,
                ExperimentName: _currentExperimentName
            };

            //override if it is something else
            if (document.getElementById('chkSourceDirectory').checked) {
                dataVal = {
                    ImageDetectionProvider: _ID_FOR_MAIN_IMAGE_TAGGING,
                    ExperimentName: _currentExperimentName
                };
            }
 
            
            var updatedTagJson = JSON.stringify(dataVal);
            console.log(updatedTagJson);
            PushPop_Wraper.pushElement(obj.id);
            InvokeWebAPICosmosDb('returnLabelledImageList', updatedTagJson, handlerCosmosDBReturnImageList);
        }

        /* ====================== Loading Tag Values  ============================== */
        /* ====================== Saving  Tag Values  ============================== */
        function SaveTagHandler(obj) {
            //console.log('SaveTagHandler');
            if (!checkExperimentNameParameters())
                return false;
            var objArray = [];
            $(".image-checkbox").each(function () {
                if ($(this).hasClass('image-checkbox-checked')) {
                    var $divElement = $(this).find('div');
                    if ($divElement) {
                        //console.log($divElement.html());
                        var tempObj = { ImageName: $divElement.html(), ConfidenceScore: 1.0 };
                        objArray.push(tempObj)
                    }
                }
            });

            if (objArray.length > 0) {
                var d = new Date();

                var dataVal = {
                    ImageDetectionProvider: _ID_FOR_USER_DETECTION,
                    ExperimentName: _currentExperimentName,
                    DateTime: d.toUTCString(),
                    detectedItems: objArray
                };

                // override
                if (document.getElementById('chkSourceDirectory').checked) {
                    dataVal = {
                        ImageDetectionProvider: _ID_FOR_MAIN_IMAGE_TAGGING,
                        ExperimentName: _currentExperimentName,
                        DateTime: d.toUTCString(),
                        detectedItems: objArray
                    };
                }

                var updatedTagJson = JSON.stringify(dataVal);
                console.log(updatedTagJson);
                PushPop_Wraper.pushElement(obj.id);
                InvokeWebAPICosmosDb('saveLabelledImageList', updatedTagJson, handlerCosmosDBSaveImageList);
            }
            else {
                $('#lblResult').html('No Tags Saved as none were found');
            }
        }

        function handlerCosmosDBSaveImageList(data) {
            PushPop_Wraper.popElement();
            $('#lblResult').html(data);
            if (_bSaveInvokedBecauseDataDirty == true) {
                _bSaveInvokedBecauseDataDirty = false;
                loadNextComboBoxValue();
            }
        }

        /* ====================== Saving  Tag Values  ============================== */
        /* ====================== Web API functinality ============================= */
        
        function InvokeWebAPICosmosDb(urlAdd, dataval, handler) {
            InvokeWebAPIGeneric(urlAdd, 
                                dataval,  
                                handler,
                                'POST',
                                null,
                                AZURE_PYTOHN_COSMOS_WEB_API);            
        }

        function handlerCosmosDBReturnImageList(data) {
            PushPop_Wraper.popElement();
            loadCurrentLabels(data);
        }

        function loadCurrentLabels(response) {
            //console.log('loadCurrentLabels');
            _imageLabelTag = [];
            var tp = $.parseJSON(response);
            if (tp) {
                var result = tp["result"];
                if (result) {
                    for (var j = 0; j < result.length; j++) {           // only one item is contained in the array
                        var detectedItems = result[j]["detectedItems"]; // leap of faith
                        if (detectedItems) {
                            for (var i = 0; i < detectedItems.length; i++) {
                                if (detectedItems[i]) {
                                    _imageLabelTag.push(detectedItems[i]["ImageName"]);
                                }
                            }
                        }
                    }
                }
            }
            // Me just thinks this makes a better solution.
            sleep(500).then(() => {
                loadDynamicImageElements();
            });
        }

        function sleep(time) {
            return new Promise((resolve) => setTimeout(resolve, time));
        }

        /* ====================== Web API functinality ============================= */
        /* ====================== Load images ====================================== */

        function loadDynamicImageElements() {
            // at this time,both the list of images and the cosmosDB list is with us
            // the list that is interesting to us is the _outputImageFiles list
            internalPaginationCtrl.resetPaginationData(_outputImageFiles.length);
            // resetPaginationData();
            // _totalSize = _outputImageFiles.length;
            // _currentSelectedPage = _basePageIndex = 1;
            // generatePaginationDisplay();
            // refreshMainPage();
        }


        function refreshMainPage(_currentSelectedPage, _itemsPerPage, _totalSize) {
            // pass the current paging offset and indexes. 
            var startIndex = (_currentSelectedPage - 1) * _itemsPerPage;
            var endIndex = startIndex + _itemsPerPage * 1;
            if (endIndex > _totalSize) endIndex = _totalSize;

            // Remove everything
            $("#dynamicImages").html("");
            //document.getElementById('dynamicImages').innerHTML = "";
            _innerHtml = [];

            if (_outputImageFiles.length > 0) {
                var currentCount = 0;
                var numberOfImagesPerRow = parseInt($('#cmbItemsPerPage option:selected').val(), 10); 
                var totalNumberOfImagesToBeDisplayed = endIndex - startIndex; 
                var numberOfRowsToBeDisplayed = Math.floor(totalNumberOfImagesToBeDisplayed / numberOfImagesPerRow) + (totalNumberOfImagesToBeDisplayed % numberOfImagesPerRow ? 1 : 0);


                var fileUri = '';

                if (document.getElementById('chkSourceDirectory').checked) {
                    fileUri = 'https://' + _account + '.file.core.windows.net' + "/" + _destinationShare + "/" + _destinationFolder + "/" + _currentExperimentName + "/";
                } else {
                    fileUri = 'https://' + _account + '.file.core.windows.net' + "/" + _destinationShare + "/" + _destinationFolder + "/" + _currentExperimentName + "/" + _outputFolder + "/";
                }

                for (var currentLine = 0; currentLine < numberOfRowsToBeDisplayed; currentLine++) {
                    _innerHtml.push('<div class="row">');
                    for (var index = 0; index < numberOfImagesPerRow;) {
                        if (currentCount < totalNumberOfImagesToBeDisplayed) {
                            var imageFileName = _outputImageFiles[startIndex + currentCount];
                            var imgSrc = fileUri + imageFileName + _sas;
                            console.log(imgSrc);

                            _innerHtml.push('<div class="col-md-');
                            _innerHtml.push(getcolumnWidth(numberOfImagesPerRow));
                            _innerHtml.push(' nopad text-center">');
                            _innerHtml.push('<label class="image-checkbox" id="');
                            _innerHtml.push('imgLabel_' + currentCount.toString());
                            _innerHtml.push('">');
                            //TODO:: height and width should be adjusted depending on the number of items per row. 
                            _innerHtml.push('<img class="img-responsive img-thumbnail" height="200" width="200" src="');
                            _innerHtml.push(imgSrc);
                            _innerHtml.push('">');
                            _innerHtml.push('<div class="bottomleft" id="');
                            _innerHtml.push(imageFileName);
                            _innerHtml.push('">')
                            _innerHtml.push(imageFileName);
                            _innerHtml.push('</div >');

                            if (_imageLabelTag.indexOf(imageFileName) >= 0) {
                                _innerHtml.push('<input type="checkbox" value="" checked />');
                            }
                            else {
                                _innerHtml.push('<input type="checkbox" value="" />');
                            }

                            _innerHtml.push('<i class="fa fa-check hidden"></i>');
                            _innerHtml.push('</label>');
                            _innerHtml.push('</div>');
                            currentCount++;
                            index++;
                        }
                        else {
                            // we are at the last line and don't have all the images to fill
                            break;
                        }
                    }
                    _innerHtml.push('</div>');
                }

                $("#dynamicImages").html(_innerHtml.join(''));
                initImages();
            }
        }

        function getcolumnWidth(numberOfImagesPerRow) {
            var rv = "2";

            switch (numberOfImagesPerRow) {
                case 1:
                    rv = "8";
                    break;
                case 2:
                    rv = "6";
                    break;
                case 3:
                    rv = "4";
                    break;
                case 4:
                    rv = "3";
                    break;
                case 5,6:
                    rv = "2";
                    break;
                case 6:
                    rv = "2"
                    break;
                case 7,8,9,10:
                    rv = "1"
                    break;
                default:
                    rv = "2";
                    break;
            }
            return rv;
        }

        /* ======================= Load images ====================================== */
        /* ======================= Azure File Share Functions ======================= */

        var _account = '';
        var _sas = '';
        var _outputImageFiles = [];
        var _experimentNames = [];
        var _destinationShare = '';
        var _destinationFolder = '';
        var _currentExperimentName = '';
        var _outputFolder = '';
        var _fileExtension = ".jpg";


        function getExperimentNames() {
            var fileService = getFileService();
            if (!fileService)
                return;

            if (!checkExperimentNameParameters())
                return null;

            $("body").css("cursor", "progress");
            fileService.listFilesAndDirectoriesSegmented(_destinationShare, _destinationFolder, null, function (error, results) {
                if (error) {
                    console.log(error);
                    $("body").css("cursor", "default");
                } else {
                    _experimentNames = [];
                    $('#ExperimentCollection').empty();
                    _outputImageFiles = [];
                    if (results.entries.directories.length < 1) {
                        console.log('no directories returned !!! length = 0');
                    }
                    else {

                        for (var i = 0, file; file = results.entries.directories[i]; i++) {
                            _experimentNames.push(file.name);
                            var option = '';
                            option += '<option value="' + file.name + '">' + file.name + '</option>';
                            $('#ExperimentCollection').append(option);
                        }
                        onExperimentCollChanged();
                    }
                }
            });
            $("body").css("cursor", "default");
        }

        function checkExperimentNameParameters() {
            _destinationShare = $('#txtDestinationShare').val();

            if (_destinationShare == null || _destinationShare.trim().length < 1) {
                alert('Please enter a valid storage destination share name!');
                return false;
            }

            _destinationFolder = $('#txtDestinationDirectory').val();

            if (_destinationFolder == null || _destinationFolder.trim().length < 1) {
                alert('Please enter a valid destination folder name!');
                return false;
            }
            return true;
        }

        function getImageFileNames() {
            var fileService = getFileService();
            if (!fileService)
                return false;

            if (!checkExperimentNameParameters())
                return false;

            if (!checkImageFilesParameters())
                return false;


            $("body").css("cursor", "progress");

            var df = ''; 
            if (document.getElementById('chkSourceDirectory').checked) {
                df = _destinationFolder + "/" + _currentExperimentName ;
            } else {
                df =  _destinationFolder + "/" + _currentExperimentName + "/" + _outputFolder;
            }
            
            //console.log(df);
            fileService.listFilesAndDirectoriesSegmented(_destinationShare, df, null, function (error, results) {
                //console.log('getImageFileNames');
                if (error) {
                    console.log(error);
                } else {
                    _outputImageFiles = [];
                    if (results.entries.files.length < 1) {
                        console.log('no files returned !!! length = 0');
                    }
                    else {
                        for (var i = 0, file; file = results.entries.files[i]; i++) {
                            if (file.name.includes(_fileExtension)) {
                                _outputImageFiles.push(file.name);
                                //console.log(file.name);
                            }
                        }
                    }
                }
            });
            $("body").css("cursor", "default");
            return true;
        }

        function checkImageFilesParameters() {
            if (!document.getElementById('chkSourceDirectory').checked) {
                _outputFolder = $('#txtOutputFolder').val();
                if (_outputFolder == null || _outputFolder.trim().length < 1) {
                    alert('Please enter a valid output folder name!');
                    return false;
                }
            }

            var comboBox = document.getElementById("ExperimentCollection");
            _currentExperimentName = comboBox.options[comboBox.selectedIndex].text.trim();

            if (_currentExperimentName == null || _currentExperimentName.length < 1) {
                alert('Please select a valid experiment name!');
                return false;
            }
            return true;
        }

        function getFileService() {
            if (!checkFileShareParameters())
                return null;

            fileUri = 'https://' + _account + '.file.core.windows.net';
            var fileService = AzureStorage.File.createFileServiceWithSas(fileUri, _sas).withFilter(new AzureStorage.File.ExponentialRetryPolicyFilter());
            return fileService;
        }

        function checkFileShareParameters() {
            _account = $('#txtAzureFileShareAccount').val();

            if (_account == null || _account.trim().length < 1) {
                alert('Please enter a valid storage account name!');
                return false;
            }

            _sas = $('#txtSAS').val();

            if (_sas == null || _sas.trim().length < 1) {
                alert('Please enter a valid SAS Token!');
                return false;
            }
            return true;
        }
/* ======================= Azure File Share Functions ======================= */

    function plugInHandlers(){
        console.log('selectExperimentDisplayImagesAndLabelCtrl:plugInHandlers')
        $('#btnLoadExperiments').on('click', btnLoadExperimentsHandler);
        $('#btnLoadTag').on('click', btnLoadTagHandler);
        $('#btnSaveTag').on('click', btnSaveTagHandler);

        internalPaginationCtrl = paginationCtrl;
        if (internalPaginationCtrl)
        {
            internalPaginationCtrl.setCallBacks(refreshMainPage, btnLoadExperimentsHandler, null)
            internalPaginationCtrl.postProcess(viewHTML);
        }

        resetCtrl(); 
    }

    window.selectExperimentDisplayImagesAndLabelCtrl = {
        requireADLogin: true,
        preProcess: function (html) {
            // This function is only declared as a placeholder for future improvements.
        },
        postProcess: function (html) {
            // This view does not need to load any data, it is blank.
            viewHTML = html;
            plugInHandlers();
        },
        // btnLoadExperimentsHandler : function(){
        //     btnLoadExperimentsHandler();
        //}
    };
}());
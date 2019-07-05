(function () {

    var viewHTML;
    var refreshMainPageCallBack = null;
    var resetPageCallBack = null;
    var resetPageParameter = null;     
    var _itemsPerPage = 16; 
    var _totalSize = 0;
    var _currentSelectedPage = 1;
    var _totalNumberOfPages = 0;
    var _idOfCurrentActivePaginationElement = 'idPaginationOne'; //starting bit
    var _basePageIndex = 1; // Page being displayed by the button at position 1
    var _CutOfForNavigationItems = 6;

    function setCallBacks(MainPageCallBack, resetCallBack, resetParameter){
        console.log("paginationCtrl:setCallBacks");
        refreshMainPageCallBack = MainPageCallBack;
        resetPageCallBack = resetCallBack;
        resetPageParameter = resetPageParameter
    }

    function resetPaginationData() {
        console.log("paginationCtrl:resetPaginationData");
        $('#divPagination').empty();
        _totalSize = 0;
        _currentSelectedPage = -1;
        _itemsPerPage = parseInt($('#cmbItemsPerPage option:selected').text(), 10);
        _idOfCurrentActivePaginationElement = 'idPaginationOne';
        $('#lblRowText').html("");
    }

    function oncmbItemsPerPageChanged() {
        console.log("paginationCtrl:oncmbItemsPerPageChanged");
        _itemsPerPage = parseInt($('#cmbItemsPerPage option:selected').val(), 10);
        if (resetPageCallBack){
            console.log("paginationCtrl:TRUE");
            if (resetPageParameter){
                resetPageCallBack(resetPageParameter);
            }
            else{
                resetPageCallBack();
            }

        }
        else{
            console.log("Error: resetPageCallBack not set")
        }
    }    

    var _paginationConstants = [
        { id: "idPaginationStart", value: -2, displayString: "|<<", CurrentPageNumber: 1 },
        { id: "idPaginationPrev", value: -1, displayString: "<<", CurrentPageNumber: 1 },
        { id: "idPaginationOne", value: 1, displayString: "1", CurrentPageNumber: 1 },
        { id: "idPaginationTwo", value: 2, displayString: "2", CurrentPageNumber: 1 },
        { id: "idPaginationThree", value: 3, displayString: "3", CurrentPageNumber: 1 },
        { id: "idPaginationMiddle", value: -3, displayString: "...", CurrentPageNumber: -1 },
        { id: "idPaginationFour", value: 4, displayString: "4", CurrentPageNumber: 1 },
        { id: "idPaginationFive", value: 5, displayString: "5", CurrentPageNumber: 1 },
        { id: "idPaginationSix", value: 6, displayString: "6", CurrentPageNumber: 1 },
        { id: "idPaginationNext", value: -4, displayString: ">>", CurrentPageNumber: 1 },
        { id: "idPaginationEnd", value: -5, displayString: ">>|", CurrentPageNumber: 1 }
    ];

    var listofPaginationButtons = [ { id: _paginationConstants[2].id }, { id: _paginationConstants[3].id }, { id: _paginationConstants[4].id },
    { id: _paginationConstants[6].id }, { id: _paginationConstants[7].id }, { id: _paginationConstants[8].id }];    

    function getTotalNumberOfPages() {
        return Math.floor(_totalSize / _itemsPerPage) + (_totalSize % _itemsPerPage ? 1 : 0);
    }

    function reDrawPaginationData() {
        //console.log("paginationCtrl:reDrawPaginationData");
        _totalNumberOfPages = getTotalNumberOfPages();
        // initially everything is switched off
        // following array acts as flag to indicate which buttons to display and whcih not to 
        // if set to 1, that control is displayed, otherwise no
        var displayControllerArray = [];
        for (var i = 0; i < _paginationConstants.length; i++) {
            displayControllerArray.push(0);
        }
        // pagination construct is needed only for certain cases when number of pages > 5
        boolInvokeDraw = true;
        document.getElementById("divPagination").setAttribute("class", "pagination");
        console.log("paginationCtrl:reDrawPaginationData = Total number of Pages = " + _totalNumberOfPages);
        switch (_totalNumberOfPages) {
            case 0:
                document.getElementById("divPagination").setAttribute("class", "");
                boolInvokeDraw = false; // pagination is not displayd in this case, this is done by resetting class info
                break;
            case 1:
                displayControllerArray[2] = 1; // 1
                break;
            case 2:
                displayControllerArray[2] = displayControllerArray[3] = 1; // 1,2
                break;
            case 3:
                displayControllerArray[2] = displayControllerArray[3] = displayControllerArray[4] = 1; // 1,2,3
                break;
            case 4:
                displayControllerArray[2] = displayControllerArray[3] = 1; // 1,2,3,4
                displayControllerArray[4] = displayControllerArray[6] = 1;
                break;
            case 5:
                displayControllerArray[2] = displayControllerArray[3] = 1; // 1,2,3,4,5
                displayControllerArray[4] = displayControllerArray[6] = 1;
                displayControllerArray[7] = 1;
                break;
            case 6:
                displayControllerArray[2] = displayControllerArray[3] = 1; // 1,2,3,4,5,6
                displayControllerArray[4] = displayControllerArray[6] = 1;
                displayControllerArray[7] = displayControllerArray[8] = 1;
                break;
            default:
                // assuming > 6
                for (var i = 0; i < _paginationConstants.length; i++) {
                    displayControllerArray[i] = 1; // |<, <<, 1,2,3,__, 4,5,6 >, >>!
                }
                break;
        }
        if (boolInvokeDraw) {
            // we are showing some part of pagination. 
            drawPaginationLayout(displayControllerArray);
        }
    }

    // dynamically construct the pagination buttons. 
    function drawPaginationLayout(displayControllerArray) {
        //console.log("paginationCtrl:drawPaginationLayout");
        $('#divPagination').empty();
        paginationTags = [];
        var i = 0;
        var boolPlugInMiddleHandler = false;

        _paginationConstants.forEach(function (element) {
            if (displayControllerArray[i]) {
                if (element.CurrentPageNumber != 1) {
                    //var aTag = '<input style="border: 0px; border-image: none; width: 0px; height: 0px; visibility: hidden; position: absolute;" id="';

                    var aTag = '<input size="1" id="';
                    aTag += element.id;
                    aTag += '"/>'

                    // aTag += element.id;
                    // aTag += '"/>'
                    paginationTags.push(aTag);
                    boolPlugInMiddleHandler = true;
                }
                else {
                        var aTag = '<a href="#" onclick="paginationCtrl.handlerPaginationClick(';
                        aTag += element.value;
                        aTag += ')"';
                        aTag += ' CurrentPageNumber=';
                        aTag += getCurrentElementNumber(element.id);
                        aTag += '';
                        aTag += ' id="'
                        aTag += element.id;
                        aTag += '">'
                        aTag += element.displayString;
                        aTag += '</a>';
                        paginationTags.push(aTag);
                        console.log("paginationCtrl:drawPaginationLayout::plugging in dynamic values =" + element.value);
                        //$('#'+element.id).click(handlerPaginationClick(element.value));
                        //$('#'+element.id).on('click', function(){handlerPaginationClick(element.value);});
                }
            }
            i++;
        });
        $('#divPagination').append(paginationTags.join(''));

        if (boolPlugInMiddleHandler){        
            $(document).keyup(function (e) {
                if ($('#idPaginationMiddle')) {
                    if ($('#idPaginationMiddle').is(":focus") && e.key == "Enter") {
                        gotoParticularPageIndex(document.getElementById('idPaginationMiddle').value);
                    }
                }
            });
        }


        // resize the input element. 
        //if (_totalNumberOfPages > _CutOfForNavigationItems) {
        //    var idOfElement = getIdOfClickedNavigationButton(_currentSelectedPage);
        //    if (idOfElement) {
        //        document.getElementById(idOfElement).setAttribute("class", "active");
        //    }
        //    //document.getElementById('idPaginationMiddle').setAttribute("onclick", "return false");
        //}

        if (_idOfCurrentActivePaginationElement) {
            var element = document.getElementById(_idOfCurrentActivePaginationElement);
            if (element) {
                element.setAttribute("class", "active");
            }
        }
        // update the CurrentPageNumber of all the pagination items
    }

    function getCurrentElementNumber(elementId) {
        console.log("paginationCtrl:getCurrentElementNumber");
        var rv = _basePageIndex;
        switch (elementId) {
            case "idPaginationOne":
                rv = _basePageIndex;
                break;
            case "idPaginationTwo":
                rv = _basePageIndex + 1;
                break;
            case "idPaginationThree":
                rv = _basePageIndex + 2;
                break;
            case "idPaginationFour":
                rv = _basePageIndex + 3;
                break;
            case "idPaginationFive":
                rv = _basePageIndex + 4;
                break;
            case "idPaginationSix":
                rv = _basePageIndex + 5;
                break;
            default:
                rv = -1;
        }
        return rv;
    }

    function gotoParticularPageIndex(pageIndex) {
        console.log("paginationCtrl:gotoParticularPageIndex");
        var valuePassed = parseInt(pageIndex);
        if (Number.isInteger(valuePassed)) {
            if (valuePassed <= _totalNumberOfPages && valuePassed >= 1) {
                _currentSelectedPage = valuePassed;
                if (_currentSelectedPage + _CutOfForNavigationItems - 1 <= _totalNumberOfPages) {
                    _basePageIndex = _currentSelectedPage;

                }
                else {
                    _basePageIndex = _totalNumberOfPages - _CutOfForNavigationItems + 1;
                }
                $('#lblRowText').html("");
                refreshMainPageCallBack(_currentSelectedPage, _itemsPerPage, _totalSize);
                updatePaginationDisplayAndInternalAttribute();
            }
        }
    }

    function handlerPaginationClick(valuePassed) {
        console.log("paginationCtrl:handlerPaginationClick, value passed ="+ valuePassed);
        $('#lblRowText').html("");
        moveCurrentSelectedPage(valuePassed);
        refreshMainPageCallBack(_currentSelectedPage, _itemsPerPage, _totalSize);
        updatePaginationDisplayAndInternalAttribute();
    }

    function moveCurrentSelectedPage(valuePassed) {
        console.log("paginationCtrl:moveCurrentSelectedPage");
        // valuePassed is the _paginationConstants value

        switch (valuePassed) {
            case -1: //prev
                // need to shift everything by one.
                moveRight(1);
                break;
            case -2: // start
                _basePageIndex = _currentSelectedPage = 1;
                break;
            case -3: // ...
                break;
            case -4: // next
                moveLeft(1);
                break;
            case -5: // End
                _currentSelectedPage = _totalNumberOfPages;
                _basePageIndex = _currentSelectedPage - _CutOfForNavigationItems + 1;
                break;
            default:
                var idOfElement = getIdOfClickedNavigationButton(valuePassed);
                if (idOfElement) {
                    var vpElement = document.getElementById(idOfElement).getAttribute("CurrentPageNumber");
                    if (vpElement > 0) {
                        _currentSelectedPage = parseInt(vpElement, 10);
                    }
                }
                break;
        }
        // update the display numbers of all pagination items
    }

    function moveLeft(noOfSteps) {
        // as if >> button is pressed
        var brv = false;
        if (_basePageIndex + _CutOfForNavigationItems - 1 + noOfSteps <= _totalNumberOfPages) {
            _basePageIndex += noOfSteps;
        }
        if (_currentSelectedPage + noOfSteps <= _totalNumberOfPages) { _currentSelectedPage += noOfSteps; brv = true; }
        return brv;
    }

    function moveRight(noOfSteps) {
        var rv = false;
        if (_basePageIndex >= 1 + noOfSteps) _basePageIndex -= noOfSteps;
        if (_currentSelectedPage >= 1 + noOfSteps) {
            _currentSelectedPage -= noOfSteps; rv = true;
        }
        return rv
    }

    function updatePaginationDisplayAndInternalAttribute() {
        console.log("paginationCtrl:updatePaginationDisplayAndInternalAttribute");
        if (_totalNumberOfPages > _CutOfForNavigationItems) {
            var index = 0;
            listofPaginationButtons.forEach(function (element) {
                document.getElementById(element.id).innerHTML = _basePageIndex + index;
                document.getElementById(element.id).setAttribute("CurrentPageNumber", _basePageIndex + index);
                if (_basePageIndex + index == _currentSelectedPage) {
                    document.getElementById(_idOfCurrentActivePaginationElement).setAttribute("class", "");
                    document.getElementById(element.id).setAttribute("class", "active");
                    _idOfCurrentActivePaginationElement = element.id;
                    $('#lblRowText').html("Row " + _currentSelectedPage + " of " + _totalNumberOfPages);
                }
                index++;
            });
        }
        else {
            listofPaginationButtons.forEach(function (element) {
                var element = document.getElementById(element.id);
                if (element) {
                    var vpElement = element.getAttribute("CurrentPageNumber");

                    if (vpElement) {
                        vpElement = parseInt(vpElement, 10);
                        if (vpElement > 0) {
                            if (parseInt(vpElement) == _currentSelectedPage) {
                                document.getElementById(_idOfCurrentActivePaginationElement).setAttribute("class", "");
                                document.getElementById(element.id).setAttribute("class", "active");
                                _idOfCurrentActivePaginationElement = element.id;
                                $('#lblRowText').html("Row " + _currentSelectedPage + " of " + _totalNumberOfPages);
                            }
                        }
                    }
                }
            });
        }
    }

    function getIdOfClickedNavigationButton(valuePassed) {
        console.log("paginationCtrl:getIdOfClickedNavigationButton");
        var idPassed = ''
        for (var i = 0, l = _paginationConstants.length; i < l;) {
            if (_paginationConstants[i].value == valuePassed) {
                idPassed = _paginationConstants[i].id;
                break;
            }
            else i++;
        }
        return idPassed;
    }

    /* ====================== Pagination handler  ============================== */
    function populatePlaceHolderUI() {
        console.log("paginationCtrl:populatePlaceHolderUI");

        var $placeHolderTop = $(".pagination-top-placeholder");
        var $placeHolderBottomVal = $(".pagination-bottom-placeholder");        

        var $html = $(viewHTML);

        if ($placeHolderTop)
        {
            console.log("paginationCtrl:populatePlaceHolderUI:placeHolderTop");
            $placeHolderTop.empty();
            _innerHtml = []
            _innerHtml.push('<div class="row">');
            _innerHtml.push('<div class="col-md-6">');
            _innerHtml.push('<p></p>')
            _innerHtml.push('</div>');
            _innerHtml.push('<div class="col-md-3">');
            _innerHtml.push('<label id="lblRowText"></label>');
            _innerHtml.push('</div>');
            _innerHtml.push('<div class="col-md-3">');
            _innerHtml.push('<label>');
            _innerHtml.push('Show');
            _innerHtml.push('<select name="cmbItemsPerPage" id="cmbItemsPerPage">');
            _innerHtml.push('<option value="2">2</option>');
            _innerHtml.push('<option value="3">3</option>');
            _innerHtml.push('<option value="5">5</option>');
            _innerHtml.push('<option value="10" selected="selected">10</option>');
            _innerHtml.push('<option value="25">25</option>');
            _innerHtml.push('<option value="50">50</option>');
            _innerHtml.push('</select>');
            _innerHtml.push('items per page');
            _innerHtml.push('</label>');
            _innerHtml.push('</div>');
            _innerHtml.push('</div>');
            $placeHolderTop.html(_innerHtml.join(''));
            if ($placeHolderBottomVal)
            {
                console.log("paginationCtrl:populatePlaceHolderUI:placeHolderBottomVal");
                $placeHolderBottomVal.empty();
                _innerBottomHtml = []
                _innerBottomHtml.push('<div class="container">');
                _innerBottomHtml.push('<div class="row">');
                _innerBottomHtml.push('<div class="col-md-6">');
                _innerBottomHtml.push('<p></p>')
                _innerBottomHtml.push('</div>');
                _innerBottomHtml.push('</div>');
                _innerBottomHtml.push('<div id="divPagination"></div>');
                _innerBottomHtml.push('</div>');
                $placeHolderBottomVal.html(_innerBottomHtml.join(''))
            }
        }
    }  

    function plugInHandlers()
    {
        console.log("paginationCtrl:plugInHandlers");
        $('#cmbItemsPerPage').on('change', oncmbItemsPerPageChanged);
    }

    /* ====================== Pagination handler  ============================== */
    window.paginationCtrl = {
        preProcess: function (html) {
            // This function is only declared as a placeholder for future improvements.
        },
        postProcess: function (html) {
            console.log("paginationCtrl:postProcess");
            viewHTML = html;
            populatePlaceHolderUI();
            plugInHandlers();
        },
        resetPaginationData : function(length) {
            console.log("paginationCtrl:resetPaginationData, length="+ length);
            resetPaginationData();
            _totalSize = length;
            _currentSelectedPage = _basePageIndex = 1;
            reDrawPaginationData();
            refreshMainPageCallBack(_currentSelectedPage, _itemsPerPage, _totalSize);       
        },
        setCallBacks : function(MainPageCallBack, ComboBoxChangeCallBack, ButtonId){
            setCallBacks(MainPageCallBack, ComboBoxChangeCallBack, ButtonId);
        },
        handlerPaginationClick: function(valuePassed){
            handlerPaginationClick(valuePassed);
        }
    };
}());
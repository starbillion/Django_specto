var stocksJson = [];
var DatatableDataLocalDemo = function () {
    var e = function () {

        /* var e=JSON.parse('[
         {
         "RecordID":1,
         "OrderID":"54473-251",
         "ShipCountry":"GT",
         "ShipCity":"San Pedro Ayampuc",
         "ShipName":"Sanford-Halvorson",
         "ShipAddress":"897 Magdeline Park",
         "CompanyEmail":"sgormally0@dot.gov",
         "CompanyAgent":"Shandra Gormally",
         "CompanyName":"Eichmann, Upton and Homenick",
         "Currency":"GTQ",
         "Notes":"sit amet cursus id turpis integer aliquet massa id lobortis convallis",
         "Department":"Computers",
         "Website":"house.gov",
         "Latitude":"14.78667",
         "Longitude":"-90.45111",
         "ShipDate":"5/21/2016",
         "TimeZone":"America/Guatemala",
         "Status":1,
         "Type":2
         }
         */
        // var e = JSON.parse(srcJson);
        var data = stocksJson;
        a = $(".stocksDataTable").mDatatable({
            data: {
                type: "local", source: data, pageSize: 10
            }
            , layout: {
                theme: "default", class: "", scroll: 1, height: 500, footer: !1
            }
            , sortable: !0, pagination: !0, search: {
                input: $("#generalSearch")
            }
            , columns: [
                {
                    field: "id",
                    title: "#",
                    width: 50,
                    sortable: 1,
                    selector: !1,
                    textAlign: "center"
                }
                , {
                    field: "symbol", title: "Symbol"
                }
                , {
                    field: "name", title: "Name", responsive: {
                        visible: "lg"
                    }
                }
                , {
                    field: "sector", title: "Sector", width: 100
                }
                , {
                    field: "industry", title: "Industry", responsive: {
                        visible: "lg"
                    }
                }
                , {
                    field: "Status", title: "Status", template: function (e) {
                        var a = {
                            true: {
                                title: "Active", class: " m-badge--success"
                            }
                            , false: {
                                title: "In-Active", class: " m-badge--danger"
                            }
                            /*1: {
                             title: "Pending", class: "m-badge--brand"
                             }
                             , 2: {
                             title: "Delivered", class: " m-badge--metal"
                             }
                             , 3: {
                             title: "Canceled", class: " m-badge--primary"
                             }
                             , 4: {
                             title: "Success", class: " m-badge--success"
                             }
                             , 5: {
                             title: "Info", class: " m-badge--info"
                             }
                             , 6: {
                             title: "Danger", class: " m-badge--danger"
                             }
                             , 7: {
                             title: "Warning", class: " m-badge--warning"
                             }*/
                        };
                        return '<span data-raw-json data-id="' + e.pk + '" data-symbol="' + e.symbol + '" data-name="' + e.name + '" data-sector="' + e.sector + '" data-industry="' + e.industry + '" data-status="' + e.status + '" class="m-badge ' + a[e.status].class + ' m-badge--wide">' + a[e.status].title + "</span>"
                    }
                }
                , {
                    field: "Actions",
                    width: 110,
                    title: "Actions",
                    sortable: !1,
                    overflow: "visible",
                    template: function (e) {
                        return '\t\t\t\t\t\t<div class="dropdown ' + (e.getDatatable().getPageSize() - e.getIndex() <= 4 ? "dropup" : "") + '">\t\t\t\t\t\t\t' +
                            '<a href="#" class="btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" data-toggle="dropdown"><i class="la la-ellipsis-h"></i></a>\t\t\t\t\t\t\t' +
                            '<div class="dropdown-menu dropdown-menu-right">\t\t\t\t\t\t\t' +
                            '<a class="dropdown-item" href="/secret-admin/stock/' + e.symbol + '" id="viewDetails"><i class="la la-leaf"></i> View Details</a>\t\t\t\t\t\t\t' +
                            '<a class="dropdown-item" href="#" data-edit-modal><i class="la la-edit"></i> Edit Details</a>\t\t\t\t\t\t\t' +
                            '<a class="dropdown-item" href="#" data-manage-subscriptions-modal><i class="la la-edit"></i> Manage Subscription</a>\t\t\t\t\t\t\t' +
                            '<a class="dropdown-item" href="#" data-subscriptions-history-modal><i class="la la-info-circle"></i> Subscription Plan History</a>\t\t\t\t\t\t\t' +
                            '<a class="dropdown-item" href="#" data-delete-record><i class="la la-remove"></i> Remove</a>' +
                            '</div>\t\t\t\t\t\t' +
                            '</div>\t\t\t\t\t\t\t\t\t\t\t'
                    }
                }
            ]
        }),
            i = a.getDataSourceQuery();
        $("#m_form_status").on("change", function () {
                console.log("Searching status", Boolean($(this).val()));
                a.search(Boolean($(this).val()), "Status")
            }
        ).val(void 0 !== i.Status ? i.Status : ""),

            $("#m_form_type").on("change", function () {
                    a.search($(this).val(), "Sector")
                }
            ).val(void 0 !== i.Type ? i.Type : ""),
            $("#m_form_status, #m_form_type").selectpicker()

    };

    return {
        init: function () {
            e()

            // Add action listener to edit details modal
            jQuery("body").on("click", "a[data-edit-modal]", function (e) {

                var $targetModal = jQuery('#myModal');
                var $rawDataElem = $(this).parents('tr').find('[data-raw-json]');
                var $modalForm = jQuery($targetModal).find('div.modal-body form');

                jQuery($modalForm).find("input[name='symbol']").val(jQuery($rawDataElem).data('symbol'));
                jQuery($modalForm).find("input[name='name']").val(jQuery($rawDataElem).data('name'));
                jQuery($modalForm).find("input[name='sector']").val(jQuery($rawDataElem).data('sector'));
                jQuery($modalForm).find("input[name='industry']").val(jQuery($rawDataElem).data('industry'));
                jQuery($modalForm).find("input[name='id']").val(jQuery($rawDataElem).data('id'));
                if ($rawDataElem.data("status"))
                    jQuery($modalForm).find("input[name='status'][data-name='active']").attr('checked', 'checked');
                else
                    jQuery($modalForm).find("input[name='status'][data-name='inactive']").attr('checked', 'checked');

                jQuery($targetModal).modal({
                    backdrop: false
                });
            });

            // Manage Subscriptions modal
            jQuery("body").on("click", "a[data-manage-subscriptions-modal]", function (e) {

                var $targetModal = jQuery('#manageSubscriptionsModal');
                var $rawDataElem = $(this).parents('tr').find('[data-raw-json]');
                var $modalForm = jQuery($targetModal).find('div.modal-body form');
                console.log("Changing stock hidden to", jQuery($rawDataElem).data('symbol'));
                jQuery($targetModal).find("input[name='stock']").val(jQuery($rawDataElem).data('symbol'));

                AjaxCall(URL_ADMIN_GET_STOCK_SUBSCRIPTIONS, "get", {'symbol': jQuery($rawDataElem).data('symbol')}, successPopulateForm, errorPopulateForm);

                jQuery($targetModal).modal({
                    backdrop: false
                });
            });

            // SHow subscription history modal
            jQuery("body").on("click", "[data-subscriptions-history-modal]", function (e) {
                var clickedStock = jQuery(this).parents('tr.m-datatable__row').find('td[data-field="symbol"] span').html();
                console.log(clickedStock + "is clicked stock");
                var $targetModal = jQuery('#subscriptionsHistoryModal');
                var $rawDataElem = $(this).parents('tr').find('[data-raw-json]');
                // var $modalForm = jQuery($targetModal).find('div.modal-body form');

                // jQuery($targetModal).find("input[name='stock']").val(jQuery($rawDataElem).data('symbol'));
                jQuery("span[data-stock-selected]").html(clickedStock);
                AjaxCall(URL_ADMIN_GET_STOCK_SUBSCRIPTIONS, "get", {
                    'symbol': jQuery($rawDataElem).data('symbol'),
                    'removed': true
                }, successPopulateStockSubsHistoryTable, errorPopulateStockSubsHistoryTable, {'$targetModal': $targetModal});
            });

            // Add action listener to edit details modal
            jQuery("body").on("click", "a[data-delete-record]", function (e) {

                if (!confirm("Are you sure to remove this record?"))
                    return;

                // var $targetModal = jQuery('#myModal');
                var $rawDataElem = $(this).parents('tr').find('[data-raw-json]');

                window.location.href = URL_REMOVE_STOCK + "?id=" + jQuery($rawDataElem).data('id');
            });

            // Add action listener to edit details modal
            jQuery("body").on("click", "a#viewDetails", function (e) {
                var $rawDataElem = $(this).parents('tr').find('[data-raw-json]');
                window.location.href = BASE_DIR + "/admin/stock/" + jQuery($rawDataElem).data('symbol');
            });

            // Populate a new plan form
            jQuery("body").on("click", "[data-trigger='add-plan']", function (e) {

                // Find index of the last form
                var lastFormElem = jQuery('.form-block').last().find(".m-radio-list input[type='radio']");
                if (lastFormElem.length == 0) {
                    index = 0;
                } else {
                    index = $(lastFormElem).attr('name').match(/\d+/)[0]
                    index = parseInt(index) + 1;
                }
                var $rawDataElem = $(this).parents('tr').find('[data-raw-json]');

                var $planFormWrap = jQuery(".plan-form-wrap");
                var html = '<div class="col-sm-6 form-block">';
                html += '<div class="form-group m-form__group">';
                html += '<label for="example_input_full_name">';
                html += 'Plan Duration <sup>(In months)</sup>';
                html += '</label>';
                html += '<input type="text" name="plan_duration[]" class="form-control m-input" placeholder="Example 1">';
                html += '</div>';


                html += '<div class="form-group m-form__group">';
                html += '<label for="example_input_full_name">';
                html += 'Valid Until Date';
                html += '</label>';
                html += '<input type="text" name="valid_until[]" class="form-control m-input datetimepicker" placeholder="Example 2018-11-23">';
                html += '</div>';


                // html += '<div class="form-group m-form__group">';
                // html += '<label for="example_input_full_name">';
                // html += 'Max month Purchasable <sup>(In months)</sup>';
                // html += '</label>';
                // html += '<input type="text" name="max_months_purchasable[]" class="form-control m-input" placeholder="Example 1">';
                // html += '</div>';


                html += '<div class="form-group m-form__group">';
                html += '<label >Price</label>';
                html += '<input type="text" name="price[]" class="form-control m-input" placeholder="Price(In USD). Example 1">';
                html += '</div>';
                html += '<div class="m-form__group form-group">';
                html += '<label for="">Status</label>';
                html += '<div class="m-radio-list">';
                html += '<label class="m-radio">';
                html += '<input type="radio" name="status[' + index + ']" data-name="active" value="1">';
                html += 'Active<span></span></label>';
                html += '<label class="m-radio">';
                html += '<input type="radio" name="status[' + index + ']" data-name="inactive" value="0">Inactive<span></span>';
                html += '</label>';
                html += '</div>';
                html += '<span class="m-form__help">';
                html += 'Enable/Disable the plan.';
                html += '</span>';
                html += '<div>';
                html += '<button data-trigger="remove-plan" type="button" class="btn btn-danger m-btn">Remove Plan</button>';
                html += '<input type="hidden" name="ids[]" value="">';
                html += '</div>';
                html += '</div>';
                html += '<hr>';
                html += '</div>';
                $planFormWrap.append(html);
                $('.datetimepicker').datepicker({
                    format: 'yyyy-mm-dd',
                });
            });

            // Populate a new plan form
            jQuery("body").on("click", "[data-trigger='remove-plan']", function (e) {
                var $this = $(this);
                AjaxCall(URL_ADMIN_REMOVE_SUBSCRIPTION_PLAN, "post", {'plan_id': $(this).attr('data-id')}, removePlanSuccessCallback, removePlanErrorCallback, {'$this': $this});
            });

            // Hack checkbox to make only one clickable out of the 2 available
            jQuery("body").on("click", ".m-radio-list input[type='radio']", function (e) {
                // e.preventDefault();
                console.log($(this));
                $(this).parents(".m-radio-list").find("input[type='radio']").removeAttr("checked");
                $(this).attr("checked", true);
            });
        }
    }
}
();

jQuery(document).ready(function () {
        var srcJson = jQuery('#stocks-data').data('raw-data');
        console.log("Src json", srcJson);
        for (var i = 0; i < srcJson.length; i++) {
            var field = srcJson[i].fields;
            field['id'] = i + 1;
            field['pk'] = srcJson[i].pk;
            stocksJson.push(field);
        }
        DatatableDataLocalDemo.init();

    }
);

function successPopulateStockSubsHistoryTable(data, extraData) {
    // console.log("Data returned==", data);
    stockSubsHistoryData = $.parseJSON(data.stock_subscriptions);
    DatatableDataSubscriptionHistory.init();
    jQuery(extraData.$targetModal).modal({
        backdrop: false
    });
}

function errorPopulateStockSubsHistoryTable(data, extraData) {
    console.log("Error", data);
    stockSubsHistoryData = [];
    DatatableDataSubscriptionHistory.init();
    jQuery(extraData.$targetModal).modal({
        backdrop: false
    });
}

function successPopulateForm(data) {

    var $planFormWrap = jQuery(".plan-form-wrap");
    $planFormWrap.empty();
    stock_subs = $.parseJSON(data.stock_subscriptions);

    if (stock_subs.length == 0) {
        var html = '<div class="col-sm-12" style="border-bottom: 1px solid #e9ecef; padding-bottom: 30px;"><div class="form-group m-form__group"><label for="example_input_full_name">Max month of subscription</label>' +
            '<input type="text" name="max_months_purchasable" class="form-control m-input" value=""></div></div>';

    }
    else {
        var html = '<div class="col-sm-12" style="border-bottom: 1px solid #e9ecef; padding-bottom: 30px;"><div class="form-group m-form__group"><label for="example_input_full_name">Max month of subscription</label>' +
            '<input type="text" name="max_months_purchasable" class="form-control m-input" value="' + stock_subs[0].fields.max_months_purchasable + '"></div></div>';

    }

    for (var i = 0; i < stock_subs.length; i++) {
        console.log(stock_subs[i]);
        html += '<div class="col-sm-6 form-block">';
        html += '<div class="form-group m-form__group">';
        html += '<label for="example_input_full_name">';
        html += 'Plan Duration <sup>(In months)</sup>';
        html += '</label>';
        html += '<input type="text" name="plan_duration[]" class="form-control m-input" placeholder="Example 1" value="' + stock_subs[i].fields.plan_duration + '">';
        html += '</div>';


        html += '<div class="form-group m-form__group">';
        html += '<label for="example_input_full_name">';
        html += 'Valid Until Date';
        html += '</label>';
        console.log(typeof(stock_subs[i].fields.valid_until), stock_subs[i].fields.valid_until);
        if (stock_subs[i].fields.valid_until == null) {
            html += '<input type="text" name="valid_until[]" class="form-control m-input datetimepicker" placeholder="Example 2018-11-23" value="">';
        }
        else {
            html += '<input type="text" name="valid_until[]" class="form-control m-input datetimepicker"  placeholder="Example 1" value="' + stock_subs[i].fields.valid_until + '">';
        }
        html += '</div>';


        // html += '<div class="form-group m-form__group">';
        // html += '<label for="example_input_full_name">';
        // html += 'Max month of subscription';
        // html += '</label>';
        // if (stock_subs[i].fields.max_months_purchasable == null){
        //     html += '<input type="text" name="max_months_purchasable[]" class="form-control m-input" placeholder="Example 1" value="">';
        // }
        // else{
        // html += '<input type="text" name="max_months_purchasable[]" class="form-control m-input" placeholder="Example 1" value="' + stock_subs[i].fields.max_months_purchasable + '">';
        // }
        // html += '</div>';

        html += '<div class="form-group m-form__group">';
        html += '<label >Price</label>';
        html += '<input type="text" name="price[]" class="form-control m-input" placeholder="Price(In USD). Example 1" value="' + stock_subs[i].fields.price + '">';
        html += '</div>';
        html += '<div class="m-form__group form-group">';
        html += '<label for="">Status</label>';
        html += '<div class="m-radio-list">';
        html += '<label class="m-radio">';
        html += '<input type="radio" name="status[' + i + ']" data-name="active" value="1"';
        if (stock_subs[i].fields.status)
            html += ' checked ';
        html += '>';
        html += 'Active<span></span></label>';
        html += '<label class="m-radio">';
        html += '<input type="radio" name="status[' + i + ']" data-name="inactive" value="0"';
        if (!stock_subs[i].fields.status)
            html += ' checked ';
        html += '>Inactive<span></span>';
        html += '</label>';
        html += '</div>';
        html += '<span class="m-form__help">';
        html += 'Enable/Disable the plan.';
        html += '</span>';
        html += '<div>';
        html += '<button data-trigger="remove-plan" type="button" data-id="' + stock_subs[i].pk + '" class="btn btn-danger m-btn">Remove Plan</button>';
        html += '<input type="hidden" name="ids[]" value="' + stock_subs[i].pk + '">';
        html += '</div>';
        html += '</div>';
        html += '<hr>';
        html += '</div>';

        $('.datetimepicker').datepicker({
            format: 'yyyy-mm-dd',
        });
    }
    $planFormWrap.append(html);
}

function errorPopulateForm(data) {
    console.log('error!!! populating form', data)
}

function updateStockFormSuccessCallback(s) {
    console.log('success', s)
    $.growl.notice({message: "Plan updated successfully!"});
    $("#close_subscription_modal").click();
}

function updateStockFormErrorCallback(e) {
    console.log('error=>', e);
    $.growl.notice({message: "Error updating plan!"});
}

function removePlanSuccessCallback(e, extraData) {
    console.log("success", e, extraData);
    $(extraData.$this).parents('.form-block').hide('slow');
    $(extraData.$this).parents('.form-block').remove();
    $.growl.notice({message: "Plan removed successfully!"});
}

function removePlanErrorCallback(e, $this) {
    console.log("error", e, $this);
    $.growl.error({message: "Error trying to remove plan!"});
}

jQuery('body').on("submit", "#updateStockForm", function (e) {
    e.preventDefault();
    formData = $(this).serializeArray();
    console.log(formData);
    for (var i = 0; i < formData.length; i++) {
        if (formData[i].name.startsWith("status")) {
            // update the name to remove index from the array
            formData[i].name = "status[]";
        }
    }
    AjaxCall($(this).attr("action"), "post", formData, updateStockFormSuccessCallback, updateStockFormErrorCallback);
});
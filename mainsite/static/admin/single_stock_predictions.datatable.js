var stocksJson = [];
var DatatableDataLocalDemo=function() {
    var e=function() {

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
        var e = stocksJson;
        console.log("++++", a);
        var a=$(".m_datatable").mDatatable( {
            data: {
                type: "local", source: e, pageSize: 10
            }
            , layout: {
                theme: "default", class: "", scroll: !1, height: 450, footer: !1
            }
            , sortable:!0, pagination:!0, search: {
                input: $("#generalSearch")
            }
            , columns:[ 
            	{
                	field: "id", 
                	title: "#", 
                	width: 50, 
                	sortable: !1, 
                	selector: !1, 
                	textAlign: "center"
	            }
	            // , {
	            //     field: "symbol", title: "Symbol"
	            // }
	            , {
	                field:"prediction_date", title:"Prediction Date", responsive: {
	                }
	            }
	            , {
	                field: "high", title: "High", width: 100
	            }
	            , {
	                field: "low", title: "Low", width: 100
	            }
	            , {
	                field: "close", title: "Close", width: 100
	            }
	            , {
	                field: "accuracy_prev_day", title: "Accuracy of previous day", width: 100
	            }
	            , {
	                field:"created_at", title:"Date Added", responsive: {
	                    visible: "lg"
	                }
	            }
	            , {
	                field:"updated_at", title:"Date Mofified", responsive: {
	                    visible: "lg"
	                }
	            }
	            , {
	                field:"Status", title:"Status", template:function(e) {
	                    a= {
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
	                    return'<span data-raw-json data-id="'+e.pk+'" data-symbol="'+e.symbol+'" data-prediction_date="'+e.prediction_date+'" data-high="'+e.high+'" data-low="'+e.low+'" data-close="'+e.close+'" data-accuracy_prev_day="'+e.accuracy_prev_day+'" data-status="'+e.status+'"  data-created_at="'+e.created_at+'" data-updated_at="'+e.updated_at+'"  data-stock_id="'+e.stock_id+'" class="m-badge '+a[e.status].class+' m-badge--wide">'+a[e.status].title+"</span>"
	                }
	            }
	            , {
	                field:"Actions", 
	                width:110, 
	                title:"Actions", 
	                sortable:!1, 
	                overflow:"visible", 
	                template:function(e) {
	                    return'\t\t\t\t\t\t<div class="dropdown '+(e.getDatatable().getPageSize()-e.getIndex()<=4?"dropup": "")+'">\t\t\t\t\t\t\t<a href="#" class="btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" data-toggle="dropdown"><i class="la la-ellipsis-h"></i></a>\t\t\t\t\t\t\t<div class="dropdown-menu dropdown-menu-right">\t\t\t\t\t\t\t<a class="dropdown-item" href="#" data-edit-modal><i class="la la-edit"></i> Edit Details</a>\t\t\t\t\t\t\t<a class="dropdown-item" href="#" data-delete-record><i class="la la-remove"></i> Remove</a></div>\t\t\t\t\t\t</div>\t\t\t\t\t\t\t\t\t\t\t'
	                }
	            }
	        ]
        } ),

        i=a.getDataSourceQuery();
        $("#m_form_status").on("change", function() {
            console.log("Searching status", Boolean($(this).val()));
            a.search(Boolean($(this).val()), "Status")
        }
        ).val(void 0!==i.Status?i.Status:""),
        
        $("#m_form_type").on("change", function() {
            a.search($(this).val(), "Sector")
        }
        ).val(void 0!==i.Type?i.Type:""),
        $("#m_form_status, #m_form_type").selectpicker()

    };

    return {
        init:function() {
            
            // Reload data from json
            stocksJson.length = 0;
			var srcJson = jQuery('#stocks-data').data('raw-data');
			console.log("Src json", srcJson);
			for (var i=0; i<srcJson.length; i++) {
				var field = srcJson[i].fields;
				
				field['id'] = i+1;
				field['pk'] = srcJson[i].pk;
				stocksJson.push(field);
			}

			console.log("Stocks json", stocksJson)

            e()
        	
        	// Add action listener to edit details modal
			jQuery("body").on("click", "a[data-edit-modal]", function(e) {

				var $targetModal = jQuery('#myModal');
				var $rawDataElem = $(this).parents('tr').find('[data-raw-json]');
				var $modalForm = jQuery($targetModal).find('div.modal-body form');

				jQuery($modalForm).find("input[name='date']").val(jQuery($rawDataElem).data('prediction_date'));
				jQuery($modalForm).find("input[name='high']").val(jQuery($rawDataElem).data('high'));
				jQuery($modalForm).find("input[name='low']").val(jQuery($rawDataElem).data('low'));
				jQuery($modalForm).find("input[name='close']").val(jQuery($rawDataElem).data('close'));
				jQuery($modalForm).find("input[name='accuracy_prev_day']").val(jQuery($rawDataElem).data('accuracy_prev_day'));
				jQuery($modalForm).find("input[name='stock_prediction_id']").val(jQuery($rawDataElem).data('id'));
				if ($rawDataElem.data("status"))
					jQuery($modalForm).find("input[name='status'][data-name='active']").attr('checked', 'checked');
				else
					jQuery($modalForm).find("input[name='status'][data-name='inactive']").attr('checked', 'checked');

				jQuery($targetModal).modal({
					backdrop: false
				});
			});

			// Add action listener to edit details modal
			jQuery("body").on("click", "a[data-delete-record]", function(e) {

				if (!confirm("Are you sure to remove this record?"))
					return;

				// var $targetModal = jQuery('#myModal');
				var $rawDataElem = $(this).parents('tr').find('[data-raw-json]');
				window.location.href= URL_REMOVE_STOCK_PREDICTION+"?stock_id="+CURRENT_STOCK_ID+"&id="+jQuery($rawDataElem).data('id');
			});

			// Add action listener to edit details modal
			jQuery("body").on("click", "a#viewDetails", function(e) {
				var $rawDataElem = $(this).parents('tr').find('[data-raw-json]');
				window.location.href= BASE_DIR+"/admin/stock/"+jQuery($rawDataElem).data('symbol');
			});

        },
    
    }
}
();

function loadJson() {
	
    // stocksJson.length = 0;
    // var srcJson = jQuery('#stocks-data').data('raw-data');
    // console.log("Src json", srcJson);
    // for (var i=0; i<srcJson.length; i++) {
    // 	var field = srcJson[i].fields;
    	
    // 	field['id'] = i+1;
    // 	field['pk'] = srcJson[i].pk;
    // 	stocksJson.push(field);
    // }
    // console.log(DatatableDataLocalDemo, "data table instance")
    DatatableDataLocalDemo.init();

}

jQuery(document).ready(function() {
	loadJson();
});
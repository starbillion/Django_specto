var stockSubsHistoryData = [];
var DatatableDataSubscriptionHistory=function() {
    var e=function() {

    	// var srcJson = Object.create(stockSubsHistoryData);
    	var srcJson = stockSubsHistoryData;
		stockSubsHistoryData = [];
		for (var k=0; k<srcJson.length; k++) {
			var field = srcJson[k].fields;
			
			field['id'] = k+1;
			field['pk'] = srcJson[k].pk;
			stockSubsHistoryData.push(field);
		}
        var e = stockSubsHistoryData;
        console.log("Data", e);
        $('.subsHistoryDataTable').html('');
        $('.subsHistoryDataTable').removeClass("m-datatable--loaded m-datatable m-datatable--default m-datatable--error m-datatable--loaded");
        $('.subsHistoryDataTable').attr('style', '');
        var a=$(".subsHistoryDataTable").mDatatable( {
            data: {
                type: "local", source: e, pageSize: 10
            }
            , layout: {
                theme: "default", class: "", scroll: !1, height: 450, footer: !1
            }
            , sortable:!0, pagination:!0, search: {
                input: $(".some")
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
	                field:"plan_duration", title:"Plan Duration", responsive: {
	                }
	            }
	            , {
	                field: "price", title: "Price", width: 100
	            }
	            , {
	                field:"created_at", title:"Date Added", responsive: {
	                    visible: "lg"
	                }
	            }
	            , {
	                field:"updated_at", title:"Date Modified", responsive: {
	                    visible: "lg"
	                }
	            }
	            , {
	                field:"removed", title:"Status", template:function(e) {
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
	                    return'<span data-raw-json data-id="'+e.pk+'" data-status="'+e.status+'"  data-created_at="'+e.created_at+'" data-updated_at="'+e.updated_at+'" class="m-badge '+a[e.status].class+' m-badge--wide">'+a[e.status].title+"</span>"
	                }
	            }
	            /*, {
	                field:"Actions", 
	                width:110, 
	                title:"Actions", 
	                sortable:!1, 
	                overflow:"visible", 
	                template:function(e) {
	                    return'\t\t\t\t\t\t<div class="dropdown '+(e.getDatatable().getPageSize()-e.getIndex()<=4?"dropup": "")+'">\t\t\t\t\t\t\t<a href="#" class="btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" data-toggle="dropdown"><i class="la la-ellipsis-h"></i></a>\t\t\t\t\t\t\t<div class="dropdown-menu dropdown-menu-right">\t\t\t\t\t\t\t<a class="dropdown-item" href="#" data-edit-modal><i class="la la-edit"></i> Edit Details</a>\t\t\t\t\t\t\t<a class="dropdown-item" href="#" data-delete-record><i class="la la-remove"></i> Remove</a></div>\t\t\t\t\t\t</div>\t\t\t\t\t\t\t\t\t\t\t'
	                }
	            }*/
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
            e()
        },
    
    }
}
();

jQuery("#subscriptionsHistoryModal").on("hide.bs.modal", function() {
	console.log("Heyaaaaaaaaa")
	jQuery(".subsHistoryDataTable").html("").removeClass("m-datatable m-datatable--default m-datatable--error m-datatable--loaded").removeAttr('style');
})
// To init the DataTable for stock subscription
// First populate the stockSubsHistoryData
// Then init the datatable plugins
// DatatableDataSubscriptionHistory.init();
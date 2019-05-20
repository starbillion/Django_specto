var stocksJson = [];
var DatatableDataLocalDemo=function() {
    var e=function() {

        /* var e=JSON.parse('[
        	{
        		id: "3",
				status: "False",
				stock: {
					id: "3",
					name: "1-800 FLOWERS.COM, Inc.",
					status: "True",
					symbol: "FLWS",
				}
				subscription_ends: "March 10, 2018, 2:37 a.m.",
				subscription_started: "Feb. 8, 2018, 2:37 a.m.",
        	}
        */
        // var e = JSON.parse(srcJson);
        var e = stocksJson;
        a=$(".m_datatable").mDatatable( {
            data: {
                type: "local", source: e, pageSize: 10
            }
            , layout: {
                theme: "default", 
                class: "m-datatable--brand", 
                scroll: !1, 
                height: 450, 
                footer: !1,
                header: true,
            },
            toolbar: {
                layout: ["pagination", "info"],
                placement: ["bottom"],
                items: {
                    pagination: {
                        type: "default",
                        pages: {
                            desktop: {
                                layout: "default",
                                pagesNumber: 6
                            },
                            tablet: {
                                layout: "default",
                                pagesNumber: 3
                            },
                            mobile: {
                                layout: "compact"
                            }
                        },
                        navigation: {
                            prev: !0,
                            next: !0,
                            first: !0,
                            last: !0
                        },
                        pageSizeSelect: [10, 20, 30, 50, 100]
                    },
                    info: !0
                }
            }
            , sortable:!0, pagination:!0, search: {
                input: $("#generalSearch")
            },
            columns:[ 
            	{
            		field:"RecordID",
            		title:"#",
            		sortable:!1,
            		width:40,
            		textAlign:"center",
            		selector:{
            			class:"m-checkbox--solid m-checkbox--brand"
            		}
            	}
	            ,{
	                field: "stock_symbol", 
	                title: "Symbol",
	                width: 150,
                    template: function(e) {
                        // console.log(e)
                        return '<span data-raw-json data-id="'+e.id+'" data-symbol="'+e.stock_symbol+'" data-name="'+e.stock_name+'" data-status="'+e.stock_status+'"><a href="'+ URL_STOCK_SINGLE+e.stock_symbol +'">'+e.stock_symbol+'</a></span>';
                    }
	            }
	            , {
	                field:"stock_name", 
	                title:"Name", 
	                responsive: {
	                    visible: "lg"
	                },
	                width: 150,
	            }
                , {
                    field:"stock_open", 
                    title:"Open", 
                    responsive: {
                        visible: "lg"
                    },
                    width: 150,
                }
                , {
                    field:"stock_close", 
                    title:"Close", 
                    responsive: {
                        visible: "lg"
                    },
                    width: 150,
                }
                , {
                    field:"stock_high", 
                    title:"High", 
                    responsive: {
                        visible: "lg"
                    },
                    width: 150,
                }
                , {
                    field:"stock_low", 
                    title:"Low", 
                    responsive: {
                        visible: "lg"
                    },
                    width: 150,
                },
                /*{
                    field:"stock_day_change", 
                    title:"Day (%) Change", 
                    responsive: {
                        visible: "lg"
                    },
                    width: 150,
                }
                , {
                    field:"stock_year_change", 
                    title:"Year (%) Change", 
                    responsive: {
                        visible: "lg"
                    },
                    width: 150,
                }*/
                
	        ],
            rows: {
                callback: function(row, data, index) {
                    // if (data.status)
                    console.log(data.status.toLowerCase() == 'false');
                    // console.log(row, "heyaa", data)
                    if (data.status.toLowerCase() == 'false')
                        $(row).addClass("row-inactive")
                    else
                        $(row).addClass("row-active")
                        // console.log(row, data, index);
                    $(row).removeClass("m-datatable__row--even")
                },
            },
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
        	
        	// Add action listener to edit details modal
			jQuery("body").on("click", "a[data-edit-modal]", function(e) {

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

			// Add action listener to edit details modal
			jQuery("body").on("click", "a[data-delete-record]", function(e) {

				if (!confirm("Are you sure to remove this record?"))
					return;

				// var $targetModal = jQuery('#myModal');
				var $rawDataElem = $(this).parents('tr').find('[data-raw-json]');
				window.location.href= URL_REMOVE_STOCK+"?id="+jQuery($rawDataElem).data('id');
			});

			// Add action listener to edit details modal
			jQuery("body").on("click", "a#viewDetails", function(e) {
				var $rawDataElem = $(this).parents('tr').find('[data-raw-json]');
				window.location.href= BASE_DIR+"/admin/stock/"+jQuery($rawDataElem).data('symbol');
			});

        }
    }
}
();

jQuery(document).ready(function() {
    // var srcJson = jQuery('#stocks-data').data('raw-data');
    console.log("Src json", favourites);
    // for (var i=0; i<srcJson.length; i++) {
    // 	var field = srcJson[i].fields;
    // 	field['id'] = i+1;
    // 	field['pk'] = srcJson[i].pk;
    // 	stocksJson.push(field);
    // }
    stocksJson = favourites;
    DatatableDataLocalDemo.init();

}

);
function AjaxCall(url, method="post", data={}, callback=function(){}, errorCallback=function(){}, extraData={}) {
	console.log("Calling ajaxxx!!!", CSRF_TOKEN)
	// console.log(url, method, data)
	$.ajax({
		url: url,
		type: method,
		data: data,
		cache: false,
		dataType: 'json',
		headers: {
			'X-CSRFToken': CSRF_TOKEN
		},
		success: function(s) {
			// console.log("Success", s);
			callback(s, extraData);
		},
		error: function(e) {
			// console.log("Error", e);
			errorCallback(e, extraData);
		}

	})
}
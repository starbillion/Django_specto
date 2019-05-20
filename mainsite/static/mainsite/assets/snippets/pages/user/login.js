var SnippetLogin = function() {
    var e = $("#m_login"),
        i = function(e, i, a) {
            var t = $('<div class="m-alert m-alert--outline alert alert-' + i + ' alert-dismissible" role="alert">\t\t\t<button type="button" class="close" data-dismiss="alert" aria-label="Close"></button>\t\t\t<span></span>\t\t</div>');
            e.find(".alert").remove(), t.prependTo(e), t.animateClass("fadeIn animated"), t.find("span").html(a)
        },
        a = function() {
            e.removeClass("m-login--forget-password"), e.removeClass("m-login--signin"), e.addClass("m-login--signup"), e.find(".m-login__signup").animateClass("flipInX animated")
        },
        t = function() {
            e.removeClass("m-login--forget-password"), e.removeClass("m-login--signup"), e.addClass("m-login--signin"), e.find(".m-login__signin").animateClass("flipInX animated")
        },
        r = function() {
            e.removeClass("m-login--signin"), e.removeClass("m-login--signup"), e.addClass("m-login--forget-password"), e.find(".m-login__forget-password").animateClass("flipInX animated")
        },
        n = function() {
            $("#m_login_forget_password").click(function(e) {
                e.preventDefault(), r()
            }), $("#m_login_forget_password_cancel").click(function(e) {
                e.preventDefault(), t()
            }), $("#m_login_signup").click(function(e) {
                e.preventDefault(), a()
            }), $("#m_login_signup_cancel").click(function(e) {
                e.preventDefault(), t()
            })
        },
        l = function() {
            $("#m_login_signin_submit").click(function(e) {
                e.preventDefault();
                var a = $(this),
                    t = $(this).closest("form");
                t.validate({
                    rules: {
                        email: {
                            required: !0,
                            email: !0
                        },
                        password: {
                            required: !0
                        }
                    }
                }), t.valid() && (a.addClass("m-loader m-loader--right m-loader--light").attr("disabled", !0), t.ajaxSubmit({
                    url: t.data('action'),
                    dataType: "json",
                    success: function(e, r, n, l) {
                        console.log('success', e);
                        setTimeout(function() {
                            if (e.status == 1) {
	                            a.removeClass("m-loader m-loader--right m-loader--light").attr("disabled", !1), i(t, "success", e.message);
	                            location.reload(t.data('success-url'));
	                        	return;
                            }
	                        a.removeClass("m-loader m-loader--right m-loader--light").attr("disabled", !1), i(t, "danger", e.message);
                        }, 2e3)
                    }
                }))
            })
        },
        s = function() {
            $("#m_login_signup_submit").click(function(a) {
                a.preventDefault();
                var r = $(this),
                    n = $(this).closest("form");
                n.validate({
                    rules: {
                        fullname: {
                            required: !0
                        },
                        email: {
                            required: !0,
                            email: !0
                        },
                        password: {
                            required: !0
                        },
                        rpassword: {
                            required: !0
                        },
                        agree: {
                            required: !0,
                        }
                    }
                }), n.valid() && (r.addClass("m-loader m-loader--right m-loader--light").attr("disabled", !0), n.ajaxSubmit({
                    url: n.data('action'),
                    dataType: "json",
                    success: function(a, l, s, o) {
                    	console.log('success', a, l, s, o);
                        setTimeout(function() {
                            r.removeClass("m-loader m-loader--right m-loader--light").attr("disabled", !1), n.clearForm(), n.validate().resetForm();
                            var sForm = e.find(".m-login__signup form");
                            if (a.status == 1){
                            	sForm.clearForm(), sForm.validate().resetForm(), i(sForm, "success", a.message)
                            	// location.reload(n.data('success-url'));
                            	return;
                            }
                            if (a.status == -1){
                            	var message = '';
                            	$.each(a.message, function(k, v){
                            		$.each(v, function(ik, iv){
                        				$.each(v, function(iik, iiv){
                        					message += "<li>"+ iiv +"</li>";
                            			});
                            		});
                            	})
                        		sForm.clearForm(), sForm.validate().resetForm(), i(sForm, "danger", message)	
                            	return;
                            }
                        	sForm.clearForm(), sForm.validate().resetForm(), i(sForm, "danger", a.message)	
                        }, 2e3)
                        return;
                    },
                    error: function(a, l, s, o) {
                    	console.log('error in call', a, l, s, o);
                    	setTimeout(function() {
                            r.removeClass("m-loader m-loader--right m-loader--light").attr("disabled", !1), n.clearForm(), n.validate().resetForm();
                            var a = e.find(".m-login__signup form");
                            a.clearForm(), a.validate().resetForm(), i(a, "error", "Server error")
                        }, 2e3)
                    }
                }))
            })
        },
        o = function() {
            $("#m_login_forget_password_submit").click(function(a) {
                a.preventDefault();
                var r = $(this),
                    n = $(this).closest("form");
                n.validate({
                    rules: {
                        email: {
                            required: !0,
                            email: !0
                        }
                    }
                }), n.valid() && (r.addClass("m-loader m-loader--right m-loader--light").attr("disabled", !0), n.ajaxSubmit({
                    url: n.data('action'),
                    dataType: "json",
                    success: function(a, l, s, o) {
                        setTimeout(function() {
                            var aForm = e.find(".m-login__forget-password form");
                            r.removeClass("m-loader m-loader--right m-loader--light").attr("disabled", !1), n.clearForm(), n.validate().resetForm();
                            if (a.status == 1){
                            	aForm.clearForm(), aForm.validate().resetForm(), i(aForm, "success", a.message);
                            	return;		
                            }
                            aForm.clearForm(), aForm.validate().resetForm(), i(aForm, "danger", a.message);
                        }, 2e3)
                    },
                    error: function(e) {
                    	console.log('error', e);
                    }
                }))
            })
        };
    return {
        init: function() {
            n(), l(), s(), o()
        }
    }
}();
jQuery(document).ready(function() {
    SnippetLogin.init()
});

/*var SnippetLogin=function(){
	var e=$("#m_login"),
	i=function(e,i,a){
		var t=$('<div class="m-alert m-alert--outline alert alert-'
			+i
			+' alert-dismissible" role="alert">\t\t\t<button type='+
			+'"button" class="close" data-dismiss="alert" aria-label'+
			+'="Close"></button>\t\t\t<span></span>\t\t</div>');
		e.find(".alert").remove(),
		t.prependTo(e),
		t.animateClass("fadeIn animated"),
		t.find("span").html(a)
	},
	a=function(){
		e.removeClass("m-login--forget-password"),
		e.removeClass("m-login--signin"),
		e.addClass("m-login--signup"),
		e.find(".m-login__signup").animateClass("flipInX animated")
	},
	t=function(){
		e.removeClass("m-login--forget-password"),
		e.removeClass("m-login--signup"),
		e.addClass("m-login--signin"),
		e.find(".m-login__signin").animateClass("flipInX animated")
	},
	r=function(){
		e.removeClass("m-login--signin"),
		e.removeClass("m-login--signup"),
		e.addClass("m-login--forget-password"),
		e.find(".m-login__forget-password").animateClass("flipInX animated")
	},
	n=function(){
		$("#m_login_forget_password").click(function(e){
			e.preventDefault(),r()
		}),
		$("#m_login_forget_password_cancel").click(function(e){
			e.preventDefault(),t()
		}),
		$("#m_login_signup").click(function(e){
			e.preventDefault(),a()
		}),
		$("#m_login_signup_cancel").click(function(e){
			e.preventDefault(),t()
		})
	},
	l=function(){
		$("#m_login_signin_submit").click(function(e){
			e.preventDefault();
			var a=$(this),
			t=$(this).closest("form");
			t.validate({
				rules:{
					email:{required:!0,email:!0},
					password:{required:!0}
				}
			}),
			t.valid()&&(a.addClass("m-loader m-loader--right m-loader--light").attr("disabled",!0),
				t.ajaxSubmit({
					url:t.data('action'),
					method: 'post',
					success:function(e,r,n,l){
						console.log('success', e, r, n, l);
						setTimeout(function(){
							a.removeClass("m-loader m-loader--right m-loader--light").attr("disabled",!1),
							i(t,"danger","Incorrect username or password. Please try again.")
						},2e3)
					},
					error: function(e){
						console.log('heyaa', e);
						setTimeout(function(){
							a.removeClass("m-loader m-loader--right m-loader--light").attr("disabled",!1)
						},2e3)
					}
				})
			)
		})
	},
	s=function(){
		$("#m_login_signup_submit").click(function(a){
			a.preventDefault();
			var r=$(this),
			n=$(this).closest("form");
			n.validate({
				rules:{
					fullname:{required:!0},
					email:{required:!0,email:!0},
					password:{required:!0},
					rpassword:{required:!0},
					agree:{required:!0}
				}
			}),
			n.valid()&&(r.addClass("m-loader m-loader--right m-loader--light").attr("disabled",!0),
				n.ajaxSubmit({
					url:"",
					success:function(a,l,s,o){
						setTimeout(function(){
							r.removeClass("m-loader m-loader--right m-loader--light").attr("disabled",!1)
							,n.clearForm(),
							n.validate().resetForm(),
							t();
							var a=e.find(".m-login__signin form");
							a.clearForm(),
							a.validate().resetForm(),
							i(a,"success","Thank you. To complete your registration please check your email.")
						},2e3)
					}
				})
			)}
		)},
		o=function(){
			$("#m_login_forget_password_submit").click(function(a){
				a.preventDefault();
				var r=$(this),
				n=$(this).closest("form");
				n.validate({
					rules:{
						email:{required:!0,email:!0}
					}
				})
				,n.valid()&&(r.addClass("m-loader m-loader--right m-loader--light").attr("disabled",!0),
					n.ajaxSubmit({
						url:"",
						success:function(a,l,s,o){
							setTimeout(
								function(){
									r.removeClass("m-loader m-loader--right m-loader--light").attr("disabled",!1),
									n.clearForm(),
									n.validate().resetForm(),
									t();
									var a=e.find(".m-login__signin form");
									a.clearForm(),
									a.validate().resetForm(),
									i(a,"success","Cool! Password recovery instruction has been sent to your email.")
								},2e3
							)
						}
					})
				)
			})
		};
		return{
			init:function(){
				n(),
				l(),
				s(),
				o()
			}
		}
	}();
	jQuery(document).ready(
		function(){
			SnippetLogin.init()
		}
	);*/
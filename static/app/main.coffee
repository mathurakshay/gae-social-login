
check_if_blank = (fields) ->
	is_blank = false
	for field in fields
		if $(field).val() == ''
			$(field).closest('.control-group').addClass('error')
			is_blank = true
		else
			$(field).closest('.control-group').removeClass('error')

	return is_blank

$("#register").click ->
	if check_if_blank ['#username', '#new_password', '#confirm_password']
		alert 'Please fill the fields marked in red and try again.'
		return false
	if $("#new_password").val() != $("#confirm_password").val()
		alert 'Password and Confirm Password do not match.'
		return false

	person_data =
		username: $("#username").val()
		password: $("#new_password").val()
		first_name: $("#username").val().split('@')[0]
		acq_source: 'email'
	register_user person_data
	
register_user = (person_data)->
	person_data.username = person_data.username.toLowerCase()
	ajax_params =
		url: "/people/add"
		dataType: "json"
		type: "PUT"
		data: person_data
		success: (response) ->
			if response
				if response.success
					alert 'Registration successful. Click OK to continue ....'
					login_success(response)
				else
					if response.reason == 'already_exist'
						alert "Your account is registered via <span style='text-transform: capitalize;'>#{response.login_type}</span>.\nPlease log in."
					else
						alert('Unexpected error. The server says: ' + response.reason)
			else
				alert 'There was some error in communication. Please try again later.'
		error: ->
			alert 'There was some error reaching the server at this time. Please try again later.'

	$.ajax ajax_params



$("#native_login").click ->
	if check_if_blank ['#email', '#password']
		alert 'Please fill the fields marked in red and try again.'
		return false
	person_data=
		username: $("#email").val()
		password: $("#password").val()
		login_type: 'email'
	authenticate_user person_data

authenticate_user = (person_data) ->
	person_data.username = person_data.username.toLowerCase()
	ajax_params =
		url: '/login'
		dataType: "json"
		data: person_data
		context: person_data
		success: (response) ->
			if response
				if response.success
					login_success(response)
				else
					if response.reason == 'unmatched_password'
						alert 'Invalid email address or password. Please try again.'
					else if response.reason == 'other_login_type'
						alert "Your account is registered via <span style='text-transform: capitalize;'>#{response.login_type}</span>.\nPlease click 'Sign in with Facebook' to log in."
					else if response.reason == 'no_user'
						alert "Invalid email address or password.\nIf you do not have an account,\nclick 'Sign up' or 'Sign in with Facebook'"
					else if response.reason == 'merge'
						prompt_for_merge(response.uid, this)
			else
				alert 'There was some error in communication. Please try again later.'
		error: ->
			alert 'There was some error reaching the server at this time. Please try again later.'
		complete: ->
			#$("#login_content").unmask()

	#$("#login_content").mask('Please wait...')
	$.ajax ajax_params

$("#logout").click ->
	ajax_params =
		url: '/logout'
		dataType: "json"
		data:
			username: cc_user.email_addr
		success: (response) ->
			if (response && response.success)
				$.cookie(response.cookie_name, '', {path: '/'})
				window.location = window.location

	$.ajax ajax_params

prompt_for_merge = (uid, person_data) ->
	$(".modal-body").html $.tmpl($.template('#merge_template'), person_data)
	$("#merging_email").data({uid: uid, person_data: person_data})
	$("#merging_popup").modal('show')
	
$("#merge_logins").click ->
	if check_if_blank ['#merging_password']
		alert 'Please fill the password (marked in red) and try again.'
		return false
	uid = $("#merging_email").data('uid')
	person_data = $("#merging_email").data('person_data')
	person_data.password = $("#merging_password").val()

	ajax_params =
		url: "/people/#{uid}"
		dataType: "json"
		type: "POST"
		data: person_data
		success: (response) ->
			if response
				if response.success
					alert 'Social login is now enabled for you.'
					login_success(response)
				else if response.reason == 'unmatched_password'
					alert 'Invalid email address or password. Please try again.'
				else
					alert 'There was some error saving the data at this time. Please try again later.'
			else
				alert 'There was some error in communication. Please try again later.'
		error: ->
			alert 'There was some error reaching the server at this time. Please try again later.'
		complete: ->
			#$("#login_content").unmask()

	$.ajax ajax_params

login_success = (response) ->
	$.cookie(response.cookie_name, response.cookie_value, {path: '/'})
	window.location = window.next_url

window.authenticate_user = authenticate_user

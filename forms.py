from wtforms import Form, TextField, TextAreaField, PasswordField, validators

class LoginForm(Form):
    email = TextField("Email", [validators.Required(), validators.Email()])
    password = PasswordField("Password", [validators.Required()])

class NewCodeForm(Form):
    company = TextField("Company", [validators.Required()])
    code = TextAreaField("Code or Link", [validators.Required()])


class NewUserForm(Form):
	first_name = TextField("First Name", [validators.Required()])
	last_name = TextField("Last Name", [validators.Required()])
	email = TextField("Email", [validators.Required()], validators.Email())
	password = PasswordField("Password", [validators.Required()])  
	#how does it connect with the password that will be authenticated?

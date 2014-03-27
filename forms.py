from wtforms import Form, TextField, TextAreaField, PasswordField, validators

class LoginForm(Form):
    email = TextField("Email", [validators.Required(), validators.Email()])
    password = PasswordField("Password", [validators.Required()])

class NewCodeForm(Form):
    company = TextField("Company", [validators.Required()])
    code = TextAreaField("Code or Link", [validators.Required()])
    expiry_date = TextField("Expiry Date", [validators.Optional()])
    description = TextField("Description")
    url = TextField("URL")
    category = TextField("Category")
    

class NewUserForm(Form):
	first_name = TextField("First Name", [validators.Required()])
	last_name = TextField("Last Name", [validators.Required()])
	email = TextField("Email", [validators.Required(), validators.Email()])
	password = PasswordField("Password", [validators.Required()])  
	#how does it connect with the password that will be authenticated?

class NewBuddyForm(Form):
    first_name = TextField("First Name", [validators.Required()])
    last_name = TextField("Last Name", [validators.Required()])
    email = TextField("Email", [validators.Required(), validators.Email()])
    message = TextField("Add a personal message for your buddy", [validators.Optional()])

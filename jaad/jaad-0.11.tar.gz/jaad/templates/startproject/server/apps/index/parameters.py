from jaad.forms import fields


class HelloWorldParameters(fields.Form):
    name = fields.StringField(required=False, help_text="Enter your name :)")

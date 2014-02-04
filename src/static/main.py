import controllers

from lib import server


# Fetch all controllers
app = server.Application(controllers.all_classes())

# Jinja templates options
app.set_jinja_options(
    block_start_string = '{%',
    block_end_string = '%}',
    variable_start_string = '{{',
    variable_end_string = '}}',
    comment_start_string = '{#',
    comment_end_string = '#}'
)


app.initialize(debug = True)

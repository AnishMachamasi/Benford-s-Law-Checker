from pyramid.view import view_config
from pyramid.config import Configurator
from wsgiref.simple_server import make_server
import pandas as pd
import math

@view_config(route_name='home', renderer='templates/home.jinja2')
def home(request):
    return {}

@view_config(route_name='benford', renderer='templates/home.jinja2')
def benford(request):
    #Read the file
    file = request.POST['file'].file
    data = pd.read_csv(file, header=None, names=['value'])

    # Get the first digit of each value
    first_digits = data['value'].apply(lambda x: int(str(x)[0]))

    # Calculate the expected Benford distribution
    benford = [None] + [math.log10((i+1)/i) for i in range(1, 10)]

    # Calculate the actual distribution of first digits
    actual = first_digits.value_counts(normalize=True).sort_index()

    # Compare the expected and actual distributions
    diff = abs(pd.Series(benford) - actual).sum()

    # check the difference within certain threshold
    if diff < 0.1:
        conforms = True
    else:
        conforms = False
        
    # Render the template with the result included
    return {'result': {'conforms': conforms, 'probabilities': actual.to_dict()}}

if __name__ == '__main__':
    with Configurator() as config:
        config.include('pyramid_jinja2')
        config.add_static_view(name='static', path='static')
        config.add_route('home', '/')
        config.add_route('benford', '/benford')
        config.scan()
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    print("Running on http://0.0.0.0:6543")
    server.serve_forever()

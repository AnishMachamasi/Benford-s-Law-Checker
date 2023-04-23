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
    # Get the uploaded file from the request
    file = request.POST['file'].file
    data = pd.read_csv(file, header=None, names=['value'])
    
    # Replace null values with NaN
    data = data.replace('', float('nan'))

    # Replace '-' with NaN
    data = data.replace('-', float('nan'))

    data.dropna(inplace=True)

    # Convert values to float
    data['value'] = data['value'].astype(float)

    # Get the first digit of each value
    first_digits = data['value'].apply(lambda x: int(str(x)[0]) if str(x)[0] != '0' else None)

    # Calculate the expected Benford distribution
    benford = [None] + [math.log10((i+1)/i) for i in range(1, 10)]

    # Calculate the actual distribution of first digits
    actual = first_digits.value_counts(normalize=True).sort_index()
    
    actual_dict = {int(key): value for key, value in actual.to_dict().items()}

    # Compare the expected and actual distributions
    diff = abs(pd.Series(benford) - actual).sum()

    # If the difference is within a certain threshold, return success
    if diff < 0.3:
        conforms = True
    else:
        conforms = False
        
    return {'result': {'conforms': conforms, 'probabilities': actual_dict}}

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

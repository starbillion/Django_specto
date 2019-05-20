def setup_venv():
    print("Setting up VirtualEnv \'venv\' in project directory")
    # install venv using p3
    # activate and use venv for next steps


def setup_packages():
    print("pip installing packages in virtual environment")


def fix_cart_module():
    print("Fxing Cart Module")
    # in cart.py: 1. replace text for .models
    # in models.py: 1. replace line 27
    # in models.py: 2. replace line 31


def setup_local_test_db():
    print("Setting up local database")
    # flag will determine whether local or production mode (#todo for now just production)
    print("Making migrations")


def populate_db():
    print("cities_light")

    print("stocks/load-db")


def populate_fake_predictions_and_plans():
    print("filling up data base with fake predictions")
    print("filling up data base with fake plans")


def run_server():
    # get local IP address
    # add to settings.py allowed_hosts
    # do python manage.py runserver local_ip:8000
    print("Starting Server")

def main_setup():
    setup_venv()
    setup_packages()
    fix_cart_module()
    setup_local_test_db()
    populate_db()
    populate_fake_predictions_and_plans()
    run_server()

main_setup()

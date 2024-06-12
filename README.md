# metamiejskie

wszystko i nic



[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)

License: MIT

## Basic Commands

### Setting Up Your Users

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser


### Type checks

Running type checks with mypy:

    $ mypy metamiejskie

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html
### test command:
`pytest --cov-config .coveragerc --cov-report term --cov=metamiejskie`
#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

## Deployment

The following details how to deploy this application.

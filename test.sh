#!/usr/bin/env bash

pytest --doctest-modules code/app-regex.py
pytest --doctest-modules code/results.py
pytest --doctest-modules code/util.py

# pytest --doctest-modules evaluate/util.py

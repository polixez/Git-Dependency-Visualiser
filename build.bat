@echo off
echo Running tests...

python -m unittest discover -s tests.

echo Build completed.
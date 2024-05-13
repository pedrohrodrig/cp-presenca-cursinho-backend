echo off
echo VERIFIQUE SE VOCE TEM O PYTHON 3.10 INSTALADO
echo.
echo A versao usada pelo seu terminal eh:
py --version
echo.
echo Caso contrario, aperte Ctrll+C para sair
pause
cd backend
py -m pip install pipenv
pipenv shell --python 3.10
pipenv run pre-commit install 
pipenv install --dev

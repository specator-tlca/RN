@echo off
chcp 65001 > nul
echo ====================================
echo RH Project - Full Test Suite
echo ====================================
echo.

REM Check virtual environment
if not exist .venv (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

REM Activate environment
call .venv\Scripts\activate.bat

echo.
echo === Testing Basic Scripts ===
echo.
python src\compute_C_right.py --P 100000
echo.
python src\measure_Cthin_star.py
echo.
python src\threshold_T0.py
echo.
python src\validate_horizontals.py

echo.
echo === Testing Enhanced Scripts ===
echo.
python src\compute_C_right_enhanced.py --P 100000
echo.
python src\measure_Cthin_star_enhanced.py --method current
echo.
python src\threshold_T0_enhanced.py
echo.
python src\validate_horizontals_enhanced.py

echo.
echo === Testing Analysis Scripts ===
echo.
python src\compare_methods.py

echo.
echo === Running Full Suite ===
echo.
python run_all.py

echo.
echo === Viewing Results ===
echo.
python view_results.py

echo.
echo ====================================
echo All tests completed!
echo Check logs\ and data\ for outputs
echo ====================================
pause

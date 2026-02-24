import pytest
import sys
import os

# Añadir el directorio '01_Local_MySQL' al path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "01_Local_MySQL"))

from SNS_Producer_events import get_temperature_status, get_wind_status

def test_get_temperature_status():
    assert get_temperature_status(-35) == "EXTREME_COLD"
    assert get_temperature_status(15) == "NORMAL"
    assert get_temperature_status(25) == "WARM"
    assert get_temperature_status(45) == "EXTREME_HEAT"

def test_get_wind_status():
    # Test only speed
    assert get_wind_status(0.5, 0) == "CALM"
    assert get_wind_status(15, 0) == "MODERATE"
    
    # Test gust override
    assert get_wind_status(15, 75) == "EXTREME"
    assert get_wind_status(5, 55) == "STORM"

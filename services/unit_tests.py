import pytest
from forecast import Forecast

def test_forecast_init():
    f = Forecast(nr_simulations=10, backlog_min=5, backlog_max=10, throughput=[1,2,3,4])
    assert f.nr_simulations == 10
    assert f.backlog_min == 5
    assert f.backlog_max == 10
    assert f.throughput == [1,2,3,4]

def test_run_simulation_returns_list_of_ints():
    f = Forecast(nr_simulations=5, backlog_min=5, backlog_max=5, throughput=[1,2,3,4])
    result = f.run_simulation()
    assert isinstance(result, list)
    assert len(result) == 5
    assert all(isinstance(x, int) for x in result)

def test_calculate_percentiles_correct_values():
    data = [1, 2, 3, 4, 5]
    percentiles = [0, 50, 100]
    expected = {0: 1, 50: 3, 100: 5}
    result = Forecast.calculate_percentiles(data, percentiles)
    assert result == expected

def test_calculate_percentiles_empty_input_raises():
    with pytest.raises(ValueError):
        Forecast.calculate_percentiles([], [50])
    with pytest.raises(ValueError):
        Forecast.calculate_percentiles([1,2,3,4], [])

def test_format_forecast_response_structure():
    f = Forecast(nr_simulations=10, backlog_min=1, backlog_max=2, throughput=[1,2,3,4])
    response = f.format_forecast_response(p50=5, p75=7, p85=8, p95=10)
    assert response['Backlog-min'] == 1
    assert response['Backlog-max'] == 2
    assert response['Throughput'] == [1,2,3,4]
    assert response['Simulations'] == 10
    assert response['Percentil-50'] == 5
    assert response['Percentil-75'] == 7
    assert response['Percentil-85'] == 8
    assert response['Percentil-95'] == 10
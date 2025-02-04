 
import pandas as pd
from model_update import update_model

def test_update_model(tmp_path):
    # Create a temporary CSV file
    df = pd.DataFrame({
        'lab_results': ['normal blood count', 'high cholesterol'],
        'interpretation': ['normal', 'abnormal']
    })
    file_path = tmp_path / "test_data.csv"
    df.to_csv(file_path, index=False)

    result = update_model(str(file_path))
    assert result['status'] == 'success'
    assert 'Model updated successfully' in result['message']

def test_interpret_lab_results():
    from interpret_lab_results import interpret_lab_results
    result = interpret_lab_results("Normal blood count, all values within range")
    assert 'interpretation' in result
    assert 'confidence' in result
    assert 'severity' in result

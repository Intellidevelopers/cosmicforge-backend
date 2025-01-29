 
import json
import io

def test_interpret_endpoint_text(client, mock_model):
    mock_model.return_value = {"interpretation": "Normal results", "confidence": "95%", "severity": 0}
    response = client.post('/interpret', data={'text': 'Sample lab result'})
    assert response.status_code == 200
    assert 'interpretation' in json.loads(response.data)

def test_interpret_endpoint_file(client, mock_model):
    mock_model.return_value = {"interpretation": "Abnormal results", "confidence": "80%", "severity": 2}
    data = {'file': (io.BytesIO(b"Sample lab result"), 'test.txt')}
    response = client.post('/interpret', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert 'interpretation' in json.loads(response.data)

def test_update_model_endpoint(client, mock_update_model):
    mock_update_model.return_value = {"status": "success", "message": "Model updated successfully"}
    data = {'file': (io.BytesIO(b"id,lab_results,interpretation\n1,test,normal"), 'update.csv')}
    response = client.post('/update-model', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'Model updated successfully'

def test_feedback_endpoint(client, mock_process_feedback):
    mock_process_feedback.return_value = {"status": "success", "message": "Feedback recorded successfully"}
    data = {'interpretation_id': '123', 'feedback': 'Great interpretation'}
    response = client.post('/feedback', json=data)
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'Feedback recorded successfully'

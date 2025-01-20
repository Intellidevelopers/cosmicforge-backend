 
from feedback_handler import process_feedback, Feedback

def test_process_feedback(db_session):
    feedback_data = {
        'interpretation_id': '123',
        'feedback': 'Great interpretation'
    }
    result = process_feedback(feedback_data)
    assert result['status'] == 'success'
    assert result['message'] == 'Feedback recorded successfully'

    # Verify that the feedback was actually saved
    saved_feedback = db_session.query(Feedback).first()
    assert saved_feedback is not None
    assert saved_feedback.interpretation_id == '123'
    assert saved_feedback.feedback == 'Great interpretation'

def test_trigger_model_update(db_session, mocker):
    mock_update = mocker.patch('feedback_handler.update_model_with_feedback')
    mock_update.return_value = {"status": "success", "message": "Model updated successfully"}

    # Add feedback to trigger update
    for i in range(100):  # Assuming FEEDBACK_THRESHOLD is 100
        process_feedback({
            'interpretation_id': str(i),
            'feedback': f'Feedback {i}'
        })

    # Verify that update_model_with_feedback was called
    mock_update.assert_called_once()

    # Verify that feedback was cleared after update
    assert db_session.query(Feedback).count() == 0

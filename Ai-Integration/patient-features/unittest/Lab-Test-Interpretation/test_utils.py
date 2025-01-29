 
from utils import preprocess_text, allowed_file

def test_preprocess_text():
    text = "This is a TEST with 123 numbers!"
    processed = preprocess_text(text)
    assert processed == "test numbers"

def test_allowed_file():
    assert allowed_file('test.txt', {'txt', 'pdf'}) == True
    assert allowed_file('test.exe', {'txt', 'pdf'}) == False

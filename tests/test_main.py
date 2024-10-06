from mslookup.app.input_manager import InputManager

def test_input_manager_get_raw_input():
    input_manager = InputManager()
    result = input_manager.get_raw_input()
    
    assert isinstance(result['file_path'], str) and result['file_path'], "O 'file_path' deve ser uma string não vazia."
    assert isinstance(result['products_type'], str) and result['products_type'], "O 'products_type' deve ser uma string não vazia."
    assert isinstance(result['item_col'], str) and result['item_col'], "O 'item_col' deve ser uma string não vazia."
    assert isinstance(result['desc_col'], str) and result['desc_col'], "O 'desc_col' deve ser uma string não vazia."
    assert isinstance(result['brand_col'], str) and result['brand_col'], "O 'brand_col' deve ser uma string não vazia."
    
    assert isinstance(result, dict), "O retorno deve ser um dicionário."
    expected_keys = ['file_path', 'products_type', 'item_col', 'desc_col', 'brand_col']
    missing_keys = [key for key in expected_keys if key not in result]
    assert not missing_keys, f"Chaves ausentes no dicionário: {missing_keys}"
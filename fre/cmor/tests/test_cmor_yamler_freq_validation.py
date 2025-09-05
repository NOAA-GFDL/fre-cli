import pytest
from fre.cmor.cmor_yamler import conv_mip_to_bronx_freq

def test_conv_mip_to_bronx_freq_valid_frequencies():
    """
    Test conversion of valid MIP table frequencies to bronx frequencies.
    """
    # Test cases from the mapping dictionary
    test_cases = [
        ("1hr", "1hr"),
        ("1hrCM", None),
        ("1hrPt", None),
        ("3hr", "3hr"),
        ("3hrPt", None),
        ("6hr", "6hr"),
        ("6hrPt", None),
        ("day", "daily"),
        ("dec", None),
        ("fx", None),
        ("mon", "monthly"),
        ("monC", None),
        ("monPt", None),
        ("subhrPt", None),
        ("yr", "annual"),
        ("yrPt", None)  # Should return None according to mapping
    ]
    
    for cmor_freq, expected_bronx_freq in test_cases:
        result = conv_mip_to_bronx_freq(cmor_freq)
        assert result == expected_bronx_freq, f"Failed for {cmor_freq}: expected {expected_bronx_freq}, got {result}"

def test_conv_mip_to_bronx_freq_fx_frequency():
    """
    Test that 'fx' frequency returns None without raising an exception.
    """
    # Arrange
    cmor_freq = "fx"
    
    # Act
    result = conv_mip_to_bronx_freq(cmor_freq)
    
    # Assert
    assert result is None

def test_conv_mip_to_bronx_freq_invalid_frequency():
    """
    Test that invalid frequencies (not 'fx') raise KeyError.
    """
    # Arrange
    invalid_frequencies = ["invalid", "unknown", "bad_freq", "yearly", "weekly"]
    
    for invalid_freq in invalid_frequencies:
        # Act & Assert
        with pytest.raises(KeyError, match=f'MIP table frequency = "{invalid_freq}" is not a valid MIP frequency'):
            conv_mip_to_bronx_freq(invalid_freq)

def test_conv_mip_to_bronx_freq_edge_cases():
    """
    Test edge cases and boundary conditions.
    """
    # Test empty string
    with pytest.raises(KeyError):
        conv_mip_to_bronx_freq("")
    
    # Test None input - should raise KeyError
    with pytest.raises(KeyError):
        conv_mip_to_bronx_freq(None)

def test_conv_mip_to_bronx_freq_case_sensitivity():
    """
    Test that the function is case-sensitive.
    """
    # These should raise KeyError because they're not exact matches
    case_variants = ["1HR", "Mon", "DAY", "YR"]
    
    for variant in case_variants:
        with pytest.raises(KeyError):
            conv_mip_to_bronx_freq(variant)

def test_conv_mip_to_bronx_freq_special_fx_logic():
    """
    Test the special logic for 'fx' frequency that was added in the diff.
    """
    # The diff shows: if bronx_freq is None and cmor_table_freq != 'fx':
    # This means 'fx' should not raise an error even though it returns None
    
    # 'fx' should return None without error
    result = conv_mip_to_bronx_freq("fx")
    assert result is None
    
    # But other frequencies that return None should raise error
    # Since 'yrPt' maps to None in the dictionary, it should still pass
    result = conv_mip_to_bronx_freq("yrPt")
    assert result is None

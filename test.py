from database import queryData
import pytest

def test_queryData():
    assert queryData("111111") == True



from pathlib import Path
import pytest
import requests
import sys

sys.path.insert(0, Path('src/'))


@pytest.fixture
def client():
    return requests

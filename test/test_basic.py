import pytest
import pandas as pd

class TestBasicData:
    
    @pytest.fixture(scope='class')
    def setup(self):
        # Load the datasets
        self.hotspots = pd.read_excel('C:/Users/oriol/OneDrive/UNI/MASTER/Modern Data Analytics/Project/data/hotspots.xlsx')
        self.greenspots = pd.read_excel('C:/Users/oriol/OneDrive/UNI/MASTER/Modern Data Analytics/Project/data/greenspots.xlsx')
        self.bluespots = pd.read_excel('C:/Users/oriol/OneDrive/UNI/MASTER/Modern Data Analytics/Project/data/bluespots.xlsx')

    def test_hotspots(self, setup):
        assert self.hotspots.shape[1] == 8, "Hotspots: Number of columns should be 8"
        assert self.hotspots.shape[0] > 0, "Hotspots: There should be at least one row"
        assert len(self.hotspots['Cluster'].unique()) > 0, "Hotspots: There should be at least one cluster"

    def test_greenspots(self, setup):
        assert self.greenspots.shape[1] == 8, "Greenspots: Number of columns should be 8"
        assert self.greenspots.shape[0] > 0, "Greenspots: There should be at least one row"
        assert len(self.greenspots['Cluster'].unique()) > 0, "Greenspots: There should be at least one cluster"

    def test_bluespots(self, setup):
        assert self.bluespots.shape[1] == 8, "Bluespots: Number of columns should be 8"
        assert self.bluespots.shape[0] > 0, "Bluespots: There should be at least one row"
        assert len(self.bluespots['Cluster'].unique()) > 0, "Bluespots: There should be at least one cluster"

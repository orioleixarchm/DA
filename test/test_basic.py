import pytest
import pandas as pd
import gdown
import os

class TestBasicData:
    
    @pytest.fixture(scope='class')
    def setup(self):
        # Download the datasets
        links = [
            "https://drive.google.com/file/d/1iZ6Cpzh4iniSv5D6firXnaWXAI5DCw3A/edit?usp=drive_link",
            "https://drive.google.com/file/d/19i47foVILPjmA4RyKP4WEBQFXSEvLyEe/edit?usp=drive_link",
            "https://drive.google.com/file/d/12UFMCiZhiIhau1dNUBUdPaOm_KBGVOhw/edit?usp=drive_link"
        ]

        # Extract file IDs and construct URLs
        file_ids = [link.split('/d/')[1].split('/')[0] for link in links]
        urls = [f'https://drive.google.com/uc?id={file_id}' for file_id in file_ids]

        # Download files
        data_dir = os.getcwd()
        gdown.download(urls[0], os.path.join(data_dir, 'hotspots_distance.xlsx'), quiet=False)
        gdown.download(urls[1], os.path.join(data_dir, 'greenspots.xlsx'), quiet=False)
        gdown.download(urls[2], os.path.join(data_dir, 'bluespots.xlsx'), quiet=False)

        # Load the datasets
        self.hotspots = pd.read_excel(os.path.join(data_dir, 'hotspots_distance.xlsx'))
        self.greenspots = pd.read_excel(os.path.join(data_dir, 'greenspots.xlsx'))
        self.bluespots = pd.read_excel(os.path.join(data_dir, 'bluespots.xlsx'))

    def test_hotspots(self, setup):
        assert self.hotspots.shape[1] == 9, "Hotspots: Number of columns should be 9"
        assert self.hotspots.shape[0] == 5340, "Hotspots: There should be 5340 rows"
        assert self.hotspots['Cluster'].nunique() == 30, "Hotspots: There should be 30 clusters"

    def test_greenspots(self, setup):
        assert self.greenspots.shape[1] == 5, "Greenspots: Number of columns should be 5"
        assert self.greenspots.shape[0] == 2654, "Bluespots: There should be 2654 rows"
        assert self.greenspots['Cluster'].nunique() == 111, "Greenspots: There should be 111 clusters"

    def test_bluespots(self, setup):
        assert self.bluespots.shape[1] == 5, "Bluespots: Number of columns should be 5"
        assert self.bluespots.shape[0] == 13, "Bluespots: There should be 13 rows"
        assert self.bluespots['Cluster'].nunique() == 2, "Bluespots: There should be 2 clusters"

if __name__ == '__main__':
    pytest.main()

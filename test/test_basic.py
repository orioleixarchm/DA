import pytest
import pandas as pd
import gdown
import os

class TestBasicData:
    
    @pytest.fixture(scope='class')
    def setup(self):
        # Download the datasets
        links = [
            "https://drive.google.com/file/d/1meuUUiUbCNDhhCvWTrs68gRgQ5qYQGcG/edit?usp=drive_link",
            "https://drive.google.com/file/d/19i47foVILPjmA4RyKP4WEBQFXSEvLyEe/edit?usp=drive_link",
            "https://drive.google.com/file/d/12UFMCiZhiIhau1dNUBUdPaOm_KBGVOhw/edit?usp=drive_link"
        ]

        # Extract file IDs and construct URLs
        file_ids = [link.split('/d/')[1].split('/')[0] for link in links]
        urls = [f'https://drive.google.com/uc?id={file_id}' for file_id in file_ids]

        # Download files
        data_dir = os.getcwd()
        gdown.download(urls[0], os.path.join(data_dir, 'hotspots.xlsx'), quiet=False)
        gdown.download(urls[1], os.path.join(data_dir, 'greenspots.xlsx'), quiet=False)
        gdown.download(urls[2], os.path.join(data_dir, 'bluespots.xlsx'), quiet=False)

        # Load the datasets
        self.hotspots = pd.read_excel(os.path.join(data_dir, 'hotspots.xlsx'))
        self.greenspots = pd.read_excel(os.path.join(data_dir, 'greenspots.xlsx'))
        self.bluespots = pd.read_excel(os.path.join(data_dir, 'bluespots.xlsx'))

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

if __name__ == '__main__':
    pytest.main()

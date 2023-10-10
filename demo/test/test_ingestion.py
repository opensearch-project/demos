import sys, pytest
sys.path.append('./demo/')

from docbot.ingestion import *

def test_read_files_from_data():
    #Test normal data
    data_list = read_files_from_data()

    assert(isinstance(data_list, list))
    assert(len(data_list) > 0)
    assert(isinstance(data_list[0], dict))

    #Test a non-valid directory
    with pytest.raises(NotADirectoryError):
        read_files_from_data("!>!>!>")

    #test an empty directory
    fake_folder = os.path.join(os.getcwd(), "TESTINGBLANKFOLDER")
    os.mkdir(fake_folder)
    with pytest.raises(FileNotFoundError):
        read_files_from_data(fake_folder)
    os.rmdir(fake_folder)

# def test_ingest_to_opensearch():
#     pass

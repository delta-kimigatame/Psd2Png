from tests.test_command import TestCommanrline

class TestCommanrPython(TestCommanrline):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        super().setUp()
        self.command = ["python","Psd2Png.py","--noalert"]
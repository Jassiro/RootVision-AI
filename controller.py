from model import RootAnalyzer

class Controller:
    def __init__(self):
        self.model = RootAnalyzer()

    def load_image(self, image_path):
        self.model.load_image(image_path)

    def measure_roots(self):
        self.model.measure_roots()

    def display_results(self):
        self.model.display_results()

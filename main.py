import sys
from controller import Controller

class Main:
    def __init__(self):
        self.controller = Controller()

    def process_image(self, image_path):
        image_path="C:/Users/R I B/Desktop/pfe_jasser/471.tif"
        self.controller.process_image(image_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    main = Main()
    main.process_image(image_path)

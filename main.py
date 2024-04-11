from controller import Controller

if __name__ == "__main__":
    controller = Controller()
    image_path = r"C:\Users\R I B\Desktop\pfe_jasser\471.tif"
    controller.load_image(image_path)
    controller.measure_roots()
    controller.display_results()

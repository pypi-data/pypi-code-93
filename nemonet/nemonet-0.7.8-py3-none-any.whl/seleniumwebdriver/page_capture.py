import os
from PIL import Image
import time

class PageCapturing:

    def __init__( self, selenium_driver):
        self.selenium_driver = selenium_driver

    def prepare_page(self):
        pass

    def capture_save( self, file_name_cpatured='capture_save_test.png'):
        self.selenium_driver.execute_script('document.body.style.overflow = "hidden";')

        total_width = self.selenium_driver.execute_script("return document.body.offsetWidth")
        total_height = self.selenium_driver.execute_script("return document.body.parentNode.scrollHeight")
        viewport_width = self.selenium_driver.execute_script("return document.body.clientWidth")
        viewport_height = self.selenium_driver.execute_script("return window.innerHeight")

        rectangles = []

        i = 0
        while i < total_height:
            ii = 0
            top_height = i + viewport_height

            if top_height > total_height:
                top_height = total_height

            while ii < total_width:
                top_width = ii + viewport_width

                if top_width > total_width:
                    top_width = total_width
                rectangles.append((ii, i, top_width, top_height))

                ii = ii + viewport_width

            i = i + viewport_height

        stitched_image = Image.new('RGB', (total_width, total_height))
        previous = None
        part = 0
        self.selenium_driver.execute_script("window.scrollTo(0, 0)")
        for rectangle in rectangles:
            if previous is not None:
                self.selenium_driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
                # print("Scrolled To ({0},{1})".format(rectangle[0], rectangle[1]))
                time.sleep(0.2)

            file_name = "part_{0}.png".format(part)
            # print("Capturing {0} ...".format(file_name))

            self.selenium_driver.get_screenshot_as_file(file_name)
            screenshot = Image.open(file_name)

            if rectangle[1] + viewport_height > total_height:
                offset = (rectangle[0], total_height - viewport_height)
            else:
                offset = (rectangle[0], rectangle[1])

            # print("Adding to stitched image with offset ({0}, {1})".format(offset[0], offset[1]))
            stitched_image.paste(screenshot, offset)

            del screenshot
            os.remove(file_name)
            part = part + 1
            previous = rectangle

        stitched_image.save( file_name_cpatured )



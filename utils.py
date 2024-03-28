class Utils:
    
    @classmethod
    def resize_window(self, driver):
        screen_width = driver.execute_script("return window.screen.availWidth")
        screen_height = driver.execute_script("return window.screen.availHeight")
        new_position = (screen_width // 2, 0)
        new_size = (screen_width // 2, screen_height)
        driver.set_window_position(*new_position)
        driver.set_window_size(*new_size)

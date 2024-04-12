import logging

import customtkinter


class SafeDisposableFrame(customtkinter.CTkFrame):
    def __init__(self, master, logger_name: str = "", **kwargs):
        super().__init__(master, **kwargs)
        self.is_active = False
        self.is_destroyed = False
        self.canvas_im = None
        self.new_photo = None
        self.placeholder_im = None
        self.logger = logging.getLogger(logger_name)

    def enter(self):
        self.logger.info("enter")
        self.is_active = True

    def leave(self):
        self.logger.info("leave")
        self.is_active = False

    def destroy(self):
        self.logger.info("destroy")
        self.is_active = False
        self.is_destroyed = True
        self.canvas_im = None
        self.new_photo = None
        self.placeholder_im = None

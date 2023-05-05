# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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


class SafeDisposableScrollableFrame(customtkinter.CTkScrollableFrame):

    def __init__(self, master, logger_name: str = "", **kwargs):
        super().__init__(master, **kwargs)
        self.is_active = False
        self.is_destroyed = False
        self.canvas_im = None
        self.new_photo = None
        self.placeholder_im = None
        self.logger = logging.getLogger(logger_name)

        self.refresh_scrollbar()

    def refresh_scrollbar(self):
        bar_start, bar_end = self._scrollbar.get()
        if (bar_end - bar_start) < 1.0:
            self._scrollbar.grid()
        else:
            self._scrollbar.grid_remove()

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

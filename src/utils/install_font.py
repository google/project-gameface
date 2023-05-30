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

from src.platform.font_management import FontManagement
import logging
from pathlib import Path


def install_fonts(font_dir: str) -> None:
    font_dir = Path(font_dir)
    for font_file in font_dir.glob("*.ttf"):
        logging.info(f"Installing font {font_file.as_posix()}")
        fm = FontManagement()
        fm.add_font_resource(font_file=font_file.as_posix())


def remove_fonts(font_dir: str) -> None:
    font_dir = Path(font_dir)
    for font_file in font_dir.glob("*.ttf"):
        logging.info(f"Removing font {font_file.as_posix()}")
        fm = FontManagement()
        fm.remove_font_resource(font_file=font_file.as_posix())

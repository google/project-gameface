import logging
import sys
import os
import customtkinter

from src.gui import MainGui
from src.pipeline import Pipeline
from src.task_killer import TaskKiller

FORMAT = "%(asctime)s %(levelname)s %(name)s: %(funcName)s: %(message)s"

log_path = os.environ["USERPROFILE"] + "\Grimassist"
if not os.path.isdir(log_path):
    os.mkdir(log_path)

logging.basicConfig(
    format=FORMAT,
    level=logging.INFO,
    handlers=[
        logging.FileHandler(log_path + "\log.txt", mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)


class MainApp(MainGui, Pipeline):
    def __init__(self, tk_root):
        super().__init__(tk_root)
        # Wait for window drawing.
        self.tk_root.wm_protocol("WM_DELETE_WINDOW", self.close_all)

        self.is_active = True

        # Enter loop
        self.tk_root.after(1, self.anim_loop)

    def anim_loop(self):
        try:
            if self.is_active:
                # Run detectors and controllers.
                self.pipeline_tick()
                self.tk_root.after(1, self.anim_loop)
        except Exception as e:
            logging.critical(e, exc_info=e)

    def close_all(self):
        logging.info("Close all")
        self.is_active = False
        # Completely close this process
        TaskKiller().exit()


if __name__ == "__main__":
    tk_root = customtkinter.CTk()

    logging.info("Starting main app.")
    TaskKiller().start()

    main_app = MainApp(tk_root)
    main_app.tk_root.mainloop()

    main_app = None

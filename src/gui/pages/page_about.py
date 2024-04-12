# Standard library imports.
#
# Logging module.
# https://docs.python.org/3.8/library/logging.html
import logging

#
# Object oriented path handling.
# https://docs.python.org/3/library/pathlib.html

#
# Tcl/Tk user interface module.
# https://docs.python.org/3/library/tkinter.html
# https://tkdocs.com/tutorial/text.html
from tkinter import Text
from tkinter.ttk import Label
from tkinter.font import Font

#
# Browser launcher module.
# https://docs.python.org/3/library/webbrowser.html
import webbrowser

#
# PIP modules.
#
#
# Local imports.
#
from src.gui.frames.safe_disposable_frame import SafeDisposableFrame
from src.config_manager import ConfigManager

logger = logging.getLogger("PageAbout")


def log_path(description, path):
    logger.info(
        " ".join(
            (
                description,
                "".join(('"', str(path), '"')),
                "Exists." if path.exists() else "Doesn't exist.",
            )
        )
    )


# Jim initially was using Python lambda expressions for the event handlers. That
# seemed to result in all tag_bind() calls being overridden to whichever was the
# last one called. So now the tags are set up here, outside the class, and
# lambda expressions aren't used.
addressTags = {}


def add_address_tag(pageAbout, address):
    def _enter(event):
        pageAbout.hover_enter(address, event)

    def _leave(event):
        pageAbout.hover_leave(address, event)

    def _click(event):
        pageAbout.open_in_browser(address, event)

    addressTag = {
        "tag": f"address{len(addressTags)}",
        "enter": _enter,
        "leave": _leave,
        "click": _click,
    }
    tagText = addressTag["tag"]

    pageAbout.text.tag_configure(tagText)

    # TOTH using tag_bind. https://stackoverflow.com/a/65733556/7657675
    # TOTH list of events that makes clear they have to be in angle brackets.
    # https://stackoverflow.com/a/32289245/7657675
    #
    # -   <Enter> is triggered when the pointer hovers here.
    # -   <Leave> is triggered when the pointer stops hovering here.
    # -   <1> is triggered when this is clicked. It seems to be a shorthand for
    #     button-1.
    pageAbout.text.tag_bind(tagText, "<Enter>", addressTag["enter"])
    pageAbout.text.tag_bind(tagText, "<Leave>", addressTag["leave"])
    pageAbout.text.tag_bind(tagText, "<1>", addressTag["click"])

    addressTags[address] = addressTag
    return addressTag


def add_address_tags(pageAbout, addresses):
    # TOTH Underlining https://stackoverflow.com/a/44890599/7657675
    pageAbout.text.tag_configure("link", underline=True, foreground="#0000EE")

    for address in addresses:
        add_address_tag(pageAbout, address)

    return addressTags


def tags_for(address):
    try:
        return ("link", addressTags[address]["tag"])
    except KeyError as keyError:
        raise ValueError(
            "Address hasn't been registered."
            f' Add add_address_tag(pageAbout,"{address}")'
        ) from keyError


class PageAbout(SafeDisposableFrame):
    hoverCursor = "hand2"

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.is_active = False
        self.grid_propagate(False)

        # Create font objects for the fonts used on this page.
        font24 = Font(family="Google Sans", size=24)
        font18 = Font(family="Google Sans", size=18)
        font12 = Font(family="Google Sans", size=12)

        # Handy code to log all font families.
        # logger.info(font_families())

        # Create the about page as a Text widget. The text won't be editable but
        # that can't be set here because the widget will ignore the
        # text.insert() method. Instead editing is disabled after the insert().
        self.text = Text(
            self,
            wrap="word",
            borderwidth=0,
            font=font12,
            spacing1=20,
            height=10,  # height value has to be guessed it seems.
        )

        # Create tags for styling the page content.
        self.text.tag_configure("h1", font=font24)
        self.text.tag_configure("h2", font=font18)

        # Create a tag for every address in the about page. That seems to be the
        # only way that event handlers can be bound.
        add_address_tags(
            self,
            (
                "https://www.flaticon.com/free-icons/eye",
                "https://github.com/acidcoke/Grimassist/",
                "https://github.com/google/project-gameface",
            ),
        )
        logger.info(f"addressTags{addressTags}")

        # At time of coding, the app windows seems to be fixed size and the
        # about page content fits in it. So there's no need for a scroll bar. If
        # that changes then uncomment this code to add a scroll bar.
        #
        # from tkinter.ttk import Scrollbar
        # self.scrollY = Scrollbar(
        #     self, orient = 'vertical', command = self.text.yview)
        # self.text['yscrollcommand'] = self.scrollY.set
        # self.scrollY.grid(column = 1, row = 0, sticky = 'ns')

        self.text.grid(row=0, column=0, padx=0, pady=5, sticky="new")

        # The argument tail is an alternating sequence of texts and tag lists.
        # If the text is to be set in the default style then an empty tag list
        # () is given.
        self.text.insert(
            "1.0",
            "About Grimassist\n",
            "h1",
            f"Version {ConfigManager().version}\n"
            "Control and move the pointer using head movements and facial"
            " gestures.\nDisclaimer: This software isn't intended for medical"
            " use.\nGrimassist is an Open Source project\n",
            (),
            "Attribution\n",
            "h2",
            "Blink graphics in the user interface are based on ",
            (),
            "Eye icons created by Kiranshastry - Flaticon",
            tags_for("https://www.flaticon.com/free-icons/eye"),
            ".\nThis software is based on ",
            (),
            "Google GameFace",
            tags_for("https://github.com/google/project-gameface"),
            ".",
            (),
        )
        self.text.configure(state="disabled")

        # When the pointer hovers over a link, change it to a hand. It might
        # seem like that could be done by adding a configuration to the tag,
        # which is how links are underlined. However, it seems like that doesn't
        # work and the cursor cannot be configured at the tag level. The
        # solution is to configure and reconfigure it dynmically, at the widget
        # level, in the hover handlers.
        #
        # Discover the default cursor configuration here and store it. The value
        # is used in the hover handlers.
        self.initialCursor = self.text["cursor"]

        # Label to display the address of a link when it's hovered over.
        #
        # TBD make it transparent. For now it takes the background colour of the
        # text control, above.
        self.hoverLabel = Label(
            self, text="", font=font12, background=self.text["background"]
        )
        self.hoverLabel.grid(row=1, column=0, sticky="sw")

    def hover_enter(self, address, event):
        logger.info(f"hover({address}, {event}) {event.type}")
        # TOTH how to set the text of a label.
        # https://stackoverflow.com/a/17126015/7657675
        self.hoverLabel.configure(text=address)
        self.text.configure(cursor=self.hoverCursor)

    def hover_leave(self, address, event):
        logger.info(f"hover({address}, {event}) {event.type}")
        # TOTH how to set the text of a label.
        # https://stackoverflow.com/a/17126015/7657675
        self.hoverLabel.configure(text="")
        self.text.configure(cursor=self.initialCursor)

    def open_in_browser(self, address, event):
        logger.info(f"open_in_browser({address}, {event})")
        webbrowser.open(address)

    def enter(self):
        super().enter()

        # Next line would opens the About file in the browser.
        # open_in_browser(aboutHTML.as_uri(), None)

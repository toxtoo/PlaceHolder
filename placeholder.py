#!/usr/bin/env python3
"""
PlaceHolder

Makes plain placeholder images for laying out web pages before the real
pictures are ready: a solid colour with the size (or your own text) in the
middle, saved as a PNG, JPEG or SVG.

Run from source with:   python3 placeholder.py
Needs:                  PyQt6

Your last colours, size, text and folder are remembered in
~/.config/PlaceHolder/settings.json

Copyright (C) 2026. Released under the GNU General Public License v3.
"""

import json
import sys
from xml.sax.saxutils import escape
from pathlib import Path

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QIcon, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QColorDialog, QComboBox, QFileDialog, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSpinBox,
    QVBoxLayout, QWidget
)

APP_NAME = "PlaceHolder"
# Change this for each new release, and use the same number for the tag
APP_VERSION = "1.0"
PROJECT_URL = "https://github.com/toxtoo/PlaceHolder"

CONFIG_FILE = Path.home() / ".config" / "PlaceHolder" / "settings.json"
# Where the first version (Placeholder Maker) kept its settings
OLD_CONFIG_FILE = Path.home() / ".config" / "placeholder-maker.json"

ICON_FILE = Path(__file__).resolve().parent / "icons" / "placeholder-icon.png"

# Sizes offered in the Common sizes list
COMMON_SIZES = [
    (150, 150), (300, 200), (300, 250), (400, 300), (640, 480),
    (800, 600), (1024, 768), (1200, 800), (1280, 720), (1920, 1080),
]

PREVIEW_WIDTH = 400
PREVIEW_HEIGHT = 260


def size_text(width, height):
    return f"{width} × {height}"   # × is the multiplication sign


def fit_text(width, height, text):
    """The largest bold text size (in pixels) that fits comfortably, and the
    font at that size."""
    font = QFont("Sans Serif")
    font.setBold(True)
    pixel_size = max(6, int(min(height * 0.22, width * 0.2)))

    while pixel_size > 6:
        font.setPixelSize(pixel_size)
        metrics = QFontMetrics(font)
        if (
            metrics.horizontalAdvance(text) <= width * 0.85
            and metrics.height() <= height * 0.8
        ):
            break
        pixel_size -= 1

    font.setPixelSize(pixel_size)
    return pixel_size, font


def make_svg(width, height, background, foreground, text, cross):
    """The placeholder as SVG: a few lines of text that stay sharp at any
    size. The words are drawn by the browser, in whichever of the fonts
    listed it has, so they may look a little different from the preview."""
    bg = background.name()
    fg = foreground.name()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{bg}"/>',
    ]

    if cross:
        parts.append(
            f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
            f'fill="none" stroke="{fg}" stroke-width="1"/>'
        )
        parts.append(
            f'<path d="M0 0L{width} {height}M0 {height}L{width} 0" '
            f'stroke="{fg}" stroke-width="1"/>'
        )

    if text:
        pixel_size, font = fit_text(width, height, text)
        metrics = QFontMetrics(font)

        if cross:
            pad = max(4, pixel_size // 3)
            box_width = metrics.horizontalAdvance(text) + pad * 2
            box_height = metrics.height() + pad
            parts.append(
                f'<rect x="{(width - box_width) // 2}" y="{(height - box_height) // 2}" '
                f'width="{box_width}" height="{box_height}" fill="{bg}"/>'
            )

        # y is the text's baseline: about a third of the text size below the
        # middle centres it (dominant-baseline isn't understood by IE9)
        baseline = round(height / 2 + pixel_size * 0.35, 1)
        parts.append(
            f'<text x="{width / 2}" y="{baseline}" text-anchor="middle" '
            f'font-family="Arial, Helvetica, sans-serif" font-weight="bold" '
            f'font-size="{pixel_size}" fill="{fg}">{escape(text)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def make_placeholder(width, height, background, foreground, text, cross):
    """Draws the placeholder and returns it as a QImage."""
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(background)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    if cross:
        # A thin border and two diagonals, the classic placeholder look
        pen = QPen(foreground)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(0, 0, width - 1, height - 1)
        painter.drawLine(0, 0, width - 1, height - 1)
        painter.drawLine(0, height - 1, width - 1, 0)

    if text:
        # The largest text size that fits comfortably
        pixel_size, font = fit_text(width, height, text)
        rect = QRect(0, 0, width, height)

        if cross:
            # Give the text a background so the lines don't run through it
            metrics = QFontMetrics(font)
            pad = max(4, pixel_size // 3)
            text_width = metrics.horizontalAdvance(text) + pad * 2
            text_height = metrics.height() + pad
            painter.fillRect(
                (width - text_width) // 2, (height - text_height) // 2,
                text_width, text_height, background
            )

        painter.setFont(font)
        painter.setPen(foreground)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    painter.end()
    return image


class PlaceholderMaker(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)

        settings = self.load_settings()
        self.background = QColor(settings.get("background", "#cccccc"))
        self.foreground = QColor(settings.get("foreground", "#555555"))
        self.last_folder = settings.get("folder", str(Path.home()))
        self.last_saved = None

        # ---- Size ---------------------------------------------------------
        self.width_box = QSpinBox()
        self.width_box.setRange(1, 8000)
        self.width_box.setValue(int(settings.get("width", 640)))
        self.width_box.setSuffix(" px")

        self.height_box = QSpinBox()
        self.height_box.setRange(1, 8000)
        self.height_box.setValue(int(settings.get("height", 480)))
        self.height_box.setSuffix(" px")

        self.sizes = QComboBox()
        self.sizes.addItem("Common sizes...")
        for w, h in COMMON_SIZES:
            self.sizes.addItem(size_text(w, h), (w, h))
        self.sizes.activated.connect(self.choose_common_size)

        # ---- Colours ------------------------------------------------------
        self.background_button = QPushButton()
        self.background_button.clicked.connect(self.choose_background)

        self.foreground_button = QPushButton()
        self.foreground_button.clicked.connect(self.choose_foreground)

        # ---- Text and style -----------------------------------------------
        self.text_box = QLineEdit(settings.get("text", ""))
        self.text_box.setPlaceholderText("Leave empty to show the size")

        self.cross_box = QCheckBox("Border and diagonal lines")
        self.cross_box.setChecked(bool(settings.get("cross", False)))

        # ---- Preview ------------------------------------------------------
        self.preview = QLabel()
        self.preview.setFixedSize(PREVIEW_WIDTH, PREVIEW_HEIGHT)
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setStyleSheet("QLabel { background: #ffffff; border: 1px solid #aaaaaa; }")

        # ---- Buttons ------------------------------------------------------
        save_button = QPushButton("Save Image...")
        save_button.setDefault(True)
        save_button.clicked.connect(self.save_image)

        about_button = QPushButton("About")
        about_button.clicked.connect(self.show_about)

        copy_button = QPushButton("Copy <img> Tag")
        copy_button.setToolTip("Copies an <img> tag for the last image saved")
        copy_button.clicked.connect(self.copy_img_tag)

        # ---- Layout -------------------------------------------------------
        form = QGridLayout()
        form.addWidget(QLabel("Width:"), 0, 0)
        form.addWidget(self.width_box, 0, 1)
        form.addWidget(QLabel("Height:"), 1, 0)
        form.addWidget(self.height_box, 1, 1)
        form.addWidget(self.sizes, 2, 1)
        form.addWidget(QLabel("Background:"), 3, 0)
        form.addWidget(self.background_button, 3, 1)
        form.addWidget(QLabel("Text colour:"), 4, 0)
        form.addWidget(self.foreground_button, 4, 1)
        form.addWidget(QLabel("Text:"), 5, 0)
        form.addWidget(self.text_box, 5, 1)
        form.addWidget(self.cross_box, 6, 1)
        form.setRowStretch(7, 1)

        top = QHBoxLayout()
        top.addLayout(form)
        top.addSpacing(12)
        top.addWidget(self.preview)

        buttons = QHBoxLayout()
        self.status = QLabel("")
        # Plain text, so "<img>" in a message isn't read as HTML
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        self.status.setStyleSheet("QLabel { color: #555555; }")
        buttons.addWidget(about_button)
        buttons.addWidget(self.status, 1)
        buttons.addWidget(copy_button)
        buttons.addWidget(save_button)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addLayout(buttons)

        # Redraw the preview whenever anything changes
        self.width_box.valueChanged.connect(self.update_preview)
        self.height_box.valueChanged.connect(self.update_preview)
        self.text_box.textChanged.connect(self.update_preview)
        self.cross_box.toggled.connect(self.update_preview)

        self.update_colour_buttons()
        self.update_preview()

    # ---- Settings ---------------------------------------------------------

    def load_settings(self):
        # Use the old Placeholder Maker settings if there are no new ones yet
        for path in (CONFIG_FILE, OLD_CONFIG_FILE):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except (OSError, ValueError):
                continue
        return {}

    def save_settings(self):
        data = {
            "width": self.width_box.value(),
            "height": self.height_box.value(),
            "background": self.background.name(),
            "foreground": self.foreground.name(),
            "text": self.text_box.text(),
            "cross": self.cross_box.isChecked(),
            "folder": self.last_folder,
        }
        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")
        except OSError:
            pass

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    # ---- Controls ---------------------------------------------------------

    def choose_common_size(self, index):
        size = self.sizes.itemData(index)
        if size:
            self.width_box.setValue(size[0])
            self.height_box.setValue(size[1])
        self.sizes.setCurrentIndex(0)

    def choose_background(self):
        colour = QColorDialog.getColor(self.background, self, "Background colour")
        if colour.isValid():
            self.background = colour
            self.update_colour_buttons()
            self.update_preview()

    def choose_foreground(self):
        colour = QColorDialog.getColor(self.foreground, self, "Text colour")
        if colour.isValid():
            self.foreground = colour
            self.update_colour_buttons()
            self.update_preview()

    def update_colour_buttons(self):
        for button, colour in (
            (self.background_button, self.background),
            (self.foreground_button, self.foreground),
        ):
            # Black or white writing, whichever shows up on the colour
            writing = "#000000" if colour.lightness() > 140 else "#ffffff"
            button.setText(colour.name())
            button.setStyleSheet(
                f"QPushButton {{ background: {colour.name()}; color: {writing}; "
                "border: 1px solid #888888; padding: 4px; }"
            )

    # ---- Drawing ----------------------------------------------------------

    def current_text(self):
        text = self.text_box.text().strip()
        return text or size_text(self.width_box.value(), self.height_box.value())

    def current_image(self):
        return make_placeholder(
            self.width_box.value(), self.height_box.value(),
            self.background, self.foreground,
            self.current_text(), self.cross_box.isChecked()
        )

    def update_preview(self):
        pixmap = QPixmap.fromImage(self.current_image())
        self.preview.setPixmap(pixmap.scaled(
            PREVIEW_WIDTH - 10, PREVIEW_HEIGHT - 10,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

    # ---- Saving -----------------------------------------------------------

    def save_image(self):
        width = self.width_box.value()
        height = self.height_box.value()
        suggested = Path(self.last_folder) / f"placeholder-{width}x{height}.png"

        path, chosen_filter = QFileDialog.getSaveFileName(
            self, "Save placeholder image", str(suggested),
            "PNG image (*.png);;JPEG image (*.jpg *.jpeg);;SVG image (*.svg)"
        )

        if not path:
            return

        path = Path(path)

        # Use the ending of the type chosen in the list, unless one of the
        # known endings was typed
        if path.suffix.lower() not in (".png", ".jpg", ".jpeg", ".svg"):
            if "JPEG" in chosen_filter:
                path = path.with_suffix(".jpg")
            elif "SVG" in chosen_filter:
                path = path.with_suffix(".svg")
            else:
                path = path.with_suffix(".png")

        if path.suffix.lower() == ".svg":
            svg = make_svg(
                width, height, self.background, self.foreground,
                self.current_text(), self.cross_box.isChecked()
            )
            try:
                path.write_text(svg, encoding="utf-8")
            except OSError as error:
                QMessageBox.warning(self, APP_NAME, f"Could not save:\n{error}")
                return
        else:
            quality = 90 if path.suffix.lower() in (".jpg", ".jpeg") else -1

            if not self.current_image().save(str(path), None, quality):
                QMessageBox.warning(self, APP_NAME, f"Could not save:\n{path}")
                return

        self.last_folder = str(path.parent)
        self.last_saved = path
        self.last_saved_size = (width, height)
        self.save_settings()
        self.status.setText(f"Saved {path.name}")

    def show_about(self):
        box = QMessageBox(self)
        box.setWindowTitle(f"About {APP_NAME}")
        box.setIconPixmap(QPixmap(str(ICON_FILE)).scaled(
            64, 64, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setText(
            f"<b>{APP_NAME} {APP_VERSION}</b><br><br>"
            "Makes plain placeholder images for laying out web pages.<br><br>"
            "Released under the GNU General Public License v3.<br>"
            f'<a href="{PROJECT_URL}">{PROJECT_URL}</a>'
        )
        box.exec()

    def copy_img_tag(self):
        if self.last_saved is None:
            self.status.setText("Save an image first.")
            return

        width, height = self.last_saved_size
        tag = (
            f'<img src="{self.last_saved.name}" '
            f'width="{width}" height="{height}" alt="">'
        )
        QApplication.clipboard().setText(tag)
        self.status.setText("Copied the <img> tag.")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(QIcon(str(ICON_FILE)))
    window = PlaceholderMaker()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

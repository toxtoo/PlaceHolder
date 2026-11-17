#!/usr/bin/env python3
"""
PlaceHolder

Makes plain placeholder images for laying out web pages before the real
pictures are ready: a solid colour with the size, your own words or a soft
outlined icon in the middle, with square, rounded or round corners. Saved as
PNG, JPEG or SVG.

Run from source with:   python3 placeholder.py
Needs:                  PyQt6 (with its QtSvg part)

Your last choices are remembered in ~/.config/PlaceHolder/settings.json

Copyright (C) 2026. Released under the GNU General Public License v3.
"""

import json
import random
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PyQt6.QtCore import Qt, QByteArray, QRectF
from PyQt6.QtGui import (
    QColor, QFont, QFontMetrics, QIcon, QImage, QPainter, QPainterPath, QPen,
    QPixmap
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QColorDialog, QComboBox, QFileDialog, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSpinBox,
    QVBoxLayout, QWidget
)

APP_NAME = "PlaceHolder"
# Change this for each new release, and use the same number for the tag
APP_VERSION = "1.1"
PROJECT_URL = "https://github.com/toxtoo/PlaceHolder"

CONFIG_FILE = Path.home() / ".config" / "PlaceHolder" / "settings.json"
# Where the first version (Placeholder Maker) kept its settings
OLD_CONFIG_FILE = Path.home() / ".config" / "placeholder-maker.json"

ICON_FILE = Path(__file__).resolve().parent / "icons" / "placeholder-icon.png"

# Sizes offered in the Common sizes list
COMMON_SIZES = [
    (64, 64), (150, 150), (300, 200), (300, 250), (400, 300), (640, 480),
    (800, 600), (1024, 768), (1200, 800), (1280, 720), (1920, 1080),
]

PREVIEW_WIDTH = 400
PREVIEW_HEIGHT = 260

# ---------------------------------------------------------------------------
# The icons, drawn on a 96 x 96 grid in SVG. The outline colour is added
# when they are drawn; FILL is replaced by the lighter fill colour. To add
# an icon, add an entry here: it appears in the Icon list straight away.
# ---------------------------------------------------------------------------
ICONS = {
    "Picture": (
        '<rect x="10" y="14" width="76" height="68" rx="12"/>'
        '<path d="M12 70 L34 46 L46 58 L62 40 L84 66 L84 70 Q84 80 74 80 '
        'L22 80 Q12 80 12 70Z" fill="FILL"/>'
        '<circle cx="34" cy="32" r="7" fill="FILL"/>'
    ),
    "Camera": (
        '<path d="M14 34 Q14 26 22 26 L32 26 L38 18 L58 18 L64 26 L74 26 '
        'Q82 26 82 34 L82 72 Q82 80 74 80 L22 80 Q14 80 14 72Z"/>'
        '<circle cx="48" cy="52" r="15" fill="FILL"/>'
    ),
    "Person": (
        '<circle cx="48" cy="48" r="38"/>'
        '<circle cx="48" cy="40" r="12" fill="FILL"/>'
        '<path d="M24 74 Q30 58 48 58 Q66 58 72 74" fill="FILL"/>'
    ),
    "Video": (
        '<rect x="10" y="18" width="76" height="60" rx="12"/>'
        '<path d="M40 34 L62 48 L40 62Z" fill="FILL"/>'
    ),
    "Document": (
        '<path d="M22 10 L58 10 L76 28 L76 78 Q76 86 68 86 L28 86 '
        'Q20 86 20 78 L20 18 Q20 10 28 10Z"/>'
        '<path d="M58 10 L58 28 L76 28" fill="FILL"/>'
        '<path d="M32 46 L64 46 M32 58 L64 58 M32 70 L52 70"/>'
    ),
    "Map pin": (
        '<path d="M48 88 Q20 58 20 38 A28 28 0 0 1 76 38 Q76 58 48 88Z"/>'
        '<circle cx="48" cy="38" r="10" fill="FILL"/>'
    ),
    "Calendar": (
        '<rect x="14" y="20" width="68" height="62" rx="10"/>'
        '<path d="M14 38 L82 38 M32 12 L32 26 M64 12 L64 26"/>'
        '<rect x="27" y="48" width="10" height="9" rx="2" fill="FILL"/>'
        '<rect x="43" y="48" width="10" height="9" rx="2" fill="FILL"/>'
        '<rect x="59" y="48" width="10" height="9" rx="2" fill="FILL"/>'
        '<rect x="27" y="64" width="10" height="9" rx="2" fill="FILL"/>'
        '<rect x="43" y="64" width="10" height="9" rx="2" fill="FILL"/>'
    ),
    "Speech bubble": (
        '<path d="M20 20 Q10 20 10 30 L10 60 Q10 70 20 70 L30 70 L30 84 '
        'L46 70 L76 70 Q86 70 86 60 L86 30 Q86 20 76 20Z"/>'
        '<circle cx="32" cy="45" r="4" fill="FILL"/>'
        '<circle cx="48" cy="45" r="4" fill="FILL"/>'
        '<circle cx="64" cy="45" r="4" fill="FILL"/>'
    ),
    "Envelope": (
        '<rect x="10" y="22" width="76" height="54" rx="10"/>'
        '<path d="M16 30 L48 54 L80 30"/>'
    ),
    "Music": (
        '<path d="M38 70 L38 22 L76 14 L76 62"/>'
        '<circle cx="29" cy="71" r="9" fill="FILL"/>'
        '<circle cx="67" cy="63" r="9" fill="FILL"/>'
    ),
    "Shopping bag": (
        '<path d="M18 32 L78 32 L74 84 L22 84Z"/>'
        '<path d="M36 44 L36 28 Q36 16 48 16 Q60 16 60 28 L60 44"/>'
    ),
    "Heart": (
        '<path d="M48 82 Q14 58 14 36 Q14 18 32 18 Q42 18 48 28 '
        'Q54 18 64 18 Q82 18 82 36 Q82 58 48 82Z" fill="FILL"/>'
    ),
    "Star": (
        '<path d="M48.0 16.0 L56.8 39.9 L82.2 40.9 L62.3 56.6 L69.2 81.1 '
        'L48.0 67.0 L26.8 81.1 L33.7 56.6 L13.8 40.9 L39.2 39.9Z" fill="FILL"/>'
    ),
}

ICON_NAMES = list(ICONS)


def size_text(width, height):
    return f"{width} × {height}"   # × is the multiplication sign


def mix(colour_a, colour_b, amount_a):
    """A colour part-way between two others (amount_a of the first)."""
    b = 1 - amount_a
    return QColor.fromRgbF(
        colour_a.redF() * amount_a + colour_b.redF() * b,
        colour_a.greenF() * amount_a + colour_b.greenF() * b,
        colour_a.blueF() * amount_a + colour_b.blueF() * b,
    )


class Design:
    """Everything that decides how the placeholder looks, and where each
    part goes. Both the PNG/JPEG drawing and the SVG writing use this, so
    they always match."""

    def __init__(self, width, height, background, foreground, text, cross,
                 radius, round_shape, style, icon, show_size, soft):
        self.width = width
        self.height = height
        self.background = background
        self.foreground = foreground
        self.cross = cross
        self.style = style
        self.icon = icon if icon in ICONS else ICON_NAMES[0]

        # Corners: Round makes a circle on a square image (and a pill shape
        # on a long one); a radius can't be more than half the short side
        short_side = min(width, height)
        self.radius = short_side / 2 if round_shape else min(radius, short_side / 2)

        # Icon colours: soft shades of the background, or from Text colour
        if soft:
            self.icon_stroke = background.darker(124)
            self.icon_fill = background.darker(107)
            self.caption_colour = background.darker(150)
        else:
            self.icon_stroke = foreground
            self.icon_fill = mix(foreground, background, 0.3)
            self.caption_colour = foreground

        if style == "Icon":
            self.layout_icon(show_size)
        else:
            self.text = text or size_text(width, height)
            self.layout_text()

    # ---- Text style -------------------------------------------------------

    def layout_text(self):
        self.pixel_size, self.font = fit_text(
            self.width, self.height, self.text, 0.85, 0.22
        )

    # ---- Icon style -------------------------------------------------------

    def layout_icon(self, show_size):
        w, h = self.width, self.height
        self.icon_size = max(8, round(min(w, h) * 0.34))
        self.caption = None

        if show_size:
            caption = size_text(w, h)
            start = max(7, round(self.icon_size * 0.17))
            pixel_size, font = fit_text(w, h, caption, 0.9, 1, start=start)
            # Leave the size out if there isn't room for it to be readable
            if pixel_size >= 7 and self.icon_size + pixel_size * 2 <= h * 0.9:
                self.caption = caption
                self.caption_px = pixel_size
                self.caption_font = font

        gap = round(self.caption_px * 0.5) if self.caption else 0
        caption_height = round(self.caption_px * 1.3) if self.caption else 0
        total = self.icon_size + gap + caption_height

        self.icon_x = (w - self.icon_size) / 2
        self.icon_y = (h - total) / 2

        if self.caption:
            self.caption_top = self.icon_y + self.icon_size + gap
            self.caption_height = caption_height

    def icon_body(self):
        return (
            f'<g fill="none" stroke="{self.icon_stroke.name()}" stroke-width="3.5" '
            'stroke-linecap="round" stroke-linejoin="round">'
            + ICONS[self.icon].replace("FILL", self.icon_fill.name())
            + "</g>"
        )


def fit_text(width, height, text, width_share, height_share, start=None):
    """The largest bold text size (in pixels) that fits comfortably, and the
    font at that size."""
    font = QFont("Sans Serif")
    font.setBold(True)

    if start is None:
        start = int(min(height * height_share, width * 0.2))

    pixel_size = max(6, start)

    while pixel_size > 6:
        font.setPixelSize(pixel_size)
        metrics = QFontMetrics(font)
        if (
            metrics.horizontalAdvance(text) <= width * width_share
            and metrics.height() <= height * 0.8
        ):
            break
        pixel_size -= 1

    font.setPixelSize(pixel_size)
    return pixel_size, font


# ---------------------------------------------------------------------------
# Drawing as a picture (PNG and JPEG, and the preview)
# ---------------------------------------------------------------------------

def make_image(design):
    """Draws the placeholder as a QImage. Outside rounded corners the image
    is see-through."""
    w, h, r = design.width, design.height, design.radius

    image = QImage(w, h, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    shape = QPainterPath()
    if r > 0:
        shape.addRoundedRect(QRectF(0, 0, w, h), r, r)
    else:
        shape.addRect(QRectF(0, 0, w, h))

    painter.fillPath(shape, design.background)

    # Everything else stays inside the shape
    painter.setClipPath(shape)

    if design.cross:
        pen = QPen(design.foreground)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if r > 0:
            painter.drawRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), r - 0.5, r - 0.5)
        else:
            painter.drawRect(QRectF(0.5, 0.5, w - 1, h - 1))
        painter.drawLine(0, 0, w, h)
        painter.drawLine(0, h, w, 0)

    if design.style == "Icon":
        draw_icon(painter, design)
    else:
        draw_text(painter, design)

    painter.end()
    return image


def draw_text(painter, design):
    w, h = design.width, design.height

    if design.cross:
        # A patch of background so the lines don't run through the text
        metrics = QFontMetrics(design.font)
        pad = max(4, design.pixel_size // 3)
        box_width = metrics.horizontalAdvance(design.text) + pad * 2
        box_height = metrics.height() + pad
        painter.fillRect(
            QRectF((w - box_width) / 2, (h - box_height) / 2, box_width, box_height),
            design.background
        )

    painter.setFont(design.font)
    painter.setPen(design.foreground)
    painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, design.text)


def draw_icon(painter, design):
    size = design.icon_size

    if design.cross:
        pad = size * 0.08
        bottom = design.icon_y + size
        if design.caption:
            bottom = design.caption_top + design.caption_height
        painter.fillRect(
            QRectF(design.icon_x - pad, design.icon_y - pad,
                   size + pad * 2, bottom - design.icon_y + pad * 2),
            design.background
        )

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" '
        'viewBox="0 0 96 96">' + design.icon_body() + "</svg>"
    )
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    renderer.render(painter, QRectF(design.icon_x, design.icon_y, size, size))

    if design.caption:
        painter.setFont(design.caption_font)
        painter.setPen(design.caption_colour)
        painter.drawText(
            QRectF(0, design.caption_top, design.width, design.caption_height),
            Qt.AlignmentFlag.AlignCenter, design.caption
        )


# ---------------------------------------------------------------------------
# Writing as SVG
# ---------------------------------------------------------------------------

def make_svg(design):
    """The placeholder as SVG: a few lines of text that stay sharp at any
    size. Any words are drawn by the browser, in whichever of the fonts
    listed it has, so they may look a little different from the preview."""
    w, h, r = design.width, design.height, design.radius
    bg = design.background.name()
    fg = design.foreground.name()
    r_text = f' rx="{r:g}"' if r > 0 else ""

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">',
    ]

    if r > 0:
        parts.append(
            f'<defs><clipPath id="shape"><rect width="{w}" height="{h}"{r_text}/>'
            '</clipPath></defs>'
        )

    parts.append(f'<rect width="{w}" height="{h}"{r_text} fill="{bg}"/>')

    if design.cross:
        clip = ' clip-path="url(#shape)"' if r > 0 else ""
        inner_r = f' rx="{max(0, r - 0.5):g}"' if r > 0 else ""
        parts.append(
            f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}"{inner_r} '
            f'fill="none" stroke="{fg}" stroke-width="1"/>'
        )
        parts.append(
            f'<path d="M0 0L{w} {h}M0 {h}L{w} 0" stroke="{fg}" '
            f'stroke-width="1"{clip}/>'
        )

    if design.style == "Icon":
        size = design.icon_size

        if design.cross:
            pad = size * 0.08
            bottom = design.icon_y + size
            if design.caption:
                bottom = design.caption_top + design.caption_height
            parts.append(
                f'<rect x="{design.icon_x - pad:g}" y="{design.icon_y - pad:g}" '
                f'width="{size + pad * 2:g}" '
                f'height="{bottom - design.icon_y + pad * 2:g}" fill="{bg}"/>'
            )

        scale = size / 96
        parts.append(
            f'<g transform="translate({design.icon_x:g} {design.icon_y:g}) '
            f'scale({scale:g})">{design.icon_body()}</g>'
        )

        if design.caption:
            # y is the baseline: about a third of the text size below the
            # middle of its line (dominant-baseline isn't understood by IE9)
            middle = design.caption_top + design.caption_height / 2
            baseline = round(middle + design.caption_px * 0.35, 1)
            parts.append(
                f'<text x="{w / 2:g}" y="{baseline:g}" text-anchor="middle" '
                f'font-family="Arial, Helvetica, sans-serif" font-weight="bold" '
                f'font-size="{design.caption_px}" fill="{design.caption_colour.name()}">'
                f'{escape(design.caption)}</text>'
            )
    else:
        if design.cross:
            metrics = QFontMetrics(design.font)
            pad = max(4, design.pixel_size // 3)
            box_width = metrics.horizontalAdvance(design.text) + pad * 2
            box_height = metrics.height() + pad
            parts.append(
                f'<rect x="{(w - box_width) / 2:g}" y="{(h - box_height) / 2:g}" '
                f'width="{box_width}" height="{box_height}" fill="{bg}"/>'
            )

        baseline = round(h / 2 + design.pixel_size * 0.35, 1)
        parts.append(
            f'<text x="{w / 2:g}" y="{baseline:g}" text-anchor="middle" '
            f'font-family="Arial, Helvetica, sans-serif" font-weight="bold" '
            f'font-size="{design.pixel_size}" fill="{fg}">{escape(design.text)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# The window
# ---------------------------------------------------------------------------

class PlaceHolderWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)

        settings = self.load_settings()
        self.background = QColor(settings.get("background", "#dde0e5"))
        self.foreground = QColor(settings.get("foreground", "#555555"))
        self.last_folder = settings.get("folder", str(Path.home()))
        self.last_saved = None
        self.last_saved_size = None
        self.random_icon = random.choice(ICON_NAMES)

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

        # ---- Corners ------------------------------------------------------
        self.corner_box = QSpinBox()
        self.corner_box.setRange(0, 4000)
        self.corner_box.setValue(int(settings.get("radius", 0)))
        self.corner_box.setSuffix(" px")
        self.corner_box.setToolTip("0 for square corners")

        self.round_box = QCheckBox("Round (a circle on a square image)")
        self.round_box.setChecked(bool(settings.get("round", False)))

        # ---- Colours ------------------------------------------------------
        self.background_button = QPushButton()
        self.background_button.clicked.connect(self.choose_background)

        self.foreground_button = QPushButton()
        self.foreground_button.clicked.connect(self.choose_foreground)

        # ---- What goes in the middle -------------------------------------
        self.style_box = QComboBox()
        self.style_box.addItems(["Text", "Icon"])
        self.style_box.setCurrentText(settings.get("style", "Text"))

        self.text_box = QLineEdit(settings.get("text", ""))
        self.text_box.setPlaceholderText("Leave empty to show the size")

        self.icon_box = QComboBox()
        self.icon_box.addItem("Random")
        self.icon_box.addItems(ICON_NAMES)
        self.icon_box.setCurrentText(settings.get("icon", "Random"))

        self.new_icon_button = QPushButton("New icon")
        self.new_icon_button.setToolTip("Pick another icon at random")
        self.new_icon_button.clicked.connect(self.pick_new_icon)

        icon_row = QHBoxLayout()
        icon_row.setContentsMargins(0, 0, 0, 0)
        icon_row.addWidget(self.icon_box, 1)
        icon_row.addWidget(self.new_icon_button)

        self.show_size_box = QCheckBox("Show the size under the icon")
        self.show_size_box.setChecked(bool(settings.get("show_size", False)))

        self.soft_box = QCheckBox("Soft icon colours (from the background)")
        self.soft_box.setChecked(bool(settings.get("soft", True)))

        self.cross_box = QCheckBox("Border and diagonal lines")
        self.cross_box.setChecked(bool(settings.get("cross", False)))

        # ---- Preview ------------------------------------------------------
        self.preview = QLabel()
        self.preview.setFixedSize(PREVIEW_WIDTH, PREVIEW_HEIGHT)
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setStyleSheet("QLabel { background: #ffffff; border: 1px solid #aaaaaa; }")

        # ---- Buttons ------------------------------------------------------
        about_button = QPushButton("About")
        about_button.clicked.connect(self.show_about)

        save_button = QPushButton("Save Image...")
        save_button.setDefault(True)
        save_button.clicked.connect(self.save_image)

        copy_button = QPushButton("Copy <img> Tag")
        copy_button.setToolTip("Copies an <img> tag for the last image saved")
        copy_button.clicked.connect(self.copy_img_tag)

        # ---- Layout -------------------------------------------------------
        form = QGridLayout()
        row = 0

        def add_row(label, widget):
            nonlocal row
            if label:
                form.addWidget(QLabel(label), row, 0)
            if isinstance(widget, QHBoxLayout):
                form.addLayout(widget, row, 1)
            else:
                form.addWidget(widget, row, 1)
            row += 1

        add_row("Width:", self.width_box)
        add_row("Height:", self.height_box)
        add_row("", self.sizes)
        add_row("Corner radius:", self.corner_box)
        add_row("", self.round_box)
        add_row("Background:", self.background_button)
        add_row("Text colour:", self.foreground_button)
        add_row("Show:", self.style_box)
        add_row("Text:", self.text_box)
        add_row("Icon:", icon_row)
        add_row("", self.show_size_box)
        add_row("", self.soft_box)
        add_row("", self.cross_box)
        form.setRowStretch(row, 1)

        top = QHBoxLayout()
        top.addLayout(form)
        top.addSpacing(12)
        top.addWidget(self.preview, 0, Qt.AlignmentFlag.AlignTop)

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
        for spin in (self.width_box, self.height_box, self.corner_box):
            spin.valueChanged.connect(self.update_preview)
        for box in (self.round_box, self.show_size_box, self.soft_box, self.cross_box):
            box.toggled.connect(self.update_preview)
        self.text_box.textChanged.connect(self.update_preview)
        self.style_box.currentIndexChanged.connect(self.update_preview)
        self.icon_box.currentIndexChanged.connect(self.update_preview)

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
            "radius": self.corner_box.value(),
            "round": self.round_box.isChecked(),
            "background": self.background.name(),
            "foreground": self.foreground.name(),
            "style": self.style_box.currentText(),
            "text": self.text_box.text(),
            "icon": self.icon_box.currentText(),
            "show_size": self.show_size_box.isChecked(),
            "soft": self.soft_box.isChecked(),
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

    def pick_new_icon(self):
        others = [name for name in ICON_NAMES if name != self.random_icon]
        self.random_icon = random.choice(others)
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

    def update_enabled(self):
        """Greys out the settings that don't apply to the current choices."""
        icon_style = self.style_box.currentText() == "Icon"
        self.corner_box.setEnabled(not self.round_box.isChecked())
        self.text_box.setEnabled(not icon_style)
        self.icon_box.setEnabled(icon_style)
        self.new_icon_button.setEnabled(
            icon_style and self.icon_box.currentText() == "Random"
        )
        self.show_size_box.setEnabled(icon_style)
        self.soft_box.setEnabled(icon_style)

    # ---- Drawing ----------------------------------------------------------

    def current_icon(self):
        chosen = self.icon_box.currentText()
        return self.random_icon if chosen == "Random" else chosen

    def current_design(self):
        return Design(
            self.width_box.value(), self.height_box.value(),
            self.background, self.foreground,
            self.text_box.text().strip(), self.cross_box.isChecked(),
            self.corner_box.value(), self.round_box.isChecked(),
            self.style_box.currentText(), self.current_icon(),
            self.show_size_box.isChecked(), self.soft_box.isChecked()
        )

    def update_preview(self):
        self.update_enabled()

        image = make_image(self.current_design())
        scaled = QPixmap.fromImage(image).scaled(
            PREVIEW_WIDTH - 10, PREVIEW_HEIGHT - 10,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # A light checkerboard behind the image shows any see-through corners
        canvas = QPixmap(scaled.size())
        canvas.fill(QColor("#ffffff"))
        painter = QPainter(canvas)
        square = 8
        for y in range(0, canvas.height(), square):
            for x in range(0, canvas.width(), square):
                if (x // square + y // square) % 2:
                    painter.fillRect(x, y, square, square, QColor("#e4e4e4"))
        painter.drawPixmap(0, 0, scaled)
        painter.end()

        self.preview.setPixmap(canvas)

    # ---- Saving -----------------------------------------------------------

    def save_image(self):
        design = self.current_design()
        width, height = design.width, design.height
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

        suffix = path.suffix.lower()
        message = f"Saved {path.name}"

        if suffix == ".svg":
            try:
                path.write_text(make_svg(design), encoding="utf-8")
            except OSError as error:
                QMessageBox.warning(self, APP_NAME, f"Could not save:\n{error}")
                return
        else:
            image = make_image(design)

            if suffix in (".jpg", ".jpeg"):
                # JPEG can't be see-through, so rounded corners are filled
                # with white
                flat = QImage(width, height, QImage.Format.Format_RGB32)
                flat.fill(QColor("#ffffff"))
                painter = QPainter(flat)
                painter.drawImage(0, 0, image)
                painter.end()
                image = flat
                quality = 90
                if design.radius > 0:
                    message += " (JPEG can't be see-through: the corners are white)"
            else:
                quality = -1

            if not image.save(str(path), None, quality):
                QMessageBox.warning(self, APP_NAME, f"Could not save:\n{path}")
                return

        self.last_folder = str(path.parent)
        self.last_saved = path
        self.last_saved_size = (width, height)
        self.save_settings()
        self.status.setText(message)

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
            f"{PROJECT_URL}"
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
    window = PlaceHolderWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

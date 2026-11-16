<img src="icons/placeholder-icon-128.png" width="96" alt="PlaceHolder icon">

# PlaceHolder

**Placeholder images for web pages, made on your own computer.**

PlaceHolder is a small Linux program that makes plain placeholder images: a solid colour with the size, or your own words, in the middle. Use them to lay out a web page before the real pictures are ready, then swap the real ones in later.

It works offline, so there's no need for a placeholder website, and the images are saved with your site.

---

## Features

- Any size from 1 to 8000 pixels, or pick one from a list of common sizes
- Your choice of background and text colour
- The text shows the size, such as **640 × 480**, or your own words, such as *Hero image*. It sizes itself to fit
- An optional border with diagonal lines, the classic placeholder look
- A live preview as you change things
- Saves as **PNG**, **JPEG** or **SVG**:
  - PNG is the default and works in every browser
  - SVG is tiny and stays sharp at any size
- **Copy `<img>` Tag** copies a ready-made tag, with the width and height, for the image you just saved
- Remembers your last size, colours, text and folder

---

## Installation

### Option 1: standalone download (easiest)

1. Download `placeholder-linux-vX.Y.tar.gz` from the [Releases](../../releases) page.
2. Extract it, open a terminal in the extracted folder and run:

   ```
   ./install.sh
   ```

3. PlaceHolder appears in your applications menu. To remove it later, run `./install.sh --uninstall`.

The standalone build is for 64-bit Linux and includes everything it needs, so you do not need to install Python or Qt.

### Option 2: run from source

You need Python 3 and PyQt6:

```
sudo apt install python3-pyqt6
python3 placeholder.py
```

Or in a virtual environment:

```
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python3 placeholder.py
```

---

## Using it

1. Set the width and height, or choose from **Common sizes**.
2. Click **Background** and **Text colour** to pick the colours.
3. Leave **Text** empty to show the size, or type your own.
4. Tick **Border and diagonal lines** if you'd like them.
5. Click **Save Image...** and choose PNG, JPEG or SVG from the file type list. The name suggested is like `placeholder-640x480.png`.
6. Click **Copy `<img>` Tag** and paste the tag into your page.

When an SVG is shown in a browser, its text uses Arial or Helvetica, whichever the visitor has, so the lettering may look slightly different from the preview. The size and position stay the same.

---

## Settings

PlaceHolder keeps your last choices in `~/.config/PlaceHolder/settings.json`. Delete that file to go back to the defaults.

---

## Building the standalone program

From the project folder:

```
python3 -m venv venv
./venv/bin/pip install -r requirements.txt pyinstaller
./build.sh
./make-release.sh 1.0
```

This creates `release/placeholder-linux-v1.0.tar.gz`.

Pushing a version tag, such as `v1.0`, to GitHub builds the release automatically on Ubuntu 22.04 and attaches the download to a GitHub Release. The tag must match `APP_VERSION` in `placeholder.py`.

---

## Project layout

```
placeholder.py      the program
icons/              the program icon (SVG source and PNG sizes)
build.sh            builds the standalone program with PyInstaller
make-release.sh     packs the standalone program for download
install.sh          installer included in the download
requirements.txt    the Python package needed to run from source
```

---

## Licence

PlaceHolder is released under the **GNU General Public License v3.0**, because it is built on PyQt6, which is GPL-licensed. See the `LICENSE` file for the full text.

---

## Credits

PlaceHolder is a hobby project, written for my own use and shared in case it is useful to others. It is a companion to my HTML editor, [TelaEdit](https://github.com/toxtoo/TelaEdit).

**Built with Claude.** I'm not a programmer. PlaceHolder was developed in conversation with [Claude](https://claude.ai) from Anthropic. I decided what it should do, designed the icon and tested it on my own computers. Claude wrote the code and redrew the icon from my design.

Built with [Qt](https://www.qt.io/) and [PyQt6](https://www.riverbankcomputing.com/software/pyqt/), and packaged with [PyInstaller](https://pyinstaller.org/).

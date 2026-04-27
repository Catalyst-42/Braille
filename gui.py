import math
import tkinter as tk
from tkinter import filedialog, ttk

from PIL import Image, ImageTk

from braille import image_to_text, text_to_image


class Braille:
    ZOOM_STEPS = [0.25, 0.5, 1, 1.5, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64]
    TILE_WIDTH = 2
    TILE_HEIGHT = 3
    SELECTION_COLOR = '#d83b3b'

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('Braille')
        self.root.geometry('1000x600')
        self.root.minsize(1000, 600)

        self.generated_image = None
        self.generated_photo = None
        self.generated_preview_key = None
        self.encode_image_item = None

        self.original_image = None
        self.source_image = None
        self.processed_image = None
        self.decode_photo = None
        self.decode_cache_key = None
        self.decode_image_item = None
        self.decode_selection_item = None
        self.decode_zoom = 2
        self.decode_pan_x = 48
        self.decode_pan_y = 48
        self.selection_anchor = None
        self.selection_region = None
        self.selection_preview_region = None
        self.pan_drag_active = False
        self.pan_drag_start = (0, 0)

        self._build_layout()
        self._bind_events()
        self._update_save_menu_state()

    def _build_layout(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.encode_tab = ttk.Frame(self.notebook)
        self.decode_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.encode_tab, text='Encoding')
        self.notebook.add(self.decode_tab, text='Decoding')

        self._build_encode_tab()
        self._build_decode_tab()

    def _build_encode_tab(self):
        self.encode_tab.columnconfigure(0, weight=1)
        self.encode_tab.columnconfigure(1, weight=0)
        self.encode_tab.rowconfigure(0, weight=1)

        preview_wrap = ttk.Frame(self.encode_tab, padding=10)
        preview_wrap.grid(row=0, column=0, sticky='nsew')
        preview_wrap.columnconfigure(0, weight=1)
        preview_wrap.rowconfigure(0, weight=1)

        self.encode_canvas = tk.Canvas(preview_wrap, highlightthickness=0)
        self.encode_canvas.grid(row=0, column=0, sticky='nsew')

        controls = ttk.Frame(self.encode_tab, padding=(10, 10, 10, 10), width=350)
        controls.grid(row=0, column=1, sticky='ns')
        controls.grid_propagate(False)
        controls.columnconfigure(0, weight=1)

        # Input
        ttk.Label(controls, text='Input').grid(
            row=0, column=0, sticky='w', pady=(0, 10)
        )

        self.encode_text = tk.Text(controls, wrap=tk.WORD, highlightthickness=0)
        self.encode_text.grid(row=1, column=0, sticky='nsew', pady=(0, 10))

        # Encode
        self.generate_button = ttk.Button(
            controls, text='Encode', command=self.generate_image
        )
        self.generate_button.grid(row=2, column=0, sticky='ew', pady=(0, 10))

        # Save image
        self.save_button = ttk.Button(
            controls, text='Save image', command=self.save_generated_image
        )
        self.save_button.grid(row=3, column=0, sticky='ew')

        controls.rowconfigure(1, weight=1)

        # Fill all canvas on resize
        self.encode_canvas.bind(
            '<Configure>', lambda _: self.render_generated_preview()
        )

    def _build_decode_tab(self):
        self.decode_tab.columnconfigure(0, weight=1)
        self.decode_tab.columnconfigure(1, weight=0)
        self.decode_tab.rowconfigure(0, weight=1)

        left = ttk.Frame(self.decode_tab, padding=10)
        left.grid(row=0, column=0, sticky='nsew')
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        self.decode_canvas = tk.Canvas(left, highlightthickness=0, cursor='crosshair')
        self.decode_canvas.grid(row=0, column=0, sticky='nsew')

        right = ttk.Frame(self.decode_tab, padding=(10, 10, 10, 10), width=350)
        right.grid(row=0, column=1, sticky='ns')
        right.grid_propagate(False)
        right.columnconfigure(0, weight=1)
        row = 0

        # Open image
        ttk.Button(right, text='Open image', command=self.load_image).grid(
            row=row, column=0, sticky='ew'
        )
        row += 1

        # Zoom controls
        zoom_frame = ttk.Frame(right)
        zoom_frame.grid(row=row, column=0, sticky='ew', pady=(10, 0))
        zoom_frame.columnconfigure(0, weight=0)
        zoom_frame.columnconfigure(1, weight=1)

        ttk.Label(zoom_frame, text='Zoom').grid(
            row=0, column=0, sticky='w', padx=(0, 10)
        )

        zoom_controls = ttk.Frame(zoom_frame)
        zoom_controls.grid(row=0, column=1, sticky='e')

        # Zoom scale level
        self.zoom_label = ttk.Label(
            zoom_controls, text=f'{self.decode_zoom}x', width=6, anchor='center'
        )
        self.zoom_label.pack(side=tk.LEFT, padx=(0, 10))

        # Zoom +
        ttk.Button(
            zoom_controls, text='+', width=6, command=lambda: self.step_zoom(1)
        ).pack(side=tk.RIGHT, padx=(0, 0))

        # Zoom -
        ttk.Button(
            zoom_controls, text='-', width=6, command=lambda: self.step_zoom(-1)
        ).pack(side=tk.RIGHT, padx=(0, 5))
        row += 1

        # Threshold
        threshold_frame = ttk.Frame(right)
        threshold_frame.grid(row=row, column=0, sticky='ew', pady=(10, 0))
        threshold_frame.columnconfigure(0, weight=1)

        # Label
        ttk.Label(threshold_frame, text='Threshold').grid(row=0, column=0, sticky='w')

        # Slider value
        slider_default = 128
        self.threshold_value_label = ttk.Label(threshold_frame, text=slider_default)
        self.threshold_value_label.grid(row=0, column=1, sticky='e', padx=(10, 0))
        row += 1

        # Slider
        self.threshold_var = tk.IntVar(value=slider_default)
        ttk.Scale(
            right,
            from_=0,
            to=255,
            variable=self.threshold_var,
            command=self.on_threshold_changed,
        ).grid(row=row, column=0, sticky='ew')
        row += 1

        # Special
        special_frame = ttk.Frame(right)
        special_frame.grid(row=row, column=0, sticky='ew', pady=(10, 0))
        special_frame.columnconfigure(0, weight=1)

        # Label
        ttk.Label(special_frame, text='Special').grid(row=0, column=0, sticky='w')

        # Invert
        self.invert_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            special_frame,
            text='Invert colors',
            variable=self.invert_var,
            command=self.apply_processing,
        ).grid(row=0, column=1, sticky='e')
        row += 1

        # Downscale
        downscale_frame = ttk.Frame(right)
        downscale_frame.grid(row=row, column=0, sticky='ew', pady=(10, 0))
        downscale_frame.columnconfigure(0, weight=0)
        downscale_frame.columnconfigure(1, weight=1)

        # Label
        ttk.Label(downscale_frame, text='Downscale').grid(
            row=0, column=0, sticky='w', padx=(0, 10)
        )

        # Entry
        downscale_default = 1
        self.downscale_var = tk.StringVar(value=downscale_default)
        downscale_entry = ttk.Entry(
            downscale_frame, textvariable=self.downscale_var, width=10
        )
        downscale_entry.grid(row=0, column=1, sticky='w')
        downscale_entry.bind('<Return>', lambda e: self.apply_downscale())

        # Apply and Rest
        ttk.Button(
            downscale_frame, text='Apply', width=6, command=self.apply_downscale
        ).grid(row=0, column=2, sticky='w', padx=(10, 0))

        ttk.Button(
            downscale_frame, text='Reset', width=6, command=self.reset_downscale
        ).grid(row=0, column=3, sticky='w', padx=(5, 0))
        row += 1

        # Language
        lang_frame = ttk.Frame(right)
        lang_frame.grid(row=row, column=0, sticky='ew', pady=(10, 0))
        lang_frame.columnconfigure(0, weight=1)

        ttk.Label(lang_frame, text='Language').grid(row=0, column=0, sticky='w')

        # Latin and Russian
        lang_buttons = ttk.Frame(lang_frame)
        lang_buttons.grid(row=0, column=1, sticky='e')
        self.decode_lang = tk.StringVar(value='latin')

        ttk.Radiobutton(
            lang_buttons, text='Latin', variable=self.decode_lang, value='latin'
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(
            lang_buttons, text='Russian', variable=self.decode_lang, value='russian'
        ).pack(side=tk.LEFT)
        row += 1

        # Clear selection
        self.clear_sel_button = ttk.Button(
            right,
            text='Clear selection',
            command=self.clear_selection,
            state=tk.DISABLED,
        )
        self.clear_sel_button.grid(row=row, column=0, sticky='ew', pady=(10, 0))
        row += 1

        # Decode
        self.recognize_button = ttk.Button(
            right, text='Decode', command=self.recognize_selection, state=tk.DISABLED
        )
        self.recognize_button.grid(row=row, column=0, sticky='ew', pady=(10, 0))
        row += 1

        # Output
        ttk.Label(right, text='Output').grid(
            row=row, column=0, sticky='w', pady=(10, 0)
        )
        row += 1

        self.result_text = tk.Text(right, wrap=tk.WORD, highlightthickness=0)
        self.result_text.grid(row=row, column=0, sticky='nsew')
        right.rowconfigure(row, weight=1)

    def _bind_events(self):
        self.decode_canvas.bind('<ButtonPress-1>', self.on_left_press)
        self.decode_canvas.bind('<B1-Motion>', self.on_left_drag)
        self.decode_canvas.bind('<ButtonRelease-1>', self.on_left_release)
        self.decode_canvas.bind('<ButtonPress-2>', self.start_pan_drag)
        self.decode_canvas.bind('<B2-Motion>', self.on_pan_drag)
        self.decode_canvas.bind('<ButtonRelease-2>', self.stop_pan_drag)
        self.decode_canvas.bind('<ButtonPress-3>', self.start_pan_drag)
        self.decode_canvas.bind('<B3-Motion>', self.on_pan_drag)
        self.decode_canvas.bind('<ButtonRelease-3>', self.stop_pan_drag)
        self.decode_canvas.bind('<MouseWheel>', self.on_zoom_wheel)
        self.decode_canvas.bind('<Button-4>', self.on_zoom_wheel_linux)
        self.decode_canvas.bind('<Button-5>', self.on_zoom_wheel_linux)

        self.root.bind_all('<plus>', lambda _: self.step_zoom(1))
        self.root.bind_all('<equal>', lambda _: self.step_zoom(1))
        self.root.bind_all('<minus>', lambda _: self.step_zoom(-1))

    def on_zoom_wheel(self, event):
        direction = 1 if event.delta > 0 else -1
        self.step_zoom(direction, pivot=(event.x, event.y))

    def on_zoom_wheel_linux(self, event):
        direction = 1 if event.num == 4 else -1
        self.step_zoom(direction, pivot=(event.x, event.y))

    def on_threshold_changed(self, _):
        self.threshold_value_label.config(text=str(int(self.threshold_var.get())))
        self.apply_processing()

    def apply_downscale(self):
        if self.source_image is None or self.original_image is None:
            return
        try:
            factor = int(self.downscale_var.get())

            self.source_image = self.original_image.copy()
            new_w = max(1, self.source_image.width // factor)
            new_h = max(1, self.source_image.height // factor)

            self.source_image = self.source_image.resize(
                (new_w, new_h), Image.Resampling.NEAREST
            )
            self.decode_cache_key = None

            self.clear_selection()
            self.apply_processing(reset_pan=True)

        except ValueError:
            return

    def reset_downscale(self):
        if self.original_image is None:
            return

        self.source_image = self.original_image.copy()
        self.downscale_var.set('1')
        self.decode_cache_key = None

        self.clear_selection()
        self.apply_processing(reset_pan=True)

    def generate_image(self):
        text = self.encode_text.get('1.0', tk.END).strip()
        if not text:
            return
        try:
            self.generated_image = text_to_image(text)
        except Exception as exception:
            print(exception)
            return

        self.generated_preview_key = None
        self.render_generated_preview()
        self._update_save_menu_state()

    def render_generated_preview(self):
        canvas_width = max(self.encode_canvas.winfo_width(), 1)
        canvas_height = max(self.encode_canvas.winfo_height(), 1)

        if self.generated_image is None:
            if self.encode_image_item:
                self.encode_canvas.delete(self.encode_image_item)
                self.encode_image_item = None
            return

        src_w, src_h = self.generated_image.size
        scale = min(canvas_width / src_w, canvas_height / src_h)
        scale = max(scale, 0.1)
        draw_w = int(src_w * scale)
        draw_h = int(src_h * scale)
        preview_key = (id(self.generated_image), canvas_width, canvas_height)

        if self.generated_preview_key != preview_key:
            resized = self.generated_image.resize(
                (draw_w, draw_h), Image.Resampling.NEAREST
            ).convert('RGBA')
            self.generated_photo = ImageTk.PhotoImage(resized)
            self.generated_preview_key = preview_key

        x = (canvas_width - draw_w) / 2
        y = (canvas_height - draw_h) / 2
        if self.encode_image_item is None:
            self.encode_image_item = self.encode_canvas.create_image(
                x, y, anchor=tk.NW, image=self.generated_photo
            )
        else:
            self.encode_canvas.itemconfig(
                self.encode_image_item, image=self.generated_photo
            )
            self.encode_canvas.coords(self.encode_image_item, x, y)

    def save_generated_image(self):
        if self.generated_image is None:
            return

        path = filedialog.asksaveasfilename(
            title='Save image', defaultextension='.png', filetypes=[('PNG', '*.png')]
        )

        if not path:
            return

        self.generated_image.save(path)

    def load_image(self):
        path = filedialog.askopenfilename(
            title='Open image', filetypes=[('Images', '*.png *.jpg *.jpeg *.bmp')]
        )

        if not path:
            return

        self.original_image = Image.open(path).convert('RGBA')
        self.source_image = self.original_image.copy()

        self.downscale_var.set('1')
        self.decode_cache_key = None
        self.clear_selection()

        self.result_text.delete('1.0', tk.END)
        self.recognize_button.config(state=tk.NORMAL)
        self.apply_processing(reset_pan=True)

    def apply_processing(self, reset_pan=False):
        if self.source_image is None:
            self.processed_image = None
            self.render_decode_canvas()
            return

        threshold = int(self.threshold_var.get())
        grayscale = self.source_image.convert('L')
        width, height = grayscale.size

        bw = Image.new('L', (width, height))
        bw_pixels = bw.load()
        src_pixels = grayscale.load()

        for y in range(height):
            for x in range(width):
                if self.invert_var.get():
                    bw_pixels[x, y] = 255 if src_pixels[x, y] < threshold else 0
                else:
                    bw_pixels[x, y] = 255 if src_pixels[x, y] > threshold else 0

        self.processed_image = bw.convert('1', dither=Image.Dither.NONE)

        self.decode_cache_key = None
        if reset_pan:
            self.reset_decode_view()
        self._clamp_selection_to_image()
        self.render_decode_canvas()

    def reset_decode_view(self):
        self.decode_zoom = 2
        if self.processed_image is not None:
            canvas_w = max(self.decode_canvas.winfo_width(), 1)
            canvas_h = max(self.decode_canvas.winfo_height(), 1)
            draw_w = self.processed_image.width * self.decode_zoom
            draw_h = self.processed_image.height * self.decode_zoom
            self.decode_pan_x = (canvas_w - draw_w) / 2
            self.decode_pan_y = (canvas_h - draw_h) / 2
        else:
            self.decode_pan_x = 48
            self.decode_pan_y = 48

        self._update_zoom_label()
        self.render_decode_canvas()

    def clear_selection(self, update_canvas=True):
        self.selection_anchor = None
        self.selection_region = None
        self.selection_preview_region = None
        if update_canvas:
            self._update_selection_overlay()

        # Disable the button when selection cleared
        if hasattr(self, 'clear_sel_button'):
            self.clear_sel_button.config(state=tk.DISABLED)

    def recognize_selection(self):
        if self.processed_image is None:
            return

        image = self.processed_image
        region = self.selection_region
        if region is not None:
            image = image.crop(region)

        try:
            parsed_text = image_to_text(image, language=self.decode_lang.get())
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert('1.0', parsed_text)
        except Exception as exception:
            print(exception)

        self._update_selection_overlay()

    def on_left_press(self, event):
        if self.processed_image is None:
            return
        image_point = self.canvas_to_image_point(event.x, event.y)
        if image_point is None:
            return
        ax, ay = image_point
        if (
            self.processed_image.width < self.TILE_WIDTH
            or self.processed_image.height < self.TILE_HEIGHT
        ):
            return
        ax = min(max(ax, 0), self.processed_image.width - self.TILE_WIDTH)
        ay = min(max(ay, 0), self.processed_image.height - self.TILE_HEIGHT)
        self.selection_anchor = (ax, ay)
        self.selection_preview_region = self._build_region_from_anchor(ax, ay, ax, ay)
        self.selection_region = self.selection_preview_region
        self._update_selection_overlay()
        self.clear_sel_button.config(state=tk.NORMAL)

    def on_left_drag(self, event):
        if self.pan_drag_active:
            self.on_pan_drag(event)
            return
        if self.selection_anchor is None or self.processed_image is None:
            return
        image_point = self.canvas_to_image_point(event.x, event.y, clamp=True)
        if image_point is None:
            return
        ax, ay = self.selection_anchor
        self.selection_preview_region = self._build_region_from_anchor(
            ax, ay, image_point[0], image_point[1]
        )
        self.selection_region = self.selection_preview_region
        self._update_selection_overlay()

    def on_left_release(self, event):
        if self.pan_drag_active:
            self.stop_pan_drag(event)
            return
        if self.selection_anchor is None:
            return
        image_point = self.canvas_to_image_point(event.x, event.y, clamp=True)
        if image_point is None:
            image_point = self.selection_anchor
        ax, ay = self.selection_anchor
        self.selection_region = self._build_region_from_anchor(
            ax, ay, image_point[0], image_point[1]
        )
        self.selection_preview_region = None
        self.selection_anchor = None
        self._update_selection_overlay()

        # Ensure button is enabled when selection exists
        if self.selection_region is not None:
            self.clear_sel_button.config(state=tk.NORMAL)
        else:
            self.clear_sel_button.config(state=tk.DISABLED)

    def _build_region_from_anchor(self, anchor_x, anchor_y, current_x, current_y):
        if self.processed_image is None:
            return None
        width = self.processed_image.width
        height = self.processed_image.height
        horizontal_tiles = max(
            1, math.ceil((abs(current_x - anchor_x) + 1) / self.TILE_WIDTH)
        )
        vertical_tiles = max(
            1, math.ceil((abs(current_y - anchor_y) + 1) / self.TILE_HEIGHT)
        )
        if current_x >= anchor_x:
            max_tiles_x = max(1, (width - anchor_x) // self.TILE_WIDTH)
            horizontal_tiles = min(horizontal_tiles, max_tiles_x)
            left = anchor_x
        else:
            max_tiles_x = max(1, (anchor_x + 1) // self.TILE_WIDTH)
            horizontal_tiles = min(horizontal_tiles, max_tiles_x)
            left = anchor_x - horizontal_tiles * self.TILE_WIDTH + 1
        if current_y >= anchor_y:
            max_tiles_y = max(1, (height - anchor_y) // self.TILE_HEIGHT)
            vertical_tiles = min(vertical_tiles, max_tiles_y)
            top = anchor_y
        else:
            max_tiles_y = max(1, (anchor_y + 1) // self.TILE_HEIGHT)
            vertical_tiles = min(vertical_tiles, max_tiles_y)
            top = anchor_y - vertical_tiles * self.TILE_HEIGHT + 1
        left = max(0, left)
        top = max(0, top)
        right = min(width, left + horizontal_tiles * self.TILE_WIDTH)
        bottom = min(height, top + vertical_tiles * self.TILE_HEIGHT)
        return left, top, right, bottom

    def start_pan_drag(self, event):
        self.pan_drag_active = True
        self.pan_drag_start = (event.x, event.y)
        self.decode_canvas.configure(cursor='fleur')

    def on_pan_drag(self, event):
        if not self.pan_drag_active:
            return
        dx = event.x - self.pan_drag_start[0]
        dy = event.y - self.pan_drag_start[1]
        self.pan_drag_start = (event.x, event.y)
        self.decode_pan_x += dx
        self.decode_pan_y += dy
        self._update_canvas_positions()

    def stop_pan_drag(self, _):
        self.pan_drag_active = False
        self.decode_canvas.configure(
            cursor='crosshair'
        )

    def step_zoom(self, direction, pivot=None):
        current_index = self.ZOOM_STEPS.index(self.decode_zoom)
        next_index = current_index + (1 if direction > 0 else -1)
        next_index = max(0, min(next_index, len(self.ZOOM_STEPS) - 1))
        new_zoom = self.ZOOM_STEPS[next_index]
        if new_zoom == self.decode_zoom:
            return
        if pivot is None and self.processed_image is not None:
            canvas_w = self.decode_canvas.winfo_width()
            canvas_h = self.decode_canvas.winfo_height()
            pivot = (canvas_w // 2, canvas_h // 2)
        if pivot is not None and self.processed_image is not None:
            image_x = (pivot[0] - self.decode_pan_x) / self.decode_zoom
            image_y = (pivot[1] - self.decode_pan_y) / self.decode_zoom
            self.decode_zoom = new_zoom
            self.decode_pan_x = pivot[0] - image_x * self.decode_zoom
            self.decode_pan_y = pivot[1] - image_y * self.decode_zoom
        else:
            self.decode_zoom = new_zoom
        self.decode_cache_key = None
        self._update_zoom_label()
        self.render_decode_canvas()

    def _update_zoom_label(self):
        if self.decode_zoom == int(self.decode_zoom):
            self.zoom_label.config(text=f'{int(self.decode_zoom)}x')
        else:
            self.zoom_label.config(text=f'{self.decode_zoom}x')

    def canvas_to_image_point(self, canvas_x, canvas_y, clamp=False):
        if self.processed_image is None:
            return None
        img_x = (canvas_x - self.decode_pan_x) / self.decode_zoom
        img_y = (canvas_y - self.decode_pan_y) / self.decode_zoom
        if clamp:
            img_x = min(max(int(img_x), 0), self.processed_image.width - 1)
            img_y = min(max(int(img_y), 0), self.processed_image.height - 1)
            return img_x, img_y
        if (
            0 <= img_x < self.processed_image.width
            and 0 <= img_y < self.processed_image.height
        ):
            return (int(img_x), int(img_y))
        return None

    def _clamp_selection_to_image(self):
        if self.selection_region is None or self.processed_image is None:
            return
        left, top, right, bottom = self.selection_region
        width = self.processed_image.width
        height = self.processed_image.height
        left = min(max(left, 0), max(0, width - self.TILE_WIDTH))
        top = min(max(top, 0), max(0, height - self.TILE_HEIGHT))
        right = min(width, right)
        bottom = min(height, bottom)
        cells_x = max(1, (right - left) // self.TILE_WIDTH)
        cells_y = max(1, (bottom - top) // self.TILE_HEIGHT)
        right = min(width, left + cells_x * self.TILE_WIDTH)
        bottom = min(height, top + cells_y * self.TILE_HEIGHT)
        self.selection_region = (left, top, right, bottom)

    def render_decode_canvas(self):
        if self.processed_image is None:
            if self.decode_image_item is not None:
                self.decode_canvas.delete(self.decode_image_item)
                self.decode_image_item = None
            if self.decode_selection_item is not None:
                self.decode_canvas.delete(self.decode_selection_item)
                self.decode_selection_item = None
            return
        self._ensure_decode_photo()
        if self.decode_image_item is None:
            self.decode_image_item = self.decode_canvas.create_image(
                self.decode_pan_x,
                self.decode_pan_y,
                anchor=tk.NW,
                image=self.decode_photo,
            )
        else:
            self.decode_canvas.itemconfig(
                self.decode_image_item, image=self.decode_photo
            )
        self._update_canvas_positions()

    def _draw_selection_overlay(self, region):
        left, top, right, bottom = region
        x1 = self.decode_pan_x + left * self.decode_zoom
        y1 = self.decode_pan_y + top * self.decode_zoom
        x2 = self.decode_pan_x + right * self.decode_zoom
        y2 = self.decode_pan_y + bottom * self.decode_zoom
        if self.decode_selection_item is None:
            self.decode_selection_item = self.decode_canvas.create_rectangle(
                x1, y1, x2, y2, outline=self.SELECTION_COLOR, width=2
            )
        else:
            self.decode_canvas.coords(self.decode_selection_item, x1, y1, x2, y2)

    def _ensure_decode_photo(self):
        cache_key = (id(self.processed_image), self.decode_zoom)
        if self.decode_cache_key == cache_key:
            return
        new_w = int(self.processed_image.width * self.decode_zoom)
        new_h = int(self.processed_image.height * self.decode_zoom)
        temp = self.processed_image.convert('L')
        resized = temp.resize((new_w, new_h), Image.Resampling.NEAREST)
        self.decode_photo = ImageTk.PhotoImage(resized)
        self.decode_cache_key = cache_key

    def _update_canvas_positions(self):
        if self.decode_image_item is not None:
            self.decode_canvas.coords(
                self.decode_image_item, self.decode_pan_x, self.decode_pan_y
            )
        self._update_selection_overlay()

    def _update_selection_overlay(self):
        region = self.selection_preview_region or self.selection_region
        if region is None:
            if self.decode_selection_item is not None:
                self.decode_canvas.delete(self.decode_selection_item)
                self.decode_selection_item = None
            return
        self._draw_selection_overlay(region)

    def _update_save_menu_state(self):
        state = tk.NORMAL if self.generated_image is not None else tk.DISABLED
        if hasattr(self, 'save_button'):
            self.save_button.config(state=state)


# Run
root = tk.Tk()
app = Braille(root)
root.mainloop()

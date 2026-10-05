
from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from .generator import (
    MAX_LENGTH,
    MIN_LENGTH,
    Options,
    entropy_bits,
    generate_password,
    strength_label,
)

SURFACE = "#f7f8fa"
TEXT = "#1f2933"
MUTED = "#616e7c"
ACCENT = "#0f766e"
ACCENT_HOVER = "#115e59"
BORDER = "#cbd2d9"
STRENGTH_COLORS = {
    "Weak": "#c0392b",
    "Fair": "#d68910",
    "Strong": "#2e8b57",
    "Very strong": "#0f766e",
}

PADDING = 16
GAP = 8
DEFAULT_LENGTH = 16
CLIPBOARD_CLEAR_MS = 30_000
MASK_CHAR = "\u2022"

OPTION_LABELS = (
    ("lowercase", "Lowercase (a-z)"),
    ("uppercase", "Uppercase (A-Z)"),
    ("digits", "Digits (0-9)"),
    ("symbols", "Symbols (!@#$...)"),
    ("exclude_ambiguous", "Exclude look-alikes (I, l, 1, O, 0, o)"),
)


def progress_style(label: str) -> str:
    return f"{label.replace(' ', '')}.Horizontal.TProgressbar"


class PasswordGeneratorApp(ttk.Frame):
    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root, padding=PADDING)
        self.password_var = tk.StringVar()
        self.length_var = tk.IntVar(value=DEFAULT_LENGTH)
        self.reveal_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar()
        self.option_vars = {
            name: tk.BooleanVar(value=name != "exclude_ambiguous") for name, _ in OPTION_LABELS
        }
        self.clipboard_job: str | None = None

        self._configure_styles(root)
        self._build_layout()
        root.bind("<Return>", lambda _event: self.generate())
        self.generate()

    def _configure_styles(self, root: tk.Tk) -> None:
        style = ttk.Style(root)
        style.theme_use("clam")
        root.configure(background=SURFACE)
        style.configure(".", background=SURFACE, foreground=TEXT)
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("TCheckbutton", focuscolor=SURFACE)
        style.configure("TButton", padding=(12, 8), bordercolor=BORDER)
        style.configure("Accent.TButton", background=ACCENT, foreground="white", bordercolor=ACCENT)
        style.map("Accent.TButton", background=[("active", ACCENT_HOVER)])
        for label, color in STRENGTH_COLORS.items():
            style.configure(
                progress_style(label),
                background=color,
                troughcolor=BORDER,
                bordercolor=SURFACE,
                thickness=8,
            )

    def _build_layout(self) -> None:
        mono = tkfont.nametofont("TkFixedFont").copy()
        mono.configure(size=14)

        self.password_entry = ttk.Entry(
            self, textvariable=self.password_var, state="readonly", font=mono, width=32
        )
        self.password_entry.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.strength_bar = ttk.Progressbar(self, maximum=100, mode="determinate")
        self.strength_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(GAP, 0))
        self.strength_text = ttk.Label(self, style="Muted.TLabel")
        self.strength_text.grid(row=2, column=0, columnspan=2, sticky="w", pady=(GAP // 2, PADDING))

        ttk.Label(self, text="Length").grid(row=3, column=0, sticky="w")
        self.length_text = ttk.Label(self, text=str(DEFAULT_LENGTH), width=4, anchor="e")
        self.length_text.grid(row=3, column=1, sticky="e")
        self.length_scale = ttk.Scale(
            self, from_=MIN_LENGTH, to=MAX_LENGTH, command=self._on_length_change
        )
        self.length_scale.set(DEFAULT_LENGTH)
        self.length_scale.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(GAP // 2, PADDING))

        for row, (name, label) in enumerate(OPTION_LABELS, start=5):
            ttk.Checkbutton(
                self, text=label, variable=self.option_vars[name], command=self.generate
            ).grid(row=row, column=0, columnspan=2, sticky="w", pady=2)

        ttk.Checkbutton(
            self, text="Show password", variable=self.reveal_var, command=self._toggle_reveal
        ).grid(row=10, column=0, columnspan=2, sticky="w", pady=(GAP, PADDING))

        ttk.Button(self, text="Generate", style="Accent.TButton", command=self.generate).grid(
            row=11, column=0, sticky="ew", padx=(0, GAP // 2)
        )
        ttk.Button(self, text="Copy", command=self.copy_to_clipboard).grid(
            row=11, column=1, sticky="ew", padx=(GAP // 2, 0)
        )

        ttk.Label(self, textvariable=self.status_var, style="Muted.TLabel").grid(
            row=12, column=0, columnspan=2, sticky="w", pady=(PADDING, 0)
        )
        self.columnconfigure((0, 1), weight=1)

    def _on_length_change(self, value: str) -> None:
        length = round(float(value))
        if length != self.length_var.get():
            self.length_var.set(length)
            self.length_text.configure(text=str(length))
            self.generate()

    def _toggle_reveal(self) -> None:
        self.password_entry.configure(show="" if self.reveal_var.get() else MASK_CHAR)

    def current_options(self) -> Options:
        return Options(
            length=self.length_var.get(),
            **{name: var.get() for name, var in self.option_vars.items()},
        )

    def generate(self) -> None:
        options = self.current_options()
        try:
            self.password_var.set(generate_password(options))
        except ValueError as error:
            self.password_var.set("")
            self.status_var.set(str(error))
            self._show_strength(0.0)
            return
        self.status_var.set("")
        self._show_strength(entropy_bits(options))

    def _show_strength(self, bits: float) -> None:
        label = strength_label(bits)
        self.strength_bar.configure(value=min(bits, 100), style=progress_style(label))
        self.strength_text.configure(text=f"{label}  -  about {bits:.0f} bits of entropy")

    def copy_to_clipboard(self) -> None:
        password = self.password_var.get()
        if not password:
            self.status_var.set("Nothing to copy. Fix the options above first.")
            return
        self.clipboard_clear()
        self.clipboard_append(password)
        self.status_var.set(f"Copied. Clipboard clears in {CLIPBOARD_CLEAR_MS // 1000} seconds.")
        if self.clipboard_job:
            self.after_cancel(self.clipboard_job)
        self.clipboard_job = self.after(CLIPBOARD_CLEAR_MS, lambda: self._clear_clipboard(password))

    def _clear_clipboard(self, copied_password: str) -> None:
        try:
            if self.clipboard_get() == copied_password:
                self.clipboard_clear()
                self.status_var.set("Clipboard cleared.")
        except tk.TclError:
            pass


def main() -> None:
    root = tk.Tk()
    root.title("Password Generator")
    root.resizable(False, False)
    PasswordGeneratorApp(root).pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()

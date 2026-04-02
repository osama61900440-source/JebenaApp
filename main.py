"""
Jebena & Sefed - Sales Manager
Samsung Galaxy S14 Android - KivyMD
"""

# ── Standard library ──────────────────────────────────────
import os
import sqlite3
from datetime import date

# ── Kivy core ─────────────────────────────────────────────
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import (
    ScreenManager, Screen,
    FadeTransition, SlideTransition
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

# ── KivyMD widgets ────────────────────────────────────────
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    MDList,
    OneLineListItem,
    TwoLineListItem,
    ThreeLineListItem,
)
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar


# ═══════════════════════════════════════════════════════════
#  DATABASE
# ═══════════════════════════════════════════════════════════

def _db_path():
    """Return a writable database path on Android and desktop."""
    try:
        # Android: use the app's private data directory
        from android import mActivity  # noqa
        ctx = mActivity.getApplicationContext()
        return os.path.join(str(ctx.getFilesDir()), "jebena.db")
    except Exception:
        # Desktop / Colab
        return os.path.join(os.path.expanduser("~"), "jebena.db")


DB_PATH = _db_path()


def db():
    """Open and return a SQLite connection."""
    return sqlite3.connect(DB_PATH)


def setup_db():
    """Create tables and seed default data."""
    with db() as con:
        cur = con.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username  TEXT    UNIQUE NOT NULL,
                password  TEXT    NOT NULL,
                role      TEXT    NOT NULL CHECK(role IN ('owner','staff')),
                full_name TEXT    DEFAULT ''
            )""")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                category   TEXT    DEFAULT 'jebena',
                qty        INTEGER DEFAULT 0,
                cost       REAL    DEFAULT 0,
                price      REAL    DEFAULT 0,
                min_qty    INTEGER DEFAULT 3
            )""")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id  INTEGER,
                product_name TEXT,
                qty         INTEGER,
                unit_price  REAL,
                total       REAL,
                payment     TEXT    DEFAULT 'Cash',
                staff_id    INTEGER,
                staff_name  TEXT,
                created_at  TEXT    DEFAULT (datetime('now','localtime'))
            )""")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                category   TEXT,
                amount     REAL,
                note       TEXT,
                created_at TEXT DEFAULT (datetime('now','localtime'))
            )""")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT NOT NULL,
                phone     TEXT DEFAULT '',
                address   TEXT DEFAULT ''
            )""")

        # Default users (only if table is empty)
        if not cur.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            cur.executemany(
                "INSERT INTO users(username,password,role,full_name) "
                "VALUES (?,?,?,?)",
                [
                    ("admin",  "admin123", "owner", "Balebet"),
                    ("staff1", "staff123", "staff", "Seratena 1"),
                ]
            )

        # Sample products (only if table is empty)
        if not cur.execute("SELECT 1 FROM products LIMIT 1").fetchone():
            cur.executemany(
                "INSERT INTO products(name,category,qty,cost,price,min_qty) "
                "VALUES (?,?,?,?,?,?)",
                [
                    ("Jebena Tiliq",        "jebena", 20, 80,  150, 3),
                    ("Jebena Mekakelegna",  "jebena", 15, 60,  110, 3),
                    ("Jebena Tinish",       "jebena", 10, 40,   80, 3),
                    ("Sefed Tiliq",         "sefed",  12, 120, 220, 2),
                    ("Sefed Tinish",        "sefed",   8, 70,  130, 2),
                ]
            )


# ═══════════════════════════════════════════════════════════
#  SESSION  (global login state)
# ═══════════════════════════════════════════════════════════

class Session:
    uid:  int  = -1
    name: str  = ""
    role: str  = ""

    @classmethod
    def set(cls, row):
        cls.uid, _, _, cls.role, cls.name = row

    @classmethod
    def clear(cls):
        cls.uid  = -1
        cls.name = ""
        cls.role = ""

    @classmethod
    def owner(cls) -> bool:
        return cls.role == "owner"


# ═══════════════════════════════════════════════════════════
#  KV  (UI layout)
# ═══════════════════════════════════════════════════════════

KV = """
# ── screen manager ──────────────────────────────────────
<AppManager>:
    transition: FadeTransition()

# ── splash ──────────────────────────────────────────────
<SplashScreen>:
    name: "splash"
    canvas.before:
        Color:
            rgba: 0.933, 0.878, 0.796, 1
        Rectangle:
            pos:  self.pos
            size: self.size
    BoxLayout:
        orientation: "vertical"
        padding:  dp(48)
        spacing:  dp(18)
        Widget:
            size_hint_y: None
            height: dp(60)
        MDLabel:
            text:      "Masha Allah"
            halign:    "center"
            font_style: "H3"
            bold:      True
            theme_text_color: "Custom"
            text_color: 0.42, 0.22, 0.07, 1
        MDLabel:
            text:      "Insha Allah"
            halign:    "center"
            font_style: "H4"
            theme_text_color: "Custom"
            text_color: 0.42, 0.22, 0.07, 0.75
        MDLabel:
            text:      "Jebena & Sefed"
            halign:    "center"
            font_style: "H5"
            bold:      True
            theme_text_color: "Custom"
            text_color: 0.42, 0.22, 0.07, 1
        MDLabel:
            text:      "Sales Manager"
            halign:    "center"
            font_style: "Subtitle1"
            theme_text_color: "Custom"
            text_color: 0.42, 0.22, 0.07, 0.6
        Widget:

# ── login ────────────────────────────────────────────────
<LoginScreen>:
    name: "login"
    canvas.before:
        Color:
            rgba: 0.933, 0.878, 0.796, 1
        Rectangle:
            pos:  self.pos
            size: self.size
    BoxLayout:
        orientation: "vertical"
        padding:  [dp(28), dp(72), dp(28), dp(28)]
        spacing:  dp(16)
        MDLabel:
            text:      "Jebena & Sefed"
            halign:    "center"
            font_style: "H5"
            bold:      True
            theme_text_color: "Custom"
            text_color: 0.42, 0.22, 0.07, 1
            size_hint_y: None
            height: dp(48)
        MDCard:
            orientation: "vertical"
            padding:   dp(24)
            spacing:   dp(14)
            elevation: 6
            radius:    [dp(18)]
            md_bg_color: 1, 1, 1, 1
            MDLabel:
                text:      "Sign In"
                halign:    "center"
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 0.42, 0.22, 0.07, 1
                size_hint_y: None
                height: dp(38)
            MDTextField:
                id:          uname
                hint_text:   "Username"
                mode:        "rectangle"
                size_hint_y: None
                height:      dp(56)
            MDTextField:
                id:          pwd
                hint_text:   "Password"
                password:    True
                mode:        "rectangle"
                size_hint_y: None
                height:      dp(56)
            MDRaisedButton:
                text:        "LOGIN"
                on_release:  app.do_login()
                md_bg_color: 0.42, 0.22, 0.07, 1
                size_hint_x: 1
                size_hint_y: None
                height:      dp(52)
                font_size:   "18sp"
        Widget:

# ── owner dashboard ──────────────────────────────────────
<OwnerScreen>:
    name: "owner"
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Owner Dashboard"
            right_action_items:
                [["logout", lambda x: app.logout()]]
            md_bg_color:        0.42, 0.22, 0.07, 1
            specific_text_color: 1, 1, 1, 1
        ScrollView:
            BoxLayout:
                orientation: "vertical"
                padding:     dp(14)
                spacing:     dp(12)
                size_hint_y: None
                height:      self.minimum_height

                # greeting
                MDLabel:
                    id:        greeting
                    text:      "Hello!"
                    font_style: "H6"
                    bold:      True
                    theme_text_color: "Custom"
                    text_color: 0.42, 0.22, 0.07, 1
                    size_hint_y: None
                    height: dp(38)

                # stat cards row
                BoxLayout:
                    orientation: "horizontal"
                    spacing:     dp(8)
                    size_hint_y: None
                    height:      dp(88)
                    MDCard:
                        md_bg_color: 0.12, 0.60, 0.35, 1
                        radius:      [dp(12)]
                        elevation:   3
                        orientation: "vertical"
                        padding:     dp(6)
                        MDLabel:
                            id:     stat_income
                            text:   "0 Birr"
                            halign: "center"
                            bold:   True
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                            font_style: "Caption"
                        MDLabel:
                            text:   "Today"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 0.8
                            font_style: "Caption"
                    MDCard:
                        md_bg_color: 0.80, 0.22, 0.22, 1
                        radius:      [dp(12)]
                        elevation:   3
                        orientation: "vertical"
                        padding:     dp(6)
                        MDLabel:
                            id:     stat_low
                            text:   "0"
                            halign: "center"
                            bold:   True
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                        MDLabel:
                            text:   "Low Stock"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 0.8
                            font_style: "Caption"
                    MDCard:
                        md_bg_color: 0.18, 0.42, 0.78, 1
                        radius:      [dp(12)]
                        elevation:   3
                        orientation: "vertical"
                        padding:     dp(6)
                        MDLabel:
                            id:     stat_month
                            text:   "0"
                            halign: "center"
                            bold:   True
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                        MDLabel:
                            text:   "Month"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 0.8
                            font_style: "Caption"

                # 4 action cards
                GridLayout:
                    cols:        2
                    spacing:     dp(10)
                    size_hint_y: None
                    height:      dp(220)
                    MDCard:
                        md_bg_color: 0.42, 0.22, 0.07, 1
                        radius:      [dp(14)]
                        elevation:   5
                        on_release:  app.goto("sale")
                        orientation: "vertical"
                        padding:     dp(10)
                        MDLabel:
                            text:   "+ SALE"
                            halign: "center"
                            bold:   True
                            font_style: "H6"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                        MDLabel:
                            text:   "New Sale"
                            halign: "center"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 0.75
                    MDCard:
                        md_bg_color: 0.18, 0.52, 0.35, 1
                        radius:      [dp(14)]
                        elevation:   5
                        on_release:  app.goto("inventory")
                        orientation: "vertical"
                        padding:     dp(10)
                        MDLabel:
                            text:   "STOCK"
                            halign: "center"
                            bold:   True
                            font_style: "H6"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                        MDLabel:
                            text:   "Inventory"
                            halign: "center"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 0.75
                    MDCard:
                        md_bg_color: 0.18, 0.42, 0.78, 1
                        radius:      [dp(14)]
                        elevation:   5
                        on_release:  app.goto("report")
                        orientation: "vertical"
                        padding:     dp(10)
                        MDLabel:
                            text:   "REPORT"
                            halign: "center"
                            bold:   True
                            font_style: "H6"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                        MDLabel:
                            text:   "Profit/Loss"
                            halign: "center"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 0.75
                    MDCard:
                        md_bg_color: 0.62, 0.35, 0.10, 1
                        radius:      [dp(14)]
                        elevation:   5
                        on_release:  app.goto("customers")
                        orientation: "vertical"
                        padding:     dp(10)
                        MDLabel:
                            text:   "CLIENTS"
                            halign: "center"
                            bold:   True
                            font_style: "H6"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                        MDLabel:
                            text:   "Customers"
                            halign: "center"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 0.75

                # extra buttons
                MDRaisedButton:
                    text:        "EXPENSE"
                    on_release:  app.goto("expense")
                    md_bg_color: 0.75, 0.22, 0.22, 1
                    size_hint_x: 1
                    size_hint_y: None
                    height:      dp(50)
                MDRaisedButton:
                    text:        "+ ADD PRODUCT"
                    on_release:  app.goto("add_product")
                    md_bg_color: 0.22, 0.55, 0.32, 1
                    size_hint_x: 1
                    size_hint_y: None
                    height:      dp(50)
                Widget:
                    size_hint_y: None
                    height:      dp(16)

# ── staff dashboard ──────────────────────────────────────
<StaffScreen>:
    name: "staff"
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Staff Dashboard"
            right_action_items:
                [["logout", lambda x: app.logout()]]
            md_bg_color:        0.42, 0.22, 0.07, 1
            specific_text_color: 1, 1, 1, 1
        BoxLayout:
            orientation: "vertical"
            padding:  dp(20)
            spacing:  dp(16)
            MDLabel:
                id:        staff_greeting
                text:      "Hello!"
                font_style: "H6"
                bold:      True
                theme_text_color: "Custom"
                text_color: 0.42, 0.22, 0.07, 1
                size_hint_y: None
                height: dp(40)
            MDCard:
                orientation: "vertical"
                padding:     dp(18)
                spacing:     dp(6)
                radius:      [dp(14)]
                md_bg_color: 0.88, 0.97, 0.90, 1
                size_hint_y: None
                height:      dp(96)
                MDLabel:
                    id:     staff_income
                    text:   "Today: 0 Birr"
                    halign: "center"
                    bold:   True
                    font_style: "H6"
                    theme_text_color: "Custom"
                    text_color: 0.10, 0.48, 0.22, 1
                MDLabel:
                    id:     staff_count
                    text:   "0 items sold"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.35, 0.35, 0.35, 1
            MDRaisedButton:
                text:        "NEW SALE"
                on_release:  app.goto("sale")
                md_bg_color: 0.42, 0.22, 0.07, 1
                size_hint_x: 1
                size_hint_y: None
                height:      dp(58)
                font_size:   "18sp"
            MDRaisedButton:
                text:        "CHECK STOCK"
                on_release:  app.goto("inventory")
                md_bg_color: 0.18, 0.52, 0.35, 1
                size_hint_x: 1
                size_hint_y: None
                height:      dp(58)
                font_size:   "18sp"
            Widget:

# ── new sale ─────────────────────────────────────────────
<SaleScreen>:
    name: "sale"
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "New Sale"
            left_action_items:
                [["arrow-left", lambda x: app.back()]]
            md_bg_color:        0.42, 0.22, 0.07, 1
            specific_text_color: 1, 1, 1, 1
        ScrollView:
            BoxLayout:
                orientation: "vertical"
                padding:     dp(18)
                spacing:     dp(14)
                size_hint_y: None
                height:      self.minimum_height
                MDCard:
                    orientation: "vertical"
                    padding:     dp(16)
                    spacing:     dp(10)
                    elevation:   4
                    radius:      [dp(14)]
                    size_hint_y: None
                    height:      dp(320)
                    MDLabel:
                        text:      "Sale Details"
                        font_style: "H6"
                        bold:      True
                        theme_text_color: "Custom"
                        text_color: 0.42, 0.22, 0.07, 1
                        size_hint_y: None
                        height: dp(34)
                    MDRaisedButton:
                        id:          sale_product_btn
                        text:        "Select Product  ▼"
                        on_release:  app.open_product_menu(self)
                        md_bg_color: 0.933, 0.878, 0.796, 1
                        theme_text_color: "Custom"
                        text_color:  0.30, 0.14, 0.04, 1
                        size_hint_x: 1
                        size_hint_y: None
                        height:      dp(50)
                    MDLabel:
                        id:     sale_price_lbl
                        text:   "Price: —"
                        theme_text_color: "Custom"
                        text_color: 0.40, 0.40, 0.40, 1
                        size_hint_y: None
                        height: dp(22)
                    MDTextField:
                        id:           sale_qty
                        hint_text:    "Quantity"
                        input_filter: "int"
                        mode:         "rectangle"
                        size_hint_y:  None
                        height:       dp(56)
                        on_text:      app.calc_total()
                    MDLabel:
                        id:     sale_total_lbl
                        text:   "Total: 0 Birr"
                        bold:   True
                        font_style: "H6"
                        theme_text_color: "Custom"
                        text_color: 0.10, 0.48, 0.22, 1
                        size_hint_y: None
                        height: dp(34)
                    MDRaisedButton:
                        id:          sale_pay_btn
                        text:        "Payment: Cash  ▼"
                        on_release:  app.open_payment_menu(self)
                        md_bg_color: 0.933, 0.878, 0.796, 1
                        theme_text_color: "Custom"
                        text_color:  0.30, 0.14, 0.04, 1
                        size_hint_x: 1
                        size_hint_y: None
                        height:      dp(50)
                MDRaisedButton:
                    text:        "SAVE SALE"
                    on_release:  app.save_sale()
                    md_bg_color: 0.10, 0.58, 0.32, 1
                    size_hint_x: 1
                    size_hint_y: None
                    height:      dp(56)
                    font_size:   "18sp"

# ── inventory ────────────────────────────────────────────
<InventoryScreen>:
    name: "inventory"
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Inventory / Stock"
            left_action_items:
                [["arrow-left", lambda x: app.back()]]
            right_action_items:
                [["plus", lambda x: app.goto("add_product")]]
            md_bg_color:        0.42, 0.22, 0.07, 1
            specific_text_color: 1, 1, 1, 1
        ScrollView:
            MDList:
                id: inv_list

# ── add product ──────────────────────────────────────────
<AddProductScreen>:
    name: "add_product"
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Add Product"
            left_action_items:
                [["arrow-left", lambda x: app.back()]]
            md_bg_color:        0.42, 0.22, 0.07, 1
            specific_text_color: 1, 1, 1, 1
        ScrollView:
            BoxLayout:
                orientation: "vertical"
                padding:     dp(18)
                spacing:     dp(12)
                size_hint_y: None
                height:      self.minimum_height
                MDCard:
                    orientation: "vertical"
                    padding:     dp(16)
                    spacing:     dp(10)
                    elevation:   4
                    radius:      [dp(14)]
                    size_hint_y: None
                    height:      dp(420)
                    MDTextField:
                        id:          ap_name
                        hint_text:   "Product Name"
                        mode:        "rectangle"
                        size_hint_y: None
                        height:      dp(56)
                    MDRaisedButton:
                        id:          ap_cat_btn
                        text:        "Category: jebena  ▼"
                        on_release:  app.open_cat_menu(self)
                        md_bg_color: 0.933, 0.878, 0.796, 1
                        theme_text_color: "Custom"
                        text_color:  0.30, 0.14, 0.04, 1
                        size_hint_x: 1
                        size_hint_y: None
                        height:      dp(50)
                    MDTextField:
                        id:           ap_qty
                        hint_text:    "Quantity"
                        input_filter: "int"
                        mode:         "rectangle"
                        size_hint_y:  None
                        height:       dp(56)
                    MDTextField:
                        id:           ap_cost
                        hint_text:    "Cost Price (Birr)"
                        input_filter: "float"
                        mode:         "rectangle"
                        size_hint_y:  None
                        height:       dp(56)
                    MDTextField:
                        id:           ap_price
                        hint_text:    "Sell Price (Birr)"
                        input_filter: "float"
                        mode:         "rectangle"
                        size_hint_y:  None
                        height:       dp(56)
                    MDTextField:
                        id:           ap_min
                        hint_text:    "Min Stock Alert"
                        input_filter: "int"
                        mode:         "rectangle"
                        size_hint_y:  None
                        height:       dp(56)
                MDRaisedButton:
                    text:        "SAVE PRODUCT"
                    on_release:  app.save_product()
                    md_bg_color: 0.22, 0.55, 0.32, 1
                    size_hint_x: 1
                    size_hint_y: None
                    height:      dp(56)
                    font_size:   "18sp"

# ── report ───────────────────────────────────────────────
<ReportScreen>:
    name: "report"
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Report / Profit"
            left_action_items:
                [["arrow-left", lambda x: app.back()]]
            md_bg_color:        0.42, 0.22, 0.07, 1
            specific_text_color: 1, 1, 1, 1
        ScrollView:
            BoxLayout:
                orientation: "vertical"
                padding:     dp(14)
                spacing:     dp(12)
                size_hint_y: None
                height:      self.minimum_height

                BoxLayout:
                    orientation: "horizontal"
                    spacing:     dp(8)
                    size_hint_y: None
                    height:      dp(88)
                    MDCard:
                        md_bg_color: 0.12, 0.60, 0.35, 1
                        radius:      [dp(12)]
                        elevation:   3
                        orientation: "vertical"
                        padding:     dp(6)
                        MDLabel:
                            id:     rep_income
                            text:   "0 Birr"
                            halign: "center"
                            bold:   True
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                            font_style: "Caption"
                        MDLabel:
                            text:   "Income"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 0.8
                            font_style: "Caption"
                    MDCard:
                        md_bg_color: 0.80, 0.22, 0.22, 1
                        radius:      [dp(12)]
                        elevation:   3
                        orientation: "vertical"
                        padding:     dp(6)
                        MDLabel:
                            id:     rep_expense
                            text:   "0 Birr"
                            halign: "center"
                            bold:   True
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                            font_style: "Caption"
                        MDLabel:
                            text:   "Expense"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 0.8
                            font_style: "Caption"
                    MDCard:
                        md_bg_color: 0.18, 0.42, 0.78, 1
                        radius:      [dp(12)]
                        elevation:   3
                        orientation: "vertical"
                        padding:     dp(6)
                        MDLabel:
                            id:     rep_profit
                            text:   "0 Birr"
                            halign: "center"
                            bold:   True
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                            font_style: "Caption"
                        MDLabel:
                            text:   "Profit"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 0.8
                            font_style: "Caption"

                MDLabel:
                    text:      "Today's Sales"
                    font_style: "Subtitle1"
                    bold:      True
                    theme_text_color: "Custom"
                    text_color: 0.42, 0.22, 0.07, 1
                    size_hint_y: None
                    height: dp(30)
                MDList:
                    id:      rep_list
                    size_hint_y: None
                    height:  self.minimum_height

# ── expense ──────────────────────────────────────────────
<ExpenseScreen>:
    name: "expense"
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Expenses"
            left_action_items:
                [["arrow-left", lambda x: app.back()]]
            md_bg_color:        0.75, 0.22, 0.22, 1
            specific_text_color: 1, 1, 1, 1
        ScrollView:
            BoxLayout:
                orientation: "vertical"
                padding:     dp(18)
                spacing:     dp(12)
                size_hint_y: None
                height:      self.minimum_height
                MDCard:
                    orientation: "vertical"
                    padding:     dp(16)
                    spacing:     dp(10)
                    elevation:   4
                    radius:      [dp(14)]
                    size_hint_y: None
                    height:      dp(268)
                    MDRaisedButton:
                        id:          exp_cat_btn
                        text:        "Category: Transport  ▼"
                        on_release:  app.open_exp_cat_menu(self)
                        md_bg_color: 0.933, 0.878, 0.796, 1
                        theme_text_color: "Custom"
                        text_color:  0.30, 0.14, 0.04, 1
                        size_hint_x: 1
                        size_hint_y: None
                        height:      dp(50)
                    MDTextField:
                        id:           exp_amount
                        hint_text:    "Amount (Birr)"
                        input_filter: "float"
                        mode:         "rectangle"
                        size_hint_y:  None
                        height:       dp(56)
                    MDTextField:
                        id:          exp_note
                        hint_text:   "Note / Description"
                        mode:        "rectangle"
                        size_hint_y: None
                        height:      dp(56)
                MDRaisedButton:
                    text:        "SAVE EXPENSE"
                    on_release:  app.save_expense()
                    md_bg_color: 0.75, 0.22, 0.22, 1
                    size_hint_x: 1
                    size_hint_y: None
                    height:      dp(56)
                    font_size:   "18sp"
                MDLabel:
                    text:      "Recent Expenses"
                    font_style: "Subtitle1"
                    bold:      True
                    theme_text_color: "Custom"
                    text_color: 0.42, 0.22, 0.07, 1
                    size_hint_y: None
                    height: dp(30)
                MDList:
                    id:      exp_list
                    size_hint_y: None
                    height:  self.minimum_height

# ── customers ────────────────────────────────────────────
<CustomerScreen>:
    name: "customers"
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Customers"
            left_action_items:
                [["arrow-left", lambda x: app.back()]]
            right_action_items:
                [["plus", lambda x: app.add_customer_dialog()]]
            md_bg_color:        0.42, 0.22, 0.07, 1
            specific_text_color: 1, 1, 1, 1
        ScrollView:
            MDList:
                id: cust_list
"""


# ═══════════════════════════════════════════════════════════
#  SCREEN CLASSES
# ═══════════════════════════════════════════════════════════

class AppManager(ScreenManager):
    pass


class SplashScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class OwnerScreen(Screen):
    pass


class StaffScreen(Screen):
    pass


class SaleScreen(Screen):
    _product = None   # (id, name, price, qty_in_stock)
    _payment = "Cash"


class InventoryScreen(Screen):
    pass


class AddProductScreen(Screen):
    _cat = "jebena"


class ReportScreen(Screen):
    pass


class ExpenseScreen(Screen):
    _cat = "Transport"


class CustomerScreen(Screen):
    pass


# ═══════════════════════════════════════════════════════════
#  APP
# ═══════════════════════════════════════════════════════════

class JebenaApp(MDApp):
    title = "Jebena & Sefed"

    # ── build ────────────────────────────────────────────
    def build(self):
        self.theme_cls.primary_palette = "Brown"
        self.theme_cls.accent_palette  = "Green"
        self.theme_cls.theme_style     = "Light"

        setup_db()
        Builder.load_string(KV)

        self.sm = AppManager()
        for cls in (
            SplashScreen, LoginScreen,
            OwnerScreen, StaffScreen,
            SaleScreen, InventoryScreen,
            AddProductScreen, ReportScreen,
            ExpenseScreen, CustomerScreen,
        ):
            self.sm.add_widget(cls())

        self.sm.current = "splash"
        Clock.schedule_once(lambda *_: self._show("login"), 2.5)
        return self.sm

    # ── navigation ───────────────────────────────────────
    def _show(self, name, direction="left"):
        self.sm.transition = SlideTransition(direction=direction)
        self.sm.current    = name

    def goto(self, name):
        loaders = {
            "owner":       self._load_owner,
            "staff":       self._load_staff,
            "sale":        self._reset_sale,
            "inventory":   self._load_inventory,
            "report":      self._load_report,
            "expense":     self._load_expenses,
            "customers":   self._load_customers,
            "add_product": None,
        }
        loader = loaders.get(name)
        if loader:
            loader()
        self._show(name)

    def back(self):
        dest = "owner" if Session.owner() else "staff"
        loader = self._load_owner if Session.owner() else self._load_staff
        loader()
        self._show(dest, direction="right")

    def logout(self):
        Session.clear()
        self.sm.transition = FadeTransition()
        self.sm.current    = "login"

    # ── login ────────────────────────────────────────────
    def do_login(self):
        s = self.sm.get_screen("login")
        u = s.ids.uname.text.strip()
        p = s.ids.pwd.text.strip()

        if not u or not p:
            Snackbar(text="Enter username and password").open()
            return

        with db() as con:
            row = con.execute(
                "SELECT id,username,password,role,full_name "
                "FROM users WHERE username=? AND password=?",
                (u, p),
            ).fetchone()

        if not row:
            Snackbar(text="Wrong username or password").open()
            return

        Session.set(row)
        s.ids.uname.text = ""
        s.ids.pwd.text   = ""

        if Session.owner():
            self._load_owner()
            self.sm.transition = FadeTransition()
            self.sm.current    = "owner"
        else:
            self._load_staff()
            self.sm.transition = FadeTransition()
            self.sm.current    = "staff"

    # ── owner dashboard ──────────────────────────────────
    def _load_owner(self):
        sc    = self.sm.get_screen("owner")
        today = date.today().isoformat()
        with db() as con:
            income = con.execute(
                "SELECT COALESCE(SUM(total),0) FROM sales "
                "WHERE date(created_at)=?", (today,)
            ).fetchone()[0]
            low    = con.execute(
                "SELECT COUNT(*) FROM products WHERE qty<=min_qty"
            ).fetchone()[0]
            month  = con.execute(
                "SELECT COUNT(*) FROM sales "
                "WHERE strftime('%Y-%m',created_at)=strftime('%Y-%m','now')"
            ).fetchone()[0]
        sc.ids.greeting.text   = "Hello " + Session.name + "!"
        sc.ids.stat_income.text = "{:,.0f} Birr".format(income)
        sc.ids.stat_low.text    = str(low)
        sc.ids.stat_month.text  = str(month)

    # ── staff dashboard ──────────────────────────────────
    def _load_staff(self):
        sc    = self.sm.get_screen("staff")
        today = date.today().isoformat()
        with db() as con:
            income = con.execute(
                "SELECT COALESCE(SUM(total),0) FROM sales "
                "WHERE date(created_at)=? AND staff_id=?",
                (today, Session.uid),
            ).fetchone()[0]
            count  = con.execute(
                "SELECT COALESCE(SUM(qty),0) FROM sales "
                "WHERE date(created_at)=? AND staff_id=?",
                (today, Session.uid),
            ).fetchone()[0]
        sc.ids.staff_greeting.text = "Hello " + Session.name + "!"
        sc.ids.staff_income.text   = "Today: {:,.0f} Birr".format(income)
        sc.ids.staff_count.text    = str(count) + " items sold"

    # ── sale ─────────────────────────────────────────────
    def _reset_sale(self):
        sc = self.sm.get_screen("sale")
        sc._product                  = None
        sc._payment                  = "Cash"
        sc.ids.sale_product_btn.text = "Select Product  ▼"
        sc.ids.sale_price_lbl.text   = "Price: —"
        sc.ids.sale_qty.text         = ""
        sc.ids.sale_total_lbl.text   = "Total: 0 Birr"
        sc.ids.sale_pay_btn.text     = "Payment: Cash  ▼"

    def open_product_menu(self, btn):
        with db() as con:
            rows = con.execute(
                "SELECT id,name,price,qty FROM products ORDER BY name"
            ).fetchall()

        items = [
            {
                "text": "{} ({:.0f} Birr) [{} left]".format(r[1], r[2], r[3]),
                "viewclass": "OneLineListItem",
                "on_release": lambda x=r: self._pick_product(x),
            }
            for r in rows
        ]
        self._prod_menu = MDDropdownMenu(
            caller=btn, items=items, width_mult=5
        )
        self._prod_menu.open()

    def _pick_product(self, row):
        sc = self.sm.get_screen("sale")
        sc._product                  = row   # (id, name, price, qty)
        sc.ids.sale_product_btn.text = row[1] + "  ▼"
        sc.ids.sale_price_lbl.text   = "Price: {:.0f} Birr".format(row[2])
        self._prod_menu.dismiss()
        self.calc_total()

    def open_payment_menu(self, btn):
        methods = ["Cash", "Telebirr", "CBE Birr", "Credit"]
        items   = [
            {
                "text": m,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=m: self._pick_payment(x),
            }
            for m in methods
        ]
        self._pay_menu = MDDropdownMenu(
            caller=btn, items=items, width_mult=4
        )
        self._pay_menu.open()

    def _pick_payment(self, method):
        sc                       = self.sm.get_screen("sale")
        sc._payment              = method
        sc.ids.sale_pay_btn.text = "Payment: " + method + "  ▼"
        self._pay_menu.dismiss()

    def calc_total(self, *_):
        sc = self.sm.get_screen("sale")
        try:
            qty   = int(sc.ids.sale_qty.text or "0")
            price = sc._product[2] if sc._product else 0
            sc.ids.sale_total_lbl.text = "Total: {:,.0f} Birr".format(
                qty * price
            )
        except Exception:
            pass

    def save_sale(self):
        sc = self.sm.get_screen("sale")

        if sc._product is None:
            Snackbar(text="Select a product first!").open()
            return

        try:
            qty = int(sc.ids.sale_qty.text)
        except Exception:
            Snackbar(text="Enter a valid quantity!").open()
            return

        if qty <= 0:
            Snackbar(text="Quantity must be at least 1").open()
            return

        pid, pname, price, stock = sc._product
        if qty > stock:
            Snackbar(text="Only {} in stock!".format(stock)).open()
            return

        total = qty * price
        with db() as con:
            con.execute(
                "INSERT INTO sales"
                "(product_id,product_name,qty,unit_price,total,"
                " payment,staff_id,staff_name)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (pid, pname, qty, price, total,
                 sc._payment, Session.uid, Session.name),
            )
            con.execute(
                "UPDATE products SET qty=qty-? WHERE id=?", (qty, pid)
            )

        Snackbar(
            text="Saved!  {:,.0f} Birr".format(total)
        ).open()
        self._reset_sale()

        if Session.owner():
            self._load_owner()
        else:
            self._load_staff()

    # ── inventory ────────────────────────────────────────
    def _load_inventory(self):
        lst = self.sm.get_screen("inventory").ids.inv_list
        lst.clear_widgets()
        with db() as con:
            rows = con.execute(
                "SELECT name,category,qty,price,min_qty FROM products ORDER BY name"
            ).fetchall()
        for r in rows:
            n, cat, qty, price, minq = r
            warn = "  ⚠ LOW!" if qty <= minq else ""
            lst.add_widget(TwoLineListItem(
                text="{} [{}]{}".format(n, cat, warn),
                secondary_text="Stock: {}  |  Price: {:.0f} Birr".format(
                    qty, price
                ),
            ))

    # ── add product ──────────────────────────────────────
    def open_cat_menu(self, btn):
        items = [
            {
                "text": c,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=c: self._pick_cat(x),
            }
            for c in ("jebena", "sefed", "other")
        ]
        self._cat_menu = MDDropdownMenu(
            caller=btn, items=items, width_mult=3
        )
        self._cat_menu.open()

    def _pick_cat(self, cat):
        sc = self.sm.get_screen("add_product")
        sc._cat                  = cat
        sc.ids.ap_cat_btn.text   = "Category: " + cat + "  ▼"
        self._cat_menu.dismiss()

    def save_product(self):
        sc   = self.sm.get_screen("add_product")
        name = sc.ids.ap_name.text.strip()
        if not name:
            Snackbar(text="Enter a product name!").open()
            return

        try:
            qty   = int(sc.ids.ap_qty.text   or "0")
            cost  = float(sc.ids.ap_cost.text or "0")
            price = float(sc.ids.ap_price.text or "0")
            minq  = int(sc.ids.ap_min.text    or "3")
        except Exception:
            Snackbar(text="Check the numbers you entered!").open()
            return

        with db() as con:
            con.execute(
                "INSERT INTO products(name,category,qty,cost,price,min_qty)"
                " VALUES (?,?,?,?,?,?)",
                (name, sc._cat, qty, cost, price, minq),
            )

        Snackbar(text=name + " saved!").open()
        for fld in (sc.ids.ap_name, sc.ids.ap_qty,
                    sc.ids.ap_cost, sc.ids.ap_price, sc.ids.ap_min):
            fld.text = ""

    # ── report ───────────────────────────────────────────
    def _load_report(self):
        sc    = self.sm.get_screen("report")
        today = date.today().isoformat()

        with db() as con:
            income  = con.execute(
                "SELECT COALESCE(SUM(total),0) FROM sales "
                "WHERE date(created_at)=?", (today,)
            ).fetchone()[0]
            expense = con.execute(
                "SELECT COALESCE(SUM(amount),0) FROM expenses "
                "WHERE date(created_at)=?", (today,)
            ).fetchone()[0]
            rows    = con.execute(
                "SELECT product_name,qty,total,staff_name,payment "
                "FROM sales WHERE date(created_at)=? "
                "ORDER BY created_at DESC", (today,)
            ).fetchall()

        sc.ids.rep_income.text  = "{:,.0f} Birr".format(income)
        sc.ids.rep_expense.text = "{:,.0f} Birr".format(expense)
        sc.ids.rep_profit.text  = "{:,.0f} Birr".format(income - expense)

        lst = sc.ids.rep_list
        lst.clear_widgets()

        if not rows:
            lst.add_widget(OneLineListItem(text="No sales today"))
            return

        for r in rows:
            lst.add_widget(ThreeLineListItem(
                text="{} x{}".format(r[0], r[1]),
                secondary_text="{:,.0f} Birr  |  {}".format(r[2], r[4]),
                tertiary_text="Staff: " + str(r[3]),
            ))

    # ── expense ──────────────────────────────────────────
    def open_exp_cat_menu(self, btn):
        items = [
            {
                "text": c,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=c: self._pick_exp_cat(x),
            }
            for c in ("Transport", "Labor", "Rent", "Other")
        ]
        self._exp_cat_menu = MDDropdownMenu(
            caller=btn, items=items, width_mult=4
        )
        self._exp_cat_menu.open()

    def _pick_exp_cat(self, cat):
        sc                       = self.sm.get_screen("expense")
        sc._cat                  = cat
        sc.ids.exp_cat_btn.text  = "Category: " + cat + "  ▼"
        self._exp_cat_menu.dismiss()

    def save_expense(self):
        sc = self.sm.get_screen("expense")
        try:
            amount = float(sc.ids.exp_amount.text)
        except Exception:
            Snackbar(text="Enter a valid amount!").open()
            return

        with db() as con:
            con.execute(
                "INSERT INTO expenses(category,amount,note) VALUES (?,?,?)",
                (sc._cat, amount, sc.ids.exp_note.text.strip()),
            )

        Snackbar(text="Saved!  {:,.0f} Birr".format(amount)).open()
        sc.ids.exp_amount.text = ""
        sc.ids.exp_note.text   = ""
        self._load_expenses()

    def _load_expenses(self):
        lst = self.sm.get_screen("expense").ids.exp_list
        lst.clear_widgets()
        with db() as con:
            rows = con.execute(
                "SELECT category,amount,note,created_at FROM expenses "
                "ORDER BY created_at DESC LIMIT 20"
            ).fetchall()
        for r in rows:
            lst.add_widget(TwoLineListItem(
                text="{} — {:,.0f} Birr".format(r[0], r[1]),
                secondary_text=r[2] if r[2] else r[3][:10],
            ))

    # ── customers ────────────────────────────────────────
    def _load_customers(self):
        lst = self.sm.get_screen("customers").ids.cust_list
        lst.clear_widgets()
        with db() as con:
            rows = con.execute(
                "SELECT name,phone,address FROM customers ORDER BY name"
            ).fetchall()
        if not rows:
            lst.add_widget(OneLineListItem(text="No customers yet"))
            return
        for r in rows:
            lst.add_widget(TwoLineListItem(
                text=r[0],
                secondary_text="{} | {}".format(r[1] or "—", r[2] or "—"),
            ))

    def add_customer_dialog(self):
        self._dlg_name    = MDTextField(hint_text="Full Name",  mode="rectangle")
        self._dlg_phone   = MDTextField(hint_text="Phone",      mode="rectangle")
        self._dlg_address = MDTextField(hint_text="Address",    mode="rectangle")

        box = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(210),
        )
        for w in (self._dlg_name, self._dlg_phone, self._dlg_address):
            box.add_widget(w)

        self._dialog = MDDialog(
            title="Add Customer",
            type="custom",
            content_cls=box,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda *_: self._dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="ADD",
                    on_release=self._save_customer,
                ),
            ],
        )
        self._dialog.open()

    def _save_customer(self, *_):
        name = self._dlg_name.text.strip()
        if not name:
            Snackbar(text="Enter the customer's name!").open()
            return

        with db() as con:
            con.execute(
                "INSERT INTO customers(name,phone,address) VALUES (?,?,?)",
                (name,
                 self._dlg_phone.text.strip(),
                 self._dlg_address.text.strip()),
            )

        self._dialog.dismiss()
        Snackbar(text=name + " added!").open()
        self._load_customers()


# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    JebenaApp().run()

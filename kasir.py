import json
import os
from datetime import datetime, date
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.core.window import Window

# Set window size for mobile (portrait mode)
Window.size = (360, 640)

class Product:
    def __init__(self, id, name, price_per_kg, stock_kg=100):
        self.id = id
        self.name = name
        self.price_per_kg = price_per_kg
        self.stock_kg = stock_kg

class CartItem:
    def __init__(self, product, weight_kg=1):
        self.product = product
        self.weight_kg = weight_kg
    
    def get_total(self):
        return self.product.price_per_kg * self.weight_kg

class Expense:
    def __init__(self, id, name, amount, date_time):
        self.id = id
        self.name = name
        self.amount = amount
        self.date_time = date_time

class UserSetupPopup(Popup):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.title = 'Setup Awal'
        self.size_hint = (0.9, 0.7)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        welcome_label = Label(
            text='Selamat Datang di Kasir Ayam Potong!\n\nMari setup aplikasi Anda',
            size_hint_y=None,
            height=dp(80),
            font_size=dp(16),
            bold=True,
            halign='center',
            color=(0.2, 0.4, 0.8, 1)
        )
        layout.add_widget(welcome_label)
        
        # Name input
        name_label = Label(
            text='Nama Pengguna/Pedagang:',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14),
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        )
        layout.add_widget(name_label)
        
        self.name_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            hint_text='Masukkan nama Anda',
            font_size=dp(14)
        )
        layout.add_widget(self.name_input)
        
        # Shop input
        shop_label = Label(
            text='Nama Toko (Opsional):',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14),
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        )
        layout.add_widget(shop_label)
        
        self.shop_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            hint_text='Contoh: Ayam Potong Segar Pak Budi',
            font_size=dp(14)
        )
        layout.add_widget(self.shop_input)
        
        # Save button
        save_btn = Button(
            text='SIMPAN & MULAI',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
            bold=True,
            background_color=(0.1, 0.7, 0.3, 1)
        )
        save_btn.bind(on_press=self.save_user_info)
        layout.add_widget(save_btn)
        
        self.content = layout
    
    def save_user_info(self, instance):
        username = self.name_input.text.strip()
        shop_name = self.shop_input.text.strip()
        
        if not username:
            self.app_ref.show_popup("Error", "Nama pengguna tidak boleh kosong!")
            return
        
        user_data = {
            'username': username,
            'shop_name': shop_name if shop_name else 'Toko Ayam Potong',
            'setup_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        try:
            with open('user_config.json', 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
            
            self.app_ref.username = username
            self.app_ref.shop_name = user_data['shop_name']
            
            main_screen = self.app_ref.root.get_screen('main')
            main_screen.update_header()
            
            self.dismiss()
            
        except Exception as e:
            self.app_ref.show_popup("Error", f"Gagal menyimpan data: {str(e)}")

class AddExpensePopup(Popup):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.title = 'Tambah Pengeluaran'
        self.size_hint = (0.9, 0.7)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        info_label = Label(
            text='Catat pengeluaran harian Anda',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16),
            bold=True,
            halign='center',
            color=(0.2, 0.4, 0.8, 1)
        )
        layout.add_widget(info_label)
        
        # Name input
        name_label = Label(
            text='Nama Pengeluaran:',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14),
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        )
        layout.add_widget(name_label)
        
        self.name_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            hint_text='Contoh: Salar, Bensin, Plastik, Es Batu',
            font_size=dp(14)
        )
        layout.add_widget(self.name_input)
        
        # Amount input
        amount_label = Label(
            text='Jumlah Pengeluaran:',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14),
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        )
        layout.add_widget(amount_label)
        
        self.amount_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            hint_text='Masukkan jumlah dalam rupiah',
            input_filter='int',
            font_size=dp(14)
        )
        layout.add_widget(self.amount_input)
        
        # Action buttons
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(15))
        
        save_btn = Button(
            text='SIMPAN',
            background_color=(0.1, 0.7, 0.3, 1),
            font_size=dp(15),
            bold=True
        )
        save_btn.bind(on_press=self.save_expense)
        
        cancel_btn = Button(
            text='BATAL',
            background_color=(0.9, 0.2, 0.2, 1),
            font_size=dp(15),
            bold=True,
            size_hint_x=0.4
        )
        cancel_btn.bind(on_press=lambda x: self.dismiss())
        
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)
        layout.add_widget(buttons_layout)
        
        self.content = layout
    
    def save_expense(self, instance):
        name = self.name_input.text.strip()
        amount_text = self.amount_input.text.strip()
        
        if not name:
            self.app_ref.show_popup("Error", "Nama pengeluaran tidak boleh kosong!")
            return
        
        if not amount_text:
            self.app_ref.show_popup("Error", "Jumlah pengeluaran tidak boleh kosong!")
            return
        
        try:
            amount = int(amount_text)
            if amount <= 0:
                self.app_ref.show_popup("Error", "Jumlah pengeluaran harus lebih dari 0!")
                return
            
            expense_id = len(self.app_ref.daily_expenses) + 1
            expense = Expense(expense_id, name, amount, datetime.now())
            self.app_ref.daily_expenses.append(expense)
            
            self.app_ref.save_daily_expenses()
            
            try:
                expenses_screen = self.app_ref.root.get_screen('expenses')
                expenses_screen.refresh_expenses()
            except:
                pass
            
            self.app_ref.show_popup("Sukses", f"Pengeluaran '{name}' sebesar {self.app_ref.format_currency(amount)} berhasil ditambahkan!")
            self.dismiss()
            
        except ValueError:
            self.app_ref.show_popup("Error", "Masukkan jumlah yang valid!")

class ProductCard(BoxLayout):
    def __init__(self, product, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.product = product
        self.main_screen = main_screen
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(130)
        self.spacing = dp(3)
        self.padding = dp(5)
        
        # Simple card design
        with self.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
            Color(0.8, 0.8, 0.8, 1)
            Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)),
                width=1
            )
        
        self.bind(size=self.update_rect, pos=self.update_rect)
        
        # Product name
        name_label = Label(
            text=product.name,
            size_hint_y=None,
            height=dp(22),
            color=(0.1, 0.1, 0.1, 1),
            bold=True,
            font_size=dp(11),
            halign='center'
        )
        
        # Price
        price_label = Label(
            text=f'{self.main_screen.app_ref.format_currency(product.price_per_kg)}/kg',
            size_hint_y=None,
            height=dp(20),
            color=(0.1, 0.6, 0.1, 1),
            bold=True,
            font_size=dp(10)
        )
        
        # Stock
        stock_color = (0.1, 0.7, 0.1, 1) if product.stock_kg > 5 else (0.9, 0.6, 0.1, 1) if product.stock_kg > 0 else (0.9, 0.1, 0.1, 1)
        
        stock_label = Label(
            text=f'Stok: {product.stock_kg} kg',
            size_hint_y=None,
            height=dp(18),
            color=stock_color,
            font_size=dp(9),
            bold=True
        )
        
        # Buttons
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(3))
        
        self.add_btn = Button(
            text='+ TAMBAH' if product.stock_kg > 0 else 'HABIS',
            disabled=product.stock_kg <= 0,
            background_color=(0.1, 0.7, 0.3, 1) if product.stock_kg > 0 else (0.6, 0.6, 0.6, 1),
            font_size=dp(9),
            bold=True,
            size_hint_x=0.7
        )
        self.add_btn.bind(on_press=self.show_weight_input)
        
        delete_btn = Button(
            text='X',
            background_color=(0.9, 0.2, 0.2, 1),
            font_size=dp(10),
            size_hint_x=0.3
        )
        delete_btn.bind(on_press=self.confirm_delete)
        
        buttons_layout.add_widget(self.add_btn)
        buttons_layout.add_widget(delete_btn)
        
        self.add_widget(name_label)
        self.add_widget(price_label)
        self.add_widget(stock_label)
        self.add_widget(buttons_layout)
    
    def update_rect(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
            Color(0.8, 0.8, 0.8, 1)
            Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)),
                width=1
            )
    
    def show_weight_input(self, instance):
        WeightInputPopup(self.product, self.main_screen).open()
    
    def confirm_delete(self, instance):
        popup_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        message = Label(
            text=f'Yakin ingin menghapus produk:\n"{self.product.name}"?',
            size_hint_y=None,
            height=dp(60),
            font_size=dp(14),
            bold=True,
            halign='center'
        )
        popup_layout.add_widget(message)
        
        buttons_layout = BoxLayout(spacing=dp(15), size_hint_y=None, height=dp(45))
        
        yes_btn = Button(
            text='YA, HAPUS',
            background_color=(0.9, 0.1, 0.1, 1),
            font_size=dp(12),
            bold=True
        )
        
        no_btn = Button(
            text='BATAL',
            background_color=(0.5, 0.5, 0.5, 1),
            font_size=dp(12),
            bold=True
        )
        
        buttons_layout.add_widget(yes_btn)
        buttons_layout.add_widget(no_btn)
        popup_layout.add_widget(buttons_layout)
        
        confirm_popup = Popup(
            title='Konfirmasi Hapus',
            content=popup_layout,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )
        
        def delete_product(btn):
            self.main_screen.app_ref.products.remove(self.product)
            cart_items_to_remove = [item for item in self.main_screen.app_ref.cart if item.product.id == self.product.id]
            for item in cart_items_to_remove:
                self.main_screen.app_ref.cart.remove(item)
            
            self.main_screen.app_ref.save_products()
            self.main_screen.refresh_products()
            self.main_screen.refresh_cart()
            
            self.main_screen.app_ref.show_popup("Sukses", f'Produk "{self.product.name}" berhasil dihapus!')
            confirm_popup.dismiss()
        
        yes_btn.bind(on_press=delete_product)
        no_btn.bind(on_press=lambda x: confirm_popup.dismiss())
        confirm_popup.open()

class WeightInputPopup(Popup):
    def __init__(self, product, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.product = product
        self.main_screen = main_screen
        self.title = f'Input Berat - {product.name}'
        self.size_hint = (0.9, 0.7)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Product info
        info_label = Label(
            text=f'{product.name}\nHarga: {main_screen.app_ref.format_currency(product.price_per_kg)}/kg\nStok: {product.stock_kg} kg',
            size_hint_y=None,
            height=dp(70),
            font_size=dp(14),
            bold=True,
            halign='center',
            color=(0.2, 0.6, 0.2, 1)
        )
        layout.add_widget(info_label)
        
        # Weight input
        weight_label = Label(
            text='Masukkan Berat:',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14),
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='center'
        )
        layout.add_widget(weight_label)
        
        weight_input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.weight_input = TextInput(
            text='1.0',
            input_filter='float',
            multiline=False,
            font_size=dp(16),
            size_hint_x=0.8
        )
        
        kg_label = Label(
            text='KG',
            size_hint_x=0.2,
            font_size=dp(14),
            bold=True,
            color=(0.4, 0.4, 0.4, 1)
        )
        
        weight_input_layout.add_widget(self.weight_input)
        weight_input_layout.add_widget(kg_label)
        layout.add_widget(weight_input_layout)
        
        # Total preview
        self.total_label = Label(
            text='Total: Rp 0',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16),
            bold=True,
            color=(0.1, 0.6, 0.1, 1),
            halign='center'
        )
        layout.add_widget(self.total_label)
        
        # Bind weight input
        self.weight_input.bind(text=self.update_total)
        self.update_total(None, '1.0')
        
        # Action buttons
        buttons_layout = BoxLayout(spacing=dp(15), size_hint_y=None, height=dp(50))
        
        add_btn = Button(
            text='TAMBAH KE KERANJANG',
            background_color=(0.1, 0.7, 0.3, 1),
            font_size=dp(13),
            bold=True
        )
        add_btn.bind(on_press=self.add_to_cart)
        
        cancel_btn = Button(
            text='BATAL',
            background_color=(0.9, 0.2, 0.2, 1),
            font_size=dp(13),
            bold=True,
            size_hint_x=0.4
        )
        cancel_btn.bind(on_press=lambda x: self.dismiss())
        
        buttons_layout.add_widget(add_btn)
        buttons_layout.add_widget(cancel_btn)
        layout.add_widget(buttons_layout)
        
        self.content = layout
    
    def update_total(self, instance, text):
        try:
            weight = float(text) if text else 0
            total = self.product.price_per_kg * weight
            self.total_label.text = f'Total: {self.main_screen.app_ref.format_currency(total)}'
        except:
            self.total_label.text = 'Total: Rp 0'
    
    def add_to_cart(self, instance):
        try:
            weight = float(self.weight_input.text)
            
            if weight <= 0:
                self.main_screen.app_ref.show_popup("Error", "Berat harus lebih dari 0!")
                return
            
            if weight > self.product.stock_kg:
                self.main_screen.app_ref.show_popup("Error", f"Stok tidak mencukupi!\nStok tersedia: {self.product.stock_kg} kg")
                return
            
            # Check if product already in cart
            existing_item = None
            for cart_item in self.main_screen.app_ref.cart:
                if cart_item.product.id == self.product.id:
                    existing_item = cart_item
                    break
            
            if existing_item:
                if existing_item.weight_kg + weight > self.product.stock_kg + existing_item.weight_kg:
                    self.main_screen.app_ref.show_popup("Error", "Stok tidak mencukupi!")
                    return
                existing_item.weight_kg += weight
            else:
                cart_item = CartItem(self.product, weight)
                self.main_screen.app_ref.cart.append(cart_item)
            
            # Update stock
            self.product.stock_kg -= weight
            
            # Refresh displays
            self.main_screen.refresh_cart()
            self.main_screen.refresh_products()
            self.dismiss()
            
        except ValueError:
            self.main_screen.app_ref.show_popup("Error", "Masukkan berat yang valid!")
        except Exception as e:
            print(f"Error adding to cart: {e}")

class CartItemWidget(BoxLayout):
    def __init__(self, cart_item, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.cart_item = cart_item
        self.main_screen = main_screen
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(70)
        self.spacing = dp(2)
        self.padding = dp(5)
        
        # Simple card design
        with self.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(8)])
            Color(0.8, 0.8, 0.8, 1)
            Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(8)),
                width=1
            )
        
        self.bind(size=self.update_rect, pos=self.update_rect)
        
        # Top row
        top_row = BoxLayout(size_hint_y=None, height=dp(20))
        
        name_label = Label(
            text=cart_item.product.name,
            color=(0.1, 0.1, 0.1, 1),
            bold=True,
            font_size=dp(10),
            text_size=(dp(70), None),
            halign='left',
            size_hint_x=0.75
        )
        
        remove_btn = Button(
            text='X',
            size_hint_x=0.25,
            background_color=(0.9, 0.2, 0.2, 1),
            font_size=dp(9),
            bold=True
        )
        remove_btn.bind(on_press=self.remove_item)
        
        top_row.add_widget(name_label)
        top_row.add_widget(remove_btn)
        
        # Weight info
        self.weight_label = Label(
            text=f'{cart_item.weight_kg} kg × {self.main_screen.app_ref.format_currency(cart_item.product.price_per_kg)}/kg',
            color=(0.4, 0.4, 0.4, 1),
            font_size=dp(8),
            size_hint_y=None,
            height=dp(15)
        )
        
        # Total
        self.total_label = Label(
            text=f'{self.main_screen.app_ref.format_currency(cart_item.get_total())}',
            color=(0.1, 0.6, 0.1, 1),
            bold=True,
            font_size=dp(11),
            size_hint_y=None,
            height=dp(22)
        )
        
        self.add_widget(top_row)
        self.add_widget(self.weight_label)
        self.add_widget(self.total_label)
    
    def update_rect(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(8)])
            Color(0.8, 0.8, 0.8, 1)
            Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(8)),
                width=1
            )
    
    def remove_item(self, instance):
        self.main_screen.remove_cart_item(self.cart_item)

class AddProductPopup(Popup):
    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.title = 'Tambah Produk Baru'
        self.size_hint = (0.9, 0.8)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Header
        header_label = Label(
            text='Tambahkan Produk Ayam Baru',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16),
            bold=True,
            color=(0.2, 0.6, 0.2, 1),
            halign='center'
        )
        layout.add_widget(header_label)
        
        # Product name
        name_label = Label(
            text='Nama Produk:',
            size_hint_y=None,
            height=dp(25),
            font_size=dp(13),
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        )
        layout.add_widget(name_label)
        
        self.name_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            hint_text='Contoh: Sayap Ayam, Ceker, Ati Ampela',
            font_size=dp(14)
        )
        layout.add_widget(self.name_input)
        
        # Price per kg
        price_label = Label(
            text='Harga per Kg:',
            size_hint_y=None,
            height=dp(25),
            font_size=dp(13),
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        )
        layout.add_widget(price_label)
        
        self.price_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            hint_text='Masukkan harga per kilogram',
            input_filter='int',
            font_size=dp(14)
        )
        layout.add_widget(self.price_input)
        
        # Stock
        stock_label = Label(
            text='Stok (kg):',
            size_hint_y=None,
            height=dp(25),
            font_size=dp(13),
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        )
        layout.add_widget(stock_label)
        
        self.stock_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            hint_text='Masukkan stok dalam kilogram',
            input_filter='float',
            text='10',
            font_size=dp(14)
        )
        layout.add_widget(self.stock_input)
        
        # Action buttons
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(15))
        
        save_btn = Button(
            text='SIMPAN',
            background_color=(0.1, 0.7, 0.3, 1),
            font_size=dp(15),
            bold=True
        )
        save_btn.bind(on_press=self.save_product)
        
        cancel_btn = Button(
            text='BATAL',
            background_color=(0.9, 0.2, 0.2, 1),
            font_size=dp(15),
            bold=True,
            size_hint_x=0.4
        )
        cancel_btn.bind(on_press=lambda x: self.dismiss())
        
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)
        layout.add_widget(buttons_layout)
        
        self.content = layout
    
    def save_product(self, instance):
        name = self.name_input.text.strip()
        price_text = self.price_input.text.strip()
        stock_text = self.stock_input.text.strip()
        
        if not name:
            self.main_screen.app_ref.show_popup("Error", "Nama produk tidak boleh kosong!")
            return
        
        if not price_text:
            self.main_screen.app_ref.show_popup("Error", "Harga tidak boleh kosong!")
            return
        
        try:
            price = int(price_text)
            stock = float(stock_text) if stock_text else 10
            
            if price <= 0:
                self.main_screen.app_ref.show_popup("Error", "Harga harus lebih dari 0!")
                return
            
            if stock <= 0:
                self.main_screen.app_ref.show_popup("Error", "Stok harus lebih dari 0!")
                return
            
            max_id = max([p.id for p in self.main_screen.app_ref.products]) if self.main_screen.app_ref.products else 0
            new_id = max_id + 1
            
            new_product = Product(new_id, name, price, stock)
            self.main_screen.app_ref.products.append(new_product)
            
            self.main_screen.app_ref.save_products()
            self.main_screen.refresh_products()
            
            self.main_screen.app_ref.show_popup("Sukses", f"Produk '{name}' berhasil ditambahkan!")
            self.dismiss()
            
        except ValueError:
            self.main_screen.app_ref.show_popup("Error", "Harga dan stok harus berupa angka yang valid!")

class PaymentPopup(Popup):
    def __init__(self, total_amount, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.total_amount = total_amount
        self.main_screen = main_screen
        self.title = 'Pembayaran'
        self.size_hint = (0.9, 0.8)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Total
        total_label = Label(
            text=f'TOTAL PEMBAYARAN:\n{main_screen.app_ref.format_currency(total_amount)}',
            size_hint_y=None,
            height=dp(60),
            font_size=dp(18),
            bold=True,
            color=(0.1, 0.6, 0.1, 1),
            halign='center'
        )
        layout.add_widget(total_label)
        
        # Payment input
        payment_label = Label(
            text='Jumlah Bayar:',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(15),
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        )
        layout.add_widget(payment_label)
        
        self.payment_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            hint_text='Masukkan jumlah uang yang dibayar',
            input_filter='int',
            font_size=dp(16)
        )
        self.payment_input.bind(text=self.calculate_change)
        layout.add_widget(self.payment_input)
        
        # Change display
        self.change_label = Label(
            text='Kembalian: Rp 0',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16),
            bold=True,
            color=(0.2, 0.6, 0.2, 1),
            halign='center'
        )
        layout.add_widget(self.change_label)
        
        # Quick amount buttons
        quick_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(100))
        
        quick_amounts = [50000, 100000, 200000]
        colors = [(0.2, 0.6, 0.9, 1), (0.6, 0.2, 0.9, 1), (0.9, 0.2, 0.6, 1)]
        
        for amount, color in zip(quick_amounts, colors):
            btn = Button(
                text=f'{self.main_screen.app_ref.format_currency(amount)}',
                background_color=color,
                font_size=dp(11),
                bold=True
            )
            btn.bind(on_press=lambda x, amt=amount: self.set_payment_amount(amt))
            quick_layout.add_widget(btn)
        
        exact_btn = Button(
            text='UANG PAS',
            background_color=(0.9, 0.6, 0.1, 1),
            font_size=dp(11),
            bold=True
        )
        exact_btn.bind(on_press=lambda x: self.set_payment_amount(self.total_amount))
        quick_layout.add_widget(exact_btn)
        
        layout.add_widget(quick_layout)
        
        # Action buttons
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(15))
        
        self.pay_btn = Button(
            text='BAYAR & CETAK STRUK',
            background_color=(0.1, 0.7, 0.3, 1),
            font_size=dp(14),
            bold=True,
            disabled=True
        )
        self.pay_btn.bind(on_press=self.process_payment)
        
        cancel_btn = Button(
            text='BATAL',
            background_color=(0.9, 0.2, 0.2, 1),
            font_size=dp(14),
            bold=True,
            size_hint_x=0.4
        )
        cancel_btn.bind(on_press=lambda x: self.dismiss())
        
        buttons_layout.add_widget(self.pay_btn)
        buttons_layout.add_widget(cancel_btn)
        layout.add_widget(buttons_layout)
        
        self.content = layout
    
    def set_payment_amount(self, amount):
        self.payment_input.text = str(amount)
    
    def calculate_change(self, instance, text):
        try:
            payment = int(text) if text else 0
            change = payment - self.total_amount
            
            if payment >= self.total_amount:
                self.change_label.text = f'Kembalian: {self.main_screen.app_ref.format_currency(change)}'
                self.change_label.color = (0.1, 0.7, 0.1, 1)
                self.pay_btn.disabled = False
            else:
                self.change_label.text = f'Kurang: {self.main_screen.app_ref.format_currency(abs(change))}'
                self.change_label.color = (0.9, 0.1, 0.1, 1)
                self.pay_btn.disabled = True
        except:
            self.change_label.text = 'Kembalian: Rp 0'
            self.change_label.color = (0.5, 0.5, 0.5, 1)
            self.pay_btn.disabled = True
    
    def process_payment(self, instance):
        try:
            payment = int(self.payment_input.text)
            change = payment - self.total_amount
            
            self.main_screen.app_ref.last_payment = payment
            self.main_screen.app_ref.last_change = change
            
            self.main_screen.app_ref.checkout()
            self.dismiss()
            
        except ValueError:
            self.main_screen.app_ref.show_popup("Error", "Masukkan jumlah pembayaran yang valid!")

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = None
        self.build_ui()
    
    def build_ui(self):
        # Main layout with neon border
        main_layout = BoxLayout(orientation='vertical', spacing=dp(5))
        
        # Neon border container
        border_container = BoxLayout(padding=dp(4))
        with border_container.canvas.before:
            # Multi-color neon border effect
            Color(1, 0, 1, 0.8)  # Magenta
            Rectangle(size=border_container.size, pos=border_container.pos)
            Color(0, 1, 1, 0.6)  # Cyan overlay
            Rectangle(size=border_container.size, pos=border_container.pos)
            Color(1, 1, 0, 0.4)  # Yellow overlay
            Rectangle(size=border_container.size, pos=border_container.pos)
        
        # Inner content with semi-transparent background
        inner_layout = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(8))
        with inner_layout.canvas.before:
            Color(1, 1, 1, 0.9)  # Semi-transparent white
            Rectangle(size=inner_layout.size, pos=inner_layout.pos)
        
        # Navigation bar with neon colors
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        
        nav_buttons = [
            ('MENU', (1, 0, 1, 1), self.show_menu),  # Magenta
            ('PENGELUARAN', (0, 1, 0.5, 1), self.go_to_expenses),  # Neon green
            ('LAPORAN', (0, 0.5, 1, 1), self.go_to_reports)  # Neon blue
        ]
        
        for text, color, action in nav_buttons:
            btn = Button(
                text=text,
                background_color=color,
                font_size=dp(10),
                bold=True
            )
            btn.bind(on_press=action)
            nav_layout.add_widget(btn)
        
        inner_layout.add_widget(nav_layout)
        
        # Header
        self.header = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(10))
        with self.header.canvas.before:
            Color(0.2, 0.4, 0.8, 1)
            RoundedRectangle(size=self.header.size, pos=self.header.pos, radius=[dp(15)])
        
        self.title_label = Label(
            text='KASIR AYAM POTONG',
            color=(1, 1, 1, 1),
            font_size=dp(16),
            bold=True,
            halign='center'
        )
        self.header.add_widget(self.title_label)
        inner_layout.add_widget(self.header)
        
        # Content area
        content = BoxLayout(orientation='horizontal', spacing=dp(8))
        
        # Products section
        products_section = BoxLayout(orientation='vertical', size_hint_x=0.6, spacing=dp(5))
        
        # Add product button
        add_product_btn = Button(
            text='+ TAMBAH PRODUK',
            background_color=(0.1, 0.7, 0.3, 1),
            font_size=dp(12),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        add_product_btn.bind(on_press=self.show_add_product_popup)
        products_section.add_widget(add_product_btn)
        
        # Products grid
        products_scroll = ScrollView()
        self.products_grid = GridLayout(
            cols=1, 
            spacing=dp(5), 
            size_hint_y=None,
            padding=dp(5)
        )
        self.products_grid.bind(minimum_height=self.products_grid.setter('height'))
        products_scroll.add_widget(self.products_grid)
        products_section.add_widget(products_scroll)
        
        content.add_widget(products_section)
        
        # Cart section
        cart_section = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=dp(5))
        
        # Cart header
        cart_header = BoxLayout(size_hint_y=None, height=dp(40), padding=dp(8))
        with cart_header.canvas.before:
            Color(0.8, 0.2, 0.2, 1)
            RoundedRectangle(size=cart_header.size, pos=cart_header.pos, radius=[dp(10)])
        
        self.cart_title = Label(
            text='KERANJANG',
            color=(1, 1, 1, 1),
            font_size=dp(12),
            bold=True
        )
        cart_header.add_widget(self.cart_title)
        cart_section.add_widget(cart_header)
        
        # Cart items
        cart_scroll = ScrollView()
        self.cart_list = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            spacing=dp(3),
            padding=dp(5)
        )
        self.cart_list.bind(minimum_height=self.cart_list.setter('height'))
        cart_scroll.add_widget(self.cart_list)
        cart_section.add_widget(cart_scroll)
        
        # Total section
        self.total_label = Label(
            text='TOTAL: Rp 0',
            color=(0.1, 0.6, 0.1, 1),
            font_size=dp(14),
            bold=True,
            size_hint_y=None,
            height=dp(35)
        )
        cart_section.add_widget(self.total_label)
        
        # Action buttons
        buttons_section = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=dp(70), 
            spacing=dp(5)
        )
        
        self.checkout_btn = Button(
            text='BAYAR',
            background_color=(0.1, 0.7, 0.3, 1),
            font_size=dp(12),
            bold=True,
            disabled=True,
            size_hint_y=None,
            height=dp(45)
        )
        self.checkout_btn.bind(on_press=self.show_payment_popup)
        
        clear_btn = Button(
            text='KOSONGKAN',
            background_color=(0.9, 0.2, 0.2, 1),
            font_size=dp(10),
            bold=True,
            size_hint_y=None,
            height=dp(25)
        )
        clear_btn.bind(on_press=self.clear_cart)
        
        buttons_section.add_widget(self.checkout_btn)
        buttons_section.add_widget(clear_btn)
        cart_section.add_widget(buttons_section)
        
        content.add_widget(cart_section)
        inner_layout.add_widget(content)
        
        border_container.add_widget(inner_layout)
        main_layout.add_widget(border_container)
        self.add_widget(main_layout)
        
        Clock.schedule_once(self.load_products, 0.1)
    
    def show_menu(self, instance):
        popup_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        title = Label(
            text='MENU UTAMA',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(18),
            bold=True,
            halign='center',
            color=(0.2, 0.4, 0.8, 1)
        )
        popup_layout.add_widget(title)
        
        # Menu buttons
        buttons_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        menu_items = [
            ('Kelola Pengeluaran', (0.9, 0.4, 0.1, 1), lambda x: [menu_popup.dismiss(), self.go_to_expenses(x)]),
            ('Lihat Laporan', (0.1, 0.6, 0.9, 1), lambda x: [menu_popup.dismiss(), self.go_to_reports(x)]),
            ('Ubah Nama Pengguna', (0.6, 0.2, 0.9, 1), lambda x: [menu_popup.dismiss(), self.show_user_settings()])
        ]
        
        for text, color, action in menu_items:
            btn = Button(
                text=text,
                background_color=color,
                font_size=dp(14),
                bold=True,
                size_hint_y=None,
                height=dp(50)
            )
            btn.bind(on_press=action)
            buttons_layout.add_widget(btn)
        
        popup_layout.add_widget(buttons_layout)
        
        close_btn = Button(
            text='TUTUP',
            background_color=(0.5, 0.5, 0.5, 1),
            font_size=dp(14),
            bold=True,
            size_hint_y=None,
            height=dp(45)
        )
        close_btn.bind(on_press=lambda x: menu_popup.dismiss())
        popup_layout.add_widget(close_btn)
        
        menu_popup = Popup(
            title='Menu',
            content=popup_layout,
            size_hint=(0.8, 0.7),
            auto_dismiss=True
        )
        menu_popup.open()
    
    def show_user_settings(self):
        UserSetupPopup(self.app_ref).open()
    
    def go_to_expenses(self, instance):
        self.manager.current = 'expenses'
        expenses_screen = self.manager.get_screen('expenses')
        expenses_screen.refresh_expenses()
    
    def go_to_reports(self, instance):
        self.manager.current = 'reports'
        reports_screen = self.manager.get_screen('reports')
        reports_screen.reset_report_content()
    
    def update_header(self):
        if self.app_ref:
            header_text = f'KASIR AYAM POTONG\nKasir: {self.app_ref.username}'
            self.title_label.text = header_text
    
    def show_add_product_popup(self, instance):
        AddProductPopup(self).open()
    
    def show_payment_popup(self, instance):
        if self.app_ref and self.app_ref.cart:
            total = self.app_ref.get_cart_total()
            PaymentPopup(total, self).open()
    
    def load_products(self, dt=None):
        if self.app_ref:
            self.refresh_products()
    
    def refresh_products(self):
        self.products_grid.clear_widgets()
        
        if not self.app_ref:
            return
        
        for product in self.app_ref.products:
            product_widget = ProductCard(product, self)
            self.products_grid.add_widget(product_widget)
    
    def refresh_cart(self):
        self.cart_list.clear_widgets()
        
        if not self.app_ref or not self.app_ref.cart:
            empty_label = Label(
                text='Keranjang kosong\n\nTambahkan produk',
                color=(0.6, 0.6, 0.6, 1),
                font_size=dp(11),
                halign='center',
                size_hint_y=None,
                height=dp(60)
            )
            self.cart_list.add_widget(empty_label)
        else:
            for cart_item in self.app_ref.cart:
                item_widget = CartItemWidget(cart_item, self)
                self.cart_list.add_widget(item_widget)
        
        if self.app_ref:
            total = self.app_ref.get_cart_total()
            self.total_label.text = f'TOTAL: {self.app_ref.format_currency(total)}'
            
            total_weight = sum(item.weight_kg for item in self.app_ref.cart)
            total_items = len(self.app_ref.cart)
            self.cart_title.text = f'KERANJANG ({total_items} item, {total_weight} kg)'
            
            self.checkout_btn.disabled = len(self.app_ref.cart) == 0
    
    def remove_cart_item(self, cart_item):
        if self.app_ref:
            cart_item.product.stock_kg += cart_item.weight_kg
            self.app_ref.cart.remove(cart_item)
            self.refresh_cart()
            self.refresh_products()
    
    def clear_cart(self, instance):
        if not self.app_ref or not self.app_ref.cart:
            return
        
        for cart_item in self.app_ref.cart:
            cart_item.product.stock_kg += cart_item.weight_kg
        
        self.app_ref.cart = []
        self.refresh_cart()
        self.refresh_products()

class ExpensesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = None
        self.build_ui()
    
    def build_ui(self):
        # FIXED: Complete white background layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Pure white background for entire screen
        with main_layout.canvas.before:
            Color(1, 1, 1, 1)  # Pure white background
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        main_layout.bind(size=self.update_bg, pos=self.update_bg)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(10))
        with header.canvas.before:
            Color(0.1, 0.1, 0.1, 0.9)
            RoundedRectangle(size=header.size, pos=header.pos, radius=[dp(15)])
        
        header_label = Label(
            text='PENGELUARAN HARIAN\nManajemen Keuangan',
            color=(1, 1, 1, 1),
            font_size=dp(16),
            bold=True,
            halign='center'
        )
        header.add_widget(header_label)
        main_layout.add_widget(header)
        
        # Action buttons
        actions_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        
        add_expense_btn = Button(
            text='+ TAMBAH PENGELUARAN',
            background_color=(0.1, 0.8, 0.2, 1),
            font_size=dp(12),
            bold=True
        )
        add_expense_btn.bind(on_press=self.show_add_expense_popup)
        
        back_btn = Button(
            text='KEMBALI',
            background_color=(0.5, 0.5, 0.5, 1),
            font_size=dp(12),
            bold=True,
            size_hint_x=0.4
        )
        back_btn.bind(on_press=self.go_back)
        
        actions_layout.add_widget(add_expense_btn)
        actions_layout.add_widget(back_btn)
        main_layout.add_widget(actions_layout)
        
        # Today's total
        total_container = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(15))
        with total_container.canvas.before:
            Color(0, 0, 0, 0.8)
            RoundedRectangle(size=total_container.size, pos=total_container.pos, radius=[dp(15)])
            Color(1, 1, 0, 1)
            Line(
                rounded_rectangle=(total_container.x, total_container.y, total_container.width, total_container.height, dp(15)),
                width=3
            )
        
        self.total_expenses_label = Label(
            text='Total Pengeluaran Hari Ini: Rp 0',
            font_size=dp(18),
            bold=True,
            color=(1, 1, 0, 1),
            halign='center'
        )
        total_container.add_widget(self.total_expenses_label)
        main_layout.add_widget(total_container)
        
        # Date info
        today_str = date.today().strftime('%d/%m/%Y')
        date_container = BoxLayout(size_hint_y=None, height=dp(40), padding=dp(10))
        with date_container.canvas.before:
            Color(0, 0, 0, 0.7)
            RoundedRectangle(size=date_container.size, pos=date_container.pos, radius=[dp(10)])
        
        date_label = Label(
            text=f'Tanggal: {today_str}',
            font_size=dp(16),
            bold=True,
            color=(0, 1, 1, 1),
            halign='center'
        )
        date_container.add_widget(date_label)
        main_layout.add_widget(date_container)
        
        # Expenses list title
        expenses_title = Label(
            text='DAFTAR PENGELUARAN HARI INI',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(18),
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            halign='center'
        )
        main_layout.add_widget(expenses_title)
        
        # Expenses list
        expenses_scroll = ScrollView()
        self.expenses_list = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5),
            padding=dp(5)
        )
        self.expenses_list.bind(minimum_height=self.expenses_list.setter('height'))
        expenses_scroll.add_widget(self.expenses_list)
        main_layout.add_widget(expenses_scroll)
        
        self.add_widget(main_layout)
    
    def update_bg(self, instance, value):
        """Update background rectangle"""
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def show_add_expense_popup(self, instance):
        AddExpensePopup(self.app_ref).open()
    
    def go_back(self, instance):
        self.manager.current = 'main'
    
    def refresh_expenses(self):
        """Refresh expenses display"""
        self.expenses_list.clear_widgets()
        
        if not self.app_ref:
            return
        
        today = date.today()
        today_expenses = [exp for exp in self.app_ref.daily_expenses if exp.date_time.date() == today]
        
        if not today_expenses:
            empty_label = Label(
                text='Belum ada pengeluaran hari ini\n\nKlik "TAMBAH PENGELUARAN" untuk menambah',
                color=(0.2, 0.2, 0.2, 1),
                font_size=dp(15),
                bold=True,
                halign='center',
                size_hint_y=None,
                height=dp(80)
            )
            self.expenses_list.add_widget(empty_label)
        else:
            colors = [
                (0.8, 0.1, 0.1, 1),    # Red
                (0.1, 0.8, 0.1, 1),    # Green
                (0.1, 0.1, 0.8, 1),    # Blue
                (0.8, 0.6, 0.1, 1),    # Orange
                (0.8, 0.1, 0.8, 1),    # Magenta
                (0.1, 0.8, 0.8, 1),    # Cyan
            ]
            
            for i, expense in enumerate(today_expenses, 1):
                color = colors[(i-1) % len(colors)]
                expense_widget = self.create_expense_widget(expense, i, color)
                self.expenses_list.add_widget(expense_widget)
        
        # Update total
        total_today = sum(exp.amount for exp in today_expenses)
        self.total_expenses_label.text = f'Total Pengeluaran Hari Ini: {self.app_ref.format_currency(total_today)}'
    
    def create_expense_widget(self, expense, number, text_color):
        """Create simple expense widget with just colored text"""
        layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10),
            padding=dp(10)
        )
        
        # Number
        number_label = Label(
            text=f'{number}.',
            color=text_color,
            bold=True,
            font_size=dp(18),
            size_hint_x=0.15,
            halign='center'
        )
        
        # Info section
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.55)
        
        name_label = Label(
            text=expense.name,
            color=text_color,
            bold=True,
            font_size=dp(15),
            text_size=(dp(120), None),
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        
        time_label = Label(
            text=f'Waktu: {expense.date_time.strftime("%H:%M:%S")}',
            color=(0.4, 0.4, 0.4, 1),
            font_size=dp(12),
            text_size=(dp(120), None),
            halign='left',
            size_hint_y=None,
            height=dp(25)
        )
        
        info_layout.add_widget(name_label)
        info_layout.add_widget(time_label)
        
        # Amount
        amount_label = Label(
            text=self.app_ref.format_currency(expense.amount),
            color=text_color,
            bold=True,
            font_size=dp(14),
            halign='center',
            size_hint_x=0.3
        )
        
        layout.add_widget(number_label)
        layout.add_widget(info_layout)
        layout.add_widget(amount_label)
        
        return layout

class ReportsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = None
        self.build_ui()
    
    def build_ui(self):
        # FIXED: Complete white background layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Pure white background for entire screen
        with main_layout.canvas.before:
            Color(1, 1, 1, 1)  # Pure white background
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        main_layout.bind(size=self.update_bg, pos=self.update_bg)
        
        # Header with blue background
        header = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(10))
        with header.canvas.before:
            Color(0, 0, 0, 0.9)
            RoundedRectangle(size=header.size, pos=header.pos, radius=[dp(15)])
        
        header_label = Label(
            text='LAPORAN PENJUALAN\nDashboard Keuangan',
            color=(0, 1, 1, 1),
            font_size=dp(16),
            bold=True,
            halign='center'
        )
        header.add_widget(header_label)
        main_layout.add_widget(header)
        
        # Action buttons
        actions_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(8))
        
        generate_btn = Button(
            text='BUAT LAPORAN\nHARI INI',
            background_color=(0.1, 0.8, 0.2, 1),
            font_size=dp(12),
            bold=True
        )
        generate_btn.bind(on_press=self.generate_daily_report)
        
        history_btn = Button(
            text='RIWAYAT\nLAPORAN',
            background_color=(0.8, 0.4, 0.1, 1),
            font_size=dp(12),
            bold=True
        )
        history_btn.bind(on_press=self.show_report_history)
        
        back_btn = Button(
            text='KEMBALI',
            background_color=(0.5, 0.5, 0.5, 1),
            font_size=dp(12),
            bold=True,
            size_hint_x=0.4
        )
        back_btn.bind(on_press=self.go_back)
        
        actions_layout.add_widget(generate_btn)
        actions_layout.add_widget(history_btn)
        actions_layout.add_widget(back_btn)
        main_layout.add_widget(actions_layout)
        
        # Report title
        report_title = Label(
            text='LAPORAN HARI INI',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(20),
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            halign='center'
        )
        main_layout.add_widget(report_title)
        
        # Report content with scroll view
        report_scroll = ScrollView()
        
        # Report text with black text on white background
        self.report_content = Label(
            text='Klik "BUAT LAPORAN HARI INI" untuk melihat ringkasan\n\nLaporan akan menampilkan:\n\n• Total Pendapatan\n• Total Pengeluaran\n• Keuntungan Bersih\n• Detail Transaksi\n• Detail Pengeluaran\n\nSemua data tersimpan otomatis',
            color=(0, 0, 0, 1),  # Black text
            font_size=dp(16),
            bold=True,
            text_size=(dp(320), None),
            halign='center',
            valign='top',
            size_hint_y=None,
            height=dp(300)
        )
        
        def update_height(instance, text):
            if text:
                lines = text.count('\n') + 1
                calculated_height = max(dp(300), lines * dp(20))
                instance.height = calculated_height
        
        self.report_content.bind(text=update_height)
        
        report_scroll.add_widget(self.report_content)
        main_layout.add_widget(report_scroll)
        
        self.add_widget(main_layout)
    
    def update_bg(self, instance, value):
        """Update background rectangle"""
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def reset_report_content(self):
        """Reset report content when navigating"""
        self.report_content.text = 'Klik "BUAT LAPORAN HARI INI" untuk melihat ringkasan\n\nLaporan akan menampilkan:\n\n• Total Pendapatan\n• Total Pengeluaran\n• Keuntungan Bersih\n• Detail Transaksi\n• Detail Pengeluaran\n\nSemua data tersimpan otomatis'
    
    def go_back(self, instance):
        self.reset_report_content()
        self.manager.current = 'main'
    
    def generate_daily_report(self, instance):
        """Generate daily report"""
        if not self.app_ref:
            return
        
        today = date.today()
        today_str = today.strftime('%d/%m/%Y')
        
        # Get today's transactions
        today_transactions = []
        try:
            if os.path.exists('transactions/transactions.json'):
                with open('transactions/transactions.json', 'r', encoding='utf-8') as f:
                    all_transactions = json.load(f)
                    today_transactions = [t for t in all_transactions if t['date'] == today_str]
        except:
            pass
        
        # Get today's expenses
        today_expenses = [exp for exp in self.app_ref.daily_expenses if exp.date_time.date() == today]
        
        # Calculate totals
        total_income = sum(t['subtotal'] for t in today_transactions)
        total_expenses = sum(exp.amount for exp in today_expenses)
        net_profit = total_income - total_expenses
        
        # Generate report
        report_lines = []
        report_lines.append("=" * 40)
        report_lines.append(f"         LAPORAN HARIAN")
        report_lines.append(f"           {today_str}")
        report_lines.append(f"       {self.app_ref.shop_name}")
        report_lines.append(f"      Kasir: {self.app_ref.username}")
        report_lines.append("=" * 40)
        report_lines.append("")
        report_lines.append("RINGKASAN PENJUALAN:")
        report_lines.append("-" * 40)
        report_lines.append(f"Jumlah Transaksi    : {len(today_transactions)}")
        report_lines.append(f"Total Pendapatan    : {self.app_ref.format_currency(total_income)}")
        report_lines.append("")
        
        if today_transactions:
            report_lines.append("DETAIL TRANSAKSI:")
            report_lines.append("-" * 40)
            for i, trans in enumerate(today_transactions, 1):
                report_lines.append(f"{i:2d}. {trans['receipt_number']} - {trans['time']}")
                report_lines.append(f"    Total: {self.app_ref.format_currency(trans['subtotal'])}")
                if i < len(today_transactions):
                    report_lines.append("")
        else:
            report_lines.append("DETAIL TRANSAKSI:")
            report_lines.append("-" * 40)
            report_lines.append("Belum ada transaksi hari ini")
        
        report_lines.append("")
        report_lines.append("PENGELUARAN HARI INI:")
        report_lines.append("-" * 40)
        
        if today_expenses:
            for i, exp in enumerate(today_expenses, 1):
                time_str = exp.date_time.strftime('%H:%M')
                report_lines.append(f"{i:2d}. {time_str} - {exp.name}")
                report_lines.append(f"    {self.app_ref.format_currency(exp.amount)}")
                if i < len(today_expenses):
                    report_lines.append("")
        else:
            report_lines.append("Belum ada pengeluaran hari ini")
        
        report_lines.append("")
        report_lines.append("-" * 40)
        report_lines.append(f"TOTAL PENGELUARAN   : {self.app_ref.format_currency(total_expenses)}")
        report_lines.append("")
        report_lines.append("=" * 40)
        report_lines.append("KEUNTUNGAN BERSIH:")
        if net_profit >= 0:
            report_lines.append(f"+ {self.app_ref.format_currency(net_profit)}")
        else:
            report_lines.append(f"- {self.app_ref.format_currency(abs(net_profit))}")
        report_lines.append("=" * 40)
        report_lines.append("")
        report_lines.append(f"Laporan dibuat: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report_lines.append(f"Oleh: {self.app_ref.username}")
        
        report_text = "\n".join(report_lines)
        self.report_content.text = report_text
        
        # Auto save report
        self.save_daily_report(report_text, today_str)
        
        # Reset daily expenses
        self.reset_daily_expenses()
        
        # Show success message
        profit_text = "PROFIT" if net_profit >= 0 else "LOSS"
        self.app_ref.show_popup("Laporan Berhasil", f"Laporan harian berhasil dibuat!\n\n{profit_text}: {self.app_ref.format_currency(abs(net_profit))}\n\nPengeluaran harian telah di-reset")
    
    def reset_daily_expenses(self):
        """Reset daily expenses after generating report"""
        self.app_ref.daily_expenses = []
        self.app_ref.save_daily_expenses()
        
        try:
            expenses_screen = self.app_ref.root.get_screen('expenses')
            expenses_screen.refresh_expenses()
        except:
            pass
    
    def save_daily_report(self, report_text, date_str):
        """Auto save daily report"""
        try:
            if not os.path.exists('reports'):
                os.makedirs('reports')
            
            filename = f"reports/laporan_{date_str.replace('/', '_')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            print(f"Laporan tersimpan: {filename}")
            
        except Exception as e:
            print(f"Gagal menyimpan laporan: {str(e)}")
    
    def show_report_history(self, instance):
        """Show saved reports history"""
        try:
            if not os.path.exists('reports'):
                self.app_ref.show_popup("Info", "Belum ada laporan tersimpan")
                return
            
            report_files = [f for f in os.listdir('reports') if f.endswith('.txt')]
            
            if not report_files:
                self.app_ref.show_popup("Info", "Belum ada laporan tersimpan")
                return
            
            # Simple popup design
            popup_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
            
            title = Label(
                text='RIWAYAT LAPORAN',
                size_hint_y=None,
                height=dp(40),
                font_size=dp(18),
                bold=True,
                color=(0.2, 0.6, 0.8, 1),
                halign='center'
            )
            popup_layout.add_widget(title)
            
            # Reports list
            scroll = ScrollView()
            reports_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
            reports_list.bind(minimum_height=reports_list.setter('height'))
            
            colors = [
                (0.8, 0.1, 0.1, 1),    # Red
                (0.1, 0.8, 0.1, 1),    # Green
                (0.1, 0.1, 0.8, 1),    # Blue
                (0.8, 0.6, 0.1, 1),    # Orange
                (0.8, 0.1, 0.8, 1),    # Magenta
                (0.1, 0.8, 0.8, 1),    # Cyan
            ]
            
            for i, report_file in enumerate(sorted(report_files, reverse=True), 1):
                date_part = report_file.replace('laporan_', '').replace('.txt', '').replace('_', '/')
                color = colors[(i-1) % len(colors)]
                
                report_btn = Button(
                    text=f'{i}. Laporan {date_part}',
                    background_color=color,
                    font_size=dp(14),
                    bold=True,
                    size_hint_y=None,
                    height=dp(50)
                )
                report_btn.bind(on_press=lambda x, file=report_file: [history_popup.dismiss(), self.show_saved_report(file)])
                
                reports_list.add_widget(report_btn)
            
            scroll.add_widget(reports_list)
            popup_layout.add_widget(scroll)
            
            close_btn = Button(
                text='TUTUP',
                size_hint_y=None,
                height=dp(45),
                background_color=(0.5, 0.5, 0.5, 1),
                font_size=dp(14),
                bold=True
            )
            close_btn.bind(on_press=lambda x: history_popup.dismiss())
            popup_layout.add_widget(close_btn)
            
            history_popup = Popup(
                title='Riwayat Laporan',
                content=popup_layout,
                size_hint=(0.9, 0.8),
                auto_dismiss=True
            )
            history_popup.open()
            
        except Exception as e:
            self.app_ref.show_popup("Error", f"Gagal memuat riwayat: {str(e)}")
    
    def update_bg(self, instance, value):
        """Update background rectangle"""
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def show_saved_report(self, filename):
        """Show saved report with high contrast"""
        try:
            with open(f'reports/{filename}', 'r', encoding='utf-8') as f:
                content = f.read()
            
            popup_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))
            
            # Header
            date_part = filename.replace('laporan_', '').replace('.txt', '').replace('_', '/')
            title_label = Label(
                text=f'LAPORAN {date_part}',
                size_hint_y=None,
                height=dp(40),
                font_size=dp(18),
                bold=True,
                color=(0.2, 0.6, 0.8, 1),
                halign='center'
            )
            popup_layout.add_widget(title_label)
            
            # Content with white background
            content_container = BoxLayout(orientation='vertical', padding=dp(15))
            with content_container.canvas.before:
                Color(1, 1, 1, 1)
                RoundedRectangle(size=content_container.size, pos=content_container.pos, radius=[dp(12)])
                Color(0.2, 0.2, 0.2, 1)
                Line(
                    rounded_rectangle=(content_container.x, content_container.y, content_container.width, content_container.height, dp(12)),
                    width=2
                )
            
            scroll = ScrollView()
            
            content_label = Label(
                text=content,
                color=(0, 0, 0, 1),
                font_size=dp(14),
                text_size=(dp(280), None),
                halign='left',
                valign='top',
                size_hint_y=None
            )
            
            def update_content_height(instance, text):
                lines = text.count('\n') + 1
                instance.height = max(dp(400), lines * dp(17))
            
            content_label.bind(text=update_content_height)
            content_label.text = content
            
            scroll.add_widget(content_label)
            content_container.add_widget(scroll)
            popup_layout.add_widget(content_container)
            
            close_btn = Button(
                text='TUTUP',
                size_hint_y=None,
                height=dp(45),
                background_color=(0.5, 0.5, 0.5, 1),
                font_size=dp(14),
                bold=True
            )
            close_btn.bind(on_press=lambda x: report_popup.dismiss())
            popup_layout.add_widget(close_btn)
            
            report_popup = Popup(
                title=f'Laporan {date_part}',
                content=popup_layout,
                size_hint=(0.95, 0.9),
                auto_dismiss=True
            )
            report_popup.open()
            
        except Exception as e:
            self.app_ref.show_popup("Error", f"Gagal membuka laporan: {str(e)}")

class ReceiptScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = None
        self.receipt_data = None
        self.build_ui()
    
    def build_ui(self):
        # FIXED: Complete white background layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Pure white background for entire screen
        with main_layout.canvas.before:
            Color(1, 1, 1, 1)  # Pure white background
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        main_layout.bind(size=self.update_bg, pos=self.update_bg)
        
        # Header with green background
        header = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(10))
        with header.canvas.before:
            Color(0.2, 0.6, 0.2, 1)
            RoundedRectangle(size=header.size, pos=header.pos, radius=[dp(15)])
        
        header_label = Label(
            text='STRUK PEMBELIAN\nTransaksi Berhasil',
            color=(1, 1, 1, 1),
            font_size=dp(16),
            bold=True,
            halign='center'
        )
        header.add_widget(header_label)
        main_layout.add_widget(header)
        
        # Receipt content with scroll view
        receipt_scroll = ScrollView()
        
        # Receipt text with black text on white background
        self.receipt_content = Label(
            text='Memuat struk pembelian...',
            color=(0, 0, 0, 1),  # Black text
            font_size=dp(14),
            text_size=(dp(320), None),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(400)
        )
        
        def update_receipt_height(instance, text):
            if text:
                lines = text.count('\n') + 1
                calculated_height = max(dp(400), lines * dp(18))
                instance.height = calculated_height
        
        self.receipt_content.bind(text=update_receipt_height)
        
        receipt_scroll.add_widget(self.receipt_content)
        main_layout.add_widget(receipt_scroll)
        
        # Action button
        new_transaction_btn = Button(
            text='TRANSAKSI BARU',
            background_color=(0.1, 0.7, 0.3, 1),
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(55)
        )
        new_transaction_btn.bind(on_press=self.new_transaction)
        main_layout.add_widget(new_transaction_btn)
        
        self.add_widget(main_layout)
    
    def update_bg(self, instance, value):
        """Update background rectangle"""
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def show_receipt(self, receipt_data):
        """Display receipt with clear formatting"""
        self.receipt_data = receipt_data
        
        # Generate receipt text
        receipt_lines = []
        receipt_lines.append("=" * 38)
        receipt_lines.append(f"         {self.app_ref.shop_name.upper()}")
        receipt_lines.append("     Jl. Pasar Ayam No. 123, Jakarta")
        receipt_lines.append("          Telp: 021-12345678")
        receipt_lines.append("=" * 38)
        receipt_lines.append("")
        receipt_lines.append(f"No. Transaksi : {receipt_data['receipt_number']}")
        receipt_lines.append(f"Tanggal       : {receipt_data['date']}")
        receipt_lines.append(f"Waktu         : {receipt_data['time']}")
        receipt_lines.append(f"Kasir         : {self.app_ref.username}")
        receipt_lines.append("")
        receipt_lines.append("-" * 38)
        receipt_lines.append("ITEM              BERAT    TOTAL")
        receipt_lines.append("-" * 38)
        
        for name, weight, price_per_kg, total in receipt_data['items']:
            name_part = name[:15].ljust(15)
            weight_part = f"{weight} kg".rjust(8)
            total_part = f"{total:,}".rjust(12)
            receipt_lines.append(f"{name_part} {weight_part} {total_part}")
        
        receipt_lines.append("-" * 38)
        receipt_lines.append("")
        
        subtotal_str = f"{receipt_data['subtotal']:,}".rjust(12)
        receipt_lines.append(f"TOTAL                : Rp {subtotal_str}")
        
        if hasattr(self.app_ref, 'last_payment') and self.app_ref.last_payment > 0:
            payment_str = f"{self.app_ref.last_payment:,}".rjust(12)
            change_str = f"{self.app_ref.last_change:,}".rjust(12)
            receipt_lines.append(f"BAYAR                : Rp {payment_str}")
            receipt_lines.append(f"KEMBALIAN            : Rp {change_str}")
        
        receipt_lines.append("=" * 38)
        receipt_lines.append("")
        receipt_lines.append("    Terima kasih atas kunjungan Anda!")
        receipt_lines.append("      Ayam segar berkualitas terbaik")
        receipt_lines.append("")
        receipt_lines.append("-" * 38)
        receipt_lines.append("    Software: Kasir Ayam Potong v1.0")
        receipt_lines.append("-" * 38)
        
        receipt_text = "\n".join(receipt_lines)
        self.receipt_content.text = receipt_text
        
        self.auto_save_receipt()
    
    def auto_save_receipt(self):
        """Auto save receipt"""
        if self.receipt_data and self.app_ref:
            try:
                if not os.path.exists('receipts'):
                    os.makedirs('receipts')
                
                filename = f"receipts/receipt_{self.receipt_data['receipt_number']}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.receipt_content.text)
                
                print(f"Struk tersimpan: {filename}")
                
            except Exception as e:
                print(f"Gagal menyimpan struk: {str(e)}")
    
    def new_transaction(self, instance):
        self.manager.current = 'main'
        main_screen = self.manager.get_screen('main')
        main_screen.refresh_cart()
        main_screen.refresh_products()

class KasirApp(App):
    def build(self):
        self.title = "Kasir Ayam Potong"
        
        # Load user config
        self.username, self.shop_name = self.load_user_config()
        
        self.products = self.load_products()
        self.cart = []
        self.daily_expenses = self.load_daily_expenses()
        self.transaction_counter = self.load_transaction_counter()
        self.last_payment = 0
        self.last_change = 0
        
        sm = ScreenManager()
        
        main_screen = MainScreen(name='main')
        main_screen.app_ref = self
        sm.add_widget(main_screen)
        
        expenses_screen = ExpensesScreen(name='expenses')
        expenses_screen.app_ref = self
        sm.add_widget(expenses_screen)
        
        reports_screen = ReportsScreen(name='reports')
        reports_screen.app_ref = self
        sm.add_widget(reports_screen)
        
        receipt_screen = ReceiptScreen(name='receipt')
        receipt_screen.app_ref = self
        sm.add_widget(receipt_screen)
        
        # Check if user setup is needed
        if not self.username:
            Clock.schedule_once(self.show_user_setup, 0.5)
        else:
            Clock.schedule_once(lambda dt: main_screen.update_header(), 0.1)
        
        return sm
    
    def load_user_config(self):
        try:
            if os.path.exists('user_config.json'):
                with open('user_config.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('username', ''), data.get('shop_name', 'Toko Ayam Potong')
        except:
            pass
        return '', 'Toko Ayam Potong'
    
    def load_daily_expenses(self):
        """Load daily expenses"""
        try:
            today = date.today().strftime('%Y-%m-%d')
            filename = f'expenses/expenses_{today}.json'
            
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    expenses = []
                    for item in data:
                        expense_date = datetime.strptime(item['date_time'], '%Y-%m-%d %H:%M:%S')
                        expenses.append(Expense(
                            item['id'], item['name'], item['amount'], expense_date
                        ))
                    return expenses
        except:
            pass
        return []
    
    def save_daily_expenses(self):
        """Save daily expenses"""
        try:
            if not os.path.exists('expenses'):
                os.makedirs('expenses')
            
            today = date.today().strftime('%Y-%m-%d')
            filename = f'expenses/expenses_{today}.json'
            
            data = []
            today_expenses = [exp for exp in self.daily_expenses if exp.date_time.date() == date.today()]
            
            for expense in today_expenses:
                data.append({
                    'id': expense.id,
                    'name': expense.name,
                    'amount': expense.amount,
                    'date_time': expense.date_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error saving expenses: {e}")
    
    def show_user_setup(self, dt):
        UserSetupPopup(self).open()
    
    def load_products(self):
        try:
            if os.path.exists('products.json'):
                with open('products.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    products = []
                    for item in data:
                        products.append(Product(
                            item['id'], item['name'], item['price_per_kg'], 
                            item['stock_kg']
                        ))
                    return products
        except:
            pass
        
        return [
            Product(1, "Sayap Ayam", 35000, 15.0),
            Product(2, "Ceker Ayam", 25000, 10.0),
            Product(3, "Ati Ampela", 30000, 8.0),
            Product(4, "Dada Ayam", 45000, 12.0),
            Product(5, "Paha Ayam", 40000, 20.0),
            Product(6, "Leher Ayam", 20000, 5.0),
        ]
    
    def save_products(self):
        try:
            data = []
            for product in self.products:
                data.append({
                    'id': product.id,
                    'name': product.name,
                    'price_per_kg': product.price_per_kg,
                    'stock_kg': product.stock_kg
                })
            with open('products.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving products: {e}")
    
    def load_transaction_counter(self):
        try:
            if os.path.exists('counter.json'):
                with open('counter.json', 'r') as f:
                    data = json.load(f)
                    return data.get('counter', 1)
        except:
            pass
        return 1
    
    def save_transaction_counter(self):
        try:
            with open('counter.json', 'w') as f:
                json.dump({'counter': self.transaction_counter}, f)
        except Exception as e:
            print(f"Error saving counter: {e}")
    
    def format_currency(self, amount):
        try:
            return f"Rp {amount:,.0f}".replace(',', '.')
        except:
            return "Rp 0"
    
    def get_cart_total(self):
        try:
            return sum(item.get_total() for item in self.cart)
        except:
            return 0
    
    def checkout(self):
        try:
            if not self.cart:
                self.show_popup("Error", "Keranjang kosong!")
                return
            
            receipt_data = self.generate_receipt()
            self.save_transaction(receipt_data)
            
            self.cart = []
            
            self.transaction_counter += 1
            self.save_transaction_counter()
            self.save_products()
            
            receipt_screen = self.root.get_screen('receipt')
            receipt_screen.show_receipt(receipt_data)
            self.root.current = 'receipt'
            
        except Exception as e:
            print(f"Error during checkout: {e}")
            self.show_popup("Error", f"Gagal checkout: {str(e)}")
    
    def generate_receipt(self):
        try:
            now = datetime.now()
            receipt_number = f"TRX{self.transaction_counter:06d}"
            
            subtotal = self.get_cart_total()
            
            receipt_data = {
                'receipt_number': receipt_number,
                'date': now.strftime('%d/%m/%Y'),
                'time': now.strftime('%H:%M:%S'),
                'username': self.username,
                'shop_name': self.shop_name,
                'items': [(item.product.name, item.weight_kg, item.product.price_per_kg, item.get_total()) 
                         for item in self.cart],
                'subtotal': subtotal,
                'payment': getattr(self, 'last_payment', 0),
                'change': getattr(self, 'last_change', 0)
            }
            
            return receipt_data
            
        except Exception as e:
            print(f"Error generating receipt: {e}")
            return {}
    
    def save_transaction(self, receipt_data):
        """Auto save transaction"""
        try:
            if not os.path.exists('transactions'):
                os.makedirs('transactions')
            
            transactions = []
            transaction_file = 'transactions/transactions.json'
            
            if os.path.exists(transaction_file):
                with open(transaction_file, 'r', encoding='utf-8') as f:
                    transactions = json.load(f)
            
            transactions.append(receipt_data)
            
            with open(transaction_file, 'w', encoding='utf-8') as f:
                json.dump(transactions, f, ensure_ascii=False, indent=2)
            
            print(f"Transaksi tersimpan: {receipt_data['receipt_number']}")
            
        except Exception as e:
            print(f"Error saving transaction: {e}")
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, text_size=(dp(250), None), halign='center', font_size=dp(14), bold=True),
            size_hint=(0.85, 0.5),
            auto_dismiss=True
        )
        popup.open()

if __name__ == '__main__':
    KasirApp().run()



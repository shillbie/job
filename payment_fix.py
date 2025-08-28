# Temporary file untuk memperbaiki payment popup di KasirMainScreen
# Akan di-copy ke main.py

def show_payment_kasir_main(self, instance):
    """Show payment popup - KasirMainScreen version"""
    if not self.app_ref or not self.app_ref.cart:
        return
        
    total = sum(item.get_total() for item in self.app_ref.cart)
    
    # Create popup content
    content = BoxLayout(orientation='vertical', spacing=15, padding=20)
    
    # Total amount
    total_layout = BoxLayout(size_hint_y=None, height=40)
    total_label = Label(
        text='Total Pembayaran:',
        size_hint_x=0.6,
        font_size='16sp',
        bold=True
    )
    total_amount = Label(
        text=self.app_ref.format_currency(total),
        size_hint_x=0.4,
        font_size='18sp',
        bold=True,
        color=(0.2, 0.6, 0.2, 1),
        halign='right'
    )
    total_layout.add_widget(total_label)
    total_layout.add_widget(total_amount)
    
    # Payment input
    payment_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
    payment_label = Label(text='Jumlah Bayar:', size_hint_x=0.4)
    payment_input = TextInput(
        input_filter='float',
        multiline=False,
        size_hint_x=0.6,
        font_size='16sp',
        text=str(int(total))
    )
    payment_layout.add_widget(payment_label)
    payment_layout.add_widget(payment_input)
    
    # Quick payment buttons
    quick_payment_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
    
    def set_payment_amount(amount):
        payment_input.text = str(amount)
        update_change(None, None)
    
    # Tombol pembayaran cepat
    pas_btn = Button(text='PAS', font_size='12sp', size_hint_x=0.25)
    pas_btn.bind(on_press=lambda x: set_payment_amount(int(total)))
    
    btn_50k = Button(text='50K', font_size='12sp', size_hint_x=0.25)
    btn_50k.bind(on_press=lambda x: set_payment_amount(50000))
    
    btn_100k = Button(text='100K', font_size='12sp', size_hint_x=0.25)
    btn_100k.bind(on_press=lambda x: set_payment_amount(100000))
    
    btn_200k = Button(text='200K', font_size='12sp', size_hint_x=0.25)
    btn_200k.bind(on_press=lambda x: set_payment_amount(200000))
    
    quick_payment_layout.add_widget(pas_btn)
    quick_payment_layout.add_widget(btn_50k)
    quick_payment_layout.add_widget(btn_100k)
    quick_payment_layout.add_widget(btn_200k)
    
    # Change display
    change_layout = BoxLayout(size_hint_y=None, height=40, opacity=0)
    change_label = Label(
        text='Kembalian:',
        size_hint_x=0.4,
        font_size='16sp',
        bold=True
    )
    change_amount = Label(
        text='Rp 0',
        size_hint_x=0.6,
        font_size='16sp',
        bold=True,
        color=(0.2, 0.2, 0.8, 1),
        halign='right'
    )
    change_layout.add_widget(change_label)
    change_layout.add_widget(change_amount)
    
    # Buttons
    btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
    cancel_btn = Button(text='BATAL')
    process_btn = Button(
        text='PROSES',
        background_color=(0.2, 0.8, 0.2, 1),
        font_size='14sp',
        disabled=True
    )
    btn_layout.add_widget(cancel_btn)
    btn_layout.add_widget(process_btn)
    
    # Add all widgets to content
    content.add_widget(total_layout)
    content.add_widget(payment_layout)
    content.add_widget(quick_payment_layout)
    content.add_widget(change_layout)
    content.add_widget(btn_layout)
    
    # Create and open popup
    popup = Popup(
        title='Pembayaran',
        content=content,
        size_hint=(0.9, 0.7)
    )
    
    def update_change(instance, value):
        try:
            payment = float(payment_input.text) if payment_input.text else 0
            change = payment - total
            
            if payment >= total:
                change_layout.opacity = 1
                change_amount.text = self.app_ref.format_currency(change)
                process_btn.disabled = False
                process_btn.background_color = (0.2, 0.8, 0.2, 1)  # Green
            else:
                change_layout.opacity = 0.5
                change_amount.text = self.app_ref.format_currency(0)
                process_btn.disabled = True
                process_btn.background_color = (0.8, 0.2, 0.2, 1)  # Red
                
        except ValueError:
            change_layout.opacity = 0.5
            process_btn.disabled = True
    
    def process_payment(instance):
        try:
            payment = float(payment_input.text) if payment_input.text else 0
            if payment >= total:
                # Process the payment
                change = payment - total
                
                # Create transaction record
                transaction = {
                    'timestamp': datetime.now().isoformat(),
                    'items': [
                        {
                            'name': item.product.name,
                            'weight': item.weight_kg,
                            'price_per_kg': item.product.price_per_kg,
                            'total': item.get_total()
                        }
                        for item in self.app_ref.cart
                    ],
                    'total': total,
                    'payment': payment,
                    'change': change
                }
                
                # Save transaction
                self.app_ref.save_transaction(transaction)
                
                # Clear cart
                self.app_ref.cart.clear()
                self.update_cart_display()
                
                # Show success message
                success_popup = Popup(
                    title='Pembayaran Berhasil',
                    content=Label(
                        text=f'Pembayaran berhasil!\nKembalian: {self.app_ref.format_currency(change)}',
                        halign='center'
                    ),
                    size_hint=(0.8, 0.4)
                )
                success_popup.open()
                
                popup.dismiss()
        except ValueError:
            pass
    
    # Bind events
    payment_input.bind(text=update_change)
    cancel_btn.bind(on_press=lambda x: popup.dismiss())
    process_btn.bind(on_press=process_payment)
    
    # Initial update
    update_change(None, None)
    
    popup.open()

#!/usr/bin/env python3
"""
Test script untuk memverifikasi emoji font di Kivy
"""

import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.text import LabelBase

class EmojiTestApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Test 1: Default font
        label1 = Label(
            text="Default Font: 🎉🟢🔴💰🆕🔄🚀📤📊🚨💬📱👥🪙",
            font_size='20sp',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(label1)
        
        # Test 2: Try to register and use emoji font
        try:
            # Check Windows emoji fonts
            emoji_fonts = [
                "C:/Windows/Fonts/seguiemj.ttf",
                "C:/Windows/Fonts/segoeui.ttf", 
                "C:/Windows/Fonts/arial.ttf"
            ]
            
            font_found = None
            for font_path in emoji_fonts:
                if os.path.exists(font_path):
                    font_found = font_path
                    print(f"Found font: {font_path}")
                    break
            
            if font_found:
                LabelBase.register(name="TestEmojiFont", fn_regular=font_found)
                
                label2 = Label(
                    text=f"With Font ({os.path.basename(font_found)}): 🎉🟢🔴💰🆕🔄🚀📤📊🚨💬📱👥🪙",
                    font_name="TestEmojiFont",
                    font_size='20sp',
                    size_hint_y=None,
                    height=50
                )
                layout.add_widget(label2)
            else:
                label2 = Label(
                    text="❌ No emoji font found on system",
                    font_size='16sp',
                    size_hint_y=None,
                    height=50
                )
                layout.add_widget(label2)
                
        except Exception as e:
            error_label = Label(
                text=f"Error: {str(e)}",
                font_size='14sp',
                size_hint_y=None,
                height=50
            )
            layout.add_widget(error_label)
        
        # Test 3: System info
        info_label = Label(
            text=f"OS: {os.name}\nPlatform: Windows" if os.name == 'nt' else f"OS: {os.name}",
            font_size='14sp',
            size_hint_y=None,
            height=100
        )
        layout.add_widget(info_label)
        
        return layout

if __name__ == '__main__':
    EmojiTestApp().run()

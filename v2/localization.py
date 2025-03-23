#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import configparser
from pathlib import Path

class LocalizationManager:
    def __init__(self, base_dir=None):
        if base_dir is None:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.base_dir = base_dir
            
        self.locales_dir = os.path.join(self.base_dir, 'locales')
        self.config = self._load_config()
        self.current_language = self.config.get('General', 'language', fallback='fr')
        self.strings = self._load_strings(self.current_language)
    
    def _load_config(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(self.base_dir, 'config.ini')
        
        if os.path.exists(config_path):
            config.read(config_path)
        
        return config
    
    def _load_strings(self, language):
        strings = configparser.ConfigParser()
        strings_path = os.path.join(self.locales_dir, language, 'strings.ini')
        
        if os.path.exists(strings_path):
            with open(strings_path, "r", encoding="utf-8") as f:
                strings.read_file(f)
        else:
            fallback_paths = [
                os.path.join(self.locales_dir, 'en', 'strings.ini'),
                os.path.join(self.locales_dir, 'fr', 'strings.ini')
            ]
            for fallback_path in fallback_paths:
                if os.path.exists(fallback_path):
                    with open(fallback_path, "r", encoding="utf-8") as f:
                        strings.read_file(f)
                    break
        
        return strings
    
    def get_string(self, section, key, fallback=None):
        if section in self.strings and key in self.strings[section]:
            return self.strings[section][key]
        return fallback
    
    def change_language(self, language):
        if language not in self.get_available_languages():
            return False
        
        self.current_language = language
        self.strings = self._load_strings(language)
        
        self.config.set('General', 'language', language)
        self._save_config()
        
        return True
    
    def get_available_languages(self):
        languages = []
        
        if os.path.exists(self.locales_dir):
            for item in os.listdir(self.locales_dir):
                if os.path.isdir(os.path.join(self.locales_dir, item)):
                    if os.path.exists(os.path.join(self.locales_dir, item, 'strings.ini')):
                        languages.append(item)
        
        return languages
    
    def get_language_display_name(self, language_code):
        language_names = {
            'en': 'English',
            'fr': 'Français',
            'es': 'Español',
            'pt': 'Português',
            'nl': 'Nederlands',
            'de': 'Deutsch',
            'jp': '日本語',
            'ru': 'Русский',
            'cn': '中文'
        }
        
        return language_names.get(language_code, language_code)
    
    def _save_config(self):
        config_path = os.path.join(self.base_dir, 'config.ini')
        with open(config_path, 'w') as configfile:
            self.config.write(configfile)


class ThemeManager:
    def __init__(self, base_dir=None):
        if base_dir is None:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.base_dir = base_dir
            
        self.themes_dir = os.path.join(self.base_dir, 'themes')
        self.config = self._load_config()
        self.current_theme = self.config.get('General', 'theme', fallback='dark')
    
    def _load_config(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(self.base_dir, 'config.ini')
        
        if os.path.exists(config_path):
            config.read(config_path)
        
        return config
    
    def get_theme_path(self, theme_name=None):
        if theme_name is None:
            theme_name = self.current_theme
            
        theme_path = os.path.join(self.themes_dir, f'{theme_name}.css')
        
        if not os.path.exists(theme_path):
            theme_path = os.path.join(self.themes_dir, 'dark.css')
        
        return theme_path
    
    def change_theme(self, theme_name):
        if theme_name not in self.get_available_themes():
            return False
        
        self.current_theme = theme_name
        
        self.config.set('General', 'theme', theme_name)
        self._save_config()
        
        return True
    
    def get_available_themes(self):
        themes = []
        
        if os.path.exists(self.themes_dir):
            for item in os.listdir(self.themes_dir):
                if item.endswith('.css'):
                    themes.append(os.path.splitext(item)[0])
        
        return themes
    
    def _save_config(self):
        config_path = os.path.join(self.base_dir, 'config.ini')
        with open(config_path, 'w') as configfile:
            self.config.write(configfile)


if __name__ == "__main__":
    localization = LocalizationManager()
    print(f"Langue actuelle: {localization.current_language}")
    print(f"Langues disponibles: {localization.get_available_languages()}")
    print(f"Titre de l'application: {localization.get_string('General', 'app_title', 'Hoshi Iso Builder')}")
    
    theme_manager = ThemeManager()
    print(f"Thème actuel: {theme_manager.current_theme}")
    print(f"Thèmes disponibles: {theme_manager.get_available_themes()}")
    print(f"Chemin du thème actuel: {theme_manager.get_theme_path()}")

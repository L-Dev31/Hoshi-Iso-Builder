#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hoshi Iso Builder - README

Ce fichier contient les informations sur l'utilisation de Hoshi Iso Builder.
"""

# Hoshi Iso Builder

## Description
Hoshi Iso Builder est un outil graphique permettant de patcher des mods avec des custom codes sur des fichiers WBFS/ISO de jeux Wii. L'application offre une interface simple et intuitive pour sélectionner les fichiers nécessaires et appliquer les patches.

## Fonctionnalités
- Interface graphique moderne avec thème sombre violet et option de thème clair
- Support multilingue (fr, en, es, pt, nl, de, jp, ru, cn)
- Sélection de fichiers ISO/WBFS, XML et dossier de mods
- Interface de sélection des patches avec options et choix
- Construction automatisée des ISO/WBFS patché
- Configuration via config.ini pour la langue et le thème

## Prérequis
- Python 3.6 ou supérieur
- Bibliothèques Python : tkinter, PIL (Pillow), lxml
- Les outils externes (WIT, GeckoLoader) doivent être présents dans le dossier "tools"

## Installation
1. Assurez-vous que Python est installé sur votre système
2. Installez les dépendances requises :
   ```
   pip install pillow lxml
   ```
3. Placez les outils externes dans le dossier "tools" à la racine du projet

## Utilisation
1. Lancez l'application en exécutant `launcher.py` :
   ```
   python launcher.py
   ```
2. Sélectionnez le fichier ISO/WBFS du jeu Wii
3. Sélectionnez le fichier XML Riivolution
4. Sélectionnez le dossier contenant les fichiers de mod
5. Cliquez sur "Construire" pour lancer le processus
6. Sélectionnez les patches à appliquer dans la fenêtre qui s'ouvre
7. Attendez la fin du processus de construction

## Configuration
Le fichier `config.ini` permet de configurer :
- La langue de l'interface (language = fr, en, es, pt, nl, de, jp, ru, cn)
- Le thème de l'interface (theme = dark, light)
- Les chemins des outils externes

## Crédits
- Hoshi Iso Builder par L-DEV
- Riiv Converter par Humming Owl
- WIT par Wiimm
- GeckoLoader par [placeholder]

# -*- mode: python ; coding: utf-8 -*-

a = Analysis(['app.py'],
             pathex=[], # O PyInstaller geralmente detecta o caminho sozinho
             binaries=[],
             datas=[
                 ('templates', 'templates', 'DATA'),
                 ('static', 'static', 'DATA'),
                 ('logo.png', '.', 'DATA'),
                 ('database.db', '.', 'DATA')
             ],
             hiddenimports=['waitress'], # 'waitress' é suficiente
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='PlanejadorDeColetas',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,  # Importante: False para não abrir o console
          icon=None) # Adicione o caminho para um .ico se tiver

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='PlanejadorDeColetas')


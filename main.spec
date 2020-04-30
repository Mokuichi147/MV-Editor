# -*- mode: python ; coding: utf-8 -*-

from kivy.deps import sdl2, glew

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\Mokuichi147\\github\\MV-Editor'],
             binaries=[],
             datas=[],
             hiddenimports=['pkg_resources.py2_warn', 'win32file', 'win32timezone'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          Tree('resources', prefix='resources'),
          Tree('fonts', prefix='fonts'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='MV-Editor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False)

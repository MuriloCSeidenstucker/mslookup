# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['mslookup\\main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/resources/laboratories.json', 'data/resources'),
        ('data/resources/patterns.json', 'data/resources'),
        ('data/resources/pdf_db.json', 'data/resources'),
        ('data/resources/stop_words.json', 'data/resources'),
        ('data/anvisa/DADOS_ABERTOS_MEDICAMENTOS.xlsx', 'data/anvisa'),
        ('data/anvisa/TA_PRECO_MEDICAMENTO_GOV.xlsx', 'data/anvisa'),
        ('data/registers_pdf', 'data/registers_pdf')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)

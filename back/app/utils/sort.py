from pypinyin import lazy_pinyin


def name_az_key(name: str) -> str:
    """姓名按拼音/字母 A-Z 排序键（中文转拼音，英文保持字母序）。"""
    return ''.join(lazy_pinyin(name or '')).lower()

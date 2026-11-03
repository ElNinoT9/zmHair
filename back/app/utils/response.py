from urllib.parse import quote


class ApiException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


def content_disposition_attachment(filename: str, ascii_fallback: str = 'download.bin') -> str:
    """HTTP 头仅支持 latin-1，中文文件名须用 filename*（RFC 5987）。"""
    encoded = quote(filename, safe='')
    safe_ascii = ''.join(c if ord(c) < 128 and c not in '"\\' else '_' for c in ascii_fallback)
    if not safe_ascii.strip('._'):
        safe_ascii = 'download.bin'
    return f'attachment; filename="{safe_ascii}"; filename*=UTF-8\'\'{encoded}'

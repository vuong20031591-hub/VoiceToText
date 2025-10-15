"""
Safe print utility for Windows console
"""
import sys


def safe_print(*args, **kwargs):
    """
    Print với encoding an toàn cho Windows console
    Tự động fallback sang ASCII nếu UTF-8 fail
    """
    try:
        # Try UTF-8 first
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback: Convert to ASCII
        try:
            ascii_args = []
            for arg in args:
                if isinstance(arg, str):
                    # Replace Vietnamese và special chars
                    cleaned = arg.encode('ascii', 'ignore').decode('ascii')
                    ascii_args.append(cleaned)
                else:
                    ascii_args.append(arg)
            print(*ascii_args, **kwargs)
        except Exception:
            # Last resort: just skip the problematic print
            pass


# Monkey patch built-in print
if sys.platform == 'win32':
    import builtins
    builtins.print = safe_print

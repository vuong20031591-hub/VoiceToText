"""
Vietnamese Text Corrector - Auto-correct Vietnamese text
"""
import re


class VietnameseTextCorrector:
    """Bộ sửa lỗi văn bản tiếng Việt tự động"""

    def __init__(self, config: dict):
        """Khởi tạo text corrector"""
        self.config = config
        self.enabled = config.get('enabled', True)
        self.method = config.get('method', 'dictionary')
        self.show_original = config.get('show_original', True)

        # Khởi tạo dictionaries
        self._init_correction_dictionaries()

    def _init_correction_dictionaries(self):
        """Khởi tạo từ điển sửa lỗi nâng cao"""
        # Dictionary cho dấu thanh phổ biến (mở rộng)
        self.tone_corrections = {
            # Chào hỏi cơ bản
            "xin chao": "xin chào",
            "chao ban": "chào bạn",
            "chao": "chào",
            "cam on": "cảm ơn",
            "cam ơn": "cảm ơn",
            "cảm on": "cảm ơn",

            # Giới thiệu bản thân
            "toi ten la": "tôi tên là",
            "toi ten": "tôi tên",
            "toi la": "tôi là",
            "ten toi": "tên tôi",
            "ten toi la": "tên tôi là",

            # Hỏi thăm sức khỏe
            "ban khoe khong": "bạn khỏe không",
            "ban co khoe khong": "bạn có khỏe không",
            "ban the nao": "bạn thế nào",
            "ban ra sao": "bạn ra sao",

            # Sửa lỗi nhận dạng phổ biến "quê" thành "khỏe"
            "ban que khong": "bạn khỏe không",
            "xin chao ban que khong": "xin chào bạn khỏe không",
            "chao ban que khong": "chào bạn khỏe không",
            "ban que ko": "bạn khỏe không",
            "ban que hem": "bạn khỏe không",

            # Cảm xúc
            "rat vui": "rất vui",
            "rat vui duoc gap": "rất vui được gặp",
            "rat vui duoc gap ban": "rất vui được gặp bạn",
            "rat hanh phuc": "rất hạnh phúc",
            "rat buon": "rất buồn",

            # Thời gian
            "hom nay": "hôm nay",
            "ngay mai": "ngày mai",
            "tuan sau": "tuần sau",
            "thang sau": "tháng sau",
            "nam sau": "năm sau",
            "bao gio": "bao giờ",
            "khi nao": "khi nào",

            # Gia đình
            "bo me": "bố mẹ",
            "anh em": "anh em",
            "chi em": "chị em",
            "ong ba": "ông bà",

            # Học tập làm việc
            "di hoc": "đi học",
            "di lam": "đi làm",
            "hoc tap": "học tập",
            "lam viec": "làm việc",
            "cong viec": "công việc",

            # Ăn uống
            "an com": "ăn cơm",
            "uong nuoc": "uống nước",
            "an sang": "ăn sáng",
            "an trua": "ăn trưa",
            "an toi": "ăn tối",

            # Từ vựng phổ biến khác
            "nha": "nhà",
            "nha ban": "nhà bạn",
            "o dau": "ở đâu",
            "lam gi": "làm gì",
            "the nao": "thế nào",
            "ra sao": "ra sao",
            "biet khong": "biết không",
            "hieu khong": "hiểu không",
            "duoc khong": "được không",
            "co the": "có thể",
            "khong the": "không thể",
            "phai khong": "phải không",
            "dung khong": "đúng không",
            "sai khong": "sai không",

            # Add các từ còn thiếu
            "duoc gap": "được gặp",
            "ban rat nhieu": "bạn rất nhiều",
            "cam on ban rat nhieu": "cảm ơn bạn rất nhiều",
            "hen gap lai": "hẹn gặp lại",
            "hen gap lai ban": "hẹn gặp lại bạn",
            "troi dep": "trời đẹp",
            "dep qua": "đẹp quá",
            "troi dep qua": "trời đẹp quá",
            "nguyen van": "Nguyễn Văn",
            "toi ten la nguyen": "tôi tên là Nguyễn",

            # Các từ ghép phổ biến
            "rat nhieu": "rất nhiều",
            "qua nhieu": "quá nhiều",
            "rat it": "rất ít",
            "qua it": "quá ít",
            "rat dep": "rất đẹp",
            "qua dep": "quá đẹp",
            "rat tot": "rất tốt",
            "qua tot": "quá tốt",
            
            # Lỗi nhận dạng dấu thanh thường gặp
            "co gi": "có gì",
            "lam gi": "làm gì",
            "vi sao": "vì sao",
            "nhu the nao": "như thế nào",
            "ra sao": "ra sao",
            "ban co": "bạn có",
            "toi co": "tôi có",
            "chung ta": "chúng ta",
            "ho co": "họ có",
            "cac ban": "các bạn",
            
            # Tên riêng và địa danh
            "ha noi": "Hà Nội",
            "ho chi minh": "Hồ Chí Minh",
            "sai gon": "Sài Gòn",
            "viet nam": "Việt Nam",
            "da nang": "Đà Nẵng",
            "can tho": "Cần Thơ",
            
            # Số đếm
            "mot": "một",
            "hai": "hai",
            "ba": "ba",
            "bon": "bốn",
            "nam": "năm",
            "sau": "sáu",
            "bay": "bảy",
            "tam": "tám",
            "chin": "chín",
            "muoi": "mười"
        }

        # Dictionary cho từ đồng âm (homophones)
        self.homophone_corrections = {
            # Ăn chua vs ăn trưa
            "an chua": {
                "context_keywords": ["trua", "sang", "toi", "com", "bua"],
                "correction": "ăn trưa"
            },
            "chua an": {
                "context_keywords": ["trua", "sang", "toi", "com", "bua"],
                "correction": "chưa ăn"
            },

            # Đi chùa vs đi chưa
            "di chua": {
                "context_keywords": ["chua", "den", "le", "phat"],
                "correction": "đi chùa"
            },
            "chua di": {
                "context_keywords": ["chua", "den", "le", "phat"],
                "correction": "chưa đi"
            },

            # Quê vs khỏe (lỗi nhận dạng phổ biến)
            "que": {
                "context_keywords": ["ban", "khong", "ko", "hem", "the", "nao", "ra", "sao"],
                "correction": "khỏe"
            },
            "ban que": {
                "context_keywords": ["khong", "ko", "hem", "the", "nao"],
                "correction": "bạn khỏe"
            },

            # Học vs hoc
            "hoc": {
                "context_keywords": ["truong", "lop", "bai", "giao", "sinh"],
                "correction": "học"
            },

            # Làm vs lam
            "lam": {
                "context_keywords": ["viec", "cong", "ty", "van", "phong"],
                "correction": "làm"
            }
        }

        # Patterns cho normalization
        self.normalization_patterns = [
            # Loại bỏ khoảng trắng thừa
            (r'\s+', ' '),
            # Add khoảng trắng sau dấu câu
            (r'([.!?])([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ])', r'\1 \2'),
            # Loại bỏ khoảng trắng trước dấu câu
            (r'\s+([.!?,:;])', r'\1'),
        ]

    def correct_text(self, text: str, language: str = "vi") -> str:
        """Sửa lỗi văn bản tiếng Việt với các tính năng nâng cao"""
        if not self.enabled or language != "vi" or not text:
            return text

        original_text = text
        corrected_text = text

        try:
            # 1. Tiền xử lý: chuẩn hóa khoảng trắng và ký tự đặc biệt
            corrected_text = self._preprocess_text(corrected_text)
            
            # 2. Sửa dấu thanh (phần quan trọng nhất)
            if self.config.get('fix_tone_marks', True):
                corrected_text = self._fix_tone_marks_advanced(corrected_text)

            # 3. Sửa từ đồng âm theo ngữ cảnh
            if self.config.get('fix_homophones', True):
                corrected_text = self._fix_homophones_advanced(corrected_text)

            # 4. Sửa lỗi chính tả phổ biến
            if self.config.get('vietnamese_specific', {}).get('correct_common_errors', True):
                corrected_text = self._fix_common_vietnamese_errors(corrected_text)

            # 5. Chuẩn hóa văn bản
            if self.config.get('normalize_text', True):
                corrected_text = self._normalize_text_advanced(corrected_text)

            # 6. Sửa ngữ pháp cơ bản
            if self.config.get('fix_grammar', True):
                corrected_text = self._fix_basic_grammar_advanced(corrected_text)
                
            # 7. Viết hoa thông minh
            if self.config.get('smart_capitalization', True):
                corrected_text = self._apply_smart_capitalization(corrected_text)
                
            # 8. Sửa lỗi theo ngữ cảnh (context-aware)
            if self.config.get('context_correction', True):
                corrected_text = self._apply_context_correction(corrected_text)

            # Log thay đổi nếu cần
            if self.show_original and corrected_text != original_text:
                print(f"[TEXT] Văn bản gốc: '{original_text}'")
                print(f"✨ Văn bản đã sửa: '{corrected_text}'")

            return corrected_text

        except Exception as e:
            print(f"[ERROR] Lỗi text correction: {e}")
            return original_text
            
    def _preprocess_text(self, text: str) -> str:
        """Tiền xử lý văn bản"""
        # Loại bỏ khoảng trắng thừa
        text = " ".join(text.split())
        
        # Loại bỏ ký tự lạ (nhưng giữ lại dấu thanh tiếng Việt)
        import re
        text = re.sub(r'[^\w\s\u00c0-\u1ef9.,!?;:-]', '', text)
        
        return text.strip()
        
    def _fix_tone_marks_advanced(self, text: str) -> str:
        """Sửa dấu thanh tiếng Việt nâng cao"""
        text_lower = text.lower().strip()
        original_case = text and text[0].isupper()

        # Sắp xếp theo độ dài giảm dần để ưu tiên cụm từ dài hơn
        sorted_corrections = sorted(self.tone_corrections.items(),
                                  key=lambda x: len(x[0]), reverse=True)

        # Áp dụng dictionary corrections
        for wrong, correct in sorted_corrections:
            if wrong in text_lower:
                text_lower = text_lower.replace(wrong, correct)

        # Giữ nguyên case của từ đầu tiên
        if original_case and text_lower:
            text_lower = text_lower[0].upper() + text_lower[1:] if len(text_lower) > 1 else text_lower.upper()

        return text_lower
        
    def _fix_homophones_advanced(self, text: str) -> str:
        """Sửa từ đồng âm dựa trên ngữ cảnh nâng cao"""
        text_lower = text.lower()
        words = text_lower.split()

        for i, word in enumerate(words):
            if word in self.homophone_corrections:
                homophone_data = self.homophone_corrections[word]
                context_keywords = homophone_data["context_keywords"]
                correction = homophone_data["correction"]

                # Kiểm tra ngữ cảnh mở rộng (7 từ trước và sau)
                context_window = 7
                start_idx = max(0, i - context_window)
                end_idx = min(len(words), i + context_window + 1)
                context_words = words[start_idx:end_idx]

                # Nếu tìm thấy từ khóa ngữ cảnh, áp dụng correction
                if any(keyword in " ".join(context_words) for keyword in context_keywords):
                    words[i] = correction

        return " ".join(words)
        
    def _fix_common_vietnamese_errors(self, text: str) -> str:
        """Sửa các lỗi chính tả phổ biến trong tiếng Việt"""
        # Các lỗi thường gặp
        common_errors = {
            # Lỗi dấu câu
            " ,": ",",
            " .": ".",
            " !": "!",
            " ?": "?",
            "( ": "(",
            " )": ")",
            
            # Lỗi khoảng trắng
            "  ": " ",
            "   ": " ",
            
            # Lỗi nhận dạng số
            " 1 ": " một ",
            " 2 ": " hai ",
            " 3 ": " ba ",
            " 4 ": " bốn ",
            " 5 ": " năm ",
        }
        
        for error, correction in common_errors.items():
            text = text.replace(error, correction)
            
        return text
        
    def _normalize_text_advanced(self, text: str) -> str:
        """Chuẩn hóa văn bản nâng cao"""
        import re

        # Áp dụng normalization patterns
        for pattern, replacement in self.normalization_patterns:
            text = re.sub(pattern, replacement, text)

        # Chuẩn hóa dấu câu
        text = re.sub(r'\s+([.!?,:;])', r'\1', text)  # Loại bỏ khoảng trắng trước dấu câu
        text = re.sub(r'([.!?])([A-ZÀ-ỹ])', r'\1 \2', text)  # Add khoảng trắng sau dấu câu

        # Trim whitespace
        text = text.strip()

        return text
        
    def _fix_basic_grammar_advanced(self, text: str) -> str:
        """Sửa ngữ pháp cơ bản tiếng Việt"""
        if not text:
            return text

        # Viết hoa chữ cái đầu câu
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()

        # Add dấu chấm cuối câu nếu cần (thông minh hơn)
        if text and not text.endswith(('.', '!', '?', ':', ';')):
            # Kiểm tra xem có phải câu hỏi không
            question_indicators = [
                'ai', 'gì', 'đâu', 'nào', 'sao', 'thế nào', 'ra sao', 
                'bao giờ', 'khi nào', 'không', 'chưa', 'có phải', 'tại sao',
                'vì sao', 'bằng cách nào', 'như thế nào'
            ]
            
            text_lower = text.lower()
            is_question = any(indicator in text_lower for indicator in question_indicators)
            
            if is_question:
                text += '?'
            else:
                text += '.'

        return text
        
    def _apply_smart_capitalization(self, text: str) -> str:
        """Viết hoa thông minh cho tiếng Việt"""
        # Viết hoa tên riêng, địa danh
        proper_nouns = {
            'việt nam': 'Việt Nam',
            'hà nội': 'Hà Nội',
            'hồ chí minh': 'Hồ Chí Minh',
            'sài gòn': 'Sài Gòn',
            'đà nẵng': 'Đà Nẵng',
            'cần thơ': 'Cần Thơ',
            'nguyễn': 'Nguyễn',
            'trần': 'Trần',
            'lê': 'Lê',
            'phạm': 'Phạm',
            'hoàng': 'Hoàng',
            'huỳnh': 'Huỳnh',
            'vũ': 'Vũ',
            'vư': 'Vư',
            'đặng': 'Đặng'
        }
        
        text_lower = text.lower()
        for proper, correct in proper_nouns.items():
            text_lower = text_lower.replace(proper, correct)
            
        return text_lower
        
    def _apply_context_correction(self, text: str) -> str:
        """Sửa lỗi theo ngữ cảnh"""
        # Context-aware corrections cho tiếng Việt
        context_rules = [
            # Nếu có "xin chào" thì thường kèm theo "bạn"
            (r'xin chào(?!.*bạn)', 'xin chào bạn'),
            
            # Nếu có "cảm ơn" thì thường kèm theo "bạn"
            (r'cảm ơn(?!.*bạn)', 'cảm ơn bạn'),
            
            # Sửa "bạn" thành "bạn" khi đứng sau "chào"
            (r'chào ban(?!\w)', 'chào bạn'),
        ]
        
        import re
        for pattern, replacement in context_rules:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            
        return text

    def _fix_tone_marks(self, text: str) -> str:
        """Sửa dấu thanh tiếng Việt"""
        text_lower = text.lower().strip()
        original_case = text and text[0].isupper()

        # Sắp xếp theo độ dài giảm dần để ưu tiên cụm từ dài hơn
        sorted_corrections = sorted(self.tone_corrections.items(),
                                  key=lambda x: len(x[0]), reverse=True)

        # Áp dụng dictionary corrections
        for wrong, correct in sorted_corrections:
            if wrong in text_lower:
                text_lower = text_lower.replace(wrong, correct)

        # Giữ nguyên case của từ đầu tiên
        if original_case and text_lower:
            text_lower = text_lower[0].upper() + text_lower[1:] if len(text_lower) > 1 else text_lower.upper()

        return text_lower

    def _fix_homophones(self, text: str) -> str:
        """Sửa từ đồng âm dựa trên ngữ cảnh"""
        text_lower = text.lower()
        words = text_lower.split()

        for i, word in enumerate(words):
            if word in self.homophone_corrections:
                homophone_data = self.homophone_corrections[word]
                context_keywords = homophone_data["context_keywords"]
                correction = homophone_data["correction"]

                # Kiểm tra ngữ cảnh xung quanh
                context_window = 3  # Kiểm tra 3 từ trước và sau
                start_idx = max(0, i - context_window)
                end_idx = min(len(words), i + context_window + 1)
                context_words = words[start_idx:end_idx]

                # Nếu tìm thấy từ khóa ngữ cảnh, áp dụng correction
                if any(keyword in " ".join(context_words) for keyword in context_keywords):
                    words[i] = correction

        return " ".join(words)

    def _normalize_text(self, text: str) -> str:
        """Chuẩn hóa văn bản"""
        import re

        # Áp dụng normalization patterns
        for pattern, replacement in self.normalization_patterns:
            text = re.sub(pattern, replacement, text)

        # Trim whitespace
        text = text.strip()

        return text

    def _fix_basic_grammar(self, text: str) -> str:
        """Sửa ngữ pháp cơ bản"""
        if not text:
            return text

        # Viết hoa chữ cái đầu câu
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()

        # Add dấu chấm cuối câu nếu cần
        if text and not text.endswith(('.', '!', '?', ':')):
            # Kiểm tra xem có phải câu hỏi không
            question_words = ['ai', 'gì', 'đâu', 'nào', 'sao', 'thế nào', 'ra sao', 'bao giờ', 'khi nào', 'không', 'chưa']
            if any(word in text.lower() for word in question_words):
                text += '?'
            else:
                text += '.'

        return text

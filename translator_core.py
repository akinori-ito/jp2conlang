import sqlite3
import math
from janome.tokenizer import Tokenizer
from vocabulary_generator import VocabularyGenerator

class LanguageTranslator:
    def __init__(self, db_path="lang_dict.db", n_gram=3):
        # 語彙生成器の初期化
        self.generator = VocabularyGenerator(n=n_gram)
        self.tokenizer = Tokenizer()
        
        # データベースのセットアップ
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        """日本語と人工言語の対応表を作成"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dictionary (
                japanese_word TEXT PRIMARY KEY,
                conlang_word TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def train_generator(self, corpus_text):
        """人工言語の元となる統計情報を学習"""
        self.generator.train_from_string(corpus_text)
    
    def train_generator_from_file(self, corpus_file):
        """人工言語の元となる統計情報を学習"""
        self.generator.train_from_file(corpus_file)

    def get_translation(self, jp_word):
        """辞書にあれば返し、なければ新しく生成して保存する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT conlang_word FROM dictionary WHERE japanese_word = ?", (jp_word,))
        row = cursor.fetchone()

        if row:
            return row[0]
        else:
            # 日本語の長さに比例した長さを計算（例：日本語長 * 2 前後）
            # 最低でも3文字、日本語1文字につき約2文字の人工言語を割り当て
            gen_length = max(3, math.ceil(len(jp_word) * 2.5))
            new_word = self.generator.generate_word(gen_length)
            
            # 辞書に保存
            cursor.execute("INSERT INTO dictionary (japanese_word, conlang_word) VALUES (?, ?)", 
                           (jp_word, new_word))
            self.conn.commit()
            return new_word

    def translate_sentence(self, sentence):
        """文章を解析して翻訳（語順逆転ルール適用）"""
        tokens = self.tokenizer.tokenize(sentence)
        
        # 1. 形態素解析して各単語を翻訳
        translated_words = []
        for token in tokens:
            # 助詞や記号も含めて全て翻訳対象とする（または品詞でフィルタリングも可能）
            jp_word = token.surface
            con_word = self.get_translation(jp_word)
            translated_words.append(con_word)
        
        # 2. 語順を逆転させる
        translated_words.reverse()
        
        return " ".join(translated_words)

    def close(self):
        self.conn.close()

# --- 実行テスト ---
if __name__ == "__main__":
    # サンプルコーパス（英語）
    english_data = "The quick brown fox jumps over the lazy dog. Artificial intelligence creates new worlds."
    
    translator = LanguageTranslator()
    translator.train_generator_from_file("genesis.txt")
    
    input_text = "私は犬が好きです"
    result = translator.translate_sentence(input_text)
    
    print(f"入力: {input_text}")
    print(f"翻訳: {result}")
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
    
    input_text = [
    "日本国民は、正当に選挙された国会における代表者を通じて行動し、われらとわれらの子孫のために、諸国民との協和による成果と、わが国全土にわたつて自由のもたらす恵沢を確保し、政府の行為によつて再び戦争の惨禍が起ることのないやうにすることを決意し、ここに主権が国民に存することを宣言し、この憲法を確定する。",
    "そもそも国政は、国民の厳粛な信託によるものであつて、その権威は国民に由来し、その権力は国民の代表者がこれを行使し、その福利は国民がこれを享受する。",
    "これは人類普遍の原理であり、この憲法は、かかる原理に基くものである。",
    "われらは、これに反する一切の憲法、法令及び詔勅を排除する。"
    "日本国民は、恒久の平和を念願し、人間相互の関係を支配する崇高な理想を深く自覚するのであつて、平和を愛する諸国民の公正と信義に信頼して、われらの安全と生存を保持しようと決意した。",
    "われらは、平和を維持し、専制と隷従、圧迫と偏狭を地上から永遠に除去しようと努めてゐる国際社会において、名誉ある地位を占めたいと思ふ。",
    "われらは、全世界の国民が、ひとしく恐怖と欠乏から免かれ、平和のうちに生存する権利を有することを確認する。",
    "われらは、いづれの国家も、自国のことのみに専念して他国を無視してはならないのであつて、政治道徳の法則は、普遍的なものであり、この法則に従ふことは、自国の主権を維持し、他国と対等関係に立たうとする各国の責務であると信ずる。",
    "日本国民は、国家の名誉にかけ、全力をあげてこの崇高な理想と目的を達成することを誓ふ。"]

    for s in input_text:
        result = translator.translate_sentence(s)
        print(s)
        print(result)


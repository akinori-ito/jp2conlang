# jp2conlang 🌌

`jp2conlang` は、日本語の文章を形態素解析し、統計的学習（n-gram）に基づいた独自の人工言語（Conlang）へ翻訳する実験的なプログラムです。

## ✨ 特徴

- **統計的語彙生成**: 既存の言語（英語など）の綴りパターン（Grapheme n-gram）を学習し、その言語に近い「響き」を持つ新しい単語を生成します。
- **永続的辞書**: 翻訳された単語は SQLite データベースに保存されるため、一度生成された単語は次回以降も固定の翻訳語として利用可能です。
- **動的単語長**: 日本語の元の単語長に比例した長さの目的言語単語を生成します。
- **文法反転**: 日本語の語順を単純に逆転させることで、異世界情緒のある独特な構文を作り出します。

## 🛠 アルゴリズムの仕組み

1. **学習**: ソースとなる言語テキストから文字の出現確率（3-gram）を計算します。
2. **解析**: `Janome` を使用して日本語を形態素（単語）単位に分割します。
3. **変換**:
   - 既にデータベース（`lang_dict.db`）にある単語は、その値を採用します。
   - 未知の単語は、元の日本語の長さに応じた単語をサンプリング生成し、データベースに新規登録します。
4. **再構成**: 単語リストを逆順に並び替え、スペース区切りで出力します。



## 🚀 セットアップ

### 必要条件
- Python 3.7+
- Janome (形態素解析エンジン)

### インストール
```bash
git clone https://github.com/akinori-ito/jp2conlang.git
cd jp2conlang
pip install janome
```

## 変換例
```
日本国民は、正義と秩序を基調とする国際平和を誠実に希求し、国権の発動たる戦争と、武力による威嚇又は武力の行使は、国際紛争を解決する手段としては、永久にこれを放棄する。
gi bechshal cheredne, hi rahourse fo sonedede ot mayseh bromethe then ga andredis ot anderead ga moneye, ga donotham chis downeyse pi andreast, gi hathas pi andephte bandri afteda fromed andephte, gi thande aredentr then fiesseve ot troyseet bromethe, then restit ot cobs fo fromptilpa.
```

Powered by [Gemini](https://gemini.google.com)

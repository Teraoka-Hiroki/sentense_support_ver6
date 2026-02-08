from flask import Flask, render_template, request, jsonify, send_file
from logic import LogicHandler
import io
import os
import json

app = Flask(__name__)

SETTINGS_FILE = "settings.json"

def load_settings():
    """設定ファイルからデータを読み込む"""
    default_data = {
        "gemini_key": "",
        "amplify_token": "",
        "topic_main": "",
        "topic_sub1": "",
        "topic_sub2": "",
        "params": {
            # Scene Craft
            "p_desc_style": 0.5,
            "p_perspective": 0.5,
            "p_sensory": 0.5,
            "p_thought": 0.5,
            "p_tension": 0.5,
            "p_reality": 0.5,
            # Character Dynamics
            "p_char_count": 0.2, # 1 person approx
            "p_char_mental": 0.5,
            "p_char_belief": 0.5,
            "p_char_trauma": 0.0,
            "p_char_voice": 0.5,
            # Output
            "length": 500
        },
        "candidates": [],
        "draft_summary": "",
        "draft_article": "",
        "additional_instruction": "",
        "final_text": "",
        "bbo_history": [] # Format: [{"attributes": dict, "rating": int}, ...]
    }
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # マージ
                for k, v in default_data.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_data
    return default_data

def save_settings(data):
    """設定ファイルへデータを保存する"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")

DATA_STORE = load_settings()

@app.route('/')
def index():
    global DATA_STORE
    DATA_STORE = load_settings()
    return render_template('index.html', state=DATA_STORE)

@app.route('/api/generate_candidates', methods=['POST'])
def generate_candidates():
    global DATA_STORE
    req = request.json
    
    DATA_STORE.update({
        'gemini_key': req.get('gemini_key'),
        'amplify_token': req.get('amplify_token'),
        'topic_main': req.get('topic_main'),
        'topic_sub1': req.get('topic_sub1'),
        'topic_sub2': req.get('topic_sub2'),
        'params': req.get('params'),
        'bbo_history': [] # Reset history on new generation
    })
    save_settings(DATA_STORE)
    
    try:
        candidates = LogicHandler.generate_candidates_api(
            DATA_STORE['gemini_key'],
            DATA_STORE['topic_main'],
            DATA_STORE['topic_sub1'],
            DATA_STORE['topic_sub2'],
            DATA_STORE['params']
        )
        DATA_STORE['candidates'] = [c.to_dict() for c in candidates]
        save_settings(DATA_STORE)
        return jsonify({"status": "success", "candidates": DATA_STORE['candidates']})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/update_rating', methods=['POST'])
def update_rating():
    """個別のユーザー評価を一時保存"""
    global DATA_STORE
    req = request.json
    item_id = req.get('id')
    rating = req.get('rating')
    
    for c in DATA_STORE['candidates']:
        if c['id'] == item_id:
            c['user_rating'] = int(rating)
            break
    save_settings(DATA_STORE)
    return jsonify({"status": "success"})

@app.route('/api/optimize', methods=['POST'])
def optimize():
    """パラメータのみに基づく静的な最適化（コールドスタート）"""
    global DATA_STORE
    req = request.json
    
    if req.get('amplify_token'):
        DATA_STORE['amplify_token'] = req.get('amplify_token')
    if req.get('params'):
        DATA_STORE['params'] = req.get('params')
        
    save_settings(DATA_STORE)

    try:
        updated_candidates = LogicHandler.run_optimization(
            DATA_STORE['amplify_token'],
            DATA_STORE['candidates'],
            DATA_STORE['params']
        )
        DATA_STORE['candidates'] = updated_candidates
        save_settings(DATA_STORE)
        return jsonify({"status": "success", "candidates": DATA_STORE['candidates']})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- BBO Endpoints ---

@app.route('/api/bbo_step', methods=['POST'])
def bbo_step():
    """リッジ回帰 + 量子アニーリングによる最適化"""
    global DATA_STORE
    req = request.json
    
    if req.get('amplify_token'):
        DATA_STORE['amplify_token'] = req.get('amplify_token')
    if req.get('params'):
        DATA_STORE['params'] = req.get('params')
        
    save_settings(DATA_STORE)
    
    # 1. 現在の候補の中で、ユーザーが評価(1-5)を付けたものを履歴に追加
    # (未評価=0の場合は学習データに含めない、または3(中立)として扱う設計もありだが、今回は評価済みのみ)
    new_data_count = 0
    for c in DATA_STORE['candidates']:
        if c.get('user_rating', 0) > 0:
            # 属性ベクトル作成用データと評価を保存
            record = {
                "attributes": c.get('attributes', {}),
                "type": c.get('type'),
                "relevance": c.get('relevance', 0.5),
                "rating": c['user_rating']
            }
            # 重複回避は簡易的にチェックしない（同じIDでも評価が変わる可能性があるため追記していく）
            DATA_STORE['bbo_history'].append(record)
            new_data_count += 1
    
    try:
        # 学習と最適化の実行
        updated_candidates = LogicHandler.run_bbo_optimization(
            DATA_STORE['amplify_token'],
            DATA_STORE['candidates'],
            DATA_STORE['bbo_history'],
            DATA_STORE['params']
        )
        
        DATA_STORE['candidates'] = updated_candidates
        save_settings(DATA_STORE)
        
        return jsonify({
            "status": "success", 
            "candidates": DATA_STORE['candidates'],
            "history_count": len(DATA_STORE['bbo_history'])
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/bbo_reset', methods=['POST'])
def bbo_reset():
    global DATA_STORE
    DATA_STORE['bbo_history'] = []
    # ユーザー評価もリセット
    for c in DATA_STORE['candidates']:
        c['user_rating'] = 0
    save_settings(DATA_STORE)
    return jsonify({"status": "success"})

# ---------------------

@app.route('/api/generate_draft', methods=['POST'])
def generate_draft():
    global DATA_STORE
    # Amplifyで選ばれたもの(selected=True)を使用
    selected = [c for c in DATA_STORE['candidates'] if c.get('selected')]
    
    if not selected:
        return jsonify({"status": "error", "message": "最適化された要素がありません。Tab 2で最適化を実行してください。"}), 400

    try:
        summary, article = LogicHandler.generate_draft(
            DATA_STORE['gemini_key'],
            selected,
            DATA_STORE['params']
        )
        DATA_STORE['draft_summary'] = summary
        DATA_STORE['draft_article'] = article
        save_settings(DATA_STORE)
        return jsonify({"status": "success", "summary": summary, "article": article})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/save_draft_edit', methods=['POST'])
def save_draft_edit():
    global DATA_STORE
    DATA_STORE['draft_article'] = request.json.get('article')
    DATA_STORE['additional_instruction'] = request.json.get('instruction')
    save_settings(DATA_STORE)
    return jsonify({"status": "success"})

@app.route('/api/generate_final', methods=['POST'])
def generate_final():
    global DATA_STORE
    try:
        final_text = LogicHandler.generate_final(
            DATA_STORE['gemini_key'],
            DATA_STORE['draft_article'],
            DATA_STORE['additional_instruction']
        )
        DATA_STORE['final_text'] = final_text
        save_settings(DATA_STORE)
        return jsonify({"status": "success", "final_text": final_text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download')
def download_file():
    global DATA_STORE
    mem = io.BytesIO()
    text = DATA_STORE.get('final_text', '')
    mem.write(text.encode('utf-8'))
    mem.seek(0)
    return send_file(
        mem,
        as_attachment=True,
        download_name='novel_scene.txt',
        mimetype='text/plain'
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)

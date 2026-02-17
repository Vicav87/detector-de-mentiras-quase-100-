from flask import Flask, request, jsonify, send_from_directory
import spacy
import numpy as np
from transformers import pipeline
from scipy.spatial.distance import euclidean

# Configura o Flask para ler tudo na pasta principal
app = Flask(__name__, template_folder='.', static_folder='.')

# Carrega o modelo de português
try:
    nlp = spacy.load("pt_core_news_sm")
except:
    import os
    os.system("python -m spacy download pt_core_news_sm")
    nlp = spacy.load("pt_core_news_sm")

# Modelo de análise emocional (Multilíngue)
emotion_classifier = pipeline(
    "text-classification", 
    model="micromodels/bert-base-portuguese-cased-emotion", 
    top_k=None
)

@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def style():
    return send_from_directory('.', 'style.css')

@app.route("/analisar", methods=["POST"])
def analisar():
    try:
        data = request.get_json()
        texto = data.get("texto", "")

        if not texto or len(texto) < 10:
            return jsonify({
                "incerteza": 0, "complexidade": "Curto", 
                "consistencia": "N/A", "observacao": "Texto muito curto para análise."
            })

        doc = nlp(texto)
        frases = [sent.text for sent in doc.sents if len(sent.text) > 3]

        if len(frases) < 2:
            return jsonify({
                "incerteza": 0, "complexidade": "Simples", 
                "consistencia": "Estável", "observacao": "Adicione mais frases para medir a variação."
            })

        # IA: Processando emoções
        resultados = emotion_classifier(frases)
        vetores = []
        for res in resultados:
            res_ordenado = sorted(res, key=lambda x: x['label'])
            vetores.append([emo["score"] for emo in res_ordenado])

        # Cálculo de variação emocional
        variacoes = [euclidean(vetores[i], vetores[i+1]) for i in range(len(vetores)-1)]
        media_oscilacao = np.mean(variacoes)

        return jsonify({
            "incerteza": round(media_oscilacao * 100, 1),
            "complexidade": "Alta" if len(texto)/len(frases) > 25 else "Média",
            "consistencia": "Alta" if media_oscilacao < 0.2 else "Baixa",
            "observacao": "Análise concluída com sucesso baseada em redes neurais."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
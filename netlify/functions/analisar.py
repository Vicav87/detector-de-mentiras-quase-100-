import json
import spacy

# Carrega o modelo de português
try:
    nlp = spacy.load("pt_core_news_sm")
except:
    nlp = None

def handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }

    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers}

    try:
        body = json.loads(event['body'])
        texto = body.get("texto", "")

        # --- LÓGICA DE PSICOLOGIA FORENSE ---
        # Analisando distanciamento e hesitação
        palavras = texto.lower().split()
        eu_referencia = sum(1 for p in palavras if p in ['eu', 'meu', 'minha', 'nós'])
        incerteza = sum(1 for p in palavras if p in ['acho', 'talvez', 'não sei', 'quase'])
        
        score = 0
        if eu_referencia < 1: score += 40  # Mentirosos se distanciam da história
        if incerteza > 2: score += 30     # Mentirosos hesitam mais

        veredito = "Baixa probabilidade de mentira" if score < 50 else "Alta probabilidade de mentira"

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                "incerteza": score,
                "complexidade": "Vaga" if score > 50 else "Detalhada",
                "consistencia": veredito,
                "observacao": "Análise psicológica concluída."
            })
        }
    except Exception as e:
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({"error": str(e)})}
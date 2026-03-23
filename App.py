"""
AVORUBY CASH — Application Flask
=================================
COMMENT LANCER :
1. Installer Flask : pip install flask
2. Lancer : python app.py
3. Ouvrir navigateur : http://localhost:5000

DONNÉES MOCKÉES :
- Chercher le commentaire "# ===== DONNÉES MOCKÉES =====" dans ce fichier
- Remplacer les valeurs par les vraies prédictions du modèle quand prêt
"""

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ============================================================
# ===== DONNÉES MOCKÉES — À REMPLACER APRÈS MODÉLISATION =====
# ============================================================
# Ces valeurs simulent les résultats du modèle LSTM + XGBoost
# Quand le modèle sera prêt, remplacer cette fonction par :
# from model import predict_sabc
# et appeler predict_sabc(data) dans la route /predict

def mock_predict(data):
    """
    FONCTION MOCKÉE — Simule le calcul SABC
    À REMPLACER par le vrai modèle après 04_modelisation.ipynb
    
    Input : dict avec les données agriculteur
    Output : dict avec scores et décision crédit
    """
    # Calcul Gamma (résilience) — RÉEL, basé sur la formule du projet
    gamma = (
        data["irrigation"] * 0.25 +
        data["solaire"] * 0.15 +
        (0.20 if data["iot"] > 0 else 0) +
        data["filets"] * 0.40
    )

    # ===== VALEURS CI-DESSOUS = MOCKÉES =====
    # Prix MAD/kg simulé selon culture
    # REMPLACER par : prix_predit = lstm_model.predict(flux_marche)
    prix_mock = {
        "Avocat": 26.5,         # MAD/kg — MOCKÉ
        "Fruits_Rouges": 62.0   # MAD/kg — MOCKÉ
    }

    # Rendement simulé selon culture et surface
    # REMPLACER par : rendement = xgb_model.predict(flux_resilience)
    rendement_mock = {
        "Avocat": 8500,         # kg/ha — MOCKÉ
        "Fruits_Rouges": 12000  # kg/ha — MOCKÉ
    }

    culture = data["culture"]
    hectares = data["hectares"]
    prix = prix_mock.get(culture, 30.0)
    rendement = rendement_mock.get(culture, 10000)

    # Production prédite
    production = rendement * hectares  # kg

    # Risque brut simulé — MOCKÉ
    # REMPLACER par : risque = ct_model.predict(flux_environnement)
    risque_brut = 1.2  # MOCKÉ — sera calculé via Ct et Ht

    # Volatilité simulée — MOCKÉE
    # REMPLACER par : volatilite = flux_marche["avocat_volatilite"].iloc[-1]
    volatilite_mock = {
        "Avocat": 1.8,          # MAD/kg std — MOCKÉ
        "Fruits_Rouges": 3.2    # MAD/kg std — MOCKÉ
    }
    volatilite = volatilite_mock.get(culture, 2.0)

    # Formule SABC = σ(Production × Prix / Risque × (1 − Γ))
    numerateur = production * prix
    denominateur = risque_brut * (1 - gamma + 0.01)  # +0.01 évite division par 0
    sabc_raw = numerateur / denominateur
    sabc = round(min(sabc_raw / 100000, 100), 1)  # Normalisé 0-100

    # Décision crédit
    if sabc >= 70:
        decision = "APPROUVÉ"
        couleur = "approved"
        message = "Profil agricole solide. Crédit recommandé."
    elif sabc >= 45:
        decision = "CONDITIONNEL"
        couleur = "conditional"
        message = "Profil acceptable. Garanties supplémentaires recommandées."
    else:
        decision = "REFUSÉ"
        couleur = "refused"
        message = "Risque élevé détecté. Améliorer les équipements."

    return {
        "sabc": sabc,
        "gamma": round(gamma, 2),
        "production": int(production),
        "prix_kg": prix,
        "volatilite": volatilite,
        "decision": decision,
        "couleur": couleur,
        "message": message,
        "is_mock": True  # SUPPRIMER quand le vrai modèle est intégré
    }
# ============================================================
# ===== FIN DONNÉES MOCKÉES ==================================
# ============================================================


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/formulaire")
def formulaire():
    return render_template("formulaire.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    result = mock_predict(data)
    return jsonify(result)

@app.route("/resultat")
def resultat():
    return render_template("resultat.html")


if __name__ == "__main__":
    # DEBUG=True → recharge automatiquement à chaque modification du code
    app.run(debug=True, port=5000)
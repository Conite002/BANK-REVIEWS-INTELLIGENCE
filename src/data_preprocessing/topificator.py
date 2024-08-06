import requests
import pandas as pd
import time


class TopicExtractor:
    def __init__(self, model="llama3.1", patience=3, url='http://localhost:11434/api/generate'):
        self.headers = {"Content-Type": "application/json"}
        self.url = url
        self.model = model
        self.max_try = patience
        self.topics = [
            "Service client",
            "Produits financiers",
            "Expérience utilisateur",
            "Gestion des comptes",
            "Sécurité",
            "Localisation et accessibilité",
            "Services additionnels",
            "Temps d'attente",
            "Facilité d'ouverture de compte",
            "Application mobile",
            "Site internet",
            "Frais bancaires",
            "Transparence des informations",
            "Compétence du personnel",
            "Offres promotionnelles",
            "Satisfaction client",
            "Feedback client",
            "Qualité des services",
            "Programmes d'éducation financière",
            "Atmosphère de la branche",
            "Services hors heures",
            "Services week-end",
            "Service client 24/7",
            "Système de réclamations",
            "Solutions de recouvrement",
            "Services multilingues",
            "Options de financement",
            "Prêts automobile",
            "Prêts étudiant",
            "Prêts commerciaux",
            "Prêts personnels sans garantie",
            "Prêts personnels avec garantie",
            "Refinancement de prêt",
            "Gestion des crises",
            "Transferts automatiques",
            "Opérations de change",
            "Programmes de parrainage",
            "Notifications de solde",
            "Historique des transactions",
            "Analyse des dépenses",
            "Paramètres de sécurité",
            "Compatibilité des technologies",
            "Expérience omnicanal",
            "Services VIP",
            "Gestion des investissements",
            "Assurance vie",
            "Assurance habitation",
            "Assurance automobile",
            "Assurance santé",
            "Plans d'épargne",
            "Conseils financiers",
            "Planification de retraite",
            "Comptes épargne jeunesse",
            "Comptes épargne entreprise",
            "Comptes épargne individuelle",
            "Cartes de crédit",
            "Cartes de débit",
            "Cartes prépayées",
            "Cartes de crédit premium",
            "Cartes de crédit entreprise",
            "Frais de carte de crédit",
            "Taux d'intérêt",
            "Taux d'intérêt variables",
            "Taux d'intérêt fixes",
            "Promotions sur les prêts",
            "Avantages pour les nouveaux clients",
            "Programme de fidélité",
            "Réductions pour étudiants",
            "Services de dépôt à distance",
            "Services de retrait sans carte",
            "Bornes de service rapide",
            "Assistance en ligne",
            "Chatbot",
            "Assistance téléphonique",
            "Service de rappel",
            "Suivi des demandes",
            "Conseils de gestion de patrimoine",
            "Gestion des dettes",
            "Planification successorale",
            "Services de notarisation",
            "Services juridiques",
            "Comptes courants",
            "Comptes joint",
            "Comptes de dépôt",
            "Comptes de transaction",
            "Comptes de chèques",
            "Comptes professionnels",
            "Services d'audit",
            "Services de conformité",
            "Sécurité des transactions en ligne",
            "Authentification à deux facteurs",
            "Notifications en temps réel",
            "Limites de retrait",
            "Détection de fraude",
            "Service d'envoi d'argent",
            "Portefeuilles électroniques",
            "Banques en ligne uniquement",
            "Paiements sans contact",
            "Paiements mobiles",
            "Virements bancaires"
        ]


        self.part_prompt = f"""
            Vous êtes un analyste de texte et un chercheur expertchargé d'analyser les avis clients de différentes banques. Votre tâche consiste à extraire les topics abordés dans chaque avis. Les topics extraites doivent etre etroitement liees aux nombres de start obtenus. Un topic peut être une caractéristique spécifique de la banque, un service, une expérience client, ou tout autre aspect pertinent mentionné dans l'avis.

            Veuillez lire attentivement chaque avis et identifier les topics presents. Voici la liste des topics a considerée {self.topics}. Fournissez un  JSON  pour chaque avis, en utilisant des mots ou des phrases courtes. Assurez-vous que les topics , sentiments et sub_topics sont spécifiques et pertinents.

            Exemples :

            Avis Client : "Le service clientèle de cette banque est très réactif. J'ai eu un problème avec ma carte bancaire et ils l'ont résolu en moins de 24 heures. Très satisfait de leur rapidité !"
            response :
            ('[Service client]', 'Positive', [Service clientèle réactif, Résolution rapide de problèmes])

            Avis Client : "Les frais bancaires sont trop élevés comparés à d'autres banques. De plus, l'application mobile est souvent lente et peu intuitive."
            response :
            ([plateforme mobile], 'Negative', [ Application mobile lente, Application mobile peu intuitive])
         Votre tâche :
            Lisez chaque avis et extrayez les topics, sub-topics et sentiments de manière similaire aux exemples ci-dessus.
            Donne juste la sortie JSON. Pas de commentaire supplementaire.   """
        self.format1 = """
        
            Voici une exemple de sortie:
            {
                "topics": [
                ("ouverture de compte", "Positive", ["rapide", "simple"]),
                
                ]
            }
            Si le review est NAN, Sortie: {'topics': []}. Pour le review donne la sortie conrespondant a son analyse """

        #Utilise seulement ces topics . Pas d'autres. """ + str(self.topics)

    def _send_request(self, prompt):
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(self.url, json=data, headers=self.headers)
        if response.status_code == 200:
            response_data = response.json()
            #print(response_data['response'])
            return response_data.get('response', 'No response field found')
        else:
            raise Exception(f"Failed to retrieve data, status code {response.status_code}")
    
    def extract(self, reviews, stars, type='SINGLE_SOURCE'):
        #print("REVIEW: ", reviews)
        if reviews == "NAN":
            return {'topics': []}
        else:
            tries = 0
            while tries < self.max_try:
                try:
                    if type == 'SINGLE_SOURCE':
                        if isinstance(reviews, str):
                            prompt = f"{self.part_prompt}  .Extraire les topics de cette revue '{reviews}'.  Les topics doivent etre etroitement liees aux nombres de start : {stars} obtenus. et donne la sortie au **format JSON** suiavnt: " + self.format1
                            response = self._send_request(prompt)
                            return self._parse_single_response(response)
                        else:
                            raise AssertionError("For SINGLE_SOURCE, reviews should be a single string.")
                    else:
                        raise AssertionError("type arg should either be 'SINGLE_SOURCE' or 'MULTI_SOURCE'")
                except Exception as e:
                    print(f"Attempt {tries + 1} failed with error: {e}")
                    tries += 1
                    time.sleep(2)
            return f"Failed to extract topics after {self.max_try} attempts"
        
    @staticmethod
    def _safejson(response):
        first_brace = response.find('{')
        last_brace = response.rfind('}')
        if last_brace == -1:
            response += "}"
        last_brace = response.rfind('}')
        if first_brace == -1 or last_brace == -1:
            raise ValueError("No JSON object could be identified in the response")
        return response[first_brace:last_brace + 1]
        
    def _parse_single_response(self, response):
        try:
            response = self._safejson(response)
            parsed_response = eval(response)
            formatted_response = {
                "topics": parsed_response.get("topics", []),
            }
            return formatted_response
        except Exception as e:
            raise Exception(f"Failed to parse response: {e}")

    @staticmethod
    def _flatten_topics(topics):
        flat_data = []
        for topic in topics.get('topics', []):
            flat_data.append({
                "topic": topic[0],
                "sentiment": topic[1],
                "subtopics": topic[2]
            })
        return flat_data
    
    def to_dataframe(self, topics):
        flat_data = self._flatten_topics(topics)
        return pd.DataFrame(flat_data)
    


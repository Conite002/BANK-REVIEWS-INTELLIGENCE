import requests
import pandas as pd
import time


class TopicExtractor:
    def __init__(self, model="llama3.1", patience=3, url='http://ollama:11434/api/generate'):
        self.headers = {"Content-Type": "application/json"}
        self.url = url
        self.model = model
        self.max_try = patience
        self.topics = [
            "service_client",
            "produits_financiers",
            "expérience_utilisateur",
            "gestion_des_comptes",
            "sécurité",
            "localisation_accessibilité",
            "services_additionnels",
            "temps_d_attente",
            "facilité_d_ouverture_de_compte",
            "application_mobile",
            "site_internet",
            "frais_bancaires",
            "transparence_des_informations",
            "compétence_du_personnel",
            "qualité_de_l_accueil",
            "prêts_personnels",
            "prêts_hypothécaires",
            "cartes_de_crédit",
            "cartes_de_débit",
            "conseils_financiers",
            "suivi_des_transactions",
            "alertes_et_notifications",
            "retraits_d_argent",
            "dépôts_d_argent",
            "virements_bancaires",
            "épargne",
            "taux_d_intérêt",
            "programmes_de_récompense",
            "gestion_de_budget",
            "planification_financière",
            "accès_aux_guichets_automatiques",
            "accessibilité_pour_les_personnes_handicapées",
            "services_aux_entreprises",
            "services_aux_particuliers",
            "service_client_téléphonique",
            "service_client_en_personne",
            "support_via_email",
            "support_via_chat",
            "rapidité_de_réponse",
            "efficacité_des_résolutions",
            "disponibilité_des_services",
            "services_internationaux",
            "change_de_devise",
            "services_d_investissement",
            "gestion_de_portefeuille",
            "retraite",
            "assurances",
            "garanties_bancaires",
            "partenariats",
            "événements_clients",
            "transferts_d_argent_internationaux",
            "options_de_paiement",
            "méthodes_de_paiement",
            "protection_contre_la_fraude",
            "confidentialité_des_données",
            "services_personnalisés",
            "programmes_de_fidélité",
            "comptes_de_dépôt",
            "comptes_corrents",
            "comptes_d_épargne",
            "comptes_jeunes",
            "comptes_professionnels",
            "comptes_joints",
            "services_en_ligne",
            "services_par_telephone",
            "consultations_financières",
            "rapports_de_crédit",
            "solvabilité",
            "gestion_des_dettes",
            "services_pour_les_étudiants",
            "comptes_pour_les_étudiants",
            "produits_de_placement",
            "offres_promotionnelles",
            "satisfaction_client",
            "feedback_client",
            "qualité_des_services",
            "programmes_d_éducation_financière",
            "atmosphère_de_la_branche",
            "services_hors_heures",
            "services_week-end",
            "service_client_24/7",
            "système_de_réclamations",
            "solutions_de_recouvrement",
            "services_multilingues",
            "options_de_financement",
            "prêts_automobile",
            "prêts_étudiant",
            "prêts_commerciaux",
            "prêts_personnels_sans_garantie",
            "prêts_personnels_avec_garantie",
            "refinancement_de_prêt",
            "gestion_des_crises",
            "transferts_automatiques",
            "opérations_de_change",
            "programmes_de_parrainage",
            "notifications_de_solde",
            "historique_des_transactions",
            "analyse_des_dépenses",
            "paramètres_de_sécurité",
            "compatibilité_des_technologies",
            "expérience_omnicanal"
        ]

        self.part_prompt = """
            Vous êtes un analyste de texte et un chercheur expertchargé d'analyser les avis clients de différentes banques. Votre tâche consiste à extraire les sujets principaux abordés dans chaque avis. Un sujet peut être une caractéristique spécifique de la banque, un service, une expérience client, ou tout autre aspect pertinent mentionné dans l'avis.

            Veuillez lire attentivement chaque avis et identifier les sujets principaux. Fournissez une liste de sujets pour chaque avis, en utilisant des mots ou des phrases courtes. Assurez-vous que les sujets sont spécifiques et pertinents.

            Exemples :

            Avis Client : "Le service clientèle de cette banque est très réactif. J'ai eu un problème avec ma carte bancaire et ils l'ont résolu en moins de 24 heures. Très satisfait de leur rapidité !"
            Sujets Extraits :

            ('Positive', [Service clientèle réactif, Résolution rapide de problèmes, Problème de carte bancaire])
            Avis Client : "Les frais bancaires sont trop élevés comparés à d'autres banques. De plus, l'application mobile est souvent lente et peu intuitive."
            Sujets Extraits :

            ('Negative', [ Frais bancaires élevés, Application mobile lente, Application mobile peu intuitive ])
            Avis Client : "J'apprécie les options de gestion de compte en ligne. Les fonctionnalités sont très complètes et faciles à utiliser. Cependant, le temps d'attente au guichet est souvent trop long."
            Sujets Extraits :

            ('Positive', [ Options de gestion de compte en ligne, Fonctionnalités complètes, Fonctionnalités faciles à utiliser, Temps d'attente au guichet long ])
            Votre tâche :
            Lisez chaque avis et extrayez les sujets principaux de manière similaire aux exemples ci-dessus.
            Donne juste la sortie JSON. Pas de commentaire supplementaire.   """
        self.format1 = """
        
            Voici une exemple de sortie:
            {
                "topics": [
                ("ouverture de compte", "Positive", ["rapide", "simple"]),
                ("Service client", "Negative", ["arrogant", "lent"]),
                ("Recommandation", "Neutre", []),
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
    
    def extract(self, reviews, type='SINGLE_SOURCE'):
        #print("REVIEW: ", reviews)
        if reviews == "NAN":
            return {'topics': []}
        else:
            tries = 0
            while tries < self.max_try:
                try:
                    if type == 'SINGLE_SOURCE':
                        if isinstance(reviews, str):
                            prompt = f"{self.part_prompt}  .Extraire les topics de cette revue '{reviews}'. et donne la sortie au **format JSON** suiavnt: " + self.format1
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
    


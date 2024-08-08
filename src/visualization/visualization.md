# Visualisations des Avis Bancaires

Ce document décrit les différentes visualisations créées à partir de la base de données décisionnelle des avis bancaires. Chaque visualisation fournit des insights spécifiques pour analyser les avis des utilisateurs sur les banques.

## 1. Distribution des Notes des Avis
- **Type**: Histogramme
- **Description**: Affiche la distribution des notes (étoiles) attribuées aux banques par les utilisateurs. Permet de visualiser la répartition des notes et d'identifier les tendances globales dans les évaluations.
```
SELECT count_review AS rating, COUNT(*) AS count
FROM fact_reviews
GROUP BY count_review
ORDER BY count_review;
```
## 2. Répartition des Avis par Banque
- **Type**: Diagramme à barres ou à colonnes
- **Description**: Montre le nombre total d'avis pour chaque banque. Cette visualisation aide à comprendre quelles banques reçoivent le plus grand nombre d'avis.
```
SELECT b.bank_name, COUNT(fr.review_id) AS total_reviews
FROM fact_reviews fr
JOIN dimension_bank b ON fr.bank_id = b.id
GROUP BY b.bank_name
ORDER BY total_reviews DESC;
```

## 3. Répartition des Avis par Ville
- **Type**: Carte géographique ou diagramme à barres
- **Description**: Affiche le nombre d'avis par ville pour visualiser les régions les plus actives. Une carte géographique permet de voir la concentration des avis sur une carte, tandis qu'un diagramme à barres montre les données de manière plus condensée.
```
SELECT t.town_name, COUNT(fr.review_id) AS total_reviews
FROM fact_reviews fr
JOIN dimension_bank b ON fr.bank_id = b.id
JOIN dimension_town t ON b.town_id = t.id
GROUP BY t.town_name
ORDER BY total_reviews DESC;
```

## 4. Évolution des Avis dans le Temps
- **Type**: Graphique en courbes
- **Description**: Visualise comment le nombre d'avis a changé au fil du temps (semaine, mois, année). Cette visualisation aide à identifier les tendances saisonnières ou les changements dans le volume des avis.
```
SELECT dt.year, dt.month, COUNT(fr.review_id) AS total_reviews
FROM fact_reviews fr
JOIN dimension_time dt ON fr.time_week = dt.week
GROUP BY dt.year, dt.month
ORDER BY dt.year, dt.month;
```

## 5. Analyse des Sentiments
- **Type**: Diagramme en secteurs (camembert) ou histogramme
- **Description**: Montre la répartition des sentiments (positifs, négatifs, neutres) dans les avis. Permet d'analyser la tonalité globale des avis.
```SELECT ds.sentiment_name, COUNT(fr.review_id) AS total_reviews
FROM fact_reviews fr
JOIN dimension_sentiment ds ON fr.sentiment_id = ds.id
GROUP BY ds.sentiment_name;
```

## 6. Fréquence des Réactions des Propriétaires
- **Type**: Diagramme à barres ou à colonnes
- **Description**: Affiche le nombre de réponses des propriétaires par banque ou par ville. Cette visualisation aide à comprendre l'engagement des propriétaires avec les avis.
```
SELECT b.bank_name, COUNT(fr.review_id) AS total_replies
FROM fact_reviews fr
JOIN dimension_bank b ON fr.bank_id = b.id
WHERE fr.count_review IS NOT NULL
GROUP BY b.bank_name
ORDER BY total_replies DESC;
```

## 7. Avis par Sujet
- **Type**: Nuage de mots ou diagramme à barres
- **Description**: Montre les sujets les plus fréquents dans les avis (par exemple, la qualité du service, les frais, etc.). Un nuage de mots met en avant les mots les plus souvent utilisés, tandis qu'un diagramme à barres quantifie leur fréquence.
```
SELECT dt.topic_name, COUNT(fr.review_id) AS total_reviews
FROM fact_reviews fr
JOIN dimension_topic dt ON fr.topic_id = dt.id_topic
GROUP BY dt.topic_name
ORDER BY total_reviews DESC;
```

## 8. Répartition des Avis par Type de Banque
- **Type**: Diagramme en secteurs ou histogramme
- **Description**: Affiche la proportion des avis pour différents types de banques (privées, publiques, coopératives, etc.). Permet de voir la répartition des avis en fonction du type de banque.
```
SELECT b.bank_type, COUNT(fr.review_id) AS total_reviews
FROM fact_reviews fr
JOIN dimension_bank b ON fr.bank_id = b.id
GROUP BY b.bank_type;
```

## 9. Analyse de la Répartition des Avis en Fonction du Temps
- **Type**: Graphique en heatmap
- **Description**: Visualise les périodes avec une densité élevée ou faible d'avis. Une heatmap montre les variations dans le nombre d'avis au fil du temps.
```
SELECT dt.year, dt.month, COUNT(fr.review_id) AS total_reviews
FROM fact_reviews fr
JOIN dimension_time dt ON fr.time_week = dt.week
GROUP BY dt.year, dt.month
ORDER BY dt.year, dt.month;
```


## 10. Comparaison des Notes entre Banques
- **Type**: Boxplot ou diagramme à barres
- **Description**: Compare la distribution des notes entre différentes banques. Cette visualisation permet de comparer les performances des banques en termes de notes attribuées.
```
SELECT b.bank_name, AVG(fr.count_review) AS avg_rating
FROM fact_reviews fr
JOIN dimension_bank b ON fr.bank_id = b.id
GROUP BY b.bank_name
ORDER BY avg_rating DESC;
```

## 11. Avis des Utilisateurs Par Type de Compte
- **Type**: Diagramme à barres ou tableau croisé dynamique
- **Description**: Analyse les avis en fonction du type de compte bancaire (compte courant, compte épargne, etc.). Permet de voir si les avis diffèrent selon le type de produit bancaire.
```
SELECT dt.topic_name, COUNT(fr.review_id) AS total_reviews
FROM fact_reviews fr
JOIN dimension_topic dt ON fr.topic_id = dt.id_topic
GROUP BY dt.topic_name;
```

## 12. Performance des Banques selon les Critères
- **Type**: Tableau ou radar chart
- **Description**: Évalue les banques sur différents critères comme le service client, les frais, etc., en utilisant une échelle de notation. Cette visualisation aide à comparer les banques sur plusieurs aspects.
```
SELECT b.bank_name, AVG(fr.count_review) AS avg_rating
FROM fact_reviews fr
JOIN dimension_bank b ON fr.bank_id = b.id
GROUP BY b.bank_name
ORDER BY avg_rating DESC;
```
## 13. Tendances des Avis Positifs et Négatifs
- **Type**: Graphique en courbes
- **Description**: Montre les tendances des avis positifs et négatifs au fil du temps pour observer des changements dans les perceptions des utilisateurs. Permet d'analyser les fluctuations dans la satisfaction des clients.
```
SELECT dt.year, dt.month, 
       SUM(CASE WHEN ds.sentiment_name = 'Positive' THEN 1 ELSE 0 END) AS positive_reviews,
       SUM(CASE WHEN ds.sentiment_name = 'Negative' THEN 1 ELSE 0 END) AS negative_reviews
FROM fact_reviews fr
JOIN dimension_time dt ON fr.time_week = dt.week
JOIN dimension_sentiment ds ON fr.sentiment_id = ds.id
GROUP BY dt.year, dt.month
ORDER BY dt.year, dt.month;
```
## 14. Répartition des Avis par Groupe Démographique
- **Type**: Diagramme à barres ou à colonnes
- **Description**: Analyse les avis en fonction de groupes démographiques comme l'âge ou le sexe des utilisateurs, si ces données sont disponibles. Permet de comprendre comment différents groupes démographiques perçoivent les banques.
```
SELECT dr.reviewer_name, COUNT(fr.review_id) AS total_reviews
FROM fact_reviews fr
JOIN dimension_reviewer dr ON fr.reviewer_id = dr.id
GROUP BY dr.reviewer_name;
```
---

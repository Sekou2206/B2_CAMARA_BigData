# Note de sécurité

## Les données personnelles du projet

Toutes les données sont fictives (DummyJSON), mais on les traite comme si elles étaient réelles.

| Où | Données personnelles |
| --- | --- |
| Collection `raw_users` | nom, prénom, email, téléphone, date de naissance, adresse, adresse IP |
| Collection `raw_users` | mot de passe, IBAN, numéro de carte, numéro de sécurité sociale |
| Commandes | `user_id`, `username` et `cart_id` (qui est égal au `user_id` ici) |
| Paiements | `user_id`, montant payé, statut du paiement |

## Les risques

1. **Retrouver une personne** : avec `user_id` ou `username`, on peut relier un achat à un client précis.
2. **Fuite de données bancaires** : IBAN, carte et mot de passe dans les profils utilisateurs.
3. **Fuite de la clé** : si la clé HMAC est publiée, n'importe qui peut recalculer les pseudonymes et retrouver les clients.
4. **Identifiant caché dans une autre colonne** : dans nos données, `cart_id` et `order_id` contiennent le même numéro que `user_id`.
5. **Base ouverte** : MongoDB tourne en local sans mot de passe.

## Les mesures appliquées

1. **Pseudonymisation HMAC SHA 256** de `user_id` dans les commandes et les paiements, avec la même clé pour pouvoir relier les deux tables.
2. **Clé secrète hors du code** : elle est lue dans la variable d'environnement `PSEUDO_KEY`. Elle n'est jamais affichée, ni écrite dans le notebook, ni enregistrée dans les résultats ou sur GitHub.
3. **Suppression des identifiants directs** dans les fichiers Parquet : `user_id`, `username`, `cart_id`, `order_id` et `payment_id` sont retirés, et `cart_id` est lui aussi pseudonymisé.
4. **Profils réduits** : le script de collecte retire le mot de passe, l'IBAN, la carte et le portefeuille crypto dans `utilisateurs_reduits.csv`.
5. **Moins de données** : le dashboard ne lit que les fichiers Parquet pseudonymisés, jamais la base MongoDB.

## Les limites

La pseudonymisation n'est pas une anonymisation. Avec la clé on peut revenir en arrière, et les données pseudonymisées restent des données personnelles au sens du RGPD. Il faut donc toujours protéger les fichiers Parquet : accès limité, pas de partage public.

Dans un vrai projet, il faudrait aussi :
1. mettre un mot de passe sur MongoDB ;
2. ne jamais publier les fichiers bruts des utilisateurs (ici `TP1/data/raw/users.json` est sur GitHub seulement parce que les données sont fictives et déjà publiques sur DummyJSON) ;
3. garder la clé dans un coffre à secrets et la changer régulièrement.

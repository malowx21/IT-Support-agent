# Modification de l'adresse email

## Présentation

La modification de l'adresse email change l'identifiant principal du compte et la destination des notifications de sécurité. Elle est donc considérée comme une action sensible. L'agent peut expliquer la procédure et collecter les informations nécessaires, mais l'exécution doit être approuvée par un opérateur humain.

## Modification en libre-service

Un utilisateur connecté peut ouvrir les paramètres du compte, sélectionner « Profil », puis « Modifier l'adresse email ». Il doit saisir la nouvelle adresse et confirmer son mot de passe actuel. Un lien de vérification valable 30 minutes est envoyé à la nouvelle adresse.

La modification ne devient effective qu'après ouverture du lien de vérification. L'ancienne adresse reçoit ensuite une notification de sécurité. Si l'utilisateur n'est pas à l'origine de la demande, il doit contacter immédiatement le support et modifier son mot de passe.

## Vérifications du support

Avant toute intervention manuelle, le support doit vérifier l'identité du demandeur avec au moins deux éléments non sensibles : numéro de client, référence d'une facture récente ou date approximative de création du compte. Le support ne doit jamais demander le mot de passe complet, un code de récupération ou les données complètes d'une carte bancaire.

La nouvelle adresse doit être différente de l'ancienne, respecter un format valide et ne pas être déjà rattachée à un autre compte. Les adresses jetables et les domaines explicitement bloqués par la politique de sécurité sont refusés.

## Perte d'accès à l'ancienne adresse

Si l'utilisateur ne peut plus consulter son ancienne boîte email, la modification en libre-service peut être impossible. Le ticket doit alors être classé dans la catégorie `account` avec une priorité au moins `high`. Un opérateur vérifie les justificatifs et décide d'approuver, de rejeter ou de demander des informations supplémentaires.

## Comptes d'organisation

Pour un compte appartenant à une organisation, seul un administrateur autorisé peut demander la modification de l'adresse principale. Si le seul administrateur a quitté l'entreprise, le ticket doit être transmis à l'équipe chargée de la propriété des comptes. Aucun transfert ne doit être effectué sur la base d'une simple demande par email.

## Après la modification

Toutes les sessions actives sont révoquées et l'utilisateur doit se reconnecter avec la nouvelle adresse. L'événement doit être enregistré dans le journal d'audit avec l'ancienne adresse masquée, la nouvelle adresse masquée, l'opérateur ayant approuvé l'action et la date de modification.


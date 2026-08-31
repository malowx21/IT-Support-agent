# Réinitialisation du mot de passe

## Objectif

Cette procédure permet à un utilisateur de récupérer l'accès à son compte lorsqu'il a oublié son mot de passe ou lorsque son mot de passe n'est plus accepté. Le support ne doit jamais demander, enregistrer ou communiquer le mot de passe actuel d'un client.

## Procédure standard

L'utilisateur doit ouvrir la page `/forgot-password`, saisir l'adresse email associée à son compte puis sélectionner « Envoyer le lien ». Si l'adresse correspond à un compte actif, un email de réinitialisation est envoyé. Pour des raisons de sécurité, l'interface affiche le même message lorsque l'adresse n'existe pas.

Le lien expire après 30 minutes et ne peut être utilisé qu'une seule fois. Le nouveau mot de passe doit contenir au moins 12 caractères, une lettre majuscule, une lettre minuscule et un chiffre. Après la modification, toutes les sessions existantes sont déconnectées, sauf celle utilisée pour terminer la procédure.

## Email non reçu

Le client doit d'abord vérifier les dossiers spam, courrier indésirable et promotions. Il doit aussi confirmer qu'il consulte la bonne boîte email et attendre jusqu'à cinq minutes. Plusieurs demandes successives invalident les anciens liens : seul le lien du message le plus récent fonctionne.

Si aucun email n'arrive après dix minutes, le support peut vérifier l'état du service d'envoi et confirmer que le domaine du client n'est pas bloqué. Le support ne doit pas révéler si une adresse inconnue possède ou non un compte.

## Compte verrouillé

Après cinq tentatives incorrectes, le compte est temporairement verrouillé pendant 15 minutes. Une réinitialisation réussie retire automatiquement ce verrouillage. Si le compte reste bloqué après la réinitialisation, le ticket doit être transmis à l'équipe sécurité avec la catégorie `access` et la priorité `high`.

## Cas nécessitant une escalade

Une escalade humaine est obligatoire lorsque l'utilisateur n'a plus accès à son adresse email, signale une connexion qu'il ne reconnaît pas ou demande au support de modifier directement ses identifiants. L'agent peut expliquer la procédure, mais il ne doit jamais modifier une adresse email ou désactiver un mécanisme de sécurité sans validation humaine.


const regex_courriel = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;

const regex_mot_de_passe = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{5,}$/;


function validerNom() {
    const nom = document.getElementById("nom").value.trim();
    const msg = document.getElementById("erreur-nom");

    msg.textContent = "";

    if (!nom) {
        msg.textContent = "Le nom ne peut pas être vide.";
        return false;
    }

    return true;
}


function validerPrenom() {
    const prenom = document.getElementById("prenom").value.trim();
    const msg = document.getElementById("erreur-prenom");

    msg.textContent = "";

    if (!prenom) {
        msg.textContent = "Le prénom ne peut pas être vide.";
        return false;
    }

    return true;
}


function validerCourriel() {
    const courriel = document.getElementById("courriel").value.trim();
    const msg = document.getElementById("erreur-courriel");

    msg.textContent = "";

    if (!courriel) {
        msg.textContent = "Le courriel ne peut pas être vide.";
        return false;
    }

    if (!regex_courriel.test(courriel)) {
        msg.textContent = "Le courriel n'est pas valide.";
        return false;
    }

    return true;
}


async function verifierCourrielExiste() {
    const courriel = document.getElementById("courriel").value.trim();
    const msg = document.getElementById("erreur-courriel");

    if (!courriel || !regex_courriel.test(courriel)) {
        return false;
    }

    try {
        const resultat = await envoyerRequeteAjax(
            "/compte/api/verifier_courriel",
            "POST",
            { courriel: courriel }
        );

        if (resultat.existe) {
            msg.textContent = "Ce courriel est déjà utilisé.";
            return false;
        }

        return true;

    } catch (err) {
        return false;
    }
}
function validerMotDePasse() {
    const mdp = document.getElementById("mot_de_passe").value.trim();
    const msg = document.getElementById("erreur-motdepasse");

    msg.textContent = "";

    if (!mdp) {
        msg.textContent = "Le mot de passe ne peut pas être vide.";
        return false;
    }

    if (!regex_mot_de_passe.test(mdp)) {
        msg.textContent = "Le mot de passe doit contenir au moins 5 caractères, une majuscule, une minuscule et un chiffre.";
        return false;
    }

    return true;
}


function validerConfirmation() {
    const mdp = document.getElementById("mot_de_passe").value.trim();
    const conf = document.getElementById("confirmation_mot_de_passe").value.trim();
    const msg = document.getElementById("erreur-confirmation");

    msg.textContent = "";

    if (mdp !== conf) {
        msg.textContent = "La confirmation ne correspond pas.";
        return false;
    }

    return true;
}


async function creerCompte(e) {
    e.preventDefault();

    const nomValide = validerNom();
    const prenomValide = validerPrenom();
    const courrielValide = validerCourriel();
    const motDePasseValide = validerMotDePasse();
    const confirmationValide = validerConfirmation();

    if (!nomValide || !prenomValide || !courrielValide || !motDePasseValide || !confirmationValide) {
        return false;
    }

    const form = document.getElementById("form-creer-compte");
    const donnees = new FormData(form);
    const parametres = Object.fromEntries(donnees);

    try {
        const resultat = await envoyerRequeteAjax(
            "/compte/api/creer_compte",
            "POST",
            parametres
        );
        alert(resultat.message);
        window.location.href = "/compte/connexion";

        return true;

    } catch (err) {
        return false;
    }
}

function initialiserValidation() {
    document.getElementById("nom").addEventListener("input", validerNom);
    document.getElementById("prenom") .addEventListener("input", validerPrenom);
    document.getElementById("courriel") .addEventListener("input", validerCourriel);
    document.getElementById("courriel").addEventListener("input", verifierCourrielExiste);
    document.getElementById("mot_de_passe").addEventListener("input", validerMotDePasse);
    document.getElementById("confirmation_mot_de_passe").addEventListener("input", validerConfirmation);
    document.getElementById("form-creer-compte").addEventListener("submit", creerCompte);
    return true;
}
window.addEventListener("load", initialiserValidation);
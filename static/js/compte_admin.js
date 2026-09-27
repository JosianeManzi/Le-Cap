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


function validerCodeSecret() {
    const code = document.getElementById("code_secret").value.trim();
    const msg = document.getElementById("erreur-code-secret");
    msg.textContent = "";
    if (!code) {
        msg.textContent = "Le code secret est requis.";
        return false;
    }
    return true;
}


async function creerCompteAdmin(e) {
    e.preventDefault();

    const nomValide = validerNom();
    const prenomValide = validerPrenom();
    const courrielValide = validerCourriel();
    const motDePasseValide = validerMotDePasse();
    const codeValide = validerCodeSecret();

    if (!nomValide || !prenomValide || !courrielValide || !motDePasseValide || !codeValide) {
        return false;
    }

    const form = document.getElementById("form-creer-compte-admin");
    const donnees = new FormData(form);
    const parametres = Object.fromEntries(donnees);

    try {
        const resultat = await envoyerRequeteAjax(
            "/compte/creer_compte_admin",
            "POST",
            parametres
        );
        alert(resultat.message);
        window.location.href = "/compte/connexion";
        return true;

    } catch (err) {
        alert("Erreur : code secret invalide ou compte déjà existant.");
        return false;
    }
}


function initialiserValidation() {
    document.getElementById("nom").addEventListener("input", validerNom);
    document.getElementById("prenom").addEventListener("input", validerPrenom);
    document.getElementById("courriel").addEventListener("input", validerCourriel);
    document.getElementById("mot_de_passe").addEventListener("input", validerMotDePasse);
    document.getElementById("code_secret").addEventListener("input", validerCodeSecret);
    document.getElementById("form-creer-compte-admin").addEventListener("submit", creerCompteAdmin);
    return true;
}
window.addEventListener("load", initialiserValidation);
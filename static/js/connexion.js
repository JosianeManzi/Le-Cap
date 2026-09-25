const regex_courriel = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;


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
    return true;
}


async function seConnecter(e) {
    e.preventDefault();

    const courrielValide = validerCourriel();
    const motDePasseValide = validerMotDePasse();
    const msgConnexion = document.getElementById("erreur-connexion");
    msgConnexion.textContent = "";

    if (!courrielValide || !motDePasseValide) {
        return false;
    }

    const form = document.getElementById("form-connexion");
    const donnees = new FormData(form);
    const parametres = Object.fromEntries(donnees);

    try {
        const resultat = await envoyerRequeteAjax(
            "/compte/connexion",
            "POST",
            parametres
        );
        alert(resultat.message);
        window.location.href = "/";
        return true;

    } catch (err) {
        msgConnexion.textContent = "Courriel ou mot de passe incorrect.";
        return false;
    }
}


function initialiserValidation() {
    document.getElementById("courriel").addEventListener("input", validerCourriel);
    document.getElementById("mot_de_passe").addEventListener("input", validerMotDePasse);
    document.getElementById("form-connexion").addEventListener("submit", seConnecter);
    return true;
}
window.addEventListener("load", initialiserValidation);
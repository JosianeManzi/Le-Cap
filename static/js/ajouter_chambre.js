function validerType() {
    const type = document.getElementById("type_chambre").value.trim();
    const msg = document.getElementById("erreur-type");
    msg.textContent = "";
    if (!type) {
        msg.textContent = "Le type de chambre est requis.";
        return false;
    }
    return true;
}


function validerDescription() {
    const description = document.getElementById("description").value.trim();
    const msg = document.getElementById("erreur-description");
    msg.textContent = "";
    if (!description) {
        msg.textContent = "La description est requise.";
        return false;
    }
    return true;
}


function validerPrix() {
    const prix = document.getElementById("prix_nuit").value.trim();
    const msg = document.getElementById("erreur-prix");
    msg.textContent = "";
    if (!prix || isNaN(prix) || Number(prix) <= 0) {
        msg.textContent = "Le prix doit être un nombre positif.";
        return false;
    }
    return true;
}


async function ajouterChambre(e) {
    e.preventDefault();

    const typeValide = validerType();
    const descriptionValide = validerDescription();
    const prixValide = validerPrix();

    if (!typeValide || !descriptionValide || !prixValide) {
        return false;
    }

    const form = document.getElementById("form-ajouter-chambre");
    const donnees = new FormData(form);

    // La case "disponible" n'envoie rien si décochée : on force la valeur
    if (!document.getElementById("disponible").checked) {
        donnees.set("disponible", "0");
    }

    const parametres = Object.fromEntries(donnees);

    try {
        const resultat = await envoyerRequeteAjax(
            "/chambres/ajouter_chambre",
            "POST",
            parametres
        );
        alert(resultat.message);
        form.reset();
        return true;

    } catch (err) {
        alert("Erreur lors de l'ajout de la chambre.");
        return false;
    }
}


function initialiserValidation() {
    document.getElementById("type_chambre").addEventListener("input", validerType);
    document.getElementById("description").addEventListener("input", validerDescription);
    document.getElementById("prix_nuit").addEventListener("input", validerPrix);
    document.getElementById("form-ajouter-chambre").addEventListener("submit", ajouterChambre);
    return true;
}
window.addEventListener("load", initialiserValidation);
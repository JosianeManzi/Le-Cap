"use strict";
async function envoyerRequeteAjax(
    url,
    methode = "GET",
    parametres = {},
    controleur = null
) {
    let urlCible = url;

    let body = null;
    if ((parametres !== null) && (Object.keys(parametres).length > 0)) {
        const paramStr = new URLSearchParams(parametres);
        if (methode.toUpperCase() == "GET") {
            urlCible = `${urlCible}?${paramStr}`;
        } else {
            body = paramStr;
        }
    }

    const parametresFetch = {
        method: methode,
        headers: {
            "Content-Type": 'application/x-www-form-urlencoded'
        },
        body: body,
        cache: "no-store"
    }

    if (controleur != null) {
        parametresFetch["signal"] = controleur.signal
    }

    const reponse = await fetch(
        urlCible,
        parametresFetch
    );
    if (!reponse.ok) {
        throw new Error(`${reponse.status} ${reponse.statusText}`)
    }

    return await reponse.json();
}

function deletePref(player, element) {
    var prefs = JSON.parse(localStorage['prefs']);
    delete prefs[player];
    localStorage['prefs'] = JSON.stringify(prefs);
    element.parentElement.removeChild(element);
}

function listPlayers() {
    var prefs = {};
    if (localStorage['prefs']) {
        prefs = JSON.parse(localStorage['prefs']);
    }

    // clear the list of player prefs
    var playersList = document.getElementById("players");
    while (playersList.firstChild) {
        playersList.removeChild(playersList.firstChild);
    }

    // build list of player prefs from localStorage
    for (let name in prefs) {
        let pref_el = document.createElement('div');
        pref_el.className = 'pref';
        var name_el = document.createElement('span');
        name_el.innerText = name;
        name_el.className = 'name';
        pref_el.appendChild(name_el);
        var image_list = document.createElement('div');
        for (var hero in prefs[name]) {
            var hero_img = document.createElement("img");
            hero_img.src = "/static/img/" + prefs[name][hero] + ".png";
            image_list.appendChild(hero_img);
        }
        var delete_button = document.createElement('div');
        delete_button.className = 'delete';
        delete_button.innerText = '✖';
        delete_button.addEventListener('click', function() { deletePref(name, pref_el); });
        pref_el.appendChild(delete_button);
        pref_el.appendChild(image_list);
        playersList.appendChild(pref_el);
    }
}

function savePlayer(e) {
    e.preventDefault();
    var prefs = {};
    if (localStorage['prefs']) {
        prefs = JSON.parse(localStorage['prefs']);
    }

    var form = document.getElementById("new_player");
    var playerName = form.elements['player_name'].value;
    prefs[playerName] = [];
    var hero_prefs = form.elements['hero_pref'];
    for (var i = 0; i < hero_prefs.length; i++) {
        if (hero_prefs[i].checked) {
            prefs[playerName].push(hero_prefs[i].value);
            hero_prefs[i].checked = false;
        }
    }
    form.elements['player_name'].value = "";

    localStorage['prefs'] = JSON.stringify(prefs);

    listPlayers();
}

function ready(fn) {
    if (document.readyState != 'loading'){
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn);
    }
}

ready(function() {
    var form = document.getElementById("new_player");
    form.addEventListener("submit", savePlayer, false);

    listPlayers();
});


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
    for (var name in prefs) {
        var li = document.createElement('li');
        li.innerText = name + " prefers";
        for (var hero in prefs[name]) {
            var hero_img = document.createElement("img");
            hero_img.src = "/static/img/" + prefs[name][hero] + ".png";
            li.appendChild(hero_img);
        }
        playersList.appendChild(li);
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
        }
    }

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


function listPlayers() {
    var prefs = {};
    if (localStorage['prefs']) {
        prefs = JSON.parse(localStorage['prefs']);
    }

    var playersList = document.getElementById('players');

    // build list of player prefs from localStorage
    for (var name in prefs) {
        var checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = name;
        checkbox.name = 'player';

        var span = document.createElement('span');
        span.innerText = name;

        var div = document.createElement('div');
        div.appendChild(checkbox);
        div.appendChild(span);
        playersList.appendChild(div);
    }
}

function sendJson(e) {
    var prefs = {};
    if (localStorage['prefs']) {
        prefs = JSON.parse(localStorage['prefs']);
    }
    var json = {};

    var form = document.getElementById("players");
    var players = form.elements['player'];
    for (var i = 0; i < players.length; i++) {
        if (players[i].checked) {
            json[players[i].value] = prefs[players[i].value];
        }
    }

    var json_input = document.createElement('input');
    json_input.type = 'hidden';
    json_input.name = 'player_json';
    json_input.value = JSON.stringify(json);
    form.appendChild(json_input);

    return true;
}


function ready(fn) {
    if (document.readyState != 'loading'){
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn);
    }
}

ready(function() {
    var form = document.getElementById('players');
    form.addEventListener('submit', sendJson, false);

    listPlayers();
});

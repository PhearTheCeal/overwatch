
function buildRandomsInput(e) {
    var sum = 0;
    var form = document.getElementById("builder_form");
    var players = form.elements['player'];
    for (var i = 0; i < players.length; i++) {
        if (players[i].checked) {
            sum++;
        }
    }
    if (sum > 6) {
        if (e) {
            e.preventDefault();
        }
        return false;
    }

    var diff = 6 - sum;
    while (document.getElementsByName('random').length != diff) {
        if (document.getElementsByName('random').length < diff) {
            // add input
            var inp = document.createElement('select');
            inp.name = 'random';
            inp.form = 'builder_form';
            inp.style.display = 'block';
            for (var i = 0; i < HEROES.length; i++) {
                var opt = document.createElement('option');
                opt.value = HEROES[i];
                opt.innerText = HEROES[i].charAt(0).toUpperCase() + HEROES[i].slice(1);
                inp.appendChild(opt);
            }
            document.getElementById('randoms').appendChild(inp);
        } else {
            // remove input
            var children = document.getElementById('randoms').children;
            document.getElementById('randoms').removeChild(children[children.length - 1]);
        }
    }
    
    return true;
}

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
        checkbox.addEventListener('click', buildRandomsInput);

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

    var form = document.getElementById("builder_form");
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
    var form = document.getElementById('builder_form');
    form.addEventListener('submit', sendJson, false);

    listPlayers();
    buildRandomsInput();
});

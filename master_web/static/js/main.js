const socket = io();

socket.on("connect", () => {
  update_etat(true);
  request_update();
});

socket.on("disconnect", () => {
  update_etat(false);
});

function request_update() {
  socket.emit("update", function() { });
}

socket.on("update", function(data) {
  update(data);
});


let dict_ieds = {};

(function() {
  setInterval(function () {
    for (id in dict_ieds)
    {
      if (dict_ieds[id] != 0) {
        x = Math.round((Date.now() - dict_ieds[id]) / 1000);
        if (x > 999) x = 999;
        x += 's'
      }
      else { x = "N/A"; }
      set('ping', id, x);
    }
  }, 100);
})();


function update(ieds)
{
  for (const [id, value] of Object.entries(ieds))
  {
    if (!(id in dict_ieds)) add_ied(id);
    dict_ieds[id] = ieds[id][2];
  }
}

let selection_mode = 'Tous';

function selection_choice() {
  let btn = document.getElementById('check-255');

  if (selection_mode == 'Tous') { selection_mode = 'Sélection'; } 
  else { selection_mode = 'Tous' }
  btn.innerText = selection_mode;
}

function ping_selection()
{

  if (selection_mode == 'Tous')
  {
    ping([255]);
  }
  else
  {
    tab = [];

    for (id in dict_ieds) {
      if (document.getElementById('check-' + id).checked)
        tab.push(id)
    }
    ping(tab)
  }

  show_loader(255, 1);
}


function fire_selection()
{
  if (selection_mode == 'Tous') {
    fire([255]);
  }
  else
  {
    tab = [];

    for (id in dict_ieds) {
      if (document.getElementById('check-' + id).checked)
        tab.push(id)
    }
    fire(tab)
  }
  show_loader(255);
}


function ping(id) {
  socket.emit("ping", {'id': id, 'time': Date.now()});
}

function fire(id) {
  socket.emit("fire", {'id': id});
}


function show_loader(id, duree = 1) {
    document.getElementById('check-' + id).parentNode.classList.add('loader');
    document.getElementById('check-' + id).parentNode.style.animationDuration = duree + 's';
    document.getElementById('check-' + id).parentNode.style.WebkitAnimationDuration = duree + 's';

    setTimeout(function () {
      document.getElementById('check-' + id).parentNode.classList.remove('loader');
    }, duree * 1000);
}

function set(attr,id,value) {
  document.getElementById(attr + '-' + id).innerText = value;
}


function update_etat(etat)
{
  let div_etat = document.getElementById('etat');
  div_etat.style.display = etat ? 'none' : 'block';
}

function add_ied(id)
{
  const tpl = document.createElement('template');
  tpl.innerHTML = get_ied_tpl(id);

  let container = document.getElementById('container');
  container.appendChild(tpl.content.firstChild);
}

function get_ied_tpl(id)
{
  return '<div class="line">' +
      '<input type="checkbox" id="check-'+ id +'" /> ' +
      
      '<label for="check-'+ id +'" class="text">' +
        '<span id="name-'+ id +'">IED '+ id +'</span>' +
        ' (<span id="ping-'+ id +'"></span>)' +
      '</label>' +

      '<span class="buttons">' +
        '<img src="../static/wifi.png" width="45" onclick="show_loader(\''+ id +'\'); ping([\''+ id +'\']);" style="margin-right: 10px;" /> ' +
        '<img src="../static/bomb.png" width="45" onclick="show_loader(\''+ id +'\'); fire([\''+ id +'\']);" />' +
      '</span>' +
    '</div>';
}

function pop_error(value) {
  document.getElementById('alert').style = 'display: block';
  document.getElementById('alert').innerText = value;

  setTimeout(function () {
    document.getElementById('alert').style = 'display: none';
  }, 4000);
}


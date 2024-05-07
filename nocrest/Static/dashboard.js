const modal = document.getElementById('profile-modal');


const modala = document.getElementById('profile-modala');


const nocmodala = document.getElementById('noc-modala');


const applybtn = document.getElementById('btnapply');
const nocapply = document.getElementById('nocapply');
const checkbtn = document.getElementById('btncheck');
const closeButton = document.getElementsByClassName('close')[0];
const closeButtona = document.getElementsByClassName('closea')[0];
const ndclose = document.getElementsByClassName('closer')[0];




applybtn.addEventListener('click',function(event){
    event.preventDefault();
    modala.style.display = 'flex';
})

nocapply.addEventListener('click',function(event){
    event.preventDefault();
    nocmodala.style.display = 'block';
})

closeButton.addEventListener('click', function() {
  modal.style.display = 'none';
});
closeButtona.addEventListener('click', function() {
  modala.style.display = 'none';
});
ndclose.addEventListener('click', function() {
  nocmodala.style.display = 'none';
});

window.addEventListener('click', function(event) {
  if (event.target === modal) {
    modal.style.display = 'none';
  }
});



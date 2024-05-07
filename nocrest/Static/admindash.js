const modal = document.getElementById('profile-modal');
const modala = document.getElementById('profile-modala');
const profileLink = document.getElementById('profile-link');
// const applybtn = document.getElementById('btnapply');
const closeButton = document.getElementsByClassName('close')[0];
const closeButtona = document.getElementsByClassName('closea')[0];
// const id = document.getElementById('profilebtn')
// console.log(profileLink)
// id.addEventListener('click', function(event) {
//   event.preventDefault(); 
//   modal.style.display = 'block';
// });
profileLink.addEventListener('click', function(event) {
    console.log("Hello")
  event.preventDefault(); 
  modal.style.display = 'block';
});
// applybtn.addEventListener('click',function(event){
//     event.preventDefault();
//     modala.style.display = 'block';
// })
closeButton.addEventListener('click', function() {
  modal.style.display = 'none';
});
closeButtona.addEventListener('click', function() {
  modala.style.display = 'none';
});

window.addEventListener('click', function(event) {
  if (event.target === modal) {
    modal.style.display = 'none';
  }
});

const btns=document.getElementsByClassName('btn');
for (i = 0; i < btns.length; i++) {
    btns[i].addEventListener('click', function (e) {
        const user_table=this.nextElementSibling;
    if(user_table.classList.contains('none1')){
        user_table.classList.remove('none1');
        e.target.classList.add('button-active');
    }else{
        user_table.classList.add('none1');
        e.target.classList.remove('button-active');
    }
    })
}


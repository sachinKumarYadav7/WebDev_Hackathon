document.getElementById("search_bar").addEventListener("click", function() {
  const mcontainer = document.getElementById('main-container');
  const ncontainer = document.getElementById('new-container');

  document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`#search_bar`).classList.add('active');

  mcontainer.classList.add('hidden');
  setTimeout(function() {
      mcontainer.style.display = 'none';
      ncontainer.style.display = 'block';
      setTimeout(function() {
          ncontainer.classList.add('visible');
      }, 150);
      
  }, 100);
});

document.getElementById("dash").addEventListener("click", function() {
  const mcontainer = document.getElementById('main-container');
  const ncontainer = document.getElementById('new-container');

  document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`#dash`).classList.add('active');

  ncontainer.classList.remove('visible');
  setTimeout(function() {
      ncontainer.style.display = 'none';
      mcontainer.style.display = 'block';
      setTimeout(function() {
          mcontainer.classList.remove('hidden');
      }, 150); // Allow reflow before applying transition
  }, 100);
});


document.addEventListener('DOMContentLoaded', () => {

  const cards = document.querySelectorAll('.card');
  let currentIndex = 0;

  function showNextCard() {
      cards.forEach((card, index) => {
          if (index === currentIndex) {
              card.style.transform = `translateZ(${index * -20}px)`;
              card.style.opacity = 1;
          } else {
              card.style.transform = `translateZ(${(index - currentIndex) * -20}px)`;
              card.style.opacity = 0;
          }
      });

      currentIndex = (currentIndex + 1) % cards.length;
    //   console
  }


  setInterval(showNextCard, 3000);
  showNextCard();

  const advertisements = document.querySelectorAll('.advertisement');
  let currentAdIndex = 0;

  function showNextAdvertisement() {
      advertisements.forEach((ad, index) => {
          if (index === currentAdIndex) {
              ad.classList.add('active');
          } else {
              ad.classList.remove('active');
          }
      });

      currentAdIndex = (currentAdIndex + 1) % advertisements.length;
  }

  setInterval(showNextAdvertisement, 3000);

  showNextAdvertisement();
});

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("mode").addEventListener("click", function() {
        const nav = document.getElementById('navbar');
        const body = document.body;
        const logo = document.getElementById('imgmode');
        const searchb = document.getElementById('search_bar');
        const g = document.getElementById('grid');
        const Pending_issue_reqs = document.getElementById('Pending_issue_reqs');
        const issuelist = document.getElementById('issuelist');
        const announcement = document.getElementById('announcement');
        const c = document.getElementById('ad');
        const feedback = document.getElementById('feedback');
        const cs = document.getElementsByClassName('card');
        const advertisements = document.getElementsByClassName('advertisement');
        const advertisements_active = document.getElementsByClassName('advertisement.active');
    
        const darkMode = nav.classList.contains('bg-dark');
  
        if (darkMode){
            nav.classList.remove('bg-dark', 'navbar-dark');
            nav.style.backgroundColor = '#6a1b9a';
            body.style.backgroundColor = '#f8f9fa';
            body.style.color = 'black'; 
            logo.src = "../static/images/moon.png";
            searchb.style.backgroundColor = 'white';
            searchb.style.color = 'black';
            Pending_issue_reqs.style.backgroundColor = 'white';
            g.style.backgroundColor = 'white';
            for (let i = 0; i < cs.length; i++) {
                cs[i].style.backgroundColor = 'white';
                cs[i].style.color = 'black';
            }
            for (let i = 0; i < advertisements.length; i++) {
                advertisements[i].style.backgroundColor = 'white';
            }
            c.style.backgroundColor = 'rgb(243, 243, 243)';
            feedback.style.backgroundColor = 'rgb(243, 243, 243)';             
        } else {
            nav.classList.remove('bg-light', 'navbar-light');
            nav.classList.add('bg-dark', 'navbar-dark');
            body.style.backgroundColor = 'black';
            body.style.color = 'white'; 
            nav.style.color = 'rgba(255, 255, 255, .5)'; 
            logo.src = "../static/images/day-mode.png";
            searchb.style.backgroundColor = 'black';
            searchb.style.color = 'white';
            g.style.backgroundColor = 'rgb(52, 55, 54)';
            Pending_issue_reqs.style.backgroundColor = 'rgb(52, 55, 54)';
            announcement.style.backgroundColor = 'rgb(52, 55, 54)';
            issuelist.style.backgroundColor = 'rgb(52, 55, 54)';
            
            for (let i = 0; i < cs.length; i++) {
                cs[i].style.backgroundColor = 'black';
                cs[i].style.color = 'white';
            }
            for (let i = 0; i < advertisements.length; i++) {
                advertisements[i].style.backgroundColor = 'black';
            }
            c.style.backgroundColor = '#343736';
            advertisements_active.backgroundColor = 'red';
            feedback.style.backgroundColor = '#343736';     
        }
    });
  });
  
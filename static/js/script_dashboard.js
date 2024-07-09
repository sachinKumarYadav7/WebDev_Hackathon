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
      }, 150); 
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
    const modeToggle = document.getElementById('mode');
    const body = document.body;
    const imgMode = document.getElementById('imgmode');
    const darkModeClass = 'dark-mode';

    function setMode(isDark) {
        if (isDark) {
            body.classList.add(darkModeClass);
            imgMode.src = "../static/images/day-mode.png"; 
        } else {
            body.classList.remove(darkModeClass);
            imgMode.src = "../static/images/moon.png"; 
        }
        localStorage.setItem('darkMode', isDark);
    }

    const savedMode = localStorage.getItem('darkMode');
    if (savedMode === 'true') {
        setMode(true);
    } else {
        setMode(false);
    }

    modeToggle.addEventListener('click', function() {
        const isDark = body.classList.contains(darkModeClass);
        setMode(!isDark);
    });
});